from .PipeLine import PipeLine
import settings

import requests

#Class definition of a datastore pipeline
class DataStorePipeLine(PipeLine):

    def __init__(self,load, **kwargs):
        if load == True:
            self.load_pipeline(**kwargs)
        else:
            #If we aren't loading data then we need to crearte a new pipeline - first we need a new session:
            self.create_new_pipeline(**kwargs)

    def load_pipeline(self, **kwargs):
        #load = True so first get the pipeline from the datastore:
        assert 'user_id' in kwargs
        assert 'session_key' in kwargs

        self.user_id = kwargs['user_id']
        self.session_key = kwargs['session_key']
        url = settings.BE_URL_PREFIX + '/drug_design_backend/api/v1/pipeline/' + self.user_id
        #the pipeline will always be returned if there is an active session
        #the session_key will be hiden by place
        #404 is returned for a dormant session
        r = requests.get(url)
        if r.status_code >= 400:
            raise Exception(r.status_code)
        else:
            self.pipeline_entity = r.json()

        #if there isn't a created date or source key then a new pipeline is created
        try:
            assert 'created' in self.pipeline_entity
            assert 'source_key' in self.pipeline_entity
        except AssertionError:
            self.create_new_pipeline(**kwargs)

        #Dictionary, source_key and created properties need added to the Pipeline object
        self.created = self.pipeline_entity['created']
        self.dictionary = {
            key : self.pipeline_entity[key]
            for key in self.pipeline_entity
            if not key == 'created'
            if not key == 'user_id'
            if not key == 'session_key'
        }
        self.source_key = self.dictionary['source_key']

        #the pipeline is loaded at this stage - all that's left to do is update any newly passed arguments
        self.update_property_datastore(**kwargs)

    def create_new_pipeline(self, **kwargs):
        #first get a fresh session or the current session for user if one is active
        assert 'user_id' in kwargs
        self.user_id = kwargs['user_id']
        url = settings.BE_URL_PREFIX + '/drug_design_backend/api/v1/session/' + self.user_id

        response = requests.get(url).json()
        self.session_key = response['session_key']
        self.source_key = ""

        #Next we need to build a pipeline everything it needs
        super().__init__(**kwargs)

        #We need to prepare the data to post to the datastore
        url = settings.BE_URL_PREFIX + '/drug_design_backend/api/v1/pipeline'
        #add the properties needed then use to create a new pipeline
        pre_pipeline_entity = { key : kwargs[key] for key in kwargs }
        pre_pipeline_entity['created'] = self.created
        pre_pipeline_entity['user_id'] = self.user_id
        pre_pipeline_entity['session_key'] = self.session_key
        pre_pipeline_entity['source_key'] = self.source_key

        #finally we can send the data and use the response to create the pipeline_entity property
        #we check that a positive respone is returned and if not we return the error status_code
        r = requests.post(url,json=pre_pipeline_entity)
        if r.status_code == 201:
            response = r.json()
            self.pipeline_entity = response['pipeline_entity']
        else:
            raise Exception(r.status_code)

    def update_property_datastore(self,**kwargs):
        update = self.handle_datastore_properties(**kwargs)
        #if there is something to update then update
        #The session key needs to be part of the PUT request
        kwargs['session_key'] = self.session_key
        if bool(update):
            super().update_property(**update)
            #the datastore can be updated with everything
            url = settings.BE_URL_PREFIX + '/drug_design_backend/api/v1/pipeline/' + self.user_id
            r = requests.put(url,json=kwargs)
            #checking the update has been received and if not aborting with the status_code
            if r.status_code == 201:
                response = r.json()
                self.pipeline_entity = response['pipeline_entity']
            else:
                raise Exception(r.status_code)

    def delete_property_datastore(self, **kwargs):
        update = self.handle_datastore_properties()
        super().delete_property(**update)
        #deletes the same property from the pipeline entity
        url = settings.BE_URL_PREFIX + '/drug_design_backend/api/v1/pipeline/' + self.user_id + '/delete_properties'
        r = requests.put(url,json=kwargs)
        response = r.json()
        self.pipeline_entity = response['pipeline_entity']

    def handle_datastore_properties(self, **kwargs):
        update = {
            key : kwargs[key]
            for key in kwargs
            if not key == 'created'
            if not key == 'user_id'
            if not key == 'session_key'
        }
        return update

    def run_datastore_pipeline(self, **kwargs):
        #apply a 4 hour lock to the session to protect the users run
        url = settings.BE_URL_PREFIX + '/drug_design_backend/api/v1/pipeline/' + self.user_id
        kwargs['lock'] = 240
        r = requests.put(url, json=kwargs)
        #If the session key is good then run the pipeline otherwise raise an exception
        if r.status_code == 201:
            result = super().run_pipeline()
            #Make the session dormant automatically after running a pipeline
            kwargs['lock'] = False
            r = requests.put(url, json=kwargs)
            return result
        else:
            raise Exception(r.status_code)
