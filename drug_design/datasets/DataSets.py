import ssl
#apparently this is needed for dealing with a certificate error
ssl._create_default_https_context = ssl._create_unverified_context

import urllib.request
import pandas as pd

#Class definition of a dataset
class DataSet(object):
    """A class for dataset objects ."""

    #initialises the object from a drive url and returns the resulting dataframe
    def __init__(self, drive_url, **kwargs):

        try:
            csv_file = urllib.request.urlopen(drive_url)
        except:
            #print("Error: I can't seem to load that file - please check you are requesting a Google Sheet format.")
            raise RuntimeError("This might not be a google sheet...")
        #the dataframe is read in chunks of 100 rows at a time and the headers are read
        chunks = pd.read_csv(csv_file, error_bad_lines=False, chunksize = 100)

        self.chunks = [ chunk for chunk in chunks ]
        m = self.how_many_chunks()

        if 'chunk_limit' in kwargs:
            m = self.how_many_chunks()
            p = int(kwargs['chunk_limit'])
            chunk_lim = min(m, p)
            self.chunks = [ self.chunks[n] for n in range(chunk_lim) ]

        self.dataframe = self.stitch_chunks()

        self.headers = [ c for c in self.dataframe ]

    def how_many_chunks(self):
        return len(self.chunks)

    def stitch_chunks(self):
        dfList = [ df for df in self.chunks ]
        self.dataframe = pd.concat(dfList,sort=False)

        return self.dataframe


#A dictionary pointing to google drive datasets - csv only
#This is not used directly but is useful to keep as a back-up
url_dict = {
    'test_download': 'https://docs.google.com/spreadsheets/d/1o__Ar6O65DowaqCATTNjeK9kvr9NXJiX4Slo0tK-e4k/export?format=csv',
    'chembl26_ph3_ph4': 'https://docs.google.com/spreadsheets/d/1djFMETW8A111b7xv421L9jJWtIIN7Sn0ap95u8ml8eQ/export?format=csv',
    'chembl26_similar_protein_mols': 'https://docs.google.com/spreadsheets/d/1upjwIomN7kIgXhRu9NFU9C0WK5S0lJSOpVC_BH1OBxs/export?format=csv',
    'not_a_csv': 'https://docs.google.com/spreadsheets/d/1Rw9DkxM_rzmS59qPS-TF6JV9MAu8LJtB/export?format=csv'
    }
