import pandas as pd
from dotenv import load_dotenv

from spotipyPipe import SpotifyPipeline
from upload import upload_file

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

df = pd.DataFrame(spotify.global_track_list)
df.to_csv("playlist_data.csv", index=False)

df = pd.DataFrame(spotify.recommendations)
df.to_csv("playlist_recommend.csv", index=False)

upload_file("playlist_data.csv", "mage-project-bucket")
upload_file("playlist_recommend.csv", "mage-project-bucket")

## TODO: airflow, docstrings, refactoring, tests
