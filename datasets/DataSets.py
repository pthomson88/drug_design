import ssl

ssl._create_default_https_context = ssl._create_unverified_context

import urllib.request
import pandas as pd
import dask.dataframe as dd

#Class definition of a dataset
class DataSet(object):
    """A class for dataset objects ."""

    def __init__(self, drive_url):
        self.drive_url = drive_url

    def getdataframe(self, drive_url):
        self.csv_file = urllib.request.urlopen(drive_url)
        dataframe = pd.read_csv(self.csv_file, error_bad_lines=False, iterator=True)
        return dataframe.get_chunk(100)


#A dictionary pointing to google drive datasets - csv only
url_dict = {
        "test_download"  : 'https://docs.google.com/spreadsheets/d/1o__Ar6O65DowaqCATTNjeK9kvr9NXJiX4Slo0tK-e4k/export?format=csv',
		"chembl26_ph3_ph4" : 'https://docs.google.com/spreadsheets/d/1djFMETW8A111b7xv421L9jJWtIIN7Sn0ap95u8ml8eQ/export?format=csv'
        }
