from datasets.DataSets import DataSet
from save_load import load_obj
from similarity import run_similarity, levenshtein
from load_data import load_data

import pandas as pd
import pytest

#Similarity module tests:
def test_sim():
    #expected score 1
    word = "dogs"
    dataframe = pd.DataFrame(data = {"col1" : ["dog"]})
    df = run_similarity(dataframe,"col1",word)

    assert int(df['sim_score_' + word].values) == 1

#load_data tests
def test_load_data(monkeypatch):

    # monkeypatch the "input" function, so that it returns "Mark".
    # This simulates the user entering "Mark" in the terminal:
    #test_download will both act as a suitable key for data and an escape for the while loop
    monkeypatch.setattr('builtins.input', lambda x: "test_download")

    # go about using input() like you normally would:
    i = load_data()
    df = i["test_download"].dataframe

    assert isinstance(df, pd.DataFrame)



#Happy path using test test_download
#Keys don't match
#Not a csv
