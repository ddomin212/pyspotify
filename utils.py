import pandas as pd


def export(
    playlist_data: list[dict[str, str | float | int]],
    playlist_recommend: list[dict[str, str | float | int]],
) -> None:
    df = pd.DataFrame(playlist_data)
    df.to_csv("playlist_data.csv", index=False)

    df = pd.DataFrame(playlist_recommend)
    df.to_csv("playlist_recommend.csv", index=False)
