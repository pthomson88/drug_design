from datasets.DataSets import DataSet
from save_load import load_obj
from similarity import run_similarity, levenshtein
import pandas as pd
import pytest

#Similarity module tests:
def test_sim():
    #expected score 0
    word = "dogs"
    dataframe = pd.DataFrame(data = {"col1" : ["dog"]})
    df = run_similarity(dataframe,"col1",word)

    assert int(df['sim_score_' + word].values) == 1
#load_data tests


#Happy path using test test_download
#Keys don't match
#Not a csv
