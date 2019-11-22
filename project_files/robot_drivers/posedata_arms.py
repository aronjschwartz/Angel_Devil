from posedata_leg import *

ARMS_ARM_TABLE = {
	"NEUTRAL":			Leg_Position(0, 45, 90),
	"ON_HIP":			Leg_Position(0, 90, 0),
	"UP":				Leg_Position(90, 0, 180),
	"STRAIGHT_OUT":		Leg_Position(90,90,90),
	"STRAIGHT_FWD":		Leg_Position(90,0,90),
	
	"WAVE_UP":			Leg_Position(30, 40, 180),
	"WAVE_DOWN":		Leg_Position(55,120,180),
	
	"HAND_SHAKE_UP":	Leg_Position(45,10,80),
	"HAND_SHAKE_MID":	Leg_Position(45, 10, 70),
	"HAND_SHAKE_DOWN":	Leg_Position(45,10,60),
	
	"JOHNNY_BRAVO_MONKEY_DOWN":	Leg_Position(90,0,80),
	"JOHNNY_BRAVO_MONKEY_UP":	Leg_Position(90,0,100),
	
	"BLOCKING_UP":		Leg_Position(30, 0, 180),
	"BLOCKING_FRONT":	Leg_Position(30, 0, 90),
	
	"LOOKING":			Leg_Position(20, 5, 155)
	
}


# this is a bundle of Leg_Position objects, one for each arm, that describes a "pose" for the robot
# DOES NOT INCLUDE WAIST INFORMATION
class Arms_Position(object):
	def __init__(self, left_arm, right_arm, description="-"):
		# TODO: URGENT! ELIMINATE THESE NAMED FIELDS BECAUSE CHANGES IN THE LIST ARE NOT REFLECTED IN THEM!
		self.left_arm = left_arm
		self.right_arm = right_arm
		# NOTE: this list is not actually indexed with ARM_L/ARM_R... might want to change this to a dict?
		# probably just fine like this
		self.list = [self.left_arm, self.right_arm]
		self.description = description
	
	def __str__(self):
		start_str = "-----------------------Arms position is-------------------------"
		left_arm_string = "left arm: " + str(self.left_arm)
		right_arm_string = "right arm: " + str(self.right_arm)
		return start_str + left_arm_string + "\n" + right_arm_string + "\n" + self.description
	
	def copy(self):
		return copy.deepcopy(self)


# relaxed
ARMS_NEUTRAL = 1

# jumping jacks
ARMS_JACK_DOWN = 2
ARMS_JACK_UP = 3

# right hand wave
ARMS_WAVE_DOWN = 4
ARMS_WAVE_UP = 5

# right hand shake
ARMS_SHAKE_DOWN = 6
ARMS_SHAKE_UP = 7

# dancing in front
ARMS_DANCE_FRONT_LEFT_OUT = 8
ARMS_DANCE_FRONT_RIGHT_OUT = 9

# dancing above
ARMS_DANCE_ABOVE_LEFT_UP = 10
ARMS_DANCE_ABOVE_RIGHT_UP = 11

# jognny bravo dance
ARMS_MONKEY_RIGHT_UP = 12
ARMS_MONKEY_LEFT_UP = 13

# finish hand shake
ARMS_SHAKE_MID = 14

# looking
ARMS_LOOKING = 15

# pointing
ARMS_POINTING_LEFT = 16
ARMS_POINTING_RIGHT= 17
ARMS_POINTING_FWD_LEFT = 18
ARMS_POINTING_FWD_RIGHT = 19

ARMS_POSITIONS = {
	# 1
	ARMS_NEUTRAL:
		Arms_Position(ARMS_ARM_TABLE["NEUTRAL"],
					  ARMS_ARM_TABLE["NEUTRAL"],
					  "torso is in the neutral position"),
	# 2
	ARMS_JACK_DOWN:
		Arms_Position(ARMS_ARM_TABLE["WAVE_DOWN"],
					  ARMS_ARM_TABLE["WAVE_DOWN"],
					  "jumping jacks (down pos)"),
	
	# 3
	ARMS_JACK_UP:
		Arms_Position(ARMS_ARM_TABLE["WAVE_UP"],
					  ARMS_ARM_TABLE["WAVE_UP"],
					  "jumping jacks (up pos)"),
	# 4
	ARMS_WAVE_DOWN:
		Arms_Position(ARMS_ARM_TABLE["NEUTRAL"],
					  ARMS_ARM_TABLE["WAVE_DOWN"],
					  "waving with the right hand (down pos)"),
	
	# 5
	ARMS_WAVE_UP:
		Arms_Position(ARMS_ARM_TABLE["NEUTRAL"],
					  ARMS_ARM_TABLE["WAVE_UP"],
					  "waving with the right hand (up pos)"),
	# 6
	ARMS_SHAKE_DOWN:
		Arms_Position(ARMS_ARM_TABLE["NEUTRAL"],
					  ARMS_ARM_TABLE["HAND_SHAKE_DOWN"],
					  "handshaking with the right hand (down pos)"),
	# 14
	ARMS_SHAKE_MID:
		Arms_Position(ARMS_ARM_TABLE["NEUTRAL"],
					  ARMS_ARM_TABLE["HAND_SHAKE_MID"],
					  "handshaking with the rigth hand (mid pos)"),
	# 7
	ARMS_SHAKE_UP:
		Arms_Position(ARMS_ARM_TABLE["NEUTRAL"],
					  ARMS_ARM_TABLE["HAND_SHAKE_UP"],
					  "handshaking with the right hand (up pos)"),
	# 8
	ARMS_DANCE_FRONT_LEFT_OUT:
		Arms_Position(ARMS_ARM_TABLE["STRAIGHT_OUT"],
					  ARMS_ARM_TABLE["BLOCKING_FRONT"],
					  "dance move with left arm out"),
	# 9
	ARMS_DANCE_FRONT_RIGHT_OUT:
		Arms_Position(ARMS_ARM_TABLE["BLOCKING_FRONT"],
					  ARMS_ARM_TABLE["STRAIGHT_OUT"],
					  "dance move with right arm out"),
	# 10
	ARMS_DANCE_ABOVE_LEFT_UP:
		Arms_Position(ARMS_ARM_TABLE["WAVE_DOWN"],
					  ARMS_ARM_TABLE["BLOCKING_UP"],
					  "dance move with left arm above head"),
	
	# 11
	ARMS_DANCE_ABOVE_RIGHT_UP:
		Arms_Position(ARMS_ARM_TABLE["BLOCKING_UP"],
					  ARMS_ARM_TABLE["WAVE_DOWN"],
					  "dance move with right arm above head"),
	
	# 13
	ARMS_MONKEY_RIGHT_UP:
		Arms_Position(ARMS_ARM_TABLE["JOHNNY_BRAVO_MONKEY_DOWN"],
					  ARMS_ARM_TABLE["JOHNNY_BRAVO_MONKEY_UP"],
					  "starting johnny bravo's monkey dance"),
	
	ARMS_MONKEY_LEFT_UP:
		Arms_Position(ARMS_ARM_TABLE["JOHNNY_BRAVO_MONKEY_UP"],
					  ARMS_ARM_TABLE["JOHNNY_BRAVO_MONKEY_DOWN"],
					  "finishing johnny bravo's monkey dance"),
	
	# 15
	ARMS_LOOKING:
		Arms_Position(ARMS_ARM_TABLE["LOOKING"],
					  ARMS_ARM_TABLE["NEUTRAL"],
					  "raising hand to act like it is looking around"),
	
	# 16
	ARMS_POINTING_LEFT:
		Arms_Position(ARMS_ARM_TABLE["STRAIGHT_OUT"],
					  ARMS_ARM_TABLE["NEUTRAL"],
					  "pointing left arm out"),
	
	# 17
	ARMS_POINTING_RIGHT:
		Arms_Position(ARMS_ARM_TABLE["NEUTRAL"],
					  ARMS_ARM_TABLE["STRAIGHT_OUT"],
					  "pointing right arm out"),
	# 18
	ARMS_POINTING_FWD_LEFT:
		Arms_Position(ARMS_ARM_TABLE["STRAIGHT_FWD"],
					  ARMS_ARM_TABLE["NEUTRAL"],
					  "pointing right arm out"),
	# 19
	ARMS_POINTING_FWD_RIGHT:
		Arms_Position(ARMS_ARM_TABLE["NEUTRAL"],
					  ARMS_ARM_TABLE["STRAIGHT_FWD"],
					  "pointing right arm out")
	
}


