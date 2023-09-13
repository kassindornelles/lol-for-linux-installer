#!/usr/bin/env python3
import os
import subprocess
import json

json_file_path = os.path.expanduser("~/.config/league_install_path.json")

with open(json_file_path, "r") as json_file:
    settings = json.load(json_file)
    game_installed_folder = settings["game_main_dir"]
    os.chdir(game_installed_folder)

game_main_dir = os.path.join(game_installed_folder)
game_main_wine_dir = os.path.join(game_main_dir, 'wine')
game_prefix_dir = os.path.join(game_main_wine_dir, 'prefix')
game_exe_path = os.path.join(game_prefix_dir, 'drive_c', 'Riot Games', 'Riot Client')
game_exe_file_name = 'RiotClientServices.exe'
wine_loader_path = os.path.join(game_main_wine_dir, 'wine-build', 'bin', 'wine')

env_vars_file_path = os.path.join(game_installed_folder, 'env_vars.json')

with open(env_vars_file_path, 'r') as env_vars_file:
    env_vars = json.load(env_vars_file)
    game_launcher_options = env_vars.get("game_launcher_options", {})

# Replace placeholders in game launcher options with actual values
game_launcher_options['PATH'] = os.path.join(game_main_wine_dir, 'wine-build', 'bin')
game_launcher_options['WINEPREFIX'] = game_prefix_dir
game_launcher_options['WINELOADER'] = wine_loader_path

start_game_vars = dict(os.environ, **game_launcher_options)

wine_process = [
    game_launcher_options['WINELOADER'],
    os.path.join(game_exe_path, game_exe_file_name),
    "--launch-product=league_of_legends",
    "--launch-patchline=live"
]

subprocess.run(wine_process, env=start_game_vars, check=True)


