from .save_load import load_obj, save_obj

#Class definition of a dataset
class UrlDict(object):
    """A class for a dictionary of urls."""

    def __init__(self, **kwargs):

        if "name" in kwargs:
            self.name = kwargs["name"]
        else:
            self.name = "url_dict"

        self.dictionary = load_obj(self.name)

    def add_gsheet_url(self,url_key,id):

        url_string = 'https://docs.google.com/spreadsheets/d/'+id+'/export?format=csv'
        self.dictionary[url_key] = url_string

        save_obj(self.dictionary, self.name)

    def delete_dataset(self, url_key):

        del self.dictionary[url_key]

        save_obj(self.dictionary, self.name)
