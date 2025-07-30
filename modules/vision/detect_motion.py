#!/usr/bin/env python3
import os
import time
import cv2
import sqlite3

from modules.vision.iff import classify_image
from modules.vision.camera import picam2
from utils.config import DB_PATH

# Parameters
# ────────────────────────────────────────────────
CAPTURE_DIR = "captures"
AREA_MIN = 1500
AREA_MAX = 50000
ASPECT_RATIO_MIN = 0.2
ASPECT_RATIO_MAX = 5.0
MOTION_REQUIRED = 10        # Number of consecutive frames to detect
DEBOUNCE_SECONDS = 10       # Time to wait after capturing
# ────────────────────────────────────────────────

# Prepare capture directory
os.makedirs(CAPTURE_DIR, exist_ok=True)

# Initialize SQLite database
print("Initializing SQLite database at", DB_PATH)
try:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS action_logs (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp      TEXT    NOT NULL,
        filepath       TEXT    NOT NULL,
        classification TEXT    NOT NULL
    )
    """)
    conn.commit()
    print("  [OK] Table 'action_logs' created.")
except Exception as e:
    print(f"Error: {e}")
    exit(1)

def detect_motion():
    time.sleep(1)  # Sensor warming up

    # Initialize background remover & morphological kernel
    fgbg = cv2.createBackgroundSubtractorMOG2(
        history=500, varThreshold=50, detectShadows=False
    )
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    motion_count = 0

    print("== Motion capture started (CTRL+C to stop) ==")
    try:
        while True:
            # Read frame & grayscale+blur
            frame = picam2.capture_array()
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            # Remove background → binary mask → remove noise
            fgmask = fgbg.apply(gray)
            _, fgmask = cv2.threshold(fgmask, 254, 255, cv2.THRESH_BINARY)
            fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)

            # Detect contours & filter
            contours, _ = cv2.findContours(
                fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            motion_detected = False
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < AREA_MIN or area > AREA_MAX:
                    continue
                x, y, w, h = cv2.boundingRect(cnt)
                ar = w / float(h)
                if ar < ASPECT_RATIO_MIN or ar > ASPECT_RATIO_MAX:
                    continue
                motion_detected = True
                break

            # Filter consecutive frames
            if motion_detected:
                motion_count += 1
            else:
                motion_count = 0

            # Capture if detected enough consecutive frames
            if motion_count >= MOTION_REQUIRED:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                fname = os.path.join(CAPTURE_DIR, f"motion_{timestamp}.jpg")
                picam2.capture_file(fname)  # Encode JPEG
                print(f"[{time.strftime('%H:%M:%S')}] Motion captured → {fname}")
                
                cls = classify_image(fname)
                print(f"Classification: {cls}")
                
                try:
                    conn = sqlite3.connect(DB_PATH)
                    cur  = conn.cursor()
                    cur.execute(
                        "INSERT INTO action_logs (timestamp, filepath, classification) VALUES (?, ?, ?)",
                        (timestamp, fname, cls)
                    )
                    conn.commit()
                    conn.close()
                    print(f"  [DB OK] {fname} → {cls}")
                except Exception as e:
                    print(f"  [DB ERROR] {e}")

                motion_count = 0
                time.sleep(DEBOUNCE_SECONDS)

            # Avoid too fast loop
            time.sleep(0.1)

    except Exception as e:
        print(f"Motion detector error: {e}")
