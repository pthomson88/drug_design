import pickle

def save_obj(obj, name ):
    with open('./obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, protocol=4)

def load_obj(name ):
    try:
        with open('./obj/' + name + '.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        print("Error: I couldn't find a file with that name")
