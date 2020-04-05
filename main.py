from load_data import load_data
from similarity import run_similarity
import pandas as pd

#The main function to take you through options
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
    for key in dataframes:
        print(key)
    print("")
    ds_key = input(":> ")
    print("")

    df = dataframes[ds_key]
    print(df.headers)

    columns = input("Which column contains the smiles you'd like to compare to :> ")

    SMILES = input("Paste or type the SMILES you'd like to score similarity for :> ")

    datasets[ds] = run_similarity(df,columns,SMILES)

elif next_action == "2":

    print("")
    print("Lets load some different data: ")
    datasets = load_data()

else:
    print("See you next time...")
