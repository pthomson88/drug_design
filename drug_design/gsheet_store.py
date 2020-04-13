from .save_load import save_obj, load_obj

def gsheet_store():
    cont = "y"
    while cont.lower() == "y":
        action = input(" Would you like to:\n \n1. Link a new dataset by Google ID \n2. Un-link an existing dataset \n3. Go back \n\n:> ")
        print("")

        if action == "1":

            add_gsheet_url()

        elif action =="2":

            delete_dataset()

        elif action =="3":
            cont = "n"

        else:

            print("Error: Something went wrong there. Make sure you are entering a number")
            print("(Remember you can use Ctrl-C to escape at any time)")

def add_gsheet_url():
    url_dict = load_obj('url_dict')

    print("Current list of available datasets:")
    print("            ---------------------------------------------------------------")
    for key in url_dict:
        print(key + "  :  " + url_dict[key] + "\n")
    print("            ---------------------------------------------------------------")

    cont = 'Y'
    while cont.lower() == 'y':
    #give the option to load more than one dataset at the start
        print("")

        id = input("Please paste the google drive id for this data :> ")
        print("")
        key = input("What will this dataset be called? :> ")
        print("")

        url_string = 'https://docs.google.com/spreadsheets/d/'+id+'/export?format=csv'

        url_dict.update({key : url_string})

        print("Updated list of available datasets:")
        print("            ---------------------------------------------------------------")
        for key in url_dict:
            print(key + "  :  " + url_dict[key] + "\n")
        print("            ---------------------------------------------------------------")
        cont = input("Would you like to link another google sheets url? enter Y for yes or N for no :> ")
        print("")

    save_obj(url_dict, 'url_dict')

    return cont

def delete_dataset():

    url_dict = load_obj('url_dict')

    print("Current list of available datasets:")

    for key in url_dict:
        print(key)

    cont = 'Y'
    while cont.lower() == 'y':
    #give the option to load more than one dataset at the start
        print("")

        key = input("Which dataset would you like to delete? :> ")
        print("")

        try:
            del url_dict[key]
        except KeyError:
            print("Error: Make sure you type the name of the dataset exactly")

        print("Updated list of available datasets:")
        for key in url_dict:
            print(key)
        cont = input("\nWould you like to unlink another dataset? enter Y for yes or N for no :> ")
        print("")

    save_obj(url_dict, 'url_dict')

    return cont
