from drug_design.load_data import *
from drug_design.similarity import *
from drug_design.gsheet_store import *
from drug_design.save_load import save_obj, load_obj
from main import *

import pandas as pd
import pytest
import io
import sys

#Main module tests
#If I don't answer numerically to a numbered choice list I should be shown an error and askey to try again
def test_main_choices(monkeypatch):

    capturedOutput = io.StringIO()          # Create StringIO object
    sys.stdout = capturedOutput                #  and redirect stdout.

    responses = iter(["", 'this is not a number', '5'])
    monkeypatch.setattr('builtins.input', lambda msg: next(responses))

    DrugDesign.main()

    sys.stdout = sys.__stdout__

    assert "error" in capturedOutput.getvalue().lower()

#Similarity module tests:
#check that the similarity score makes sense in a basic test using main as entry point
def test_sim(monkeypatch):

    capturedOutput = io.StringIO()
    sys.stdout = capturedOutput

    responses = iter(["test_download", "N", "1", "1", "a", "dog", "5"])
    monkeypatch.setattr('builtins.input', lambda msg: next(responses))

    DrugDesign.main()

    sys.stdout = sys.__stdout__

    #check the new column is added
    assert "sim_score_dog" in capturedOutput.getvalue()

#check similarity score directly
def test_sim2():
    word = {"word" : "dogs"}
    dataframe = pd.DataFrame(data = {"col1" : ["dog"]})

    dataframe = run_similarity(dataframe,"col1",**word)

    assert isinstance(dataframe, pd.DataFrame) and int(dataframe["sim_score_dogs"]) == 1

#Tests for non standard entities - e.g. integers, floats and lists
def test_sim_int():
    #expected score 3 - an integer should be treated as a string by the similarity algorithm or return an error message
    word = {"word" : 543}
    dataframe = pd.DataFrame(data = {"col1" : ["dog"]})

    capturedOutput = io.StringIO()                # Create StringIO object
    sys.stdout = capturedOutput                   #  and redirect stdout.

    df = run_similarity(dataframe,"col1",**word)

    sys.stdout = sys.__stdout__

    assert ( "error" in capturedOutput.getvalue().lower() ) or ( int(df['sim_score_' + str(word["word"])].values) == 3 )


#Tests for errors being returned if column keys don't match
def test_sim_keys_dont_match():
    #expected score 3 - an integer should be treated as a string by the similarity algorithm or return an error message
    word = {"word" : "dog"}
    dataframe = pd.DataFrame(data = {"col1" : ["dog"]})

    capturedOutput = io.StringIO()                # Create StringIO object
    sys.stdout = capturedOutput                   #  and redirect stdout.

    df = run_similarity(dataframe,"col2",**word)

    sys.stdout = sys.__stdout__

    assert "error" in capturedOutput.getvalue().lower()

#test for if dataframe isn't a dataframe
def test_sim_not_a_df():
    #expected score 3 - an integer should be treated as a string by the similarity algorithm or return an error message
    word = {"word" : "dog"}
    dataframe = {"col1" : ["dog"]}        #dataframe is a dictionary instead

    capturedOutput = io.StringIO()                # Create StringIO object
    sys.stdout = capturedOutput                   #  and redirect stdout.

    df = run_similarity(dataframe,"col2",**word)

    sys.stdout = sys.__stdout__

    assert "error" in capturedOutput.getvalue().lower() #some sort of error message should be displayed

#Test to check happy path for checking similarity fo strings in one dataframe to those in another
def test_sim_df_df(monkeypatch):

    df_source = pd.DataFrame(data = {"col1" : ["dog"]})
    df_reference = pd.DataFrame(data = {"col2" : ["dogs", "cats"]})

    df2 = {"df_reference" : df_reference}

    monkeypatch.setattr('builtins.input', lambda x: "col2")

    df_source = run_similarity(df_source,"col1",**df2)

    assert df_source['sim_score_df_reference_col2'].values[0] == 1

#Keys don't match in 2nd DataFrame

#2nd dataframe isn't a dataframe but should be useable - e.g. lists, strings, integers

#2nd dataframe isn't a dataframe and isn't useable - e.g. custom class object, image etc.

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

    monkeypatch.setattr('builtins.input', lambda x: "an unlikely name for a dataset")
    capturedOutput = io.StringIO()          # Create StringIO object
    sys.stdout = capturedOutput                   #  and redirect stdout.

    i = load_data()

    sys.stdout = sys.__stdout__                   # Reset redirect.

    assert ("error" in capturedOutput.getvalue().lower())

#Can't be converted to a csv
def test_no_csv(monkeypatch):

    #give responses in a sensible order - note the google id to a google image as the first
    responses = iter(['1Rw9DkxM_rzmS59qPS-TF6JV9MAu8LJtB', 'not_a_csv', 'N', 'not_a_csv', 'N'])
    monkeypatch.setattr('builtins.input', lambda msg: next(responses))
    capturedOutput = io.StringIO()          # Create StringIO object
    sys.stdout = capturedOutput                   #  and redirect stdout.

    #load the image as if it were a potential new dataset
    j = add_gsheet_url()
    #next try and load it into a dataframe - this will fail
    i = load_data()

    sys.stdout = sys.__stdout__                   # Reset redirect.

    assert "error" in capturedOutput.getvalue().lower()
    #you should end up with an error message

#Tests for the add_gsheet_url module
#add a url to the dict and check it's there
def test_gsheet_happy(monkeypatch):

    #make sure there is no test_key
    k = load_obj('url_dict')
    if 'test_key' in k:
        del k['test_key']
        save_obj(k,'url_dict')

    responses = iter(['1','test_entry1', 'test_key', 'N', '3'])
    monkeypatch.setattr('builtins.input', lambda msg: next(responses))

    j = gsheet_store()
    k = load_obj('url_dict')

    assert 'test_key' in k and 'test_entry1' in k['test_key']

#remove url to the dict and check it's worked
def test_gsheet_delete(monkeypatch):

    #make sure there is a test_key
    k = load_obj('url_dict')
    if not 'test_key' in k:
        k.update({'test_key' : 'junk test data to be removed'})
        save_obj(k,'url_dict')

    responses = iter(['2','test_key', 'N', '3'])
    monkeypatch.setattr('builtins.input', lambda msg: next(responses))

    j = gsheet_store()
    k = load_obj('url_dict')

    assert not 'test_key' in k

#Key mismatch in deleting data
def test_gsheet_delete(monkeypatch):

    capturedOutput = io.StringIO()          # Create StringIO object
    sys.stdout = capturedOutput                   #  and redirect stdout.

    #make sure there is a test_key
    k = load_obj('url_dict')
    if not 'test_key' in k:
        k.update({'test_key' : 'junk test data to be removed'})
        save_obj(k,'url_dict')

    responses = iter(['2','mismatched_key', 'N', '3'])
    monkeypatch.setattr('builtins.input', lambda msg: next(responses))

    j = gsheet_store()
    k = load_obj('url_dict')

    sys.stdout = sys.__stdout__                   # Reset redirect.

    assert 'test_key' in k and "error" in capturedOutput.getvalue().lower()

#Try and load a non-existant objects
def test_load_absent_obj():

        capturedOutput = io.StringIO()          # Create StringIO object
        sys.stdout = capturedOutput                   #  and redirect stdout.

        k=load_obj('not_and_object')

        sys.stdout = sys.__stdout__                   # Reset redirect.

        assert "error" in capturedOutput.getvalue().lower()
        #you should end up with an error message