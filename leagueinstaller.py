#!/usr/bin/env python3

# WARNING
# DO NOT USE THIS SCRIPT YET
# IS BROKEN !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import os
import sys
import subprocess
import time
import wget
import tarfile
import lzma
from pathlib import Path

# Variables
print("Setting all variables") # Cheap logging
wine_lutris_build_url = "https://github.com/GloriousEggroll/wine-ge-custom/releases/download/7.0-GE-5-LoL/wine-lutris-ge-lol-7.0-5-x86_64.tar.xz"
tar_file_name = "wine-lutris-ge-lol-7.0-5-x86_64.tar.xz"
league_installer_url="https://lol.secure.dyn.riotcdn.net/channels/public/x/installer/current/live.na.exe"
exe_file_name = "live.na.exe"
home_dir = os.path.expanduser("~")
game_main_dir = os.path.join(home_dir, 'leagueoflegends')
game_downloads_dir = os.path.join(game_main_dir, 'downloads')
game_winetricks_cache_dir = os.path.join(game_downloads_dir, "winetricks-cache")
game_main_wine_dir = os.path.join(game_main_dir, 'wine')
game_prefix_dir = os.path.join(game_main_wine_dir, 'prefix')
folder_paths = [game_main_dir, game_downloads_dir, game_main_wine_dir, game_prefix_dir, game_winetricks_cache_dir]
wine_lutris_build_file = os.path.join(game_downloads_dir, tar_file_name)
league_installer_file = os.path.join(game_downloads_dir, exe_file_name)

# Create all folders that we are going to use
print("Creating folders for our League install") # Cheap logging
for folder_path in folder_paths:
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        os.chmod(folder_path, 0o777)

# Download necessary files
print("Downloading wine-lutris-lol build") # Cheap logging
subprocess.run(["wget", "-O", wine_lutris_build_file, wine_lutris_build_url], check=True)
print("Downloading League of Legends installer from Riot NA Servers") # Cheap logging

subprocess.run(["wget", "-O", league_installer_file, league_installer_url], check=True)
print("All files Downloaded") # Cheap logging

# Extract tar file
print("Extracting the wine-lutris-lol build file") # Cheap logging
file = tarfile.open(os.path.join(game_downloads_dir, tar_file_name))
file.extractall(os.path.join(game_main_wine_dir))
file.close()
print("Extraction on the wine-lutris-lol build file completed") # Cheap logging

# Start the first-boot script to setup DXVK and the prefix

# Set the environment variables you want to apply
first_boot_envs = {
        "PATH": f"{game_main_wine_dir}/lutris-ge-lol-7.0-5-x86_64/bin:{os.environ['PATH']}",
        "WINEARCH": "win64",
        "WINEPREFIX": game_prefix_dir,
        "WINELOADER": f"{game_main_wine_dir}/lutris-ge-lol-7.0-5-x86_64/bin",
        "WINEFSYNC": "1",
        "WINEDEBUG": "-all",
        "WINEDLLOVERRIDES": "winemenubuilder.exe=d",
        "WINETRICKS_CACHE": f"{game_winetricks_cache_dir}",
        "XDG_CACHE_HOME": f"{os.environ['HOME']}/.cache",
    }

# Start the software and pass the environment variables
subprocess.run(["wineboot", "-u"], env=first_boot_envs, check=True)
subprocess.run(["winetricks", "dxvk"], env=first_boot_envs, check=True)

# TODO
# fix winetricks not properly writing to the cache folder
# create a launch script for the .desktop file
# make a .desktop file
# create icons for the desktop file
# kdialog messages/window
