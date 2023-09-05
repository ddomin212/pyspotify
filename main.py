import pandas as pd
from dotenv import load_dotenv

from spotipyPipe import SpotifyPipeline
from utils import export, upload_file

load_dotenv()

RELEVANT_PLAYLISTS = [
    "FMJ wkt",
    "wkt",
    "uk chill",
    "gaming chill",
    "00s-10s rock",
    "outrun tunes",
    "Jazz Rap",
    "Video Game Soundtracks",
    "Road Trip To Tokyo",
    "Epic Classical",
    "phonk",
    "vaporwave",
    "Chillwave / Chill Synthwave",
    "I Love My '90s Hip-Hop",
    "Vietnam War Music",
]

spotify = SpotifyPipeline(RELEVANT_PLAYLISTS)
spotify.get_playlists()

export(spotify.playlist_data, spotify.playlist_recommend)

upload_file("playlist_data.csv", "mage-project-bucket")
upload_file("playlist_recommend.csv", "mage-project-bucket")

## TODO: airflow, tests, create playlist from recommendations
