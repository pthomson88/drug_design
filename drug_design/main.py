from .load_data import load_data
from .similarity import run_similarity
import pandas as pd

#The main function to take you through options
def main():
    #first we're going to need to import some data
    dataframes = {}
    while not dataframes:
        print("")
        print("Before we get started you're going to need to load some data.")
        print("")

        dataframes = load_data()

    print("What would you like to do next? \n Your options are:")

    next_action = input(" \n1. Similarity score \n2. Load more data \n3. Quit \n \n :> ")

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
                print("Sorry, that's not a valid entry, please select a number")
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

        dataframes[ds_key].dataframe = run_similarity(dataframes[ds_key].dataframe,columns,SMILES)

        print(dataframes[ds_key].dataframe)

    elif next_action == "2":

        print("")
        print("Lets load some different data: ")
        datasets = load_data()

    else:
        print("See you next time...")
