from modules.vision.detect_motion import detect_motion
from modules.vision.broadcast import broadcast
import threading
import argparse

def observe(stream=False):
    if stream:
        t = threading.Thread(target=detect_motion, daemon=True)
        t.start()
        broadcast()
    else:
        detect_motion()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stream", action="store_true", help="Enable stream mode")
    parser.add_argument("--no-stream", action="store_true", help="Disable stream mode")
    parser.set_defaults(stream=False)
    args = parser.parse_args()
    observe(args.stream)
