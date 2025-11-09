import cv2
import time
import json
import os
from utils.camera_utils import *
from utils.system_files import *
from flask import Flask, Response, request, render_template, redirect


x = input("camera feed: ")

camera = Camera(x)
isRecordable=True



app = Flask(__name__)

@app.route('/video_feed')
def video_feed():
    # Streaming response that serves frames to the browser
    return Response(camera.grab_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    # Run the app on port 80, accessible from any network interface
    app.run(host='0.0.0.0', port=8777, debug=False)