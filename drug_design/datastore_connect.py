def datastore_connect():
    from google.cloud import datastore

    # Explicitly use service account credentials by specifying the private key
    # file.
    ds_client = datastore.Client.from_service_account_json(
        'service_account.json')
    return ds_client
