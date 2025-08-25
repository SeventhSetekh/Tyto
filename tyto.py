import cv2
import time
import json
import os
from utils.camera_utils import *
from utils.system_files import *
from flask import Flask, Response, request, render_template, redirect, abort

CONFIG_LOCATION = "/home/seth/Documents/Projects/Tyto/config.json"
LOG_LOCATION = "/home/seth/Documents/Projects/Tyto/log.txt"
isRecordable=True
isRecording=False
video_index = 0
feeds = []

log = Log(LOG_LOCATION)
config = Config(CONFIG_LOCATION)
config_data = config.read()

#camera = Camera(config_data[config_data["mode"]]["local_feed"])
#feeds.append(camera)
for i in config_data['cameras']:
    feeds.append(Camera(i))
for i in config_data['streams']:
    feeds.append(Camera(i))
print(feeds)



app = Flask(__name__)

@app.route('/video_feed', methods = ["GET"])
def video_feed():
    # Streaming response that serves frames to the browser
    if "feed" in request.args:
        try:
            active_feed = int(request.args["feed"])
            print(active_feed)
            print(type(active_feed))
            if(video_index >= len(feeds)):
                abort(404)
            return Response(feeds[active_feed].grab_image(), mimetype='multipart/x-mixed-replace; boundary=frame')
            #return Response(feeds[active_feed].grab_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')
        except:
            return redirect("/feed_list")
    return redirect("/feed_list")

@app.route("/stats")
def stats():
    return(feeds[video_index].grab_stats())

@app.route("/add_feed")
def add_feed():
    return True

@app.route("/feed_list")
def feed_list():
    return render_template('feed_list.html')



#ALL STREAM VEIW
@app.route('/streams', methods = ["GET","POST"])
def streams():
    print (request.method)
    if request.is_json:
        print(request.get_json())
    print(request.form)
    # Simple webpage with video feed
    print("index accessed")
    return render_template('server_index.html', video_feeds=feeds)


#INDIVIDUAL STREAM VIEW
@app.route('/', methods=['GET','POST'])
def index():
    global isRecording
    global video_index
    
    print(video_index)
    if "feed" in request.args:
        try:
            video_index = int(request.args["feed"])
        except:
            print("inproper GET request")
    print(video_index)
    print("length of feed: "+str(len(feeds)))
    if(video_index >= len(feeds)):
        abort(404)
    print("is it still open?:")
    camStats = str(feeds[video_index].grab_stats())
    if "format" in request.args:
        format = request.args["format"]
        match format:
            case "Default":
                print("select default")
                feeds[video_index].format = 0
            case "Negative":
                print("select negative")
                feeds[video_index].format = 1
            case "Gray":
                print("select gray")
                feeds[video_index].format = 2
    if "time_stamp" in request.args:
        print("adding timestamp")
        if feeds[video_index].timeStamp:
            feeds[video_index].timeStamp = False
        else:
            feeds[video_index].timeStamp = True    

    if request.is_json:
        print(request.get_json())
    for values in request.form:
        print(request.form[values])
    #<-- end for testing
    
    if "startrecording" in request.form:
        print("starting the recording")
        print(request.form["filename"])
        feeds[video_index].start_recording_thread(str(request.form["filename"]))
        isRecording=True
    if "stoprecording" in request.form:
        print("stopping the recording")
        feeds[video_index].stop_recording_thread()
        isRecording=False
    # Simple webpage with video feed
    print("index accessed")
    return render_template('client_index.html',recordOption=isRecordable,recording=isRecording,video_feed=video_index,statistics=camStats)



if __name__ == '__main__':
    # Run the app on port 80, accessible from any network interface
    print("starting app")
    app.run(host='0.0.0.0', port=8777, debug=False)