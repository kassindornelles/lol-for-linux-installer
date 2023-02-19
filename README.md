# lol-for-linux-bash-installer
A bash (.sh) script that installs league of legends automagically! 

## How to use this script:
- Download the latest release from the [Releases page](https://github.com/kassindornelles/lol-for-linux-bash-installer/releases)
- Extract the files
- Run the `leagueinstaller.sh` file (`./leagueinstaller.sh` in a terminal or just double click and follow the instructions, might be necessary to run chmod +x ./leagueinstaller.sh first.)
- DON'T RUN THIS SCRIPT AS SUDO

## Dependencies, install those packages system-wide first:
- winetricks
- xdg-user-dirs
- wget
- wine (both 32-bit and 64-bit support)
- tar
- kdialog 
- And the rest of the dependency hell that comes with [WINE](https://www.gloriouseggroll.tv/how-to-get-out-of-wine-dependency-hell/)

## My goals
- Finish up the bash script and make it as perfect and safe as possible
- Maybe move to QTCreator and Python (or C++)
- Make a nice GUI installer (We use Kdialog now so we kinda have... a nice GUI installer?)
- Polish it as much as possible
- Flatpak it for easy use by new Linux users
