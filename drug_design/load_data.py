#We need to import the DataSet class and load the dictionary of urls
from .datasets.DataSets import DataSet
from .save_load import load_obj

def load_data():

    print("this function is starting")

    url_dict = load_obj('url_dict')

    #list the available dataset keys
    print("The available dataset keys are : ")
    print("")

    for key in url_dict:
        print(key)

    print("")

    #create a new dictionary with the datasets to load
    files = {}

    cont = 'Y'
    while cont.lower() == 'y':
    #Ask the user for a file and add create a new file entry with the dataset_name as key and a DataSet object as the value
        dataset_name = input("Which dataset would you like to load. If you'd like to skip this step just press enter :> ")

        if dataset_name == "":
            print("Skipping loading data...")
            files = {"placeholder" : "placeholder data"}
            return files
        else:
            try:
                files[dataset_name]= DataSet(url_dict[dataset_name])
            except:
                print("Error: I'm sorry, I couldn't load that dataset - please make sure it is a google sheet \n(remember you can hit Ctrl-C at any time to quit)")

    #give the option to load more than one dataset
            cont = input("Would you like to load another dataset? enter Y for yes or N for no :> ")

    #now create a dataframe for every dataset using the same keys
    #df = {}
    #for key in files:
    #     df[key]= files[key].dataframe

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
