# lol-for-linux-installer
League of Legends unofficial installer for linux

This software is not affiliated with nor supported by Riot Games.

![Screenshot_20230326_042247](https://user-images.githubusercontent.com/40970965/227761459-316840e1-591b-485b-837d-676b6195be64.png)

## How to install it (Python version - Recommended)
- Download the latest release from the [Releases page](https://github.com/kassindornelles/lol-for-linux-bash-installer/releases)
- The file should be named `lol-installer-for-linux-release.tar.gz`
- Extract the files
- Run the `ui_installer.py` script in a terminal/console:

  Open a console/terminal in the script main directory (where the files are)

  Type `python 'Install League of Legends (Python).py'` and press enter.

- Alternatively you can go to the `Install League of Legends (Python).py` file properties, set it as executable, and then double-click to open it

### Python Script features:
- You can choose where to install the game
- It installs wine-ge-lol with FSYNC/FUTEX2 support enabled by default
- Installs the latest DXVK version to translate DirectX 9 and 11 to Vulkan for ultra performance!
- It creates a desktop file in the system menu (with icons for the game)
- Creates an uninstaller in case you want to nuke the game, after you rage quit a match that your teammates did everything they could to make you lose

## How to install it (Bash version - Simpler and safer version)
- Download the latest release from the [Releases page](https://github.com/kassindornelles/lol-for-linux-bash-installer/releases)
- Extract the files
- Run the `Install League of Legends (Bash).sh` script in a terminal/console:

   Open a console/terminal in the script main directory (where the files are)

   Type and run ```chmod +x ./'Install League of Legends (Bash).sh'``` first

   Type and run `./'Install League of Legends (Bash).sh'` to install the game


## Dependencies (install those packages system-wide first):
- `winetricks`
- `wget` (Bash script)
- `kdialog` (Bash script)
- `tar`
- `python` and `python-requests` (Python script)
- `qt5-base` and `pyqt5` (Python script)
- WINE 32-64 bits and its [Dependency hell](https://www.gloriouseggroll.tv/how-to-get-out-of-wine-dependency-hell/)

## Remaining tasks:
- Flatpak it

## Can i uninstall the game?
- You can with the Python script, as it will generate an `uninstall.py` file in the directory you installed the game.

- The bash script does not have a uninstaller script, but you can remove it manually by deleting the leagueoflegends desktop file from `/.local/share/applications` and deleting the game folder.

## Buy me a coffee
[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate/?hosted_button_id=9D3JQM8NAYS98)
