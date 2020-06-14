
#this approach was taken from: https://stackabuse.com/levenshtein-distance-and-text-similarity-in-python/
import numpy as np
import pandas as pd

from multiprocessing import Pool, cpu_count

#Take a dataframe with SMILES strings and one target SMILES then add a column of the scores
def run_similarity(dataframe,column_key,**kwargs):

#The first argument must be a dataframe
    if isinstance(dataframe, pd.DataFrame):
        #You need to put in a valid argument for a column header for the source dataframe
        if column_key in dataframe.columns:
        #There should only be one key in kwargs - the name of the second argument passed
            for key in kwargs:
                #If the second argument isn't a list, dictionary or dataframe:
                if isinstance(kwargs[key][0], (str, int)):
                    SMILES = str(kwargs[key][0])
                    norm = kwargs[key][1]
                    score_col = 'sim_score_' + SMILES
                    if norm == True:
                        dataframe[score_col] = dataframe[column_key].apply(levenshtein_norm, args = (SMILES,))
                    else:
                        dataframe[score_col] = dataframe[column_key].apply(levenshtein, args = (SMILES,))
                    print("SUCCESS!!!")
                    print(dataframe)
                    return dataframe
                #The dataframe will be as its dataset object so we need to look at the dataframe parameter
                elif isinstance(kwargs[key][0].dataframe, pd.DataFrame):
                    #there should only be a single column passed
                    ref_column = kwargs[key][1]
                    norm = kwargs[key][2]
                    #Double check we've not screwed up by looking at the headers parameter
                    if ref_column in kwargs[key][0].headers:
                        print("Calculating")
                        print(".")
                        df2_dataset = kwargs[key][0]

                        #We need to apply the lev_aggregator function this time and unpack the result into new columns
                        dataframe['new'] = dataframe[column_key].apply(lev_aggregator, args = (df2_dataset,ref_column,norm,))
                        score_col = 'sim_score_' + str(key) +"_"+ str(ref_column)
                        try:
                            print("trying updates...")
                            dataframe['sim_match_' + str(key) +"_"+ str(ref_column)], dataframe[sort_col] = dataframe.new.str
                        except FutureWarning:
                            print("Ignoring FutureWarning...")
                        except:
                            print("Ignoring some other exception...")
                        finally:
                            print("dropping the processing column...")
                            dataframe = dataframe.drop(columns=['new'])
                            print("SUCCESS!!!")
                            print(dataframe)
                            return dataframe

                    else:
                        print("Error: I'm sorry I couldn't find that column in the reference dataframe you submitted")
        else:
            print("Error: I'm sorry I couldn't find that column in the source dataframe you submitted")
    else:
        print("Error: It looks like your dataframe isn't a pandas DataFrame")

#Scores every SMILES in list against one and returns only the max score
def lev_aggregator(seqA, colB, col_header,norm):
    #remember that colB is a dataset object - let's add a results column to each chunk
    df_col = colB.dataframe[col_header]
    max_cpu = cpu_count()
    #result = [ levenshtein(seqA, x) for x in df_col ]
    if norm == True:
        with Pool(max_cpu) as p:
            result = p.starmap(levenshtein_norm,[(seqA, x) for x in df_col],100)
            #result = [ levenshtein(seqA, x) for x in df_col ]
    else:
        with Pool(max_cpu) as p:
            result = p.starmap(levenshtein,[(seqA, x) for x in df_col],100)
            #result = [ levenshtein(seqA, x) for x in df_col ]
    colB.dataframe['result'] = pd.Series(result)
    #stitch the chunks back together and pull out the best score from the whole dataframe
    if norm == True:
        idx = colB.dataframe['result'].idxmax()
        min = colB.dataframe['result'].max()
    else:
        idx = colB.dataframe['result'].idxmin()
        min = colB.dataframe['result'].min()
    return colB.dataframe[col_header][idx] , min

#the minimum number of insertions, deletions and substitutions required to turn 1 string into another
def levenshtein(seqA, seqB):
    seq1 = str(seqA)
    seq2 = str(seqB)
    if seq1 == "" or seq1.lower() == "nan" or seq2 == "" or seq2.lower() == "nan":
        return 10000
    else:
        if len(seq1) > len(seq2):
            seq1, seq2 = seq2, seq1
        return levenshtein_calc(seq1,seq2)

#the minimum number of insertions, deletions and substitutions required to turn 1 string into another
def levenshtein_norm(seqA, seqB):
    seq1 = str(seqA)
    seq2 = str(seqB)
    if seq1 == "" or seq1.lower() == "nan" or seq2 == "" or seq2.lower() == "nan":
        return 10000
    else:
        if len(seq1) > len(seq2):
            seq1, seq2 = seq2, seq1
        max = len(seq2)
        raw_score = levenshtein_calc(seq1,seq2)
        result = 100 * (max - raw_score) / max
        return result

def levenshtein_calc(seq1,seq2):
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
