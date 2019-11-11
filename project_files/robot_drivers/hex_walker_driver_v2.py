
# Brian Henson

# new version of hex_walker_driver, first created in fall2019 project1.
# moved some contents from here to hex_util or hex_walker_constants files for cleanliness and organization.
# adds interpolation & threading improvments to the Leg object driver, some of the Hex_Walker driver, more improvements pending.
# also improved organization of Leg object by grouping variables into lists.
# also improved code reuse by making Rotator object a subclass of Leb object.


from __future__ import division
import time
import threading
from hex_walker_data import *
from leg_data import *
from torso_data import *

from hex_walker_constants import *
from hex_util import *
from leg_thread import *

#Extraneous
HW_MOVE_DEBUG = 0 #toggle 0/1 to turn debug prints on/off

LEG_THREAD_DEBUG = False

USE_THREADING = True



# arbitrary values
LEFT = 1
RIGHT = 2

# error codes and coding constants
SUCCESS = 0
INV_PARAM = -1
ILLEGAL_MOVE = -2


# speed options: this is just the time it waits betweeen moves (for hexwalker object)
PLAID_SPEED = .1
NORMAL = .2
SLOW = .4


# Leg_Position class defined in leg_data.py
# Hex_Walker_Position class defined in hex_walker_data.py
# Torso_Position class defined in torso_data.py

# a leg object should be able to associate itself with specific channels
# on a specific i2c interface address and then control all parts of the
# leg. It should be able to set each servo according to a degree, max, min,
# or a value from 0-100 in terms of percent of maximum
class Leg(object):
	# list of functions:
	# __init__
	# print_self
	# angle_to_pwm
	# pwm_to_angle
	# percent_to_angle
	# set_servo_percent
	# set_servo_pwm
	# set_servo_angle
	# set_servo_angle_thread
	# set_leg_position
	# set_leg_position_thread
	# abort
	# do_set_servo_angle
	def __init__(self, pwm, channels, leg_num):

		# unique ID, not actually used for much, just stores the leg_num
		self.uid = leg_num
		# this can be either the new-style PWM wrapper or the old-style actual pwm object, works just the same
		self.pwm = pwm
		# running/idle flags: normal Events can only wait for a rising edge, if I want to wait for a falling edge, i need to 
		# set up a complementary system like this. also they're really being used as flags, not as "events", but whatever.
		self.running_flag = threading.Event()
		self.idle_flag = threading.Event()
		self.idle_flag.set()
		# i want setting one/clearing other to be an atomic operation so it should have a lock object just in case
		self._state_flag_lock = threading.Lock()
		# the list of frames that the leg thread is consuming as the leg object is adding onto
		self.frame_queue = []
		# locking object to ensure no collisions happen around the frame queue
		self._frame_queue_lock = threading.Lock()
		# locking object to ensure no collisions happen around self.tip_motor/self.tip_motor_angle, etc
		# might not be necessary but couldn't hurt, technically both the leg thread and leg object write into them
		self._curr_pos_lock = threading.Lock()

		# create and launch the thread for this leg
		# note: this MUST be daemon type because the thread is designed to run forever... the only way to stop it is by stopping its parent, which means it must be a daemon!
		# it should be able to access all of this leg's other member variables and functions
		# threadname = "framethread" + str(leg_num)
		self.framethread = threading.Thread(name="framethread_" + str(leg_num), target=Frame_Thread_Func, args=(self, LEG_THREAD_DEBUG), daemon=True)
		# just to be safe, don't start the thread until the end of __init__
		
		
		# set the channels to use for the PWM object, comes in as a list
		self.pwm_channels = channels		
		
		
		# now, assign the correct constants to limit PWM values
		self.SERVO_PWM_LIMITS = [[0,1],[0,1],[0,1]]
		if leg_num == LEG_0:
			# leg: out in, up down, right left
			self.SERVO_PWM_LIMITS[TIP_MOTOR] = [c_0_TIP_MOTOR_OUT, 	c_0_TIP_MOTOR_IN]
			self.SERVO_PWM_LIMITS[MID_MOTOR] = [c_0_MID_MOTOR_UP, 	c_0_MID_MOTOR_DOWN]
			self.SERVO_PWM_LIMITS[ROT_MOTOR] = [c_0_ROT_MOTOR_RIGHT,c_0_ROT_MOTOR_LEFT]
		elif leg_num == LEG_1:
			self.SERVO_PWM_LIMITS[TIP_MOTOR] = [c_1_TIP_MOTOR_OUT, 	c_1_TIP_MOTOR_IN]
			self.SERVO_PWM_LIMITS[MID_MOTOR] = [c_1_MID_MOTOR_UP, 	c_1_MID_MOTOR_DOWN]
			self.SERVO_PWM_LIMITS[ROT_MOTOR] = [c_1_ROT_MOTOR_RIGHT,c_1_ROT_MOTOR_LEFT]
		elif leg_num == LEG_2:
			self.SERVO_PWM_LIMITS[TIP_MOTOR] = [c_2_TIP_MOTOR_OUT, 	c_2_TIP_MOTOR_IN]
			self.SERVO_PWM_LIMITS[MID_MOTOR] = [c_2_MID_MOTOR_UP, 	c_2_MID_MOTOR_DOWN]
			self.SERVO_PWM_LIMITS[ROT_MOTOR] = [c_2_ROT_MOTOR_RIGHT,c_2_ROT_MOTOR_LEFT]
		elif leg_num == LEG_3:
			self.SERVO_PWM_LIMITS[TIP_MOTOR] = [c_3_TIP_MOTOR_OUT, 	c_3_TIP_MOTOR_IN]
			self.SERVO_PWM_LIMITS[MID_MOTOR] = [c_3_MID_MOTOR_UP, 	c_3_MID_MOTOR_DOWN]
			self.SERVO_PWM_LIMITS[ROT_MOTOR] = [c_3_ROT_MOTOR_RIGHT,c_3_ROT_MOTOR_LEFT]
		elif leg_num == LEG_4:
			self.SERVO_PWM_LIMITS[TIP_MOTOR] = [c_4_TIP_MOTOR_OUT, 	c_4_TIP_MOTOR_IN]
			self.SERVO_PWM_LIMITS[MID_MOTOR] = [c_4_MID_MOTOR_UP, 	c_4_MID_MOTOR_DOWN]
			self.SERVO_PWM_LIMITS[ROT_MOTOR] = [c_4_ROT_MOTOR_RIGHT,c_4_ROT_MOTOR_LEFT]
		elif leg_num == LEG_5:
			self.SERVO_PWM_LIMITS[TIP_MOTOR] = [c_5_TIP_MOTOR_OUT, 	c_5_TIP_MOTOR_IN]
			self.SERVO_PWM_LIMITS[MID_MOTOR] = [c_5_MID_MOTOR_UP, 	c_5_MID_MOTOR_DOWN]
			self.SERVO_PWM_LIMITS[ROT_MOTOR] = [c_5_ROT_MOTOR_RIGHT,c_5_ROT_MOTOR_LEFT]
		elif leg_num == ARM_R:
			# arm: out in, out in, up down
			self.SERVO_PWM_LIMITS[TIP_MOTOR] = [c_R_ARM_TIP_MOTOR_OUT, 	c_R_ARM_TIP_MOTOR_IN]
			self.SERVO_PWM_LIMITS[MID_MOTOR] = [c_R_ARM_MID_MOTOR_OUT, 	c_R_ARM_MID_MOTOR_IN]
			self.SERVO_PWM_LIMITS[ROT_MOTOR] = [c_R_ARM_ROT_MOTOR_UP,	c_R_ARM_ROT_MOTOR_DOWN]
		elif leg_num == ARM_L:
			self.SERVO_PWM_LIMITS[TIP_MOTOR] = [c_L_ARM_TIP_MOTOR_OUT, 	c_L_ARM_TIP_MOTOR_IN]
			self.SERVO_PWM_LIMITS[MID_MOTOR] = [c_L_ARM_MID_MOTOR_OUT, 	c_L_ARM_MID_MOTOR_IN]
			self.SERVO_PWM_LIMITS[ROT_MOTOR] = [c_L_ARM_ROT_MOTOR_UP,	c_L_ARM_ROT_MOTOR_DOWN]
		elif leg_num == WAIST:
			# waist: left right
			self.SERVO_PWM_LIMITS[WAIST_MOTOR] = [c_ROTATOR_MOTOR_LEFT, c_ROTATOR_MOTOR_RIGHT]
		

		self.SERVO_ANGLE_LIMITS = [[0,1],[0,1],[0,1]]
		if(leg_num == ARM_L or leg_num == ARM_R):
			# arm: out in, out in, up down
			self.SERVO_ANGLE_LIMITS[TIP_MOTOR] = [ARM_TIP_MOTOR_OUT_ANGLE, 	ARM_TIP_MOTOR_IN_ANGLE]
			self.SERVO_ANGLE_LIMITS[MID_MOTOR] = [ARM_MID_MOTOR_OUT_ANGLE, 	ARM_MID_MOTOR_IN_ANGLE]
			self.SERVO_ANGLE_LIMITS[ROT_MOTOR] = [ARM_ROT_MOTOR_UP_ANGLE, 	ARM_ROT_MOTOR_DOWN_ANGLE]
		elif leg_num == WAIST:
			# waist: left right
			self.SERVO_ANGLE_LIMITS[WAIST_MOTOR] = [ROTATOR_LEFT_ANGLE, ROTATOR_RIGHT_ANGLE]
		else:
			# leg: out in, up down, right left
			self.SERVO_ANGLE_LIMITS[TIP_MOTOR] = [TIP_MOTOR_OUT_ANGLE, 	TIP_MOTOR_IN_ANGLE]
			self.SERVO_ANGLE_LIMITS[MID_MOTOR] = [MID_MOTOR_UP_ANGLE, 	MID_MOTOR_DOWN_ANGLE]
			self.SERVO_ANGLE_LIMITS[ROT_MOTOR] = [ROT_MOTOR_RIGHT_ANGLE,ROT_MOTOR_LEFT_ANGLE]
			

		# declare these member variables, immediately have value overwritten...
		self.curr_servo_angle = [-1, -1, -1]
		self.curr_servo_pwm =   [-1, -1, -1]
		
		# ...this code should overwrite the "-1"s with sensible values on bootup
		# NEEDS to use the non-thread versions
		if(leg_num == ARM_L or leg_num == ARM_R):
			# default position is with arms fully extended
			self.set_leg_position(TORSO_ARM_TABLE["STRAIGHT_OUT"])
		elif(leg_num == WAIST):
			self.set_servo_angle(90, WAIST_MOTOR)
		else:
			# default position is 90-degree crouch
			# self.set_leg_position(MISC_TABLE["STRAIGHT_OUT"])
			self.set_leg_position(MISC_TABLE["INIT"])

		# start the thread
		self.framethread.start()


	def print_self(self):
		print("leg uid : " + str(self.uid) + " ===========================")
		print("on channels : tip/mid/rot = " + str(self.pwm_channels))
		print("servo PWMs: tip/mid/rot = " + str(self.curr_servo_pwm))
		print("servo angles: tip/mid/rot = " + str(self.curr_servo_angle))
		print("frame queue size: " + str(len(self.frame_queue)))


	# conversion functions: use linear mapping from input to output
	def angle_to_pwm(self, angle, motor):
		if motor < 0 or motor > 2:
			print("ERR#1: INVALID PARAM")
			return INV_PARAM
		return linear_map(self.SERVO_ANGLE_LIMITS[motor][0], self.SERVO_PWM_LIMITS[motor][0], 
						self.SERVO_ANGLE_LIMITS[motor][1], self.SERVO_PWM_LIMITS[motor][1], 
						angle)
		
	def pwm_to_angle(self, pwm, motor):
		if motor < 0 or motor > 2:
			print("ERR#2: INVALID PARAM")
			return INV_PARAM
		return linear_map(self.SERVO_PWM_LIMITS[motor][0], self.SERVO_ANGLE_LIMITS[motor][0], 
						self.SERVO_PWM_LIMITS[motor][1], self.SERVO_ANGLE_LIMITS[motor][1], 
						pwm)

	def percent_to_angle(self, percent, motor):
		# maps 0-100 to each motor's min and max angle values
		if motor < 0 or motor > 2:
			print("ERR#3: INVALID PARAM")
			return INV_PARAM
		return linear_map(100, self.SERVO_ANGLE_LIMITS[motor][0], 
						0, self.SERVO_ANGLE_LIMITS[motor][1], 
						angle)

	# convert-then-set functions:
	def set_servo_percent(self, percent, motor):
		# convert and pass off to set_servo_angle
		self.set_servo_angle(self.percent_to_angle(percent, motor), motor)
	def set_servo_pwm(self, pwm, motor):
		# convert and pass off to set_servo_angle
		self.set_servo_angle(self.angle_to_pwm(pwm, motor), motor)

	# the old-fashioned "do the thing" command: clamps value to safety limits, ensures it won't collide with any thread operations, and calls do_set_servo_angle
	def set_servo_angle(self, angle, motor):
		if angle < 0 or angle > 360:
			print("ERR#4: INVALID PARAM")
			return INV_PARAM
		if motor < 0 or motor > 2:
			print("ERR#5: INVALID PARAM")
			return INV_PARAM

		# wait until running_flag is clear (idle_flag is set)
		# this ensures that it won't conflict with the thread if it is running
		# you SHOULDN'T be using both the thread and the direct-set method, but better to be safe than sorry
		self.idle_flag.wait()
		
		# safety checking for each motor
		safe_angle = bidirectional_clamp(angle, self.SERVO_ANGLE_LIMITS[motor][0], self.SERVO_ANGLE_LIMITS[motor][1])
		
		return self.do_set_servo_angle(safe_angle, motor)
		
		
	# creates a temporary "leg position" object to give to the leg_position_thread function
	# changes the given motor to the given position over the given time
	# OTHER MOTORS CANNOT CHANGE WHILE THIS IS CHANGING, to change multiple motors at a time use set_leg_position_thread
	def set_servo_angle_thread(self, angle, motor, time):
		# # TODO: if the Leg_Position object is changed to list-style, i can use:
		# v = self.curr_servo_angle.copy() # explicitly make a copy
		# v[motor] = angle # modify the copy
		# L = Leg_Position(v)
		
		L = None
		if motor == TIP_MOTOR or motor == WAIST_MOTOR:
			L = Leg_Position(angle, self.curr_servo_angle[1], self.curr_servo_angle[2])			
		if motor == MID_MOTOR:
			L = Leg_Position(self.curr_servo_angle[0], angle, self.curr_servo_angle[2])			
		if motor == ROT_MOTOR:
			L = Leg_Position(self.curr_servo_angle[0], self.curr_servo_angle[1], angle)
		self.set_leg_position_thread(L, time)
		
	
	# uses the "leg_position" objects, immediate set (no threading)
	def set_leg_position(self, leg_position):
		self.set_servo_angle(leg_position.tip_motor, TIP_MOTOR)
		self.set_servo_angle(leg_position.mid_motor, MID_MOTOR)
		self.set_servo_angle(leg_position.rot_motor, ROT_MOTOR)

	# safety clamp (in angle space) 
	# interpolate (in angle space)
	# adds commands to the command queue (with lock)
	# sets the "running" flag unconditionally (note: no harm in setting an already set flag)
	# * thread will jump in with "do_set_servo_angle" when it is the correct time
	def set_leg_position_thread(self, leg_position, time):
		# assemble command from the leg position
		# TODO: add a time component to the leg position object? or make a new object type? or just build the command like this? not sure how to best integrate/use this system
		command = [0, 0, 0, time]
		
		# safety checking for each motor
		command[TIP_MOTOR] = bidirectional_clamp(leg_position.tip_motor, 
					self.SERVO_ANGLE_LIMITS[TIP_MOTOR][0], self.SERVO_ANGLE_LIMITS[TIP_MOTOR][1])
		command[MID_MOTOR] = bidirectional_clamp(leg_position.mid_motor, 
					self.SERVO_ANGLE_LIMITS[MID_MOTOR][0], self.SERVO_ANGLE_LIMITS[MID_MOTOR][1])
		command[ROT_MOTOR] = bidirectional_clamp(leg_position.rot_motor, 
					self.SERVO_ANGLE_LIMITS[ROT_MOTOR][0], self.SERVO_ANGLE_LIMITS[ROT_MOTOR][1])
		
		
		# if there is a queued interpolation frame, interpolate from the final frame in the queue to the desired pose.
		# otherwise, interpolate from current position.
		lastframe = []
		with self._frame_queue_lock:
			if len(self.frame_queue) > 0:
				# be sure it is a copy and not a reference, just to be safe
				lastframe = list(self.frame_queue[-1])
		if lastframe == []:   # "else" but outside of the lock block
			lastframe = self.curr_servo_angle
		
		# run interpolation
		# NOTE: "command" must have 4 elements, "lastframe" only needs 3, the 4th is just unused
		interpolate_list = interpolate(command, lastframe)
		
		# add new frames onto the END of the frame queue (with lock)
		with self._frame_queue_lock:
			self.frame_queue = self.frame_queue + interpolate_list
			if LEG_THREAD_DEBUG and self.uid == 0:
				print("leg_" + str(self.uid) + ": add " + str(len(interpolate_list)) + " frames to frame_queue, new length is " + str(len(self.frame_queue)))
		
		with self._state_flag_lock:
			# clear "sleeping" event, does not trigger anything (note: clear before set)
			self.idle_flag.clear()
			# set the "running" event, this may trigger other waiting tasks
			self.running_flag.set()
		
		

	# clear the frame queue to stop any currently-pending movements.
	# note that when the hexwalker calls this it should first abort() all legs, THEN call "synchronize" on all legs. 
	# this way it doesn't wait for one leg to stop before clearing the queue of the next.
	def abort(self):
		with self._frame_queue_lock: 
			self.frame_queue = []
		
	
	# internal-use-only function
	# set the actual PWM and the internally-tracked position
	# guarantees that the determined PWM value isn't too crazy
	def do_set_servo_angle(self, angle, servo):
		if servo < 0 or servo > 2:
			# ensure servo index is valid
			print("ERR#6: INVALID SERVO INDEX! valid values are 0 to 2")
			print("leg="+str(self.uid)+", servo="+str(servo)+", angle="+str(angle))
			return INV_PARAM
		# convert to pwm
		pwm_val = int(self.angle_to_pwm(angle, servo))
		
		if pwm_val < c_PWM_ABSOLUTE_MINIMUM or pwm_val > c_PWM_ABSOLUTE_MAXIMUM:
			# guarantee somewhat-sensible PWM value
			print("ERR#7: UNSAFE PWM! safe values are "+str(c_PWM_ABSOLUTE_MINIMUM)+" to "+str(c_PWM_ABSOLUTE_MAXIMUM))
			print("leg="+str(self.uid)+", servo="+str(servo)+", angle="+str(angle)+", pwm="+str(pwm_val))
			# TODO: raise an exception of some kind??
			return INV_PARAM
		
		# # do the write out, with lock just to be safe
		with self._curr_pos_lock:
			self.curr_servo_angle[servo] = angle
			self.curr_servo_pwm[servo] = pwm_val
			self.pwm.set_pwm(self.pwm_channels[servo], 0, pwm_val)
			
		return SUCCESS


# make the "rotator" class a subclass of "leg"
# any functions that would work on a leg also work on the rotator, it inherits absolutely everything
# redefines do_set_servo_angle to only touch the one servo, ignore other two
# to use this with threading it will need to use set_servo_angle_thread(angle, motor, time)
# technically you can try to set the other 2 leg motors and it won't crash but nothing will happen unless you are setting the waist motor
class Rotator(Leg):
	# internal-use-only function
	# if servo is not WAIST_MOTOR, then return & do nothing... otherwise call normal do_set_servo_angle()
	def do_set_servo_angle(self, angle, servo):
		if servo != WAIST_MOTOR:
			# print("ERR#10: INVALID PARAM")
			return INV_PARAM
		# if it is valid, do the exact same code as the Leg would
		return super().do_set_servo_angle(angle, servo)



class Hex_Walker(object):
	def __init__(self, rf_leg, rm_leg, rb_leg, lb_leg, lm_leg, lf_leg):
	
		# TODO: make the leg objects live in an actual list so we can iterate over it
		
		# this is an initial array that serves as a permanent holder
		# these need to stay
		self.leg0 = rf_leg
		self.leg1 = rm_leg
		self.leg2 = rb_leg
		self.leg3 = lb_leg
		self.leg4 = lm_leg
		self.leg5 = lf_leg
		
		# leglist indexed by LEG_RM, etc
		self.leglist = [rf_leg, rm_leg, rb_leg, lb_leg, lm_leg, lf_leg]

		# now, we assign meaningful values in order to define the "front"
		# TODO: replace this with a list, indexed by "LEG_LF" "LEG_RB" etc
		self.front = "5-0"
		self.lf_leg = lf_leg
		self.lm_leg = lm_leg
		self.lb_leg = lb_leg
		self.rf_leg = rf_leg
		self.rm_leg = rm_leg
		self.rb_leg = rb_leg

		# create the lists of leg combinations that would be useful
		self.all_legs = [rf_leg, rm_leg, rb_leg, lb_leg, lm_leg, lf_leg]
		self.left_legs = [lf_leg, lm_leg, lb_leg]
		self.right_legs = [rf_leg, rm_leg, rb_leg]
		self.left_triangle = [lf_leg, rm_leg, lb_leg]
		self.right_triangle = [rf_leg, lm_leg, rb_leg]
		self.front_legs = [lf_leg, rf_leg]
		self.mid_legs = [lm_leg, rm_leg]
		self.rear_legs = [lb_leg, rb_leg]

		# set operating mode
		self.current_pos = NORMAL_NEUTRAL
		self.speed = NORMAL
		self.front = "5-0"
		# set all legs to neutral
		self.set_hexwalker_position(TALL_NEUTRAL)

	def print_self(self):
		print("speed: " + str(self.speed) + " || self.current_pos: " + str(self.current_pos) + " || self.front: " + self.front)
		for leg in self.all_legs:
			leg.print_self()

	def set_speed(self, new_speed):
		self.speed = new_speed

	# this function will change the front from being between the "5-0" legs to being
	# between any two legs. The key is "(leg on frontleft)-(leg on frontright)"
	def set_new_front(self, new_front):
		cp = self.current_pos
		if(cp != TALL_NEUTRAL and cp != NORMAL_NEUTRAL and cp != CROUCH_NEUTRAL):
			print("Cannot change front while not in the neutral position")
			return ILLEGAL_MOVE
		
		# check for which side should be the front and re-assign the legs
		# accordingly
		if( new_front == "0-1" ):
			self.rf_leg = self.leg1
			self.rm_leg = self.leg2
			self.rb_leg = self.leg3
			self.lb_leg = self.leg4
			self.lm_leg = self.leg5
			self.lf_leg = self.leg0
			self.front = new_front
			return SUCCESS

		elif( new_front == "1-2" ):
			self.rf_leg = self.leg2
			self.rm_leg = self.leg3
			self.rb_leg = self.leg4
			self.lb_leg = self.leg5
			self.lm_leg = self.leg0
			self.lf_leg = self.leg1
			self.front = new_front
			return SUCCESS

		elif( new_front == "2-3" ):
			self.rf_leg = self.leg3
			self.rm_leg = self.leg4
			self.rb_leg = self.leg5
			self.lb_leg = self.leg0
			self.lm_leg = self.leg1
			self.lf_leg = self.leg2
			self.front = new_front
			return SUCCESS

		elif( new_front == "3-4" ):
			self.rf_leg = self.leg4
			self.rm_leg = self.leg5
			self.rb_leg = self.leg0
			self.lb_leg = self.leg1
			self.lm_leg = self.leg2
			self.lf_leg = self.leg3
			self.front = new_front
			return SUCCESS

		elif( new_front == "4-5" ):
			self.rf_leg = self.leg5
			self.rm_leg = self.leg0
			self.rb_leg = self.leg1
			self.lb_leg = self.leg2
			self.lm_leg = self.leg3
			self.lf_leg = self.leg4
			self.front = new_front
			return SUCCESS

		elif( new_front == "5-0" ):
			self.rf_leg = self.leg0
			self.rm_leg = self.leg1
			self.rb_leg = self.leg2
			self.lb_leg = self.leg3
			self.lm_leg = self.leg4
			self.lf_leg = self.leg5
			self.front = new_front
			return SUCCESS

		else:
			print("invalid front specified") 
			return INV_PARAM


	## take a list of INDICES of poses to run through.
	# safety: for each transition, checks that the next pose is listed as a "safe pose" of the current pose
	def run_move_list(self, hex_walker_position_list):
		for next_pos in hex_walker_position_list:
			if next_pos in HEX_WALKER_POSITIONS[self.current_pos].safe_moves:
				if HW_MOVE_DEBUG:
					print("Sending command")
				self.set_hexwalker_position(next_pos)
				self.synchronize()
			else:
				print("invalid move set")
				return ILLEGAL_MOVE
		return SUCCESS
	
	
	## used to set the pose of the whole 6-leg system and update "current pose" if possible.
	# hexwalker_pose_id can be index or object. 
	# if index, update current_pos. if object, don't, because it was probably dynamically created.
	# optional arg with speed
	def set_hexwalker_position(self, hexwalker_pose_id, time=self.speed):
		if isinstance(hexwalker_pose_id, int):
			# if it is an index, then update current_pos and do the rest of the thing
			self.current_pos = hexwalker_pose_id
			pose = HEX_WALKER_POSITIONS[hexwalker_pose_id]
			if(HW_MOVE_DEBUG):
				print("current pose is: " + HEX_WALKER_POSITIONS[self.current_pos].description + ", moving to pose: " + pose.description)
		else:
			# if it is the actual object, then it was probably dynamically created. don't update pose, dont print debug description
			pose = hexwalker_pose_id
		
		# self.set_hexwalker_leg_position(pose, GROUP_ALL_LEGS, self.speed)
		self.set_hexwalker_leg_position(pose)


	## used to set the pose of some/all of the while keeping other legs untouched.
	## if using threading, can set multiple simultaneous leg transitions with different durations by calling 
	## this multiple times without synchronize() between.
	# if given dest=Leg_Position, set all specified legs to that same pose
	# if given dest=Hex_Walker_Position, set all specified legs to the pose corresponding to that leg within the Hex_Walker_Position object
	# leglist can be int or list, or none (defaults to all legs)
	# optional arg with speed
	# check USE_THREADING and call set_leg_position or set_leg_position_thread 
	def set_hexwalker_leg_position(self, dest, leglist=GROUP_ALL_LEGS, time=self.speed):
		# leglist: if given a single index rather than an iteratable, make it into a set
		# if given something else, cast the leglist as a set to remove potential duplicates
		legs = set((leglist)) if isinstance(leglist, int) else set(leglist)
		
		if isinstance(dest, Hex_Walker_Position):
			if USE_THREADING:
				for n in legs:
					# extract the appropriate pose from the object
					# TODO: listify the Hex_Walker_Position object and eliminate this case-statement chain
					if n == LEG_RF:
						pose = dest.rf_pos
					elif n == LEG_RM:
						pose = dest.rm_pos
					elif n == LEG_RB:
						pose = dest.rr_pos
					elif n == LEG_LB:
						pose = dest.lr_pos
					elif n == LEG_LM:
						pose = dest.lm_pos
					elif n == LEG_LF:
						pose = dest.lf_pos
					self.idx_to_leg(n).set_leg_position_thread(pose, time)
			else:
				for n in legs:
					# extract the appropriate pose from the object
					# TODO: listify the Hex_Walker_Position object and eliminate this case-statement chain
					if n == LEG_RF:
						pose = dest.rf_pos
					elif n == LEG_RM:
						pose = dest.rm_pos
					elif n == LEG_RB:
						pose = dest.rr_pos
					elif n == LEG_LB:
						pose = dest.lr_pos
					elif n == LEG_LM:
						pose = dest.lm_pos
					elif n == LEG_LF:
						pose = dest.lf_pos
					self.idx_to_leg(n).set_leg_position(pose)
		elif isinstance(dest, Leg_Position):
			if USE_THREADING:
				for leg in [self.idx_to_leg(n) for n in legs]:
					# threading version
					leg.set_leg_position_thread(dest, time)
			else:
				for leg in [self.idx_to_leg(n) for n in legs]:
					# non-threading version
					leg.set_leg_position(dest)
		else:
			print("ERROR: given invalid hexwalker leg position type")



	# synchronize the legs with the main thread by not returning until all of the specified legs are done moving
	# accepts list, set, int (treated as single-element set)
	# if not given any arg, default is GROUP_ALL_LEGS
	# depending on USE_THREADING, either simply sleep or do the actual synchro
	def synchronize(self, masklist=GROUP_ALL_LEGS):
		if USE_THREADING:
			# if given a single index rather than an iteratable, make it into a set
			# if given something else, cast the masklist as a set to remove potential duplicates
			mask = set((masklist)) if isinstance(masklist, int) else set(masklist)
			
			for leg in [self.idx_to_leg(n) for n in mask]:
				# wait until the leg is done, if it is already done this returns immediately
				leg.idle_flag.wait()
		else:
			time.sleep(self.speed)
		
		
	# convert given index to the actual leg object... trivial but whatever
	# TODO: apply custom "front" offset here
	def idx_to_leg(self, n):
		return self.leglist[n]
	
	
	# abort all queued leg thread movements, and wait a bit to ensure they all actually stopped.
	# their "current angle/pwm" variables should still be correct, unless it was trying to move beyond its range somehow.
	def abort(self):
		# first clear all the queues
		for leg in self.leglist:
			leg.abort()
		# then wait until all legs returned to "sleeping" state
		self.synchronize(self.leglist)
		# then wait for 3x the interpolate time, just to be safe
		time.sleep(INTERPOLATE_TIME * 3)


	########################################################################################
	########################################################################################
	# movement functions
	def walk(self, num_steps, direction):
		
		self.set_new_front(get_front_from_direction(direction))
		if HW_MOVE_DEBUG:
			print("walk dir: " + get_front_from_direction(direction))
		
		# start walk by lifting legs
		self.set_hexwalker_position(TALL_TRI_RIGHT_NEUTRAL_LEFT_UP_NEUTRAL)
		# define positions to go through to get steps from a neutral legs up
		left_step = [
		TALL_TRI_RIGHT_BACK_LEFT_UP_FORWARD,
		TALL_TRI_RIGHT_BACK_LEFT_FORWARD,
		TALL_TRI_RIGHT_UP_BACK_LEFT_FORWARD,
		TALL_TRI_RIGHT_UP_NEUTRAL_LEFT_NEUTRAL ]
		
		right_step = [
		TALL_TRI_RIGHT_UP_FORWARD_LEFT_BACK,
		TALL_TRI_RIGHT_FORWARD_LEFT_BACK,
		TALL_TRI_RIGHT_FORWARD_LEFT_UP_BACK,
		TALL_TRI_RIGHT_NEUTRAL_LEFT_UP_NEUTRAL ]
		
		last_step = "right"

		for i in range (0, num_steps):
			if(last_step == "right"):
				self.run_move_list(left_step)
				last_step = "left"
			elif(last_step == "left"):
				self.run_move_list(right_step)
				last_step = "right"
		#cleanup
		self.set_hexwalker_position(TALL_NEUTRAL)
		self.set_new_front("5-0")

	def rotate(self, num_steps, direction):
		
		# start rotate by lifting legs
		self.set_hexwalker_position(TALL_TRI_RIGHT_UP_NEUTRAL_LEFT_NEUTRAL)
		# define positions to go through to get steps from neutral legs up
		go_left_right_step = [
		TALL_TRI_RIGHT_RIGHT_LEFT_UP_LEFT,
		TALL_TRI_RIGHT_RIGHT_LEFT_LEFT,
		TALL_TRI_RIGHT_UP_RIGHT_LEFT_LEFT,
		TALL_TRI_RIGHT_UP_NEUTRAL_LEFT_NEUTRAL]

		go_left_left_step = [
		TALL_TRI_RIGHT_UP_LEFT_LEFT_RIGHT,
		TALL_TRI_RIGHT_LEFT_LEFT_RIGHT,
		TALL_TRI_RIGHT_LEFT_LEFT_UP_RIGHT,
		TALL_TRI_RIGHT_NEUTRAL_LEFT_UP_NEUTRAL]

		go_right_right_step = [
		TALL_TRI_RIGHT_LEFT_LEFT_UP_RIGHT,
		TALL_TRI_RIGHT_LEFT_LEFT_RIGHT,
		TALL_TRI_RIGHT_UP_LEFT_LEFT_RIGHT,
		TALL_TRI_RIGHT_UP_NEUTRAL_LEFT_NEUTRAL]

		go_right_left_step = [
		TALL_TRI_RIGHT_UP_RIGHT_LEFT_LEFT,
		TALL_TRI_RIGHT_RIGHT_LEFT_LEFT,
		TALL_TRI_RIGHT_RIGHT_LEFT_UP_LEFT,
		TALL_TRI_RIGHT_NEUTRAL_LEFT_UP_NEUTRAL]

		if(direction == RIGHT):
			left_step = go_right_left_step
			right_step = go_right_right_step
		if(direction == LEFT):
			left_step = go_left_left_step
			right_step = go_left_right_step

		last_step = "right"
		for i in range (0, num_steps):
			if(last_step == "right"):
				self.run_move_list(left_step)
				last_step = "left"
			elif(last_step == "left"):
				self.run_move_list(right_step)
				last_step = "right"
		#cleanup
		self.set_hexwalker_position(TALL_NEUTRAL)

	def fine_rotate(self, num_steps, direction):
		
		# start rotate by lifting legs
		self.set_hexwalker_position(TALL_TRI_RIGHT_UP_NEUTRAL_LEFT_NEUTRAL)
		# define positions to go through to get steps from neutral legs up
		go_left_right_step = [
		TALL_TRI_FINE_RIGHT_RIGHT_LEFT_UP_LEFT,
		TALL_TRI_FINE_RIGHT_RIGHT_LEFT_LEFT,
		TALL_TRI_FINE_RIGHT_UP_RIGHT_LEFT_LEFT,
		TALL_TRI_RIGHT_UP_NEUTRAL_LEFT_NEUTRAL]

		go_left_left_step = [
		TALL_TRI_FINE_RIGHT_UP_LEFT_LEFT_RIGHT,
		TALL_TRI_FINE_RIGHT_LEFT_LEFT_RIGHT,
		TALL_TRI_FINE_RIGHT_LEFT_LEFT_UP_RIGHT,
		TALL_TRI_RIGHT_NEUTRAL_LEFT_UP_NEUTRAL]

		go_right_right_step = [
		TALL_TRI_FINE_RIGHT_LEFT_LEFT_UP_RIGHT,
		TALL_TRI_FINE_RIGHT_LEFT_LEFT_RIGHT,
		TALL_TRI_FINE_RIGHT_UP_LEFT_LEFT_RIGHT,
		TALL_TRI_RIGHT_UP_NEUTRAL_LEFT_NEUTRAL]

		go_right_left_step = [
		TALL_TRI_FINE_RIGHT_UP_RIGHT_LEFT_LEFT,
		TALL_TRI_FINE_RIGHT_RIGHT_LEFT_LEFT,
		TALL_TRI_FINE_RIGHT_RIGHT_LEFT_UP_LEFT,
		TALL_TRI_RIGHT_NEUTRAL_LEFT_UP_NEUTRAL]

		if(direction == RIGHT):
			left_step = go_right_left_step
			right_step = go_right_right_step
		if(direction == LEFT):
			left_step = go_left_left_step
			right_step = go_left_right_step

		last_step = "right"
		for i in range (0, num_steps):
			if(last_step == "right"):
				self.run_move_list(left_step)
				last_step = "left"
			elif(last_step == "left"):
				self.run_move_list(right_step)
				last_step = "right"
		#cleanup
		self.set_hexwalker_position(TALL_NEUTRAL)

	# "ripple" the legs around the robot in one direction or the other
	def leg_wave(self, direction, speed, repetitions):
		for i in range(0, repetitions):
			if(direction == RIGHT):
				for n in GROUP_ALL_LEGS:
					# pull_up = (60, 75, 90), tip above horizontal
					# normal neutral = (120, 90, 90)
					# crouch neutral = (45, 135, 90)
					self.set_hexwalker_leg_position(MISC_TABLE["PULL_UP"], n, speed)
					self.synchronize()
					# tall neutral = (120, 45, 90)
					self.set_hexwalker_leg_position(TALL_TRI_MOVEMENT_TABLE["NEUTRAL"], n, speed)
			if(direction == LEFT):
				reverselist = GROUP_ALL_LEGS.copy()
				reverselist.reverse()
				for n in reverselist:
					self.set_hexwalker_leg_position(MISC_TABLE["PULL_UP"], n, speed)
					self.synchronize()
					self.set_hexwalker_leg_position(TALL_TRI_MOVEMENT_TABLE["NEUTRAL"], n, speed)
		# one last synchronize() for the final movement to complete
		self.synchronize()

	# tea-bag
	def bounce(self, wait, repetitions):
		for i in range(0, repetitions):
			self.set_hexwalker_position(TALL_TRI_BOUNCE_DOWN, wait)
			self.synchronize()
			self.set_hexwalker_position(TALL_NEUTRAL, wait)
			self.synchronize()

	def do_nothing(self):
		self.set_hexwalker_position(TALL_NEUTRAL)
		
	########################################################################################
	########################################################################################



class Robot_Torso(object):
	def __init__(self, right_arm, left_arm, rotator):
		self.right_arm = right_arm
		self.left_arm = left_arm
		self.rotator = rotator
		self.current_position = TORSO_NEUTRAL
		self.set_torso_position(TORSO_NEUTRAL, 90)

	def set_torso_position(self, torso_position_number, rotation):
		self.current_position = torso_position_number
		self.do_set_torso_position(TORSO_POSITIONS[torso_position_number], rotation)

	def do_set_torso_position(self, torso_position, rotation):
		self.right_arm.set_leg_position(torso_position.right_arm)
		self.left_arm.set_leg_position(torso_position.left_arm)
		self.rotator.set_servo_angle(rotation, WAIST_MOTOR)

	def do_moveset(self, positions, rotations, sleeps, repetitions):
		for j in range(0, repetitions):
			for i in range(0, len(positions)):
				self.set_torso_position(positions[i], rotations[i])
				time.sleep(sleeps[i])

	def set_torso_rotation(self, rotation):
		self.rotator.set_servo_angle(rotation, WAIST_MOTOR)

	# torso movement functions
	def monkey(self, repetitions):
		moves = []
		moves.append(TORSO_MONKEY_RIGHT_UP)
		moves.append(TORSO_MONKEY_LEFT_UP)
		moves.append(TORSO_MONKEY_RIGHT_UP)
		moves.append(TORSO_MONKEY_LEFT_UP)
		moves.append(TORSO_MONKEY_RIGHT_UP)
		moves.append(TORSO_MONKEY_LEFT_UP)
		moves.append(TORSO_MONKEY_RIGHT_UP)
		moves.append(TORSO_MONKEY_LEFT_UP)
		moves.append(TORSO_MONKEY_RIGHT_UP)
		moves.append(TORSO_MONKEY_LEFT_UP)
		moves.append(TORSO_MONKEY_RIGHT_UP)
		moves.append(TORSO_MONKEY_LEFT_UP)
		moves.append(TORSO_MONKEY_RIGHT_UP)
		moves.append(TORSO_MONKEY_LEFT_UP)
		moves.append(TORSO_MONKEY_RIGHT_UP)
		moves.append(TORSO_MONKEY_LEFT_UP)
		rotations = [45, 45, 45, 45, 45, 45, 45, 45, 135, 135, 135, 135, 135, 135, 135,135]
		sleeps =	[.1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1]
		self.do_moveset(moves, rotations, sleeps, repetitions)
		self.set_torso_position(TORSO_NEUTRAL, 90)
	
	def look(self):
		self.set_torso_position(TORSO_LOOKING, 90)

	def point(self, direction, duration):
		if(direction == RIGHT):
			self.set_torso_position(TORSO_POINTING_RIGHT, 90)
		else:
			self.set_torso_position(TORSO_POINTING_LEFT, 90)
		time.sleep(duration)
		self.set_torso_position(TORSO_NEUTRAL, 90)

	def king_kong(self, rotation, repetitions):
		moves = []
		moves.append(TORSO_DANCE_FRONT_LEFT_OUT)
		moves.append(TORSO_DANCE_FRONT_RIGHT_OUT)
		rotations = [rotation, rotation]
		sleeps = [.4, .4]
		self.do_moveset(moves, rotations, sleeps, repetitions)
		self.set_torso_position(TORSO_NEUTRAL, 90)
	
	def stab(self, rotation, repetitions):
		moves = []
		moves.append(TORSO_POINTING_LEFT)
		rotations = [rotation]
		sleeps = [.4, .4]
		self.do_moveset(moves, rotations, sleeps, repetitions)
		self.set_torso_rotation(rotation)

	def hand_shake(self, rotation, repetitions):
		moves = []
		moves.append(TORSO_SHAKE_DOWN)
		moves.append(TORSO_SHAKE_MID)
		moves.append(TORSO_SHAKE_UP)
		moves.append(TORSO_SHAKE_MID)
		rotations = [rotation, rotation, rotation, rotation]
		sleeps = [.1, .1, .1, .1]
		self.do_moveset(moves, rotations, sleeps, repetitions)
		self.set_torso_position(TORSO_NEUTRAL, 90)
	
	def wave(self, rotation, repetitions):
		moves = []
		moves.append(TORSO_WAVE_DOWN)
		moves.append(TORSO_WAVE_UP)
		rotations = [rotation, rotation]
		sleeps = [.4, .4]
		self.do_moveset(moves, rotations, sleeps, repetitions)
		self.set_torso_position(TORSO_NEUTRAL, 90)

	def neutral_rotate(self, direction):
		self.set_torso_position(TORSO_NEUTRAL, direction)

	def do_nothing(self):
		self.set_torso_position(TORSO_NEUTRAL, 90)
