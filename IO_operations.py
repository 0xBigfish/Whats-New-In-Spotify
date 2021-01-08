import json
import re
from datetime import date

# check valid line with a regular expression
name_re = "[^#].*"  # ".*" is any number (including zero) of any characters (including whitespaces), "^#" matches any
# character except "#"
uri_artist_re = "spotify:artist:\S*"  # \S matches any non-whitespace character
uri_playlist_re = "spotify:playlist:\S*"


def safe_playlist_to_hard_drive(sp, playlist_id):
    """
    :param sp: the connection to spotify ( like sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
     for example )
    :param playlist_id: the spotify id of the playlist
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


def read_playlists_and_artists_from_file():
    """
    Reads playlists and artists URIs from file and return them as a list of tuples: (<name>, <URI>)

    :return: a list of (name, URI) tuples
    """

    p_and_a_list = []

    # noinspection RegExpDuplicateAlternationBranch
    # a warning is thrown but this is the correct pattern !!
    # "\s*" = any number of any whitespace character
    regex = re.compile(name_re + "=\s*" + uri_playlist_re + "|" +
                       name_re + "=\s*" + uri_artist_re, re.IGNORECASE)

    with open("playlists_and_artists.txt", "r") as file:
        lines = file.readlines()

    # entries must be of format: "<name> = <URI>", extract them using the regular expression
    for line in lines:
        match = regex.match(line)

        # if a part of the line matches the regex
        if match:
            name_and_uri = match.group()  # get the matched string
            tup = (name_and_uri.partition("=")[0], name_and_uri.partition("=")[2])  # split it at the "="
            p_and_a_list.append(tup)

    return p_and_a_list


def read_playlists_from_file():
    """
    Reads playlists URIs from file and return them as a list of tuples: (<name>, <URI>)

    :return: a list of (name, URI) tuples
    """

    p_and_a_list = []

    # noinspection RegExpDuplicateAlternationBranch
    # a warning is thrown but this is the correct pattern !!
    # "\s*" = any number of any whitespace character
    regex = re.compile(name_re + "=\s*" + uri_playlist_re, re.IGNORECASE)

    with open("playlists_and_artists.txt", "r") as file:
        lines = file.readlines()

    # entries must be of format: "<name> = <URI>", extract them using the regular expression
    for line in lines:
        match = regex.match(line)

        # if a part of the line matches the regex
        if match:
            name_and_uri = match.group()  # get the matched string
            tup = (name_and_uri.partition("=")[0], name_and_uri.partition("=")[2])  # split it at the "="
            p_and_a_list.append(tup)

    return p_and_a_list


def read_artists_from_file():
    """
    Reads artists URIs from file and return them as a list of tuples: (<name>, <URI>)

    :return: a list of (name, URI) tuples
    """

    p_and_a_list = []

    # noinspection RegExpDuplicateAlternationBranch
    # a warning is thrown but this is the correct pattern !!
    # "\s*" = any number of any whitespace character
    regex = re.compile(name_re + "=\s*" + uri_artist_re, re.IGNORECASE)

    with open("playlists_and_artists.txt", "r") as file:
        lines = file.readlines()

    # entries must be of format: "<name> = <URI>", extract them using the regular expression
    for line in lines:
        match = regex.match(line)

        # if a part of the line matches the regex
        if match:
            name_and_uri = match.group()  # get the matched string
            tup = (name_and_uri.partition("=")[0], name_and_uri.partition("=")[2])  # split it at the "="
            p_and_a_list.append(tup)

    return p_and_a_list
