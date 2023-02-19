#!/usr/bin/env python3
import os
import sys
import subprocess

home_dir = os.path.expanduser("~")
game_main_dir = os.path.join(home_dir, 'leagueoflegends')

# Step 1: Check if leagueoflegends directory and Launch.sh script exist
if os.path.isdir(f"{game_main_dir}") and os.path.isfile(f"{game_main_dir}/launch-league-of-legends.py"):
    # Step 2: Start the Launch.sh script
    print("League of legends was detected, running the game...")
    os.chdir(f"{game_main_dir}")
    os.chmod("launch-league-of-legends.py", 0o777)
    os.system("python launch-league-of-legends.py")
else:
    # Step 3: Launch leagueinstaller.py from current directory
    print("League of legends install not detected, installing the game...")
    os.chmod("leagueinstaller.py", 0o777)
    os.system("python leagueinstaller.py")
