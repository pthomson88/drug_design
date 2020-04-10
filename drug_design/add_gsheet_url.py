from .save_load import save_obj, load_obj

def add_gsheet_url():
    url_dict = load_obj('url_dict')

    print(url_dict)

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

        print(url_dict)

        cont = input("Would you like to add another google sheets url? enter Y for yes or N for no :> ")
        print("")

    save_obj(url_dict, 'url_dict')
