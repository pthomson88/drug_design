from .load_data import load_data
from .similarity import run_similarity

import pandas as pd
import pytest
import io
import sys

#Similarity module tests:
#check that the similarity score makes sense in a basic test
def test_sim():
    #expected score 1
    word = "dogs"
    dataframe = pd.DataFrame(data = {"col1" : ["dog"]})
    df = run_similarity(dataframe,"col1",word)

    assert int(df['sim_score_' + word].values) == 1

#Tests for non standard entities - e.g. integers, floats and lists

#Tests for errors being returned if column keys don't match

#test for if dataframe isn't a dataframe

#load_data tests:
#Happy path using test test_download
def test_load_data(monkeypatch):

    # monkeypatch the "input" function, so that it returns "test_download".
    # This simulates the user entering "test_download" in the terminal:
    #test_download will both act as a suitable key for data and an escape for the while loop
    monkeypatch.setattr('builtins.input', lambda x: "test_download")

    i = load_data()
    df = i["test_download"].dataframe

    assert isinstance(df, pd.DataFrame)

#Keys don't match
def test_load_data_fail1(monkeypatch):

    monkeypatch.setattr('builtins.input', lambda x: "an unlikely anme for a dataset")
    capturedOutput = io.StringIO()          # Create StringIO object
    sys.stdout = capturedOutput                   #  and redirect stdout.

    i = load_data()
    df = i["an unlikely name for a dataset"].dataframe
    sys.stdout = sys.__stdout__                   # Reset redirect.

    assert ("error" in capturedOutput.getvalue() or "Error" in capturedOutput.getvalue() or "ERROR" in capturedOutput.getvalue() ) and not isinstance(df, pd.DataFrame)

#Not a csv

#Tests for the add_gsheet_url module
