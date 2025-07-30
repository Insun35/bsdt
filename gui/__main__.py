import sys
from PyQt5 import QtWidgets
from gui.main_window import MainWindow
from utils.config import API_BASE

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    url = f"{API_BASE}/video_feed"
    window = MainWindow(url)
    window.show()
    sys.exit(app.exec_())
