import sys
sys.path.append("../project_files/robot_drivers/")

import numpy as np
import cv2
import math
from picamera.array import PiRGBArray
from picamera import PiCamera
import pwm_wrapper as pw
import hex_walker_driver_v2 as hwd
from hex_walker_constants import *

# in_to_pixels function
# DESCRIPTION:
#   Converts a measurement in units of inches and converts to pixels.
# ATTRIBUTES:
#   (input) inches: numerical value indicating number of inches
#   (return) pixels: amount of pixels in provided inches measurement

def in_to_pixels(inches):
    # convert from inches to centimeters to pixels in a 72 DPI image (pi camera DPI)
    pixels = (inches) * (2.54) * (28.346456693)
    # return the number of pixels in given length
    return pixels

class color_detector:
    # __init__ method
    #
    # DESCRIPTION:
    #   Initialization method for the color_detector class.
    #
    # ATTRIBUTES:
    #   (input) print_statements:   boolean value that indicates if class print statements will be displayed
    #                               (True = print statements visible, False = print statements hidden)
    #   (input) headless:   boolean value that indicates whether or not images/video feeds will be shown on the display
    #                       (True = feeds are shown, False = feeds are hidden)
    #   (input) which_color:    string value that indicates which color the color detector will be searching for.
    #                           ('r' = red, 'b' = blue)
    #   (input) object_width: The width of the object you are searching for in inches
    #   (input) pi_camera:  boolean value that indicates whether a pi camera is being used or a webcam is being used.
    #                       (True = pi camera v2.1, False = webcam)
    #   (input) testing: boolean to indicate if the code is for testing/calibration purposes, will only run torso
    #                    and arms (True = only run torso and arms for testing, False = running with game or full robot)
    #   (method) TAG: string that associates print statements with the method
    #   (class) self.print_statements: saves the input print_statements value as a class variable
    #   (class) self.which_color: saves the input which_color value as a class variable
    #   (class) self.pi_camera: saves the input pi_camera value as a class variable
    #   (class) self.headless_mode: saves the input headless value as a class variable
    #   (class) self.object_width_in: saves the input object_width value as a class variable
    #   (class) self.object_width_pixels: indicates the focal length of the camera in pixels (hard-coded for pi camera)
    #   (class) self.focal_length_pixels: indicates the focal length of the camera in inches
    def __init__(self, print_statements, headless, which_color, object_width, pi_camera, testing, hex_walker_object):

        TAG = "INIT: "

        # setting class variables to the initialization input variables
        self.print_statements = print_statements
        self.which_color = which_color
        self.pi_camera = pi_camera
        self.testing = testing
        self.headless_mode = headless
        self.object_width_in = object_width
        self.object_width_pixels = in_to_pixels(object_width)
        self.focal_length_pixels = 1126.85714  # currently setup for pi camera v2.1
        self.set_color_bounds()
        self.get_camera_properties()
        self.torso = hex_walker_object

        # if only using the torso and arms for testing reasons
        # if self.testing:
        #     # initialize arms and torso
        #     pwm_bot = pw.Pwm_Wrapper(PWM_ADDR_BOTTOM, PWM_FREQ)
        #     larm = hwd.Leg(pwm_bot, PWM_CHANNEL_ARRAY[ARM_L], ARM_L)
        #     rot = hwd.Rotator(pwm_bot, PWM_CHANNEL_ARRAY[WAIST], WAIST)
        #     pwm_top = pw.Pwm_Wrapper(PWM_ADDR_TOP, PWM_FREQ)
        #     rarm = hwd.Leg(pwm_top, PWM_CHANNEL_ARRAY[ARM_R], ARM_R)
        #     self.torso = hwd.Robot_Torso(rarm, larm, rot)

        if self.print_statements: print(TAG + "color_detector class successfully created")

    # set_color_bounds method
    #
    # DESCRIPTION:
    #   Using the color specified from input in the __init__ method set the upper and lower bounds to specify which
    #   color the color detector is identifying.
    #
    # ATTRIBUTES:
    #   (method) TAG: string that associates print statements with the method
    #   (method) lower_color:   string value of the lowercase value of color string given as an input in
    #                           the __init__ method
    #   (method) COLOR: string value used in a print statement indicating which color is being identified
    #   (class) self.lower_bound:   array that holds the RGB values indicating the color of the lower bounds of the
    #                               color detector
    #   (class) self.upper_bound:   array that holds the RGB values indicating the color of the upper bounds of the
    #                               color detector
    def set_color_bounds(self):

        TAG = "SET_COLOR_BOUNDS: "

        # set the color string to be all lowercase so the user can use uppercase or lowercase arguments
        lower_color = self.which_color.lower()

        # if user wants to detect red
        if lower_color == 'r':
            # set the color bounds to be red
            self.lower_bound = np.array([161, 155, 84])
            self.upper_bound = np.array([179, 255, 255])
            # string used in print statement
            COLOR = "red"
        # if user wants to detect blue
        elif lower_color == 'b':
            # set the color bounds to be blue
            self.lower_bound = np.array([100, 50, 50])
            self.upper_bound = np.array([130, 255, 255])
            # string used in print statement
            COLOR = "blue"

        if self.print_statements: print(TAG + "color bounds set to " + COLOR)

    # get_camera_properties method
    #
    # DESCRIPTION:
    #   Obtain the camera height and width in pixels and then determine where the center of the camera is located.
    #
    # ATTRIBUTES:
    #   (method) TAG: string that associates print statements with the method
    #   (method) camera: OpenCV camera object
    #   (method) frame: holds the image that the camera has captured
    #   (class) self.camera_height_pixels: height of the camera in pixels
    #   (class) self.camera_width_pixels: width of the camera in pixels
    #   (class) self.camera_center_x: x coordinate of for the center of the camera's FOV
    #   (class) self.camera_center_y: y coordinate of for the center of the camera's FOV
    def get_camera_properties(self):

        TAG = "GET_CAMERA_STATS: "

        # if using a PI camera
        if self.pi_camera:
            # set camera dimensions
            self.camera_height_pixels = 720
            self.camera_width_pixels = 1080
            # set middle of camera
            self.camera_center_x = int((self.camera_width_pixels) / 2 - 1)
            self.camera_center_y = int((self.camera_height_pixels) / 2 - 1)
        # if using a web camera
        else:
            # set camera dimensions
            camera = cv2.VideoCapture(0)
            ret, frame = camera.read()
            self.camera_height_pixels = int(frame.shape[0])
            self.camera_width_pixels = int(frame.shape[1])
            # set middle of camera
            self.camera_center_x = int((self.camera_width_pixels) / 2 - 1)
            self.camera_center_y = int((self.camera_height_pixels) / 2 - 1)
            camera.release()

        if self.print_statements: print(TAG + "camera properties updated")

    # run_detector method
    #
    # DESCRIPTION:
    #   Identifies an image of the specified color and then calculates how far the object is away and how far the object
    #   is from the center of the image.
    #
    # ATTRIBUTES:
    #   (method) TAG: string that associates print statements with the method
    #   (method) count: how many times the objects location has been calculated
    #   (method) distances: list of distances used to calculate the average distance to an object
    #   (method) x_correct: list of angels used to calculate the average angle the object is from the center of the
    #                       object in the x direction
    #   (method) y_correct: list of angels used to calculate the average angle the object is from the center of the
    #                       object in the y direction
    #   (method) camera: pi camera object
    #   (method) raw_capture: image captured from pi camera
    #   (method) frame: RGB image from camera
    #   (method) hsv: hsv image of captured RGB image
    #   (method) mask: color mask using color bounds and hsv image
    #   (method) counts: the total pixels of a bounding rectangle in pixels
    #   (method) total_area: the total area of the bounding rectangle given the its pixel count
    #   (method) center_rect: coordinates of the center of the bounding rectangle
    #   (method) cap: OpenCV camera object for webcam
    #   (class) average_distance: the average distance to the object in pixels
    #   (class) average_x_correct: the average x correction angle in degrees
    #   (class) average_y_correct: the average y correction angle in degrees
    def run_detector(self):

        # TODO: should we take the average of all the measurements? (n=10) or throw out some of the values? (like min and max values)

        TAG = "RUN_DETECTOR: "

        count = 1
        distances = []
        x_correct = []
        y_correct = []

        # if using a PI camera
        if self.pi_camera:
            # start capturing image frames using the pi camera
            camera = PiCamera()
            camera.resolution = (1080, 720)
            camera.framerate = 60
            rawCapture = PiRGBArray(camera, size=(1080, 720))

            # for each frame
            for frame_value in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                # convert image to array
                frame = frame_value.array
                # convert from BGR to HSV format
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                # only keep the colors within the specified color range
                mask = cv2.inRange(hsv, self.lower_bound, self.upper_bound)
                # getting how many pixels are within color range
                counts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
                # indicating the middle of the camera on the image
                cv2.line(frame, (self.camera_center_x, self.camera_center_y - 10),
                         (self.camera_center_x, self.camera_center_y + 10), (0, 0, 255), 2)
                cv2.line(frame, (self.camera_center_x - 10, self.camera_center_y),
                         (self.camera_center_x + 10, self.camera_center_y), (0, 0, 255), 2)
                # if there is at least one colored pixel
                if len(counts) > 0:
                    # get the area of the rectangle using contours
                    total_area = max(counts, key=cv2.contourArea)
                    # get the bounds of the rectangle
                    self.get_bounding_rect(total_area)
                    # draw rectangle on frame
                    cv2.rectangle(frame, (self.rect_x_start, self.rect_y_start),
                                  (self.rect_x_start + self.rect_width, self.rect_y_start + self.rect_height),
                                  (0, 255, 0), 2)
                    # calculate how far rectangle is from center
                    center_rect = self.distance_to_center()
                    # draw line on frame between center of rectangle and center of frame
                    cv2.line(frame, (center_rect[0], center_rect[1]), (self.camera_center_x, self.camera_center_y),
                             (0, 0, 255), 2)
                    # draw circle on frame which indicates center of rectangle
                    frame = cv2.circle(frame, (center_rect[0], center_rect[1]), 5, (255, 0, 0), -1)
                    # calculate how far object is away
                    self.distance_camera_to_object()
                    # put text on frame indicating distance and correction angles
                    cv2.putText(frame, "Distance: " + str(round(self.distance_to_object, 2)) + " in.", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                    cv2.putText(frame, self.get_correction(), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                                cv2.LINE_AA)
                    # take average distance, x correction angles and y correction angles of 10 different frame
                    if 10 < count:
                        self.average_distance = sum(distances) / len(distances)
                        self.average_x_correct = sum(x_correct) / len(x_correct)
                        self.average_y_correct = sum(y_correct) / len(y_correct)
                        self.convert_angle()
                        break
                    else:
                        distances.append(self.distance_to_object)
                        x_correct.append(self.x_offset_angle)
                        y_correct.append(self.y_offset_angle)
                        count = count + 1

                # if not in headless mode show the camera feed on screen
                if not self.headless_mode:
                    cv2.imshow("Frame", frame)

                rawCapture.truncate(0)

        # if using a webcam
        else:
            cap = cv2.VideoCapture(0)

            while True:
                # read a frame
                _, frame = cap.read()
                # convert frame from BRG to HSV
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                # mask frame for color
                mask = cv2.inRange(hsv, self.lower_bound, self.upper_bound)
                # determine how many pixels are within color range
                counts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
                # indicate where center of the image is
                cv2.line(frame, (self.camera_center_x, self.camera_center_y - 10),
                         (self.camera_center_x, self.camera_center_y + 10), (0, 0, 255), 2)
                cv2.line(frame, (self.camera_center_x - 10, self.camera_center_y),
                         (self.camera_center_x + 10, self.camera_center_y), (0, 0, 255), 2)
                # if there is a colored object within bounds
                if len(counts) > 0:
                    # get area of object
                    total_area = max(counts, key=cv2.contourArea)
                    # determine bounds of rectangle
                    self.get_bounding_rect(total_area)
                    # draw rectangle on frame outlining object
                    cv2.rectangle(frame, (self.rect_x_start, self.rect_y_start),
                                  (self.rect_x_start + self.rect_width, self.rect_y_start + self.rect_height),
                                  (0, 255, 0), 2)
                    # calculate the center of the object
                    center_rect = self.distance_to_center()
                    # draw line on frame from center of image to center of rectangle
                    cv2.line(frame, (center_rect[0], center_rect[1]), (self.camera_center_x, self.camera_center_y),
                             (0, 0, 255), 2)
                    # draw circle to indicate center of rectangle
                    frame = cv2.circle(frame, (center_rect[0], center_rect[1]), 5, (255, 0, 0), -1)
                    # calculate distance to object
                    self.distance_camera_to_object()
                    # put text on frame indicating distance and correction angles
                    cv2.putText(frame, "Distance: " + str(round(self.distance_to_object, 2)) + " in.", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                    cv2.putText(frame, self.get_correction(), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                                cv2.LINE_AA)
                    # take average distance, x correction angles and y correction angles of 10 different frame
                    if 10 < count:
                        self.average_distance = sum(distances) / len(distances)
                        self.average_x_correct = sum(x_correct) / len(x_correct)
                        self.average_y_correct = sum(y_correct) / len(y_correct)
                        break
                    else:
                        distances.append(self.distance_to_object)
                        x_correct.append(self.x_offset_angle)
                        y_correct.append(self.y_offset_angle)
                        count = count + 1

                # if not in headless mode show the camera feed on screen
                if not self.headless_mode:
                    cv2.imshow('frame', frame)

            # release cammera
            cap.release()
            cv2.destroyAllWindows()

        # if testing, send commands to torso
        if self.testing:
            # use arm depending on horizontal correctino angle
            if self.horizontal_correction > 90:
                #self.torso.right_arm.set_servo_angle(self.vertical_correction, ROT_SERVO)
                self.torso.left_arm.set_servo_angle(90, ROT_SERVO)
                self.torso.left_arm.set_servo_angle(45, MID_SERVO)
                self.torso.left_arm.set_servo_angle(90, TIP_SERVO)
                self.torso.right_arm.set_servo_angle(90, ROT_SERVO)
                self.torso.right_arm.set_servo_angle(90, MID_SERVO)
                self.torso.right_arm.set_servo_angle(90, TIP_SERVO)
                self.torso.rotator.set_servo_angle(self.horizontal_correction, WAIST_SERVO)
            elif self.horizontal_correction < 90:
                #self.torso.right_arm.set_servo_angle(self.vertical_correction, ROT_SERVO)
                self.torso.right_arm.set_servo_angle(90, ROT_SERVO)
                self.torso.right_arm.set_servo_angle(45, MID_SERVO)
                self.torso.right_arm.set_servo_angle(90, TIP_SERVO)
                self.torso.left_arm.set_servo_angle(90, ROT_SERVO)
                self.torso.left_arm.set_servo_angle(90, MID_SERVO)
                self.torso.left_arm.set_servo_angle(90, TIP_SERVO)
                self.torso.rotator.set_servo_angle(self.horizontal_correction, WAIST_SERVO)

        if self.print_statements: print(TAG + "detector has finished")

    # get_bounding_rect method
    #
    # DESCRIPTION:
    #   Obtain the bounding rectangle of an object given it's area.
    #
    # ATTRIBUTES:
    #   (input) area: the area of an object in pixels
    #   (method) TAG: string that associates print statements with the method
    #   (class) self.rect_x_start: the x coordinate of the top left point of the bounding rectangle
    #   (class) self.rect_y_start: the y coordinate of the top left point of the bounding rectangle
    #   (class) self.rect_width: the horizontal width of the rectangle in pixels
    #   (class) self.rect_height: the vertical height of the rectangle in pixels
    def get_bounding_rect(self, area):

        TAG = "GET_BOUNDING_REC: "

        # get bounding rectangle parameters and save within instance of class
        (self.rect_x_start, self.rect_y_start, self.rect_width, self.rect_height) = cv2.boundingRect(area)

        if self.print_statements: print(TAG + "obtained bounding rectangle")

    # distance_to_center method
    #
    # DESCRIPTION:
    #   Calculates the distance from the center of the camera's FOV to the center of the identified object.
    #
    # ATTRIBUTES:
    #   (method) TAG: string that associates print statements with the method
    #   (method) x_middle: x coordinate that corresponds to the middle of the identified object
    #   (method) y_middle: y coordinate that corresponds to the middle of the identified object
    #   (class) self.x_offset:  distance between the center of the camera and the center of the identified object in the
    #                           x coordinate plane
    #   (class) self.y_offset:  distance between the center of the camera and the center of the identified object in the
    #                           y coordinate plane
    #   (return) center_rect: list that holds the object's center point x and y coordinates
    def distance_to_center(self):

        TAG = "DISTANCE_TO_CENTER: "
        center_rect = []

        # get the x coordinate of the middle of middle of the rectangle
        x_middle = int((self.rect_width) / 2 - 1 + self.rect_x_start)
        # get the y coordinate of the middle of middle of the rectangle
        y_middle = int((self.rect_height) / 2 - 1 + self.rect_y_start)
        # get the vertical offset between center of image and center of rectangle
        self.y_offset = self.camera_center_y - y_middle
        # get the horizontal offset between center of image and center of rectangle
        self.x_offset = self.camera_center_x - x_middle
        # package middle values into list for easy use later
        center_rect.append(x_middle)
        center_rect.append(y_middle)

        if self.print_statements: print(
            TAG + "distance between center of camera FOV and center of object has been calculated")

        return center_rect

    # distance_camera_to_object method
    #
    # DESCRIPTION:
    #   Calculates the distance from the camera to an identified object.
    #
    # ATTRIBUTES:
    #   (method) TAG: string that associates print statements with the method
    #   (class) self.distance_to_object: distance in inches from camera to identified object
    def distance_camera_to_object(self):

        TAG = "DISTANCE_CAMERA_TO_OBJECT: "

        # distance to object in inches
        self.distance_to_object = ((self.object_width_in) * (self.focal_length_pixels)) / (self.rect_width)

        if self.print_statements: print(TAG + "distance from camera to object has been determined")

    # get_correction method
    #
    # DESCRIPTION:
    #   Determines the angle in both the x and y direction that the object is from the center of the camera.
    #
    # ATTRIBUTES:
    #   (method) TAG: string that associates print statements with the method
    #   (class) self.x_offset_angle:    angle in degrees indicating how far off the object is from the center of the
    #                                   camera in the x coordinate plane
    #   (class) self.y_offset_angle:    angle in degrees indicating how far off the object is from the center of the
    #                                   camera in the y coordinate plane
    #   (return) offset_string: formatted string that includes the offset angles
    def get_correction(self):

        TAG = "GET_CORRECTION: "

        # calculate how the angle from the the center of the image to the center of the rectangle in the x direction
        self.x_offset_angle = round(math.atan2(self.x_offset, self.distance_to_object) * (180 / math.pi), 2)
        # calculate how the angle from the the center of the image to the center of the rectangle in the y direction
        self.y_offset_angle = round(math.atan2(self.y_offset, self.distance_to_object) * (180 / math.pi), 2)
        offset_string = "X: {} | Y: {}".format(self.x_offset_angle, self.y_offset_angle)

        if self.print_statements: print(TAG + "correct angles have been calculated")

        return offset_string

    # convert_angle method
    #
    # DESCRIPTION:
    #   Converts the correction angle determined in the get_correction method to an angle value that corresponds with
    #   the hexapod drivers.
    #
    # ATTRIBUTES:
    #   (method) TAG: string that associates print statements with the method
    #   (function) max_angle: the vertical angle from the center of the image to the top of the image
    #   (class) self.horizontal_correction: converted horizontal angle that works with robot movement drivers
    #   (class) self.vertical_correction: converted vertical angle that works with robot movement drivers
    def convert_angle(self):

        TAG = "CONVERT_ANGLE: "

        # calculate angle from middle of image to top of image
        max_angle = math.atan2(self.camera_height_pixels,self.distance_to_object)*(180 / math.pi)
        # correct vertical angle
        self.horizontal_correction = 90 - self.average_x_correct
        # correct horizontal angle
        self.vertical_correction = 90 + (self.average_y_correct)*(90/max_angle)

        # horizontal angle is limited by torso rotation which is between 30 and 150
        if 30 >= self.horizontal_correction:
            self.horizontal_correction = 30
        elif self.horizontal_correction >= 150:
            self.horizontal_correction = 150

        if self.print_statements: print(TAG + "converted correction angle to angle recognized by hexapod drivers")


# my_tester = color_detector(False, True, 'b', 7, True, True, walker_object)
# my_tester.run_detector()
