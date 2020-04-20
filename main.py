from drug_design.load_data import load_data
from drug_design.similarity import run_similarity
from drug_design.gsheet_store import gsheet_store
from drug_design.datasets.DataSets import DataSet
from drug_design.save_load import load_obj, save_obj
from drug_design.key_increment import key_increment, get_shifted_key
import pandas as pd
import drug_design

from flask import Flask, jsonify, request, render_template, redirect, url_for, Markup
from wtforms import Form, BooleanField, StringField, validators

app = Flask(__name__)

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

    header = request.form['column_choice']
    pipeline = load_obj('tmp_pipeline')
    sim_key = key_increment("similarity_score",**pipeline)

    #The pipeline is updated with the sim_key kept unique by an inreasing integer
    pipeline[sim_key] = header
    save_obj(pipeline, 'tmp_pipeline')

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

    return redirect(url_for('main'))

@app.route('/do-things/sim-smiles/ref_dataframe/', methods=['GET','POST'])
def similarity_score_page_dataframe():

    ref_data_key = request.form["dataset_choice"]
    pipeline = load_obj('tmp_pipeline')
    new_entry = key_increment("dataframe_smiles_ref",**pipeline)
    pipeline[new_entry] = ref_data_key
    save_obj(pipeline, 'tmp_pipeline')
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
            next_key = get_shifted_key(pipeline,key,1)
            if "single_smiles" in next_key:
                mol_reference = {"SMILES" : pipeline[next_key]}
                for chunk in dataset[ds_key].chunks:
                    chunk = run_similarity(chunk,header,**mol_reference)
                dataset[ds_key].stitch_chunks()

            elif "dataframe_smiles_ref" in next_key:
                ref_key = pipeline[next_key]
                ref_dataset = load_data(ref_key)
                next_next_key = get_shifted_key(pipeline,next_key,1)
                ref_column = pipeline[next_next_key]
                #pass in the reference df as its DataSet object
                mol_reference = { ref_key : [ ref_dataset[ref_key] , ref_column] }
                n = 0
                save_obj(n,'n_temp')
                max = len(dataset[ds_key].dataframe.index)
                save_obj(max,'max_temp')
                dataset[ds_key].chunks = [ run_similarity(df,header,**mol_reference) for df in dataset[ds_key].chunks]
                dataset[ds_key].stitch_chunks()


    return render_template('results_page.html', Results = Markup(dataset[ds_key].dataframe.to_html()))


#print(dataframes[ds_key].headers)

#@app.route('/', methods=['POST'])
#def my_form_post():
#    text = request.form['text']
#    processed_text = text.upper()
#    return processed_text


def main_2():
    a = "\n******************************************************** \n** You can hit Ctrl-C at any time to exit the program ** \n********************************************************"
    return a
    quit = False
    #when we start for the first time dataframes should be empty
    dataframes = {}
    try:
        while quit == False:
            #first we're going to need to import some data
            while not dataframes:

                a = "\n******************************************************** \n** You can hit Ctrl-C at any time to exit the program ** \n********************************************************"
                b = "\nBefore we get started you're going to need to load some data.\n"

                message(a,b)

                dataframes = load_data()

            retry = True
            while retry == True:
                print("What would you like to do next? \n Your options are:")

                next_action = input(" \n1. Similarity score \n2. Load more data \n3. Clear my loaded data \n4. Link or unlink a dataset \n5. Quit \n \n :> ")

                if next_action == "1":
                    print("")
                    print("which dataset will you use? Your options are: ")
                    print("")

                    rego = 'Y'
                    ds_no = 0
                    while rego.lower() == 'y':
                        n=1
                        for key in dataframes:
                            print(str(n) + ". " + key)
                            n = n + 1
                        n=1
                        print("")
                        ds_no = int(input(":> "))
                        print("")

                        p=1
                        for key in dataframes:
                            if ds_no == p:
                                ds_key = key
                            p = p + 1
                        p=1
                        if not ds_key:
                            print("Error: Sorry, that's not a valid entry, please select a number")
                            rego = input("Would you like to try again? Type Y for yes or N for no :> ")
                        else:
                            rego = 'N'

                    regoz = 'Y'
                    while regoz.lower() =='y':

                        print(dataframes[ds_key].headers)
                        print("")

                        columns = input("Which column contains the smiles you'd like to compare to :> ")
                        print("")

                        if not columns:
                            print("Sorry, that's not a valid entry, please type a column header exactly")
                            regoz = input("Would you like to try again? Type Y for yes or N for no :> ")
                        else:
                            regoz = 'N'


                    SMILES = input("Paste or type the SMILES you'd like to score similarity for :> ")
                    print("")

                    mol_reference = {"SMILES" : SMILES}

                    dataframes[ds_key].dataframe = run_similarity(dataframes[ds_key].dataframe,columns,**mol_reference)

                    print(dataframes[ds_key].dataframe)

                elif next_action == "2":

                    print("")
                    print("Lets load some more data: ")
                    dataframes.update(load_data())

                elif next_action == "3":

                    print("")
                    print("Clearing the data currently loaded... ")
                    dataframes = {}

                elif next_action == "4":
                    gsheet_store()

                elif next_action == "5":
                    quit = True
                    print("See you next time... \n")
                    retry = False

                else:
                    print("Error: Something went wrong there. Make sure you are entering a number")
                    print("(Remember you can use Ctrl-C to escape at any time)")

    except KeyboardInterrupt:
        print("\nSee you next time... \n")

    #def main_func(self,instance):

        #textinput = TextInput(text="Hello World")

if __name__ == '__main__':
    app.run(debug=True)
