import datetime

from drug_design.load_data import load_data
from drug_design.similarity import run_similarity
from drug_design.gsheet_store import gsheet_store
from drug_design.datasets.DataSets import DataSet
from drug_design.save_load import load_obj, save_obj
from drug_design.fetch_visits import store_time, fetch_times
from drug_design.key_increment import key_increment, get_shifted_key, sub_key_gen
from drug_design.DataStorePipeLine import DataStorePipeLine
import pandas as pd
import drug_design

from flask import Flask, jsonify, request, render_template, redirect, url_for, Markup
from flask_redis import FlaskRedis
from wtforms import Form, BooleanField, StringField, validators

def create_app():
    app = Flask(__name__)

    #The main function to take you through option
    @app.route("/index/", methods=['GET','POST'])
    def main():
        # Store the current access time in Datastore.
        store_time(datetime.datetime.now())

        # Fetch the most recent 10 access times from Datastore.
        times = fetch_times(1)

        msg = "Welcome to the main page"
        b = "You already have some data loaded, your options are:"
        pipeline = DataStorePipeLine(True, user_id = 'test')
        if not pipeline.source_key == '':
            return render_template('welcome_options.html', var1 = msg, times = times, var3 = b)

        else:
            b = "Before we get started you're going to need to load some data."
            return render_template('welcome_page.html', var1 = msg, var2 = a, var3 = b)

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

        if clear == "clear":
            pipeline = DataStorePipeLine(False,source_key = key)
        else:
            #If the pipeline doesn't exist yet - this upsert will create it
            pipeline = DataStorePipeLine(True,user_id = 'test',source_key = key)

        return redirect( url_for('main') )

    @app.route('/sim-score/', methods=['GET','POST'])
    def sim_score_start():
        #We need to load the data to show the headers
        pipeline = DataStorePipeLine(True,user_id = 'test')
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
        pipeline_obj = DataStorePipeLine(True,user_id = 'test')
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
        pipeline_obj = DataStorePipeLine(True, user_id = 'test')
        pipeline = pipeline_obj.dictionary
        new_entry = sub_key_gen("single_smiles", "similarity_score", **pipeline)
        kwargs = {new_entry : SMILES}
        pipeline_obj.update_property_datastore(**kwargs)
        #pipeline keys so far ["source_key", "similarity_score", "normalise_scores", "single_smiles"]

        return redirect(url_for('main'))

    @app.route('/do-things/sim-smiles/ref_dataframe/', methods=['GET','POST'])
    def similarity_score_page_dataframe():

        ref_data_key = request.form["dataset_choice"]
        pipeline_obj = DataStorePipeLine(True, user_id = 'test')
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
        pipeline_obj = DataStorePipeLine(True, user_id = 'test')
        pipeline = pipeline_obj.dictionary
        new_entry = sub_key_gen("dataframe_smiles_col", "similarity_score", **pipeline)
        kwargs = {new_entry : ref_column}
        pipeline_obj.update_property_datastore(**kwargs )
        #pipeline keys so far ["source_key", "similarity_score", "normalise_scores", "dataframe_smiles", "dataframe_smiles_col"]
        return redirect(url_for('main'))

    @app.route('/do-things/')
    def generate_results():
        pipeline_obj = DataStorePipeLine(True, user_id = 'test')
        pipeline = pipeline_obj.dictionary
        return render_template("run_pipeline.html", Pipeline = pipeline)

    @app.route('/do-things/results', methods = ['GET','POST'])
    def generate_results_2():

        pipeline_obj = DataStorePipeLine(True, user_id = 'test')
        result = pipeline_obj.run_pipeline()

        return render_template('results_page.html', Results = Markup(result.dataframe.to_html()))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
