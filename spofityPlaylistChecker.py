import sys

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

import Playlist_operations
from IO_operations import read_groups_from_file
from IO_operations import safe_uri_content_to_hard_drive
from URI_operations import get_playlist_id_from_uri

REDIRECT_URI = "https://www.duckduckgo.com"

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


# TODO: currently only the first group can be read with this script
group = read_groups_from_file()[0]
RELEASE_RADAR = group.get_target_playlist()

if flag_authorization_code_flow:
    scope = "playlist-modify-private, user-follow-modify"  # to add more just add them separated by a comma
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, redirect_uri=REDIRECT_URI))

    new_tracks = []
    no_duplicates = []
    for playlist_data in group.get_playlist_tuples():
        name = playlist_data[0]
        uri = playlist_data[1]

        new_tracks = new_tracks + Playlist_operations.get_new_songs_in_playlist(sp, uri)

        # remove duplicates using list comprehension
        no_duplicates = [s for n, s in enumerate(new_tracks) if s not in new_tracks[:n]]

    if no_duplicates:
        print("emptying playlist")
        Playlist_operations.remove_all_songs_from_playlist(sp, RELEASE_RADAR)
        print("adding songs")
        Playlist_operations.add_songs_to_playlist(sp, RELEASE_RADAR, no_duplicates)
    else:
        print("no new songs")
    print("done")

else:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

    # playlist_data is a tuple (name, URI)
    for playlist_data in group.get_playlist_tuples():
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
