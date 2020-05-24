import datetime
import requests

from drug_design.load_data import load_data
from drug_design.similarity import run_similarity
from drug_design.gsheet_store import gsheet_store
from drug_design.datasets.DataSets import DataSet
from drug_design.save_load import load_obj, save_obj
from drug_design.key_increment import key_increment, get_shifted_key, sub_key_gen
from drug_design.DataStorePipeLine import DataStorePipeLine
import settings
import pandas as pd

from flask import Flask, jsonify, request, render_template, redirect, url_for, Markup, make_response
from wtforms import Form, BooleanField, StringField, validators

def create_app():

    app = Flask(__name__)

    def get_session_key(user_id):
        url = settings.BE_URL_PREFIX + '/drug_design_backend/api/v1/session/' + user_id
        try:
            r = requests.get(url)
            response = r.json()
            #saving the session_key to the pip
            session_key =  response['session_key']
            return session_key
        except:
            return "Something went wrong - maybe a session is already active for this user"

    def set_session_cookie(user_id,response_contents):
        session_key = get_session_key(user_id)
        response = make_response(response_contents)
        response.set_cookie('session_key', session_key)
        return {'session_key' : session_key, 'response' : response}

    #The main function to take you through option
    @app.route("/index/", methods=['GET','POST'])
    def main():

        msg = "Welcome to the main page"
        a = "hello world"

        #Session in  cookie - try and use that
        try:
            session_key = request.cookies.get('session_key')
        finally:
            if not session_key == None:
                b = "You already have some data loaded, your options are:"
                response = render_template('welcome_options.html', var1 = msg, var3 = b)
                #check that the pipeline is from this session
                check_session_key = get_session_key('test')
                try:
                    assert check_session_key == session_key
                except AssertionError:
                    #If the session cookie doesn't match the active session then set it again
                    cookied_session = set_session_cookie('test',response)
                    session_key = cookied_session['session_key']
                    response = cookied_session['response']
                finally:
                    #try and build a pipeline
                    pipeline = DataStorePipeLine(True, user_id = 'test',session_key = session_key)
                    try:
                        #any situation where a valid session key is passed buyt it doesn't match the pipeline
                        assert pipeline.takeover == True
                    except AssertionError:
                        b = "It looks like you have loaded data in a separate session, your options are:"
                    finally:
                        return response

            #no session in cookie - ask for a new one
            else:
                b = "Before we get started you're going to need to load some data."
                cookied_response= set_session_cookie('test',render_template('welcome_page.html', var1 = msg, var2 = a, var3 = b))
                session_key = cookied_response['session_key']
                response = cookied_response['response']
                pipeline = DataStorePipeLine(True, user_id = 'test',session_key = session_key)
                return response

    @app.route('/example-load-data/')
    def example_load_data_form():
        return render_template('my-form.html', variable = '12345', variable2 = 'next_variable')

    #A Page for loading data example
    @app.route('/example-load-data/', methods=['POST'])
    def example_load_data_post():
        text = request.form['text']
        text2 = request.form['text2']
        processed_text = text.upper() + text2.upper()
        return render_template('welcome_page.html', var1 = processed_text, var2 = 'hello', var3 = 'howdy')



    #Load data
    @app.route('/load-data/')
    def load_data_form():
        url_dict = load_obj('url_dict')
        return render_template('load_data_form.html', Datafiles = url_dict)

    @app.route('/load-data/', methods = ['POST'])
    def load_data_form_post():
        key = request.form['dataset_choice']
        clear = request.form.get('clear_pipe')

        #if the request is to clear the pipe then we should be starting a new session
        if clear == "clear":
            cookied_response = set_session_cookie('test', redirect( url_for('main') ))
            session_key = cookied_response['session_key']
            response = cookied_response['response']
            pipeline = DataStorePipeLine(False,source_key = key, user_id = 'test', session_key = session_key)
            #If you go via the index page you can take over an old pipeline but if you
            try:
                assert pipeline.takeover == True
            except:
                response = "<h1>Pipeline takeover warning</h1><p>You have taken over this pipeline from an older session - clearing a pipeline can't be undone </p>"
            finally:
                return response

        else:
            #If the pipeline doesn't exist yet - this upsert will create it. You should already have a session by now
            session_key = request.cookies.get('session_key')
            pipeline = DataStorePipeLine(True,user_id = 'test',source_key = key, session_key = session_key)

            return redirect( url_for('main') )


    @app.route('/sim-score/', methods=['GET','POST'])
    def sim_score_start():
        #We need to load the data to show the headers
        #You don't get to start a session from here
        session_key = request.cookies.get('session_key')
        pipeline = DataStorePipeLine(True,user_id = 'test', session_key = session_key)
        ds_key = pipeline.source_key
        loaded_data = load_data(ds_key)
        headers = loaded_data[ds_key].headers
        return render_template('choose_column_form.html', Columns = headers)

    #Similarity score
    @app.route('/sim-score/reference_smiles', methods=['GET','POST'])
    def similarity_score_page():
        norm = False
        header = request.form['column_choice']
        try:
            norm_on = request.form['norm_on']
            if norm_on == "norm_true":
                norm = True
        except:
            print('normalisation off')
        session_key = request.cookies.get('session_key')
        pipeline_obj = DataStorePipeLine(True,user_id = 'test', session_key = session_key)
        pipeline = pipeline_obj.dictionary
        sim_key = key_increment("similarity_score",**pipeline)

        #update the sim key and reload the dictionary
        kwargs = {sim_key : header}
        pipeline_obj.update_property_datastore(**kwargs)
        pipeline = pipeline_obj.dictionary

        #generate correct norm key
        norm_key = sub_key_gen("normalise", "similarity_score", **pipeline)
        kwargs2 = {norm_key : norm}
        pipeline_obj.update_property_datastore(**kwargs2)

        if request.form["what_smiles"] == "single_smiles":
            return render_template('text_entry.html')

        elif request.form["what_smiles"] == "dataframe_smiles":
            url_dict = load_obj('url_dict')
            return render_template('ref_data_form.html', Datafile = url_dict)


    @app.route('/do-things/sim-smiles/single/', methods=['GET','POST'])
    def similarity_score_page_single():

        SMILES = request.form["Smiles"]
        session_key = request.cookies.get('session_key')
        pipeline_obj = DataStorePipeLine(True, user_id = 'test', session_key = session_key)
        pipeline = pipeline_obj.dictionary
        new_entry = sub_key_gen("single_smiles", "similarity_score", **pipeline)
        kwargs = {new_entry : SMILES}
        pipeline_obj.update_property_datastore(**kwargs)
        #pipeline keys so far ["source_key", "similarity_score", "normalise_scores", "single_smiles"]

        return redirect(url_for('main'))

    @app.route('/do-things/sim-smiles/ref_dataframe/', methods=['GET','POST'])
    def similarity_score_page_dataframe():

        ref_data_key = request.form["dataset_choice"]
        session_key = request.cookies.get('session_key')
        pipeline_obj = DataStorePipeLine(True, user_id = 'test', session_key = session_key)
        pipeline = pipeline_obj.dictionary
        new_entry = sub_key_gen("dataframe_smiles_ref", "similarity_score", **pipeline)
        kwargs = {new_entry : ref_data_key}
        pipeline_obj.update_property_datastore(**kwargs)
        #pipeline keys so far ["source_key", "similarity_score", "normalise_scores", "dataframe_smiles"]
        dataset = load_data(ref_data_key)
        headers = dataset[ref_data_key].headers
        return render_template('ref_column_form.html', Columns = headers )

    @app.route('/do-things/sim-smiles/ref_dataframe_cols/', methods=['GET','POST'])
    def similarity_score_page_dataframe_2():
        ref_column = request.form["column_choice"]
        session_key = request.cookies.get('session_key')
        pipeline_obj = DataStorePipeLine(True, user_id = 'test', session_key = session_key)
        pipeline = pipeline_obj.dictionary
        new_entry = sub_key_gen("dataframe_smiles_col", "similarity_score", **pipeline)
        kwargs = {new_entry : ref_column}
        pipeline_obj.update_property_datastore(**kwargs )
        #pipeline keys so far ["source_key", "similarity_score", "normalise_scores", "dataframe_smiles", "dataframe_smiles_col"]
        return redirect(url_for('main'))

    @app.route('/do-things/')
    def generate_results():
        session_key = request.cookies.get('session_key')
        pipeline_obj = DataStorePipeLine(True, user_id = 'test', session_key = session_key)
        pipeline = pipeline_obj.dictionary
        return render_template("run_pipeline.html", Pipeline = pipeline)

    @app.route('/do-things/results', methods = ['GET','POST'])
    def generate_results_2():

        session_key = request.cookies.get('session_key')
        pipeline_obj = DataStorePipeLine(True, user_id = 'test', session_key = session_key)
        result = pipeline_obj.run_pipeline()

        return render_template('results_page.html', Results = Markup(result.dataframe.to_html()))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
