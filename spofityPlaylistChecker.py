import spotipy
import sys
import json

from spotipy.oauth2 import SpotifyClientCredentials
from pprint import pprint


spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

if len(sys.argv) > 1:
    name = ' '.join(sys.argv[1:])
else:
    name = 'while(1)'

results = spotify.playlist_items(playlist_id='37i9dQZF1DX36edUJpD76c')

with open("ModusMio_content.txt", "w") as file:
    file.write(json.dumps(results))

#pprint(results)