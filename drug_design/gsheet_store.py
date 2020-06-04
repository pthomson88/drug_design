from .save_load import save_obj, load_obj
from .UrlDict import UrlDict

def gsheet_store():
    cont = "y"
    while cont.lower() == "y":
        action = input(" Would you like to:\n \n1. Link a new dataset by Google ID \n2. Un-link an existing dataset \n3. Go back \n\n:> ")
        print("")

        url_dict_obj = UrlDict()
        url_dict = url_dict_obj.dictionary

        if action == "1":

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
                url_key = input("What will this dataset be called? :> ")
                print("")

                url_dict_obj.add_gsheet_url(url_key,id)
                url_dict = url_dict_obj.dictionary

                print("Updated list of available datasets:")
                print("            ---------------------------------------------------------------")
                for key in url_dict:
                    print(key + "  :  " + url_dict[key] + "\n")
                print("            ---------------------------------------------------------------")
                cont = input("Would you like to link another google sheets url? enter Y for yes or N for no :> ")
                print("")

        elif action =="2":

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
                    url_dict_obj.delete_dataset(key)
                except KeyError:
                    print("Error: Make sure you type the name of the dataset exactly")

                url_dict = url_dict_obj.dictionary

                print("Updated list of available datasets:")
                for key in url_dict:
                    print(key)
                cont = input("\nWould you like to unlink another dataset? enter Y for yes or N for no :> ")
                print("")

        elif action =="3":
            cont = "n"

        else:

            print("Error: Something went wrong there. Make sure you are entering a number")
            print("(Remember you can use Ctrl-C to escape at any time)")
