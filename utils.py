import os

import pandas as pd
from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials


def upload_file(filename, bucket_name):
    """upload a file to a GCS bucket

    Args:
        filename
        bucket_name
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        os.getenv("CRED_FILE")
    )
    client = storage.Client(
        credentials=credentials, project=os.getenv("PROJECT_NAME")
    )
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)


def export(playlist_data, playlist_recommend):
    df = pd.DataFrame(playlist_data)
    df.to_csv("playlist_data.csv", index=False)

    df = pd.DataFrame(playlist_recommend)
    df.to_csv("playlist_recommend.csv", index=False)
