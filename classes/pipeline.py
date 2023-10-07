import os
from .api import SpotifyAPI
from .playlist import Playlist
from .recommendation import RecommendationEngine
from .track import TrackFactory

class OOPSpotifyPipeline:
    def __init__(self, relevant_playlists) -> None:
        self.relevant_playlists = relevant_playlists
        self.sp = SpotifyAPI(
            os.getenv("CLIENT_ID"),
            os.getenv("CLIENT_SECRET"),
            "http://localhost:8080/callback",
        ).sp
        self.track_factory = TrackFactory(self.sp)
        self.re = RecommendationEngine(self.sp, self.track_factory)
        self.all_tracks = []
        

    def get_recommendations_from_user_playlists(
        self, create_playlist=False
    ) -> None:
        """Get all the playlists from the user and get recommendations for the relevant ones"""
        playlists_data = self.sp.current_user_playlists(limit=50)
        print(f"Found {playlists_data['total']} playlists")
        for playlist_info in playlists_data["items"]:
            playlist = Playlist(playlist_info)

            print(f"Fetching playlist {playlist.name}")

            if playlist.name in self.relevant_playlists:
                tracks = playlist.get_playlist_tracks(self.sp, self.track_factory)
                self.re.add_recommendation(playlist.name, playlist.img, tracks)
                self.all_tracks.extend(tracks)
                
        # if create_playlist:
        #     self.re.create_recommendation_playlist()

        return self.re.recommendations, self.all_tracks
