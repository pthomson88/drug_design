#We're in the test directory so we need to jump back to the root dir to find modules
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from drug_design.load_data import *
from drug_design.similarity import *
from drug_design.gsheet_store import *
from drug_design import UrlDict
from drug_design.save_load import save_obj, load_obj
from main_term import main_term
from drug_design.term_num_opts import selector

import pandas as pd
import pytest
import io

#we might need to mokeypatch a test url_dict for some tests
class MockUrlDict:

    # mock out sessions so that the following is always returned on initialising a session
    @staticmethod
    def mock_url_dict(self, *args, **kwargs):
        self.name = "test_url_dict"
        self.dictionary = {
            'test_download': 'https://docs.google.com/spreadsheets/d/1o__Ar6O65DowaqCATTNjeK9kvr9NXJiX4Slo0tK-e4k/export?format=csv',
            'chembl26_ph3_ph4': 'https://docs.google.com/spreadsheets/d/1djFMETW8A111b7xv421L9jJWtIIN7Sn0ap95u8ml8eQ/export?format=csv',
            'chembl26_similar_protein_mols': 'https://docs.google.com/spreadsheets/d/1upjwIomN7kIgXhRu9NFU9C0WK5S0lJSOpVC_BH1OBxs/export?format=csv',
            'not_a_csv': 'https://docs.google.com/spreadsheets/d/1Rw9DkxM_rzmS59qPS-TF6JV9MAu8LJtB/export?format=csv'
            }
        self.webdictionary = self.dictionary

#Main module tests
#If I don't answer numerically to a numbered choice list I should be shown an error and askey to try again
#The seector module handles this across the board, below is simply a unit test for that module
def test_selector_choices(monkeypatch):

    capturedOutput = io.StringIO()          # Create StringIO object
    sys.stdout = capturedOutput                #  and redirect stderr.

    responses = iter(['this is not a number','n'])
    monkeypatch.setattr('builtins.input', lambda msg: next(responses))

    selector(["test option 1", "test option 2", "test option 3"])

    sys.stdout = sys.__stdout__

    assert "error" in capturedOutput.getvalue().lower()

#Similarity module tests:
#check that the similarity score makes sense in a basic test using main as entry point
def test_sim(monkeypatch):

    monkeypatch.setattr('drug_design.UrlDict.UrlDict.__init__',MockUrlDict.mock_url_dict)

    capturedOutput = io.StringIO()
    sys.stdout = capturedOutput

    #responses "1" for "test_download", "2" for "Similarity score", "2" for "a"...
    # ... 5 for "manual entry", "dog" for SMILES,  "Y" for normalise...
    #..."1" for "View and run pipeline", "Y" for run, "" for default cores, the 6 to "Quit"
    responses = iter([1,2,2,5,"dog","Y",1,"Y","",6])
    monkeypatch.setattr('builtins.input', lambda msg: next(responses))

    main_term()

    sys.stdout = sys.__stdout__

    #check the new column is added
    assert "sim_score_dog" in capturedOutput.getvalue()

#check similarity score directly
def test_sim2():
    #Set the reference string to be "dogs" and normalisation to be off
    mol_reference = {"SMILES" : ["dogs",False]}
    dataframe = pd.DataFrame(data = {"col1" : ["dog"]})

    dataframe = run_similarity(dataframe,"col1",mol_reference)

    assert isinstance(dataframe, pd.DataFrame) and int(dataframe["sim_score_dogs"]) == 1

#Tests for non standard entities - e.g. integers, floats and lists
def test_sim_int():
    #expected score 3 - an integer should be treated as a string by the similarity algorithm or return an error message
    mol_reference = {"SMILES" : [543,False]}
    dataframe = pd.DataFrame(data = {"col1" : ["dog"]})

    capturedOutput = io.StringIO()                # Create StringIO object
    sys.stdout = capturedOutput                   #  and redirect stdout.

    df = run_similarity(dataframe,"col1",mol_reference)

    sys.stdout = sys.__stdout__

    assert ( "error" in capturedOutput.getvalue().lower() ) or ( int(df['sim_score_' + str(mol_reference["SMILES"][0])].values) == 3 )

#Tests for errors being returned if column keys don't match
def test_sim_keys_dont_match():
    mol_reference = {"SMILES" : ["dog",False]}
    dataframe = pd.DataFrame(data = {"col1" : ["dog"]})

    capturedOutput = io.StringIO()                # Create StringIO object
    sys.stdout = capturedOutput                   #  and redirect stdout.

    df = run_similarity(dataframe,"col2",mol_reference)

    sys.stdout = sys.__stdout__

    assert "error" in capturedOutput.getvalue().lower()

#test for if dataframe isn't a dataframe
def test_sim_not_a_df():
    mol_reference = {"SMILES" : ["dog",False]}
    dataframe = {"col1" : ["dog"]}        #dataframe is a dictionary instead

    capturedOutput = io.StringIO()                # Create StringIO object
    sys.stdout = capturedOutput                   #  and redirect stdout.

    df = run_similarity(dataframe,"col1",mol_reference)

    sys.stdout = sys.__stdout__

    assert "error" in capturedOutput.getvalue().lower() #some sort of error message should be displayed

#Test to check happy path for checking similarity fo strings in one dataframe to those in another
def test_sim_df_df():

    df_source = pd.DataFrame(data = {"col1" : ["dog"]})
    df_reference = pd.DataFrame(data = {"col2" : ["dogs", "cats"]})

    #... for dataframe SMILES = { reference_dataset_key : [reference dataframe : pandas.DataFrame, reference_column: string, norm : boolean, reference_dataset_headers : list ] }
    mol_reference = {"df_reference" : [df_reference,"col2",False,["col2"]]}

    result = run_similarity(df_source,"col1",mol_reference)

    assert result['sim_score_df_reference_col2'].values[0] == 1

#test levenshtein normalisation happy path
def test_sim_norm_happy():
    seq1 = "dog"
    seq_long = "dogcat"
    #if normalisation is on the score should be 50 - if not it will be 3
    assert levenshtein_norm(seq1,seq_long) == 50

#test levenshtein normalisation long and short mismatches
def test_sim_norm_lengthcheck():
    seq1 = "dog"
    seq2 = "dot"
    seq3 ="ddoogg"
    seq4 = "ddoott"
    short = levenshtein_norm(seq1,seq2)
    long = levenshtein_norm(seq3,seq4)
    #if normalisation is on the score of both should be 66
    #if its off the short string comparison will score 1 and the long 2
    assert short == long

#basic unit test - test download should be a dataframe - use MockUrlDict
def test_load_data(monkeypatch):

    monkeypatch.setattr('drug_design.UrlDict.UrlDict.__init__',MockUrlDict.mock_url_dict)
    i = load_data("test_download")
    df = i["test_download"].dataframe

    assert isinstance(df, pd.DataFrame)

#Keys don't match
def test_load_data_fail1(monkeypatch):

    monkeypatch.setattr('drug_design.UrlDict.UrlDict.__init__',MockUrlDict.mock_url_dict)
    capturedOutput = io.StringIO()          # Create StringIO object
    sys.stdout = capturedOutput                   #  and redirect stdout.

    i = load_data("an unlikely name for a dataset")

    sys.stdout = sys.__stdout__                   # Reset redirect.

    assert ("error" in capturedOutput.getvalue().lower())

#Can't be converted to a csv
def test_no_csv(monkeypatch):

    monkeypatch.setattr('drug_design.UrlDict.UrlDict.__init__',MockUrlDict.mock_url_dict)

    capturedOutput = io.StringIO()          # Create StringIO object
    sys.stdout = capturedOutput                   #  and redirect stdout.

    #next try and load it into a dataframe - this will fail
    i = load_data("not_a_csv")

    sys.stdout = sys.__stdout__                   # Reset redirect.

    assert "error" in capturedOutput.getvalue().lower()
    #you should end up with an error message

#Tests for the add_gsheet_url module
#add a url to the dict and check it's there
def test_gsheet_happy(monkeypatch):

    test_url_dict = {"test_url_dict" : "for testing only"}
    save_obj(test_url_dict, "test_url_dict")

    # 1: Link new dataset, "test_entry_1" : Google ID, "test_key" : name , "n" : quit
    responses = iter([1,'test_entry1', 'test_key_1', "n"])
    monkeypatch.setattr('builtins.input', lambda msg: next(responses))

    #option to use a test url_dict built into module for testing purposes
    j = gsheet_store(test = "test_url_dict")
    k = load_obj("test_url_dict")

    assert 'test_key_1' in k and 'test_entry1' in k['test_key_1']

#remove url to the dict and check it's worked
def test_gsheet_delete(monkeypatch):

    #make sure there is an appropriate dict to delete from
    test_url_dict = {"test_url_dict" : "for testing only", "test_key_1" : "junk test data to be removed"}
    save_obj(test_url_dict, "test_url_dict")

    # 2: Unlink dataset, 2 : name = "test_key" , "n" : quit
    responses = iter([2,2,"n"])
    monkeypatch.setattr('builtins.input', lambda msg: next(responses))

    j = gsheet_store(test = "test_url_dict")
    k = load_obj('test_url_dict')

    assert not 'test_key_1' in k

#Try and load a non-existant objects
def test_load_absent_obj():

    k = load_obj('not_and_object')

    assert "error" in k.lower()
    #you should end up with an error message
