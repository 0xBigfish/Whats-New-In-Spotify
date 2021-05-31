# WhatsNewInSpotify

A little script that adds new songs in playlists and new releases from artist to a designated playlist.

## Installation


## How to get a Spotify URI or Spotify Link
### Playlists: 
Open your playlist in your Spotify desktop client or in the web browser. Next to the ```Play``` button should be three 
dots (or a button with three dots). Click this button, and then select ```Share```. Now you can select
``Copy Playlist Link`` or ``Copy Spotify URI`` depending on your Spotify version. 

When holding the ``alt`` key while the share window is still open, you should be able to select the corresponding other 
option.

### Artists:
Go to the artist profile in your Spotify desktop client or web browser. Above the artist's top songs and
right next to the ``Play`` button should be three dots (or a button with three dots). Click this button, and then select
```Share```. Now you can select ``Copy Artist Link`` or ``Copy Spotify URI`` depending on your Spotify version. 

When holding the ``alt`` key while the share window is still open, you should be able to select the corresponding other 
option.



## How to use
### Main window
In the top of the window you can select a group. In the middle the observed playlists and artist
of the currently selected group are shown. When running the script new songs added to these playlists and new
releases by these artists will be added to the previously set playlist, also shown just below
the group selection box. 

To add more playlist / artist or remove them see use the 'Add' or 'Remove' button.


### New group Window
Here you can create a new group. This could be useful for when you want sort your observed playlists
by genre. You could create one group for pop playlists and artists and another for hiphop playlists.

In the ```Group Name```field you can enter whatever name you want to name your playlist. In the ``Target playlist``
field you must enter a valid Spotify playlist URI or Spotify playlist link 
(see [here](#How-to-get-a-Spotify-URI-or-Spotify-Link)). Newly added songs in the playlists and new
releases by artists observed by this group will be added to this playlist.


### Remove group window
Here you can delete a previously creates group. Attention: a deleted group can NOT be restored.


### Run window
Probably the most used window. When you press "run" all new songs and new releases will be shown in separate windows
with respect to their playlist or artist.

You can choose to save the current playlist content / artist releases to the 
hard drive, in order to have a copy to compare later playlist / artist content to (**I recommend doing this every 
time you run the script**).

Other options are to add new songs and releases to the group's target playlist and to clear the playlist clear
before adding new songs.

You can also select a date from which the current content will be compared to. An example: you select 13.04.2021 as
date. If there is a content_file from this date, it will be used as comparison, otherwise the
script searches for the oldest content_file that dates to AFTER the given date; a file from 15.04.2021 for example.


### Add playlist / artist window
Here you can add new playlists and artist to the group's list of observed items. You have to enter a valid Spotify
playlist URI or Spotify artist URI (see [how to get a uri](#How-to-get-a-Spotify-URI-or-Spotify-Link))


### Remove playlist / artist window
Select one or more playlists / artist that will be removed from the group's list of
observed items. They will no longer be checked for new songs or releases when you run the script


### Settings window
You can change the group will be initially be shown when you start the script, and make a small visual
change here. Additionally, you can enter the ``Danger Zone`` where you can (soon) uninstall the program and clear
previously set Windows path variables


### Bonus features window
Coming soon (maybe, possibly, I don't know)


## Credits
This script utilizes the Spotipy library (Copyright (c) 2014 Paul Lamere).

You can find it here: https://github.com/plamere/spotipy
