from drug_design.load_data import load_data
from drug_design.similarity import run_similarity
from drug_design.gsheet_store import gsheet_store
from drug_design.datasets.DataSets import DataSet
from drug_design.save_load import load_obj, save_obj
from drug_design.key_increment import key_increment, get_shifted_key
import pandas as pd
import drug_design
#same repo test 1
#test comment B same repo edit
from flask import Flask, jsonify, request, render_template, redirect, url_for, Markup
from flask_redis import FlaskRedis
from wtforms import Form, BooleanField, StringField, validators

def create_app():
    app = Flask(__name__)
    redis_client = FlaskRedis(app)
    app.config['REDIS_URL'] = "redis://:password@localhost:6379/0"

    #The main function to take you through option
    @app.route("/index/", methods=['GET','POST'])
    def main():
        msg = "Welcome to the main page"
        a = "You can hit Ctrl-C at any time to exit the program \n "
        b = "You already have some data loaded, your options are:"
        pipeline = load_obj('tmp_pipeline')
        if isinstance(pipeline,dict):
            return render_template('welcome_options.html', var1 = msg, var2 = a, var3 = b)

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
        save_obj(key, 'tmp_key')
        pipeline = load_obj('tmp_pipeline')
        if isinstance(pipeline, dict):
            if clear == "clear":
                pipeline = {"source_key" : key}
            else:
                pipeline["source_key"] =  key
            save_obj(pipeline, 'tmp_pipeline')
            #pipeline keys so far ["source_key"]
        else:
            pipeline = {"source_key" : key}
            save_obj(pipeline, 'tmp_pipeline')
        return redirect( url_for('main') )

    @app.route('/sim-score/', methods=['GET','POST'])
    def sim_score_start():
        #We need to load the data to show the headers
        ds_key = load_obj('tmp_key')
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
        pipeline = load_obj('tmp_pipeline')
        sim_key = key_increment("similarity_score",**pipeline)
        norm_key = key_increment("normalise_scores",**pipeline)

        #The pipeline is updated with the sim_key kept unique by an inreasing integer
        pipeline[sim_key] = header
        pipeline[norm_key] = norm
        save_obj(pipeline, 'tmp_pipeline')
        #pipeline keys so far ["source_key", "similarity_score", "normalise_scores"]

        if request.form["what_smiles"] == "single_smiles":
            return render_template('text_entry.html')

        elif request.form["what_smiles"] == "dataframe_smiles":
            url_dict = load_obj('url_dict')
            return render_template('ref_data_form.html', Datafile = url_dict)


    @app.route('/do-things/sim-smiles/single/', methods=['GET','POST'])
    def similarity_score_page_single():

        SMILES = request.form["Smiles"]
        pipeline = load_obj('tmp_pipeline')
        new_entry = key_increment("single_smiles",**pipeline)

        pipeline[new_entry] = SMILES
        save_obj(pipeline, 'tmp_pipeline')
        #pipeline keys so far ["source_key", "similarity_score", "normalise_scores", "single_smiles"]

        return redirect(url_for('main'))

    @app.route('/do-things/sim-smiles/ref_dataframe/', methods=['GET','POST'])
    def similarity_score_page_dataframe():

        ref_data_key = request.form["dataset_choice"]
        pipeline = load_obj('tmp_pipeline')
        new_entry = key_increment("dataframe_smiles_ref",**pipeline)
        pipeline[new_entry] = ref_data_key
        save_obj(pipeline, 'tmp_pipeline')
        #pipeline keys so far ["source_key", "similarity_score", "normalise_scores", "dataframe_smiles"]
        dataset = load_data(ref_data_key)
        headers = dataset[ref_data_key].headers
        return render_template('ref_column_form.html', Columns = headers )

    @app.route('/do-things/sim-smiles/ref_dataframe_cols/', methods=['GET','POST'])
    def similarity_score_page_dataframe_2():
        ref_column = request.form["column_choice"]
        pipeline = load_obj('tmp_pipeline')
        new_entry = key_increment("dataframe_smiles_col",**pipeline)
        pipeline[new_entry] = ref_column
        save_obj(pipeline, 'tmp_pipeline')
        #pipeline keys so far ["source_key", "similarity_score", "normalise_scores", "dataframe_smiles", "dataframe_smiles_col"]
        return redirect(url_for('main'))

    @app.route('/do-things/')
    def generate_results():
        pipeline = load_obj('tmp_pipeline')
        return render_template("run_pipeline.html", Pipeline = pipeline)

    @app.route('/do-things/results', methods = ['GET','POST'])
    def generate_results_2():
        pipeline = load_obj('tmp_pipeline')
        ds_key = pipeline["source_key"]
        dataset = load_data(ds_key)

        for key in pipeline:
            if "similarity_score" in key:
                header = pipeline[key]
                norm = pipeline[get_shifted_key(pipeline,key,1)]
                next_key = get_shifted_key(pipeline,key,2)
                if "single_smiles" in next_key:
                    mol_reference = {"SMILES" : [pipeline[next_key],norm]}
                    for chunk in dataset[ds_key].chunks:
                        chunk = run_similarity(chunk,header,**mol_reference)
                    dataset[ds_key].stitch_chunks()

                elif "dataframe_smiles_ref" in next_key:
                    ref_key = pipeline[next_key]
                    ref_dataset = load_data(ref_key)
                    next_next_key = get_shifted_key(pipeline,next_key,1)
                    ref_column = pipeline[next_next_key]
                    #pass in the reference df as its DataSet object
                    mol_reference = { ref_key : [ ref_dataset[ref_key] , ref_column, norm] }
                    n = 0
                    save_obj(n,'n_temp')
                    max = len(dataset[ds_key].dataframe.index)
                    save_obj(max,'max_temp')
                    dataset[ds_key].chunks = [ run_similarity(df,header,**mol_reference) for df in dataset[ds_key].chunks]
                    dataset[ds_key].stitch_chunks()


        return render_template('results_page.html', Results = Markup(dataset[ds_key].dataframe.to_html()))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
