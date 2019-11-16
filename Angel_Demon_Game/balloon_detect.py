# TODO: add comments to document
# TODO: clean up code
# TODO: make code more readable? add more debug/visual features?

import numpy as np
import cv2
import math
from picamera.array import PiRGBArray
from picamera import PiCamera

def in_to_pixels(inches):
    pixels = (inches)*(2.54)*(28.346456693)
    return pixels

class color_detector:
    def __init__(self, print_statements,headless, which_color, object_width, pi_camera):

        TAG = "INIT: "

        self.print_statements = print_statements
        self.which_color = which_color
        self.pi_camera = pi_camera
        self.headless_mode = headless

        self.object_width_in = object_width
        self.object_width_pixels = in_to_pixels(object_width)

        self.focal_length_pixels = 1126.85714

        if self.print_statements: print(TAG + "color_detector class successfully created")

        self.set_color_bounds()
        self.get_camera_properties()

    def set_color_bounds(self):

        TAG = "SET_COLOR_BOUNDS: "
        lower_color = self.which_color.lower()

        if lower_color == 'r':
            self.lower_bound = np.array([161, 155, 84])
            self.upper_bound = np.array([179, 255, 255])
            COLOR = "red"
        elif lower_color == 'b':
            self.lower_bound = np.array([100, 50, 50])
            self.upper_bound = np.array([130, 255, 255])
            COLOR = "blue"

        if self.print_statements: print(TAG + "color bounds set to " + COLOR)

    def get_camera_properties(self):

        TAG = "GET_CAMERA_STATS: "

        if self.pi_camera:
            self.camera_height_pixels = 720
            self.camera_width_pixels = 1080
            self.camera_center_x = int((self.camera_width_pixels) / 2 - 1)
            self.camera_center_y = int((self.camera_height_pixels) / 2 - 1)
        else:
            camera = cv2.VideoCapture(0)
            ret, frame = camera.read()
            self.camera_height_pixels = int(frame.shape[0])
            self.camera_width_pixels = int(frame.shape[1])
            self.camera_center_x = int((self.camera_width_pixels) / 2 - 1)
            self.camera_center_y = int((self.camera_height_pixels) / 2 - 1)
            camera.release()

        if self.print_statements: print(TAG + "camera properties updated")

    def run_detector(self):

        # TODO: should we take the average of all the measurements? (n=10) or throw out some of the values? (like min and max values)

        TAG = "RUN_DETECTOR: "

        count = 1
        distances = []
        x_correct = []
        y_correct = []

        if self.pi_camera:
            print("pi")
            camera = PiCamera()
            camera.resolution = (1080, 720)
            camera.framerate = 60
            rawCapture = PiRGBArray(camera, size = (1080 , 720))

            for frame_value in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                # grab the raw NumPy array representing the image, then initialize the timestamp
                # and occupied/unoccupied text
                frame = frame_value.array

                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                # Threshold the HSV image to get only blue colors
                mask = cv2.inRange(hsv, self.lower_bound, self.upper_bound)
                counts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

                cv2.line(frame, (self.camera_center_x, self.camera_center_y - 10),(self.camera_center_x, self.camera_center_y + 10), (0, 0, 255), 2)
                cv2.line(frame, (self.camera_center_x - 10, self.camera_center_y),(self.camera_center_x + 10, self.camera_center_y), (0, 0, 255), 2)

                if len(counts) > 0:
                    total_area = max(counts, key=cv2.contourArea)
                    self.get_bounding_rect(total_area)
                    cv2.rectangle(frame, (self.rect_x_start, self.rect_y_start),(self.rect_x_start + self.rect_width, self.rect_y_start + self.rect_height),(0, 255, 0), 2)
                    center_rect = self.distance_to_center()
                    cv2.line(frame, (center_rect[0], center_rect[1]), (self.camera_center_x, self.camera_center_y),
                             (0, 0, 255), 2)
                    frame = cv2.circle(frame, (center_rect[0], center_rect[1]), 5, (255, 0, 0), -1)
                    self.distance_camera_to_object()
                    cv2.putText(frame, "Distance: " + str(round(self.distance_to_object, 2)) + " in.", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                    cv2.putText(frame, self.get_correction(), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                                cv2.LINE_AA)
                    if 10 < count:
                        distances.sort()
                        self.average_distance = sum(distances)/len(distances)
                        self.average_x_correct = sum(x_correct) / len(x_correct)
                        self.average_y_correct = sum(y_correct) / len(y_correct)
                        break
                    else:
                        distances.append(self.distance_to_object)
                        x_correct.append(self.x_offset_angle)
                        y_correct.append(self.y_offset_angle)
                        count = count + 1

                # show the frame

                if not self.headless_mode:
                    cv2.imshow("Frame", frame)

                rawCapture.truncate(0)

        else:
            cap = cv2.VideoCapture(0)

            while True:
                _, frame = cap.read()

                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                mask = cv2.inRange(hsv, self.lower_bound, self.upper_bound)
                counts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

                cv2.line(frame, (self.camera_center_x, self.camera_center_y - 10),(self.camera_center_x, self.camera_center_y + 10), (0, 0, 255), 2)
                cv2.line(frame, (self.camera_center_x - 10, self.camera_center_y),(self.camera_center_x + 10, self.camera_center_y), (0, 0, 255), 2)

                if len(counts) > 0:
                    total_area = max(counts, key=cv2.contourArea)
                    self.get_bounding_rect(total_area)
                    cv2.rectangle(frame, (self.rect_x_start, self.rect_y_start), (self.rect_x_start + self.rect_width,self.rect_y_start+self.rect_height), (0, 255, 0), 2)
                    center_rect = self.distance_to_center()
                    cv2.line(frame,(center_rect[0],center_rect[1]),(self.camera_center_x,self.camera_center_y),(0,0,255),2)
                    frame = cv2.circle(frame, (center_rect[0],center_rect[1]), 5, (255, 0, 0), -1)
                    self.distance_camera_to_object()
                    cv2.putText(frame, "Distance: " + str(round(self.distance_to_object,2)) + " in.", (10, 30), cv2.FONT_HERSHEY_SIMPLEX ,1, (255, 0, 0) , 2, cv2.LINE_AA)
                    cv2.putText(frame, self.get_correction(), (10, 60),cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                    if 10 < count:
                        distances.sort()
                        self.average = sum(distances) / len(distances)
                        break
                    else:
                        distances.append(self.distance_to_object)
                        count = count + 1

                if not self.headless_mode:
                    cv2.imshow('frame', frame)


            cap.release()
            cv2.destroyAllWindows()

        if self.print_statements: print(TAG + "detector has finished")

    def get_bounding_rect(self, area):

        TAG = "GET_BOUNDING_REC: "

        (self.rect_x_start, self.rect_y_start, self.rect_width, self.rect_height) = cv2.boundingRect(area)

        if self.print_statements: print(TAG + "obtained bounding rectangle")

    def distance_to_center(self):

        TAG = "DISTANCE_TO_CENTER: "

        center_rect = []

        x_middle = int((self.rect_width)/2 - 1 + self.rect_x_start)
        y_middle = int((self.rect_height)/2 - 1 + self.rect_y_start)

        self.y_offset = self.camera_center_y - y_middle
        self.x_offset = self.camera_center_x - x_middle

        center_rect.append(x_middle)
        center_rect.append(y_middle)

        if self.print_statements: print(TAG + "distance between center of camera and center of object has been calculated")

        return center_rect

    def distance_camera_to_object(self):

        TAG = "DISTANCE_CAMERA_TO_OBJECT: "

        self.distance_to_object = ((self.object_width_in)*(self.focal_length_pixels))/(self.rect_width)

        if self.print_statements: print(TAG + "distance from camera to object has been determined")

    def get_correction(self):

        # TODO: check to see if angles are correct
        # TODO: convert angle to be between 0 and 180 degrees

        TAG = "GET_CORRECTION: "

        self.x_offset_angle = round(math.atan2(self.x_offset,self.distance_to_object)*(180/math.pi),2)
        self.y_offset_angle = round(math.atan2(self.y_offset, self.distance_to_object)*(180/math.pi),2)
        offset_string = "X: {} | Y: {}".format(self.x_offset_angle, self.y_offset_angle)

        if self.print_statements: print(TAG + "correct angles have been calculated")

        return offset_string

    def check_balloon(self):

        # TODO: do we need this? should we add more checking parameters?

        TAG = "CHECK_BALLOON: "

        percent_difference = abs(self.rect_width - self.rect_height)/100

        if percent_difference > 0.6:
            print("not balloon")
        else:
            print("balloon")

        if self.print_statements: print(TAG + "object has been identified as a balloon or not")

my_tester = color_detector(False, True,'b',7,True)
my_tester.run_detector()
print(my_tester.average_distance)
print(my_tester.average_x_correct)
print(my_tester.average_y_correct)