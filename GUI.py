# sg is the default PySimpleGUI naming convention for the import
# noinspection PyPep8Naming
import PySimpleGUI as sg

import IO_operations


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
# variables / layouts


def get_group_id_from_name(group_name):
    """
    Extract the id from the constructed group_name.


    Group names are constructed like this:
        ``[str(group.get_group_id()) + ": " + group.get_group_name() for group in groups]``
    """
    # group name is of format <id>: <group_name>
    return group_name.split(":")[0]


groups = IO_operations.read_groups_from_file()
initial_group_id = 0

playlist_tuples = groups[initial_group_id].get_playlist_tuples()
artist_tuples = groups[initial_group_id].get_artist_tuples()

playlist_names = [sg.Text(playlist_tuple[0]) for playlist_tuple in playlist_tuples]
playlist_names_and_uris = [sg.Text(playlist_tuple) for playlist_tuple in playlist_tuples]
artist_names = [sg.Text(artist_tuple[0]) for artist_tuple in artist_tuples]
artist_names_and_uris = [sg.Text(artist_tuple) for artist_tuple in artist_tuples]

playlist_layout = [[name] for name in playlist_names]
artist_layout = [[name] for name in artist_names]

# include the group Id in the name, to have a bijective mapping from group_name to group id
group_names = [str(group.get_group_id()) + ": " + group.get_group_name() for group in groups]

# Define the window's contents
# the windows is divided into a grid. "layout" is a list of list, representing columns and rows
# currently there are two layout themes:
release_radar_layout_frames = [
    [sg.Frame("Playlists", layout=[
#        [sg.Listbox(values=playlist_layout, size=(50, 10), select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED)]], font="default 12 bold")],
        [sg.Column(scrollable=True, layout=playlist_layout, size=(350, 250))]], font="default 12 bold")],
    [sg.Frame("Artists", layout=[
        [sg.Column(scrollable=True, layout=artist_layout, size=(350, 250))]], font="default 12 bold")],
]
# if this is not commented an error is thrown: "YOU ARE ATTEMPTING TO REUSE AN ELEMENT IN YOUR LAYOUT!"
# release_radar_layout_no_frames = [
#    [sg.Text("Playlist")],
#    [sg.Column(scrollable=True, layout=playlist_layout, size=(250, 250))],
#    [sg.Text("Artists")],
#    [sg.Column(scrollable=True, layout=artist_layout, size=(250, 250))]
# ]


buttons_layout = [
    [sg.Button("Run", size=(15, 1), key="-RunButton-")],
    [sg.Button("New Group", size=(15, 1), key="-NewGroupButton-")],
    [sg.Button("Add", size=(15, 1), key="-AddButton-")],
    [sg.Button("Remove", size=(15, 1), key="-RemoveButton-")],
    [sg.Button("Bonus Features", size=(15, 1), key="-BonusFeaturesButton-")]
]


main_window_layout = \
    [[sg.Combo(values=group_names, default_value=group_names[initial_group_id], font="default 16 bold", readonly=True,
               background_color=sg.theme_background_color(), text_color=sg.theme_text_color(), key="-ComboBox-"),
      sg.Button("Settings", size=(15, 1))],
     [sg.Checkbox("Show Spotify URIs")],
     [sg.Text("", size=(10, 1))],  # blank line
     [sg.Column(layout=release_radar_layout_frames), sg.Column(layout=buttons_layout, vertical_alignment="top")],
     [sg.Button('Ok'), sg.Button('Quit')]]


# Create the window
window = sg.Window("What\'s new in Spotify", main_window_layout)


# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == sg.WINDOW_CLOSED or event == 'Quit':
        break

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

    # when "Change Group" button is pressed, open

# Finish up by removing from the screen
window.close()
