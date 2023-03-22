#!/usr/bin/env python3
import os, json, shutil

if __name__ == '__main__':
    # Define the path to the directory where the JSON file is located
    home_dir = os.path.expanduser("~")
    user_local_share = os.path.join(home_dir, ".local/share")
    desktop_file_path = os.path.join(os.path.expanduser("~"), ".local", "share", "applications", "LeagueLauncherPython.desktop")
    user_config_folder= os.path.join(home_dir, ".config")
    json_file_path = os.path.join(user_config_folder, "league_install_path.json")

    try:
        # Read the JSON file and get the game_main_dir value
        with open(json_file_path, "r") as infile:
            data = json.load(infile)
            game_main_dir = data["game_main_dir"]
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Handle the exception by printing an error message
        print(f"Failed to read JSON file: {e}")

    # Remove the game directory
    try:
        shutil.rmtree(game_main_dir)
    except FileNotFoundError:
        print(f"Directory {game_main_dir} does not exist")

    try:
        os.remove(desktop_file_path)
    except FileNotFoundError:
        print(f"File {desktop_file_path} does not exist")

    try:
        os.remove(json_file_path)
    except FileNotFoundError:
        print(f"File {json_file_path} does not exist")
