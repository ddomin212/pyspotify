import os

from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials


def upload_file(filename, bucket_name):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        os.getenv("CRED_FILE")
    )
    client = storage.Client(
        credentials=credentials, project=os.getenv("PROJECT_NAME")
    )
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)
