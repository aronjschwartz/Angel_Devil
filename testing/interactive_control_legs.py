"""
Simple way to control each leg through a ui
Author: Patrick Gmerek
"""
import sys
sys.path.append("../project_files/robot_drivers/")

import cv2 as cv
import time

import pwm_wrapper
from hex_walker_driver_v2 import *
from hex_walker_constants import *


def main():
    all_legs = initialize_legs()
    slider_names = ["Leg", "Rotary Joint", "Mid Joint", "Tip Joint"]
	# TODO: look up these limits, don't hard-code them
    slider_limits = [[1, 5], [0, 180], [45, 180], [90, 270]]
    window_name = "Hexapod Leg Control"
    cv.namedWindow(window_name)

    for slider, limits in zip(slider_names, slider_limits):
        cv.createTrackbar(slider, window_name, limits[0], limits[1], dummy)

    user_inputs = fetch_trackbar_pos(window_name, slider_names)
    all_legs[user_inputs[0]].set_leg_position(Leg_Position(user_inputs[1], user_inputs[2], user_inputs[3]))
    while True:
        previous_user_inputs = user_inputs
        user_inputs = fetch_trackbar_pos(window_name, slider_names)
        key = cv.waitKey(1) & 0xFF
        time.sleep(0.05)    # Our poor processor....
        if key == ord("q"):  # Quit if the user presses "q"
            break
        if not compare_lists(user_inputs, previous_user_inputs):
            print("Values changed")
            all_legs[user_inputs[0]].set_leg_position(Leg_Position(user_inputs[1], user_inputs[2], user_inputs[3]))
    cv.destroyAllWindows()


def compare_lists(list1, list2):
    if not len(list1) == len(list1):
        return -1

    for i in range(0, len(list1)):
        if not list1[i] == list2[i]:
            return 0

    return 1


def fetch_trackbar_pos(window_name, slider_names):
    leg_num = cv.getTrackbarPos(slider_names[0], window_name)
    rot_angle = cv.getTrackbarPos(slider_names[1], window_name)
    mid_angle = cv.getTrackbarPos(slider_names[2], window_name)
    tip_angle = cv.getTrackbarPos(slider_names[3], window_name)
    return [leg_num, rot_angle, mid_angle, tip_angle]


def dummy(x):
    return


def initialize_legs():
	pwm_bot = pwm_wrapper.Pwm_Wrapper(PWM_ADDR_BOTTOM, PWM_FREQ)
	rf = Leg(pwm_bot, LEG_PWM_CHANNEL[LEG_RF], LEG_RF)
	rm = Leg(pwm_bot, LEG_PWM_CHANNEL[LEG_RM], LEG_RM)
	rb = Leg(pwm_bot, LEG_PWM_CHANNEL[LEG_RB], LEG_RB)
	larm = Leg(pwm_bot, LEG_PWM_CHANNEL[ARM_L], ARM_L)
	rot = Rotator(pwm_bot, LEG_PWM_CHANNEL[WAIST], WAIST)

	pwm_top = pwm_wrapper.Pwm_Wrapper(PWM_ADDR_TOP, PWM_FREQ)
	lb = Leg(pwm_top, LEG_PWM_CHANNEL[LEG_LB], LEG_LB)
	lm = Leg(pwm_top, LEG_PWM_CHANNEL[LEG_LM], LEG_LM)
	lf = Leg(pwm_top, LEG_PWM_CHANNEL[LEG_LF], LEG_LF)
	rarm = Leg(pwm_top, LEG_PWM_CHANNEL[ARM_R], ARM_R)

	all = [rf, rm, rb, lb, lm, lf, larm, rarm, rot]
	
	# no need to create hex_walker or torso objects
	
    return [rf, rm, rb, lb, lm, lf]


if __name__ == '__main__':
    main()
