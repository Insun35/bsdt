from modules.vision.detect_motion import detect_motion
from modules.vision.broadcast import broadcast
import threading

def observe():
    t = threading.Thread(target=detect_motion, daemon=True)
    t.start()
    broadcast()
    
if __name__ == "__main__":
    observe()
