from __future__ import division
import time
import threading
from hex_walker_data import *
from leg_data import *
from torso_data import *

from hex_walker_constants import *
# from pwm_wrapper import *
from hex_util import *
from leg_thread import *

#Extraneous
HW_MOVE_DEBUG = 0 #toggle 0/1 to turn debug prints on/off

LEG_THREAD_DEBUG = True

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
# ??
DEBUG = 5



# NOTE: these values are ANGLES not raw pwms
class Leg_Position(object):
	def __init__(self, tip_motor, mid_motor, rot_motor):
		self.tip_motor = tip_motor
		self.mid_motor = mid_motor
		self.rot_motor = rot_motor

	def __str__(self):
		return "TIP : " + str(self.tip_motor) + " MID : " + str(self.mid_motor) + " ROT : " + str(self.rot_motor)

# a leg object should be able to associate itself with specific channels
# on a specific i2c interface address and then control all parts of the
# leg. It should be able to set each join according to a degree, max, min,
# or a value from 0-100 in terms of percent of maximum
class Leg(object):
	def __init__(self, pwm, channels, leg_num):

		# TODO: turn limit parameters into a list
		# TODO: turn "current position" vars into lists
		# these changes offer little practical benefit, just code cleanliness, but are potentially a real pain to transition to, so they are low-priority
		
		
		# unique ID, not actually used for much, just stores the leg_num
		self.uid = leg_num
		# this can be either the new-style PWM wrapper or the old-style actual pwm object, works just the same
		self.pwm = pwm
		# running/sleeping flags: normal Events can only wait for a rising edge, if I want to wait for a falling edge, i need to set up a complementary system like this. also they're really being used as flags, not as "events", but whatever
		self.running_flag = threading.Event()
		self.sleeping_flag = threading.Event()
		self.sleeping_flag.set()
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
		
		
		
		self.pwm_channels = channels		
		
		# now, assign the correct constants
		# TODO: self.SERVO_PWM_LIMITS = [[0,1],[0,1],[0,1]]
		if leg_num == LEG_0:
			self.TIP_MOTOR_OUT	  = c_0_TIP_MOTOR_OUT
			self.TIP_MOTOR_IN	   = c_0_TIP_MOTOR_IN
			self.MID_MOTOR_UP	   = c_0_MID_MOTOR_UP
			self.MID_MOTOR_DOWN	 = c_0_MID_MOTOR_DOWN
			self.ROT_MOTOR_RIGHT	= c_0_ROT_MOTOR_RIGHT
			self.ROT_MOTOR_LEFT	 = c_0_ROT_MOTOR_LEFT
			# TODO:
			# self.SERVO_PWM_LIMITS[TIP_MOTOR] = [c_0_TIP_MOTOR_OUT, 	c_0_TIP_MOTOR_IN]
			# self.SERVO_PWM_LIMITS[MID_MOTOR] = [c_0_MID_MOTOR_UP, 	c_0_MID_MOTOR_DOWN]
			# self.SERVO_PWM_LIMITS[ROT_MOTOR] = [c_0_ROT_MOTOR_RIGHT, 	c_0_ROT_MOTOR_LEFT]
		elif leg_num == LEG_1:
			self.TIP_MOTOR_OUT	  = c_1_TIP_MOTOR_OUT
			self.TIP_MOTOR_IN	   = c_1_TIP_MOTOR_IN
			self.MID_MOTOR_UP	   = c_1_MID_MOTOR_UP
			self.MID_MOTOR_DOWN	 = c_1_MID_MOTOR_DOWN
			self.ROT_MOTOR_RIGHT	= c_1_ROT_MOTOR_RIGHT
			self.ROT_MOTOR_LEFT	 = c_1_ROT_MOTOR_LEFT
		elif leg_num == LEG_2:
			self.TIP_MOTOR_OUT	  = c_2_TIP_MOTOR_OUT
			self.TIP_MOTOR_IN	   = c_2_TIP_MOTOR_IN
			self.MID_MOTOR_UP	   = c_2_MID_MOTOR_UP
			self.MID_MOTOR_DOWN	 = c_2_MID_MOTOR_DOWN
			self.ROT_MOTOR_RIGHT	= c_2_ROT_MOTOR_RIGHT
			self.ROT_MOTOR_LEFT	 = c_2_ROT_MOTOR_LEFT
		elif leg_num == LEG_3:
			self.TIP_MOTOR_OUT	  = c_3_TIP_MOTOR_OUT
			self.TIP_MOTOR_IN	   = c_3_TIP_MOTOR_IN
			self.MID_MOTOR_UP	   = c_3_MID_MOTOR_UP
			self.MID_MOTOR_DOWN	 = c_3_MID_MOTOR_DOWN
			self.ROT_MOTOR_RIGHT	= c_3_ROT_MOTOR_RIGHT
			self.ROT_MOTOR_LEFT	 = c_3_ROT_MOTOR_LEFT
		elif leg_num == LEG_4:
			self.TIP_MOTOR_OUT	  = c_4_TIP_MOTOR_OUT
			self.TIP_MOTOR_IN	   = c_4_TIP_MOTOR_IN
			self.MID_MOTOR_UP	   = c_4_MID_MOTOR_UP
			self.MID_MOTOR_DOWN	 = c_4_MID_MOTOR_DOWN
			self.ROT_MOTOR_RIGHT	= c_4_ROT_MOTOR_RIGHT
			self.ROT_MOTOR_LEFT	 = c_4_ROT_MOTOR_LEFT
		elif leg_num == LEG_5:
			self.TIP_MOTOR_OUT	  = c_5_TIP_MOTOR_OUT
			self.TIP_MOTOR_IN	   = c_5_TIP_MOTOR_IN
			self.MID_MOTOR_UP	   = c_5_MID_MOTOR_UP
			self.MID_MOTOR_DOWN	 = c_5_MID_MOTOR_DOWN
			self.ROT_MOTOR_RIGHT	= c_5_ROT_MOTOR_RIGHT
			self.ROT_MOTOR_LEFT	 = c_5_ROT_MOTOR_LEFT
		elif leg_num == ARM_R:
			self.TIP_MOTOR_OUT	  = c_R_ARM_TIP_MOTOR_OUT
			self.TIP_MOTOR_IN	   = c_R_ARM_TIP_MOTOR_IN
			self.MID_MOTOR_UP	   = c_R_ARM_MID_MOTOR_OUT
			self.MID_MOTOR_DOWN	 = c_R_ARM_MID_MOTOR_IN
			self.ROT_MOTOR_RIGHT	= c_R_ARM_ROT_MOTOR_UP
			self.ROT_MOTOR_LEFT	 = c_R_ARM_ROT_MOTOR_DOWN
		elif leg_num == ARM_L:
			self.TIP_MOTOR_OUT	  = c_L_ARM_TIP_MOTOR_OUT
			self.TIP_MOTOR_IN	   = c_L_ARM_TIP_MOTOR_IN
			self.MID_MOTOR_UP	   = c_L_ARM_MID_MOTOR_OUT
			self.MID_MOTOR_DOWN	 = c_L_ARM_MID_MOTOR_IN
			self.ROT_MOTOR_RIGHT	= c_L_ARM_ROT_MOTOR_UP
			self.ROT_MOTOR_LEFT	 = c_L_ARM_ROT_MOTOR_DOWN
		
		
		# TODO: self.SERVO_ANGLE_LIMITS = [[0,1],[0,1],[0,1]]
		if(leg_num == ARM_L or leg_num == ARM_R):
			self.TIP_MOTOR_OUT_ANGLE = ARM_TIP_MOTOR_OUT_ANGLE
			self.TIP_MOTOR_IN_ANGLE = ARM_TIP_MOTOR_IN_ANGLE
			self.MID_MOTOR_UP_ANGLE = ARM_MID_MOTOR_OUT_ANGLE
			self.MID_MOTOR_DOWN_ANGLE = ARM_MID_MOTOR_IN_ANGLE
			self.ROT_MOTOR_RIGHT_ANGLE = ARM_ROT_MOTOR_UP_ANGLE
			self.ROT_MOTOR_LEFT_ANGLE = ARM_ROT_MOTOR_DOWN_ANGLE
			# TODO
			# self.SERVO_ANGLE_LIMITS[TIP_MOTOR] = [ARM_TIP_MOTOR_OUT_ANGLE, 	ARM_TIP_MOTOR_IN_ANGLE]
			# self.SERVO_ANGLE_LIMITS[MID_MOTOR] = [ARM_MID_MOTOR_OUT_ANGLE, 	ARM_MID_MOTOR_IN_ANGLE]
			# self.SERVO_ANGLE_LIMITS[ROT_MOTOR] = [ARM_ROT_MOTOR_UP_ANGLE, 	ARM_ROT_MOTOR_DOWN_ANGLE]
		else:
			self.TIP_MOTOR_OUT_ANGLE = TIP_MOTOR_OUT_ANGLE
			self.TIP_MOTOR_IN_ANGLE = TIP_MOTOR_IN_ANGLE
			self.MID_MOTOR_UP_ANGLE = MID_MOTOR_UP_ANGLE
			self.MID_MOTOR_DOWN_ANGLE = MID_MOTOR_DOWN_ANGLE
			self.ROT_MOTOR_RIGHT_ANGLE = ROT_MOTOR_RIGHT_ANGLE
			self.ROT_MOTOR_LEFT_ANGLE = ROT_MOTOR_LEFT_ANGLE
			
		# TODO: set these constants (both angle and pwm) to handle condition where if the "leg_num" is of rotator type


		# TODO: self.curr_servo_angle = [-1, -1, -1]
		# TODO: self.curr_servo_pwm = [-1, -1, -1]
		# declare these member variables, immediately have value overwritten...
		self.tip_motor = -1
		self.mid_motor = -1
		self.rot_motor = -1
		self.tip_motor_angle = -1
		self.mid_motor_angle = -1
		self.rot_motor_angle = -1
		
		# ...this code should overwrite the "-1"s with sensible values on bootup
		# NEEDS to use the non-thread versions
		if(leg_num == ARM_L or leg_num == ARM_R):
			self.set_leg_position(TORSO_ARM_TABLE["NEUTRAL"])
		else:
			self.set_servo_angle(45, TIP_MOTOR)
			self.set_servo_angle(180, MID_MOTOR)
			self.set_servo_angle(90, ROT_MOTOR)

		# start the thread
		self.framethread.start()


	def print_self(self):
		print("leg uid : " + str(self.uid) + " ===========================")
		# print("on channels : " + str(self.tip_channel) + " " + str(self.mid_channel) + " " + str(self.rot_channel))
		print("on channels : " + str(self.pwm_channels))
		print("tip_motor pwm : " + str(self.tip_motor) + " angle : " + str(self.pwm_to_angle(self.tip_motor, TIP_MOTOR)))
		print("mid_motor pwm : " + str(self.mid_motor) + " angle : " + str(self.pwm_to_angle(self.mid_motor, MID_MOTOR)))
		print("rot_motor pwm : " + str(self.rot_motor) + " angle : " + str(self.pwm_to_angle(self.rot_motor, ROT_MOTOR)))
		# mock function useful for testing when not in the lab. change all instances
		# of pwm.set_pwm to pwm.set_pwm to use the real function
		# Use the pwm.pwn for real, robot usage


	# conversion functions:
	def angle_to_pwm(self, angle, motor):
		if motor == TIP_MOTOR:
			return linear_map(self.TIP_MOTOR_OUT_ANGLE, self.TIP_MOTOR_OUT, self.TIP_MOTOR_IN_ANGLE, self.TIP_MOTOR_IN, angle)
		elif motor == MID_MOTOR:
			return linear_map(self.MID_MOTOR_UP_ANGLE, self.MID_MOTOR_UP, self.MID_MOTOR_DOWN_ANGLE, self.MID_MOTOR_DOWN, angle)
		elif motor == ROT_MOTOR:
			return linear_map(self.ROT_MOTOR_RIGHT_ANGLE, self.ROT_MOTOR_RIGHT, self.ROT_MOTOR_LEFT_ANGLE, self.ROT_MOTOR_LEFT, angle)
		else:
			return INV_PARAM
		# TODO: after things are turned into lists, the code above can be replaced with:
		# return linear_map(self.SERVO_ANGLE_LIMITS[motor][0], self.SERVO_PWM_LIMITS[motor][0], self.SERVO_ANGLE_LIMITS[motor][1], self.SERVO_PWM_LIMITS[motor][1], angle)
		
	def pwm_to_angle(self, pwm, motor):
		if motor == TIP_MOTOR:
			return linear_map(self.TIP_MOTOR_OUT, self.TIP_MOTOR_OUT_ANGLE, self.TIP_MOTOR_IN, self.TIP_MOTOR_IN_ANGLE, pwm)
		elif motor == MID_MOTOR:
			return linear_map(self.MID_MOTOR_UP, self.MID_MOTOR_UP_ANGLE, self.MID_MOTOR_DOWN, self.MID_MOTOR_DOWN_ANGLE, pwm)
		elif motor == ROT_MOTOR:
			return linear_map(self.ROT_MOTOR_RIGHT, self.ROT_MOTOR_RIGHT_ANGLE, self.ROT_MOTOR_LEFT, self.ROT_MOTOR_LEFT_ANGLE, pwm)
		else:
			return INV_PARAM
		# TODO: after things are turned into lists, the code above can be replaced with:
		# return linear_map(self.SERVO_PWM_LIMITS[motor][0], self.SERVO_ANGLE_LIMITS[motor][0], self.SERVO_PWM_LIMITS[motor][1], self.SERVO_ANGLE_LIMITS[motor][1], angle)

	def percent_to_angle(self, percent, motor):
		# maps 0-100 to each motor's min and max angle values
		if motor == TIP_MOTOR:
			return linear_map(100, self.TIP_MOTOR_OUT_ANGLE, 0, self.TIP_MOTOR_IN_ANGLE, percent)
		elif motor == MID_MOTOR:
			return linear_map(100, self.MID_MOTOR_UP_ANGLE, 0, self.MID_MOTOR_DOWN_ANGLE, percent)
		elif motor == ROT_MOTOR:
			return linear_map(100, self.ROT_MOTOR_RIGHT_ANGLE, 0, self.ROT_MOTOR_LEFT_ANGLE, percent)
		else:
			return INV_PARAM
		# TODO: after things are turned into lists, the code above can be replaced with:
		# return linear_map(100, self.SERVO_ANGLE_LIMITS[motor][0], 0, self.SERVO_ANGLE_LIMITS[motor][1], angle)

	# convert-then-set functions:
	def set_servo_percent(self, percent, motor):
		# convert and pass off to set_servo_angle
		self.set_servo_angle(self.percent_to_angle(percent, motor), motor)
	def set_servo_pwm(self, pwm, motor):
		# convert and pass off to set_servo_angle
		self.set_servo_angle(self.angle_to_pwm(pwm, motor), motor)

	# uses the "leg position" objects
	def set_leg_position(self, leg_position):
		self.set_servo_angle(leg_position.tip_motor, TIP_MOTOR)
		self.set_servo_angle(leg_position.mid_motor, MID_MOTOR)
		self.set_servo_angle(leg_position.rot_motor, ROT_MOTOR)
	def set_leg_position_up(self, leg_position):
		self.set_servo_angle(leg_position.tip_motor, TIP_MOTOR)
		self.set_servo_angle(leg_position.mid_motor + 45, MID_MOTOR)
		self.set_servo_angle(leg_position.rot_motor, ROT_MOTOR)

	
	# the old-fashioned "do the thing" command: clamps value to safety limits, ensures it won't collide with any thread operations, and calls do_set_servo_angle
	def set_servo_angle(self, angle, motor):
		# wait until running_flag is clear (sleeping_flag is set)
		# this ensures that it won't conflict with the thread if it is running
		# you SHOULDN'T be using both the thread and the direct-set method, but better to be safe than sorry
		self.sleeping_flag.wait()
		
		# safety checking for each motor
		(a, b) = (0, 0)
		if motor == TIP_MOTOR:
			(a, b) = (self.TIP_MOTOR_IN_ANGLE, self.TIP_MOTOR_OUT_ANGLE)
		elif motor == MID_MOTOR:
			(a, b) = (self.MID_MOTOR_UP_ANGLE, self.MID_MOTOR_DOWN_ANGLE)
		elif motor == ROT_MOTOR:
			(a, b) = (self.ROT_MOTOR_LEFT_ANGLE, self.ROT_MOTOR_RIGHT_ANGLE)
		else:
			return INV_PARAM
		safe_angle = bidirectional_clamp(angle, a, b)
		# TODO: after things are turned into lists, the code above can be replaced with:
		# safety checking for each motor
		# (safe_angle = bidirectional_clamp(angle, self.SERVO_ANGLE_LIMITS[motor][0], self.SERVO_ANGLE_LIMITS[motor][1])
		
		return self.do_set_servo_angle(safe_angle, motor)
		
		
	# clear the frame queue to stop any currently-pending movements.
	# note that when the hexwalker calls this it should first abort() all legs, THEN call "synchronize" on all legs. this way it doesn't wait for one leg to stop before clearing the queue of the next.
	def abort():
		with self._frame_queue_lock: 
			self.frame_queue = []
		
		
		
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
		command[TIP_MOTOR] = bidirectional_clamp(leg_position.tip_motor, self.TIP_MOTOR_IN_ANGLE, self.TIP_MOTOR_OUT_ANGLE)
		command[MID_MOTOR] = bidirectional_clamp(leg_position.mid_motor, self.MID_MOTOR_UP_ANGLE, self.MID_MOTOR_DOWN_ANGLE)
		command[ROT_MOTOR] = bidirectional_clamp(leg_position.rot_motor, self.ROT_MOTOR_LEFT_ANGLE, self.ROT_MOTOR_RIGHT_ANGLE)
		
		
		# if there is a queued interpolation frame, interpolate from the final frame in the queue to the desired pose.
		# otherwise, interpolate from current position.
		lastframe = []
		with self._frame_queue_lock:
			if len(self.frame_queue) > 0:
				# be sure it is a copy and not a reference, just to be safe
				lastframe = list(self.frame_queue[-1])
		if lastframe == []:   # "else" but outside of the lock block
			lastframe = [self.tip_motor_angle, self.mid_motor_angle, self.rot_motor_angle]
				# TODO: lastframe = self.curr_servo_angle
		
		# run interpolation
		# NOTE: "command" must have 4 elements, "lastframe" only needs 3, the 4th is just unused
		interpolate_list = interpolate(command, lastframe)
		
		# add new frames onto the END of the frame queue (with lock)
		with self._frame_queue_lock:
			self.frame_queue = self.frame_queue + interpolate_list
			if LEG_THREAD_DEBUG and self.uid == 0:
				print("leg_" + str(self.uid) + ": add " + str(len(interpolate_list)) + " frames to frame_queue, new length is " + str(len(frame_queue)))
		
		with self._state_flag_lock:
			# clear "sleeping" event, does not trigger anything (note: clear before set)
			self.sleeping_flag.clear()
			# set the "running" event, this may trigger other waiting tasks
			self.running_flag.set()
		
		
	# unprotected internal-use-only function
	# set the actual PWM and the internally-tracked position
	def do_set_servo_angle(self, angle, motor):
		# get pwm val
		pwm_val = int(self.angle_to_pwm(angle, motor))

		# do the write out, with lock just to be safe
		with self._curr_pos_lock:
			if motor == TIP_MOTOR:
				(self.tip_motor_angle, self.tip_motor) = (angle, pwm_val)
				self.pwm.set_pwm(self.pwm_channels[0], 0, pwm_val)
			elif motor == MID_MOTOR:
				(self.mid_motor_angle, self.mid_motor) = (angle, pwm_val)
				self.pwm.set_pwm(self.pwm_channels[1], 0, pwm_val)
			elif motor == ROT_MOTOR:
				(self.rot_motor_angle, self.rot_motor) = (angle, pwm_val)
				self.pwm.set_pwm(self.pwm_channels[2], 0, pwm_val)
				
		# TODO: after things are turned into lists, the code above can be replaced with:
		# # do the write out, with lock just to be safe
		# with self._curr_pos_lock:
			# self.curr_servo_angle[motor] = angle
			# self.curr_servo_pwm[motor] = pwm_val
			# self.pwm.set_pwm(self.pwm_channels[motor], 0, pwm_val)
			
			
		return SUCCESS



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
		self.set_hex_walker_position(TALL_NEUTRAL)

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

	# torso movement functions
	def walk(self, num_steps, direction):
		
		self.set_new_front(get_front_from_direction(direction))
		print("dir: " + get_front_from_direction(direction))
		
		# start walk by lifting legs
		self.set_hex_walker_position(TALL_TRI_RIGHT_NEUTRAL_LEFT_UP_NEUTRAL)
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
				self.do_move_set(left_step)
				last_step = "left"
			elif(last_step == "left"):
				self.do_move_set(right_step)
				last_step = "right"
		#cleanup
		self.set_hex_walker_position(TALL_NEUTRAL)
		self.set_new_front("5-0")

	def rotate(self, num_steps, direction):
		
		# start rotate by lifting legs
		self.set_hex_walker_position(TALL_TRI_RIGHT_UP_NEUTRAL_LEFT_NEUTRAL)
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
				self.do_move_set(left_step)
				last_step = "left"
			elif(last_step == "left"):
				self.do_move_set(right_step)
				last_step = "right"
		#cleanup
		self.set_hex_walker_position(TALL_NEUTRAL)

	def fine_rotate(self, num_steps, direction):
		
		# start rotate by lifting legs
		self.set_hex_walker_position(TALL_TRI_RIGHT_UP_NEUTRAL_LEFT_NEUTRAL)
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
				self.do_move_set(left_step)
				last_step = "left"
			elif(last_step == "left"):
				self.do_move_set(right_step)
				last_step = "right"
		#cleanup
		self.set_hex_walker_position(TALL_NEUTRAL)

	def leg_wave(self, direction, speed, repetitions):
		# TODO: figure out what the hell this is doing
		for i in range(0, repetitions):
			if(direction == RIGHT):
				for leg in self.all_legs:
					leg.set_leg_position(MISC_TABLE["PULL_UP"])
					time.sleep(speed)
					leg.set_leg_position(TALL_TRI_MOVEMENT_TABLE["NEUTRAL"])
			if(direction == LEFT):
				for i in range(len(self.all_legs)-1, -1, -1):
					self.all_legs[i].set_leg_position(MISC_TABLE["PULL_UP"])
					time.sleep(speed)
					self.all_legs[i].set_leg_position(TALL_TRI_MOVEMENT_TABLE["NEUTRAL"])

	def bounce(self, wait, repetitions):
		for i in range(0, repetitions):
			self.set_hex_walker_position(TALL_TRI_BOUNCE_DOWN)
			time.sleep(wait)
			self.set_hex_walker_position(TALL_NEUTRAL)
			time.sleep(wait)

	def do_nothing(self):
		self.set_hex_walker_position(TALL_NEUTRAL)


	# old version: direct-set then wait
	def do_move_set(self, hex_walker_position_list):
		for next_pos in hex_walker_position_list:
			if next_pos in HEX_WALKER_POSITIONS[self.current_pos].safe_moves:
				if HW_MOVE_DEBUG:
					print("Sending command")
				if USE_THREADING:
					self.set_hex_walker_position_thread(next_pos)
					self.synchronize([LEG_RF, LEG_RM, LEG_RB, LEG_LB, LEG_LM, LEG_RF])
				else:
					self.set_hex_walker_position(next_pos)
					time.sleep(self.speed)
			else:
				print("invalid move set")
				return ILLEGAL_MOVE
		return SUCCESS
	
# NOTE: the functinos set_hex_walker_position and do_set_hex_walker_position are similar but one takes in a raw position and the other uses the defined table AND updates the current position. Using the do
# version skips this state-updating and so it can be useful for testing

# NOTE: this function should not be called from external code (except testing) because it might not be safe
	def set_hex_walker_position(self, hex_walker_position_number):
		if(HW_MOVE_DEBUG):
			print("current position is : " + HEX_WALKER_POSITIONS[self.current_pos].description + ", moving to position: " + HEX_WALKER_POSITIONS[hex_walker_position_number].description)
		self.current_pos = hex_walker_position_number
		self.do_set_hex_walker_position(HEX_WALKER_POSITIONS[hex_walker_position_number])

# NOTE: this function should not be called from external code (except testing) because it might not be safe
	def do_set_hex_walker_position(self, hex_walker_position):
		self.rf_leg.set_leg_position(hex_walker_position.rf_pos)
		self.rm_leg.set_leg_position(hex_walker_position.rm_pos)
		self.rb_leg.set_leg_position(hex_walker_position.rr_pos)
		self.lb_leg.set_leg_position(hex_walker_position.lr_pos)
		self.lm_leg.set_leg_position(hex_walker_position.lm_pos)
		self.lf_leg.set_leg_position(hex_walker_position.lf_pos)


	# new version: gradual motion
	#TODO: make this better
	def do_move_set_thread(self, hex_walker_position_list):
		for next_pos in hex_walker_position_list:
			if next_pos in HEX_WALKER_POSITIONS[self.current_pos].safe_moves:
				if HW_MOVE_DEBUG:
					print("Sending command")
				self.set_hex_walker_position_thread(next_pos)
				self.synchronize([LEG_RF, LEG_RM, LEG_RB, LEG_LB, LEG_LM, LEG_RF])
			else:
				print("invalid move set")
				return ILLEGAL_MOVE
		return SUCCESS
		

	#TODO: make this better
	def set_hex_walker_position_thread(self, hex_walker_position_number):
		if(HW_MOVE_DEBUG):
			print("current position is : " + HEX_WALKER_POSITIONS[self.current_pos].description + ", moving to position: " + HEX_WALKER_POSITIONS[hex_walker_position_number].description)
		self.current_pos = hex_walker_position_number
		self.do_set_hex_walker_position_thread(HEX_WALKER_POSITIONS[hex_walker_position_number])


	#TODO: make this better
	def do_set_hex_walker_position_thread(self, hex_walker_position):
		self.rf_leg.set_leg_position_thread(hex_walker_position.rf_pos, self.speed)
		self.rm_leg.set_leg_position_thread(hex_walker_position.rm_pos, self.speed)
		self.rb_leg.set_leg_position_thread(hex_walker_position.rr_pos, self.speed)
		self.lb_leg.set_leg_position_thread(hex_walker_position.lr_pos, self.speed)
		self.lm_leg.set_leg_position_thread(hex_walker_position.lm_pos, self.speed)
		self.lf_leg.set_leg_position_thread(hex_walker_position.lf_pos, self.speed)
	


	# synchronize the legs by not returning until all of the specified legs are done moving
	# works with the new threadwise execution
	# uses "absolute" positions of each leg: ignores the "change direction" stuff
	def synchronize(self, masklist):
		# first cast the leglist as a set to remove potential duplicates
		mask = set(masklist)
		for leg in mask:
			# wait until the leg is done, if it is already done this returns immediately
			self.leglist[leg].sleeping_flag.wait()
		
		


# TODO: make the "rotator" class a subclass of "leg"
class Rotator(object):
	def __init__(self, uid, pwm, channel):
		self.uid = uid
		self.pwm = pwm
		self.channel = channel
		self.pwm_val = -1
		self.ROTATOR_MOTOR_LEFT  = ROTATOR_MOTOR_LEFT
		self.ROTATOR_MOTOR_RIGHT = ROTATOR_MOTOR_RIGHT
		self.ROTATOR_LEFT_ANGLE = ROTATOR_LEFT_ANGLE
		self.ROTATOR_RIGHT_ANGLE = ROTATOR_RIGHT_ANGLE
		self.set_servo_angle(90)

	def angle_to_pwm(self, angle):
		return linear_map(self.ROTATOR_LEFT_ANGLE, self.ROTATOR_MOTOR_LEFT, self.ROTATOR_RIGHT_ANGLE, self.ROTATOR_MOTOR_RIGHT, angle)

	def set_servo_angle(self, angle):
		pwm_val = int(self.angle_to_pwm(angle))
		# safety check
		upper = max(self.ROTATOR_MOTOR_LEFT, self.ROTATOR_MOTOR_RIGHT)
		lower = min(self.ROTATOR_MOTOR_LEFT, self.ROTATOR_MOTOR_RIGHT)

		if pwm_val < lower:
			pwm_val = lower

		elif pwm_val > upper:
			pwm_val = upper

		self.pwm_val = pwm_val
		self.pwm.set_pwm(self.channel, 0, pwm_val)

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
		self.rotator.set_servo_angle(rotation)

	def do_moveset(self, positions, rotations, sleeps, repetitions):
		for j in range(0, repetitions):
			for i in range(0, len(positions)):
				self.set_torso_position(positions[i], rotations[i])
				time.sleep(sleeps[i])

	def set_torso_rotation(self, rotation):
		self.rotator.set_servo_angle(rotation)

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
