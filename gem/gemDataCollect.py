import numpy as np
import cv2
import imutils
import minimalmodbus
import time
import yaml
import datetime

class SingleGemCollector:
    def __init__(self):
        with open("settings.yml", "r") as settings_file:
            settings = yaml.load(settings_file, Loader=yaml.FullLoader)
        self.settings = settings

        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.wire_overlay = None
        self.wireframe = None
        self.frame_overlay = None

        self.yaw = 0
        self.roll = 0
        self.pitch = 0

    def updateOverlay(self, orientation):
        # function that returns the overlay for the image on a black background

        
        

        # drawing the wire frame and reticle
        if self.wireframe == None:
            image = np.zeros((self.settings["cameraResolution"][1], self.settings["cameraResolution"][0], 3), np.uint8)
            image = cv2.line(image, (50, 470), (50, 350), (255, 255, 255), 1, lineType=cv2.LINE_AA)
            image = cv2.line(image, (50, 470), (200, 470), (255, 255, 255), 1, lineType=cv2.LINE_AA)
            image = cv2.line(image, (50, 350), (200, 350), (255, 255, 255), 1, lineType=cv2.LINE_AA)
            image = cv2.line(image, (200, 470), (200, 350), (255, 255, 255), 1, lineType=cv2.LINE_AA)
            self.wireframe = cv2.circle(image, (320, 240), 15, (200, 0, 0), -1)


        
        if pitch_min <= self.pitch <= pitch_max and yaw_min <= self.yaw <= yaw_max:
            # determining where in the wireframe to draw the newest circle
            paint_x = int(((self.yaw - yaw_min)/(yaw_max-yaw_min))*150 + 50)
            paint_y = int(470 - ((self.pitch - pitch_min)/(pitch_max-pitch_min))*120)
            
            if self.wire_overlay == None:
                self.wire_overlay = np.zeros((self.settings["cameraResolution"][1], self.settings["cameraResolution"][0], 3), np.uint8)
            
            new_circle = np.zeros((self.settings["cameraResolution"][1], self.settings["cameraResolution"][0], 3), np.uint8)
            new_circle = cv2.circle(new_circle, (paint_x, paint_y), 10, (55, 55, 55), -1)
            self.wire_overlay = cv2.add(self.wire_overlay, new_circle)
            image_overlay = cv2.add(image, self.wire_overlay)
            self.frame_overlay = image_overlay
            return image_overlay

    def orientationOverlay(self, frame, orientation):
        # reading orientation and altering pitch for convenience later
        self.yaw = orientation["yaw"]
        self.roll = orientation["roll"]
        pitch = orientation["pitch"]
        if pitch > 180:
            pitch = pitch - 360
        self.pitch = -1*pitch

        # writing the current orientation values in the top left
        image = cv2.putText(frame, str("Y: " + str(int(yaw))), (10, 20), self.font, .5, (255, 255, 255), lineType=cv2.LINE_AA)
        image = cv2.putText(image, str("P: " + str(int(pitch))), (10, 35), self.font, .5, (255, 255, 255), lineType=cv2.LINE_AA)
        image = cv2.putText(image, str("R: " + str(int(roll))), (10, 50), self.font, .5, (255, 255, 255), lineType=cv2.LINE_AA)

        # timestamp
        timestamp = datetime.datetime.now()
        image = cv2.putText(image, timestamp.strftime("%A %d %B %Y %I:%M:%S%p"),
                    (10, 65), self.font, 0.5,
                     (255, 255, 255), lineType=cv2.LINE_AA)
        
        return image









