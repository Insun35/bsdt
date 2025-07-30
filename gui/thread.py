import cv2
import json

from PyQt5 import QtCore, QtGui
import requests


class VideoThread(QtCore.QThread):
    changePixmap = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self._running = True

    def run(self):
        cap = cv2.VideoCapture(self.url)
        if not cap.isOpened():
            print(f"Error: cannot open stream {self.url}")
            return
        while self._running:
            ret, frame = cap.read()
            if not ret:
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            qt_img = QtGui.QImage(
                rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888
            )
            scaled = qt_img.scaled(800, 450, QtCore.Qt.KeepAspectRatio)
            self.changePixmap.emit(scaled)
        cap.release()

    def stop(self):
        self._running = False
        self.wait()


class SSEThread(QtCore.QThread):
    newEvent = QtCore.pyqtSignal(dict)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self._running = True

    def run(self):
        with requests.get(self.url, stream=True) as resp:
            for line in resp.iter_lines():
                if not self._running:
                    break
                if line and line.startswith(b"data: "):
                    payload = line[len(b"data: ") :]
                    try:
                        data = json.loads(payload.decode())
                        self.newEvent.emit(data)
                    except:
                        pass

    def stop(self):
        self._running = False
        self.wait()
