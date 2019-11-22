import copy
from hex_walker_constants import TIP_SERVO, MID_SERVO, ROT_SERVO, WAIST_SERVO

# NOTE: these values are ANGLES not raw pwms
# thing.rot_servo and thing.list[ROT_SERVO] are synonymous/aliases that point to the same underlying data, for both read/write
class Leg_Position(object):
	def __init__(self, rot_servo: float, mid_servo: float, tip_servo: float):
		self.list = [0.0, 0.0, 0.0]
		self.list[ROT_SERVO] = rot_servo
		self.list[MID_SERVO] = mid_servo
		self.list[TIP_SERVO] = tip_servo
	
	def getrot(self) -> float:
		return self.list[ROT_SERVO]
	def setrot(self, v: float):
		self.list[ROT_SERVO] = v
	rot_servo = property(getrot, setrot)
	
	def getmid(self) -> float:
		return self.list[MID_SERVO]
	def setmid(self, v: float):
		self.list[MID_SERVO] = v
	mid_servo = property(getmid, setmid)
	
	def gettip(self) -> float:
		return self.list[TIP_SERVO]
	def settip(self, v: float):
		self.list[TIP_SERVO] = v
	tip_servo = property(gettip, settip)
	
	def getwaist(self) -> float:
		return self.list[WAIST_SERVO]
	def setwaist(self, v: float):
		self.list[WAIST_SERVO] = v
	waist_servo = property(getwaist, setwaist)
	
	def __str__(self):
		return "ROT: " + str(self.rot_servo) + "|| MID : " + str(self.mid_servo) + "|| TIP : " + str(self.tip_servo)
	
	def copy(self):
		return copy.deepcopy(self)


# TODO: remove normal/crouch version and make them derived from tall version

# NOTE: table naming convention is: (standing height)_(gait)_(what type of movement)_TABLE

# table to be used when the robot is trying to rotate in place
LEG_NORMAL_ROTATION_TABLE = {
	"NEUTRAL":			Leg_Position(90, 90, 0),
	"UP_NEUTRAL":		Leg_Position(90, 135, 0),
	
	"RIGHT":			Leg_Position(120, 90, 5),
	"UP_RIGHT":			Leg_Position(120, 135, 5),
	
	"LEFT":				Leg_Position(60, 90, 5),
	"UP_LEFT":			Leg_Position(60, 135, 5)
	
}

# table to be used when the robot is trying to move in a "normal" way (moving with two legs forward)
# tip motor, mid motor, rot motor
LEG_NORMAL_MOVEMENT_TABLE = {
	#all the positions for the front and back legs
	"NEUTRAL":			Leg_Position(90, 90, 30),
	"UP_NEUTRAL":		Leg_Position(90, 135, 30),
	
	"CORN_OUT":			Leg_Position(75, 105, 45),
	"CORN_IN":			Leg_Position(125, 80, 0),
	
	"CORN_UP_OUT":		Leg_Position(75, 150, 45),
	"CORN_UP_IN":		Leg_Position(125, 125, 0),
	
	#now all of the positions for the side legs
	"SIDE_RIGHT":		Leg_Position(115, 90, 0),
	"SIDE_LEFT":		Leg_Position(65, 90, 0),
	
	"SIDE_UP_RIGHT":	Leg_Position(115, 135, 0),
	"SIDE_UP_LEFT":		Leg_Position(65, 135, 0)
}

# # table to be used when the robot is trying to move in a "sideways" way (moving with a single leg forward)
# NORMAL_TRI_SIDE_MOVEMENT_TABLE = {
# 	"NEUTRAL":			Leg_Position(90, 90, 0),
# 	"UP_NEUTRAL":		Leg_Position(90, 135, 0),
# 	"CORN_LEFT":		Leg_Position(0, 0, 0),
# 	"CORN_RIGHT":		Leg_Position(0, 0, 0),
# 	"CENT_OUT":			Leg_Position(0, 0, 0),
# 	"CENT_IN":			Leg_Position(0, 0, 0)
# }



# this is extra. don't do this until the above is working
# table to be used when the robot is trying to rotate in place
LEG_CROUCH_ROTATION_TABLE = {
	"NEUTRAL":			Leg_Position(90, 135, 0),
	"UP_NEUTRAL":		Leg_Position(90, 180, 0),
	
	"RIGHT":			Leg_Position(120, 130, 0),
	"UP_RIGHT":			Leg_Position(120, 180, 0),
	
	"LEFT":				Leg_Position(60, 130, 0),
	"UP_LEFT":			Leg_Position(60, 180, 0)
	
}

LEG_CROUCH_MOVEMENT_TABLE = {
	"NEUTRAL":				Leg_Position(90, 135, 0),
	"UP_NEUTRAL":			Leg_Position(90, 180, 0),
	
	"CORN_LEFT":		Leg_Position(85, 125, 0),
	"CORN_RIGHT":		Leg_Position(95, 125, 0),
	
	"CORN_UP_LEFT":		Leg_Position(85, 175, 0),
	"CORN_UP_RIGHT":	Leg_Position(95, 175, 0),
	
	"SIDE_RIGHT":			Leg_Position(105, 125, 0),
	"SIDE_LEFT":			Leg_Position(75, 125, 0),
	
	"SIDE_UP_RIGHT":		Leg_Position(95, 170, 0),
	"SIDE_UP_LEFT":			Leg_Position(85, 170, 0)
}

# CROUCH_TRI_SIDE_MOVEMENT_TABLE = {
# 	"OUT_RIGHT":		Leg_Position(0, 0, 0),
# 	"OUT":				Leg_Position(0, 0, 0),
# 	"OUT_LEFT":			Leg_Position(0, 0, 0),
# 	"RIGHT":			Leg_Position(0, 0, 0),
# 	"NEUTRAL":			Leg_Position(0, 0, 0),
# 	"LEFT":				Leg_Position(0, 0, 0),
# 	"TUCK_RIGHT":		Leg_Position(0, 0, 0),
# 	"TUCK":				Leg_Position(0, 0, 0),
# 	"TUCK_LEFT":		Leg_Position(0, 0, 0)
# }

LEG_TALL_ROTATION_TABLE = {
	"NEUTRAL":			Leg_Position(90, 45, 30),
	"UP_NEUTRAL":		Leg_Position(90, 90, 0),
	
	"RIGHT":			Leg_Position(120, 45, 30),
	"UP_RIGHT":			Leg_Position(120, 90, 0),
	
	"LEFT":				Leg_Position(60, 45, 30),
	"UP_LEFT":			Leg_Position(60, 90, 0)
	
}

# TODO: fine rotation table is obsolete, remove this
LEG_TALL_FINE_ROTATION_TABLE = {
	"NEUTRAL":			Leg_Position(90, 45, 30),
	"UP_NEUTRAL":		Leg_Position(90, 90, 0),
	
	"RIGHT":			Leg_Position(92, 45, 30),
	"UP_RIGHT":			Leg_Position(92, 90, 0),
	
	"LEFT":				Leg_Position(88, 45, 30),
	"UP_LEFT":			Leg_Position(89, 90, 0)
	
}

# TODO: duplicate neutral/up_neutral with corn_ and side_ names, for readability
LEG_TALL_MOVEMENT_TABLE = {
	"NEUTRAL":				Leg_Position(90, 45, 30),
	"UP_NEUTRAL":			Leg_Position(90, 90, 0),
	
	"CORN_LEFT":		Leg_Position(80, 52, 35),
	"CORN_RIGHT":		Leg_Position(100, 52, 35),
	
	"CORN_UP_LEFT":		Leg_Position(80, 90, 0),
	"CORN_UP_RIGHT":	Leg_Position(100, 90, 0),
	
	"SIDE_RIGHT":			Leg_Position(130, 60, 25),
	"SIDE_LEFT":			Leg_Position(50, 60, 25),
	
	"SIDE_UP_RIGHT":		Leg_Position(130, 80, 0),
	"SIDE_UP_LEFT":			Leg_Position(50, 80, 0)
}

# There's no center in because the mid motor is limited to 45 degrees 
LEG_TALL_SIDE_MOVEMENT_TABLE = {
	"NEUTRAL":				Leg_Position(90, 45, 30),
	"UP_NEUTRAL":			Leg_Position(90, 90, 0),
	
	"SIDE_OUT_LEFT":		Leg_Position(65, 50, 30),
	"SIDE_OUT_RIGHT":		Leg_Position(115, 50, 30),
	
	"SIDE_UP_OUT_LEFT":		Leg_Position(65, 70, 0),
	"SIDE_UP_OUT_RIGHT":	Leg_Position(115, 70, 0),
	
	"CENTER_OUT":			Leg_Position(90, 45, 30),
	
	"CENTER_UP_OUT":		Leg_Position(90, 70, 10),
}


# misc table
# TODO: make neutral/up_neutral in the other movement tables all reference it in this table... only change it in one place!
LEG_MISC_TABLE = {
	"INIT":				Leg_Position(90, 90, 0),
	"NEUTRAL": 			Leg_Position(90, 45, 30),
	"UP_NEUTRAL": 		Leg_Position(90, 90, 0),
	"BOUNCE":			Leg_Position(90, 75, 0),
	"PULL_UP":			Leg_Position(90, 75, 0),
	"STRAIGHT_OUT":		Leg_Position(90, 90, 90)
	
}


