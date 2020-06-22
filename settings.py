
BE_URL_PREFIX = 'https://drug-design-backend.appspot.com'

#It seems to take a while for requests to register a new SSL cert for appspot drug_design_backend
#Set this to False to be able to run locally whilst it's having problems
VERIFY_SSL = True

#matches those allowlisted on backend - ideally this would be from an endpoint
ALLOWLIST = ['hydrogen','oxygen','carbon','nitrogen','calcium', 'phosphorus' ,'potassium', 'sulfur','sodium','chlorine','magnesium','iron','copper','molybdenum','zinc','iodine']

#for datasets chunks are 100 rows - so a limit of 1...
# ... limits the size of datasets to the first 100 rows
CHUNK_LIMIT = 1

#HIdes the dataset from being visible on web
HIDE_DATASET = ["not_a_csv","test_download_2", "test_key"]

#For parralelisation
CORES = 8
