import copy

# NOTE: these values are ANGLES not raw pwms
class Leg_Position(object):
	# TODO: once tip/rot servo values are swapped, swap their position in this arg list too
	def __init__(self, tip_servo, mid_servo, rot_servo):
		self.rot_servo = rot_servo
		self.mid_servo = mid_servo
		self.tip_servo = tip_servo
		# TODO: once tip/rot servo values are swapped, swap their location in self.list too
		self.list = [self.tip_servo, self.mid_servo, self.rot_servo]
	
	def __str__(self):
		return "ROT: " + str(self.rot_servo) + "|| MID : " + str(self.mid_servo) + "|| TIP : " + str(self.tip_servo)
	
	def copy(self):
		return copy.deepcopy(self)


# NOTE: table naming convention is: (standing height)_(gait)_(what type of movement)_TABLE

# table to be used when the robot is trying to rotate in place
NORMAL_TRI_ROTATION_TABLE = {
	"NEUTRAL":			Leg_Position(0, 90, 90),
	"UP_NEUTRAL":		Leg_Position(0, 135, 90),
	
	"RIGHT":			Leg_Position(5, 90, 120),
	"UP_RIGHT":			Leg_Position(5, 135, 120),
	
	"LEFT":				Leg_Position(5, 90, 60),
	"UP_LEFT":			Leg_Position(5, 135, 60)
	
}

# table to be used when the robot is trying to move in a "normal" way (moving with two legs forward)
# tip motor, mid motor, rot motor
NORMAL_TRI_MOVEMENT_TABLE = {
	#all the positions for the front and back legs
	"NEUTRAL":			Leg_Position(30, 90, 90),
	"UP_NEUTRAL":		Leg_Position(30, 135, 90),
	
	"CORN_OUT":			Leg_Position(45, 105, 75),
	"CORN_IN":			Leg_Position(-5, 80, 125),
	
	"CORN_UP_OUT":		Leg_Position(45, 150, 75),
	"CORN_UP_IN":		Leg_Position(-5, 125, 125),
	
	#now all of the positions for the side legs
	"SIDE_RIGHT":		Leg_Position(-10, 90, 115),
	"SIDE_LEFT":		Leg_Position(-10, 90, 65),
	
	"SIDE_UP_RIGHT":	Leg_Position(-10, 135, 115),
	"SIDE_UP_LEFT":		Leg_Position(-10, 135, 65)
}

# table to be used when the robot is trying to move in a "sideways" way (moving with a single leg forward)
NORMAL_TRI_SIDE_MOVEMENT_TABLE = {
	"NEUTRAL":			Leg_Position(0, 90, 90),
	"UP_NEUTRAL":		Leg_Position(0, 135, 90),
	"CORN_LEFT":		Leg_Position(-90, 0, 0),
	"CORN_RIGHT":		Leg_Position(-90, 0, 0),
	"CENT_OUT":			Leg_Position(-90, 0, 0),
	"CENT_IN":			Leg_Position(-90, 0, 0)
}



# this is extra. don't do this until the above is working
# table to be used when the robot is trying to rotate in place
CROUCH_TRI_ROTATION_TABLE = {
	"NEUTRAL":			Leg_Position(-45, 135, 90),
	"UP_NEUTRAL":		Leg_Position(-45, 180, 90),
	
	"RIGHT":			Leg_Position(-40, 130, 120),
	"UP_RIGHT":			Leg_Position(-40, 180, 120),
	
	"LEFT":				Leg_Position(-40, 130, 60),
	"UP_LEFT":			Leg_Position(-40, 180, 60)
	
}

CROUCH_TRI_MOVEMENT_TABLE = {
	"NEUTRAL":				Leg_Position(-45, 135, 90),
	"UP_NEUTRAL":			Leg_Position(-45, 180, 90),
	
	"CORN_OUT_LEFT":		Leg_Position(-10, 125, 85),
	"CORN_OUT_RIGHT":		Leg_Position(-10, 125, 95),
	
	"CORN_UP_OUT_LEFT":		Leg_Position(-5, 175, 85),
	"CORN_UP_OUT_RIGHT":	Leg_Position(-5, 175, 95),
	
	"SIDE_RIGHT":			Leg_Position(-20, 125, 105),
	"SIDE_LEFT":			Leg_Position(-20, 125, 75),
	
	"SIDE_UP_RIGHT":		Leg_Position(-20, 170, 95),
	"SIDE_UP_LEFT":			Leg_Position(-20, 170, 85)
}

CROUCH_TRI_SIDE_MOVEMENT_TABLE = {
	"OUT_RIGHT":		Leg_Position(-90, 0, 0),
	"OUT":				Leg_Position(-90, 0, 0),
	"OUT_LEFT":			Leg_Position(-90, 0, 0),
	"RIGHT":			Leg_Position(-90, 0, 0),
	"NEUTRAL":			Leg_Position(-90, 0, 0),
	"LEFT":				Leg_Position(-90, 0, 0),
	"TUCK_RIGHT":		Leg_Position(-90, 0, 0),
	"TUCK":				Leg_Position(-90, 0, 0),
	"TUCK_LEFT":		Leg_Position(-90, 0, 0)
}

TALL_TRI_ROTATION_TABLE = {
	"NEUTRAL":			Leg_Position(30, 45, 90),
	"UP_NEUTRAL":		Leg_Position(-45, 90, 90),
	
	"RIGHT":			Leg_Position(30, 45, 120),
	"UP_RIGHT":			Leg_Position(-45, 90, 120),
	
	"LEFT":				Leg_Position(30, 45, 60),
	"UP_LEFT":			Leg_Position(-45, 90, 60)
	
}

TALL_TRI_FINE_ROTATION_TABLE = {
	"NEUTRAL":			Leg_Position(30, 45, 90),
	"UP_NEUTRAL":		Leg_Position(-45, 90, 90),
	
	"RIGHT":			Leg_Position(30, 45, 92),
	"UP_RIGHT":			Leg_Position(-45, 90, 92),
	
	"LEFT":				Leg_Position(30, 45, 88),
	"UP_LEFT":			Leg_Position(-45, 90, 89)
	
}

TALL_TRI_MOVEMENT_TABLE = {
	"NEUTRAL":				Leg_Position(30, 45, 90),
	"UP_NEUTRAL":			Leg_Position(-45, 90, 90),
	
	"CORN_OUT_LEFT":		Leg_Position(35, 52, 80),
	"CORN_OUT_RIGHT":		Leg_Position(35, 52, 100),
	
	"CORN_UP_OUT_LEFT":		Leg_Position(-30, 90, 80),
	"CORN_UP_OUT_RIGHT":	Leg_Position(-30, 90, 100),
	
	"SIDE_RIGHT":			Leg_Position(25, 60, 130),
	"SIDE_LEFT":			Leg_Position(25, 60, 50),
	
	"SIDE_UP_RIGHT":		Leg_Position(-30, 80, 130),
	"SIDE_UP_LEFT":			Leg_Position(-30, 80, 50)
}

# There's no center in because the mid motor is limited to 45 degrees 
TALL_TRI_SIDE_MOVEMENT_TABLE = {
	"NEUTRAL":				Leg_Position(30, 45, 90),
	"UP_NEUTRAL":			Leg_Position(-45, 90, 90),
	
	"SIDE_OUT_LEFT":		Leg_Position(30, 50, 65),
	"SIDE_OUT_RIGHT":		Leg_Position(30, 50, 115),
	
	"SIDE_UP_OUT_LEFT":		Leg_Position(0, 70, 65),
	"SIDE_UP_OUT_RIGHT":	Leg_Position(0, 70, 115),
	
	"CENTER_OUT":			Leg_Position(30, 45, 90),
	
	"CENTER_UP_OUT":		Leg_Position(10, 70, 90),
}


# misc table
MISC_TABLE = {
	"BOUNCE":			Leg_Position(0, 75, 90),
	"PULL_UP":			Leg_Position(-30, 75, 90),
	"INIT":				Leg_Position(0, 90, 90),
	"STRAIGHT_OUT":		Leg_Position(90, 90, 90)
	
}


