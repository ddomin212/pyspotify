import spotipy
from .track import Track

class RecommendationEngine:
    def __init__(self, sp: spotipy.Spotify, track_factory) -> None:
        self.sp = sp
        self.recommendations = []
        self.track_factory = track_factory

    def recommend_5_for_5(
        self, top_20: list[dict[str, str | float | int]], playlist_name, playlist_img, idx: int
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
            parsed_track = self.track_factory.get_track(track,
                playlist_name,
                playlist_img,)
            self.recommendations.append(parsed_track)

    def add_recommendation(self, playlist_name, playlist_img, tracks) -> None:
        """Get the top 20 tracks from a playlist and get recommendations for them"""
        top_20 = sorted(
            tracks,
            key=lambda x: x["popularity"],
            reverse=True,
        )[:20]
        for idx in range(0, 15, 5):
            self.recommend_5_for_5(top_20, playlist_name, playlist_img, idx)

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