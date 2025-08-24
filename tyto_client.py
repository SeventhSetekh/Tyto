import cv2
import time
import json
import os
from utils.camera_utils import *
from flask import Flask, Response, request, render_template, redirect

CONFIG_LOCATION = "/home/seth/Documents/Projects/Tyto/"
LOG_LOCATION = CONFIG_LOCATION

if os.path.exists("/Tyto/config2.json"):
    print("path exists")
else:
    with open("config2.json",'w') as read_file:
        print("opened")

#Pull in the config file
with open("config.json", "r") as read_file:
    config = json.load(read_file)

print(config)
config["server"]["local_feeds"].append("video3")
config["server"]["local_feeds"][0]=("video3")
config["server"]["config_settings"]=[0,1,2,3,4]
print()
print(config)
print()
config2 = config
with open("config.json", "w") as read_file:
    config2 = json.dump(config,read_file,indent=4)



app = Flask(__name__)

camera = Camera(config[config["mode"]]["local_feed"])
isRecordable=True
isRecording=False

@app.route('/video_feed')
def video_feed():
    # Streaming response that serves frames to the browser
    return Response(camera.grab_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/stats")
def stats():
    return(camera.grab_stats())


@app.route('/', methods = ["GET","POST"])
def index():
    global isRecording
    camStats = str(camera.grab_stats())
    #-->for testing
    print (request.method)
    if request.is_json:
        print(request.get_json())
    for values in request.form:
        print(request.form[values])
    #<-- end for testing
    if "gray" in request.form:
        print("a;slkdfj;askldjf")
        camera.format = 2
    if "negative" in request.form:
        print("select negative")
        camera.format = 1
    if "default" in request.form:
        print("select default")
        camera.format = 0
    if "time_stamp" in request.form:
        print("adding timestamp")
        if camera.timeStamp:
            camera.timeStamp = False
        else:
            camera.timeStamp = True
    if "startrecording" in request.form:
        print("starting the recording")
        print(request.form["filename"])
        camera.startRecord(str(request.form["filename"]))
        isRecording=True
    if "stoprecording" in request.form:
        print("stopping the recording")
        camera.stopRecord()
        isRecording=False
    # Simple webpage with video feed
    print("index accessed")
    return render_template('client_index.html',recordOption=isRecordable,recording=isRecording,statistics=camStats)


if __name__ == '__main__':
    # Run the app on port 80, accessible from any network interface
    app.run(host='0.0.0.0', port=8777, debug=False)