import cv2
import time
import json
from flask import Flask, Response, request, render_template
from utils.camera_utils import Camera

#Pull in the config file
with open("config.json", "r") as read_file:
    config = json.load(read_file)
#print (config["feed"])

div_html = '''
/video_feed>
'''
feed_urls = [
    "/video_feed",
    "http://192.168.1.15:8777/video_feed",
    "http://192.168.1.15:8776/video_feed"
]

app = Flask(__name__)

camera = Camera(config[config["mode"]]["local_feed"])
isRecordable=True
isRecording=False

@app.route('/video_feed')
def video_feed():
    # Streaming response that serves frames to the browser
    return Response(camera.grab_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/', methods = ["GET","POST"])
def index():
    print (request.method)
    if request.is_json:
        print(request.get_json())
    print(request.form)
    # Simple webpage with video feed
    print("index accessed")
    return render_template('server_index.html', video_feeds=feed_urls)


if __name__ == '__main__':
    # Run the app on port 80, accessible from any network interface
    app.run(host='0.0.0.0', port=8778, debug=False)