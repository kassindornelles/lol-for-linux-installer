#!/usr/bin/env python3
import os

# XDG stuff
XDG_DATA_HOME = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))

# Step 1: Check if leagueoflegends directory and Launch.sh script exist
if os.path.isdir(f"{XDG_DATA_HOME}/leagueoflegends") and os.path.isfile(f"{XDG_DATA_HOME}/leagueoflegends/Launch.sh"):
    # Step 2: Start the Launch.sh script
    print("League of legends was detected, running the game...")
    os.chdir(f"{XDG_DATA_HOME}/leagueoflegends")
    os.chmod("./Launch.sh", 0o755)
    os.system("./Launch.sh")
else:
    # Step 3: Launch leagueinstaller.sh from current directory
    print("League of legends install not detected, installing the game...")
    os.chmod("./leagueinstaller.sh", 0o755)
    os.system("./leagueinstaller.sh")
