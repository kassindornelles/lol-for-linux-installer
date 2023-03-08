import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import QThread, pyqtSignal, QObject, Qt
from subprocess import Popen
from queue import Queue


class Installer(QMainWindow):
    def __init__(self):
        super(Installer, self).__init__()
        loadUi("installer.ui", self)  # load the UI from the .ui file
        self.setFixedSize(self.size())
        self.setWindowTitle('League of Legends installer')
        self.install_button.clicked.connect(self.start_installation)

    def start_installation(self):
        self.welcomelabel.setText("This may take a while based on your internet and system speed...")
        self.install_button.hide()  # hide the button
        self.adviselabel.setText("Installing, please be patient. \n This window will close itself when the install process is done \n Launch the game using the shortcut in the system menu")

        # Create a new thread to run the installation process
        self.thread = QThread()
        self.installer = LeagueInstaller()
        self.installer.moveToThread(self.thread)
        self.installer.finished.connect(self.installation_finished)
        self.thread.started.connect(self.installer.run)
        self.thread.start()

    def installation_finished(self):
        self.welcomelabel.setText("Installation finishing, leaving installer...")
        self.adviselabel.hide()
        sys.exit(app.exec_())

class LeagueInstaller(QObject):
    finished = pyqtSignal()

    def run(self):
        # We run the 'leagueinstaller.py' script here
        import subprocess
        subprocess.call(['python', 'leagueinstaller.py'])

        self.finished.emit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    installer = Installer()
    installer.show()
    sys.exit(app.exec_())
