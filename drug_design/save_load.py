import pickle
import os

#This will try to connect to the datastore using whatever credentials it finds
#from google.cloud import datastore
#datastore_client = datastore.Client()

def set_path(name ):
    script_dir = os.path.dirname(__file__)
    rel_path = 'obj/'+ name + '.pkl'
    abs_file_path = os.path.join(script_dir, rel_path)
    return abs_file_path

def save_obj(obj, name ):
    abs_file_path = set_path(name)
    with open(abs_file_path, 'wb') as f:
        pickle.dump(obj, f, protocol=4)

def load_obj(name ):
    abs_file_path = set_path(name)
    try:
        with open(abs_file_path, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        error_msg = "Error: I couldn't find a file with that name"
        return error_msg

def store_time(dt):
    entity = datastore.Entity(key=datastore_client.key('visit'))
    entity.update({
        'timestamp': dt
    })

    datastore_client.put(entity)

def fetch_times(limit):
    query = datastore_client.query(kind='visit')
    query.order = ['-timestamp']

    times = query.fetch(limit=limit)

    return times

def store_entity(kind, name):
    ek = datastore_client.key(kind, name)
    entity = datastore.Entity(key=ek)
    task['description'] = 'Buy milk'

    # Saves the entity
    datastore_client.put(task)


    entity.update({
        'timestamp': dt
    })

    datastore_client.put(entity)

def fetch_pipeline(ek,limit):
    query = datastore_client.query(kind=ek)
    result = query.fetch(limit=limit)

    return result
