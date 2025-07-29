#!/usr/bin/env python3
import os
import time
import cv2
from picamera2 import Picamera2

# Parameters
# ────────────────────────────────────────────────
CAPTURE_DIR = "logs"
AREA_MIN = 1500
AREA_MAX = 50000
ASPECT_RATIO_MIN = 0.2
ASPECT_RATIO_MAX = 5.0
MOTION_REQUIRED = 20        # Number of consecutive frames to detect
DEBOUNCE_SECONDS = 10       # Time to wait after capturing
# ────────────────────────────────────────────────

# Prepare capture directory
os.makedirs(CAPTURE_DIR, exist_ok=True)

# Initialize camera
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()
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
        # a) Read frame & grayscale+blur
        frame = picam2.capture_array()                                   # H×W×3 RGB
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # b) Remove background → binary mask → remove noise
        fgmask = fgbg.apply(gray)
        _, fgmask = cv2.threshold(fgmask, 254, 255, cv2.THRESH_BINARY)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)

        # c) Detect contours & filter
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

        # d) Filter consecutive frames
        if motion_detected:
            motion_count += 1
        else:
            motion_count = 0

        # e) Capture if detected enough consecutive frames
        if motion_count >= MOTION_REQUIRED:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            fname = os.path.join(CAPTURE_DIR, f"motion_{timestamp}.jpg")
            picam2.capture_file(fname)  # Encode JPEG
            print(f"[{time.strftime('%H:%M:%S')}] Motion captured → {fname}")
            motion_count = 0
            time.sleep(DEBOUNCE_SECONDS)

        # f) Avoid too fast loop
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n== Stopped by user ==")
