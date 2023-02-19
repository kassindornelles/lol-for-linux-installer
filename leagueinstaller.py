#!/usr/bin/env python3

# WARNING
# DO NOT USE THIS SCRIPT YET
# IS BROKEN !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import os
import sys
import subprocess
import time
import gi
import dbus
import enum
import wget
import tarfile
import lzma
from pathlib import Path
import getpass
import locale

# Expose variables
user_locale = locale.getdefaultlocale()
print("Setting all variables") # Cheap logging
wine_lutris_build_url = "https://github.com/GloriousEggroll/wine-ge-custom/releases/download/7.0-GE-5-LoL/wine-lutris-ge-lol-7.0-5-x86_64.tar.xz"
tar_file_name = "wine-lutris-ge-lol-7.0-5-x86_64.tar.xz"
league_installer_url = "https://lol.secure.dyn.riotcdn.net/channels/public/x/installer/current/live.na.exe"
exe_file_name = "live.na.exe"
home_dir = os.path.expanduser("~")
game_main_dir = os.path.join(home_dir, 'leagueoflegends')
game_downloads_dir = os.path.join(game_main_dir, 'downloads')
game_winetricks_cache_dir = os.path.join(game_downloads_dir, "winetricks-cache")
game_main_wine_dir = os.path.join(game_main_dir, 'wine')
game_prefix_dir = os.path.join(game_main_wine_dir, 'prefix')
wine_lutris_build_file = os.path.join(game_downloads_dir, tar_file_name)
league_installer_file = os.path.join(game_downloads_dir, exe_file_name)
launch_file_path = os.path.join(game_main_dir, "Launch.py")
user_local_share = os.path.join(home_dir, ".local/share")
user_icons_folder = os.path.join(home_dir, user_local_share, "icons")
user_hicolor_folder = os.path.join(user_icons_folder, "hicolor")
user_applications_folder = os.path.join(home_dir, user_local_share, "applications")
folder_paths = [game_main_dir, game_downloads_dir, game_main_wine_dir, game_prefix_dir, game_winetricks_cache_dir, user_icons_folder, user_hicolor_folder, os.path.join(user_hicolor_folder, "16x16"), os.path.join(user_hicolor_folder, "32x32"), os.path.join(user_hicolor_folder, "48x48"), os.path.join(user_hicolor_folder, "64x64"), os.path.join(user_hicolor_folder, "128x128"), os.path.join(user_hicolor_folder, "256x256"), user_applications_folder]
desktop_file_path = os.path.join(os.path.expanduser("~"), ".local", "share", "applications", "LeagueLauncherPython.desktop")
game_launch_file_path = os.path.join(game_main_dir, "launch-league-of-legends.py")

# Set locale
locale.setlocale(locale.LC_ALL, user_locale)

# Create all folders that we are going to use
print("Creating folders for our League install") # Cheap logging
for folder_path in folder_paths:
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        os.chmod(folder_path, 0o700)

# Download necessary files
print("Downloading wine-lutris-lol build") # Cheap logging
subprocess.run(["wget", "-O", wine_lutris_build_file, wine_lutris_build_url], check=True)
print("Downloading League of Legends installer from Riot NA Servers") # Cheap logging

subprocess.run(["wget", "-O", league_installer_file, league_installer_url], check=True)
print("All files Downloaded") # Cheap logging

# Extract tar file
print("Extracting the wine-lutris-lol build file") # Cheap logging
with tarfile.open(os.path.join(game_downloads_dir, tar_file_name)) as file:
    file.extractall(os.path.join(game_main_wine_dir))
print("Extraction on the wine-lutris-lol build file completed") # Cheap logging

# Start the first-boot script to setup DXVK and the prefix
first_boot_envs = { **os.environ,
        "PATH": f"{game_main_wine_dir}/lutris-ge-lol-7.0-5-x86_64/bin:{os.environ['PATH']}",
        "WINEARCH": "win64",
        "WINEPREFIX": game_prefix_dir,
        "WINELOADER": f"{game_main_wine_dir}/lutris-ge-lol-7.0-5-x86_64/bin/wine",
        "WINEFSYNC": "1",
        "WINEDEBUG": "-all",
        "WINEDLLOVERRIDES": "winemenubuilder.exe=d",
        "WINETRICKS_CACHE": f"{game_winetricks_cache_dir}",
    }

subprocess.run(["wineboot", "-u"], env=first_boot_envs, check=True)
subprocess.run(["winetricks", "dxvk"], env=first_boot_envs, check=True)
wine_process = ["wine", league_installer_file]
subprocess.run(wine_process, env=first_boot_envs, check=True)

# Create launch-league-of-legends.py script
file_content = """import os
import sys
import subprocess

# Expose variables
home_dir = os.path.expanduser("~")
game_main_dir = os.path.join(home_dir, 'leagueoflegends')
game_main_wine_dir = os.path.join(game_main_dir, 'wine')
game_prefix_dir = os.path.join(game_main_wine_dir, 'prefix')
game_exe_path = os.path.join(game_prefix_dir, "drive_c", "Riot Games", "Riot Client")
game_exe_file_name = "RiotClientServices.exe"


start_game_vars = { **os.environ,
        "PATH": f"{game_main_wine_dir}/lutris-ge-lol-7.0-5-x86_64/bin:{os.environ['PATH']}",
        "WINEARCH": "win64",
        "WINEPREFIX": game_prefix_dir,
        "WINELOADER": f"{game_main_wine_dir}/lutris-ge-lol-7.0-5-x86_64/bin/wine",
        "WINEFSYNC": "1",
        "WINEDEBUG": "-all",
        "WINEDLLOVERRIDES": "winemenubuilder.exe=d",
    }

# Start the game
wine_process = ["wine", os.path.join(game_exe_path, game_exe_file_name), "--launch-product=league_of_legends", "--launch-patchline=live"]
subprocess.run(wine_process, env=start_game_vars, check=True)
"""

# Create the file and write the content
with open(game_launch_file_path, "w") as f:
    f.write(file_content)

# Create .desktop file
if os.path.exists(desktop_file_path):
    os.remove(desktop_file_path)

with open(desktop_file_path, "w") as file:
    # Write file contents
    file.write("[Desktop Entry]\n")
    file.write("Name=League of Legends (Python Launcher)\n")
    file.write("Comment=Play League of Legends on Linux\n")
    file.write(f"Exec=python {game_launch_file_path}\n")
    file.write("Terminal=false\n")
    file.write("Icon=leagueoflol.png\n")
    file.write("Type=Application\n")
    file.write("Categories=Game;\n")

os.chmod(desktop_file_path, 0o755)

# TODO:
# create icons for the desktop file
# messages/window UI (kdialog again?)
