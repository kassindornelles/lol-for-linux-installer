#!/usr/bin/env python3
import os, shutil, requests, tarfile, subprocess, json, logging
from PyQt5.QtCore import pyqtSignal, QObject

def league_install_code(game_main_dir, game_region_link, shortcut_bool):

    # Expose variables
    logging.info("Setting all variables")  # Cheap logging
    wine_version = "wine-build"
    home_dir = os.environ.get('XDG_CONFIG_HOME') or os.path.expanduser('~/')
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
    ui_dir = os.path.join(game_main_dir, "python_src", "ui")
    wine_loader_path = os.path.join(game_main_wine_dir, 'wine-build', 'bin', 'wine')

    # Create all folders that we are going to use
    folder_paths = [game_main_dir, game_downloads_dir, game_main_wine_dir, game_prefix_dir, user_config_folder, game_winetricks_cache_dir,
                    user_icons_folder, user_hicolor_folder, os.path.join(user_hicolor_folder, "16x16"),
                    os.path.join(user_hicolor_folder, "32x32"), os.path.join(user_hicolor_folder, "48x48"),
                    os.path.join(user_hicolor_folder, "64x64"), os.path.join(user_hicolor_folder, "128x128"),
                    os.path.join(user_hicolor_folder, "256x256"), user_applications_folder, ui_dir]
    logging.info("Creating folders for our League install")  # Cheap logging
    for folder_path in folder_paths:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            os.chmod(folder_path, 0o700)

    # Download necessary files
    logging.info("Downloading wine-lutris-lol build")  # Cheap logging
    wine_lutris_build_url = "https://github.com/GloriousEggroll/wine-ge-custom/releases/download/8.7-GE-1-LoL/wine-lutris-ge-lol-8.7-1-x86_64.tar.xz"
    tar_file_name = wine_version + ".tar.xz"
    wine_lutris_build_file = os.path.join(game_downloads_dir, tar_file_name)
    response = requests.get(wine_lutris_build_url)
    with open(wine_lutris_build_file, "wb") as f:
        f.write(response.content)

    logging.info("Downloading League of Legends installer from " + game_region_link)  # Cheap logging
    exe_file_name = "lolinstaller.exe"
    league_installer_file = os.path.join(game_downloads_dir, exe_file_name)
    response = requests.get(game_region_link)
    with open(league_installer_file, "wb") as f:
        f.write(response.content)

    logging.info("All files Downloaded")  # Cheap logging

    # Extract tar file
    logging.info("Extracting the wine-lutris-lol build file")
    with tarfile.open(os.path.join(game_downloads_dir, tar_file_name)) as file:
        file.extractall(path=game_main_wine_dir)
        extracted_folder_name = file.getnames()[0]
    os.rename(os.path.join(game_main_wine_dir, extracted_folder_name), os.path.join(game_main_wine_dir, "wine-build"))
    logging.info("Extraction of the wine-lutris-lol build file completed")

    with open('env_vars.json', 'r') as f:
        env_vars = json.load(f)

    env_vars['PATH'] = os.path.join(game_main_wine_dir, 'wine-build', 'bin', ":{os.environ['PATH']}")
    env_vars['WINEPREFIX'] = game_prefix_dir
    env_vars['WINELOADER'] = wine_loader_path

    first_boot_envs = dict(os.environ, **env_vars)
    subprocess.run(["wine", league_installer_file], env=first_boot_envs, check=True)

    # create py script
    try:
        shutil.copy("python_src/src/launch-script.py", os.path.join(game_main_dir, "launch-script.py"))
    # Fallback for appimage
    except:
        shutil.copy("/usr/share/lol-for-linux-installer/python_src/src/launch-script.py", os.path.join(game_main_dir, "launch-script.py"))

    # Create .desktop file
    # if shortcut_bool:
    #     try:
    #         if os.path.exists(desktop_file_path):
    #             os.remove(desktop_file_path)
    #
    #         with open(desktop_file_path, "w") as file:
    #             # Write file contents
    #             file.write("[Desktop Entry]\n")
    #             file.write("Name=League of Legends (Python Launcher)\n")
    #             file.write("Comment=Play League of Legends on Linux\n")
    #             file.write(f'Exec=python3 launch-league-of-legends.py\n')
    #             file.write(f'Path={game_main_dir}\n')
    #             file.write("Terminal=false\n")
    #             file.write("Icon=leagueoflol\n")
    #             file.write("Terminal=false\n")
    #             file.write("Type=Application\n")
    #             file.write("Categories=Game;\n")
    #
    #         os.chmod(desktop_file_path, 0o755)
    #
    #         # create icons for the desktop file
    #         github_icons_url = "https://github.com/kassindornelles/lol-for-linux-bash-installer/raw/main/icons/league{}.png"
    #         sizes = ["16", "32", "48", "64", "128", "256"]
    #         github_icons_download_path = os.path.join(game_downloads_dir, "league-icons")
    #
    #         if not os.path.exists(github_icons_download_path):
    #             os.makedirs(github_icons_download_path)
    #
    #         for size in sizes:
    #             url = github_icons_url.format(size)
    #             filename = "league{}.png".format(size)
    #             dest_folder = os.path.join(user_hicolor_folder, size + "x" + size, "apps")
    #             dest_path = os.path.join(dest_folder, "leagueoflol.png")
    #
    #             # Download the file
    #             response = requests.get(url)
    #             with open(os.path.join(github_icons_download_path, filename), "wb") as f:
    #                 f.write(response.content)
    #
    #             # Move the file to the correct subfolder
    #             if not os.path.exists(dest_folder):
    #                 os.makedirs(dest_folder)
    #             shutil.move(os.path.join(github_icons_download_path, filename), dest_path)
    #
    #         logging.info("Icons created")
    #     except:
    #         logging.warning("Couldn't create desktop files/download icons")
    # else:
    #     logging.info("Skipping desktop icons")

    # Create a dictionary to hold the install dir data
    data_folder = {
        "game_main_dir": game_main_dir
    }

    # Create the directory if it doesn't exist
    os.makedirs(user_config_folder, exist_ok=True)

    # Write the dictionary to a JSON file in the user_config_folder directory
    with open(os.path.join(user_config_folder, "league_install_path.json"), "w") as outfile:
        json.dump(data_folder, outfile)

    logging.info("json file created")

    # Wine build version json
    lol_build_current = {
        "current_build_name": wine_lutris_build_url
    }

    with open(os.path.join(game_main_dir, "buildversion.json"), "w") as outfile:
        json.dump(lol_build_current, outfile)

    logging.info("LoL installed build json file created")

    # Delete downloads folder
    try:
        shutil.rmtree(game_downloads_dir)
    except FileNotFoundError:
        logging.warning(f"Directory {game_downloads_dir} does not exist")
    logging.info("Downloads folder deletion")

    # Copy launcher
    try:
        shutil.copy("launch-league-of-legends.py", os.path.join(game_main_dir, "launch-league-of-legends.py"))
        shutil.copy("python_src/ui/installer.ui", os.path.join(game_main_dir, "python_src", "ui", "installer.ui"))
        shutil.copy("python_src/ui/lolbanner.jpeg", os.path.join(game_main_dir, "python_src", "ui", "lolbanner.jpeg"))
        shutil.copy("leagueinstaller_code.py", os.path.join(game_main_dir, "leagueinstaller_code.py"))
    # Fallback for PKGBUILD/AppImage
    except:
        shutil.copy("/usr/share/bin/lol-for-linux-installer", os.path.join(game_main_dir, "launch-league-of-legends.py"))
    os.chmod(os.path.join(game_main_dir, "launch-league-of-legends.py"), 0o777)
    logging.info("Copied launcher")
