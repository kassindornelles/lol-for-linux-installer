# lol-for-linux-installer

League of Legends unofficial installer/manager for linux

<b>This software is not affiliated with nor supported by Riot Games.</b>

<noscript><a href="https://liberapay.com/kassindornelles/donate"><img alt="Donate using Liberapay" src="https://liberapay.com/assets/widgets/donate.svg"></a></noscript> <a href="https://www.paypal.com/donate/?hosted_button_id=UMJWYGDH2RC7E"><img src="https://github.com/andreostrovsky/donate-with-paypal/blob/master/grey.svg" alt="Donate with PayPal" width="150" height="40"></a>

### Features:
- Choose where to install the game (as long as the directory is writable by current user)
- wine-ge-lol with ESYNC/FSYNC/FUTEX2 support enabled by default for better CPU performance
- Desktop file in the system menu
- Options for the use of dGPU/APU/SecondaryGPU
- obs-gamecapture support
- vkBasalt CAS (Sharpening filter) support with a slider for sharpness strength
- You can change between the Wine builds supported
- DXVK version management
- Feral Gamemode support
- Discord Rich Presence support (Thanks to @JocarLixo and @daglaroglou)

### GPU's and Drivers suppported:
Check for it in the [DXVK Driver support wiki page](https://github.com/doitsujin/dxvk/wiki/Driver-support)


## <a name="dependencies"></a> Dependencies:

### Necessary Dependencies:

`python` `python-psutil` `python-pyqt5` `python-cffi` `wine` `python-requests` `qt5-base` `tar` `lib32-gnutls` `gnutls` `lib32-libldap` `libldap` `libpng` `lib32-libpng` `mesa` `lib32-mesa` `libgphoto2` `libpulse` `lib32-libpulse` `python-pip`

### Optional dependencies:

- `vkbasalt`: Enables additional visual enhancements, 
- `gamemode`: Improves game performance', 
- `mangohud`: Provides an overlay with game performance metrics')

 ** Different distributions have different names for packages
   
- WINE and its [Dependency hell](https://www.gloriouseggroll.tv/how-to-get-out-of-wine-dependency-hell/)


## Easy installation
- Packages are made for Fedora, Ubuntu 22.04 LTS and Arch Linux, they are available in the [release page](https://github.com/kassindornelles/lol-for-linux-installer/releases)

- If you want to build the packages yourself check the [Packaging repository](https://github.com/kassindornelles/lol-for-linux-installer-packages)



## Interface and options:
![Screenshot_20231230_161625](https://github.com/kassindornelles/lol-for-linux-installer/assets/40970965/7d437423-7515-4c20-9208-4d9c44f7e92d)
![Screenshot_20231230_162211](https://github.com/kassindornelles/lol-for-linux-installer/assets/40970965/35668c6e-6c00-4457-a84d-bbe2447e5346)
![Screenshot_20231025_052345](https://github.com/kassindornelles/lol-for-linux-installer/assets/40970965/a79f7992-442a-41ed-8e22-a8bca3e736a5)

## FAQ:

- This project <b>DOES NOT manage League of Legends installations that were done via Lutris or any other source</b>, we do the installation ourselves and we handle our own installation and ONLY it.

- <b> Don't demand features in the bug tracker, open a pull request instead and contribute with code</b>, depending of the amount of work i might be able to pull it off but if things get super complex or are super niche i won't be able to do it.

- The .svg icon that this application uses is provided by the [papirus-icon-theme project](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme)

