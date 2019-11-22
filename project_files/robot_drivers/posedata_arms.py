from posedata_leg import *
from hex_walker_constants import ARM_L, ARM_R

ARMS_ARM_TABLE = {
	"NEUTRAL":			Leg_Position(90, 45, 0),
	"ON_HIP":			Leg_Position(0, 90, 0),
	"UP":				Leg_Position(180, 0, 90),
	"STRAIGHT_OUT":		Leg_Position(90, 90, 90),
	"STRAIGHT_FWD":		Leg_Position(90, 0, 90),
	
	"WAVE_UP":			Leg_Position(180, 40, 30),
	"WAVE_DOWN":		Leg_Position(180, 120, 55),
	
	"HAND_SHAKE_UP":	Leg_Position(80, 10, 45),
	"HAND_SHAKE_MID":	Leg_Position(70, 10, 45),
	"HAND_SHAKE_DOWN":	Leg_Position(60, 10, 45),
	
	"JOHNNY_BRAVO_MONKEY_DOWN":	Leg_Position(80, 0, 90),
	"JOHNNY_BRAVO_MONKEY_UP":	Leg_Position(100, 0, 90),
	
	"BLOCKING_UP":		Leg_Position(180, 0, 30),
	"BLOCKING_FRONT":	Leg_Position(90, 0, 30),
	
	"LOOKING":			Leg_Position(155, 5, 20)
	
}


# this is a bundle of Leg_Position objects, one for each arm, that describes a "pose" for the robot
# DOES NOT INCLUDE WAIST INFORMATION
# thing.arm_l and thing.list[ARM_L] are synonymous/aliases that point to the same underlying data, for both read/write
class Arms_Position(object):
	def __init__(self, left_arm: Leg_Position, right_arm: Leg_Position, description="-"):
		self.description = description
		# technically its a dict and not a list but whatever its gotta use the same name as the other classes
		self.list = dict()
		self.list[ARM_L] = copy.deepcopy(left_arm)
		self.list[ARM_R] = copy.deepcopy(right_arm)
	
	def getarml(self) -> Leg_Position:
		return self.list[ARM_L]
	def setarml(self, v: Leg_Position):
		self.list[ARM_L] = v
	arm_l = property(getarml, setarml)
	
	def getarmr(self) -> Leg_Position:
		return self.list[ARM_R]
	def setarmr(self, v: Leg_Position):
		self.list[ARM_R] = v
	arm_r = property(getarmr, setarmr)
	
	def __str__(self):
		start_str = "-----------------------Arms position is-------------------------"
		left_arm_string = "left arm: " + str(self.arm_l)
		right_arm_string = "right arm: " + str(self.arm_r)
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


