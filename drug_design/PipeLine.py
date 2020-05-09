import datetime
from .save_load import load_obj, save_obj
from .load_data import load_data
from .similarity import run_similarity

#Class definition of a pipeline
class PipeLine(object):
    """A class for the pipeline object."""
    #A pipeline consists of a dictionary defining actions, a source_key and a created datetime
    def __init__(self, **kwargs):
        self.created = srt(datetime.datetime.now())
        self.dictionary = {'source_key' : '' }
        update_property(self, **kwargs)

    #a pipeline can be updated with new kwargs
    def update_property(self,**kwargs):
        for key in kwargs:
            self.dictionary[key] = kwargs[key]

        self.source_key = self.dictionary['source_key']

    def delete_property(self,**kwargs):
        for key in kwargs:
            del self.dictionary[key]

    #a pipeline can be run
    def run_pipeline(self):

        pipeline = self.dictionary
        ds_key = self.source_key
        dataset = load_data(ds_key)

        #look for similariy scoring
        for key in pipeline:
            if key[16] == "similarity_score":
                tmp_key = key
                sim_pipe = {tmp_key : pipeline[tmp_key]}
                    for key in pipeline:
                        if tmp_key in key:
                            sim_pipe[key] = pipeline[key]


                header = sim_pipe[tmp_key]
                norm_key = sub_key_gen("normalise_scores", tmp_key, **sim_pipe)
                norm = sim_pipe[norm_key]

                for key in sim_pipe:
                    #look for single smiles task
                    if "single_smiles" in key:
                        mol_reference = {"SMILES" : [sim_pipe[key],norm]}
                        for chunk in dataset[ds_key].chunks:
                            chunk = run_similarity(chunk,header,**mol_reference)
                        dataset[ds_key].stitch_chunks()

                    #look for dataframe smiles task next
                    if "dataframe_smiles_ref" in key:
                        ref_key = pipeline[key]
                        ref_dataset = load_data(ref_key)
                        #sub key gen can also be used to generate an existing key
                        col_key = sub_key_gen("dataframe_smiles_col", tmp_key, **sim_pipe)
                        ref_column = pipeline[col_key]
                        #pass in the reference df as its DataSet object
                        mol_reference = { ref_key : [ ref_dataset[ref_key] , ref_column, norm] }

                        dataset[ds_key].chunks = [ run_similarity(df,header,**mol_reference) for df in dataset[ds_key].chunks]
                        dataset[ds_key].stitch_chunks()


#Class definition of a terminal pipeline
class TermPipeLine(PipeLine):

    #initiated as a PipeLine but with the option to load from tmp_pipeline
    def __init__(self, load, **kwargs):
        super(TermPipeLine, self).__init__(**kwargs)

        if load == True:
            self.created = load_obj('last_created_at')
            self.source_key = load_obj('tmp_key')
            self.dictionary = load_obj('tmp_pipeline')

        #for the terminal app only one pipeline can exist at once
        #instantiating a new pipeline object will wipe the existing pipeline
        save_changes()
        save_obj(self.created, 'last_created_at')

    def update_property(self,**kwargs):
        super().update_property(**kwargs)
        save_changes()

    def delete_property(self, **kwargs):
        super().delete_property(**kwargs)
        save_changes()

    def save_changes(self):
        self.source_key = self.dictionary['source_key']
        save_obj(self.dictionary,'tmp_pipeline')
        save_obj(self.source_key, 'tmp_key')

    def run_pipeline(self):
        super().run_pipeline()

#Class definition of a datastore pipeline
class DataStorePipeLine(PipeLine):

    #This will try to connect to the datastore using whatever credentials it finds
    from google.cloud import datastore
    datastore_client = datastore.Client()

    def __init__(self,load, **kwargs):

        if load == True:
            self.user_id = kwargs['user_id']
        else:
            #obviously this is a placeholder and needs user id funcitonality piped in
            self.user_id = 'test'
            #This will establish created, source_key and dictionary properties
            super(DataStorePipeLine, self).__init__(**kwargs)

        #for a first pass we'll have 1 pipeline per user (hence id  = user_id)
        self.id = self.user_id
        name = self.id
        kind = 'Pipeline'
        pipeline_key = datastore_client.key(kind,name)
        self.pipeline_entity = datastore.Entity(key=pipeline_key)

        if load != True:
            #Add the create time and user_id to the datastore entity at the start
            self.pipeline_entity['created'] = self.created
            self.pipeline_entity['user_id'] = self.user_id

        #update the pipeline with kwargs  - no need to update the dictionary as this was done already
        update_property2(**kwargs)

    def update_property(self,**kwargs):
    #use this when updating properties separately from initialising a Pipeline
        super().update_property(**kwargs)
        update_property2(**kwargs)

    def update_property2(self, **kwargs):
    #this is for use as part of initialising a pipeline
        for key in self.dictionary:
            self.pipeline_entity[key] = self.dictionary[key]
        save_changes()

    def delete_property(self, **kwargs):
        #deleted from the dictionary
        super().delete_property(**kwargs)
        #deletes the same property from the pipeline entity
        for key in kwargs:
            if key in self.pipeline_entity:
                del self.pipeline_entity[key]
        save_changes()

    def save_changes(self):
        pipeline = self.pipeline_entity
        datastore_client.put(pipeline)
        
    def run_pipeline(self):
        super().run_pipeline()
