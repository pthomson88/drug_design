from drug_design.load_data import *
from drug_design.similarity import run_similarity
from drug_design.save_load import *
from drug_design.term_num_opts import *
from drug_design.gsheet_store import *
from drug_design.datastore_connect import datastore_connect

def main_term():
    #connect to the database - we don't use it yet but we will 
    ds_client = datastore_connect

    quit = False
    #when we start for the first time dataframes should be empty
    dataframes = {}
    try:
        while quit == False:
            #first we're going to need to import some data
            print("\n ******************************************************** \n ** You can hit Ctrl-C at any time to exit the program ** \n ********************************************************")
            while not dataframes:

                print("\n Before we get started you're going to need to load some data.\n ")

                dataframes = term_load_data()
                if dataframes == False:
                    print("** Remember you can hit Ctrl-C to quit at any time **")

            retry = True
            while retry == True:
                print("What would you like to do next? \n Your options are:")
                next_action = input(" \n1. Similarity score \n2. Load more data \n3. Clear my loaded data \n4. Link or unlink a dataset \n5. Quit \n \n :> ")

                if next_action == "1":

                    print(
                    "\n Which dataset will you use? Your options are:\n")

                    options  = [key for key in dataframes]
                    ds_key = selector(options)

                    regoz = 'y'
                    while regoz.lower() =='y':

                        print(dataframes[ds_key].headers)
                        print("")

                        columns = input("Which column contains the smiles you'd like to compare to :> ")
                        print("")

                        if not columns in dataframes[ds_key].headers:
                            print("Sorry, that's not a valid entry, please type a column header exactly")
                            regoz = input("Would you like to try again? Type Y for yes or N for no :> ")
                        else:
                            regoz = 'n'


                    SMILES = input("Paste or type the SMILES you'd like to score similarity for :> ")
                    print("")

                    #indicates that levenshtein_norm should be used ratehr than levenshtein - see similarity module
                    print("Would you like to use normalised scores?")
                    print("This balances the score for the length of Smiles - exactly matching smiles score 100, completely dissimilar strings score 0")
                    norm_on = input("Type Y to turn normalisation on or N to keep it off :> ")

                    if norm_on.lower() == "y":
                        norm = True
                        print("Normalised scoring on")
                    else:
                        norm = False
                        print("Normalised scoring off")

                    mol_reference = {"SMILES" : [SMILES, norm]}

                    dataframes[ds_key].dataframe = run_similarity(dataframes[ds_key].dataframe,columns,**mol_reference)

                    print(dataframes[ds_key].dataframe)

                elif next_action == "2":

                    print("")
                    print("Lets load some more data: ")
                    dataframes.update(term_load_data())

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

if __name__ == '__main__':
    # execute only if run as the entry point into the program
    main_term()
