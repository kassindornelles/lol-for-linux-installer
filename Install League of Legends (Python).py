#!/usr/bin/env python3
import sys, os, signal, psutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import QThread, QObject
import leagueinstaller


class Installer(QMainWindow):
    def __init__(self):
        super(Installer, self).__init__()
        loadUi("installer.ui", self)  # load the UI from the .ui file
        self.setFixedSize(self.size())
        self.setWindowTitle('League of Legends installer')
        self.install_button.clicked.connect(self.installer_code)
        self.selectFolder.clicked.connect(self.select_folder_path)
        self.cancelButton.clicked.connect(self.cancel_installation)
        self.install_button.setEnabled(False)
        self.cancelButton.hide()

    def select_folder_path(self):
        self.game_main_dir = QFileDialog.getExistingDirectory(self, 'Where do you want to install the game?')
        while self.game_main_dir and os.path.abspath(self.game_main_dir) == os.path.expanduser("~"):
            # If the user selected their home directory, display an error message
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setText("Cannot install the game directly in the home directory.")
            msg_box.setInformativeText("Please create a folder in your home directory instead so we can use it")
            msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg_box.setDefaultButton(QMessageBox.Ok)
            if msg_box.exec_() == QMessageBox.Ok:
                # If the user clicks "Ok", allow them to select a different directory
                self.game_main_dir = QFileDialog.getExistingDirectory(self, 'Where do you want to install the game?')
            else:
                # If the user clicks "Cancel", exit the loop and do not set the directory
                self.game_main_dir = None

        if self.game_main_dir:
            self.install_button.setEnabled(True)
        else:
            # Handle case where user pressed cancel
            print("User pressed cancel")

    def cancel_installation(self):
        # Get the PID of the current process
        pid = os.getpid()

        # Get a list of all child processes
        children = psutil.Process(pid).children(recursive=True)

        # Terminate all child processes
        for child in children:
            child.send_signal(signal.SIGTERM)

        # Terminate the main application process
        os.kill(pid, signal.SIGTERM)

    def installer_code(self):
        self.selectFolder.hide()
        self.cancelButton.show()
        self.cancelButton.setEnabled(True)
        self.welcomelabel.setText("This may take a while based on your internet and system speed...")
        self.install_button.hide()  # hide the button
        self.adviselabel.setText(
            "Installing, please be patient. \n This window will close itself when the install process is done \n Launch the game using the shortcut in the system menu")
        self.thread = QThread()
        self.worker = Worker(self.game_main_dir)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.finish_installation)
        self.thread.start()
        self.thread.quit()

    def finish_installation(self):

        QApplication.quit()


class Worker(QObject):
    def __init__(self, game_main_dir):
        super().__init__()
        self.game_main_dir = game_main_dir

    def run(self):
        leagueinstaller.league_install_code(self.game_main_dir)
        QApplication.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    installer = Installer()
    installer.show()
    sys.exit(app.exec_())
