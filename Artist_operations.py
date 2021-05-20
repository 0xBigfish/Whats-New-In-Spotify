import json
from datetime import date

from IO_operations import find_latest_content_file, save_uri_content_to_hard_drive
from URI_operations import *


def get_all_albums_from_artist(sp, a_uri, album_type=None):
    """
    Returns a list of dictionaries holding each albums uri, name, artist(s), group and type.

    Dictionary fields:
        - "uri" : str
        - "name" : str
        - "artists" : list(str)
        - "album_group" : str
        - "album_type" : str

    **If no content file is found for the album, a new content file is created.**

    :param a_uri: the spotify uri of the artist
    :param sp: the Spotify API client
    :param album_type: filter for albums (values: "album", "single", "compilation"
    :type a_uri: str
    :type sp: spotipy.Spotify
    :type album_type: str
    :return: a list of dictionaries each representing an album by the artist
    """
    # "items": [
    #    {
    #        "album_group": <"album" or "single" or "appears_on">,
    #        "album_type": <"album" or "single" or "compilation">,
    #        "artists": [
    #            {
    #                "external_urls":
    #                "href": "https://api.spotify.com/..."
    #                "id": "<album_id>",
    #                "name": <artist name>,
    #                "type": "artist",
    #                "uri": <spotify artist uri>
    #            }
    #        ],
    #        "available_markets": []
    #        ],
    #        "external_urls": {}
    #        "href": "https://api.spotify.com/....",
    #        "id": <id>,
    #        "images": [],
    #        "name": <album name>,
    #        "release_date": "2021-04-29",
    #        "release_date_precision": "day",
    #        "total_tracks": 13,
    #        "type": "album",
    #        "uri": "spotify:album:<id>"
    #    },
    #    ...
    #    ]
    results_dict = sp.artist_albums(artist_id=get_artist_id_from_uri(a_uri), album_type=album_type)

    # get the playlists tracks
    albums = results_dict["items"]

    # data is a list of dictionaries, each representing an album.
    data = []
    for n, track in enumerate(albums):
        data.insert(n, {"uri": albums[n]["uri"],
                        "name": albums[n]["name"],
                        "artists": [art["name"] for art in albums[n]["artists"]],
                        "album_group": albums[n]["album_group"],
                        "album_type": albums[n]["album_type"]
                        })

    return data


def get_new_albums(sp, a_uri, since_date=None, as_dict=False):
    """
    Albums that have newly been released by the artist or feature them will be returned as a list of album URIs.
    Alternatively a list of dictionaries can be returned using the ``as_dict`` flag, which are holding
    each albums uri, name and artist(s)

    Dictionary fields:
        - "uri" : str
        - "name" : str
        - "artists" : list(str)

    **If no content file is found for the artist, a new content file is created.**

    :param a_uri: the spotify uri of the artist
    :param sp: the Spotify API client
    :param since_date: a date
    :param as_dict: flag to return a dictionary with more information about an album
    :type a_uri: str
    :type sp: spotipy.Spotify
    :type since_date: date
    :type as_dict: bool
    :return: an empty list when no content file is found, a list of uris or a list of dictionaries
    """
    # search for a content file
    if since_date is None:
        latest_content_file = find_latest_content_file(a_uri)
    else:
        latest_content_file = find_latest_content_file(a_uri, since_date)

    # if a content file exists for the uri:
    if latest_content_file:

        # read old artist data from file
        with open(latest_content_file, "r") as old_artist_file:
            old_data = json.load(old_artist_file)
            old_album_uris = [album_data["uri"] for album_data in old_data["items"]]

        # get the uri, name and artist(s) of every album released by or featuring the artist
        # entries of artist_data: {"uri" : <song_uri>,
        #                          "name": <song_name>,
        #                          "artists: <song_artist(s)>}
        artist_data = get_all_albums_from_artist(sp, a_uri)

        # check the playlist for new songs by checking whether their uri was already in the old content_file
        new_albums = [data for data in artist_data if not old_album_uris.__contains__(data["uri"])]

        # remove duplicate entries using list comprehension
        no_duplicates = [s for n, s in enumerate(new_albums) if s not in new_albums[:n]]

        if as_dict:
            return no_duplicates
        else:
            # only return the uris of the new albums
            return [elem["uri"] for elem in no_duplicates]

    else:
        # if there are no records of the artist yet, create the first record
        save_uri_content_to_hard_drive(sp, a_uri)
        return []


def get_all_songs_from_album(sp, alb_uri):
    """
    Returns a list of dictionaries holding uri, name and artist(s) of each track in the album

    Dictionary fields:
        - "uri" : str
        - "name" : str
        - "artists" : list(str)

    **If no content file is found for the album, a new content file is created.**

    :param alb_uri: the spotify uri of the album
    :param sp: the Spotify API client
    :type alb_uri: str
    :type sp: spotipy.Spotify
    :return: a list of dictionaries each representing a track in the album
    """
    results_dict = sp.album_tracks(album_id=alb_uri)  # album_id can be an ID, URI or URL

    # get the album tracks
    tracks = results_dict["items"]

    # data is a list of dictionaries, each representing a song.
    data = []
    for n, track in enumerate(tracks):
        data.insert(n, {"uri": tracks[n]["uri"],
                        "name": tracks[n]["name"],
                        "artists": [art["name"] for art in tracks[n]["artists"]]
                        })

    return data


def get_artists_songs_from_album(sp, alb_uri, art_uri):
    """
    Returns a list of dictionaries holding uri, name and artist(s) of each track in the album that features the artist
    specified by ``art_uri``.

    **Hint**: 'artists' in the method name represents 'artist's' and is not the plural of artists. Only pass the uri
    of ONE artist in ``art_uri``

    Dictionary fields:
        - "uri" : str
        - "name" : str
        - "artists" : list(str)

    **If no content file is found for the album, a new content file is created.**

    :param alb_uri: the spotify uri of the album
    :param sp: the Spotify API client
    param art_uri: the artist's uri
    :type alb_uri: str
    :type sp: spotipy.Spotify
    :type art_uri: str
    :return: a list of dictionaries each representing a track released by the artist in the album
    """
    results_dict = sp.album_tracks(album_id=alb_uri)  # album_id can be an ID, URI or URL

    # get the album tracks
    tracks = results_dict["items"]

    # data is a list of dictionaries, each representing a song.
    data = []
    for n, track in enumerate(tracks):
        if [ar_uri for ar_uri in tracks[n]["artists"]["uri"]].__contains__(art_uri):
            data.insert(n, {"uri": tracks[n]["uri"],
                            "name": tracks[n]["name"],
                            "artists": [art["name"] for art in tracks[n]["artists"]]
                            })

    return data
