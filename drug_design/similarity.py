
#this approach was taken from: https://stackabuse.com/levenshtein-distance-and-text-similarity-in-python/
import numpy as np
import pandas as pd

#Take a dataframe with SMILES strings and one target SMILES then add a column of the scores
def run_similarity(dataframe,column_key,SMILES):

    if isinstance(dataframe, pd.DataFrame):

        if column_key in dataframe.columns:

            dataframe['sim_score_' + str(SMILES)] = dataframe[column_key].apply(levenshtein, args = (SMILES,))
            return dataframe

        else:
            print("Error: I'm sorry I couldn't find that column in the dataframe you submitted")
    else:
        print("Error: It looks like your dataframe isn't a pandas DataFrame")

#the minimum number of insertions, deletions and substitutions required to turn 1 string into another
def levenshtein(seqA, seqB):
    seq1 = str(seqA)
    seq2 = str(seqB)
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros ((size_x, size_y))
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x-1] == seq2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
    #print (matrix)
    return (matrix[size_x - 1, size_y - 1])
