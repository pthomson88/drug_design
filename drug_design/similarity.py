
#this approach was taken from: https://stackabuse.com/levenshtein-distance-and-text-similarity-in-python/
import numpy as np
import pandas as pd
import pathos.multiprocessing as mp
from functools import partial
from itertools import repeat, starmap
import settings
import datetime

def parallelize_dataframe(series, func, **kwargs):

    start = datetime.datetime.now()
    cores = settings.CORES

    if "cores" in kwargs:
        try:
            cores = int(kwargs["cores"])
        except:
            print("Cores passed not an integer - keeping default")

    del kwargs["cores"]

    #series_split = np.array_split(series, settings.CORES)
    pool = mp.Pool(cores)
    partial_func = partial(func,**kwargs)
    #df = pd.concat( pool.starmap( func, params )
    result = pool.map( partial_func, series )
    pool.close()
    pool.join()

    end  = datetime.datetime.now()
    time = end - start
    print("Processing time: " + str(time.total_seconds()) + " seconds")
    
    return result

#Take a dataframe with SMILES strings and one target SMILES then add a column of the scores
def run_similarity(dataframe,column_key,mol_reference,**kwargs):

    #The first argument must be a dataframe
    if isinstance(dataframe, pd.DataFrame):
        #You need to put in a valid argument for a column header for the source dataframe
        if column_key in dataframe.columns:
        #There should only be one key in kwargs - the name of the second argument passed
            for key in mol_reference:
                #If the second argument isn't a list, dictionary or dataframe:
                if isinstance(mol_reference[key][0], (str, int)):
                    SMILES = str(mol_reference[key][0])
                    norm = mol_reference[key][1]
                    score_col = 'sim_score_' + SMILES
                    if norm == True:
                        dataframe[score_col] = dataframe[column_key].apply(levenshtein_norm, args = (SMILES,))
                    else:
                        dataframe[score_col] = dataframe[column_key].apply(levenshtein, args = (SMILES,))
                    print("SUCCESS!!!")
                    print(dataframe)
                    return dataframe
                #The dataframe will be as its dataset object so we need to look at the dataframe parameter
                elif isinstance(mol_reference[key][0], pd.DataFrame):
                    #there should only be a single column passed
                    ref_column = mol_reference[key][1]
                    norm = mol_reference[key][2]
                    #Double check we've not screwed up by looking at the headers parameter
                    if ref_column in mol_reference[key][3]:
                        print("Calculating")
                        print(".")
                        df2_dataset = mol_reference[key][0]

                        #We need to apply the lev_aggregator function this time and unpack the result into new columns
                        if "multiprocess" in kwargs:
                            cores = kwargs['multiprocess']
                            dataframe['new'] = parallelize_dataframe(dataframe[column_key],lev_aggregator, colB = df2_dataset, col_header = ref_column, norm = norm, cores = cores )
                        else:
                            dataframe['new'] = dataframe[column_key].apply(lev_aggregator, args = (df2_dataset, ref_column, norm,))

                        score_col = 'sim_score_' + str(key) +"_"+ str(ref_column)
                        try:
                            print("trying updates...")
                            dataframe['sim_match_' + str(key) +"_"+ str(ref_column)], dataframe[score_col] = dataframe.new.str
                        except FutureWarning:
                            print("Ignoring FutureWarning...")
                        except:
                            print("Ignoring some other exception...")
                        dataframe = dataframe.drop(['new'],axis=1)
                        if norm == True:
                            dataframe = dataframe.sort_values(score_col,ascending=False)
                        else:
                            dataframe = dataframe.sort_values(score_col)
                        print("SUCCESS!!!")
                        return dataframe

                    else:
                        print("Error: I'm sorry I couldn't find that column in the reference dataframe you submitted")
        else:
            print("Error: I'm sorry I couldn't find that column in the source dataframe you submitted")
    else:
        print("Error: It looks like your dataframe isn't a pandas DataFrame")

#Scores every SMILES in list against one and returns only the max score
def lev_aggregator(seqA, colB, col_header, norm):
    #if not isinstance(colB, pd.Series):
    #    print("Lev aggregator needs a dataframe for colB")
    #remember that colB is a dataset object - let's add a results column to each chunk
    df_col = colB[col_header]
    #result = [ levenshtein(seqA, x) for x in df_col ]
    if norm == True:
        result = [levenshtein_norm(seqA,x) for x in df_col]
    else:
        #result = p.starmap(levenshtein,[(seqA, x) for x in df_col],100)
        result = [ levenshtein(seqA, x) for x in df_col ]
    colB['result'] = pd.Series(result)
    #stitch the chunks back together and pull out the best score from the whole dataframe
    if norm == True:
        idx = colB['result'].idxmax()
        min = colB['result'].max()
    else:
        idx = colB['result'].idxmin()
        min = colB['result'].min()
    return colB[col_header][idx] , min

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
        return 0
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
