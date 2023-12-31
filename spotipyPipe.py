import os

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from tqdm import tqdm


class SpotifyPipeline:
    def __init__(self, relevant_playlists: list[str]) -> None:
        self.relevant_playlists = relevant_playlists
        self.playlist_track_list = []
        self.global_track_list = []
        self.recommendations = []
        self.tracks_str = ""
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        self.REDIRECT_URI = "http://localhost:8080/callback"

        # Initialize the Spotipy client
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

    def get_recommendations_from_user_playlists(
        self, create_playlist=False
    ) -> None:
        """Get all the playlists from the user and get recommendations for the relevant ones"""
        playlists_data = self.sp.current_user_playlists(limit=50)
        print(f"Found {playlists_data['total']} playlists")
        for playlist in playlists_data["items"]:
            playlist_name, playlist_img, playlist_id = self.get_playlist_info(
                playlist
            )

            print(f"Fetching playlist {playlist_name}")

            if playlist_name in self.relevant_playlists:
                self.get_recommendations_for_playlist(
                    playlist_name, playlist_id, playlist_img
                )

            if create_playlist:
                self.create_recommendation_playlist()

    def get_playlist_info(self, playlist: dict) -> tuple[str, str, str]:
        """Get the information we need from a playlist object

        Args:
            playlist: the playlist JSON object

        Returns:
            playlist_name: the name of the playlist
            img: the cover of the playlist on Spotify for nice visuals in dashboard
            playlist_id: the id of the playlist
        """
        if len(playlist["images"]) > 0:
            img = playlist["images"][0]["url"]
        else:
            img = "https://iili.io/HlHy9Yx.png"

        return playlist["name"], img, playlist["id"]

    def get_recommendations_for_playlist(
        self, name: str, id: str, img: str
    ) -> None:
        """Use the spotify API to get recommendations for a playlist's tracks

        Args:
            name: the name of the playlist
            id: the id of the playlist
            img: the cover of the playlist on Spotify for nice visuals in dashboard

        Returns:
            None
        """
        self.get_playlist_tracks(id, name, img)
        self.spotify_recommendation()
        self.global_track_list += self.playlist_track_list
        self.playlist_track_list = []

    def get_playlist_tracks(
        self,
        playlist_id: str,
        playlist_name: str | None = None,
        playlist_img: str | None = None,
    ) -> None:
        """Get all the tracks from a playlist

        Args:
            playlist_id: the id of the playlist
            playlist_name: the name of the playlist
            playlist_img: the cover of the playlist on Spotify for nice visuals in dashboard
        """
        tracks_data = self.sp.playlist_tracks(playlist_id)

        for track in tqdm(tracks_data["items"]):
            self.parse_add_track(
                track["track"],
                self.playlist_track_list,
                playlist_name,
                playlist_img,
            )

    def parse_add_track(
        self,
        track: dict,
        acc: list,
        playlist_name: str | None = None,
        playlist_img: str | None = None,
    ) -> None:
        """Parse a track object and add it to the accumulator

        Args:
            track: track JSON object
            acc: accumulator

        Returns:
            None
        """
        track_info = self.get_track_info(track)

        if playlist_name and playlist_img:
            track_info["playlist_name"] = playlist_name
            track_info["playlist_img"] = playlist_img

        relevant_features_data = self.get_track_audio_features(
            track_info["track_uri"]
        )

        acc.append(
            {
                **track_info,
                **relevant_features_data,
            }
        )

    def get_track_info(
        self, track: dict[str, str | int | list]
    ) -> dict[str, str | int]:
        """Get the information we need from a track object

        Args:
            track: track JSON object

        Returns:
            track_info: dictionary with the relevant information
        """
        track_info = {
            "artist_name": track["artists"][0]["name"],
            "artist_uri": track["artists"][0]["uri"],
            "artist_img": self.get_artist_img(track["artists"][0]["uri"]),
            "track_name": track["name"],
            "popularity": track["popularity"],
            "release_date": track["album"]["release_date"],
            "album_cover": track["album"]["images"][0]["url"],
            "album_name": track["album"]["name"],
            "track_uri": track["uri"].split(":")[-1],
        }
        return track_info

    def get_artist_img(self, uri: str) -> str:
        """Get the image of an artist, if none, use a placeholder, used for nice visuals in dashboard

        Args:
            uri: artirst uri

        Returns:
            the URL for an image of the artist
        """
        artist_data = self.sp.artist(uri)
        if len(artist_data["images"]) > 0:
            artist_img = artist_data["images"][0]["url"]
        else:
            artist_img = "https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png?20170328184010"
        return artist_img

    def get_track_audio_features(self, track_uri: str) -> dict[str, float]:
        """Get the audio features for a track

        Args:
            track_uri: the uri of the track

        Returns:
            relevant_features_data: dictionary with the relevant audio features
        """
        audio_features_data = self.sp.audio_features(track_uri)[0]
        relevant_features = [
            "danceability",
            "energy",
            "loudness",
            "speechiness",
            "acousticness",
            "instrumentalness",
            "liveness",
            "valence",
            "tempo",
            "mode",
        ]
        relevant_features_data = {
            feature: audio_features_data.get(feature)
            for feature in relevant_features
        }
        return relevant_features_data

    def recommend_5_for_5(
        self, top_20: list[dict[str, str | float | int]], idx: int
    ) -> None:
        """Get 5 recommendations for 5 tracks

        Args:
            top_20: the top 20 tracks from a playlist
            idx: the index of the first track in the batch of 5

        Returns:
            None
        """
        batch_5 = [track["track_uri"] for track in top_20[idx : idx + 5]]
        recommendations = self.sp.recommendations(seed_tracks=batch_5, limit=5)
        for track in recommendations["tracks"]:
            self.parse_add_track(track, self.recommendations)

    def spotify_recommendation(self) -> None:
        """Get the top 20 tracks from a playlist and get recommendations for them"""
        top_20 = sorted(
            self.playlist_track_list,
            key=lambda x: x["popularity"],
            reverse=True,
        )[:20]
        for idx in range(0, 15, 5):
            self.recommend_5_for_5(top_20, idx)

    def create_recommendation_playlist(self) -> None:
        """Create a playlist from the recommendations"""
        user_id = self.sp.current_user()["id"]
        playlist = self.sp.user_playlist_create(
            user=user_id,
            name="Recommended from pyspotify",
            public=True,
            collaborative=False,
            description="The recommended tracks based on all the playlist you deem as relevant",
        )
        playlist_id = playlist["id"]
        track_uris = [
            f"spotify:track:{track['track_uri']}"
            for track in self.recommendations
        ]
        self.sp.user_playlist_add_tracks(
            user=user_id, playlist_id=playlist_id, tracks=track_uris
        )
