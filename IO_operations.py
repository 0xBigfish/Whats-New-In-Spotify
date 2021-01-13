import json
import re
from datetime import date
import pathlib
from os import listdir
import os.path
from URI_operations import get_playlist_id_from_uri

name_of_content_directory = "content_files"

# ------------------------------------------------ Regular Expression --------------------------------------------------
# check valid line with a regular expression
name_re = "[^#].*"  # ".*" is any number (including zero) of any characters (including whitespaces), "^#" matches any
# character except "#"
uri_artist_re = "spotify:artist:\S*"  # \S matches any non-whitespace character
uri_playlist_re = "spotify:playlist:\S*"


def safe_playlist_to_hard_drive(sp, uri):
    """
    Saves the playlist's content to a file

    :param sp: the connection to spotify ( like sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
     for example )
    :param uri: the spotify uri of the playlist
    :type sp: Spotify
    :type uri: str
    """

    # get current date and change the date format to yyyy.mm.dd
    today = str(date.today())  # current format: yyyy-mm-dd
    today = today.replace("-", ".")

    # rename a uri "spotify:playlist:37 ..." to "spotify_playlist_37 ..."
    uri_directory_name = uri.replace(":", "_")
    file_name = uri_directory_name + "_content_raw(" + today + ").txt"

    # get main directory (all .py files are in the main directory)
    main_dir_path = os.path.dirname(__file__)  # returns the directory of this file

    # navigate to the directory containing all content file directories
    content_file_dir_path = os.path.join(main_dir_path, name_of_content_directory)

    uri_directory_path = os.path.join(content_file_dir_path, uri_directory_name)

    # check if the needed directory already exists, if not create it
    try:
        os.mkdir(uri_directory_path)
    except FileExistsError:
        print("directory " + uri_directory_name + " already exists")
    finally:
        # get the content of the playlist and save it into a file called <uri>_(<currentDate>).txt
        file_path = os.path.join(uri_directory_path, file_name)
        with open(file_path, "w") as file:
            content = sp.playlist_items(playlist_id=get_playlist_id_from_uri(uri))
            json.dump(content, file)
            file.close()


def read_playlists_and_artists_uris_from_file():
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


def read_playlists_uris_from_file():
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


def read_artists_uris_from_file():
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


def find_latest_content_file(uri):
    """
    Searches for the most recently saved content file of the playlist

    :param uri: the spotify URI of the playlist / artist
    :type uri: str
    :return: the path as a pathlib.Path object. When no file was found for URI, "None" is returned
    """

    # directory structure:
    # main dir (containing all the .py files)
    #   - content_files ( =name_of_content_directory )
    #       -spotify:playlist:<id>
    #           -spotify:playlist:<id>_content_raw_<date> (dictionary / json file)
    #           -spotify:playlist:<id>_content_raw_<date2> (dictionary / json file)
    #           ...
    #       -spotify:artist:<id>
    #           ...

    # remove ":" from uri and replace them with "_" as ":" may not be part of filename on some OS
    uri = uri.replace(":", "_")

    # get main directory (all .py files are in the main directory)
    main_dir_path = os.path.dirname(__file__)  # returns the directory of this file

    # navigate to the directory containing all content file directories
    content_file_dir_path = os.path.join(main_dir_path, name_of_content_directory)

    # list all files and directories of the content directory (NOT recursive)
    content_overview = listdir(content_file_dir_path)

    # list all available content files for the given uri and sort them
    for directory in content_overview:
        if directory == uri and not os.path.isfile(directory):
            # find the newest / most recently saved content file
            content_files = listdir(os.path.join(content_file_dir_path, directory))
            content_files.sort()

            # because of the date format yyyy.mm.dd the newest file will be at the end of the SORTED list
            latest_content_file = content_files[len(content_files)-1]

            # return the path to the file as a Path object (better than a String when run on different OS)
            return pathlib.Path(os.path.join(content_file_dir_path, directory, latest_content_file))

    # if no content file is found, return nothing
    return None
