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
