#We're in the test directory so we need to jump back to the root dir to find modules
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import pytest
from flask import url_for, request
from lxml import etree
import pandas as pd

from main import create_app
from drug_design.save_load import save_obj, load_obj

#Simply checks that the "/index/" url actually loads a page
def test_index_loads(client):
    result = client.get("/index/").status_code
    assert  result == 200

#Checks that normalisation checkbox actually normalises
def test_norm_pipeline(client):
    #GIVEN I have checked the normalise checkbox on the choose columns page
    #WHEN I press submit
    #THEN My pipeline dictionary includes "normalise_scores : True"
    pipeline = {"source_key" : "test normalisation"}
    save_obj(pipeline, 'tmp_pipeline')

    response = client.post(
          url_for('similarity_score_page'),
          data = dict(column_choice = "", what_smiles = "single_smiles", norm_on="norm_true"),
          follow_redirects=True
          )
    assert response.status_code == 200

    pipeline = load_obj('tmp_pipeline')
    #print included for loggin to console if test fails
    print("Pipeline contents:")
    print(pipeline)
    assert pipeline['normalise_scores'] == True
    pipeline = {"source_key" : ""}
    save_obj(pipeline, 'tmp_pipeline')


def test_norm_single_smiles(client):
    #GIVEN I have a pipeline including normalisation and single smiles similarity scoring
    #AND I am on the view pipline page
    #WHEN I press submit to run the pipeline
    #THEN The similarity scores in my results are normalised
    pipeline = {"source_key":"test_download", "similarity_score": "a", "normalise_scores": "True", "single_smiles": "dog"}
    save_obj(pipeline, 'tmp_pipeline')
    print("Pipeline contents:")
    print(pipeline)
    result = client.post(url_for('generate_results_2'))
    assert  result.status_code == 200

    sim_result = result.data
    print(sim_result)
    table = pd.read_html(sim_result)
    assert table[0]['sim_score_dog'][2] == 33.333333

    pipeline = {"source_key" : ""}
    save_obj(pipeline, 'tmp_pipeline')


def test_norm_df_smiles(client):
    #GIVEN I have a pipeline including normalisation and dataframe smiles similarity scoring
    #AND I am on the view pipline page
    #WHEN I press submit to run the pipeline
    #THEN The similarity scores in my results are normalised
    #AND the correct best score is returned based on the normalised scores
    pipeline = {"source_key":"test_download", "similarity_score": "a", "normalise_scores": "True", "dataframe_smiles_ref": "test_download_2", "dataframe_smiles_col": "animal"}
    save_obj(pipeline, 'tmp_pipeline')
    print("Pipeline contents:")
    print(pipeline)
    result = client.post(url_for('generate_results_2'))
    assert  result.status_code == 200

    sim_result = result.data
    print(sim_result)
    table = pd.read_html(sim_result)
    assert table[0]['sim_match_test_download_2_animal'][1] == "cat"
    assert table[0]['sim_score_test_download_2_animal'][1] == 33.333333

    pipeline = {"source_key" : ""}
    save_obj(pipeline, 'tmp_pipeline')
