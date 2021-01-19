import json

import spotipy

from IO_operations import find_latest_content_file
from IO_operations import safe_uri_content_to_hard_drive
from URI_operations import get_playlist_id_from_uri

RELEASE_RADAR = "spotify:playlist:7I0dtpfqqtcPYNsaJn32dF"


def print_playlist_changes(sp, p_uri):
    """
    Prints the changes made to the playlist, compared to the latest content file, to the console.

    :param p_uri: the spotify uri of the playlist
    :param sp: the Spotify API client
    :type p_uri: str
    :type sp: spotipy.Spotify
    """
    # results is a json file
    # object{7}:
    #   href: https://api.spoitfy....
    #   items [number_of_items]:
    #       0 {6}:
    #           added_at: 2020-12-27T23:01:00Z
    #           added_by {5}:
    #           is_local : false
    #           primary_color : null
    #           track{19}:
    #               album{13}:
    #               artists [number_of_artists] :
    #                   0 {6}:
    #                       external_urls {1}:
    #                       href:
    #                       id:
    #                       name:
    #                       type:
    #                       uri:
    #                   1 {6}:
    #                       ...
    #               available_markets [n_of_avail_markets] :
    #               disc_number : 1
    #               duration_ms : 140026
    #               episode : false
    #               explicit : true
    #               external_ids {1}:
    #               external_urls {1}:
    #               href: https://api.spotify..
    #               id : j01u0u401
    #               is_local : false
    #               name : Lost (feat. xyz)
    #               popularity : 80
    #               preview_url : null
    #               track : true
    #               track_number : 1
    #               type : track
    #               uri : spotify:track:sjfldlksjl
    #           video_thumbnail {1} :
    #       1 {6}:
    #           .....
    #
    #   limit : 100
    #   next : null
    #   offset: 0
    #   previous: null
    #   total : 50

    # playlist_items yields a dictionary or JSON file
    results_dict = sp.playlist_items(playlist_id=get_playlist_id_from_uri(p_uri))

    # get the playlists tracks
    latest_tracks = results_dict["items"]

    # read old playlist content from file
    latest_content_file = find_latest_content_file(p_uri)
    print(latest_content_file)

    # if a content file exists for the uri:
    if latest_content_file:
        with open(latest_content_file, "r") as oldTrackFile:
            data = oldTrackFile.readline()  # only reads ONE line (json files have only one (very long) line)

            # if there is another line throw an error
            if oldTrackFile.readline() != "":
                print("error: not a json format (file has more than one single line)")
                # TODO: throw error or stop further execution of this script

            old_results = json.loads(data)
            old_tracks = old_results["items"]

        # both are a list of dictionaries each containing the song's name and its artists names
        new_songs = []
        removed_songs = []

        # print("comparing tracks")

        # check the playlist for new songs
        for new_track in latest_tracks:
            flag_is_new_song = True
            for old_track in old_tracks:
                # if the current track matches with a track in the old list, then it's not a new song
                if new_track["track"]["uri"] == old_track["track"]["uri"]:
                    flag_is_new_song = False
                    break

            if flag_is_new_song:
                song_info = {"name": new_track["track"]["name"],
                             "artists": new_track["track"]["artists"]}
                new_songs.append(song_info)

        # check the playlist for removed songs
        for old_track in old_tracks:
            flag_was_removed = True
            for new_track in latest_tracks:
                if old_track["track"]["name"] == new_track["track"]["name"]:
                    flag_was_removed = False
                    break

            if flag_was_removed:
                song_info = {"name": old_track["track"]["name"],
                             "artists": old_track["track"]["artists"]}
                removed_songs.append(song_info)

        print("-------------------------- New Songs: --------------------------")
        for song in new_songs:
            artists = ""
            n_of_artists = len(song["artists"])

            for i in range(0, n_of_artists - 1):
                artists += song["artists"][i]["name"] + ", "
            artists += song["artists"][n_of_artists - 1]["name"]

            print(song["name"] + " - " + artists)

        print("------------------------ Removed Songs: ------------------------")
        for song in removed_songs:

            artists = ""
            n_of_artists = len(song["artists"])

            for i in range(0, n_of_artists - 1):
                artists += song["artists"][i]["name"] + ", "
            artists += song["artists"][n_of_artists - 1]["name"]

            print(song["name"] + " - " + artists)
    else:
        print("------------------- No data for playlist yet -------------------")


def add_new_songs_in_playlist_to_release_radar(sp, p_uri):
    """
    ! REQUIRES LOGIN !

    songs that have newly been added to this playlist will be added to the release radar

    :param p_uri: the spotify uri of the playlist
    :param sp: the Spotify API client
    :type p_uri: str
    :type sp: spotipy.Spotify
    :raise TypeError: the content file is not a json file.
    """
    # results is a json file
    # object{7}:
    #   href: https://api.spoitfy....
    #   items [number_of_items]:
    #       0 {6}:
    #           added_at: 2020-12-27T23:01:00Z
    #           added_by {5}:
    #           is_local : false
    #           primary_color : null
    #           track{19}:
    #               album{13}:
    #               artists [number_of_artists] :
    #                   0 {6}:
    #                       external_urls {1}:
    #                       href:
    #                       id:
    #                       name:
    #                       type:
    #                       uri:
    #                   1 {6}:
    #                       ...
    #               available_markets [n_of_avail_markets] :
    #               disc_number : 1
    #               duration_ms : 140026
    #               episode : false
    #               explicit : true
    #               external_ids {1}:
    #               external_urls {1}:
    #               href: https://api.spotify..
    #               id : j01u0u401
    #               is_local : false
    #               name : Lost (feat. xyz)
    #               popularity : 80
    #               preview_url : null
    #               track : true
    #               track_number : 1
    #               type : track
    #               uri : spotify:track:sjfldlksjl
    #           video_thumbnail {1} :
    #       1 {6}:
    #           .....
    #
    #   limit : 100
    #   next : null
    #   offset: 0
    #   previous: null
    #   total : 50

    # playlist_items yields a dictionary or JSON file
    results_dict = sp.playlist_items(playlist_id=get_playlist_id_from_uri(p_uri))

    # get the playlists tracks
    latest_tracks = results_dict["items"]

    # read old playlist content from file
    latest_content_file = find_latest_content_file(p_uri)

    # if a content file exists for the uri:
    if latest_content_file:
        with open(latest_content_file, "r") as old_track_file:
            data = old_track_file.readline()  # only reads ONE line (json files have only one (very long) line)

            # if there is another line throw an error
            if old_track_file.readline() != "":
                raise TypeError("The content file is not a json file. Json files have only one (very long) line.")

            old_results = json.loads(data)
            old_tracks = old_results["items"]

        # both are a list of dictionaries each containing the song's name and its artists names
        new_songs = []

        # check the playlist for new songs
        for new_track in latest_tracks:
            flag_is_new_song = True
            for oldTrack in old_tracks:
                # if the current track matches with a track in the old list, then it's not a new song
                if new_track["track"]["uri"] == oldTrack["track"]["uri"]:
                    flag_is_new_song = False
                    break

            if flag_is_new_song:
                song_uri = new_track["track"]["uri"]
                new_songs.append(song_uri)

        # add new songs to the release radar
        if len(new_songs) > 0:  # an error occurs when trying to add an empty list of uris to the playlist
            add_songs_to_playlist(sp, RELEASE_RADAR, new_songs)

    else:
        # if there are no records of the playlist yet, create the first record
        safe_uri_content_to_hard_drive(sp, p_uri)


def create_new_private_playlist(sp, name):
    """
    ! REQUIRES LOGIN TO SPOTIFY !

    creates a new playlist called <name> for the user that is currently logged in

    :param sp: the Spotify API client
    :param name: what the playlist will be named
    :type sp: spotipy.Spotify
    :type name: str
    """
    sp.user_playlist_create(user=sp.current_user()["id"], name=name, public=False)


def add_song_to_playlist(sp, playlist_uri, song_uri):
    """
    ! REQUIRES LOGIN TO SPOTIFY !

    adds a song to a playlist

    :param sp: the Spotify API client
    :param song_uri: the uri of the song that will be added
    :param playlist_uri: the uri of the playlist that the song will be added to
    :type sp: spotipy.Spotify
    :type song_uri: str
    :type playlist_uri: str
    """
    playlist_id = get_playlist_id_from_uri(playlist_uri)
    sp.playlist_add_items(playlist_id, [song_uri])


def add_songs_to_playlist(sp, playlist_uri, song_uris):
    """
    ! REQUIRES LOGIN TO SPOTIFY !

    adds multiple songs to a playlist

    :param sp: the Spotify API client
    :param song_uris: the list of uris of the songs that will be added
    :param playlist_uri: the uri of the playlist that the song will be added to
    :type sp: spotipy.Spotify
    :type song_uris: list
    :type playlist_uri: str
    """
    playlist_id = get_playlist_id_from_uri(playlist_uri)
    sp.playlist_add_items(playlist_id, song_uris)


def remove_song_from_playlist(sp, playlist_uri, song_uri):
    """
    ! REQUIRES LOGIN TO SPOTIFY !

    removes all occurrences of the song in the playlist

    :param sp: the Spotify API client
    :param song_uri: the uri of the song that will be removed
    :param playlist_uri: the uri of the playlist that the song will be removed from
    :type sp: spotipy.Spotify
    :type song_uri: str
    :type playlist_uri: str
    """
    playlist_id = get_playlist_id_from_uri(playlist_uri)
    sp.playlist_remove_all_occurrences_of_items(playlist_id, [song_uri])


def remove_songs_from_playlist(sp, playlist_uri, song_uris):
    """
    ! REQUIRES LOGIN TO SPOTIFY !

    removes all occurrences of the song in the playlist

    :param sp: the Spotify API client
    :param song_uris: the list of uris of the song that will be removed
    :param playlist_uri: the uri of the playlist that the songs will be removed from
    :type sp: spotipy.Spotify
    :type song_uris: list
    :type playlist_uri: str
    """
    playlist_id = get_playlist_id_from_uri(playlist_uri)
    sp.playlist_remove_all_occurrences_of_items(playlist_id, song_uris)
