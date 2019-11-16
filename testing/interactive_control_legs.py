"""
Simple way to control each leg through a ui
Author: Patrick Gmerek
"""
import sys
sys.path.append("../project_files/robot_drivers/")

import cv2 as cv
import time

import pwm_wrapper as pw
import hex_walker_driver_v2 as hwd
from hex_walker_constants import *
from leg_data import *


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
    pwm_bot = pw.Pwm_Wrapper(PWM_ADDR_BOTTOM, PWM_FREQ)
    rf = hwd.Leg(pwm_bot, PWM_CHANNEL_ARRAY[LEG_RF], LEG_RF) #0
    rm = hwd.Leg(pwm_bot, PWM_CHANNEL_ARRAY[LEG_RM], LEG_RM) #1
    rb = hwd.Leg(pwm_bot, PWM_CHANNEL_ARRAY[LEG_RB], LEG_RB) #2
    larm = hwd.Leg(pwm_bot, PWM_CHANNEL_ARRAY[ARM_L], ARM_L) #6
    rot = hwd.Rotator(pwm_bot, PWM_CHANNEL_ARRAY[WAIST], WAIST) #8

    pwm_top = pw.Pwm_Wrapper(PWM_ADDR_TOP, PWM_FREQ)
    lb = hwd.Leg(pwm_top, PWM_CHANNEL_ARRAY[LEG_LB], LEG_LB) #3
    lm = hwd.Leg(pwm_top, PWM_CHANNEL_ARRAY[LEG_LM], LEG_LM) #4
    lf = hwd.Leg(pwm_top, PWM_CHANNEL_ARRAY[LEG_LF], LEG_LF) #5
    rarm = hwd.Leg(pwm_top, PWM_CHANNEL_ARRAY[ARM_R], ARM_R) #7

    all = [rf, rm, rb, lb, lm, lf, larm, rarm, rot]
    
    # no need to create hex_walker or torso objects
    
    return [rf, rm, rb, lb, lm, lf]


if __name__ == '__main__':
    main()
