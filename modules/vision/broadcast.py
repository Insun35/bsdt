from flask import Flask, Response
import cv2
from modules.vision.camera import picam2

PORT = 8080

app = Flask(__name__)

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
