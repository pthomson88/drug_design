from drug_design.load_data import load_data
from drug_design.similarity import run_similarity
from drug_design.gsheet_store import gsheet_store
from drug_design.datasets.DataSets import DataSet
from drug_design.save_load import load_obj
import pandas as pd
import drug_design

from flask import Flask, jsonify, request, render_template
from wtforms import Form, BooleanField, StringField, validators

app = Flask(__name__)

#The main function to take you through option
@app.route("/")
def main():
    msg = "Welcome to the main page"
    a = "You can hit Ctrl-C at any time to exit the program \n "
    b = "Before we get started you're going to need to load some data."
    return render_template('welcome_page.html', var1 = msg, var2 = a, var3 = b)

@app.route('/example_load_data/')
def example_load_data_form():
    return render_template('my-form.html', variable = '12345', variable2 = 'next_variable')

#A Page for loading data example
@app.route('/example_load_data/', methods=['POST'])
def example_load_data_post():
    text = request.form['text']
    text2 = request.form['text2']
    processed_text = text.upper() + text2.upper()
    return processed_text

#Load data
@app.route('/load_data/')
def load_data_form():
    url_dict = load_obj('url_dict')
    return render_template('load_data_form.html', Datafiles = url_dict)

@app.route('/load_data/', methods=['POST'])
def load_data_post():
    key = request.form['dataset choice']
    loaded_data = load_data(key).to_html()
    return loaded_data




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
