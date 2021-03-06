import datetime
import requests

from drug_design.load_data import load_data
from drug_design.similarity import run_similarity
from drug_design.gsheet_store import gsheet_store
from drug_design.datasets.DataSets import DataSet
from drug_design.save_load import load_obj, save_obj
from drug_design.key_increment import key_increment, get_shifted_key, sub_key_gen
from drug_design.DataStorePipeLine import DataStorePipeLine
from drug_design.UrlDict import UrlDict
import settings
import pandas as pd

from flask import Flask, jsonify, request, render_template, redirect, url_for, Markup, make_response, abort

#Some silent function to fetch a csrf token from drug_design_backend
#This needs to be required by the backend and included in every requests
#We should call this function at the start of every view
def csrf_token():
    url = settings.BE_URL_PREFIX + '/drug_design_backend/api/v1/token'
    r = requests.get(url, verify = settings.VERIFY_SSL)
    response = r.json()
    token = response['csrf_token']
    return token

def get_session_key(user_id):
    url = settings.BE_URL_PREFIX + '/drug_design_backend/api/v1/session/' + user_id
    r = requests.get(url, verify = settings.VERIFY_SSL)
    if r.status_code == 403:
        raise Exception(r.status_code)
    response = r.json()
    session_key =  response['session_key']
    return session_key

def set_session_cookie(user_id, response_contents, **kwargs):
    #only try to get a session yey if you have to
    if not 'session_key' in kwargs:
        session_key = get_session_key(user_id)
    else:
        session_key = kwargs['session_key']

    response = make_response(response_contents)
    response.set_cookie('session_key', session_key)
    response.set_cookie('user_id', user_id)
    return {'session_key' : session_key, 'response' : response}

def fetch_session_cookies():
    session_key = request.cookies.get('session_key')
    user_id = request.cookies.get('user_id')

    cookies = {

        "user_id" : user_id,
        "session_key" : session_key

        }

    return cookies

def selectuser_loadpipeline(*args,**kwargs):
    max = len(settings.ALLOWLIST)
    end = settings.ALLOWLIST[max-1]
    pipeline = None
    assert 'user_id' in kwargs
    user_id = kwargs['user_id']
    print("starting with " + str(user_id))
    #first see if the pipeline loads with the passed user
    try:
        pipeline = DataStorePipeLine(*args, **kwargs)
        return pipeline, user_id
    except ValueError:
        #if it doesn't work then try and find another dormant user_id
        print("user_id " + user_id + " failed")
        for item in settings.ALLOWLIST:
            user_id = item
            kwargs['user_id'] = user_id
            print("... " + user_id)
            try:
                pipeline = DataStorePipeLine(*args, **kwargs)
                return pipeline, user_id
            except ValueError:
                print("user_id " + user_id + " failed")

            if user_id == end:
                print("all user_id's failed")
                return False, settings.ALLOWLIST[0]
            else:
                print("trying another user_id... " )

def create_app():

    app = Flask(__name__)

    @app.route("/access-restricted/", methods=['GET'])
    def access_denied():
        return render_template('access_denied.html')

    #The main function to take you through option
    @app.route("/index/", methods=['GET'])
    def main():
        msg = "Welcome to the main page"
        a = "hello world"

        #begin with the user_id as the first option - it doesn't really matter at this stage
        user_id = settings.ALLOWLIST[0]
        #Check if there is a cookie
        try:
            cookies = fetch_session_cookies()
            cookie_session_key = cookies["session_key"]
            user_id = cookies["user_id"]
        finally:
            #if there is a cookie
            if not cookie_session_key == None and not user_id == None:
                try:
                    #if there is an existing pipeline this should not attempt the update as no extra kwargs are passed
                    pipeline, user_id = selectuser_loadpipeline(True, user_id = user_id,session_key = cookie_session_key)
                except:
                    #if something goes wrong it's most likely the session is dormant so try and start a fresh one
                    b = "Your last session went dormant - but don't worrry we've started a new one for you"
                    pre_response = render_template('welcome_options.html', var1 = msg, var2 = b)
                    #If the cookied session fails then theres a good chance the session is occupoed
                    try:
                        cookied_session = set_session_cookie(user_id, pre_response)
                    except:
                        return redirect( url_for('access_denied') )
                    response = cookied_session['response']
                    return response
                if pipeline == False:
                    return redirect( url_for('access_denied') )
                #succesful loading confirms this is a useful session_key
                session_key = pipeline.session_key
                #no need to save a new cookie
                b = "You already have some data loaded, your options are:"
                response = render_template('welcome_options.html', var1 = msg, var2 = b)
                return response

            #aka there is no cookie to match against session_keys
            else:
                #We don't know the user_id so we'll start with the first option
                user_id = settings.ALLOWLIST[0]
                #this is to iterate through available user_id's and find one that is free
                pipeline, user_id = selectuser_loadpipeline(False, user_id = user_id)

                if pipeline == False:
                    return redirect( url_for('access_denied') )

                #a new cookie needs saved - creating a new pipeline will generate a new key in the pipeline
                session_key = pipeline.session_key
                b = "Before we get started you're going to need to load some data."
                pre_response = render_template('welcome_page.html', var1 = msg, var2 = b)
                cookied_session = set_session_cookie(user_id, pre_response, session_key = session_key)
                response = cookied_session['response']

                return response

    @app.route('/example-load-data/')
    def example_load_data_form():
        token = csrf_token()
        return render_template('my-form.html', variable = '12345', variable2 = 'next_variable', csrf_token = token)

    #A Page for loading data example
    @app.route('/example-load-data/', methods=['POST'])
    def example_load_data_post():
        token = csrf_token()
        try:
            assert request.form['tokenField'] == token
        except:
            abort(403)
        text = request.form['text']
        text2 = request.form['text2']
        processed_text = text.upper() + text2.upper()
        return render_template('welcome_page.html', var1 = processed_text, var2 = 'hello', var3 = 'howdy')



    #Load data
    @app.route('/load-data/')
    def load_data_form():
        url_dict = UrlDict(name = "url_dict")
        token = csrf_token()
        return render_template('load_data_form.html', Datafiles = url_dict.webdictionary, csrf_token = token)

    @app.route('/load-data/', methods = ['POST'])
    def load_data_form_post():
        token = csrf_token()
        try:
            assert request.form['tokenField'] == token
        except:
            abort(403)
        key = request.form['dataset_choice']
        clear = request.form.get('clear_pipe')

        # update the pipeline with the new source_key
        cookies = fetch_session_cookies()
        session_key = cookies["session_key"]
        user_id = cookies["user_id"]
        try:
            pipeline_obj = DataStorePipeLine(True,user_id = user_id, source_key = key, session_key = session_key)
        except:
            return redirect( url_for('access_denied') )
        pipeline = pipeline_obj.dictionary

        #if the request is to clear the pipe then simply use the current session and clear the pipe
        #This is not ideal and perhaps it would be better to create a new pipe and session from scratch
        if clear == "clear":
            clearance = { key : pipeline[key] for key in pipeline if not key == 'source_key'}
            if not clearance == None:
                pipeline_obj.delete_property_datastore(**clearance, session_key = session_key)

        return redirect( url_for('main') )

    @app.route('/manage-data/', methods=['GET'])
    def data_management():
        #We need to load the data to show the headers
        #You don't get to start a session from here
        token = csrf_token()
        cookies = fetch_session_cookies()
        session_key = cookies["session_key"]
        user_id = cookies["user_id"]

        url_dict = UrlDict(name = "url_dict")

        return render_template('manage_datasets.html', urldict = url_dict.webdictionary, csrf_token = token)

    @app.route('/manage-data/', methods=['POST'])
    def data_management_do():
        #We need to load the data to show the headers
        #You don't get to start a session from here
        token = csrf_token()
        try:
            assert request.form['tokenField'] == token
        except:
            abort(403)
        cookies = fetch_session_cookies()
        session_key = cookies["session_key"]
        user_id = cookies["user_id"]

        #load the url_dict
        url_dict = UrlDict(name = "url_dict")

        #check if anything should be deleted
        [
            url_dict.delete_dataset(request.form[key])
            for key in request.form
            if request.form[key] in url_dict.webdictionary
        ]

        #check if anything should be added
        if "url_key" in request.form and "id" in request.form:
            id = request.form['id']
            url_key = request.form['url_key']
            url_dict.add_gsheet_url(url_key, id)

        return redirect( url_for('data_management') )

    @app.route('/sim-score/', methods=['GET'])
    def sim_score_start():
        #We need to load the data to show the headers
        #You don't get to start a session from here
        token = csrf_token()
        cookies = fetch_session_cookies()
        session_key = cookies["session_key"]
        user_id = cookies["user_id"]
        try:
            pipeline = DataStorePipeLine(True,user_id = user_id, session_key = session_key)
        except:
            return redirect( url_for('access_denied') )
        ds_key = pipeline.source_key
        #data is only loaded for the headers - even 1 chunk is wasteful
        loaded_data = load_data(ds_key, chunk_limit = 1)
        headers = loaded_data[ds_key].headers
        return render_template('choose_column_form.html', Columns = headers, csrf_token = token)

    #Similarity score
    @app.route('/sim-score/', methods=['POST'])
    def similarity_score_page():
        token = csrf_token()
        try:
            assert request.form['tokenField'] == token
        except:
            abort(403)
        norm = False
        header = request.form['column_choice']
        try:
            norm_on = request.form['norm_on']
            if norm_on == "norm_true":
                norm = True
        except:
            print('normalisation off')
        cookies = fetch_session_cookies()
        session_key = cookies["session_key"]
        user_id = cookies["user_id"]
        try:
            pipeline_obj = DataStorePipeLine(True,user_id = user_id, session_key = session_key)
        except:
            return redirect( url_for('access_denied') )
        pipeline = pipeline_obj.dictionary
        sim_key = key_increment("similarity_score",**pipeline)

        #update the sim key and reload the dictionary
        kwargs = {sim_key : header}
        try:
            pipeline_obj.update_property_datastore(**kwargs)
        except:
            return redirect( url_for('access_denied') )
        pipeline = pipeline_obj.dictionary

        #generate correct norm key
        norm_key = sub_key_gen("normalise", "similarity_score", **pipeline)
        kwargs2 = {norm_key : norm}
        try:
            pipeline_obj.update_property_datastore(**kwargs2)
        except:
            return redirect( url_for('access_denied') )

        if request.form["what_smiles"] == "single_smiles":
            return render_template('text_entry.html', csrf_token = token)

        elif request.form["what_smiles"] == "dataframe_smiles":
            url_dict = UrlDict(name = "url_dict")
            return render_template('ref_data_form.html', Datafile = url_dict.webdictionary, csrf_token = token)


    @app.route('/sim-score/single/', methods=['POST'])
    def similarity_score_page_single():
        token = csrf_token()
        try:
            assert request.form['tokenField'] == token
        except:
            abort(403)
        SMILES = request.form["Smiles"]
        cookies = fetch_session_cookies()
        session_key = cookies["session_key"]
        user_id = cookies["user_id"]
        try:
            pipeline_obj = DataStorePipeLine(True, user_id = user_id, session_key = session_key)
        except:
            return redirect( url_for('access_denied') )
        pipeline = pipeline_obj.dictionary
        new_entry = sub_key_gen("single_smiles", "similarity_score", **pipeline)
        kwargs = {new_entry : SMILES}
        try:
            pipeline_obj.update_property_datastore(**kwargs)
        except:
            return redirect( url_for('access_denied') )
        #pipeline keys so far ["source_key", "similarity_score", "normalise_scores", "single_smiles"]

        return redirect(url_for('main'))

    @app.route('/sim-score/dataframe/', methods=['POST'])
    def similarity_score_page_dataframe():
        token = csrf_token()
        try:
            assert request.form['tokenField'] == token
        except:
            abort(403)
        ref_data_key = request.form["dataset_choice"]
        cookies = fetch_session_cookies()
        session_key = cookies["session_key"]
        user_id = cookies["user_id"]
        try:
            pipeline_obj = DataStorePipeLine(True, user_id = user_id, session_key = session_key)
        except:
            return redirect( url_for('access_denied') )
        pipeline = pipeline_obj.dictionary
        new_entry = sub_key_gen("dataframe_smiles_ref", "similarity_score", **pipeline)
        kwargs = {new_entry : ref_data_key}
        try:
            pipeline_obj.update_property_datastore(**kwargs)
        except:
            return redirect( url_for('access_denied') )
        #pipeline keys so far ["source_key", "similarity_score", "normalise_scores", "dataframe_smiles"]
        #data is only loaded for headers - even 1 chunk is wasteful
        dataset = load_data(ref_data_key, chunk_limit = 1)
        headers = dataset[ref_data_key].headers
        return render_template('ref_column_form.html', Columns = headers, csrf_token = token )

    @app.route('/sim-score/dataframe/ref_cols/', methods=['POST'])
    def similarity_score_page_dataframe_2():
        token = csrf_token()
        try:
            assert request.form['tokenField'] == token
        except:
            abort(403)
        ref_column = request.form["column_choice"]
        cookies = fetch_session_cookies()
        session_key = cookies["session_key"]
        user_id = cookies["user_id"]
        try:
            pipeline_obj = DataStorePipeLine(True, user_id = user_id, session_key = session_key)
        except:
            return redirect( url_for('access_denied') )
        pipeline = pipeline_obj.dictionary
        new_entry = sub_key_gen("dataframe_smiles_col", "similarity_score", **pipeline)
        kwargs = {new_entry : ref_column}
        try:
            pipeline_obj.update_property_datastore(**kwargs)
        except:
            return redirect( url_for('access_denied') )
        #pipeline keys so far ["source_key", "similarity_score", "normalise_scores", "dataframe_smiles", "dataframe_smiles_col"]
        return redirect(url_for('main'))

    @app.route('/do-things/', methods = ['GET'])
    def generate_results():
        cookies = fetch_session_cookies()
        session_key = cookies["session_key"]
        user_id = cookies["user_id"]
        try:
            pipeline_obj = DataStorePipeLine(True, user_id = user_id, session_key = session_key)
        except:
            return redirect( url_for('access_denied') )
        pipeline = pipeline_obj.dictionary
        return render_template("run_pipeline.html", Pipeline = pipeline)

    @app.route('/do-things/results', methods = ['POST'])
    def generate_results_2():

        cookies = fetch_session_cookies()
        session_key = cookies["session_key"]
        user_id = cookies["user_id"]
        try:
            pipeline_obj = DataStorePipeLine(True, user_id = user_id, session_key = session_key)
        except:
            return redirect( url_for('access_denied') )
        try:
            result = pipeline_obj.run_datastore_pipeline(session_key = session_key, chunk_limit = settings.CHUNK_LIMIT)
        except:
            return redirect( url_for('access_denied') )

        return render_template('results_page.html', Results = Markup(result.to_html()))

    return app

#for some reason this needs to be here for app engine to work - it doesn't affect running locally
app = create_app()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
