import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyAPI:
    def __init__(self, client_id, client_secret, redirect_uri) -> None:
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.REDIRECT_URI = redirect_uri
        self.sp = self.get_spotipy_client()

    def get_spotipy_client(self) -> spotipy.client.Spotify:
        """Initialize the Spotipy client, we dont use requests because Spotipy can handle the OAuth flow for us"""

        # Set up Spotipy OAuth flow
        auth_manager = SpotifyOAuth(
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET,
            redirect_uri=self.REDIRECT_URI,
            scope="""user-library-read 
                    playlist-read-private 
                    playlist-modify-public 
                    playlist-modify-private 
                    playlist-read-collaborative""",
        )

        # Create a Spotipy client
        sp = spotipy.Spotify(auth_manager=auth_manager)

        return sp