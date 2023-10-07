from dotenv import load_dotenv

from classes.pipeline import OOPSpotifyPipeline
from utils import export

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

spotify = OOPSpotifyPipeline(RELEVANT_PLAYLISTS)
tracks, recommendations = spotify.get_recommendations_from_user_playlists(create_playlist=True)

export(tracks, recommendations)
