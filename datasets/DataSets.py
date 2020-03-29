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
        return dd.read_csv(self.csv_file, error_bad_lines=False)

#A dictionary pointing to google drive datasets - csv only
url_dict = {
        "test_download"  : 'https://drive.google.com/spreadsheets/d/1o__Ar6O65DowaqCATTNjeK9kvr9NXJiX4Slo0tK-e4k/export?usp=sharing&format=csv',
		"chembl26_all_small_mols" : 'https://drive.google.com/spreadsheets/d/1xAXHyyH4vMPtrWLDSPVLjFw6A9rbApd6/export?usp=sharing&format=csv'
        }
