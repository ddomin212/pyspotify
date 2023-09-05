### spotify pipeline

This is a pipeline that uses the Spotify API to get information about a user's playlists and tracks, then uses the same API to make recommendations for new tracks to add to the user's playlists.

### Setup
1. Clone this repository
2. Install the requirements
3. Create a Spotify developer account and create an app
4. Add the app's client ID and client secret to the `.env` file
5. Create a GCS bucket and add the bucket name to the `.env` file
6. Create a service account and download the JSON key file, this is also added to the `.env` file
7. Run the pipeline, you will be prompted to log in to Spotify and authorize the app
8. The pipeline will run and create 2 CSV files in the GCS bucket, one with the tracks in the user's playlists, and one with the recommended tracks.
9. You can visualize this in Looker Studio, as I have done [here](https://lookerstudio.google.com/u/3/reporting/f6ec216d-a24d-4d08-9eca-563c10624349/page/p_9kbydi4i9c).