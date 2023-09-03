import os
import time

import spotipy
from revChatGPT.V1 import Chatbot
from spotipy.oauth2 import SpotifyOAuth
from tqdm import tqdm


class SpotifyPipeline:
    def __init__(self, relevant_playlists) -> None:
        self.relevant_playlists = relevant_playlists
        self.playlist_track_list = []
        self.global_track_list = []
        self.recommendations = []
        self.tracks_str = ""

        # Initialize the Spotipy client
        self.sp = self.get_spotipy_client()

    def get_spotipy_client(self):
        CLIENT_ID = os.getenv("CLIENT_ID")
        CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        REDIRECT_URI = "http://localhost:8080/callback"  # Your redirect URI

        # Set up Spotipy OAuth flow
        auth_manager = SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope="user-library-read playlist-read-private playlist-read-collaborative",
        )

        # Create a Spotipy client
        sp = spotipy.Spotify(auth_manager=auth_manager)

        return sp

    def get_library(self):
        # Fetch the user's saved tracks
        tracks_data = self.sp.current_user_saved_tracks()
        total_tracks = tracks_data["total"]
        print(f"Found {total_tracks} tracks in library")

        for track in tracks_data["items"]:
            track_name = track["track"]["name"]
            print(f"Fetching track {track_name}")

    def get_playlists(self):
        # Fetch the user's playlists
        playlists_data = self.sp.current_user_playlists(limit=50)
        print(f"Found {playlists_data['total']} playlists")
        for playlist in playlists_data["items"]:
            playlist_name = playlist["name"]

            if len(playlist["images"]) > 0:
                playlist_img = playlist["images"][0]["url"]
            else:
                playlist_img = "https://iili.io/HlHy9Yx.png"

            print(f"Fetching playlist {playlist_name}")

            if playlist_name in self.relevant_playlists:
                self.get_playlist_tracks(
                    playlist["id"], playlist_name, playlist_img
                )
                self.spotify_recommendation()
                self.global_track_list += self.playlist_track_list
                self.playlist_track_list = []

    def get_artist_img(self, uri):
        # Fetch the artist's image
        artist_data = self.sp.artist(uri)
        if len(artist_data["images"]) > 0:
            artist_img = artist_data["images"][0]["url"]
        else:
            artist_img = "https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png?20170328184010"
        return artist_img

    def get_playlist_tracks(self, playlist_id, playlist_name, playlist_img):
        tracks_data = self.sp.playlist_tracks(playlist_id)

        for track in tqdm(tracks_data["items"]):
            artist_name = track["track"]["artists"][0]["name"]
            artist_uri = track["track"]["artists"][0]["uri"]
            artist_img = self.get_artist_img(artist_uri)
            track_name = track["track"]["name"]
            popularity = track["track"]["popularity"]
            release_date = track["track"]["album"]["release_date"]
            album_cover = track["track"]["album"]["images"][0]["url"]
            album_name = track["track"]["album"]["name"]
            track_uri = track["track"]["uri"].split(":")[-1]

            relevant_features_data = self.get_audio_features(track_uri)

            self.playlist_track_list.append(
                {
                    "playlist_name": playlist_name,
                    "artist_name": artist_name,
                    "track_name": track_name,
                    "release_date": release_date,
                    "album_cover": album_cover,
                    "popularity": popularity,
                    "playlist_img": playlist_img,
                    "artist_img": artist_img,
                    "album_name": album_name,
                    "uri": track_uri,
                    **relevant_features_data,
                }
            )

    def get_audio_features(self, audio_features_id):
        # Fetch audio features for a track
        audio_features_data = self.sp.audio_features(audio_features_id)[0]
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

    def spotify_recommendation(self):
        top_20 = sorted(
            self.playlist_track_list,
            key=lambda x: x["popularity"],
            reverse=True,
        )[:20]
        for idx in range(0, 15, 5):
            batch_5 = [track["uri"] for track in top_20[idx : idx + 5]]
            recommendations = self.sp.recommendations(
                seed_tracks=batch_5, limit=5
            )
            for track in recommendations["tracks"]:
                artist_name = track["artists"][0]["name"]
                artist_uri = track["artists"][0]["uri"]
                artist_img = self.get_artist_img(artist_uri)
                track_name = track["name"]
                popularity = track["popularity"]
                release_date = track["album"]["release_date"]
                album_cover = track["album"]["images"][0]["url"]
                album_name = track["album"]["name"]
                track_uri = track["uri"].split(":")[-1]

                relevant_features_data = self.get_audio_features(track_uri)

                self.recommendations.append(
                    {
                        "artist_name": artist_name,
                        "track_name": track_name,
                        "release_date": release_date,
                        "album_cover": album_cover,
                        "popularity": popularity,
                        "artist_img": artist_img,
                        "album_name": album_name,
                        "uri": track_uri,
                        **relevant_features_data,
                    }
                )

    def gpt_recommendation(self, playlist_name):
        chatbot = Chatbot(config={"access_token": os.getenv("OPEN_AI_TOKEN")})
        prompt = f"""You are to act as a music recommendation expert.
        Your task is, given a list of favorite songs, in a format "song_name - author_name"
        to recommend 20 new songs to the user, that they will like.

        You should stick to the same genre as the user's favorite songs.
        The return format should be "song_name - author_name - album_name".

        If you think a song from the favorite songs does not exist, skip it.
        Do not recommend songs that do not exist, rather just skip them, also dont recommend the songs that are already in the users favorites.
        Do not say you need more specific information, since there is none to be had.

        USER FAVORITE SONGS:
        =====================
        {self.tracks_str}
        """
        response = ""
        for data in chatbot.ask(prompt):
            response = data["message"]
        print("CHATGPT says: " + response)
        self.playlist_recommendations[playlist_name] = response
        self.tracks_str = ""
