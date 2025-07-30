import sys
import os
import sqlite3
import cv2
import requests
import json
from PyQt5 import QtCore, QtGui, QtWidgets

API_BASE = "http://localhost:8080"


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


class MainWindow(QtWidgets.QMainWindow):
    POLL_INTERVAL_MS = 2000

    def __init__(self, stream_url):
        super().__init__()

        self.setWindowTitle("BSDT Live Stream + Snapshot")
        self.resize(820, 720)

        central = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout(central)
        vbox.setContentsMargins(5, 5, 5, 5)
        vbox.setSpacing(10)

        self.video_label = QtWidgets.QLabel(
            "Connecting...", alignment=QtCore.Qt.AlignCenter
        )
        self.video_label.setFixedHeight(460)
        vbox.addWidget(self.video_label)

        bottom = QtWidgets.QWidget()
        hbox = QtWidgets.QHBoxLayout(bottom)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(10)

        self.snapshot_label = QtWidgets.QLabel()
        self.snapshot_label.setFixedSize(200, 150)
        self.snapshot_label.setFrameShape(QtWidgets.QFrame.Box)
        hbox.addWidget(self.snapshot_label)

        self.text_label = QtWidgets.QLabel("No captures yet.")
        self.text_label.setWordWrap(True)
        hbox.addWidget(self.text_label, 1)

        vbox.addWidget(bottom)
        self.setCentralWidget(central)

        self.statusBar().showMessage("Ready", 2000)

        # Video Thread
        self.thread = VideoThread(stream_url)
        self.thread.changePixmap.connect(self.update_video)
        self.thread.start()

        # SSE Thread
        self.sse = SSEThread(API_BASE + "/events")
        self.sse.newEvent.connect(self.on_new_capture)
        self.sse.start()

        self.current_id = None
        self.timer = QtCore.QTimer(self)
        self.timer.start(self.POLL_INTERVAL_MS)

    def update_video(self, qt_img):
        self.video_label.setPixmap(QtGui.QPixmap.fromImage(qt_img))

    def on_new_capture(self, data: dict):
        try:
            self.statusBar().showMessage("🚨 Motion detected!", 2000)
            r = requests.get(API_BASE + "/latest", timeout=1.0)
            if r.status_code != 200:
                return
            data = r.json()
            fn = data["filename"]
            if fn == getattr(self, "current_filename", None):
                return
            self.current_filename = fn

            # 1) load snapshot via HTTP
            img_data = requests.get(API_BASE + data["image_url"], timeout=1.0).content
            img = QtGui.QImage.fromData(img_data, "JPG")
            thumb = img.scaled(
                self.snapshot_label.width(),
                self.snapshot_label.height(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation,
            )
            self.snapshot_label.setPixmap(QtGui.QPixmap.fromImage(thumb))

            # 2) update text
            display = (
                f"<b>Time:</b> {data['timestamp']}<br>"
                f"<b>Class:</b> {data['classification']}"
            )
            self.text_label.setText(display)

        except Exception as e:
            print("Error fetching latest capture:", e)

    def closeEvent(self, event):
        self.thread.stop()
        self.sse.stop()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    url = f"{API_BASE}/video_feed"
    window = MainWindow(url)
    window.show()
    sys.exit(app.exec_())
