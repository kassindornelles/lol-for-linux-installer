pkgname=lol-for-linux-installer
pkgver=2.1
pkgrel=1
pkgdesc="League of Legends installer and manager for Linux"
arch=('x86_64')
url="https://github.com/kassindornelles/lol-for-linux-installer"
license=('GPL-3.0')
depends=('python' 'python-psutil' 'python-pyqt5' 'wine' 'python-requests' 'qt5-base' 'tar' 'lib32-gnutls' 'gnutls' 'lib32-libldap' 'libldap' 'libpng' 'lib32-libpng' 'mesa' 'lib32-mesa' 'libgphoto2' 'libpulse' 'lib32-libpulse')

package() {
  cd "$srcdir"

  # Copy launch-league-of-legends.py
  install -Dm755 lol-for-linux-installer.py "$pkgdir/usr/bin/lol-for-linux-installer"

  # Copy other necessary files and directories
  install -Dm644 env_vars.json "$pkgdir/usr/share/lol-for-linux-installer/env_vars.json"
  install -Dm644 lol-for-linux-installer.png "$pkgdir/usr/share/lol-for-linux-installer/lol-for-linux-installer.png"
  install -Dm644 leagueinstaller_code.py "$pkgdir/usr/share/lol-for-linux-installer/leagueinstaller_code.py"
  # Install the desktop file
  install -Dm644 "$srcdir/lol-for-linux-installer.desktop" "$pkgdir/usr/share/applications/lol-for-linux-installer.desktop"

  # Copy python_src directory
  cp -R python_src "$pkgdir/usr/share/lol-for-linux-installer/"
}
