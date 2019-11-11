"""
Simple way to control the torso through a ui
Author: Patrick Gmerek
"""
import sys
sys.path.append("../project_files/robot_drivers/")

import cv2 as cv
import time

import pwm_wrapper as pw
import hex_walker_driver_v2 as hwd
from hex_walker_constants import *


def main():
    torso = initialize_torso()
    slider_names = ["Waist",
                    "Right Tip Joint", "Right Mid Joint", "Right Rotary Joint",
                    "Left Tip Joint", "Left Mid Joint", "Left Rotary Joint"]
	# TODO: look up these limits, don't hard-code them
    slider_limits = [[60, 150],
                     [0, 180], [0, 180], [0, 180],
                     [0, 180], [0, 180], [0, 180]]
    window_name = "Hexapod Torso Control"
    cv.namedWindow(window_name)

    for slider, limits in zip(slider_names, slider_limits):
        cv.createTrackbar(slider, window_name, limits[0], limits[1], dummy)

    user_inputs = fetch_trackbar_pos(window_name, slider_names)

    torso[0].set_leg_position(Leg_Position(user_inputs[1], user_inputs[2], user_inputs[3]))
    torso[1].set_leg_position(Leg_Position(user_inputs[4], user_inputs[5], user_inputs[6]))
    torso[2].set_servo_angle(user_inputs[0])
    while True:
        previous_user_inputs = user_inputs
        user_inputs = fetch_trackbar_pos(window_name, slider_names)
        key = cv.waitKey(1) & 0xFF
        if key == ord("q"):  # Quit if the user presses "q"
            break
        if not compare_lists(user_inputs, previous_user_inputs):
            print("Values changed")
            torso[0].set_leg_position(Leg_Position(user_inputs[1], user_inputs[2], user_inputs[3]))
            torso[1].set_leg_position(Leg_Position(user_inputs[4], user_inputs[5], user_inputs[6]))
            torso[2].set_servo_angle(user_inputs[0])
    cv.destroyAllWindows()


def compare_lists(list1, list2):
    if not len(list1) == len(list1):
        return -1

    for i in range(0, len(list1)):
        if not list1[i] == list2[i]:
            return 0

    return 1


def fetch_trackbar_pos(window_name, slider_names):
    waist = cv.getTrackbarPos(slider_names[0], window_name)
    rr = cv.getTrackbarPos(slider_names[1], window_name)
    rm = cv.getTrackbarPos(slider_names[2], window_name)
    rt = cv.getTrackbarPos(slider_names[3], window_name)
    lr = cv.getTrackbarPos(slider_names[4], window_name)
    lm = cv.getTrackbarPos(slider_names[5], window_name)
    lt = cv.getTrackbarPos(slider_names[6], window_name)
    return [waist, rr, rm, rt, lr, lm, lt]


def dummy(x):
    return


def initialize_torso():
	pwm_bot = pw.Pwm_Wrapper(PWM_ADDR_BOTTOM, PWM_FREQ)
	rf = hwd.Leg(pwm_bot, LEG_PWM_CHANNEL[LEG_RF], LEG_RF) #0
	rm = hwd.Leg(pwm_bot, LEG_PWM_CHANNEL[LEG_RM], LEG_RM) #1
	rb = hwd.Leg(pwm_bot, LEG_PWM_CHANNEL[LEG_RB], LEG_RB) #2
	larm = hwd.Leg(pwm_bot, LEG_PWM_CHANNEL[ARM_L], ARM_L) #6
	rot = hwd.Rotator(pwm_bot, LEG_PWM_CHANNEL[WAIST], WAIST) #8

	pwm_top = pw.Pwm_Wrapper(PWM_ADDR_TOP, PWM_FREQ)
	lb = hwd.Leg(pwm_top, LEG_PWM_CHANNEL[LEG_LB], LEG_LB) #3
	lm = hwd.Leg(pwm_top, LEG_PWM_CHANNEL[LEG_LM], LEG_LM) #4
	lf = hwd.Leg(pwm_top, LEG_PWM_CHANNEL[LEG_LF], LEG_LF) #5
	rarm = hwd.Leg(pwm_top, LEG_PWM_CHANNEL[ARM_R], ARM_R) #7

	all = [rf, rm, rb, lb, lm, lf, larm, rarm, rot]
	
	# no need to create hex_walker or torso objects
	
    return [rarm, larm, rot]


if __name__ == '__main__':
    main()
