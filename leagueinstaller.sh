#!/usr/bin/env bash

# Variables
[ ! -d "${XDG_DATA_HOME}" ] && XDG_DATA_HOME=~/.local/share     # Setup XDG stuff
leagueoflegends_dir="${XDG_DATA_HOME}/leagueoflegends"    # League of legends path
downloads_dir="$leagueoflegends_dir/Downloads"    # Download path
league_installer_url="https://lol.secure.dyn.riotcdn.net/channels/public/x/installer/current/live.na.exe"   # league client installer URL
wine_lutris_ge_lol_url="https://github.com/GloriousEggroll/wine-ge-custom/releases/download/7.0-GE-5-LoL/wine-lutris-ge-lol-7.0-5-x86_64.tar.xz"  # Wine build URL
wine_dir="$leagueoflegends_dir/wine"  # Wine main directory
league_installer_file="$downloads_dir/live.na.exe"  # Original LoL client name
league_installer_name="leagueinstaller.exe"  # LoL client name we will use
wine_lol_lutris_dir="$wine_dir/wine-lol-lutris"   # Wine build path name
leaguefirstboot="Firstboot.sh"    # First boot script name
leaguelauncherfile="Launch.sh"    # League of Legends launcher script name

# Function for logging messages to file
function log_message() {
  message="$1"
  timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[$timestamp] $message" | tee -a "$leagueoflegends_dir/leagueoflegends.log"
}

# Show a dialog with an Install and a Cancel button
kdialog --title "Install LOL?" --yesno "Do you want to install League of Legends? \n (Before proceeding make sure that you are not running this script as root)"

if [ $? -eq 0 ]; then

  dbusRef=`kdialog --title "Installing LoL" --progressbar "Initializing" 15`
  qdbus $dbusRef showCancelButton false


if [ ! -d "$leagueoflegends_dir" ]; then
  mkdir "$leagueoflegends_dir"
  log_message "Created directory $leagueoflegends_dir"
fi

# Create Downloads directory in leagueoflegends directory

if [ -d "$downloads_dir" ]; then
  rm -rf "$downloads_dir"
  log_message "Removed directory $downloads_dir"
fi
mkdir "$downloads_dir"
log_message "Created directory $downloads_dir"

qdbus $dbusRef Set "" value 1
qdbus $dbusRef setLabelText "Directory created"
sleep 1

# Download League installer file and the wine translation layer for League

qdbus $dbusRef setLabelText "Downloading wine-lol-lutris and the League of Legends installer"
log_message "Downloading wine-lol-lutris and the League of Legends installer"

wget -P "$downloads_dir" "$league_installer_url"
wget -P "$downloads_dir" "$wine_lutris_ge_lol_url"

log_message "Finished downloading files"
qdbus $dbusRef Set "" value 2
qdbus $dbusRef setLabelText "wine-lol-lutris and League of Legends installer downloaded"
sleep 1

# Extract wine translation layer file to wine directory

qdbus $dbusRef setLabelText "Extracting wine-lutris-lol package, please wait"


if [ -d "$wine_dir" ]; then
  rm -rf "$wine_dir"
  log_message "Removed directory $wine_dir"
fi
mkdir "$wine_dir"
log_message "Created directory $wine_dir"
tar -xf "$downloads_dir/wine-lutris-ge-lol-7.0-5-x86_64.tar.xz" -C "$wine_dir" --strip-components=1

qdbus $dbusRef Set "" value 3
qdbus $dbusRef setLabelText "Extracted wine-lutris-lol"


# Rename League installer file to leagueinstaller.exe
qdbus $dbusRef setLabelText "Renaming installer file"

mv "$league_installer_file" "$downloads_dir/$league_installer_name"
log_message "Renamed $league_installer_file to $league_installer_name"

# Rename wine directory subfolder to wine-lol-lutris
for subfolder in "$wine_dir"/*; do
  if [[ $subfolder == *"lutris-ge-lol-"* ]]; then
    mv "$subfolder" "$wine_lol_lutris_dir"
    log_message "Renamed $subfolder to $wine_lol_lutris_dir"
    break
  fi
done

qdbus $dbusRef Set "" value 4
qdbus $dbusRef setLabelText "Renamed lutris-lol folder"
sleep 1

# Create prefix directory inside wine directory
qdbus $dbusRef setLabelText "Creating WINE prefix folder"

prefix_dir="$wine_dir/prefix"
if [ ! -d "$prefix_dir" ]; then
  mkdir "$prefix_dir"
  log_message "Created directory $prefix_dir"
fi

qdbus $dbusRef Set "" value 5
qdbus $dbusRef setLabelText "WINE prefix folder created"
sleep 1

# Create and run first-boot script
log_message "Creating first-boot script"
qdbus $dbusRef setLabelText "Creating first-boot script"

cd "$leagueoflegends_dir"
touch $leaguefirstboot
echo '#!/usr/bin/env bash

# XDG stuff
[ ! -d "${XDG_DATA_HOME}" ] && XDG_DATA_HOME=~/.local/share

export PATH="${XDG_DATA_HOME}/leagueoflegends/wine/bin:$PATH"
export WINEPREFIX="${XDG_DATA_HOME}/leagueoflegends/wine/prefix"
export WINEDLLOVERRIDES=winemenubuilder.exe=d
export WINELOADER="${XDG_DATA_HOME}/leagueoflegends/wine/bin/wine"
export WINEFSYNC=1
export WINEDEBUG=-all
winetricks dxvk &
wait
wine "${XDG_DATA_HOME}/leagueoflegends/Downloads/leagueinstaller.exe"
wineserver -w &
wait
exit 0' > $leaguefirstboot
chmod +x $leaguefirstboot
wait

qdbus $dbusRef Set "" value 6
qdbus $dbusRef setLabelText "First-boot script created"
sleep 1

# Launching first-boot script
kdialog --title "League of Legends installer" --passivepopup \
"Manual action required in the LoL installer" 10
kdialog --msgbox "Launching the First-boot script now \n Manual action is required now: \n 1 - We will install DXVK automatically so be patient \n 2 - Once the installer opens please press the install button and wait \n 3 - Once it opens the login screen please close it so we can continue."
log_message "Launching the First-boot script now \n Manual action is required now: \n 1 - We will install DXVK automatically so be patient \n 2 - Once the installer opens please press the install button and wait \n 3 - Once it opens the login screen please close it so we can continue."
./Firstboot.sh &
wait
log_message "Finished first boot"


# Create Launch game .sh script
qdbus $dbusRef setLabelText "Creating Launch.sh script"
log_message "Creating Launch.sh script"

cd $leagueoflegends_dir
touch $leaguelauncherfile

echo '##!/usr/bin/env bash
# XDG stuff
[ ! -d "${XDG_DATA_HOME}" ] && XDG_DATA_HOME=~/.local/share
LEAGUEPATH="${XDG_DATA_HOME}/leagueoflegends/wine/prefix/drive_c/Riot Games/Riot Client"
export PATH="${XDG_DATA_HOME}/leagueoflegends/wine/bin:$PATH"
export WINEPREFIX="${XDG_DATA_HOME}/leagueoflegends/wine/prefix"
export WINELOADER="${XDG_DATA_HOME}/leagueoflegends/wine/bin/wine"
export WINEFSYNC=1
export WINEDEBUG=-all
export WINEDLLOVERRIDES=winemenubuilder.exe=d
cd "$LEAGUEPATH"
wine "RiotClientServices.exe" ---launch-product=league_of_legends --launch-patchline=live' > $leaguelauncherfile

chmod +x $leaguelauncherfile

log_message "Launch.sh file created in $leagueoflegends_dir"
qdbus $dbusRef Set "" value 7
qdbus $dbusRef setLabelText "Launch.sh file created"
sleep 1

# Create system menu shortcut
qdbus $dbusRef setLabelText "Creating system menu shortcut for the Launch.sh script"
log_message "Creating system menu shortcut for the Launch.sh script"

cd ~/.local/share/applications
touch "LeagueofLegendsLauncher.desktop"
chmod +x "LeagueofLegendsLauncher.desktop"

echo '[Desktop Entry]
Name=League of Legends
Comment=Play League of Legends on Linux
Exec=/home/$USER/.local/share/leagueoflegends/Launch.sh
Terminal=false
Icon=leagueoflol.png
Type=Application
Categories=Game;' > LeagueofLegendsLauncher.desktop

log_message "System menu shortcut created"
qdbus $dbusRef Set "" value 8
qdbus $dbusRef setLabelText "System menu shortcut created"
sleep 1

# Move the .png file to the icons path
qdbus $dbusRef setLabelText "Installing system icons"

# Download the image files to the league of legends data directory
wget -P "$leagueoflegends_dir" https://github.com/kassindornelles/lol-for-linux-bash-installer/raw/main/icons/league16.png
wget -P "$leagueoflegends_dir" https://github.com/kassindornelles/lol-for-linux-bash-installer/raw/main/icons/league32.png
wget -P "$leagueoflegends_dir" https://github.com/kassindornelles/lol-for-linux-bash-installer/raw/main/icons/league48.png
wget -P "$leagueoflegends_dir" https://github.com/kassindornelles/lol-for-linux-bash-installer/raw/main/icons/league64.png
wget -P "$leagueoflegends_dir" https://github.com/kassindornelles/lol-for-linux-bash-installer/raw/main/icons/league128.png
wget -P "$leagueoflegends_dir" https://github.com/kassindornelles/lol-for-linux-bash-installer/raw/main/icons/league256.png

# Move the image files to the appropriate folders
for size in 16 32 48 64 128 256; do
    if [ -d "${XDG_DATA_HOME}/icons/hicolor/${size}x${size}/apps/" ]; then
        cp "$leagueoflegends_dir/league${size}.png" "${XDG_DATA_HOME}/icons/hicolor/${size}x${size}/apps/leagueoflol.png"
    fi
done

rm "$leagueoflegends_dir/league"*.png  # Delete downloaded icons since they all got installed

log_message "System icons installed"
qdbus $dbusRef Set "" value 10
qdbus $dbusRef setLabelText "System icons are installed"
sleep 1
qdbus $dbusRef close

# Launch the Launch.sh script

# Show a dialog with an Install and a Cancel button
kdialog --title "Installation finished" --yesno "Do you want to launch LoL now?"

# Check the exit status of the dialog
if [ $? -eq 0 ]; then
  # If Install was clicked, create the lol folder in the user's home directory
  cd "$leagueoflegends_dir"
  ./Launch.sh
  log_message "All finished! have fun :)"
else
  # If Cancel was clicked, exit the script
  exit 0
fi

else
  # If Cancel was clicked, exit the script
  exit 0
fi


