# TODO: add comments to document
# TODO: clean up code
# TODO: make code more readable? add more debug/visual features?

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
    #   (method) TAG: string that associates print statements with the method
    #   (class) self.print_statements: saves the input print_statements value as a class variable
    #   (class) self.which_color: saves the input which_color value as a class variable
    #   (class) self.pi_camera: saves the input pi_camera value as a class variable
    #   (class) self.headless_mode: saves the input headless value as a class variable
    #   (class) self.object_width_in: saves the input object_width value as a class variable
    #   (class) self.object_width_pixels: indicates the focal length of the camera in pixels (hard-coded for pi camera)
    #   (class) self.focal_length_pixels: indicates the focal length of the camera in inches
    def __init__(self, print_statements, headless, which_color, object_width, pi_camera):

        TAG = "INIT: "

        self.print_statements = print_statements
        self.which_color = which_color
        self.pi_camera = pi_camera
        self.headless_mode = headless
        self.object_width_in = object_width
        self.object_width_pixels = in_to_pixels(object_width)
        self.focal_length_pixels = 1126.85714  # for pi camera v2.1
        self.set_color_bounds()
        self.get_camera_properties()
        pwm_bot = pw.Pwm_Wrapper(PWM_ADDR_BOTTOM, PWM_FREQ)
        larm = hwd.Leg(pwm_bot, PWM_CHANNEL_ARRAY[ARM_L], ARM_L)  # 6
        rot = hwd.Rotator(pwm_bot, PWM_CHANNEL_ARRAY[WAIST], WAIST)  # 8
        pwm_top = pw.Pwm_Wrapper(PWM_ADDR_TOP, PWM_FREQ)
        rarm = hwd.Leg(pwm_top, PWM_CHANNEL_ARRAY[ARM_R], ARM_R)  # 7

        self.torso = hwd.Robot_Torso(rarm, larm, rot)

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
            camera = PiCamera()
            camera.resolution = (1080, 720)
            camera.framerate = 60
            rawCapture = PiRGBArray(camera, size=(1080, 720))

            for frame_value in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                frame = frame_value.array
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(hsv, self.lower_bound, self.upper_bound)
                counts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
                cv2.line(frame, (self.camera_center_x, self.camera_center_y - 10),
                         (self.camera_center_x, self.camera_center_y + 10), (0, 0, 255), 2)
                cv2.line(frame, (self.camera_center_x - 10, self.camera_center_y),
                         (self.camera_center_x + 10, self.camera_center_y), (0, 0, 255), 2)

                if len(counts) > 0:
                    total_area = max(counts, key=cv2.contourArea)
                    self.get_bounding_rect(total_area)
                    cv2.rectangle(frame, (self.rect_x_start, self.rect_y_start),
                                  (self.rect_x_start + self.rect_width, self.rect_y_start + self.rect_height),
                                  (0, 255, 0), 2)
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

        # if using a web camera
        else:
            cap = cv2.VideoCapture(0)

            while True:
                _, frame = cap.read()
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(hsv, self.lower_bound, self.upper_bound)
                counts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
                cv2.line(frame, (self.camera_center_x, self.camera_center_y - 10),
                         (self.camera_center_x, self.camera_center_y + 10), (0, 0, 255), 2)
                cv2.line(frame, (self.camera_center_x - 10, self.camera_center_y),
                         (self.camera_center_x + 10, self.camera_center_y), (0, 0, 255), 2)

                if len(counts) > 0:
                    total_area = max(counts, key=cv2.contourArea)
                    self.get_bounding_rect(total_area)
                    cv2.rectangle(frame, (self.rect_x_start, self.rect_y_start),
                                  (self.rect_x_start + self.rect_width, self.rect_y_start + self.rect_height),
                                  (0, 255, 0), 2)
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

            cap.release()
            cv2.destroyAllWindows()

        # TODO: return angle here?

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

        # TODO: is there a reason to return the values or can we just set them to the class?  could be easier?

        x_middle = int((self.rect_width) / 2 - 1 + self.rect_x_start)
        y_middle = int((self.rect_height) / 2 - 1 + self.rect_y_start)
        self.y_offset = self.camera_center_y - y_middle
        self.x_offset = self.camera_center_x - x_middle
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

        # TODO: check to see if angles are correct
        # TODO: convert angle to be between 0 and 180 degrees

        TAG = "GET_CORRECTION: "

        self.x_offset_angle = round(math.atan2(self.x_offset, self.distance_to_object) * (180 / math.pi), 2)
        self.y_offset_angle = round(math.atan2(self.y_offset, self.distance_to_object) * (180 / math.pi), 2)
        offset_string = "X: {} | Y: {}".format(self.x_offset_angle, self.y_offset_angle)

        if self.print_statements: print(TAG + "correct angles have been calculated")

        return offset_string

    # check_balloon method
    #
    # DESCRIPTION:
    #   Determines if the identified object has the characteristics of a balloon.
    #
    # ATTRIBUTES:
    #   (method) TAG: string that associates print statements with the method
    #   (method) percent_difference: the difference in size between the height and width of the object
    def check_balloon(self):

        # TODO: do we need this? should we add more checking parameters?

        TAG = "CHECK_BALLOON: "

        percent_difference = abs(self.rect_width - self.rect_height) / 100

        if percent_difference > 0.6:
            print("not balloon")
        else:
            print("balloon")

        if self.print_statements: print(TAG + "object has been identified as a balloon or not")

    def convert_angle(self):
        max_angle = math.atan2(self.camera_height_pixels,self.distance_to_object)*(180 / math.pi)

        # x angle: negative = right, positive = left
        # y angle: positive = up, negative = down

        # TODO: horizontal angle is from 30 to 150 not 0 to 180, possibly some calibration is in store?
        self.horizontal_correction = 90 - self.average_x_correct
        self.vertical_correction = 90 + (self.average_y_correct)*(90/max_angle)

        if 30 >= self.horizontal_correction:
            self.horizontal_correction = 30
        elif self.horizontal_correction >= 150:
            self.horizontal_correction = 150


my_tester = color_detector(False, True, 'b', 7, True)
my_tester.run_detector()
