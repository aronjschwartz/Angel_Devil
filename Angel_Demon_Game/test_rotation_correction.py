# **********************************************************************************************
# *																							  *
# *	   Program: Implements the Angel/Demon game with a quantum-based decision making		  *
# *																							  *
# **********************************************************************************************

import sys

sys.path.append("../project_files/robot_drivers/")

import rotation_corrector
import forward_back_corrector

import pwm_wrapper as pw
import hex_walker_driver_v2 as hwd
from hex_walker_constants import *

pwm_bot = pw.Pwm_Wrapper(PWM_ADDR_BOTTOM, PWM_FREQ)
rf = hwd.Leg(pwm_bot, PWM_CHANNEL_ARRAY[LEG_RF], LEG_RF)  # 0
rm = hwd.Leg(pwm_bot, PWM_CHANNEL_ARRAY[LEG_RM], LEG_RM)  # 1
rb = hwd.Leg(pwm_bot, PWM_CHANNEL_ARRAY[LEG_RB], LEG_RB)  # 2
larm = hwd.Leg(pwm_bot, PWM_CHANNEL_ARRAY[ARM_L], ARM_L)  # 6
rot = hwd.Rotator(pwm_bot, PWM_CHANNEL_ARRAY[WAIST], WAIST)  # 8

pwm_top = pw.Pwm_Wrapper(PWM_ADDR_TOP, PWM_FREQ)
lb = hwd.Leg(pwm_top, PWM_CHANNEL_ARRAY[LEG_LB], LEG_LB)  # 3
lm = hwd.Leg(pwm_top, PWM_CHANNEL_ARRAY[LEG_LM], LEG_LM)  # 4
lf = hwd.Leg(pwm_top, PWM_CHANNEL_ARRAY[LEG_LF], LEG_LF)  # 5
rarm = hwd.Leg(pwm_top, PWM_CHANNEL_ARRAY[ARM_R], ARM_R)  # 7

# create the hex walker
hex_walker = hwd.Hex_Walker(rf, rm, rb, lb, lm, lf)
hex_walker.set_speed(0.1)
# create the torso
torso = hwd.Robot_Torso(rarm, larm, rot)

# let the robot move nice and slow to show off the new smoothness
# hex_walker.set_speed(0.5)

stab_angle = 150

# calibration stuff: assuming speed = 0.1
# fine-steps per 90:
ROTATE_FINESTEPS_PER_90 = 22
ROTATE_STEPS_PER_90 = 5
WALK_STEPS_PER_SQUARE = 13





def main():
	while True:
		input("Press any key when ready to correct rotation")
		rotation_correction_angle = rotation_corrector.process_image()
		print("Rotation needed: ", str(rotation_correction_angle))
		if rotation_correction_angle is not None:
			if rotation_correction_angle < 0:
				direction = RIGHT
			else:
				direction = LEFT
			# ratio: 22 fine-steps = 90%
			num_correction_steps = abs(round((ROTATE_FINESTEPS_PER_90 * rotation_correction_angle) / 90))
			if num_correction_steps != 0:
				hex_walker.fine_rotate(num_correction_steps, direction)



if __name__ == '__main__':
	main()
