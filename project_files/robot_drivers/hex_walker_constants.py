
# Brian Henson

# this file defines constants that are used in many places throughout many files, so they
# can be changed from just one place.

# ==========================================================

# set the "leg number" IDs, do not change!!!
# used as array indices so they must be be contiguous starting from 0
LEG_0 = 0	#rf
LEG_1 = 1	#rm
LEG_2 = 2	#rb
LEG_3 = 3	#lb
LEG_4 = 4	#lm
LEG_5 = 5	#lf
LEG_RF = LEG_0
LEG_RM = LEG_1
LEG_RB = LEG_2
LEG_LB = LEG_3
LEG_LM = LEG_4
LEG_LF = LEG_5
ARM_L = 6
ARM_R = 7
WAIST = 8

# set the servo IDs, do not change!!!
# used as array indices so they must be be contiguous starting from 0
TIP_MOTOR = 0
MID_MOTOR = 1
ROT_MOTOR = 2
WAIST_MOTOR = 0

# ==========================================================


# all constants related to the hex_walker leg servos
# TODO: revisit and tune these constants!!! arms done, waist done, leg0 done
# these are PWM values that correspond to the ends of the range for that servo (match the angles listed below)
# used for linear mapping from angle-space to pwm-space
c_0_TIP_MOTOR_OUT = 158
c_0_TIP_MOTOR_IN = 642
c_0_MID_MOTOR_UP = 600
c_0_MID_MOTOR_DOWN = 260
c_0_ROT_MOTOR_RIGHT = 145
c_0_ROT_MOTOR_LEFT = 595

c_1_TIP_MOTOR_OUT = 129
c_1_TIP_MOTOR_IN = 606
c_1_MID_MOTOR_UP = 604
c_1_MID_MOTOR_DOWN = 259
c_1_ROT_MOTOR_RIGHT = 154
c_1_ROT_MOTOR_LEFT = 603

c_2_TIP_MOTOR_OUT = 140
c_2_TIP_MOTOR_IN = 616
c_2_MID_MOTOR_UP = 613
c_2_MID_MOTOR_DOWN = 266
c_2_ROT_MOTOR_RIGHT = 144
c_2_ROT_MOTOR_LEFT = 620

c_3_TIP_MOTOR_OUT = 634
c_3_TIP_MOTOR_IN = 164
c_3_MID_MOTOR_UP = 148
c_3_MID_MOTOR_DOWN = 493
c_3_ROT_MOTOR_RIGHT = 155
c_3_ROT_MOTOR_LEFT = 601

c_4_TIP_MOTOR_OUT = 624
c_4_TIP_MOTOR_IN = 140
c_4_MID_MOTOR_UP = 145
c_4_MID_MOTOR_DOWN = 487
c_4_ROT_MOTOR_RIGHT = 154
c_4_ROT_MOTOR_LEFT = 590

c_5_TIP_MOTOR_OUT = 627
c_5_TIP_MOTOR_IN = 157
c_5_MID_MOTOR_UP = 142
c_5_MID_MOTOR_DOWN = 482
c_5_ROT_MOTOR_RIGHT = 155
c_5_ROT_MOTOR_LEFT = 614

c_L_ARM_TIP_MOTOR_OUT = 610
c_L_ARM_TIP_MOTOR_IN = 153
c_L_ARM_MID_MOTOR_OUT = 95
c_L_ARM_MID_MOTOR_IN = 540
c_L_ARM_ROT_MOTOR_UP = 95
c_L_ARM_ROT_MOTOR_DOWN = 570

c_R_ARM_TIP_MOTOR_OUT = 145
c_R_ARM_TIP_MOTOR_IN = 605
c_R_ARM_MID_MOTOR_OUT = 565
c_R_ARM_MID_MOTOR_IN = 125
c_R_ARM_ROT_MOTOR_UP = 640
c_R_ARM_ROT_MOTOR_DOWN = 110

# rotator motor constants
c_ROTATOR_MOTOR_LEFT = 480
c_ROTATOR_MOTOR_RIGHT = 135

# to prevent damage, Leg.do_set_servo_angle() will raise an error if trying to set a servo with PWM limits outside this range
# this applies to all servos on the robot
# damage could easily occur before these limits but whatever, its for catching extreme outliers
c_PWM_ABSOLUTE_MINIMUM = 50
c_PWM_ABSOLUTE_MAXIMUM = 700


# sevo angle limits in degrees
# used for linear mapping from angle-space to pwm-space, corresponds to the pwm endpoints listed above
# also used for safety clamping
# leg limits in degrees
TIP_MOTOR_OUT_ANGLE = 270
TIP_MOTOR_IN_ANGLE = 90
MID_MOTOR_UP_ANGLE = 180
MID_MOTOR_DOWN_ANGLE = 45
ROT_MOTOR_RIGHT_ANGLE = 180
ROT_MOTOR_LEFT_ANGLE = 0
# arm limits in degrees
ARM_TIP_MOTOR_OUT_ANGLE = 180
ARM_TIP_MOTOR_IN_ANGLE = 0
ARM_MID_MOTOR_OUT_ANGLE = 180
ARM_MID_MOTOR_IN_ANGLE = 0
ARM_ROT_MOTOR_UP_ANGLE = 190
ARM_ROT_MOTOR_DOWN_ANGLE = 0
# rotator limits in degrees
ROTATOR_LEFT_ANGLE = 30
ROTATOR_RIGHT_ANGLE = 150

# ==========================================================

PWM_FREQ = 60

# set up the channels used on the PWM hat for each motor
# one variable for each servo + indexable array
PWM_ADDR_BOTTOM = 0x40 # bottom: 	R legs + L arm + waist

CHANNEL_LEG0_TIP = 0	#rf
CHANNEL_LEG0_MID = 1
CHANNEL_LEG0_ROT = 2
CHANNEL_LEG1_TIP = 3	#rm
CHANNEL_LEG1_MID = 4
CHANNEL_LEG1_ROT = 5
CHANNEL_LEG2_TIP = 6	#rb
CHANNEL_LEG2_MID = 7
CHANNEL_LEG2_ROT = 8

CHANNEL_LEG6_TIP = 12	#arm_L
CHANNEL_LEG6_MID = 11
CHANNEL_LEG6_ROT = 10

CHANNEL_WAIST_ROT = 9	#waist, connected to bottom

PWM_ADDR_TOP = 0x41 # top: 		L legs + R arm

CHANNEL_LEG3_TIP = 0	#lb
CHANNEL_LEG3_MID = 1
CHANNEL_LEG3_ROT = 2
CHANNEL_LEG4_TIP = 6	#lm
CHANNEL_LEG4_MID = 4
CHANNEL_LEG4_ROT = 5
CHANNEL_LEG5_TIP = 3	#lf
CHANNEL_LEG5_MID = 7
CHANNEL_LEG5_ROT = 8

CHANNEL_LEG7_TIP = 14	#arm_R
CHANNEL_LEG7_MID = 11
CHANNEL_LEG7_ROT = 15


# usage: LEG_PWM_CHANNEL[leg# 0-7][servo# 0-2: tip=0, mid=1, rot=2]
# example: LEG_PWM_CHANNEL[LEG_0][MID_MOTOR]
# example: LEG_PWM_CHANNEL[LEG_RF] returns a list
# example: LEG_PWM_CHANNEL[WAIST][WAIST_MOTOR]
LEG_PWM_CHANNEL = [
[	CHANNEL_LEG0_TIP,	CHANNEL_LEG0_MID,	CHANNEL_LEG0_ROT	],
[	CHANNEL_LEG1_TIP,	CHANNEL_LEG1_MID,	CHANNEL_LEG1_ROT	],
[	CHANNEL_LEG2_TIP,	CHANNEL_LEG2_MID,	CHANNEL_LEG2_ROT	],
[	CHANNEL_LEG3_TIP,	CHANNEL_LEG3_MID,	CHANNEL_LEG3_ROT	],
[	CHANNEL_LEG4_TIP,	CHANNEL_LEG4_MID,	CHANNEL_LEG4_ROT	],
[	CHANNEL_LEG5_TIP,	CHANNEL_LEG5_MID,	CHANNEL_LEG5_ROT	],
[	CHANNEL_LEG6_TIP,	CHANNEL_LEG6_MID,	CHANNEL_LEG6_ROT	],
[	CHANNEL_LEG7_TIP,	CHANNEL_LEG7_MID,	CHANNEL_LEG7_ROT	],
[	CHANNEL_WAIST_ROT,	CHANNEL_WAIST_ROT,	CHANNEL_WAIST_ROT	]
]



# ==========================================================

# time between interpolated poses is known constant, number of interpolated poses is dynamic
# .05 is okay, try 0.03 or 0.02 next
INTERPOLATE_TIME = 0.03

