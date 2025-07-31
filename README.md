# BSDT

BSDT(Bird Shit Defense Turret) is a defense system that protects private property from contamination such as droppings or dead bodies by identifying and preemptively striking birds or insects approaching private property from the air.

## 🎯 Goal

Build a defense system that identifies and deters aerial objects immediately. (While deterring access, it uses water guns or optical signals to minimize physical damage while respecting bioethics.)

## 📖 Get started

Follow these steps to get BSDT up and running:

### 1. 🥞 Raspberry Pi (Server)

1.1  Hardware & OS

- Raspberry Pi 4 (or later)
- Pi Camera v2 (CSI) connected
- Raspberry Pi OS (Bullseye/Bookworm) up‑to‑date

```bash
sudo apt update && sudo apt upgrade -y
```

1.2. System Dependencies

```bash
sudo apt install -y python3-pip python3-venv \
python3-picamera2 python3-libcamera \
libatlas-base-dev
```

1.3. Clone & Virtualenv

```bash
cd ~
git clone https://github.com/Insun35/bsdt.git
cd bsdt
python3 -m venv .venv
source .venv/bin/activate
```

1.4. Python Requirements

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

1.5. Configure OpenAI Key
Create a `.env` in the project root:

```ini
OPENAI_API_KEY=sk-...
```

1.6. Start the motion detection & streaming server

```bash
# motion detection + MJPEG streaming
python -m modules.vision --stream
```

- MJPEG stream: http://<Pi_IP>:8080/video_feed
- Latest capture JSON: http://<Pi_IP>:8080/latest
- Static JPEGs: http://<Pi_IP>:8080/captures/<filename>
- Server‑Sent Events: http://<Pi_IP>:8080/events

To run motion detection only (no streaming):

```bash
python -m modules.vision --no-stream
# or
python -m modules.vision # No streaming by default
```

### 2. 💻 GUI Client

2.1. Prerequisites

- Python 3.8+
- Network access to your Pi’s port 8080

2.2. Clone & Virtualenv

```bash
cd ~
git clone https://github.com/Insun35/bsdt.git
cd bsdt/gui
python3 -m venv .venv
source .venv/bin/activate
```

2.3. Install GUI Dependencies

```bash
pip install --upgrade pip
pip install pyqt5 opencv-python requests sseclient-py
```

2.4. Configure the Pi Address
Edit the top of stream_viewer_with_event.py (or pass as argument) to point at your Pi:

```ini
API_BASE = "http://<Pi_IP>:8080"   # ← replace with your Pi’s IP
```

2.5. Launch the GUI

```bash
python -m gui
```

You should see:

- Live video from http://<Pi_IP>:8080/video_feed
- Latest snapshot + classification updating in real‑time
- “🚨 Motion detected!” alert in the status bar on each new event

## 🧩 Specification

- **Hardware**
  - Raspberry Pi 4B
  - Camera - Raspberry Pi camera module 5MP
  - Monitoring device: Macbook Pro
- **Vision computing:** OpenCV, YOLOv5 (TBD)
- **LLM:** OpenAI API

### 🔧 Flow chart

```
┌──────────────────┐          ┌────────────────────┐
│   Camera module  │ ─────▶   │    Detect motion   │
└──────────────────┘          └────────────────────┘
                                    │
                                    ▼
                              ┌─────────────────────┐
                              │   Identify entity   │
                              └─────────────────────┘
                                    │ No (Human) → safety mode
                                   Yes
                                    │
                                    ▼
                              ┌──────────────────────────┐
                              │   Defense action module  │
                              └──────────────────────────┘
                                    │
                                    ▼
                              ┌─────────────────────┐
                              │   Save log & report │
                              └─────────────────────┘

```

### 📁 Directory structure

```
bsdt/
├── README.md
├── .gitignore
├── requirements.txt
│
├── utils/
│   └── config.py
│
├── scripts/
│   ├── start_bsdt.sh
│   ├── calibrate_camera.py
│   └── capture_test.py
│
├── modules/
│   ├── vision/
│   │   ├─ broadcast.py
│   │   ├─ camera.py
│   │   ├─ detect_motion.py
│   │   └─ iff.py
│   │
│   └── control/
│       ├── pump.py
│       ├── turret.py
│       └── speaker.py
│
├── gui/
│   ├── main_window.py
│   └── thread.py
│
├── tests/
│   ├── test_motion.py
│   ├── test_pump.py
│   └── test_classifier.py
│
├── action_logs.db
│
└── captures/
```

## 🚀 Roadmap

- Implement prototype using OpenAI API
  - ~ Aug 2025: motion detection
  - ~ Sep 2025: complete prototype
- OpenAI API → on-device model migration
