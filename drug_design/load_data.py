#We need to import the DataSet class and load the dictionary of urls
from .datasets.DataSets import DataSet
from .UrlDict import UrlDict

def load_data(dataset_name, **kwargs):

    url_dict = UrlDict(name = "url_dict")

    #create a new dictionary with the datasets to load
    files = {}
    try:
        #if a chunk_limit is passed in kwargs then it will be reflected for the dataset object
        files[dataset_name]  = DataSet(url_dict.dictionary[dataset_name], **kwargs)
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

    return files
