from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2
import numpy as np
from gem.gemDataCollect import SingleGemCollector
from sense_hat import SenseHat
import yaml

# output frame initialization
# lock thread in case of multiple users
outputFrame = None
lock = threading.Lock()
with open("gem/settings.yml", "r") as f:
    settings = yaml.load(f, Loader=yaml.FullLoader)
# flask initialization
app = Flask(__name__)

# initialize video stream and sensor warmup
cap = cv2.VideoCapture(-1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings["cameraResolution"][0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings["cameraResolution"][1])
cap.set(cv2.CAP_PROP_FPS, settings["cameraFramerate"])
time.sleep(1)

# initialize the sense hat
sense = SenseHat()

# home route
@app.route("/")
def index():
    return render_template("index.html")


def scanning():
    # global ref to vid capture, frame, and lock
    global cap, outputFrame, lock

    gemDevice = SingleGemCollector()
    total_frames = 0

    while True:
        ret, frame = cap.read()
        timestamp = datetime.datetime.now()

        orientation = sense.get_orientation()
        frame = gemDevice.orientationOverlay(frame, orientation)
        if total_frames % gemDevice.settings["cameraFramerate"] == 0:
            gemDevice.updateOverlay()

        frame = cv2.add(frame, gemDevice.frame_overlay)

        total_frames += 1

        with lock:
            outputFrame = frame.copy()

def generate_encoded():
    # global references
    global outputFrame, lock

    while True:
        with lock:
            if outputFrame is None:
                continue

            # encode frame in jpeg
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

            if not flag:
                continue

        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
    return Response(generate_encoded(),
    mimetype= "multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    # command line args
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
                    help="ip address of device")
    ap.add_argument("-o", "--port", type=int, required=True,
                    help="port num of server")
    args = vars(ap.parse_args())

    t = threading.Thread(target=updateOverlay)
    t.daemon = True
    t.start()

    app.run(host = args["ip"], port = args["port"], debug=True,
            threaded=True, use_reloader=False)

cap.release()


        