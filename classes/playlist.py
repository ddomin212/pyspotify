from tqdm import tqdm
from .track import Track

class Playlist:
    def __init__(self, playlist) -> None:
        self.get_playlist_info(playlist)

    def get_playlist_info(self, info: dict) -> tuple[str, str, str]:
        """Get the information we need from a playlist object

        Args:
            playlist: the playlist JSON object

        Returns:
            playlist_name: the name of the playlist
            img: the cover of the playlist on Spotify for nice visuals in dashboard
            playlist_id: the id of the playlist
        """
        if len(info["images"]) > 0:
            img = info["images"][0]["url"]
        else:
            img = "https://iili.io/HlHy9Yx.png"

        self.name, self.img, self.id = info["name"], img, info["id"]

    def get_playlist_tracks(
        self, sp, track_factory
    ) -> None:
        """Get all the tracks from a playlist"""
        tracks_data = sp.playlist_tracks(self.id)

        parsed_tracks = []

        for track in tqdm(tracks_data["items"]):
            track = track_factory.get_track(track["track"],
                                                self.name,
                                                self.img,)
            parsed_tracks.append(track)

        return parsed_tracks
