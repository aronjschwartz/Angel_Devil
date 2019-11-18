
# Brian Henson

# this file defines constants that are used in many places throughout many files, so they
# can be changed from just one place.


# ==========================================================

# arbitrary values
LEFT = 1
RIGHT = 2

# direction codes
# TODO: change code to use these 
DIR_F =    0
DIR_FR =  60
DIR_FL = 120
DIR_B =  180
DIR_BR = 240
DIR_BL = 300

# return codes
SUCCESS = 0
INV_PARAM = -1
ILLEGAL_MOVE = -2

# speed options: this is just the time it waits betweeen moves (for hexwalker object)
PLAID_SPEED = .1
NORMAL_SPEED = .2
SLOW_SPEED = .4

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

# set up useful "groups" of leg indices, do not change!!!
# should only be used as "for L in [self.idx_to_leg(n) for n in GROUP]:"
GROUP_ALL_LEGS =   [LEG_RF, LEG_RM, LEG_RB, LEG_LB, LEG_LM, LEG_LF]
GROUP_LEFT_LEGS =  [LEG_LB, LEG_LM, LEG_LF]
GROUP_RIGHT_LEGS = [LEG_RF, LEG_RM, LEG_RB]
GROUP_LEFT_TRI =   [LEG_RM, LEG_LB, LEG_LF]
GROUP_RIGHT_TRI =  [LEG_RF, LEG_RB, LEG_LM]
GROUP_FRONT_LEGS = [LEG_RF, LEG_LF]
GROUP_MID_LEGS =   [LEG_RM, LEG_LM]
GROUP_BACK_LEGS =  [LEG_RB, LEG_LB]

GROUP_ALL_TORSO =  [ARM_L, ARM_R, WAIST]
GROUP_ALL_ARMS =   [ARM_L, ARM_R]


# set the servo IDs, do not change!!!
# used as array indices so they must be be contiguous starting from 0
# TODO: swap ROT_SERVO and TIP_SERVO values so WAIST_SERVO = ROT_SERVO = 0
TIP_SERVO = 0
MID_SERVO = 1
ROT_SERVO = 2
WAIST_SERVO = 0

GROUP_ALL_SERVOS = [TIP_SERVO, MID_SERVO, ROT_SERVO]

# ==========================================================


# all constants related to the hex_walker leg servos
# TODO: revisit and tune these constants!!! arms done, waist done, leg0 done
# these are PWM values that correspond to the ends of the range for that servo (match the angles listed below)
# used for linear mapping from angle-space to pwm-space
c_0_TIP_SERVO_OUT = 158
c_0_TIP_SERVO_IN = 642
c_0_MID_SERVO_UP = 600
c_0_MID_SERVO_DOWN = 260
c_0_ROT_SERVO_RIGHT = 145
c_0_ROT_SERVO_LEFT = 595

c_1_TIP_SERVO_OUT = 133
c_1_TIP_SERVO_IN = 612
c_1_MID_SERVO_UP = 610
c_1_MID_SERVO_DOWN = 270
c_1_ROT_SERVO_RIGHT = 154
c_1_ROT_SERVO_LEFT = 620

c_2_TIP_SERVO_OUT = 165
c_2_TIP_SERVO_IN = 645
c_2_MID_SERVO_UP = 613
c_2_MID_SERVO_DOWN = 275
c_2_ROT_SERVO_RIGHT = 144
c_2_ROT_SERVO_LEFT = 620


c_3_TIP_SERVO_OUT = 640
c_3_TIP_SERVO_IN = 164
# TODO: leg 3 mid servo needs replaced and re-calibrated... malfunctioning
c_3_MID_SERVO_UP = 148
c_3_MID_SERVO_DOWN = 493
c_3_ROT_SERVO_RIGHT = 145
c_3_ROT_SERVO_LEFT = 590

c_4_TIP_SERVO_OUT = 635
c_4_TIP_SERVO_IN = 148
c_4_MID_SERVO_UP = 155
c_4_MID_SERVO_DOWN = 500
c_4_ROT_SERVO_RIGHT = 150
c_4_ROT_SERVO_LEFT = 590

c_5_TIP_SERVO_OUT = 635
c_5_TIP_SERVO_IN = 163
c_5_MID_SERVO_UP = 145
c_5_MID_SERVO_DOWN = 479
c_5_ROT_SERVO_RIGHT = 155
c_5_ROT_SERVO_LEFT = 614

c_L_ARM_TIP_SERVO_OUT = 610
c_L_ARM_TIP_SERVO_IN = 153
c_L_ARM_MID_SERVO_OUT = 95
c_L_ARM_MID_SERVO_IN = 540
c_L_ARM_ROT_SERVO_UP = 95
c_L_ARM_ROT_SERVO_DOWN = 570

c_R_ARM_TIP_SERVO_OUT = 145
c_R_ARM_TIP_SERVO_IN = 605
c_R_ARM_MID_SERVO_OUT = 565
c_R_ARM_MID_SERVO_IN = 125
c_R_ARM_ROT_SERVO_UP = 640
c_R_ARM_ROT_SERVO_DOWN = 110

# rotator motor constants
c_WAIST_SERVO_PWM_LEFT = 480
c_WAIST_SERVO_PWM_RIGHT = 135

# to prevent damage, Leg.do_set_servo_angle() will raise an error if trying to set a servo with PWM limits outside this range
# this applies to all servos on the robot
# damage could easily occur before these limits but whatever, its for catching extreme outliers
c_PWM_ABSOLUTE_MINIMUM = 50
c_PWM_ABSOLUTE_MAXIMUM = 700


# sevo angle limits in degrees
# used for linear mapping from angle-space to pwm-space, corresponds to the pwm endpoints listed above
# also used for safety clamping
# leg limits in degrees
LEG_TIP_SERVO_OUT_ANGLE = 180
LEG_TIP_SERVO_IN_ANGLE = 0
LEG_MID_SERVO_UP_ANGLE = 180
LEG_MID_SERVO_DOWN_ANGLE = 45
LEG_ROT_SERVO_RIGHT_ANGLE = 180
LEG_ROT_SERVO_LEFT_ANGLE = 0
# arm limits in degrees
ARM_TIP_SERVO_OUT_ANGLE = 180
ARM_TIP_SERVO_IN_ANGLE = 0
ARM_MID_SERVO_OUT_ANGLE = 180
ARM_MID_SERVO_IN_ANGLE = 0
ARM_ROT_SERVO_UP_ANGLE = 190
ARM_ROT_SERVO_DOWN_ANGLE = 0
# rotator limits in degrees
WAIST_SERVO_LEFT_ANGLE = 30
WAIST_SERVO_RIGHT_ANGLE = 150

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

CHANNEL_ARML_TIP = 12	#arm_L
CHANNEL_ARML_MID = 11
CHANNEL_ARML_ROT = 10

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

CHANNEL_ARMR_TIP = 14	#arm_R
CHANNEL_ARMR_MID = 11
CHANNEL_ARMR_ROT = 15


# usage: PWM_CHANNEL_ARRAY[leg# 0-7][servo# 0-2]
# example: PWM_CHANNEL_ARRAY[LEG_0][MID_SERVO]
# example: PWM_CHANNEL_ARRAY[LEG_RF] returns a list
# example: PWM_CHANNEL_ARRAY[WAIST][WAIST_SERVO]
# PWM_CHANNEL_ARRAY = [
# [	CHANNEL_LEG0_TIP,	CHANNEL_LEG0_MID,	CHANNEL_LEG0_ROT	],
# [	CHANNEL_LEG1_TIP,	CHANNEL_LEG1_MID,	CHANNEL_LEG1_ROT	],
# [	CHANNEL_LEG2_TIP,	CHANNEL_LEG2_MID,	CHANNEL_LEG2_ROT	],
# [	CHANNEL_LEG3_TIP,	CHANNEL_LEG3_MID,	CHANNEL_LEG3_ROT	],
# [	CHANNEL_LEG4_TIP,	CHANNEL_LEG4_MID,	CHANNEL_LEG4_ROT	],
# [	CHANNEL_LEG5_TIP,	CHANNEL_LEG5_MID,	CHANNEL_LEG5_ROT	],
# [	CHANNEL_ARML_TIP,	CHANNEL_ARML_MID,	CHANNEL_ARML_ROT	],
# [	CHANNEL_ARMR_TIP,	CHANNEL_ARMR_MID,	CHANNEL_ARMR_ROT	],
# [	CHANNEL_WAIST_ROT,	CHANNEL_WAIST_ROT,	CHANNEL_WAIST_ROT	]
# ]

# init the channel array with correct size, then put the values in the right spots
# DO NOT CHANGE!!!
PWM_CHANNEL_ARRAY = [[-1 for i in range(3)] for j in range(9)]
PWM_CHANNEL_ARRAY[LEG_0][TIP_SERVO] = CHANNEL_LEG0_TIP
PWM_CHANNEL_ARRAY[LEG_0][MID_SERVO] = CHANNEL_LEG0_MID
PWM_CHANNEL_ARRAY[LEG_0][ROT_SERVO] = CHANNEL_LEG0_ROT
PWM_CHANNEL_ARRAY[LEG_1][TIP_SERVO] = CHANNEL_LEG1_TIP
PWM_CHANNEL_ARRAY[LEG_1][MID_SERVO] = CHANNEL_LEG1_MID
PWM_CHANNEL_ARRAY[LEG_1][ROT_SERVO] = CHANNEL_LEG1_ROT
PWM_CHANNEL_ARRAY[LEG_2][TIP_SERVO] = CHANNEL_LEG2_TIP
PWM_CHANNEL_ARRAY[LEG_2][MID_SERVO] = CHANNEL_LEG2_MID
PWM_CHANNEL_ARRAY[LEG_2][ROT_SERVO] = CHANNEL_LEG2_ROT
PWM_CHANNEL_ARRAY[ARM_L][TIP_SERVO] = CHANNEL_ARML_TIP
PWM_CHANNEL_ARRAY[ARM_L][MID_SERVO] = CHANNEL_ARML_MID
PWM_CHANNEL_ARRAY[ARM_L][ROT_SERVO] = CHANNEL_ARML_ROT
PWM_CHANNEL_ARRAY[WAIST][TIP_SERVO] = CHANNEL_WAIST_ROT # waist gets all 3 entries on this row, just in case
PWM_CHANNEL_ARRAY[WAIST][MID_SERVO] = CHANNEL_WAIST_ROT # waist gets all 3 entries on this row, just in case
PWM_CHANNEL_ARRAY[WAIST][ROT_SERVO] = CHANNEL_WAIST_ROT # waist gets all 3 entries on this row, just in case
PWM_CHANNEL_ARRAY[LEG_3][TIP_SERVO] = CHANNEL_LEG3_TIP
PWM_CHANNEL_ARRAY[LEG_3][MID_SERVO] = CHANNEL_LEG3_MID
PWM_CHANNEL_ARRAY[LEG_3][ROT_SERVO] = CHANNEL_LEG3_ROT
PWM_CHANNEL_ARRAY[LEG_4][TIP_SERVO] = CHANNEL_LEG4_TIP
PWM_CHANNEL_ARRAY[LEG_4][MID_SERVO] = CHANNEL_LEG4_MID
PWM_CHANNEL_ARRAY[LEG_4][ROT_SERVO] = CHANNEL_LEG4_ROT
PWM_CHANNEL_ARRAY[LEG_5][TIP_SERVO] = CHANNEL_LEG5_TIP
PWM_CHANNEL_ARRAY[LEG_5][MID_SERVO] = CHANNEL_LEG5_MID
PWM_CHANNEL_ARRAY[LEG_5][ROT_SERVO] = CHANNEL_LEG5_ROT
PWM_CHANNEL_ARRAY[ARM_R][TIP_SERVO] = CHANNEL_ARMR_TIP
PWM_CHANNEL_ARRAY[ARM_R][MID_SERVO] = CHANNEL_ARMR_MID
PWM_CHANNEL_ARRAY[ARM_R][ROT_SERVO] = CHANNEL_ARMR_ROT


# ==========================================================

# time between interpolated poses is known constant, number of interpolated poses is dynamic
# .05 is okay, try 0.03 or 0.02 next
INTERPOLATE_TIME = 0.03

