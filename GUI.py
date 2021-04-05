# sg is the default PySimpleGUI naming convention for the import
# noinspection PyPep8Naming
import datetime

import PySimpleGUI as sg
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import IO_operations
from IO_operations import get_date_from_latest_con_file
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


def get_group_id_from_name(group_name):
    """
    Extract the id from the constructed group_name.

    Group names are constructed like this:
        ``[str(group.get_group_id()) + ": " + group.get_group_name() for group in groups]``
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
            [sg.Text("Playlist")],
            [sg.Column(scrollable=True, layout=playlist_layout, size=(250, 250))],
            [sg.Text("Artists")],
            [sg.Column(scrollable=True, layout=artist_layout, size=(250, 250))]
        ]

    return generated_group_content_layout


def generate_button_column_layout():
    """
    Generate the layout for the button column

    :return: the generated button layout
    """
    generated_buttons_layout = [
        [sg.Button("Run", size=(15, 1), key="-RunButton-")],
        [sg.Button("New Group", size=(15, 1), key="-NewGroupButton-")],
        [sg.Button("Add", size=(15, 1), key="-AddButton-")],
        [sg.Button("Remove", size=(15, 1), key="-RemoveButton-")],
        [sg.Button("Bonus Features", size=(15, 1), key="-BonusFeaturesButton-")]
    ]

    return generated_buttons_layout


#########################################################################################
#                                                                                       #
#                              Open connection to Spotify                               #
#                                                                                       #
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())                           #
#                                                                                       #
#########################################################################################


# the state of some elements is saved by the values. They are global, are read by the generator methods and are
# overwritten in the event loop based on the user's input
# for example: whether a checkbox is ticked
# state values
uri_checkbox_value = False
use_frames_in_layout = True
current_group_id = 0

groups = IO_operations.read_groups_from_file()

# include the group Id in the name, to have a bijective mapping from group_name to group id
group_names = [str(group.get_group_id()) + ": " + group.get_group_name() for group in groups]

# Define the window's contents
# the windows is divided into a grid. A layout is a list of list, representing columns and rows
group_content_layout = generate_group_content_layout(current_group_id)
buttons_layout = generate_button_column_layout()


def generate_main_window_layout():
    generated_main_window_layout = [
        [sg.Combo(values=group_names, default_value=group_names[current_group_id], font="default 16 bold",
                  readonly=True,
                  background_color=sg.theme_background_color(), text_color=sg.theme_text_color(), key="-ComboBox-",
                  enable_events=True),
         sg.Button("Settings", size=(15, 1))],
        [sg.Checkbox("Show Spotify URIs", enable_events=True, key="-URICheckbox-", default=uri_checkbox_value)],
        [sg.Text("", size=(10, 1))],  # blank line
        [sg.Column(layout=group_content_layout), sg.Column(layout=buttons_layout, vertical_alignment="top")],
        [sg.Button('Ok'), sg.Button('Quit')]]

    return generated_main_window_layout


main_window_layout = generate_main_window_layout()

# Create the window
window = sg.Window("What\'s new in Spotify", main_window_layout)

# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == sg.WINDOW_CLOSED or event == 'Quit':
        break

    # when "Run" button is pressed, open an input window
    if event == "-RunButton-":
        window.disable()  # freeze the main window until the user has made their input

        # layout of the window that opens when the "Add" button is pressed
        layout_run_window = [
            [sg.Checkbox("Safe playlist content to hard drive")],
            [sg.Checkbox("Add new songs to my playlist(s)")],
            [sg.Text("Show newly added songs since")],
            [sg.In(default_text=str(datetime.date.today()), key="-RunWindowDateInput-", size=(15, 1)),
             sg.CalendarButton("Select from calender", target="-RunWindowDateInput-", format="%Y-%m-%d")],
            [sg.Text("")],  # blank line
            [sg.Button("Run", key="-RunButtonRunWindow-", size=(15, 1))]
        ]
        window_run = sg.Window("What\'s new in Spotify", layout_run_window)

        event_run, values_run = window_run.read()
        while True:
            if event_run == "-RunButtonRunWindow-":
                # show an individual window with new songs for each playlist
                for p_tuple in groups[current_group_id].get_playlist_tuples():

                    # list new songs in this layout and later add it to a column to assign a fixed size to it
                    # TODO: show song name and artist instead of URI
                    presentation_window_songs_layout \
                        = [[sg.Text(song)] for song in get_new_songs_in_playlist(sp,
                                                                                 p_tuple[1],
                                                                                 values_run["-RunWindowDateInput-"])]
                    # if there are no new songs, show "no new songs" in the presentation window
                    if not presentation_window_songs_layout:
                        date_str = get_date_from_latest_con_file(p_tuple[1]).strftime("%A %Y-%m-%d")

                        presentation_window_songs_layout = [
                            [sg.Text("There are no new songs since " + values_run["-RunWindowDateInput-"])],
                            [sg.Text("")],
                            [sg.Text("The last saved changes are from:  " + date_str)]
                        ]

                    # the layout for the windows that show new songs that have been added / released
                    layout_presentation_window = [
                        [sg.Text("New Songs in " + p_tuple[0], font="default 16 bold")],
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

            if event_run == sg.WINDOW_CLOSED:
                break

        window.enable()
        window_run.close()
        window.force_focus()

    # when "Add" button is pressed, open an input window
    if event == "-AddButton-":
        window.disable()  # freeze the main window until the user has made their input

        # layout of the window that open when the "Add" button is pressed
        layout_add_window = [
            [sg.Text("Playlist / Artist name", size=(40, 1)), sg.Text("Spotify URI", size=(40, 1))],
            [sg.Input(size=(40, 1), key="-AddWindowName-"), sg.Input(size=(40, 1), key="-AddWindowURI-")],
            [sg.Button("Confirm", size=(10, 1))]]

        window_add = sg.Window("What\'s new in Spotify", layout_add_window)

        event_add, values_add = window_add.read()
        while True:
            if event_add == sg.WINDOW_CLOSED or event_add == "Confirm":
                break

        # close the input window and unfreeze the main window
        window.enable()
        window_add.close()
        window.force_focus()

    # when "Remove" button is pressed, open an input window
    if event == "-RemoveButton-":
        window.disable()  # freeze the main window until the user has made their input

        # find the id of the currently selected group and read the group's meta data
        # the loop will always find the correct corresponding element
        for i in range(len(group_names)):
            if groups[i].get_group_id() == get_group_id_from_name(values["-ComboBox-"]):
                rem_win_playlist_names_and_uris = groups[i].get_playlist_tuples()
                rem_win_artist_names_and_uris = groups[i].get_artist_tuples()
                break

        # TODO: the value is unassigned, there probably is an error in the get_group_id_from_name method
        playlist_names_only = [playlist_tuple[0] for playlist_tuple in rem_win_playlist_names_and_uris]

        artist_names_only = [artist_tuple[0] for artist_tuple in rem_win_artist_names_and_uris]

        # layout of the window that opens when the "Remove" button is pressed
        # the columns contain listboxs, where the user can select multiple entries which will then be removed from the
        # release radar
        column1 = [
            [sg.Text("Playlists")],
            [sg.Listbox(values=playlist_names_only, size=(50, 10),
                        select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE)]
        ]
        column2 = [
            [sg.Text("Artists")],
            [sg.Listbox(values=artist_names_only, size=(50, 10),
                        select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE)]
        ]

        layout_remove_window = [
            [sg.Text("Select playlists and artist to be removed", size=(30, 1))],
            [sg.Checkbox("Show Spotify URI", key="-UriCheckbox-", size=(30, 2))],
            [sg.Column(vertical_scroll_only=True, layout=column1),
             sg.Column(vertical_scroll_only=True, layout=column2)],
            [sg.Button("Remove Selected", size=(30, 2)), sg.Button("Go Back", size=(30, 2))]
        ]

        window_remove = sg.Window("What\'s new in Spotify", layout_remove_window)

        event_remove, values_remove = window_remove.read()
        while True:
            if event_remove == sg.WINDOW_CLOSED or event_remove == "Go Back":
                break

        # close the input window and unfreeze the main window
        window.enable()
        window_remove.close()
        window.force_focus()

    # when "Change Group" button is pressed, update the whole window.
    # actually only the group specific information has to be updated, but the whole needs to be reloaded to show
    # these changes, as PySimpleGUI can't update the content of the playlist and artist columns / frame without
    # creating a new layout for them.
    if event == "-ComboBox-":
        current_group_id = get_group_id_from_name(values["-ComboBox-"])
        group_content_layout = generate_group_content_layout(current_group_id)
        buttons_layout = generate_button_column_layout()
        window = sg.Window("What\'s new in Spotify", generate_main_window_layout())
        print("updated")

    # when the URI checkbox is clicked, update the whole window
    # (for the same reason as described above the "-ComboBox-" event)
    if event == "-URICheckbox-":
        uri_checkbox_value = values["-URICheckbox-"]
        group_content_layout = generate_group_content_layout(current_group_id)
        buttons_layout = generate_button_column_layout()
        window = sg.Window("What\'s new in Spotify", generate_main_window_layout())
        print("updated")

# Finish up by removing from the screen
window.close()
