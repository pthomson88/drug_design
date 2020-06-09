from .save_load import load_obj, save_obj
import settings

#Class definition of a dataset
class UrlDict(object):
    """A class for a dictionary of urls."""

    def __init__(self, **kwargs):

        if "name" in kwargs:
            self.name = kwargs["name"]
        else:
            self.name = "url_dict"

        self.dictionary = load_obj(self.name)
        self.webdictionary = { key : self.dictionary[key] for key in self.dictionary if not key in settings.HIDE_DATASET }

    def add_gsheet_url(self,url_key,id):

        url_string = 'https://docs.google.com/spreadsheets/d/'+id+'/export?format=csv'
        self.dictionary[url_key] = url_string
        self.webdictionary[url_key] = url_string

        save_obj(self.dictionary, self.name)

    def delete_dataset(self, url_key):

        del self.dictionary[url_key]
        del self.webdictionary[url_key]

        save_obj(self.dictionary, self.name)
