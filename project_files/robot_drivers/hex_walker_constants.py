
# this file defines constants and macros that don't cleanly fit into the other files.
# or are important enough that they deserve their own file.
# or whatever i feel like.


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

# ==========================================================


# all constants related to the hex_walker leg servos
# TODO: revisit and tune these constants!!!
# each constant should correspond to the end of the range for that servo (match the angles listed below)
c_0_TIP_MOTOR_OUT = 158
c_0_TIP_MOTOR_IN = 642
c_0_MID_MOTOR_UP = 612
c_0_MID_MOTOR_DOWN = 264
c_0_ROT_MOTOR_RIGHT = 149
c_0_ROT_MOTOR_LEFT = 603

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

c_L_ARM_TIP_MOTOR_OUT = 609
c_L_ARM_TIP_MOTOR_IN = 153
c_L_ARM_MID_MOTOR_OUT = 92
c_L_ARM_MID_MOTOR_IN = 544
c_L_ARM_ROT_MOTOR_UP = 118
c_L_ARM_ROT_MOTOR_DOWN = 574

c_R_ARM_TIP_MOTOR_OUT = 146
c_R_ARM_TIP_MOTOR_IN = 603
c_R_ARM_MID_MOTOR_OUT = 569
c_R_ARM_MID_MOTOR_IN = 135
c_R_ARM_ROT_MOTOR_UP = 628
c_R_ARM_ROT_MOTOR_DOWN = 110

# rotator motor constants
ROTATOR_MOTOR_LEFT = 424
ROTATOR_MOTOR_RIGHT = 217


# angle limits in degrees: same regardless of side so no need to l/r differentiate
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
ARM_ROT_MOTOR_UP_ANGLE = 180
ARM_ROT_MOTOR_DOWN_ANGLE = 0
# rotator limits in degrees
ROTATOR_LEFT_ANGLE = 45
ROTATOR_RIGHT_ANGLE = 135

# ==========================================================

# set up the channels used on the PWM hat for each motor
# one variable for each servo + indexable array
CHANNEL_LEG0_TIP = 0	#rf
CHANNEL_LEG0_MID = 1
CHANNEL_LEG0_ROT = 2
CHANNEL_LEG1_TIP = 3	#rm
CHANNEL_LEG1_MID = 4
CHANNEL_LEG1_ROT = 5
CHANNEL_LEG2_TIP = 6	#rb
CHANNEL_LEG2_MID = 7
CHANNEL_LEG2_ROT = 8
CHANNEL_LEG3_TIP = 0	#lb
CHANNEL_LEG3_MID = 1
CHANNEL_LEG3_ROT = 2
CHANNEL_LEG4_TIP = 6	#lm
CHANNEL_LEG4_MID = 4
CHANNEL_LEG4_ROT = 5
CHANNEL_LEG5_TIP = 3	#lf
CHANNEL_LEG5_MID = 7
CHANNEL_LEG5_ROT = 8

# TODO: determine channels for arms + waist
#arm_L
CHANNEL_LEG6_TIP = 99
CHANNEL_LEG6_MID = 99
CHANNEL_LEG6_ROT = 99
#arm_R
CHANNEL_LEG7_TIP = 99
CHANNEL_LEG7_MID = 99
CHANNEL_LEG7_ROT = 99
#waist
CHANNEL_WAIST_ROT = 99

# usage: LEG_PWM_CHANNEL[leg# 0-7][servo# 0-2: tip=0, mid=1, rot=2]
# example: LEG_PWM_CHANNEL[LEG_0][MID_MOTOR]
# example: LEG_PWM_CHANNEL[LEG_RF][MID_MOTOR]
# example: LEG_PWM_CHANNEL[WAIST][ROT_MOTOR]
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


# set Adafruit pwm address and frequency
PWM_ADDR_R = 0x40
PWM_ADDR_L = 0x41
PWM_FREQ = 60
# TODO: which hat do the torso servos connect to? might change names of constants to reflect this

# ==========================================================

# time between interpolated poses is known constant, number of interpolated poses is dynamic
INTERPOLATE_TIME = 0.1

