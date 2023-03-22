#!/usr/bin/env python3
import os, shutil, requests, tarfile, subprocess, json


def league_install_code(game_main_dir):

    # Expose variables
    print("Setting all variables")  # Cheap logging
    home_dir = os.path.expanduser("~")
    game_downloads_dir = os.path.join(game_main_dir, 'downloads')
    game_winetricks_cache_dir = os.path.join(game_downloads_dir, "winetricks-cache")
    game_main_wine_dir = os.path.join(game_main_dir, 'wine')
    game_prefix_dir = os.path.join(game_main_wine_dir, 'prefix')
    user_local_share = os.path.join(home_dir, ".local/share")

    user_icons_folder = os.path.join(home_dir, user_local_share, "icons")
    user_hicolor_folder = os.path.join(user_icons_folder, "hicolor")
    user_applications_folder = os.path.join(home_dir, user_local_share, "applications")
    desktop_file_path = os.path.join(os.path.expanduser("~"), ".local", "share", "applications",
                                     "LeagueLauncherPython.desktop")
    game_launch_file_path = os.path.join(game_main_dir, "launch-league-of-legends.py")
    user_config_folder= os.path.join(home_dir, ".config")

    # Create all folders that we are going to use
    folder_paths = [game_main_dir, game_downloads_dir, game_main_wine_dir, game_prefix_dir, user_config_folder, game_winetricks_cache_dir,
                    user_icons_folder, user_hicolor_folder, os.path.join(user_hicolor_folder, "16x16"),
                    os.path.join(user_hicolor_folder, "32x32"), os.path.join(user_hicolor_folder, "48x48"),
                    os.path.join(user_hicolor_folder, "64x64"), os.path.join(user_hicolor_folder, "128x128"),
                    os.path.join(user_hicolor_folder, "256x256"), user_applications_folder]
    print("Creating folders for our League install")  # Cheap logging
    for folder_path in folder_paths:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            os.chmod(folder_path, 0o700)

    # Download necessary files
    print("Downloading wine-lutris-lol build")  # Cheap logging
    wine_lutris_build_url = "https://github.com/GloriousEggroll/wine-ge-custom/releases/download/7.0-GE-5-LoL/wine-lutris-ge-lol-7.0-5-x86_64.tar.xz"
    tar_file_name = "wine-lutris-ge-lol-7.0-5-x86_64.tar.xz"
    wine_lutris_build_file = os.path.join(game_downloads_dir, tar_file_name)
    response = requests.get(wine_lutris_build_url)
    with open(wine_lutris_build_file, "wb") as f:
        f.write(response.content)

    print("Downloading League of Legends installer from Riot NA Servers")  # Cheap logging
    exe_file_name = "live.na.exe"
    league_installer_url = "https://lol.secure.dyn.riotcdn.net/channels/public/x/installer/current/live.na.exe"
    league_installer_file = os.path.join(game_downloads_dir, exe_file_name)
    response = requests.get(league_installer_url)
    with open(league_installer_file, "wb") as f:
        f.write(response.content)

    print("All files Downloaded")  # Cheap logging

    # Extract tar file
    print("Extracting the wine-lutris-lol build file")  # Cheap logging
    with tarfile.open(os.path.join(game_downloads_dir, tar_file_name)) as file:
        file.extractall(os.path.join(game_main_wine_dir))
    print("Extraction on the wine-lutris-lol build file completed")  # Cheap logging

    # Start the first-boot script to setup DXVK and the prefix
    first_boot_envs = {**os.environ,
                       "PATH": f"{game_main_wine_dir}/lutris-ge-lol-7.0-5-x86_64/bin:{os.environ['PATH']}",
                       "WINEARCH": "win64",
                       "WINEPREFIX": game_prefix_dir,
                       "WINELOADER": f"{game_main_wine_dir}/lutris-ge-lol-7.0-5-x86_64/bin/wine",
                       "WINEFSYNC": "1",
                       "WINEDEBUG": "-all",
                       "WINEDLLOVERRIDES": "winemenubuilder.exe=d",
                       "WINETRICKS_CACHE": f"{game_winetricks_cache_dir}",
                       }

    subprocess.run(["winetricks", "dxvk"], env=first_boot_envs, check=True)
    wine_process = ["wine", league_installer_file]
    subprocess.run(wine_process, env=first_boot_envs, check=True)

    # create py script
    with open(game_launch_file_path, "w") as file:
        file.write("import os\nimport subprocess\n")
        file.write(f"home_dir = os.path.expanduser('{home_dir}')\n")
        file.write(f"game_main_dir = os.path.join('{game_main_dir}')\n")
        file.write(f"game_main_wine_dir = os.path.join(game_main_dir, 'wine')\n")
        file.write(f"game_prefix_dir = os.path.join(game_main_wine_dir, 'prefix')\n")
        file.write(f"game_exe_path = os.path.join(game_prefix_dir, 'drive_c', 'Riot Games', 'Riot Client')\n")
        file.write(f"game_exe_file_name = 'RiotClientServices.exe'\n")
        file.write('start_game_vars = dict(os.environ,\n')
        file.write(f"        PATH='{game_main_wine_dir}/lutris-ge-lol-7.0-5-x86_64/bin',\n")
        file.write('        WINEARCH="win64",\n')
        file.write('        WINEPREFIX=game_prefix_dir,\n')
        file.write(f'        WINELOADER="{game_main_wine_dir}/lutris-ge-lol-7.0-5-x86_64/bin/wine",\n')
        file.write('        WINEFSYNC="1",\n')
        file.write('        WINEDEBUG="-all",\n')
        file.write('        WINEDLLOVERRIDES="winemenubuilder.exe=d",\n')
        file.write('    )\n')
        file.write(
            'wine_process = ["wine", os.path.join(game_exe_path, game_exe_file_name), "--launch-product=league_of_legends", "--launch-patchline=live"]\n')
        file.write('subprocess.run(wine_process, env=start_game_vars, check=True)\n')

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
        file.write("Icon=leagueoflol\n")
        file.write("Type=Application\n")
        file.write("Categories=Game;\n")

    os.chmod(desktop_file_path, 0o755)

    # create icons for the desktop file
    github_icons_url = "https://github.com/kassindornelles/lol-for-linux-bash-installer/raw/main/icons/league{}.png"
    sizes = ["16", "32", "48", "64", "128", "256"]
    github_icons_download_path = os.path.join(game_downloads_dir, "league-icons")

    if not os.path.exists(github_icons_download_path):
        os.makedirs(github_icons_download_path)

    for size in sizes:
        url = github_icons_url.format(size)
        filename = "league{}.png".format(size)
        dest_folder = os.path.join(user_hicolor_folder, size + "x" + size, "apps")
        dest_path = os.path.join(dest_folder, "leagueoflol.png")

        # Download the file
        response = requests.get(url)
        with open(os.path.join(github_icons_download_path, filename), "wb") as f:
            f.write(response.content)

        # Move the file to the correct subfolder
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        shutil.move(os.path.join(github_icons_download_path, filename), dest_path)

    print("Icons created")

    # create json file
    # Create a dictionary to hold the data
    data = {
        "game_main_dir": game_main_dir
    }

    # Create the directory if it doesn't exist
    os.makedirs(user_config_folder, exist_ok=True)

    # Write the dictionary to a JSON file in the user_config_folder directory
    with open(os.path.join(user_config_folder, "league_install_path.json"), "w") as outfile:
        json.dump(data, outfile)

    print("json file created")

    # Delete downloads folder
    try:
        shutil.rmtree(game_downloads_dir)
    except FileNotFoundError:
        print(f"Directory {game_downloads_dir} does not exist")
    print("Downloads folder deletion")

    # Copy uninstaller
    shutil.copy("uninstall.py", os.path.join(game_main_dir, "uninstall.py"))
    os.chmod(os.path.join(game_main_dir), "uninstall.py", 0o777)
    print("Created uninstall.py file in game dir")
