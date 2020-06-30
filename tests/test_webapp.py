#We're in the test directory so we need to jump back to the root dir to find modules
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import pytest
from flask import url_for, request
from lxml import etree
import pandas as pd
import requests
import functools

from main import create_app
from drug_design.save_load import save_obj, load_obj
from drug_design.key_increment import sub_key_gen
from drug_design.DataStorePipeLine import DataStorePipeLine
import settings

def csrf_token():
    url = settings.BE_URL_PREFIX + '/drug_design_backend/api/v1/token'
    r = requests.get(url, verify = settings.VERIFY_SSL)
    response = r.json()
    token = response['csrf_token']
    return token


def mock_cookies(*args,**kwargs):

    session_key = load_obj("test_session_key")

    mock_cookies = {

        "user_id" : "test",
        "session_key" : session_key

        }

    return mock_cookies

def withtestpipeline(func):

    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        #get a working session and pipeline (both in create_new_pipeline in DataStorePipeLine)
        token = csrf_token()
        test_pipeline_obj = DataStorePipeLine( False, user_id = "test" )
        session_key = test_pipeline_obj.session_key
        #We'll need this for mock cookies later
        save_obj(session_key,"test_session_key")

        kwargs['token'] = token
        kwargs['test_pipeline'] = test_pipeline_obj

        func(*args,**kwargs)

        #make session dormant and clear pipeline
        url = settings.BE_URL_PREFIX + '/drug_design_backend/api/v1/pipeline/test'
        json_data = { 'lock' : False, 'session_key' : test_pipeline_obj.session_key }
        r = requests.put(url, json=json_data, verify = False)

    return wrapper


#Simply checks that the "/index/" url actually loads a page
#We don't need the decorator but this is a good function to test if the decorator actually works
@withtestpipeline
def test_index_loads(client, *args,**kwargs):
    result = client.get("/index/").status_code
    assert  result == 200

#Checks that normalisation checkbox actually normalises
@withtestpipeline
def test_norm_pipeline(client, monkeypatch, *args,**kwargs):
    #GIVEN I have checked the normalise checkbox on the choose columns page
    #WHEN I press submit
    #THEN My pipeline dictionary includes "normalise_scores : True"

    test_pipeline = kwargs["test_pipeline"]
    test_session_key = test_pipeline.session_key

    post_data = {

        'tokenField' : kwargs['token'],
        'norm_on' : "norm_true",
        'column_choice' : "",
        'user_id' : "test",
        'session_key' : test_session_key,
        'what_smiles' : "single_smiles"

    }

    monkeypatch.setattr( 'main.fetch_session_cookies', mock_cookies )

    url = url_for('similarity_score_page')

    #monkeypatch in moack_cookies
    response = client.post( url, data = post_data, follow_redirects = True)

    #just fetch the pipeline directly to check if it has updated correctly
    url = settings.BE_URL_PREFIX + '/drug_design_backend/api/v1/pipeline/test'
    r = requests.get(url, verify = False)
    test_pipeline_entity = r.json()

    assert response.status_code == 200

    #will be the basic normalise key
    norm_key = sub_key_gen("normalise", "similarity_score", similarity_score_100 = "foo" )

    assert test_pipeline_entity[norm_key] == True

def test_norm_single_smiles(client,*args,**kwargs):
    #GIVEN I have a pipeline including normalisation and single smiles similarity scoring
    #AND I am on the view pipline page
    #WHEN I press submit to run the pipeline
    #THEN The similarity scores in my results are normalised
    pipeline = {"source_key":"test_download", "similarity_score": "a", "normalise_scores": True, "single_smiles": "dog" }
    save_obj(pipeline, 'tmp_pipeline')
    print("Pipeline contents:")
    print(pipeline)
    result = client.post(url_for('generate_results_2'))
    assert result.status_code == 200

    sim_result = result.data
    print(sim_result)
    table = pd.read_html(sim_result)
    assert table[0]['sim_score_dog'][2] == 33.333333

    pipeline = {"source_key" : ""}
    save_obj(pipeline, 'tmp_pipeline')

def test_single_smiles(client):
    #GIVEN I have a pipeline with normalisation off and single smiles similarity scoring
    #AND I am on the view pipline page
    #WHEN I press submit to run the pipeline
    #THEN The similarity scores in my results are not normalised
    pipeline = {"source_key":"test_download", "similarity_score": "a", "normalise_scores": False, "single_smiles": "dog"}
    save_obj(pipeline, 'tmp_pipeline')
    print("Pipeline contents:")
    print(pipeline)
    result = client.post(url_for('generate_results_2'))
    assert result.status_code == 200

    sim_result = result.data
    print(sim_result)
    table = pd.read_html(sim_result)
    assert table[0]['sim_score_dog'][2] == 2

    pipeline = {"source_key" : ""}
    save_obj(pipeline, 'tmp_pipeline')


def test_norm_df_smiles(client):
    #GIVEN I have a pipeline including normalisation and dataframe smiles similarity scoring
    #AND I am on the view pipline page
    #WHEN I press submit to run the pipeline
    #THEN The similarity scores in my results are normalised
    #AND the correct best score is returned based on the normalised scores
    pipeline = {"source_key":"test_download", "similarity_score": "a", "normalise_scores": True, "dataframe_smiles_ref": "test_download_2", "dataframe_smiles_col": "animal"}
    save_obj(pipeline, 'tmp_pipeline')
    print("Pipeline contents:")
    print(pipeline)
    result = client.post(url_for('generate_results_2'))
    assert result.status_code == 200

    sim_result = result.data
    print(sim_result)
    table = pd.read_html(sim_result)
    assert table[0]['sim_match_test_download_2_animal'][1] == "cat"
    assert table[0]['sim_score_test_download_2_animal'][1] == 33.333333

    pipeline = {"source_key" : ""}
    save_obj(pipeline, 'tmp_pipeline')

def test_df_smiles(client):
    #GIVEN I have a pipeline with normalisation off and dataframe smiles similarity scoring
    #AND I am on the view pipline page
    #WHEN I press submit to run the pipeline
    #THEN The similarity scores in my results are not normalised
    #AND the correct best score is returned based on the un-normalised scores
    pipeline = {"source_key":"test_download", "similarity_score": "a", "normalise_scores": False, "dataframe_smiles_ref": "test_download_2", "dataframe_smiles_col": "animal"}
    save_obj(pipeline, 'tmp_pipeline')
    print("Pipeline contents:")
    print(pipeline)
    result = client.post(url_for('generate_results_2'))
    assert result.status_code == 200

    sim_result = result.data
    print(sim_result)
    table = pd.read_html(sim_result)
    assert table[0]['sim_match_test_download_2_animal'][1] == "cat"
    assert table[0]['sim_score_test_download_2_animal'][1] == 2

    pipeline = {"source_key" : ""}
    save_obj(pipeline, 'tmp_pipeline')
