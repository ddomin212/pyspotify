import unittest

import spotipy
from dotenv import load_dotenv

from spotipyPipe import SpotifyPipeline

load_dotenv()


class TestSpotifyPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = SpotifyPipeline(["Lounge Jazz"])
        self.playlist_dummy = {
            "name": "Lounge Jazz",
            "images": [{"url": "https://iili.io/HlHy9Yx.png"}],
            "id": "37i9dQZF1DXbl3JqaogQ4y",
        }
        self.track_dummy = {
            "artists": [
                {
                    "name": "Tame Impala",
                    "uri": "5INjqkS1o8h1imAzPqGZBb",
                }
            ],
            "name": "The Less I Know The Better",
            "popularity": 79,
            "album": {
                "release_date": "2015-07-17",
                "images": [
                    {
                        "url": "https://i.scdn.co/image/ab67616d0000b2739e1cfc756886ac782e363d79"
                    }
                ],
                "name": "Currents",
            },
            "uri": "spotify:track:6K4t31amVTZDgR3sKmwUJJ",
        }
        self.relevant_features = [
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
        self.parsed_features = {
            "artist_name": "Tame Impala",
            "artist_uri": "5INjqkS1o8h1imAzPqGZBb",
            "artist_img": self.pipeline.get_artist_img(
                "5INjqkS1o8h1imAzPqGZBb"
            ),
            "popularity": 79,
            "track_name": "The Less I Know The Better",
            "release_date": "2015-07-17",
            "album_cover": "https://i.scdn.co/image/ab67616d0000b2739e1cfc756886ac782e363d79",
            "album_name": "Currents",
            "track_uri": "6K4t31amVTZDgR3sKmwUJJ",
        }

    def test_get_spotipy_client(self):
        self.assertIsNotNone(self.pipeline.get_spotipy_client())
        self.assertEqual(
            isinstance(
                self.pipeline.get_spotipy_client(), spotipy.client.Spotify
            ),
            True,
        )

    def test_get_playlist_info(self):
        self.assertEqual(
            self.pipeline.get_playlist_info(self.playlist_dummy),
            (
                "Lounge Jazz",
                "https://iili.io/HlHy9Yx.png",
                "37i9dQZF1DXbl3JqaogQ4y",
            ),
        )

    def test_get_recommendations_for_playlist(self):
        self.pipeline.get_recommendations_for_playlist(
            "Lounge Jazz",
            "37i9dQZF1DXbl3JqaogQ4y",
            "https://iili.io/HlHy9Yx.png",
        )
        self.assertEqual(len(self.pipeline.global_track_list), 100)
        self.assertEqual(len(self.pipeline.playlist_track_list), 0)

    def test_get_artist_img(self):
        self.assertEqual(
            self.pipeline.get_artist_img("0TnOYISbd1XYRBk9myaseg"),
            "https://i.scdn.co/image/ab6761610000e5eb6761852cd2852fceb64e8cd9",
        )

    def test_track_info(self):
        response = self.pipeline.get_track_info(self.track_dummy)
        self.assertEqual(response, self.parsed_features)

    def test_get_playlist_tracks(self):
        self.pipeline.get_playlist_tracks(
            "37i9dQZF1DXbl3JqaogQ4y",
            "Lounge Jazz",
            "https://iili.io/HlHy9Yx.png",
        )
        self.assertEqual(len(self.pipeline.playlist_track_list), 100)

    def test_get_audio_features(self):
        response = self.pipeline.get_audio_features("6K4t31amVTZDgR3sKmwUJJ")
        self.assertEqual(
            all(
                elem in list(response.keys())
                for elem in self.relevant_features
            ),
            True,
        )

    def test_parse_add_track(self):
        dummy_accumulator = []
        self.pipeline.parse_add_track(
            self.track_dummy,
            dummy_accumulator,
            "Random Playlist",
            "https://iili.io/HlHy9Yx.png",
        )
        self.assertEqual(len(dummy_accumulator), 1)
        all_keys = (
            list(self.parsed_features.keys())
            + ["playlist_name", "playlist_img"]
            + self.relevant_features
        )
        self.assertEqual(
            all(
                elem in list(dummy_accumulator[0].keys()) for elem in all_keys
            ),
            True,
        )

    def test_recommend_5_for_5(self):
        dummy_tracks = [self.parsed_features] * 20
        self.pipeline.recommend_5_for_5(dummy_tracks, 0)
        self.assertEqual(len(self.pipeline.recommendations), 5)

    def test_spotify_recommendation(self):
        self.pipeline.get_playlist_tracks(
            "37i9dQZF1DXbl3JqaogQ4y",
            "Lounge Jazz",
            "https://iili.io/HlHy9Yx.png",
        )
        self.pipeline.spotify_recommendation()
        self.assertEqual(len(self.pipeline.recommendations), 15)

    def test_create_recommendation_playlist(self):
        self.pipeline.get_playlist_tracks(
            "37i9dQZF1DXbl3JqaogQ4y",
            "Lounge Jazz",
            "https://iili.io/HlHy9Yx.png",
        )
        self.pipeline.spotify_recommendation()
        self.pipeline.create_recommendation_playlist()
        playlists = self.pipeline.sp.current_user_playlists(limit=50)
        playlist_id = None
        for i in playlists["items"]:
            if i["name"] == "Recommended from pyspotify":
                playlist_id = i["id"]
                self.assertEqual(
                    i["tracks"]["total"],
                    15,
                )
                break
        self.assertEqual(
            playlist_id == None,
            False,
        )


if __name__ == "__main__":
    unittest.main()
