# BSDT

BSDT(Bird Shie Defense Turret) is a defense system that protects private property from contamination such as droppings or dead bodies by identifying and preemptively striking birds or insects approaching private property from the air.

## 🎯 Goal

Build a defense system that identifies and deters aerial objects immediately. (While deterring access, it uses water guns or optical signals to minimize physical damage while respecting bioethics.)

## 🧩 Specification

- **Hardware**
  - Raspberry Pi 4B
  - Camara - Raspberry Pi camera module 5MP
  - Monitoring device: Macbook Pro
- **Vision computing:** OpenCV, YOLOv5 (TBD)
- **LLM:** OpenAI API

## 🔧 Flow chart

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

## 📁 Directory structure

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
- OpenAI API → on-divice model migration
