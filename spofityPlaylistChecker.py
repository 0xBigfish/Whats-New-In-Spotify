import sys

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

import Playlist_operations
from IO_operations import read_playlists_uris_from_file
from IO_operations import safe_uri_content_to_hard_drive
from URI_operations import get_playlist_id_from_uri

REDIRECT_URI = "https://www.duckduckgo.com"
RELEASE_RADAR = "spotify:playlist:7I0dtpfqqtcPYNsaJn32dF"

# Check if any of the flags have been set
flag_save_content_to_file = False
flag_authorization_code_flow = False
if len(sys.argv) > 1:
    print(sys.argv)
    for arg in sys.argv:
        if arg == "save":
            flag_save_content_to_file = True

        if arg == "authorization":
            flag_authorization_code_flow = True


if flag_authorization_code_flow:
    scope = "playlist-modify-private, user-follow-modify"  # to add more just add them separated by a comma
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, redirect_uri=REDIRECT_URI))

    playlist_list = read_playlists_uris_from_file()
    new_tracks = []
    for playlist_data in playlist_list:
        name = playlist_data[0]
        uri = playlist_data[1]

        new_tracks = new_tracks + Playlist_operations.get_new_songs_in_playlist(sp, uri)

        # remove duplicates using list comprehension
        no_duplicates = [s for n, s in enumerate(new_tracks) if s not in new_tracks[:n]]

    print("adding songs")
    Playlist_operations.add_songs_to_playlist(sp, RELEASE_RADAR, no_duplicates)
    print("done")

else:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

    playlist_list = read_playlists_uris_from_file()

    # playlist_data is a tuple (name, URI)
    for playlist_data in playlist_list:
        name = playlist_data[0]
        uri = playlist_data[1]
        playlist_id = get_playlist_id_from_uri(uri)

        print("\n\n##########################################")
        print("Checking content of '" + name + "'")
        print("Playlist ID: " + playlist_id)
        print("##########################################\n")
        Playlist_operations.print_playlist_changes(sp, uri)

        if flag_save_content_to_file:
            print("############ Saving Content of " + name + " To Hard Drive ############")
            safe_uri_content_to_hard_drive(sp, uri)
