import cv2
import time
import datetime
import numpy as np
from threading import Thread, Lock

class Camera:
    def __init__(self,
                 source):
        
        self.infile = source
        self.recording = False
        self.outfileExt = ".mp4"
        self.recordingLengths = 20 #in seconds
        self.recordingInterval = 1
        self.format = 0
        self.timeStamp = True
        self.is_running = False
        self.frame = np.zeros((480,640,3), dtype=np.uint8)
        self.start_cam_thread()
        #self.pullFeed()
    
    def pullFeed(self):
        print("pulling feed for camera")
        self.isAttached = False
        while(not self.isAttached):
            #try:
            self.camera = cv2.VideoCapture(self.infile)
            
            self.fps = int(self.camera.get(cv2.CAP_PROP_FPS))
            self.width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.brightness = int(self.camera.get(cv2.CAP_PROP_BRIGHTNESS))
            self.contrast = int(self.camera.get(cv2.CAP_PROP_CONTRAST))
            self.saturation = int(self.camera.get(cv2.CAP_PROP_SATURATION))
            self.msec = int(self.camera.get(cv2.CAP_PROP_POS_MSEC))
            self.count = int(self.camera.get(cv2.CAP_PROP_FRAME_COUNT))
            
            print("pull feed loop attached?")
            status, frame = self.camera.read()
            print("status: "+str(status))
            if(status):
                #self.frame = frame
                self.isAttached = True
                self.is_running = True
            else:
                print("releasing feed")
                self.camera.release()
                
                
            #except:
            #    print("could not pull camera feed")
            time.sleep(1)
        return True 
        
    def releaseFeed(self):
        print("releasing feed")
        self.camera.release()
        return True
    
    def grab_frame(self):
        while True:
            # Read frame from the camera
            success, frame = self.camera.read()
            if not success:
                print("Can't receive frame (stream end?). Exiting ...")
                #create blank frame (black)
                channels = 3
                frame = np.zeros((self.height, self.width, channels), dtype=np.uint8)
                #self.pullFeed()
                continue
            else:
                if self.format == 1:
                    frame = cv2.bitwise_not(frame)
                if self.format == 2:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if self.timeStamp:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cv2.putText(frame, timestamp, (10,20),cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0),1)
                if self.recording:
                    if time.time()-self.recordingStartTime >= self.recordingLengths:
                        self.stopRecord(False)
                        self.recordingInterval = self.recordingInterval + 1
                        self.startRecord(str(self.outfile))
                    self.out.write(frame)

                # Encode the frame in JPEG format
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()

                # Yield the frame in byte form
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def grab_stats(self):
        stats = []
        
        stats.append(self.fps)
        stats.append(self.width )
        stats.append(self.height)
        stats.append(self.brightness)
        stats.append(self.contrast)
        stats.append(self.saturation)
        stats.append(self.msec)
        stats.append(self.count)
        
        return (stats)
    # ALL RECORDING FUNCTIONS
    def startRecord(self, outfile):
        self.outfile = outfile
        if self.recording:
            print ("[!] system already rocording")
            return False
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        self.out = cv2.VideoWriter(str(outfile)+str(self.recordingInterval)+self.outfileExt, fourcc, self.fps, (self.width, self.height))
        self.recordingStartTime = time.time()
        self.recording = True

    def stopRecord(self,reset_recordInterval=True):
        self.recording = False
        self.out.release()
        if reset_recordInterval:
            self.recordingInterval = 1

    def start_recording_thread(self,outfile: str,time_interval=20):
        self.recording_thread = Thread(target=self.recordFeed,args=(outfile,time_interval))
        self.recording_thread.daemon = True
        self.recording_thread.start()
        return True
    
    def stop_recording_thread(self):
        self.recording = False
        self.recording_thread.join()
        return True
    
    def recordFeed(self,outfile: str,time_interval: int):
        interval = time_interval
        self.startRecord(outfile)
        while self.recording:
            if time.time()-self.recordingStartTime >= self.recordingLengths:
                self.stopRecord(False)
                self.recordingInterval = self.recordingInterval + 1
                self.startRecord(str(self.outfile))
            self.out.write(self.get_image())
        self.stopRecord()
    # END OF ALL RECORDING FUNCTIONS
    # FRAME GRABBING THREAD
    def start_cam_thread(self):
        self.cam_thread = Thread(target=self.camera_thread,args=())
        self._lock = Lock()
        self.cam_thread.daemon = True
        self.cam_thread.start()
        self.is_running = False

    def camera_thread(self):
        while True:
            if self.is_running:
                status, frame = self.camera.read()
                if status:
                    with self._lock:
                        self.frame = frame
                else:
                    print("thread loop no frame")
                    self.releaseFeed()
                    self.pullFeed()
            else:
                print("thread initiallizing feed")
                self.pullFeed()

    def get_image(self):
        with self._lock:
            return self.frame.copy()
        
    def grab_image(self):
        while True:
            # Read frame from the camera
            frame = self.get_image()

            if self.format == 1:
                frame = cv2.bitwise_not(frame)
            if self.format == 2:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if self.timeStamp:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(frame, timestamp, (10,20),cv2.FONT_HERSHEY_PLAIN, 1, (0,255,0),1)
            '''
            if self.recording:
                if time.time()-self.recordingStartTime >= self.recordingLengths:
                    self.stopRecord(False)
                    self.recordingInterval = self.recordingInterval + 1
                    self.startRecord(str(self.outfile))
                self.out.write(frame)
            '''
            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Yield the frame in byte form
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    # END OF FRAME GRABBING THREAD


    def movement_detection_thread(self,time_interval,trigger):
        frame = self.get_image()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        last_mean = np.abs(np.mean(frame))
        time.sleep(time_interval)
        while True:
            frame = self.get_image()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            result = np.abs(np.mean(frame) - last_mean)
            if result > trigger:
                self.isMovement = True
            else:
                self.isMovement = False
            last_mean = result
            time.sleep(time_interval)

def returnString(var):
    return(var)

if __name__ == "__main__":
    print("camera_utils.py")