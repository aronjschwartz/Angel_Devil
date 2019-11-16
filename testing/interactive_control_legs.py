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

all_legs = None
slider_names = ["Which Leg/Group", "Enable", 
				"Tip Joint", "Mid Joint", "Rot Joint"]
# first is init, second is max (min is always 0)
slider_limits = [[0, 10], [0,1], 
				[0, 180], [90, 180], [90, 180]]
window_name = "Hexapod Leg Control"

# TODO: leg groups

def main():
	global all_legs
	all_legs = initialize_legs()
	cv.namedWindow(window_name)

	cv.createTrackbar(slider_names[0], window_name, slider_limits[0][0], slider_limits[0][1], changeleg)
	for slider, limits in zip(slider_names[1:], slider_limits[1:]):
		cv.createTrackbar(slider, window_name, limits[0], limits[1], dummy)

	user_inputs = fetch_trackbar_pos(window_name, slider_names)
	all_legs[user_inputs[0]].set_leg_position(Leg_Position(user_inputs[2], user_inputs[3], user_inputs[4]))
	while True:
		previous_user_inputs = user_inputs
		user_inputs = fetch_trackbar_pos(window_name, slider_names)
		key = cv.waitKey(1) & 0xFF
		time.sleep(0.05) # Our poor processor....
		if key == ord("q"): # Quit if the user presses "q"
			break
		if not compare_lists(user_inputs, previous_user_inputs):
			# if the enable bar is set:
			if user_inputs[1] == 1:
				print("Values changed")
				newleg = Leg_Position(user_inputs[2], user_inputs[3], user_inputs[4])
				if user_inputs[0] == 6:
					# all legs at once
					for leg in [all_legs[n] for n in GROUP_ALL_LEGS]:
						leg.set_leg_position(newleg)
				elif user_inputs[0] == 7:
					# left legs
					for leg in [all_legs[n] for n in GROUP_LEFT_LEGS]:
						leg.set_leg_position(newleg)
				elif user_inputs[0] == 8:
					# right legs
					for leg in [all_legs[n] for n in GROUP_RIGHT_LEGS]:
						leg.set_leg_position(newleg)
				elif user_inputs[0] == 9:
					# left tri
					for leg in [all_legs[n] for n in GROUP_LEFT_TRI]:
						leg.set_leg_position(newleg)
				elif user_inputs[0] == 10:
					# right tri
					for leg in [all_legs[n] for n in GROUP_RIGHT_TRI]:
						leg.set_leg_position(newleg)
				else:
					all_legs[user_inputs[0]].set_leg_position(newleg)
	cv.destroyAllWindows()


def compare_lists(list1, list2):
	if not len(list1) == len(list1):
		return -1

	for i in range(0, len(list1)):
		if not list1[i] == list2[i]:
			return 0

	return 1


def fetch_trackbar_pos(window_name, slider_names):
	r = []
	for name in slider_names:
		r.append(cv.getTrackbarPos(name, window_name))
	return r

def changeleg(x):
	print("change leg")
	# function called when leg is changed
	# if x == 6:
	if x >= 6: # temp code
		# if x == 6, then selecting "all legs"...
		# set the "enable" trackbar to 0
		cv.setTrackbarPos(slider_names[1], window_name, 0)
		# TODO: calculate average for each joint
		# for leg in [all_legs[n] for n in GROUP_ALL_LEGS]:
			# leg.curr_servo_angle
		# for now, set to defaults
		cv.setTrackbarPos(slider_names[2], window_name, 0)
		cv.setTrackbarPos(slider_names[3], window_name, 90)
		cv.setTrackbarPos(slider_names[4], window_name, 90)
	# elif x == 7:
		# # left legs
		# for leg in [all_legs[n] for n in GROUP_LEFT_LEGS]:
			# leg.set_leg_position(newleg)
	# elif x == 8:
		# # right legs
		# for leg in [all_legs[n] for n in GROUP_RIGHT_LEGS]:
			# leg.set_leg_position(newleg)
	# elif x == 9:
		# # left tri
		# for leg in [all_legs[n] for n in GROUP_LEFT_TRI]:
			# leg.set_leg_position(newleg)
	# elif x == 10:
		# # right tri
		# for leg in [all_legs[n] for n in GROUP_RIGHT_TRI]:
			# leg.set_leg_position(newleg)
	else:
		# set the "enable" trackbar to 1
		cv.setTrackbarPos(slider_names[1], window_name, 1)
		# lookup current angle values of leg and set trackbars to reflect that
		curr = all_legs[x].curr_servo_angle
		cv.setTrackbarPos(slider_names[2], window_name, curr[TIP_SERVO])
		cv.setTrackbarPos(slider_names[3], window_name, curr[MID_SERVO])
		cv.setTrackbarPos(slider_names[4], window_name, curr[ROT_SERVO])
	

def dummy(x):
	return


def initialize_legs():
	global all_legs
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
