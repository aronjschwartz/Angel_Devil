"""
Simple way to control the torso through a ui
Author: Patrick Gmerek
v2: Brian Henson

Not sure where the extra invisible buttons come from, or what they do, or the big black rectangle... but at least
the sliders are working as intended. Looks pretty messy, not at all like the screenshot in the docs, but it works.

Changes to the sliders are immediately sent to the relevant servos.

The WAIST servo can only move from [30-150] but the slider range must start at 0 so I expanded the slider to [0-180].

This uses the non-threading direct-set functions of the Leg objects.
"""
import sys
sys.path.append("../project_files/robot_drivers/")

import cv2 as cv
import time

import pwm_wrapper as pw
import hex_walker_driver_v2 as hwd
from hex_walker_constants import *
from posedata_leg import *


def main():
	torso = initialize_torso()
	slider_names = ["Waist",
					"Right Tip Joint", "Right Mid Joint", "Right Rotary Joint",
					"Left Tip Joint", "Left Mid Joint", "Left Rotary Joint"]
	# note: min is always 0. below values are [initial, max]
	slider_limits = [[90, 180],
					 [90, 180], [90, 180], [90, 180],
					 [90, 180], [90, 180], [90, 180]]
	window_name = "Hexapod Torso Control"
	cv.namedWindow(window_name)

	for slider, limits in zip(slider_names, slider_limits):
		cv.createTrackbar(slider, window_name, limits[0], limits[1], dummy)

	user_inputs = fetch_trackbar_pos(window_name, slider_names)

	torso[1].set_leg_position(Leg_Position(user_inputs[1+ROT_SERVO], user_inputs[1+MID_SERVO], user_inputs[1+TIP_SERVO]))
	torso[0].set_leg_position(Leg_Position(user_inputs[4+ROT_SERVO], user_inputs[4+MID_SERVO], user_inputs[4+TIP_SERVO]))
	torso[2].set_servo_angle(user_inputs[0], WAIST_SERVO)
	while True:
		previous_user_inputs = user_inputs
		user_inputs = fetch_trackbar_pos(window_name, slider_names)
		key = cv.waitKey(1) & 0xFF
		time.sleep(0.05)  # 20Hz refresh rate
		if key == ord("q"):  # Quit if the user presses "q"
			break
		if not compare_lists(user_inputs, previous_user_inputs):
			print("Values changed")
			torso[1].set_leg_position(Leg_Position(user_inputs[1 + ROT_SERVO], user_inputs[1 + MID_SERVO], user_inputs[1 + TIP_SERVO]))
			torso[0].set_leg_position(Leg_Position(user_inputs[4 + ROT_SERVO], user_inputs[4 + MID_SERVO], user_inputs[4 + TIP_SERVO]))
			torso[2].set_servo_angle(user_inputs[0], WAIST_SERVO)
	cv.destroyAllWindows()


def compare_lists(list1, list2):
	if not len(list1) == len(list1):
		return -1
	for i in range(0, len(list1)):
		if not list1[i] == list2[i]:
			return 0
	return 1


def fetch_trackbar_pos(mwindow_name, mslider_names):
	r = []
	for name in mslider_names:
		r.append(cv.getTrackbarPos(name, mwindow_name))
	return r


def dummy(x):
	return


def initialize_torso():
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

	return [larm, rarm, rot]


if __name__ == '__main__':
	main()
