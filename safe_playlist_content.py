import json
from datetime import date


def safe_playlist_to_hard_drive(sp, playlist_id):
    """
    :param sp: the connection to spotify ( like sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
     for example )
    :type sp: Spotify
    :type playlist_id: str
    """

    # get current date and change the date format to dd.mm.yyyy
    today = str(date.today())  # current format: yyyy-mm-dd
    today = today.split("-")[2] + "." + today.split("-")[1] + "." + today.split("-")[0]

    with open("ModusMio_content_raw(" + today + ").txt", "w") as file:
        content = sp.playlist_items(playlist_id=playlist_id)
        json.dump(content, file)
        file.close()
