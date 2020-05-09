from .PipeLine import PipeLine

#This will try to connect to the datastore using whatever credentials it finds
from google.cloud import datastore
datastore_client = datastore.Client()

#Class definition of a datastore pipeline
class DataStorePipeLine(PipeLine):

    def __init__(self,load, **kwargs):

        kind = 'Pipeline'
        if load == True:
            self.user_id = kwargs['user_id']
            #one pipeline per user to start
            self.id = self.user_id
            name = self.id
            pipeline_key = datastore_client.key(kind,name)
            self.pipeline_entity = datastore_client.get(pipeline_key)

            #if data is loaded then dictionary and created properties need added
            self.dictionary = {'source_key' : ''}
            self.created = self.pipeline_entity['created']

            for key in self.pipeline_entity:
                if key != 'created':
                    if key != 'user_id':
                        self.dictionary[key] = self.pipeline_entity[key]

            self.source_key = self.dictionary['source_key']
            self.update_property_datastore(**kwargs)

        else:
            #obviously this is a placeholder and needs user id funcitonality piped in
            self.user_id = 'test'
            #This will establish created, source_key and dictionary properties
            super().__init__(**kwargs)
            #one pipeline per user to start
            self.id = self.user_id
            name = self.id
            kind = 'Pipeline'
            pipeline_key = datastore_client.key(kind,name)
            self.pipeline_entity = datastore.Entity(key=pipeline_key)

            #If the data is new then the user_id and created properties need added
            self.pipeline_entity['created'] = self.created
            self.pipeline_entity['user_id'] = self.user_id

            #update the pipeline with kwargs  - no need to update the dictionary as this was done already
            self.update_property2_datastore(**kwargs)

    def update_property_datastore(self,**kwargs):
    #use this when updating properties separately from initialising a Pipeline
        super().update_property(**kwargs)
        self.update_property2_datastore(**kwargs)

    def update_property2_datastore(self, **kwargs):
    #this is for use as part of initialising a pipeline
        for key in self.dictionary:
            self.pipeline_entity[key] = self.dictionary[key]
        self.save_changes_datastore()

    def delete_property_datastore(self, **kwargs):
        #deleted from the dictionary
        super().delete_property(**kwargs)
        #deletes the same property from the pipeline entity
        for key in kwargs:
            if key in self.pipeline_entity:
                del self.pipeline_entity[key]
        self.save_changes_datastore()

    def save_changes_datastore(self):
        pipeline = self.pipeline_entity
        datastore_client.put(pipeline)

    def run_pipeline_datastore(self):
        super().run_pipeline()
