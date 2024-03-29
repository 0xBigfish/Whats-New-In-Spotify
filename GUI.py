import datetime
import json

# sg is the default PySimpleGUI naming convention for the import
# noinspection PyPep8Naming
import PySimpleGUI as sg
import spotipy
from spotipy.oauth2 import SpotifyOAuth

import IO_operations
import Playlist_operations
import URI_operations
from Artist_operations import get_new_albums, get_artists_songs_from_album
from IO_operations import get_date_from_latest_cont_file, find_latest_content_file
from Playlist_operations import get_new_songs_in_playlist


#########################################################################################
#                                                                                       #
#       Documentation of PySimpleGUI at https://pysimplegui.readthedocs.io              #
#       Github: https://github.com/PySimpleGUI/PySimpleGUI                              #
#                                                                                       #
#########################################################################################

# Notes:
#
#       PySimpleGUI enforces that each layout may only be used ONCE, so if a layout has been used in an element,
# it can not be used in another window or other element again. Fix: just assign the same values to new
# variables / layouts or use methods to generate the layouts

def set_settings(dic):
    """
    Overwrite settings in the setting.json file

    :param dic:
    :type dic: dict
    """
    with open("settings.json", "r") as file:
        data = json.load(file)

    for key in dic:
        data[key] = dic[key]

    with open("settings.json", "w") as file:
        json.dump(data, file)


def get_group_id_from_name(group_name):
    """
    Extract the id from the constructed group_name.

    Group names are constructed like this:
        ``[str(group.get_group_id()) + ": " + group.get_group_name() for group in groups]``

    :param group_name: the group's name format 'id: group_name' (there is a space after the ':')
    :type group_name: str
    """
    # group name is of format <id>: <group_name>    (there is a space after the ":")
    return int(group_name.split(":")[0])


def generate_group_content_layout(group_id):
    """
    Generate the layout for the playlist and artist part section

    :param group_id: id of the group whose content will be displayed
    :type group_id: int
    :return: the generated layout
    """
    playlist_tuples = groups[group_id].get_playlist_tuples()
    artist_tuples = groups[group_id].get_artist_tuples()
    playlist_names = [sg.Text(playlist_tuple[0]) for playlist_tuple in playlist_tuples]
    artist_names = [sg.Text(artist_tuple[0]) for artist_tuple in artist_tuples]

    playlist_names_and_uris = \
        [sg.Text(playlist_tuple[0] + "  ** URI: " + playlist_tuple[1]) for playlist_tuple in playlist_tuples]
    artist_names_and_uris = \
        [sg.Text(artist_tuple[0] + "  ** URI: " + artist_tuple[1]) for artist_tuple in artist_tuples]

    if uri_checkbox_value:
        playlist_layout = [[name] for name in playlist_names_and_uris]
        artist_layout = [[name] for name in artist_names_and_uris]
    else:
        playlist_layout = [[name] for name in playlist_names]
        artist_layout = [[name] for name in artist_names]

    if use_frames_in_layout:
        generated_group_content_layout = [
            [sg.Frame("Playlists", key="-PlaylistsFrame-", layout=[
                [sg.Column(scrollable=True, layout=playlist_layout, size=(350, 250))]], font="default 12 bold")],
            [sg.Frame("Artists", key="-ArtistsFrame-", layout=[
                [sg.Column(scrollable=True, layout=artist_layout, size=(350, 250))]], font="default 12 bold")],
        ]
    else:
        generated_group_content_layout = [
            [sg.Text("Playlists", font="Default 12 bold")],
            [sg.Column(scrollable=True, layout=playlist_layout, size=(350, 250))],
            [sg.Text("Artists", font="Default 12 bold")],
            [sg.Column(scrollable=True, layout=artist_layout, size=(350, 250))]
        ]

    return generated_group_content_layout


def generate_button_column_layout():
    """
    Generate the layout for the button column

    :return: the generated button layout
    """
    generated_buttons_layout = [
        [sg.Button("Run", size=(15, 1), key="-RunButton-")],
        [sg.Button("Add", size=(15, 1), key="-AddButton-")],
        [sg.Button("Remove", size=(15, 1), key="-RemoveButton-")],
        [sg.Button("Bonus Features", size=(15, 1), key="-BonusFeaturesButton-")]
    ]

    return generated_buttons_layout


def update_groups_data():
    """
    This method is mainly used to initially read and create the groups, and then whenever any group is altered
        - group added to the file
        - group deleted from the file
        - playlist / artist added to a group
        - playlist / artist removed from a group


    Read the groups from the file and include each group's ID in the string that's shown to the user
    """
    # make groups and group_names global to ensure consistency across all operations on groups
    global groups, group_names
    groups = IO_operations.read_groups_from_file()

    # include the group Id in the name, to have a bijective mapping from group_name to group id
    group_names = [str(group.get_group_id()) + ": " + group.get_group_name() for group in groups]


def update_main_window(curr_group_id=None):
    """
    Update the whole main window. This method is used when any group information that is shown in the
    group_content_layout column elements is altered:
        - a playlist / artist is added to the current group
        - a playlist / artist is removed from the current group


    PySimpleGui can NOT update the content of columns and frames without creating a new column / frame element that
    needs to be embedded in a new window.
    This method basically creates a new window and closes the old one. The PySimpleGUI creator said in an issue
    on github (can't remember the exact issue ID right now) that creating a new window was the best solution to this
    problem.

    :param curr_group_id: manually set current group id, otherwise it will be read from the main window's combo box
    :type curr_group_id: int
    """
    # to alter variables outside of the scope of this method the 'global' identifier must be used
    global current_group_id, group_content_layout, buttons_layout, window

    # update data
    update_groups_data()
    if curr_group_id is None:
        current_group_id = get_group_id_from_name(values["-ComboBox-"])
    else:
        current_group_id = curr_group_id

    # create new layouts
    group_content_layout = generate_group_content_layout(current_group_id)
    buttons_layout = generate_button_column_layout()

    # create new window
    old_window = window
    window = sg.Window("What\'s new in Spotify", generate_main_window_layout(), finalize=True)
    old_window.close()
    print("updated")


#########################################################################################
#                                                                                       #
#                              Open connection to Spotify                               #
#                                                                                       #
REDIRECT_URI = "https://www.duckduckgo.com"                                             #
# to add more just add them separated by a comma                                        #
scope = "playlist-modify-private"                                                       #
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,                             #
                                               redirect_uri=REDIRECT_URI))              #
#                                                                                       #
#########################################################################################


# read settings data from settings.json
with open("settings.json", "r") as settings_file:
    settings = json.load(settings_file)

# the state of some elements is saved by the values. They are global, are read by the generator methods and are
# overwritten in the event loop based on the user's input
# for example: whether a checkbox is ticked
# state values
uri_checkbox_value = False
use_frames_in_layout = settings["use_frames"]
current_group_id = settings["default_group"]

# read groups from the playlist_and_artist.txt file and add each group's id to its name to archive bijective mapping
# from group_name to group id
groups = []
group_names = []
update_groups_data()

# Define the window's contents
# the windows is divided into a grid. A layout is a list of list, representing columns and rows
group_content_layout = generate_group_content_layout(current_group_id)
buttons_layout = generate_button_column_layout()


def generate_main_window_layout():
    generated_main_window_layout = [
        [sg.Combo(values=group_names, default_value=group_names[current_group_id], font="default 16 bold",
                  readonly=True,
                  background_color=sg.theme_background_color(), text_color=sg.theme_text_color(), key="-ComboBox-",
                  enable_events=True, size=(31, 1)),
         sg.Button("Settings", size=(15, 1), key="-SettingsButton-")
         ],
        [sg.Button("New Group", size=(15, 1), key="-NewGroupButton-"),
         sg.Button("Remove Group", size=(15, 1), key="-RemoveGroupButton-")
         ],
        [sg.Text("Add new songs to: " + groups[current_group_id].get_target_playlist())],
        [sg.Text("", size=(10, 1))],  # blank line
        [sg.Checkbox("Show Spotify URIs", enable_events=True, key="-URICheckbox-", default=uri_checkbox_value)],
        [sg.Column(layout=group_content_layout), sg.Column(layout=buttons_layout, vertical_alignment="top")],
        [sg.Button("Quit", size=(15, 1))]]

    return generated_main_window_layout


main_window_layout = generate_main_window_layout()

# Create the window
window = sg.Window("What\'s new in Spotify", main_window_layout)

# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    # if the window was closed
    if event in (sg.WINDOW_CLOSED, "Quit"):
        break

    # when "Run" button is pressed, open an input window
    if event == "-RunButton-":
        window.disable()  # freeze the main window until the user has made their input

        # layout of the window that opens when the "Add" button is pressed
        layout_run_window = [
            [sg.Text("Run update on current group:", font="default 16 bold")],
            [sg.Text("Add newly added songs from playlists in this group and newly released songs by artists in this "
                     "group to the target playlist")],
            [sg.Checkbox("Safe playlist content to hard drive", key="-RunWindowSaveCheck-", default=True)],
            [sg.Checkbox("Add new songs to my playlist(s)", key="-RunWindowAddCheck-")],
            [sg.Checkbox("Remove / clear every songs from playlist before adding new songs",
                         key="-RunWindowClearCheck-")],
            [sg.Text("")],  # blank line
            [sg.Text("Show newly added songs since")],
            [sg.In(default_text=str(datetime.date.today() - datetime.timedelta(7)),
                   key="-RunWindowDateInput-",
                   size=(15, 1)),
             sg.CalendarButton("Select from calender", target="-RunWindowDateInput-", format="%Y-%m-%d")],
            [sg.Text("")],  # blank line
            [sg.Button("Run", key="-RunButtonRunWindow-", size=(15, 1)), sg.Button("Go Back", size=(15, 1))]
        ]
        window_run = sg.Window("What\'s new in Spotify", layout_run_window)

        event_run, values_run = window_run.read()
        while True:
            if event_run == "-RunButtonRunWindow-":
                new_songs_lists = []

                # get new songs from each playlist and artist and save them as lists in new_songs_lists
                for n, info_tuple in enumerate(groups[current_group_id].get_playlist_tuples() +
                                               groups[current_group_id].get_artist_tuples()):
                    new_songs = []
                    # tuples of format: (<name>, <uri>)
                    if URI_operations.is_playlist_uri(info_tuple[1]):
                        new_songs = get_new_songs_in_playlist(sp,
                                                              p_uri=info_tuple[1],
                                                              since_date=values_run["-RunWindowDateInput-"],
                                                              as_dict=True)

                    elif URI_operations.is_artist_uri(info_tuple[1]):
                        new_albums = get_new_albums(sp,
                                                    a_uri=info_tuple[1],
                                                    since_date=values_run["-RunWindowDateInput-"],
                                                    as_dict=True)
                        for n_album in new_albums:
                            new_songs += get_artists_songs_from_album(sp,
                                                                      alb_uri=n_album["uri"],
                                                                      art_uri=info_tuple[1])

                    # if the tuple somehow neither contains a p_uri nor a_uri, throw an error
                    else:
                        raise ValueError("The tuple " + repr(info_tuple) + " does not represent a playlist or "
                                                                           "an artist!")

                    # check if the user wants to create new content files
                    if values_run["-RunWindowSaveCheck-"]:
                        IO_operations.save_uri_content_to_hard_drive(sp, info_tuple[1])

                    # add all new songs to new_songs_lists as a list
                    new_songs_lists.append(new_songs)

                # Check the user's choices in the "Run" window
                # if the "clear playlist" checkbox is ticked, clear the entire playlist (before adding the new songs)
                if values_run["-RunWindowClearCheck-"]:
                    Playlist_operations.remove_all_songs_from_playlist(sp,
                                                                       groups[current_group_id].get_target_playlist())

                # if the "add songs to playlist" checkbox is ticked, save new songs in songs_to_add
                if values_run["-RunWindowAddCheck-"]:
                    # add all new songs at once => only a single request is sent to Spotify instead of one per playlist
                    # also remove duplicate songs because who needs to have the same song multiple times in a playlist
                    all_new_songs = []
                    for song_list in new_songs_lists:
                        for song_dic in song_list:
                            all_new_songs.append(song_dic["uri"])
                    no_duplicates = [s for n, s in enumerate(all_new_songs) if s not in all_new_songs[:n]]
                    Playlist_operations.add_songs_to_playlist(
                                                            sp,
                                                            playlist_uri=groups[current_group_id].get_target_playlist(),
                                                            song_uris=no_duplicates)

                # Give feedback to the user
                # show an individual window with new songs for each playlist and artist
                for n, info_tuple in enumerate(groups[current_group_id].get_playlist_tuples() +
                                               groups[current_group_id].get_artist_tuples()):

                    # list new songs in this layout and later add it to a column to assign a fixed size to it
                    presentation_window_songs = []
                    for song_data in new_songs_lists[n]:
                        # song_data["artists"] is a list of strings
                        # ", ".join(<list of str>) concat the list of strings into a single string separated by commas
                        # ", ".join(["ab", "c", "d"]) = 'ab, c, d'
                        presentation_window_songs.append(song_data["name"] + "  -  " + ", ".join(song_data["artists"]))
                    # finish the layout
                    presentation_window_songs_layout = [[sg.Text(song)] for song in presentation_window_songs]

                    # if there are no new songs, show "no new songs" in the presentation window
                    if not presentation_window_songs_layout:
                        if find_latest_content_file(info_tuple[1]) is not None:
                            date_str = get_date_from_latest_cont_file(info_tuple[1]).strftime("%A %Y-%m-%d")

                            presentation_window_songs_layout = [
                                [sg.Text("There are no new songs since " + values_run["-RunWindowDateInput-"])],
                                [sg.Text("")],
                                [sg.Text("The last saved changes (excluding today) are from:  " + date_str)]
                            ]

                        else:
                            presentation_window_songs_layout = [
                                [sg.Text("There are is no data for this playlist / artist yet!")]
                            ]

                    # if the "save playlist content" checkbox is ticked, tell the user that the content has been saved
                    # in the presentation window
                    if values_run["-RunWindowSaveCheck-"]:
                        presentation_window_songs_layout.insert(0, [sg.Text("Playlist content saved to hard drive!")])
                        presentation_window_songs_layout.insert(1, [sg.Text("")])  # blank line

                    # the layout for the windows that show new songs that have been added / released
                    layout_presentation_window = [
                        [sg.Text("New Songs " +
                                 ("in " if URI_operations.is_playlist_uri(info_tuple[1]) else "from ") + info_tuple[0],
                                 font="default 16 bold")],
                        [sg.Column(
                            layout=presentation_window_songs_layout, size=(1000, 500), scrollable=True)],
                        [sg.Button("Next")]
                    ]
                    window_presentation = sg.Window("What's new in Spotify", layout_presentation_window)
                    event_presentation, values_presentation = window_presentation.read()

                    # the quit_flag is set if the user presses the "X" button instead of "Next"
                    # the GUI will close all windows and return to the main menu
                    quit_flag = False
                    while True:
                        if event_presentation == "Next":
                            window_presentation.close()
                            break
                        if event_presentation == sg.WINDOW_CLOSED:
                            quit_flag = True
                            break

                    if quit_flag:
                        break

                break

            if event_run in (sg.WINDOW_CLOSED, "Go Back"):
                break

        window.enable()
        window_run.close()
        window.force_focus()

    # when "New Group" button is pressed, open an input window
    if event == "-NewGroupButton-":
        window.disable()  # freeze the main window until the user has correctly made their input or closed the window

        layout_new_group_window = [
            [sg.Text("Create a new Group:", font="default 16 bold")],
            [sg.Text("Group name: "), sg.In("", size=(20, 1), key="-NewGroupWindowGroupNameInput-")],
            [sg.Text("")],  # blank line
            [sg.Text("Enter the Spotify URI of the target playlist below. All songs from the playlists and artists you"
                     " want to observe, will be added to this playlist. \n"
                     "\n"
                     "In order to get the playlist's Spotify URI, go to Spotify, open the playlist and click the "
                     "three dots next to the 'Play' button.\n"
                     "A menu will open where you select 'Share' and click"
                     " 'Copy Spotify URI'. Paste the copied URI into the box below.")],
            [sg.Text("Target playlist:"), sg.In("", size=(40, 1), key="-NewGroupWindowTargetPlaylistInput-")],
            [sg.Text("")],  # blank line
            [sg.Button("Create Group", key="-CreateGroupButton-", size=(15, 1)), sg.Button("Go Back", size=(15, 1))]
        ]
        window_new_group = sg.Window("What\'s new in Spotify", layout_new_group_window)

        event_new_group, values_new_group = window_new_group.read()
        while True:
            if event_new_group in (sg.WINDOW_CLOSED, "Go Back"):
                break

            if event_new_group == "-CreateGroupButton-":
                # Check if the target playlist is a link instead of a uri. If it is a link try to convert it into a uri
                # If it's not a link, it can still be a regular uri and if that's also not the case, the other following
                # if statements will catch it and handle it accordingly
                if URI_operations.is_link(values_new_group["-NewGroupWindowTargetPlaylistInput-"]):
                    # transform the input into a uri
                    window_new_group["-NewGroupWindowTargetPlaylistInput-"].Update(
                        value=URI_operations.transform_link_to_uri(values_new_group[
                                                                       "-NewGroupWindowTargetPlaylistInput-"]))

                    # read the window values again to reset the button press event and by that prevent and infinite loop
                    event_new_group, values_new_group = window_new_group.read()

                # Check if the target playlist is a correct spotify playlist URI. Otherwise the created group will not
                # be recognised by the REs used to get the groups and their playlist and stuff from the file
                elif not URI_operations.is_playlist_uri(values_new_group["-NewGroupWindowTargetPlaylistInput-"]) \
                        and not values_new_group["-NewGroupWindowTargetPlaylistInput-"] == "":
                    sg.PopupError("Error: The URI you entered is not a playlist URI!\n"
                                  "A playlist URI always looks "
                                  "like this: \n\n"
                                  "spotify:playlist:<playlist_id> \n\n"
                                  "where <playlist_id> is the playlist's ID (without the '<' and '>').\n"
                                  "Ensure you don't have (white-)spaces at the beginning or end of the URI!\n\n"
                                  "Your input was:\n" +
                                  "\'" + values_new_group["-NewGroupWindowTargetPlaylistInput-"] + "\'")

                    # read the window values again to reset the button press event and by that prevent and infinite loop
                    event_new_group, values_new_group = window_new_group.read()

                # check if the user named the group. An empty name is not allowed as it will probably result in a bug
                elif values_new_group["-NewGroupWindowGroupNameInput-"] == "":
                    sg.PopupError("Error: You have not entered a value in the 'Group name' field!\n"
                                  "\n"
                                  "The field must NOT be emtpy, your group needs a name!")

                    # read the window values again to reset the button press event and by that prevent and infinite loop
                    event_new_group, values_new_group = window_new_group.read()

                # check if the user specified a target playlist. The script can't add new songs to it if
                # there is no target playlist
                elif values_new_group["-NewGroupWindowTargetPlaylistInput-"] == "":
                    sg.PopupError("Error: You have not entered a value in the 'Target Playlist' field!\n"
                                  "\n"
                                  "The field must NOT be emtpy!")

                    # read the window values again to reset the button press event and by that prevent and infinite loop
                    event_new_group, values_new_group = window_new_group.read()

                # the user had entered a valid spotify playlist URI -> save the new group to the file
                else:
                    new_group = IO_operations.Group(group_id=0,
                                                    group_name=values_new_group["-NewGroupWindowGroupNameInput-"],
                                                    target_playlist=values_new_group[
                                                        "-NewGroupWindowTargetPlaylistInput-"],
                                                    playlist_tuples=[],
                                                    artist_tuples=[])
                    IO_operations.save_group_to_file(new_group)

                    # update the groups and group_names lists to actually show the new group
                    update_groups_data()
                    window["-ComboBox-"].Update(values=group_names)

                    sg.PopupOK("New group successfully created !")
                    break

        window.enable()
        window_new_group.close()
        window.force_focus()

    # when "Remove Group" button is pressed, open an input window
    if event == "-RemoveGroupButton-":
        window.disable()  # freeze the main window until the user has made their input

        # layout of the window that opens when the "Remove Group" button is pressed
        # the column contains a listbox, where the user can select multiple entries which will then be deleted from the
        # playlist_and_artist.txt file
        rem_group_win_column1 = [
            [sg.Text("Groups")],
            [sg.Listbox(values=group_names, size=(50, 10),
                        select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                        background_color=sg.theme_background_color(),
                        text_color=sg.theme_text_color(),
                        key="-RemGroupWindowsListbox-")]
        ]

        layout_rem_group_window = [
            [sg.Text("Delete group from file", font="Default 16 bold")],
            [sg.Text("Select a group to delete", size=(30, 1))],
            [sg.Column(vertical_scroll_only=True, layout=rem_group_win_column1)],
            [sg.Button("Remove Selected", size=(15, 1)), sg.Button("Go Back", size=(15, 1))]
        ]

        window_remove_group = sg.Window("What\'s new in Spotify", layout_rem_group_window)

        event_rem_group, values_rem_group = window_remove_group.read()
        while True:
            if event_rem_group == sg.WINDOW_CLOSED or event_rem_group == "Go Back":
                break

            if event_rem_group == "Remove Selected":
                # singular, because the listbox mode is Single Select
                group_id_to_remove = window_remove_group["-RemGroupWindowsListbox-"].get_indexes()[0]

                # open popup asking for confirmation before deleting selected group
                rem_group_conf_popup = sg.popup_ok_cancel(
                    "Are you sure you want to remove the selected group? \n"
                    "\n"
                    "THIS CAN NOT BE UNDONE. \n"
                    "Better double check before deleting, otherwise you might have to add every"
                    "playlist and artist one by one to a new group again!!"
                    "\n \n"
                    "You Selected: \n"
                    "\n" +
                    groups[group_id_to_remove].get_group_name() +
                    "\n")

                # user has to confirm their choice
                if rem_group_conf_popup == "OK":
                    IO_operations.remove_group_from_file(groups[group_id_to_remove])
                else:
                    break

                # when updating the window via update_main_windows() the current_group_id is set by reading the
                # currently selected group in the main window's combo box. Manually set the current_group_id to 0
                # to prevent index out of bounds when the group that is currently selected in the combo box gets
                # removed.
                if current_group_id == group_id_to_remove:
                    update_main_window(curr_group_id=0)
                else:
                    update_main_window()

                break

        # close the input window and unfreeze the main window
        window.enable()
        window_remove_group.close()
        window.force_focus()

    # when "Add" button is pressed, open an input window
    if event == "-AddButton-":
        window.disable()  # freeze the main window until the user has made their input

        # layout of the window that open when the "Add" button is pressed
        layout_add_window = [
            [sg.Text("Add playlist or artist to the current group:", font="default 16 bold")],
            [sg.Text("Playlist / artist name: ", size=(20, 1)), sg.Input(size=(40, 1), key="-AddWindowName-")],
            [sg.Text("")],  # blank line
            [sg.Text("Enter the Spotify URI of the playlist or artist below. \n"
                     "\n"
                     "In order to get the playlist's Spotify URI, go to Spotify, open the playlist and click the "
                     "three dots next to the 'Play' button.\n"
                     "A menu will open where you select 'Share' and click"
                     " 'Copy Spotify URI'. Paste the copied URI into the box below.\n"
                     "\n"
                     "To get an artist's URI navigate to the artist's page, where their top songs and every release "
                     "is listed, and click the three dots \n"
                     "next to the artist's name there.")],
            [sg.Text("Spotify URI: ", size=(20, 1)), sg.Input(size=(40, 1), key="-AddWindowURI-")],
            [sg.Text("")],
            [sg.Button("Confirm", size=(15, 1)), sg.Button("Go Back", size=(15, 1))]
        ]

        window_add = sg.Window("What\'s new in Spotify", layout_add_window)

        event_add, values_add = window_add.read()
        while True:
            if event_add in (sg.WINDOW_CLOSED, "Go Back"):
                break

            if event_add == "Confirm":
                # Check if the input is a link instead of a uri. If it is a link try to convert it into a uri
                # If it's not a link, it can still be a regular uri and if that's also not the case, the other following
                # if statements will catch it and handle it accordingly
                if URI_operations.is_link(values_add["-AddWindowURI-"]):
                    # transform the input into a uri
                    window_add["-AddWindowURI-"].Update(
                        value=URI_operations.transform_link_to_uri(values_add["-AddWindowURI-"]))

                    # read the window values again to reset the button press event and by that prevent and infinite loop
                    event_add, values_add = window_add.read()

                # an error popup is shown if the user doesn't enter a name for the playlist / artist
                elif values_add["-AddWindowName-"] == "":
                    sg.PopupError("Error: You have not entered a value in the 'Playlist / artist name' field!\n"
                                  "\n"
                                  "The field must NOT be emtpy!")
                    # read the window values again to reset the button press event and by that prevent and infinite loop
                    event_add, values_add = window_add.read()

                # an error popup is shown if the user made no input to the 'Spotify URI' field
                elif values_add["-AddWindowURI-"] == "":
                    sg.PopupError("Error: You have not entered a value in the 'Spotify URI' field!\n"
                                  "\n"
                                  "The field must NOT be emtpy!")
                    # read the window values again to reset the button press event and by that prevent and infinite loop
                    event_add, values_add = window_add.read()

                # if the user entered a valid ARTIST uri, add the artist to the group
                elif URI_operations.is_artist_uri(values_add["-AddWindowURI-"]):
                    IO_operations.add_artist_to_group(
                        a_tuple=(values_add["-AddWindowName-"], values_add["-AddWindowURI-"]),
                        group=groups[current_group_id]
                    )
                    sg.Popup("Entry successfully added!")

                    # update the whole window to show the newly added playlist / artist
                    update_main_window()
                    break

                # if the user entered a valid PLAYLIST uri, add the playlist to the group
                elif URI_operations.is_playlist_uri(values_add["-AddWindowURI-"]):
                    IO_operations.add_playlist_to_group(
                        p_tuple=(values_add["-AddWindowName-"], values_add["-AddWindowURI-"]),
                        group=groups[current_group_id]
                    )
                    sg.Popup("Entry successfully added!")

                    # update the whole window to show the newly added playlist / artist
                    update_main_window()
                    break

                # the user made inputs but the entered string is not an artist or playlist uri
                else:
                    sg.PopupError("Error: The URI you entered is not a playlist URI!\n"
                                  "A playlist URI always looks "
                                  "like this: \n\n"
                                  "spotify:playlist:<playlist_id> \n\n"
                                  "where <playlist_id> is the playlist's ID (without the '<' and '>').\n"
                                  "Ensure you don't have (white-)spaces at the beginning or end of the URI!\n\n"
                                  "Your input was:\n" +
                                  values_add["-AddWindowURI-"])
                    # read the window values again to reset the button press event and by that prevent and infinite loop
                    event_add, values_add = window_add.read()

        # close the input window and unfreeze the main window
        window.enable()
        window_add.close()
        window.force_focus()

    # when "Remove" button is pressed, open an input window
    if event == "-RemoveButton-":
        window.disable()  # freeze the main window until the user has made their input

        # find the id of the currently selected group and read the group's meta data
        # the loop will always find the correct corresponding element
        rem_win_playlist_names_and_uris = []
        rem_win_artist_names_and_uris = []
        for i in range(len(group_names)):
            if groups[i].get_group_id() == get_group_id_from_name(values["-ComboBox-"]):
                rem_win_playlist_names_and_uris = groups[i].get_playlist_tuples()
                rem_win_artist_names_and_uris = groups[i].get_artist_tuples()
                break

        playlist_names_only = [playlist_tuple[0] for playlist_tuple in rem_win_playlist_names_and_uris]
        artist_names_only = [artist_tuple[0] for artist_tuple in rem_win_artist_names_and_uris]

        # layout of the window that opens when the "Remove" button is pressed
        # the columns contain listboxs, where the user can select multiple entries which will then be removed from the
        # release radar
        column1 = [
            [sg.Text("Playlists", font="Default 10 bold")],  # 10 APPEARS to be the default font size, I'm not sure tho
            [sg.Listbox(values=playlist_names_only, size=(50, 10),
                        select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                        background_color=sg.theme_background_color(),
                        text_color=sg.theme_text_color(),
                        key="-RemWindowPlaylistListbox-")]
        ]
        column2 = [
            [sg.Text("Artists", font="Default 10 bold")],  # 10 APPEARS to be the default font size, I'm not sure tho
            [sg.Listbox(values=artist_names_only, size=(50, 10),
                        select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                        background_color=sg.theme_background_color(),
                        text_color=sg.theme_text_color(),
                        key="-RemWindowArtistListbox-")]
        ]

        layout_remove_window = [
            [sg.Text("Remove from the current group", font="Default 16 bold")],
            [sg.Text("Select playlists and artist to be removed", size=(30, 1))],
            [sg.Column(vertical_scroll_only=True, layout=column1),
             sg.Column(vertical_scroll_only=True, layout=column2)],
            [sg.Button("Remove Selected", size=(15, 1)), sg.Button("Go Back", size=(15, 1))]
        ]

        window_remove = sg.Window("What\'s new in Spotify", layout_remove_window)

        event_remove, values_remove = window_remove.read()
        while True:
            if event_remove == sg.WINDOW_CLOSED or event_remove == "Go Back":
                break

            if event_remove == "Remove Selected":
                # get the indices of the selected entries
                p_indices_to_remove = window_remove["-RemWindowPlaylistListbox-"].get_indexes()
                a_indices_to_remove = window_remove["-RemWindowArtistListbox-"].get_indexes()

                # open a popup asking for confirmation before deleting selected playlists and artists
                rem_window_popup = sg.popup_ok_cancel(
                    "Are you sure you want to remove the selected playlists and "
                    "artists? THIS CAN NOT BE UNDONE \n"
                    "You Selected: \n"
                    "\n"
                    "PLAYLISTS: \n" +
                    " \n".join([tup[0] for tup in [rem_win_playlist_names_and_uris[i] for i in p_indices_to_remove]]) +
                    "\n \n" +
                    "ARTISTS: \n" +
                    " \n".join([tup[0] for tup in [rem_win_artist_names_and_uris[i] for i in a_indices_to_remove]]) +
                    "\n")

                # user has to confirm their choice
                if rem_window_popup == "OK":
                    for i in p_indices_to_remove:
                        IO_operations.remove_playlist_from_group(playlist_tuple=rem_win_playlist_names_and_uris[i],
                                                                 group=groups[current_group_id])
                        print("removed: " + rem_win_playlist_names_and_uris[i][0])

                    for i in a_indices_to_remove:
                        IO_operations.remove_artist_from_group(artist_tuple=rem_win_artist_names_and_uris[i],
                                                               group=groups[current_group_id])
                        print("removed: " + rem_win_artist_names_and_uris[i][0])

                update_main_window()
                break

        # close the input window and unfreeze the main window
        window.enable()
        window_remove.close()
        window.force_focus()

    # when "Bonus Features" button is pressed, open an input window
    if event == "-BonusFeaturesButton-":
        sg.popup("This feature is not yet implemented. It might come with future releases of this program. \n"
                 "\n"
                 "If you have suggestions for features you'd like to see submit them as an issue on this project's "
                 "github")

    # when "Settings" button is pressed, open an input window
    if event == "-SettingsButton-":
        window.disable()  # freeze the main window until the user has made their input

        layout_settings_window = [
            [sg.Text("Settings", font="Default 16 bold")],
            [sg.Checkbox("Show frames around group content in main window", default=use_frames_in_layout,
                         key="-SettingsFramesCheckbox-")],
            [sg.Text("")],  # blank line
            [sg.Text("Set default group. This will be the first group you see when opening this program.")],
            [sg.Text("Default group: "),
             sg.Combo(values=group_names, default_value=group_names[current_group_id], readonly=True,
                      background_color=sg.theme_background_color(), text_color=sg.theme_text_color(),
                      key="-SettingsComboBox-", size=(31, 1)),
             ],
            [sg.Text("")],  # blank line
            [sg.Button("Confirm", size=(15, 1), key="-SettingsConfirmButton-"),
             sg.Button("Go Back", size=(15, 1)),
             sg.Text("", size=(35, 1)),
             sg.Button("Danger Zone", size=(15, 1), button_color=("white", "#8f1000"), key="-SettingsDangerZone-")]
        ]

        window_settings = sg.Window("What\'s new in Spotify", layout_settings_window)

        event_settings, values_settings = window_settings.read()
        while True:
            if event_settings in (sg.WINDOW_CLOSED, "Go Back"):
                break

            # when the user pressed confirm, overwrite the settings.json file with the new settings
            if event_settings == "-SettingsConfirmButton-":
                setting_dic = {
                    "default_group": get_group_id_from_name(values_settings["-SettingsComboBox-"]),
                    "use_frames": values_settings["-SettingsFramesCheckbox-"]
                }

                # save changes to the settings.json file
                set_settings(setting_dic)

                # update the main window to show possible visual changes
                use_frames_in_layout = setting_dic["use_frames"]
                update_main_window()
                break

            # open a window with actions that you only use when uninstalling the the program
            if event_settings == "-SettingsDangerZone-":
                # show a warning to the user
                settings_danger_popup = sg.PopupOKCancel(
                    "WARNING: In the following window you can remove the connection to Spotify and "
                    "uninstall this program. You can also remove previously set path variables. \n"
                    "\n"
                    "These are NOT action you want to take when you intent to keep using this program. \n"
                    "\n"
                    "You can safely click 'OK', but be careful which button you press in the next window.")

                # user has to confirm in order to continue
                if settings_danger_popup == "OK":
                    window_settings.disable()  # freeze the main window until the user has made their input

                    layout_danger_zone = [
                        [sg.Text("Danger Zone", font="Default 16 bold")],
                        [sg.Text("These are NOT action you want to take when you intent to keep using this program.")],
                        [sg.Text("")],  # blank line
                        [sg.Text("This button uninstalls this program. You will have to confirm your \n"
                                 "action before that's happening. \n"
                                 "You do not need to run the other buttons below, when uninstalling, all \n"
                                 "these other actions are taken as well.")],
                        [sg.Button("Uninstall (not implemented)", size=(15, 1), button_color=("white", "#8f1000"))],
                        [sg.Text("")],  # blank line
                        [sg.Text("Remove Spotify Client ID and Client Secret from the path variable")],
                        [sg.Button("Unset path variables (not implemented)", size=(15, 1),
                                   button_color=("white", "#8f1000"))],
                        [sg.Text("")],  # blank line
                        [sg.Text("Cut connection to Spotify. You will have to manually do this over \n"
                                 "your browser. This button will refer you to the website where you \n"
                                 "can do that.")],
                        [sg.Button("Cut connection (not yet implemented)")],
                        [sg.Text("")],  # blank line
                        [sg.Text("")],  # blank line
                        [sg.Button("Close", size=(15, 1))]
                    ]
                    window_danger_zone = sg.Window("Danger Zone", layout_danger_zone)

                    event_danger_zone, values_danger_zone = window_danger_zone.read()
                    while True:
                        if event_danger_zone in ("Close", sg.WINDOW_CLOSED):
                            break
                        else:
                            # TODO: implement buttons
                            break

                    # close the input window and unfreeze the main window
                    window_settings.enable()
                    window_danger_zone.close()
                    window.force_focus()  # otherwise the main window can get lost behind a window from other apps
                    window_settings.force_focus()

                # read user input in order to prevent the confirmation pop-up from continuously appearing
                event_settings, values_settings = window_settings.read()

        # close the input window and unfreeze the main window
        window.enable()
        window_settings.close()
        window.force_focus()

    # when "Change Group" button is pressed, update the whole window.
    # actually only the group specific information has to be updated, but the whole window needs to be reloaded to show
    # these changes, as PySimpleGUI can't update the content of the playlist and artist columns / frame without
    # creating a new layout for them.
    if event == "-ComboBox-":
        update_main_window()

    # when the URI checkbox is clicked, update the whole window
    # (for the same reason as described above the "-ComboBox-" event)
    if event == "-URICheckbox-":
        uri_checkbox_value = values["-URICheckbox-"]
        update_main_window()

# Finish up by removing from the screen
window.close()
