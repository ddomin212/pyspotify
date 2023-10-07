class TrackFactory:
    def __init__(self, sp) -> None:
        self.sp = sp
    
    def get_track(self, track_info, playlist_name, playlist_img) -> dict:
        track = Track(
            track_info,
            playlist_name,
            playlist_img,
        )
        return track.get_parsed(self.sp)

class Track:
    def __init__(self, track_info, playlist_name, playlist_img) -> None:
        self.raw_info = track_info
        self.playlist_name = playlist_name
        self.playlist_img = playlist_img

    def get_parsed(
        self, sp
    ) -> dict:
        track_info = self.get_track_info(sp)

        if self.playlist_name and self.playlist_img:
            track_info["playlist_name"] = self.playlist_name
            track_info["playlist_img"] = self.playlist_img

        relevant_features_data = self.get_track_audio_features(
            sp, track_info["track_uri"]
        )

        return {
            **track_info,
            **relevant_features_data,
        }

    def get_track_info(
        self, sp
    ) -> dict[str, str | int]:
        """Get the information we need from a track object

        Args:
            track: track JSON object

        Returns:
            track_info: dictionary with the relevant information
        """
        track_info = {
            "artist_name": self.raw_info["artists"][0]["name"],
            "artist_uri": self.raw_info["artists"][0]["uri"],
            "artist_img": self.get_artist_img(sp),
            "track_name": self.raw_info["name"],
            "popularity": self.raw_info["popularity"],
            "release_date": self.raw_info["album"]["release_date"],
            "album_cover": self.raw_info["album"]["images"][0]["url"],
            "album_name": self.raw_info["album"]["name"],
            "track_uri": self.raw_info["uri"].split(":")[-1],
        }
        return track_info
    
    def get_track_audio_features(self, sp, track_uri: str) -> dict[str, float]:
        """Get the audio features for a track

        Args:
            track_uri: the uri of the track

        Returns:
            relevant_features_data: dictionary with the relevant audio features
        """
        audio_features_data = sp.audio_features(track_uri)[0]
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
    
    def get_artist_img(self, sp) -> str:
        """Get the image of an artist, if none, use a placeholder, used for nice visuals in dashboard

        Args:
            uri: artirst uri

        Returns:
            the URL for an image of the artist
        """
        artist_data = sp.artist(self.raw_info["artists"][0]["uri"])
        if len(artist_data["images"]) > 0:
            artist_img = artist_data["images"][0]["url"]
        else:
            artist_img = "https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png?20170328184010"
        return artist_img