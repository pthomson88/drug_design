#We need to import the DataSet class and load the dictionary of urls
from .datasets.DataSets import DataSet
from .save_load import load_obj
from .term_num_opts import *

def term_load_data():
    url_dict = load_obj('url_dict')
    options = [key for key in url_dict]
    selection = selector(options,"Which dataset would you like to load. If you'd like to skip this step just press enter")
    if selection == False:
        print("No new data loaded")
        return False
    files = load_data(selection)
    return files

def load_data(dataset_name):
    url_dict = load_obj('url_dict')

    #create a new dictionary with the datasets to load
    files = {}
    try:
        files[dataset_name]= DataSet(url_dict[dataset_name])
    except:
        print("Error: I'm sorry, I couldn't load that dataset - please make sure it is a google sheet \n(remember you can hit Ctrl-C at any time to quit)")

    #check it all worked
    print("\n New data added: \n")
    for key in files:
        print(key)
        print("*******************")
        #loop added to account for chunking
        print(files[key].dataframe)

        print("*******************")
        print("")
    print("")
íí
    return files
