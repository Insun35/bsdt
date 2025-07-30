import os
from flask import Flask, Response, send_from_directory, jsonify, stream_with_context
import cv2
import sqlite3
import queue
import json

from modules.vision.camera import picam2
from utils.config import DB_PATH

PORT = 8080
CAPTURES_DIR = "captures"
BASE_DIR     = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

app = Flask(__name__)
app.config['CAPTURES_DIR'] = os.path.join(BASE_DIR, CAPTURES_DIR)
subscribers = []

@app.route('/captures/<path:filename>')
def serve_capture(filename):
    print(f"== Serving capture {filename} from {app.config['CAPTURES_DIR']} ==")
    return send_from_directory(app.config['CAPTURES_DIR'], filename, as_attachment=True)

@app.route('/latest')
def latest():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()
    cur.execute(
        "SELECT timestamp, filepath, classification "
        "FROM action_logs ORDER BY id DESC LIMIT 1"
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({}), 204

    ts, path, cls = row
    fn = os.path.basename(path)
    return jsonify({
        "timestamp": ts,
        "filename":  fn,
        "classification": cls,
        "image_url":   f"/captures/{fn}"
    })
    
@app.route('/events')
def events():
    def gen():
        q = queue.Queue()
        subscribers.append(q)
        try:
            while True:
                data = q.get()
                yield f"data: {json.dumps(data)}\n\n"
        except GeneratorExit:
            subscribers.remove(q)

    return Response(stream_with_context(gen()),
                    mimetype='text/event-stream')

def notify_subscribers(record: dict):
    for q in subscribers:
        q.put(record)

def gen_frames():
    while True:
        frame = picam2.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ret:
            continue
        jpg_bytes = buffer.tobytes()
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + jpg_bytes + b'\r\n'
        )

@app.route('/video_feed')
def video_feed():
    return Response(
        gen_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/')
def index():
    return '<html><body><img src="/video_feed" /></body></html>'

def broadcast():
    print("== Starting Flask MJPEG server on port {} ==".format(PORT))
    app.run(host='0.0.0.0', port=PORT, threaded=True)
