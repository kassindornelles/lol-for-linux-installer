#!/usr/bin/env python3
import os, subprocess, json


json_file_path = os.path.expanduser("~/.config/league_install_path.json")

with open(json_file_path, "r") as json_file:
    data = json.load(json_file)
    game_installed_folder = data["game_main_dir"]
    os.chdir(game_installed_folder)

game_main_dir = os.path.join(game_installed_folder)
game_main_wine_dir = os.path.join(game_main_dir, 'wine')
game_prefix_dir = os.path.join(game_main_wine_dir, 'prefix')
game_exe_path = os.path.join(game_prefix_dir, 'drive_c', 'Riot Games', 'Riot Client')
game_exe_file_name = 'RiotClientServices.exe'
wine_loader_path = os.path.join(game_main_wine_dir, 'wine-build', 'bin', 'wine')

with open('env_vars.json', 'r') as f:
    env_vars = json.load(f)

# Replace placeholders with actual values
env_vars['PATH'] = os.path.join(game_main_wine_dir, 'wine-build', 'bin')
env_vars['WINEPREFIX'] = game_prefix_dir
env_vars['WINELOADER'] = wine_loader_path

start_game_vars = dict(os.environ, **env_vars)

wine_process = ["wine", os.path.join(game_exe_path, game_exe_file_name), "--launch-product=league_of_legends", "--launch-patchline=live"]
subprocess.run(wine_process, env=start_game_vars, check=True)

