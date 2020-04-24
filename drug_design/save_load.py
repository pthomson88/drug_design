import pickle
import os

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
