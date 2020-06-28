from .save_load import save_obj, load_obj
from .UrlDict import UrlDict
from .term_num_opts import selector

def gsheet_store(**kwargs):
    cont = "y"
    while cont.lower() == "y":
        print("Would you like to...")
        action = selector(["Link a new dataset by Google ID" , "Un-link an existing dataset" , "Go back"])
        print("")

        if "test" in kwargs:
            url_dict_obj = UrlDict(name = kwargs["test"])
        else:
            url_dict_obj = UrlDict(name = "url_dict")

        url_dict = url_dict_obj.dictionary

        if action == "Link a new dataset by Google ID":

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

        elif action =="Un-link an existing dataset":

            dataset_options = [ key for key in url_dict ]

            cont = 'Y'
            while cont.lower() == 'y':

                print("Your availble datasets are...")
                key = selector( dataset_options , "Which dataset would you like to delete?" )

                url_dict_obj.delete_dataset(key)

                url_dict = url_dict_obj.dictionary

                print("Updated list of available datasets:")
                for key in url_dict:
                    print(key)
                cont = input("\nWould you like to unlink another dataset? enter Y for yes or N for no :> ")
                print("")

        elif action =="Go back":
            cont = "n"

        else:

            print("Error: Something went wrong there. Make sure you are entering a number")
            print("(Remember you can use Ctrl-C to escape at any time)")
