import PySimpleGUI as sg

import IO_operations

#########################################################################################
#                                                                                       #
#       Documentation of PySimpleGUI at https://pysimplegui.readthedocs.io              #
#       Github: https://github.com/PySimpleGUI/PySimpleGUI                              #
#                                                                                       #
#########################################################################################


playlist_names = [sg.Text(playlist_tuple[0]) for playlist_tuple in IO_operations.read_playlists_uris_from_file()]
artist_names = [sg.Text(artist_tuple[0]) for artist_tuple in IO_operations.read_artists_uris_from_file()]

playlist_layout = [[name] for name in playlist_names]
artist_layout = [[name] for name in artist_names]

# Define the window's contents
# the windows is divided into a grid. "layout" is a list of list, representing columns and rows
main_window_layout = \
    [[sg.Text("Release Radar"), sg.Text("", size=(10, 1)), sg.Button("Run", size=(10, 1), key="-RunButton-"),
      sg.Button("New Group", size=(10, 1), key="-NewGroupButton-")],

     [sg.Text("Playlist"), sg.Text("", size=(15, 1)), sg.Button("Add", size=(10, 1), key="-AddButton-"),
      sg.Button("Remove", size=(10, 1), key="-RemoveButton-")],

     [sg.Column(vertical_scroll_only=True, layout=playlist_layout)],
     [sg.Text("Artists")],
     [sg.Column(vertical_scroll_only=True, layout=artist_layout)],
     [sg.Text("", size=(10, 1))],  # blank line
     [sg.Input(key='-INPUT-')],
     [sg.Text(size=(40, 1), key='-OUTPUT-')],
     [sg.Button('Ok'), sg.Button('Quit')]]


# Create the window
window = sg.Window("What\'s new in Spotify", main_window_layout)

second_window_open = False

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

    # when "Add" button is pressed, open an input window
    if event == "-RemoveButton-":
        window.disable()  # freeze the main window until the user has made their input

        # both playlist and artist layouts have already been used in the main window. PySimpleGUI enforces that each
        # layout may only be used ONCE. Just assign the same values to new variables / layouts here.
        # Also they need a different format as their values will be fed into the Listbox
        playlist_name_and_uris = IO_operations.read_playlists_uris_from_file()
        playlist_names_only = [playlist_tuple[0] for playlist_tuple in playlist_name_and_uris]

        artist_name_and_uris = IO_operations.read_artists_uris_from_file()
        artist_names_only = [sg.Text(artist_tuple[0]) for artist_tuple in artist_name_and_uris]

        # layout of the window that opens when the "Remove" button is pressed
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

# Finish up by removing from the screen
window.close()
