import re

import IO_operations

# ------------------------------------------------ Regular Expressions ------------------------------------------------
#
#                   Visit https://regex101.com/ for a graphical explanation of what a given RE does
#                                      (ensure to choose Python for RE semantic)
#

# a link has the following structure:
#           https://open.spotify.com/<type>/<id>?si=<some_parameter_id>
#
# regular expression to check validity and extract information from the link ('\' is the escape character)
# the RE has the named groups 'type' and 'id'
# type can be 'playlist', 'artist', 'track' or 'episode' (for podcast episodes)
# A link has the format
#         https://open.spotify.com/<type>/<id>?si=<some_parameter_id>
_LINK_RE = "https:\/\/open\.spotify\.com\/(?P<type>(?:playlist)|(?:artist)|(?:track)|(?:episode))\/(?P<id>\S*)\?\S*"


def get_playlist_id_from_uri(uri):
    """
    Extracts the ID out of the URI. The ID is the code at the end of the URI, for example: \n
        URI = spotify:playlist:37xk3QZF1DX36edUJpD76c \n
    =>  ID = 37xk3QZF1DX36edUJpD76c

    :param uri: the URI of the playlist
    :type uri: str
    :raise ValueError: URI is not a playlist URI
    :return: the ID of the playlist
    """
    temp = uri.partition(":")[2]
    if temp.partition(":")[0] != "playlist":
        raise ValueError("URI is not not a playlist URI! URI type: " + temp.partition(":")[0])

    return temp.partition(":")[2]


def get_artist_id_from_uri(uri):
    """
    Extracts the ID out of the URI. The ID is the code at the end of the URI, for example: \n
        URI = spotify:artist:37i9dQZFdkLX36edUJpD76c \n
    =>  ID = 37i9dQZFdkLX36edUJpD76c

    :param uri: the URI of the artist
    :type uri: str
    :raise ValueError: URI is not a artist URI
    :return: the ID of the playlist
    """
    temp = uri.partition(":")[2]
    if temp.partition(":")[0] != "artist":
        raise ValueError("URI is not not an artist URI! URI type: " + temp.partition(":")[0])

    return temp.partition(":")[2]


def get_song_id_from_uri(uri):
    """
    Extracts the ID out of the URI. The ID is the code at the end of the URI, for example: \n
        URI = spotify:song:37i9dQZFdkLX36edUJpD76c \n
    =>  ID = 37i9dQZFdkLX36edUJpD76c

    :param uri: the URI of the song
    :type uri: str
    :raise ValueError: URI is not a artist URI
    :return: the ID of the playlist
    """
    temp = uri.partition(":")[2]
    if temp.partition(":")[0] != "track":
        raise ValueError("URI is not not a song URI! URI type: " + temp.partition(":")[0])

    return temp.partition(":")[2]


def is_playlist_uri(given_string):
    """
    Check whether or not a given string is a spotify playlist URI.


    Attention: The string MUST NOT contain anything else than the URI.
        For example: If there is a whitespace at the end
        of the URI the method will return false

    :param given_string: the string that will be checked
    :type given_string: str
    :return: True when the given string is a Spotify playlist URI, False when not
    """
    uri_playlist_re = IO_operations.get_playlist_re()

    # if there is a match and the match is the whole original string, the match is correct
    match = re.match(uri_playlist_re, given_string)
    if match and match.group(0) == given_string:
        return True
    else:
        return False


def is_artist_uri(given_string):
    """
    Check whether or not a given string is a spotify artist URI.


    Attention: The string MUST NOT contain anything else than the URI.
        For example: If there is a whitespace at the end
        of the URI the method will return false

    :param given_string: the string that will be checked
    :type given_string: str
    :return: True when the given string is a Spotify artist URI, False when not
    """
    uri_artist_re = IO_operations.get_artist_re()

    # if there is a match and the match is the whole original string, the match is correct
    match = re.match(uri_artist_re, given_string)
    if match and match.group(0) == given_string:
        return True
    else:
        return False


def is_link(given_link):
    """
    Check whether or not a given string is a link to a spotify playlist / artist / track / episode

        Attention: The string MUST NOT contain anything else than the URI.
        For example: If there is a whitespace at the end
        of the URI the method will return false

    :param given_link: the string that will be checked
    :type given_link: str
    :return: True when the given link is a link to one of the above specified entities (playlist / ...), False when not
    """
    # if there is a match and the match is the whole original string, the match is correct
    match = re.match(_LINK_RE, given_link)
    if match and match.group(0) == given_link:
        return True
    else:
        return False


def transform_link_to_uri(given_link):
    """
    Transforms a spotify link to a uri. A link has the format
        https://open.spotify.com/<type>/<id>?si=<some_parameter_id>


    Current spotify desktop version 1.1.58.820.g2ae50076-a offers a 'copy link to playlist' and '... to artist' instead
    of 'copy playlist uri'. To get the uri one has to hold the 'alt' key when clicking the 'copy link' button.

    In order to offer flexibility this methods transformed this copied link into a regular spotify uri

    :param given_link: the link to the playlist or artist
    :type given_link: str
    :return: the uri of the playlist or artist the link refers to
    """
    # if there is a match and the match is the whole original string, the match is correct
    match = re.match(_LINK_RE, given_link)
    if match and match.group(0) == given_link:
        # transform the link to an uri
        # uri format: spotify:<type>:<id>
        uri = "spotify:" + match.group('type') + ":" + match.group('id')
        return uri

    else:
        return None
