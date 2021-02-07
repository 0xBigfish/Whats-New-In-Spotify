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

        add_window = sg.Window("What\'s new in Spotify", layout_add_window)

        event_add, values_add = add_window.read()
        while True:
            if event_add == sg.WINDOW_CLOSED or event_add == "Confirm":
                break

        # close the input window and unfreeze the main window
        window.enable()
        add_window.close()
        window.force_focus()

# Finish up by removing from the screen
window.close()
