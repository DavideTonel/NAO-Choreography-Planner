#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import time
import vlc

def play_song(song_name):
    """
    Tries to play an audio file using VLC.
    """
    try:
        player = vlc.MediaPlayer(song_name)
        player.play()
        return player   # <-- important: return the player so caller can keep it alive
    except Exception as e:
        print(f"[WARN] Could not play '{song_name}': {e}")
        return None


def do_moves(moves, robot_ip, robot_port):
    """
    Executes a list of NAO robot movements.
    
    Each movement corresponds to a Python2 script located in ./NaoMoves/,
    named <move>.py.
    
    For every move:
    - builds the Python2 command
    - measures execution time
    - prints how long the move took to run
    """
    for move in moves:
        print(f"Executing: {move}... ", end="", flush=True)
        python2_command = f"python2 ./NaoMoves/{move}.py {robot_ip} {robot_port}"
        start_move = time.time()
        # subprocess.run executes the command and returns stdout
        process = subprocess.run(python2_command.split(), stdout=subprocess.PIPE)
        end_move = time.time()
        # print(process.stdout)  # Uncomment to see the output of the Python2 script
        print("done in %.2f seconds." % (end_move - start_move), flush=True)


def from_state_to_dict(state):
    """
    Converts a state (list of tuples) into a dictionary {key: value}.
    
    Each element in 'state' is a tuple:
        (key, value)            -> maps to key: value
        (key, v1, v2, ...)      -> maps to key: (v1, v2, ...)
    
    The function:
    - ignores tuples that are too short
    - assigns either a single value or a group of values
    - does not overwrite existing keys in the dictionary
    """
    params_dict = dict()

    for t in state:
        len_t = len(t)
        if len_t < 2:
            continue  # Invalid tuple, skip it

        key = t[0]

        # If the tuple contains more than 2 elements, store all remaining values
        if len_t > 2:
            value = t[1:]
        else:
            value = t[1]

        # Only add the key if it is not already present
        if key not in params_dict:
            params_dict[key] = value

    return params_dict
