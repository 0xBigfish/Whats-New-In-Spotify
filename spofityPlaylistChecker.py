import spotipy
import sys
import json

from spotipy.oauth2 import SpotifyClientCredentials
from pprint import pprint

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

if len(sys.argv) > 1:
    name = ' '.join(sys.argv[1:])
else:
    name = 'while(1)'

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
resultsDict = sp.playlist_items(playlist_id='37i9dQZF1DX36edUJpD76c')

# get the playlists tracks
latestTracks = resultsDict["items"]

# read old playlist content from file
with open("ModusMio_content_raw(26.11.2020).txt", "r") as oldTrackFile:
    data = oldTrackFile.readline()  # only reads ONE line (json files have only one (very long) line)

    # if there is another line throw an error
    if oldTrackFile.readline() != "":
        print("error: not a json format (file has more than one single line)")
        # TODO: throw error

    oldResults = json.loads(data)
    oldTracks = oldResults["items"]


latestTracksNames = []
oldTracksNames = []

# both are a list of dictionaries each containing the song's name and its artists names
newSongs = []
removedSongs = []

print("comparing tracks")

# check the playlist for new songs
for newTrack in latestTracks:
    flagIsNewSong = True
    for oldTrack in oldTracks:
        # if the current track matches with a track in the old list, then it's not a new song
        if newTrack["track"]["name"] == oldTrack["track"]["name"]:
            flagIsNewSong = False
            break

    if flagIsNewSong:
        songInfo = {"name": newTrack["track"]["name"],
                    "artists": newTrack["track"]["artists"]}
        newSongs.append(songInfo)


# check the playlist for removed songs
for oldTrack in oldTracks:
    flagWasRemoved = True
    for newTrack in latestTracks:
        if oldTrack["track"]["name"] == newTrack["track"]["name"]:
            flagWasRemoved = False
            break

    if flagWasRemoved:
        songInfo = {"name": oldTrack["track"]["name"],
                    "artists": oldTrack["track"]["artists"]}
        removedSongs.append(songInfo)

print("-------------------------- New Songs: --------------------------")
for song in newSongs:
    print(song["name"])

print("------------------------ Removed Songs: ------------------------")
for song in removedSongs:
    print(song["name"])

# pprint(results)
