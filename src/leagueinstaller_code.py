#!/usr/bin/env python3
import os, shutil, requests, tarfile, subprocess, json, logging, urllib.request

def install_dxvk_code(game_main_dir):
    dst_path = os.path.join(game_main_dir, 'wine', 'prefix', 'drive_c', 'windows')
    tmp_path = 'dxvk-tmp'
    url = 'https://github.com/doitsujin/dxvk/releases/download/v1.10.3/dxvk-1.10.3.tar.gz'
    filename = os.path.basename(url)
    urllib.request.urlretrieve(url, filename)

    with tarfile.open(filename, 'r:gz') as tar:
        tar.extractall(tmp_path)

    for arch in ['x64', 'x32']:
        src_path = os.path.join(tmp_path, 'dxvk-1.10.3', arch)
        dst_path_arch = os.path.join(dst_path, 'system32' if arch == 'x64' else 'syswow64')

        if not os.path.exists(dst_path_arch):
            os.makedirs(dst_path_arch)

        for file_name in os.listdir(src_path):
            if file_name.endswith('.dll'):
                src_file = os.path.join(src_path, file_name)
                dst_file = os.path.join(dst_path_arch, file_name)
                shutil.copy2(src_file, dst_file)

    os.remove(filename)
    shutil.rmtree(tmp_path)

def league_install_code(game_main_dir, game_region_link):
    logging.info("Setting all variables")  # Cheap logging
    wine_version = "wine-build"
    home_dir = os.environ.get('XDG_CONFIG_HOME') or os.path.expanduser('~/')
    game_downloads_dir = os.path.join(game_main_dir, 'downloads')
    game_main_wine_dir = os.path.join(game_main_dir, 'wine')
    game_prefix_dir = os.path.join(game_main_wine_dir, 'prefix')
    user_local_share = os.path.join(home_dir, ".local/share")
    game_launch_file_path = os.path.join(game_main_dir, "launch-league-of-legends.py")
    user_config_folder= os.path.join(home_dir, ".config")
    wine_loader_path = os.path.join(game_main_wine_dir, 'wine-build', 'bin', 'wine')
    folder_paths = [game_main_dir, game_downloads_dir, game_main_wine_dir, game_prefix_dir, user_config_folder]
    logging.info("Creating folders")  # Cheap logging
    for folder_path in folder_paths:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            os.chmod(folder_path, 0o700)

    logging.info("Downloading WINE build")  # Cheap logging
    wine_lutris_build_url = "https://github.com/kassindornelles/lol-for-linux-installer-wine-builds/releases/download/8.7-4/wine-lutris-ge-lol-8.7-4-x86_64.tar.xz"
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

    logging.info("Extracting the WINE build file")
    with tarfile.open(os.path.join(game_downloads_dir, tar_file_name)) as file:
        file.extractall(path=game_main_wine_dir)
        extracted_folder_name = file.getnames()[0]
    os.rename(os.path.join(game_main_wine_dir, extracted_folder_name), os.path.join(game_main_wine_dir, "wine-build"))
    logging.info("Extraction of the WINE build file completed")

    with open('env_vars.json', 'r') as env_vars_file:
        env_vars = json.load(env_vars_file)
        game_launcher_options = env_vars.get("game_launcher_options", {})

    game_launcher_options['PATH'] = os.path.join(game_main_wine_dir, 'wine-build', 'bin')
    game_launcher_options['WINEPREFIX'] = game_prefix_dir
    game_launcher_options['WINELOADER'] = wine_loader_path

    first_boot_envs = dict(os.environ, **game_launcher_options)
    subprocess.run(["wine", league_installer_file], env=first_boot_envs, check=True)

    data_folder = {
        "game_main_dir": game_main_dir
    }

    with open(os.path.join(user_config_folder, "league_install_path.json"), "w") as outfile:
        json.dump(data_folder, outfile)

    logging.info("json file created")

    os.makedirs(user_config_folder, exist_ok=True)

    lol_build_current = {
        "current_build_name": wine_lutris_build_url
    }

    with open(os.path.join(game_main_dir, "buildversion.json"), "w") as outfile:
        json.dump(lol_build_current, outfile)

    logging.info("LoL build json file created")

    try:
        shutil.rmtree(game_downloads_dir)
    except FileNotFoundError:
        logging.warning(f"Directory {game_downloads_dir} does not exist")
    logging.info("Delete temp folders")

    logging.info("Installing DXVK 1.10.3...")
    install_dxvk_code(game_main_dir)
    logging.info("Finishing...")
