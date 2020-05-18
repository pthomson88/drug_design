from .PipeLine import PipeLine
import settings

import requests

#Class definition of a datastore pipeline
class DataStorePipeLine(PipeLine):

    def __init__(self,load, **kwargs):
        if load == True:
            #load = True so first kets get the pipeline from the datastore:
            if not 'user_id' in kwargs or not 'session_key' in kwargs:
                return "Error - insufficient kwargs passed"
            self.user_id = kwargs['user_id']
            self.session_key = kwargs['session_key']
            url = settings.BE_URL_PREFIX + '/drug_design_backend/api/v1/pipeline/' + self.user_id
            self.pipeline_entity = requests.get(url)
            #if the session key passed doesn't match that returned then we'll have problems later so send an error
            if not self.pipeline_entity['session_key'] == self.session_key:
                return "Error - session keys don't match"

            #Dictionary, source_key and created properties need added to the Pipeline object
            self.created = self.pipeline_entity['created']
            self.dictionary = {
                key : self.pipeline_entity[key]
                for key in self.pipeline_entity
                if not key == 'created'
                or not key == 'user_id'
                or not key == 'session_key'
            }
            self.source_key = self.dictionary['source_key']

            #the pipeline is loaded at this stage - all that's left to do is update any newly passed arguments
            self.update_property_datastore(**kwargs)

        else:
            #If we aren't loading data then we need to crearte a new pipeline - first we need a new session:
            if not 'user_id' in kwargs:
                return "Error - insufficient kwargs passed"
            self.user_id = kwargs['user_id']
            url = settings.BE_URL_PREFIX + '/drug_design_backend/api/v1/session/' + self.user_id
            response = requests.get(url)
            self.session_key = response['session_key']

            #Next we need to build a pipeline everything it needs
            super().__init__(**kwargs)

            #We need to prepare the data to post to the datastore
            url = settings.BE_URL_PREFIX + '/drug_design_backend/api/v1/pipeline/' + self.user_id
            #add the properties needed then use to create a new pipeline
            pre_pipeline_entity = { key : kwargs[key] for key in kwargs }
            pre_pipeline_entity['created'] = self.created
            pre_pipeline_entity['user_id'] = self.user_id
            pre_pipeline_entity['session_key'] = self.session_key

            #finally we can send the data and use the response to create the pipeline_entity property
            response = requests.post(url,data=pre_pipeline_entity)
            self.pipeline_entity = response['pipeline_entity']

    def update_property_datastore(self,**kwargs):
        update = self.handle_datastore_properties()
        super().update_property(**update)
        #the datastore can be updated with everything
        url = settings.BE_URL_PREFIX + '/drug_design_backend/api/v1/pipeline/' + self.user_id
        response = requests.put(url,data=kwargs)
        self.pipeline_entity = response['pipeline_entity']

    def delete_property_datastore(self, **kwargs):
        update = self.handle_datastore_properties()
        super().delete_property(**update)
        #deletes the same property from the pipeline entity
        url = settings.BE_URL_PREFIX + '/drug_design_backend/api/v1/pipeline/' + self.user_id + '/delete_properties'
        response = requests.put(url,data=kwargs)
        self.pipeline_entity = response['pipeline_entity']

    def handle_datastore_properties(self, **kwargs):
        if not 'session_key' in kwargs:
            return 'Error - you need to supply a session_key'
        update = {
            key : kwargs[key]
            for key in kwargs
            if not key == 'created'
            or not key == 'user_id'
            or not key == 'session_key'
        }
        return update
