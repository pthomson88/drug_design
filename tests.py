from datasets.DataSets import DataSet
from save_load import load_obj
from similarity import run_similarity, levenshtein
import pandas as pd

#Similarity module tests:
def sim_test():
    #expected score 0
    SMILES = 'dog'
    dataframe = pd.DataFrame(data = {"col1" : ["dog"]})
    df = run_similarity(dataframe,"col1","dog")
    assert df['sim_score_dog'] == 0
#load_data tests


#Happy path using test test_download
#Keys don't match
#Not a csv
