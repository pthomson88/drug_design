
#this approach was taken from: https://stackabuse.com/levenshtein-distance-and-text-similarity-in-python/
import numpy as np
import pandas as pd

#Take a dataframe with SMILES strings and one target SMILES then add a column of the scores
def run_similarity(dataframe,column_key,**kwargs):

#The first argument must be a dataframe
    if isinstance(dataframe, pd.DataFrame):
        #You need to put in a valid argument for a column header for teh source dataframe
        if column_key in dataframe.columns:

        #There should only be one key in kwargs - the name of the second argument passed
            for key in kwargs:

                #If the second argument isn't a list, dictionary or dataframe:
                if not isinstance(kwargs[key], (pd.DataFrame, list, dict)):

                    SMILES = str(kwargs[key])
                    dataframe['sim_score_' + str(SMILES)] = dataframe[column_key].apply(levenshtein, args = (SMILES,))

                    return dataframe


                #If the argument passed is a dataframe
                elif isinstance(kwargs[key], pd.DataFrame):

                    print(kwargs[key].columns)
                    col_reference = input("\nWhich column contains your reference SMILES? :> ")

                    #make sure that the column exists
                    if col_reference in kwargs[key].columns:

                        #We need to apply the lev_aggregator function this time and unpack the result into new columns
                        df2 = kwargs[key]
                        dataframe['new'] = dataframe[column_key].apply(lev_aggregator, args = (df2[col_reference],col_reference,))
                        dataframe['sim_match_' + str(key) + str(col_reference)], dataframe['sim_score_' + str(key) +"_"+ str(col_reference)] = dataframe.new.str
                        dataframe.drop(['new'], axis=1)

                        return dataframe

                    else:
                        print("Error: I'm sorry I couldn't find that column in the reference dataframe you submitted")

        else:
            print("Error: I'm sorry I couldn't find that column in the source dataframe you submitted")


    else:
        print("Error: It looks like your dataframe isn't a pandas DataFrame")

#Scores every SMILES in list against one and returns only the max score
def lev_aggregator(seqA, colB, col_header):

    colB['result'] = colB.apply(levenshtein, args = (seqA,))
    idx = colB['result'].idxmin()

    return colB[idx] , colB['result'].min()



#the minimum number of insertions, deletions and substitutions required to turn 1 string into another
#the minimum number of insertions, deletions and substitutions required to turn 1 string into another
def levenshtein(seqA, seqB):
    seq1 = str(seqA)
    seq2 = str(seqB)
    if seq1 == "" or seq1.lower() == "nan" or seq2 == "" or seq2.lower() == "nan":
        return 10000
    else:
        if len(seq1) > len(seq2):
            #make sure the shorter string is seq1
            seq1, seq2 = seq2, seq1
            #don't calculate bad strings  - just penalise immediately
        size_x = len(seq1)
        size_y = len(seq2)
        v0 = [0]+[ i for i in range(1,size_x+1)]
        v1 = [ j for j in range(1,size_y+1)]

        #Note that only swaps and deletions are considered to map the longest string to the shortest
        matrix = [v0] + [ v0 :=
            ( [v1[i]] +
                [
                    min(v0[j],(v0[j + 1] + 1))
                    if seq1[j] == seq2[i]
                    else min((v0[j] + 1),(v0[j + 1] + 1))
                    for j in range(size_x)
                ]
            )
            for i in range(size_y)
        ]
        return (matrix[size_y][size_x])
