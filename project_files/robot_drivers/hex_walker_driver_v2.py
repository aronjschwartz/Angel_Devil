
# Brian Henson

# new version of hex_walker_driver, first created in fall2019 project1.
# moved some contents from here to hex_util or hex_walker_constants files for cleanliness and organization.
# adds interpolation & threading improvments to the Leg object driver, some of the Hex_Walker driver, more improvements pending.
# also improved organization of Leg object by grouping variables into lists.
# also improved code reuse by making Rotator object a subclass of Leb object.


import time
import threading
from typing import List

from posedata_arms import *
from posedata_walker import *
from posedata_leg import *

from hex_walker_constants import *
from hex_util import *
import frame_thread as ft
from pwm_wrapper import Pwm_Wrapper

#Extraneous

HW_MOVE_DEBUG = 0 #toggle 0/1 to turn debug prints on/off

LEG_THREAD_DEBUG = False

USE_THREADING = True



# Leg_Position class defined in posedata_leg.py
# Hex_Walker_Position class defined in posedata_walker.py
# Arms_Position class defined in posedata_arms.py


# A Leg object is a group of 3 servos that are controlled as one unit. It is used for the 6 legs
# and both arms of Feynman bot, and the subclass Rotator is used for the waist. The servos in the
# leg can be directly and immediately set or gradually/linearly transition to the destination pose
# depending on the function used. They can be individually set via angle, PWM value, or percentage.
# To set all at once, the Leg_Position object must be used. When initialized it is given the I2C
# address of the PWM hat it is connected to, and the PWM channels on that hat the individual servos
# connect to. All servos in a Leg must be on the same PWM hat.
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
	def __init__(self, pwm: Pwm_Wrapper, channels: List[int], leg_num: int):

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
		# locking object to ensure no collisions happen around self.curr_servo_angle/self.curr_servo_pwm
		# might not be necessary but couldn't hurt, technically both the leg thread and leg object can write into them
		self._curr_pos_lock = threading.Lock()

		# create and launch the thread for this leg
		# note: this MUST be daemon type because the thread is designed to run forever... the only way to stop it is by stopping its parent, which means it must be a daemon!
		# it should be able to access all of this leg's other member variables and functions
		# threadname = "framethread" + str(leg_num)
		self.framethread = threading.Thread(name="framethread_" + str(leg_num), target=ft.Frame_Thread_Func, args=(self, LEG_THREAD_DEBUG), daemon=True)
		# just to be safe, don't start the thread until the end of __init__
		
		
		# set the channels to use for the PWM object, comes in as a list
		self.pwm_channels = channels		
		
		
		# now, assign the correct constants to limit PWM values
		self.SERVO_PWM_LIMITS = [[0,1],[0,1],[0,1]]
		if leg_num == LEG_0:
			# leg: out in, up down, right left
			self.SERVO_PWM_LIMITS[TIP_SERVO] = [c_0_TIP_SERVO_OUT, c_0_TIP_SERVO_IN]
			self.SERVO_PWM_LIMITS[MID_SERVO] = [c_0_MID_SERVO_UP, c_0_MID_SERVO_DOWN]
			self.SERVO_PWM_LIMITS[ROT_SERVO] = [c_0_ROT_SERVO_RIGHT, c_0_ROT_SERVO_LEFT]
		elif leg_num == LEG_1:
			self.SERVO_PWM_LIMITS[TIP_SERVO] = [c_1_TIP_SERVO_OUT, c_1_TIP_SERVO_IN]
			self.SERVO_PWM_LIMITS[MID_SERVO] = [c_1_MID_SERVO_UP, c_1_MID_SERVO_DOWN]
			self.SERVO_PWM_LIMITS[ROT_SERVO] = [c_1_ROT_SERVO_RIGHT, c_1_ROT_SERVO_LEFT]
		elif leg_num == LEG_2:
			self.SERVO_PWM_LIMITS[TIP_SERVO] = [c_2_TIP_SERVO_OUT, c_2_TIP_SERVO_IN]
			self.SERVO_PWM_LIMITS[MID_SERVO] = [c_2_MID_SERVO_UP, c_2_MID_SERVO_DOWN]
			self.SERVO_PWM_LIMITS[ROT_SERVO] = [c_2_ROT_SERVO_RIGHT, c_2_ROT_SERVO_LEFT]
		elif leg_num == LEG_3:
			self.SERVO_PWM_LIMITS[TIP_SERVO] = [c_3_TIP_SERVO_OUT, c_3_TIP_SERVO_IN]
			self.SERVO_PWM_LIMITS[MID_SERVO] = [c_3_MID_SERVO_UP, c_3_MID_SERVO_DOWN]
			self.SERVO_PWM_LIMITS[ROT_SERVO] = [c_3_ROT_SERVO_RIGHT, c_3_ROT_SERVO_LEFT]
		elif leg_num == LEG_4:
			self.SERVO_PWM_LIMITS[TIP_SERVO] = [c_4_TIP_SERVO_OUT, c_4_TIP_SERVO_IN]
			self.SERVO_PWM_LIMITS[MID_SERVO] = [c_4_MID_SERVO_UP, c_4_MID_SERVO_DOWN]
			self.SERVO_PWM_LIMITS[ROT_SERVO] = [c_4_ROT_SERVO_RIGHT, c_4_ROT_SERVO_LEFT]
		elif leg_num == LEG_5:
			self.SERVO_PWM_LIMITS[TIP_SERVO] = [c_5_TIP_SERVO_OUT, c_5_TIP_SERVO_IN]
			self.SERVO_PWM_LIMITS[MID_SERVO] = [c_5_MID_SERVO_UP, c_5_MID_SERVO_DOWN]
			self.SERVO_PWM_LIMITS[ROT_SERVO] = [c_5_ROT_SERVO_RIGHT, c_5_ROT_SERVO_LEFT]
		elif leg_num == ARM_R:
			# arm: out in, out in, up down
			self.SERVO_PWM_LIMITS[TIP_SERVO] = [c_R_ARM_TIP_SERVO_OUT, c_R_ARM_TIP_SERVO_IN]
			self.SERVO_PWM_LIMITS[MID_SERVO] = [c_R_ARM_MID_SERVO_OUT, c_R_ARM_MID_SERVO_IN]
			self.SERVO_PWM_LIMITS[ROT_SERVO] = [c_R_ARM_ROT_SERVO_UP, c_R_ARM_ROT_SERVO_DOWN]
		elif leg_num == ARM_L:
			self.SERVO_PWM_LIMITS[TIP_SERVO] = [c_L_ARM_TIP_SERVO_OUT, c_L_ARM_TIP_SERVO_IN]
			self.SERVO_PWM_LIMITS[MID_SERVO] = [c_L_ARM_MID_SERVO_OUT, c_L_ARM_MID_SERVO_IN]
			self.SERVO_PWM_LIMITS[ROT_SERVO] = [c_L_ARM_ROT_SERVO_UP, c_L_ARM_ROT_SERVO_DOWN]
		elif leg_num == WAIST:
			# waist: left right
			self.SERVO_PWM_LIMITS[WAIST_SERVO] = [c_WAIST_SERVO_PWM_LEFT, c_WAIST_SERVO_PWM_RIGHT]
		

		self.SERVO_ANGLE_LIMITS = [[0,1],[0,1],[0,1]]
		if leg_num == ARM_L or leg_num == ARM_R:
			# arm: out in, out in, up down
			self.SERVO_ANGLE_LIMITS[TIP_SERVO] = [ARM_TIP_SERVO_OUT_ANGLE, ARM_TIP_SERVO_IN_ANGLE]
			self.SERVO_ANGLE_LIMITS[MID_SERVO] = [ARM_MID_SERVO_OUT_ANGLE, ARM_MID_SERVO_IN_ANGLE]
			self.SERVO_ANGLE_LIMITS[ROT_SERVO] = [ARM_ROT_SERVO_UP_ANGLE, ARM_ROT_SERVO_DOWN_ANGLE]
		elif leg_num == WAIST:
			# waist: left right
			self.SERVO_ANGLE_LIMITS[WAIST_SERVO] = [WAIST_SERVO_LEFT_ANGLE, WAIST_SERVO_RIGHT_ANGLE]
		else:
			# leg: out in, up down, right left
			self.SERVO_ANGLE_LIMITS[TIP_SERVO] = [LEG_TIP_SERVO_UP_ANGLE, LEG_TIP_SERVO_DOWN_ANGLE]
			self.SERVO_ANGLE_LIMITS[MID_SERVO] = [LEG_MID_SERVO_UP_ANGLE, LEG_MID_SERVO_DOWN_ANGLE]
			self.SERVO_ANGLE_LIMITS[ROT_SERVO] = [LEG_ROT_SERVO_RIGHT_ANGLE, LEG_ROT_SERVO_LEFT_ANGLE]
			

		# declare these member variables, immediately have value overwritten...
		self.curr_servo_angle = [-1.0, -1.0, -1.0]
		self.curr_servo_pwm =   [-1, -1, -1]
		
		# ...this code should overwrite the "-1"s with sensible values on bootup
		# NEEDS to use the non-thread versions
		if leg_num == ARM_L or leg_num == ARM_R:
			# default position is with arms fully extended
			self.set_leg_position(ARMS_ARM_TABLE["STRAIGHT_OUT"])
		elif leg_num == WAIST:
			self.set_servo_angle(90, WAIST_SERVO)
		else:
			# default position is 90-degree crouch
			# self.set_leg_position(LEG_MISC_TABLE["STRAIGHT_OUT"])
			self.set_leg_position(LEG_MISC_TABLE["INIT"])

		# start the thread
		self.framethread.start()


	def print_self(self):
		print("leg uid : " + str(self.uid) + " ===========================")
		print("on channels : tip/mid/rot = " + str(self.pwm_channels))
		print("servo PWMs: tip/mid/rot = " + str(self.curr_servo_pwm))
		print("servo angles: tip/mid/rot = " + str(self.curr_servo_angle))
		print("frame queue size: " + str(len(self.frame_queue)))


	# conversion functions: use linear mapping from input to output
	def angle_to_pwm(self, angle: float, servo: int) -> int:
		if servo < 0 or servo > 2:
			print("ERR#1: INVALID SERVO INDEX! valid values are 0 to 2")
			print("leg="+str(self.uid)+", servo="+str(servo)+", angle="+str(angle))
			return INV_PARAM
		r = linear_map(self.SERVO_ANGLE_LIMITS[servo][0], self.SERVO_PWM_LIMITS[servo][0],
						self.SERVO_ANGLE_LIMITS[servo][1], self.SERVO_PWM_LIMITS[servo][1], 
						angle)
		return round(r)
		
	def pwm_to_angle(self, pwm: int, servo: int) -> float:
		if servo < 0 or servo > 2:
			print("ERR#2: INVALID SERVO INDEX! valid values are 0 to 2")
			print("leg="+str(self.uid)+", servo="+str(servo)+", pwm="+str(pwm))
			return INV_PARAM
		return linear_map(self.SERVO_PWM_LIMITS[servo][0], self.SERVO_ANGLE_LIMITS[servo][0], 
						self.SERVO_PWM_LIMITS[servo][1], self.SERVO_ANGLE_LIMITS[servo][1], 
						pwm)

	def percent_to_angle(self, percent: float, servo: int) -> float:
		# maps 0-100 to each servo's min and max angle values
		if servo < 0 or servo > 2:
			print("ERR#3: INVALID SERVO INDEX! valid values are 0 to 2")
			print("leg="+str(self.uid)+", servo="+str(servo)+", percent="+str(percent))
			return INV_PARAM
		return linear_map(100, self.SERVO_ANGLE_LIMITS[servo][0], 
						0, self.SERVO_ANGLE_LIMITS[servo][1], 
						percent)

	# convert-then-set functions:
	def set_servo_percent(self, percent: float, servo: int):
		# convert and pass off to set_servo_angle
		self.set_servo_angle(self.percent_to_angle(percent, servo), servo)
	def set_servo_pwm(self, pwm: int, servo: int):
		# convert and pass off to set_servo_angle
		self.set_servo_angle(self.angle_to_pwm(pwm, servo), servo)

	# the old-fashioned "do the thing" command: clamps value to safety limits, ensures it won't collide with any thread operations, and calls do_set_servo_angle
	def set_servo_angle(self, angle: float, servo: int):
		if servo < 0 or servo > 2:
			# ensure servo index is valid
			print("ERR#4: INVALID SERVO INDEX! valid values are 0 to 2")
			print("leg="+str(self.uid)+", servo="+str(servo)+", angle="+str(angle))
			return INV_PARAM

		# wait until running_flag is clear (idle_flag is set)
		# this ensures that it won't conflict with the thread if it is running
		# you SHOULDN'T be using both the thread and the direct-set method, but better to be safe than sorry
		self.idle_flag.wait()
		
		# safety checking for each servo
		safe_angle = bidirectional_clamp(angle, self.SERVO_ANGLE_LIMITS[servo][0], self.SERVO_ANGLE_LIMITS[servo][1])
		
		return self.do_set_servo_angle(safe_angle, servo)
		
		
	# creates a temporary "leg position" object to give to the leg_position_thread function
	# changes the given servo to the given position over the given time
	# OTHER MOTORS (on this leg) CANNOT CHANGE DURING THIS TIME, to change multiple motors at a time use set_leg_position_thread
	def set_servo_angle_thread(self, angle: float, servo: int, durr: float):
		if servo < 0 or servo > 2:
			# ensure servo index is valid
			print("ERR#5: INVALID SERVO INDEX! valid values are 0 to 2")
			print("leg="+str(self.uid)+", servo="+str(servo)+", angle="+str(angle))
			return INV_PARAM
		# explicitly make a copy of current angles
		v = list(self.curr_servo_angle)
		# modify one entry of the copy
		v[servo] = angle
		# init the Leg_Position from the list
		L = Leg_Position(v[0], v[1], v[2])
		
		self.set_leg_position_thread(L, durr)


	# uses the "leg_position" objects, immediate set (no threading)
	def set_leg_position(self, leg_position: Leg_Position):
		for s in GROUP_ALL_SERVOS:
			self.set_servo_angle(leg_position.list[s], s)


	# safety clamp (in angle space) 
	# interpolate (in angle space)
	# adds frames to the frame queue (with lock)
	# sets the "running" flag unconditionally (note: no harm in setting an already set flag)
	# * thread will jump in with "do_set_servo_angle" when it is the correct time
	def set_leg_position_thread(self, leg_position: Leg_Position, durr: float):
		# assemble dest from the leg position
		dest = [0, 0, 0]
		
		# safety checking for each motor
		for s in GROUP_ALL_SERVOS:
			dest[s] = bidirectional_clamp(leg_position.list[s], self.SERVO_ANGLE_LIMITS[s][0], self.SERVO_ANGLE_LIMITS[s][1])
		
		# if there is a queued interpolation frame, interpolate from the final frame in the queue to the desired pose.
		# otherwise, interpolate from current position.
		curr = []
		with self._frame_queue_lock:
			if len(self.frame_queue) > 0:
				# be sure it is a copy and not a reference, just to be safe
				curr = list(self.frame_queue[-1])
		if curr == []:   # "else" but outside of the lock block
			# this is fine as a reference, because this only happens when the thread isn't running
			curr = self.curr_servo_angle
		
		# run interpolation
		# NOTE: "curr" only needs 3 elements, but when copied from frame_queue it has 4... the 4th is just unused
		interpolate_list = ft.interpolate(dest, curr, durr)
		
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
	def do_set_servo_angle(self, angle: float, servo: int):
		if servo < 0 or servo > 2:
			# ensure servo index is valid
			print("ERR#6: INVALID SERVO INDEX! valid values are 0 to 2")
			print("leg="+str(self.uid)+", servo="+str(servo)+", angle="+str(angle))
			return INV_PARAM
		# convert to pwm
		pwm_val = self.angle_to_pwm(angle, servo)
		
		if pwm_val < c_PWM_ABSOLUTE_MINIMUM or pwm_val > c_PWM_ABSOLUTE_MAXIMUM:
			# guarantee somewhat-sensible PWM value
			print("ERR#7: UNSAFE PWM! safe values are "+str(c_PWM_ABSOLUTE_MINIMUM)+" to "+str(c_PWM_ABSOLUTE_MAXIMUM))
			print("leg="+str(self.uid)+", servo="+str(servo)+", angle="+str(angle)+", pwm="+str(pwm_val))
			# TODO: raise an exception of some kind??
			return INV_PARAM
		
		# do the write out, with lock just to be safe
		with self._curr_pos_lock:
			self.curr_servo_angle[servo] = angle
			self.curr_servo_pwm[servo] = pwm_val
			self.pwm.set_pwm(self.pwm_channels[servo], 0, pwm_val)
			
		return SUCCESS


# make the "rotator" class a subclass of "leg"
# any functions that would work on a leg also work on the rotator, it inherits absolutely everything
# redefines lowest-level function do_set_servo_angle to only touch the one servo, ignore other two
# set_servo_angle_thread(angle, motor=WAIST_SERVO, time) is the "right" way to change the waist rotation
# set_leg_position_thread(Leg_Position, time) also works because the non-WAIST_SERVO servos will be ignored
# nothing will change unless you are setting the waist motor, regardless how you try
class Rotator(Leg):
	# internal-use-only function
	# if servo is not WAIST_SERVO, then return & do nothing... otherwise call normal do_set_servo_angle()
	def do_set_servo_angle(self, angle: float, servo: int):
		if servo != WAIST_SERVO:
			# print("ERR#10: INVALID PARAM")
			return INV_PARAM
		# if it is valid, do the exact same code as the Leg would
		return super().do_set_servo_angle(angle, servo)




# The Hex_Walker is a way of grouping the 6 actual legs for macro-control. This is totally isolated from the torso
# servos. This contains the "motion functions" for things like walking and turning, as well as the driver functions
# to execute these motions.
# Most func accept optional arg "durr" to specify the duration of the transition; if missing, default is self.speed.
# Most func accept optional arg "masklist" to specify the legs being set or waited on.
# synchronize() will wait until the specified legs are done moving before it returns (default value is wait for all).
# !!! WIP !!! abort() will flush the frame queues of each leg, stopping their movements immediately. They then hold
# whatever in-between pose they happened to have when it was called. TODO: It also interrupts any in-progress "motion function", method TBD.
# run_pose_list() takes a list of indices within HEX_WALKER_POSITIONS array and runs through them with durr=self.speed.
# set_hexwalker_position() sets any combination of legs from an index or Hex_Walker_Position object.
# do_set_hexwalker_position() sets any combination of legs from a Leg_Position object.
class Hex_Walker(object):
	# list of functions:
	# __init__
	# print_self
	# set_speed
	# idx_to_leg
	# set_new_front
	# run_pose_list
	# set_hexwalker_position
	# do_set_hexwalker_position
	# synchronize
	# abort
	# + assorted "motion" functions
	def __init__(self, rf_leg: Leg, rm_leg: Leg, rb_leg: Leg, lb_leg: Leg, lm_leg: Leg, lf_leg: Leg):
		# create backup members permanently and explicitly tied to each leg
		# currently not used but it couldn't hurt, really
		self.leg0 = rf_leg
		self.leg1 = rm_leg
		self.leg2 = rb_leg
		self.leg3 = lb_leg
		self.leg4 = lm_leg
		self.leg5 = lf_leg
		
		# leglist indexed by leg ID, etc
		self.leglist = [rf_leg, rm_leg, rb_leg, lb_leg, lm_leg, lf_leg]

		# if running with synchronize(), it works. curr_pose corresponds to actual current pose.
		# if running append-style, curr_pose corresponds to the pose of the last thing i added to the queue... this
		# would not correspond to the actual physical pose of the robot any more, but as long as abort() not called,
		# this would work for safety-checking.
		# when dynamically modifying a pose, need to modify the proper (closest) pose, not just pick 1 at random.
		self.current_pose = NORMAL_NEUTRAL
		# set operating speed
		self.speed = NORMAL_SPEED
		self.front = "5-0"
		self.front_index_offset = 0
		# set all legs to neutral
		self.set_hexwalker_position(TALL_NEUTRAL)


	def print_self(self):
		print("speed: " + str(self.speed) + " || self.current_pose: " + str(self.current_pose) + " || self.front: " + self.front)
		for leg in self.leglist:
			leg.print_self()


	def set_speed(self, new_speed):
		self.speed = new_speed


	## convert given index to the actual leg object... trivial but whatever
	# apply a custom "front" by circular offsetting the index into the array
	# direct-index into leglist gets the absolute leg, using idx_to_leg gets the relative-to-current-direction leg
	def idx_to_leg(self, n):
		return self.leglist[(n + self.front_index_offset) % 6]


	# this function will change the front from being between the "5-0" legs to being
	# between any two legs. The key is "(leg on frontleft)-(leg on frontright)"
	# NEW: now accepts only [DIR_F, DIR_FL, DIR_FR, DIR_B, DIR_BL, DIR_BR]
	def set_new_front(self, new_front):
		cp = self.current_pose
		if(cp != TALL_NEUTRAL and cp != NORMAL_NEUTRAL and cp != CROUCH_NEUTRAL):
			print("Cannot change front while not in the neutral position")
			return ILLEGAL_MOVE
		
		# check for which side should be the front and re-assign the leg offset accordingly
		if new_front == DIR_F:
			self.front_index_offset = 0
			self.front = new_front
		elif new_front == DIR_FR:
			self.front_index_offset = 1
			self.front = new_front
		elif new_front == DIR_BR:
			self.front_index_offset = 2
			self.front = new_front
		elif new_front == DIR_B:
			self.front_index_offset = 3
			self.front = new_front
		elif new_front == DIR_BL:
			self.front_index_offset = 4
			self.front = new_front
		elif new_front == DIR_FL:
			self.front_index_offset = 5
			self.front = new_front
		else:
			print("ERR: set_new_front() accepts only direction = (DIR_F, DIR_FL, DIR_FR, DIR_B, DIR_BL, DIR_BR)")
			return INV_PARAM
		return SUCCESS


	## takes a list of indices within HEX_WALKER_POSITIONS array, or Hex_Walker_Position objects, and runs through them.
	# safety: for each transition, checks that the next pose is listed as a "safe pose" of the current pose
	# previously "do_move_set"
	def run_pose_list(self, hex_walker_position_list, repeat=1, masklist=GROUP_ALL_LEGS, durr=None):
		for i in range(repeat):
			for next_pose in hex_walker_position_list:
				# if next_pose is a Hex_Walker_Position object, convert it to its id
				next_pose_idx = next_pose if isinstance(next_pose, int) else next_pose.id
				if next_pose_idx in HEX_WALKER_POSITIONS[self.current_pose].safe_moves:
					self.set_hexwalker_position(next_pose_idx, masklist=masklist, durr=durr)
					self.synchronize()
				else:
					print("ERR: invalid move set")
					return ILLEGAL_MOVE
		return SUCCESS


	## sets any combination of legs from an index or Hex_Walker_Position while keeping other legs untouched.
	# also updates the current_pose value
	# masklist can be int or list, or none (defaults to all legs)
	# previously "set_hex_walker_position"
	def set_hexwalker_position(self, hex_pose_idx, masklist=GROUP_ALL_LEGS, durr=None):
		# if given a single index rather than an iteratable, make it into a set
		mask = {masklist} if isinstance(masklist, int) else set(masklist)
		# if given hex_pose_idx as an index, convert to Hex_Walker_Position object via lookup
		hex_pose_obj = hex_pose_idx if isinstance(hex_pose_idx, Hex_Walker_Position) else HEX_WALKER_POSITIONS[hex_pose_idx]
		
		if HW_MOVE_DEBUG:
			print("current pose is: " + HEX_WALKER_POSITIONS[self.current_pose].description + ", moving to pose: " + hex_pose_obj.description)
		self.current_pose = hex_pose_obj.id
		
		for n in mask:
			# extract the appropriate pose from the object, send to appropriate leg
			self.do_set_hexwalker_position(hex_pose_obj.list[n], masklist=n, durr=durr)


	## sets any combination of legs from a Leg_Position object while keeping other legs untouched.
	# masklist can be int or list, or none (defaults to all legs)
	# previously "do_set_hex_walker_position"
	def do_set_hexwalker_position(self, dest, masklist=GROUP_ALL_LEGS, durr=None):
		# default time if not given is self.speed, can't put "self" in default args tho
		durr = self.speed if durr is None else durr
		# if given a single index rather than an iteratable, make it into a set
		mask = {masklist} if isinstance(masklist, int) else set(masklist)
		
		for leg in [self.idx_to_leg(n) for n in mask]:
			if USE_THREADING:
				leg.set_leg_position_thread(dest, durr) # threading version
			else:
				leg.set_leg_position(dest) # non-threading version


	## synchronize the legs with the main thread by not returning until all of the specified legs are done moving
	# masklist accepts list, set, int (treated as single-element set)
	# if not given any arg, default is GROUP_ALL_LEGS
	# depending on USE_THREADING, either simply sleep or do the actual wait
	def synchronize(self, masklist=GROUP_ALL_LEGS):
		if USE_THREADING:
			# if given a single index rather than an iteratable, make it into a set
			# if given something else, cast the masklist as a set to remove potential duplicates
			mask = {masklist} if isinstance(masklist, int) else set(masklist)
			
			for leg in [self.idx_to_leg(n) for n in mask]:
				# wait until the leg is done, if it is already done this returns immediately
				leg.idle_flag.wait()
		else:
			time.sleep(self.speed)


	# abort all queued leg thread movements, and wait a bit to ensure they all actually stopped.
	# their "current angle/pwm" variables should still be correct, unless it was trying to move beyond its range somehow.
	# TODO: the "flushing" part is good, now decide how to break out of a "movement function"
	# ideas:
	# A) Set “aborting” flag, leave it high. Make hex.do_leg_position check it and do nothing, causes any motion
	# functions to rapidly “fall through” their list of commands. Requires cleanup function at end of each movement
	# function to clear the flag.
	# B) Synchronize() checks for “aborting” flag before returning. If high, clear it, clear “running” flag, release
	# locks, whatever. Raise a custom exception that needs to be caught somewhere…?
	# C) Launch motion functions in a separate thread (only permit one running at a time). Synchronize() checks for
	# “aborting” flag before returning. If high, clear it, clear “running” flag, release locks, whatever. Then call
	# sys.exit() to terminate the thread early. Very similar to the "raise an exception" idea, actually raising an
	# uncaught exception from a thread is pretty much the same as calling sys.exit() from a thread
	def abort(self):
		# first clear all the queues
		for leg in self.leglist:
			leg.abort()
		# then wait until all legs returned to "sleeping" state
		self.synchronize()
		# then wait for 3x the interpolate time, just to be safe
		time.sleep(INTERPOLATE_TIME * 3)


	########################################################################################
	########################################################################################
	# movement functions
	
	# note: TALL_TRI_RIGHT_NEUTRAL_LEFT_UP_NEUTRAL, TALL_TRI_RIGHT_UP_NEUTRAL_LEFT_NEUTRAL are used in both walk and rotate
	
	# assumes beginning in true neutral position
	### true neutral -> Bhalf-raised -> {Asequence -> Ahalf-raised -> Bsequence -> Bhalf-raised}, repeat -> true neutral
	# always begins with a "left step"... just means which legs are being moved forward first
	# can end after left-step (if num_steps=odd) or right-step (if num_steps=even)
	# variable speed, number of steps, and distance per step
	def walk(self, num_steps, front=DIR_F, scale=1.0, durr=None):
		if front not in [DIR_F, DIR_FL, DIR_FR, DIR_B, DIR_BL, DIR_BR]:
			print("ERR: walk() accepts only front = (DIR_F, DIR_FL, DIR_FR, DIR_B, DIR_BL, DIR_BR)")
			return INV_PARAM
		if num_steps < 1:
			print("ERR: walk() accepts only num_steps >= 1")
			return INV_PARAM
		if scale <= 0.0 or scale > 2.0:
			# todo: depends on actual motions of the legs
			# basic walk moves legs by ?????
			# i'll limit the scale to 2.0 so max turn is 30 or 150
			print("ERR: walk() accepts only scale = (0.0 - 2.0]")
			return INV_PARAM

		# apply a new front so we can use the same walk cycle unmodified to walk in 6 different directions by just
		# redefining which leg is which.
		self.set_new_front(front)
		if HW_MOVE_DEBUG:
			print("walk dir: " + str(front))
		
		# define positions to go through to get steps from a neutral legs up
		# these all ultimately reference the LEG_TALL_MOVEMENT_TABLE in posedata_leg.py
		# TODO: first, understand the current animation. then, improve it with full-range motion.
		# start 		TALL_TRI_RIGHT_NEUTRAL_LEFT_UP_NEUTRAL
		left_step = [	TALL_TRI_RIGHT_BACK_LEFT_UP_FORWARD,
						TALL_TRI_RIGHT_BACK_LEFT_FORWARD,
						TALL_TRI_RIGHT_UP_BACK_LEFT_FORWARD,
						TALL_TRI_RIGHT_UP_NEUTRAL_LEFT_NEUTRAL]
		right_step = [	TALL_TRI_RIGHT_UP_FORWARD_LEFT_BACK,
						TALL_TRI_RIGHT_FORWARD_LEFT_BACK,
						TALL_TRI_RIGHT_FORWARD_LEFT_UP_BACK,
						TALL_TRI_RIGHT_NEUTRAL_LEFT_UP_NEUTRAL]
		
		# todo: scale
		
		# begin walk sequence by lifting some of the legs: "half-raised neutral position"
		# this is the pose at the end of a right-step or beginning of a left-step
		self.set_hexwalker_position(TALL_TRI_RIGHT_NEUTRAL_LEFT_UP_NEUTRAL, durr=durr)
		self.synchronize()

		last_step_right = True
		for i in range(num_steps):
			if last_step_right:
				# this branch always runs first!!
				# if last step was right, do a left
				self.run_pose_list(left_step, durr=durr)
				last_step_right = False
			else:
				# if last step was left, do a right
				self.run_pose_list(right_step, durr=durr)
				last_step_right = True
			self.synchronize()
		#cleanup
		self.set_hexwalker_position(TALL_NEUTRAL, durr=durr)
		self.set_new_front(DIR_F)
		self.synchronize()


	# to apply "stance" changes: set_hexwalker_position(), probably?
	# also, create run_pose_list() without the synchronize() calls

	# TODO: TEST THIS!!! should be running exactly the same as before
	# assumes beginning in true neutral position
	# true neutral -> Bhalf-raised -> {Asequence -> Ahalf-raised -> Bsequence -> Bhalf-raised}, repeat -> true neutral
	# always begins with a "left step", regardless of turn direction... just means which legs are being moved forward first
	# can end after left-step (if num_steps=odd) or right-step (if num_steps=even)
	# variable speed, number of steps, and distance per step
	def rotate(self, num_steps, direction, scale=1.0, durr=None):
		if not (direction == LEFT or direction == RIGHT):
			print("ERR: rotate() accepts only direction = (LEFT or RIGHT)")
			return INV_PARAM
		if num_steps < 1:
			print("ERR: rotate() accepts only num_steps >= 1")
			return INV_PARAM
		if scale <= 0.0 or scale > 2.0:
			# basic turn moves legs by 30* (from 90 to 60 or 120), hard limit is 0-180 but shouldn't go that far
			# i'll limit the scale to 2.0 so max turn is 30 or 150
			print("ERR: rotate() accepts only scale = (0.0 - 2.0]")
			return INV_PARAM
		
		# define positions to go through: technically this is just the turning-left sequence but you'll see how it works
		# these all ultimately reference the LEG_TALL_ROTATION_TABLE in posedata_leg.py
		# left turn: run these top to bottom, right turn: run these bottom to top
		# start 			TALL_TRI_RIGHT_NEUTRAL_LEFT_UP_NEUTRAL
		temp_left_step = [	TALL_TRI_RIGHT_RIGHT_LEFT_UP_LEFT,
							TALL_TRI_RIGHT_RIGHT_LEFT_LEFT,
							TALL_TRI_RIGHT_UP_RIGHT_LEFT_LEFT,
							TALL_TRI_RIGHT_UP_NEUTRAL_LEFT_NEUTRAL]
		temp_right_step = [	TALL_TRI_RIGHT_UP_LEFT_LEFT_RIGHT,
							TALL_TRI_RIGHT_LEFT_LEFT_RIGHT,
							TALL_TRI_RIGHT_LEFT_LEFT_UP_RIGHT,
							TALL_TRI_RIGHT_NEUTRAL_LEFT_UP_NEUTRAL]
		
		# if direction is not left, mirror the rot-servo values by using a negative scale
		# equivalent to reversing & L/R swapping the pose-list, but less confusing this way
		if direction == RIGHT:
			scale = -scale
			
		# NEW: scale the "rot-servo" portion to produce fine-stepping behavior!
		temp_both = []
		for pose_idx in temp_left_step + temp_right_step:		# combine the lists for easier iteration
			pose = HEX_WALKER_POSITIONS[pose_idx].copy()		# dereference and copy
			for l in pose.list:		# modify: for each leg in the hex-pose, scale the rot-servo around 90*
				l.list[ROT_SERVO] = ((l.list[ROT_SERVO] - 90.) * scale) + 90.	# subtract 90, scale, add 90
			temp_both.append(pose)		# store
		# re-split the merged list
		left_step = temp_both[:4]  # first half
		right_step = temp_both[4:] # second half
		
		# begin rotate sequence by lifting some of the legs: "half-raised neutral position"
		# this is the pose at the end of a right-step or beginning of a left-step
		self.set_hexwalker_position(TALL_TRI_RIGHT_NEUTRAL_LEFT_UP_NEUTRAL, durr=durr)
		self.synchronize()
		
		last_step_right = True
		for i in range(num_steps):
			if last_step_right: # if last_step_right == True:
				# this branch always runs first!!
				# if last step was right, do a left
				self.run_pose_list(left_step, durr=durr)
				last_step_right = False
			else: # elif last_step_right == False:
				# if last step was left, do a right
				self.run_pose_list(right_step, durr=durr)
				last_step_right = True
			self.synchronize()
		#cleanup
		self.set_hexwalker_position(TALL_NEUTRAL, durr=durr)
		self.synchronize()
		return SUCCESS


	# def rotate(self, num_steps, direction):
	# 	# start rotate by lifting legs
	# 	self.set_hexwalker_position(TALL_TRI_RIGHT_UP_NEUTRAL_LEFT_NEUTRAL)
	# 	# define positions to go through to get steps from neutral legs up
	# 	go_left_right_step = [
	# 	TALL_TRI_RIGHT_RIGHT_LEFT_UP_LEFT,
	# 	TALL_TRI_RIGHT_RIGHT_LEFT_LEFT,
	# 	TALL_TRI_RIGHT_UP_RIGHT_LEFT_LEFT,
	# 	TALL_TRI_RIGHT_UP_NEUTRAL_LEFT_NEUTRAL]
	#
	# 	go_left_left_step = [
	# 	TALL_TRI_RIGHT_UP_LEFT_LEFT_RIGHT,
	# 	TALL_TRI_RIGHT_LEFT_LEFT_RIGHT,
	# 	TALL_TRI_RIGHT_LEFT_LEFT_UP_RIGHT,
	# 	TALL_TRI_RIGHT_NEUTRAL_LEFT_UP_NEUTRAL]
	#
	# 	go_right_right_step = [
	# 	TALL_TRI_RIGHT_LEFT_LEFT_UP_RIGHT,
	# 	TALL_TRI_RIGHT_LEFT_LEFT_RIGHT,
	# 	TALL_TRI_RIGHT_UP_LEFT_LEFT_RIGHT,
	# 	TALL_TRI_RIGHT_UP_NEUTRAL_LEFT_NEUTRAL]
	#
	# 	go_right_left_step = [
	# 	TALL_TRI_RIGHT_UP_RIGHT_LEFT_LEFT,
	# 	TALL_TRI_RIGHT_RIGHT_LEFT_LEFT,
	# 	TALL_TRI_RIGHT_RIGHT_LEFT_UP_LEFT,
	# 	TALL_TRI_RIGHT_NEUTRAL_LEFT_UP_NEUTRAL]
	#
	# 	if(direction == RIGHT):
	# 		left_step = go_right_left_step
	# 		right_step = go_right_right_step
	# 	if(direction == LEFT):
	# 		left_step = go_left_left_step
	# 		right_step = go_left_right_step
	#
	# 	last_step = "right"
	# 	for i in range (0, num_steps):
	# 		if(last_step == "right"):
	# 			self.run_pose_list(left_step)
	# 			last_step = "left"
	# 		elif(last_step == "left"):
	# 			self.run_pose_list(right_step)
	# 			last_step = "right"
	# 	#cleanup
	# 	self.set_hexwalker_position(TALL_NEUTRAL)


	# fine_rotate is just a special case of the multi-use "rotate" function
	def fine_rotate(self, num_steps, direction, scale=0.2, durr=None):
		self.rotate(num_steps, direction, scale=scale, durr=durr)
		
		
	# def fine_rotate(self, num_steps, direction):
	# 	# start rotate by lifting legs
	# 	self.set_hexwalker_position(TALL_TRI_RIGHT_UP_NEUTRAL_LEFT_NEUTRAL)
	# 	# define positions to go through to get steps from neutral legs up
	# 	go_left_right_step = [
	# 	TALL_TRI_FINE_RIGHT_RIGHT_LEFT_UP_LEFT,
	# 	TALL_TRI_FINE_RIGHT_RIGHT_LEFT_LEFT,
	# 	TALL_TRI_FINE_RIGHT_UP_RIGHT_LEFT_LEFT,
	# 	TALL_TRI_RIGHT_UP_NEUTRAL_LEFT_NEUTRAL]
	#
	# 	go_left_left_step = [
	# 	TALL_TRI_FINE_RIGHT_UP_LEFT_LEFT_RIGHT,
	# 	TALL_TRI_FINE_RIGHT_LEFT_LEFT_RIGHT,
	# 	TALL_TRI_FINE_RIGHT_LEFT_LEFT_UP_RIGHT,
	# 	TALL_TRI_RIGHT_NEUTRAL_LEFT_UP_NEUTRAL]
	#
	# 	go_right_right_step = [
	# 	TALL_TRI_FINE_RIGHT_LEFT_LEFT_UP_RIGHT,
	# 	TALL_TRI_FINE_RIGHT_LEFT_LEFT_RIGHT,
	# 	TALL_TRI_FINE_RIGHT_UP_LEFT_LEFT_RIGHT,
	# 	TALL_TRI_RIGHT_UP_NEUTRAL_LEFT_NEUTRAL]
	#
	# 	go_right_left_step = [
	# 	TALL_TRI_FINE_RIGHT_UP_RIGHT_LEFT_LEFT,
	# 	TALL_TRI_FINE_RIGHT_RIGHT_LEFT_LEFT,
	# 	TALL_TRI_FINE_RIGHT_RIGHT_LEFT_UP_LEFT,
	# 	TALL_TRI_RIGHT_NEUTRAL_LEFT_UP_NEUTRAL]
	#
	# 	if(direction == RIGHT):
	# 		left_step = go_right_left_step
	# 		right_step = go_right_right_step
	# 	if(direction == LEFT):
	# 		left_step = go_left_left_step
	# 		right_step = go_left_right_step
	#
	# 	last_step = "right"
	# 	for i in range (0, num_steps):
	# 		if(last_step == "right"):
	# 			self.run_pose_list(left_step)
	# 			last_step = "left"
	# 		elif(last_step == "left"):
	# 			self.run_pose_list(right_step)
	# 			last_step = "right"
	# 	#cleanup
	# 	self.set_hexwalker_position(TALL_NEUTRAL)


	# "ripple" the legs around the robot in one direction or the other
	def leg_wave(self, direction, speed, repetitions):
		for i in range(0, repetitions):
			if(direction == RIGHT):
				for n in GROUP_ALL_LEGS:
					# pull_up = (60, 75, 90), tip above horizontal
					# normal neutral = (120, 90, 90)
					# crouch neutral = (45, 135, 90)
					self.do_set_hexwalker_position(LEG_MISC_TABLE["PULL_UP"], n, speed)
					self.synchronize()
					# tall neutral = (120, 45, 90)
					self.do_set_hexwalker_position(LEG_TALL_MOVEMENT_TABLE["NEUTRAL"], n, speed)
			if(direction == LEFT):
				reverselist = list(GROUP_ALL_LEGS)
				reverselist.reverse()
				for n in reverselist:
					self.do_set_hexwalker_position(LEG_MISC_TABLE["PULL_UP"], n, speed)
					self.synchronize()
					self.do_set_hexwalker_position(LEG_TALL_MOVEMENT_TABLE["NEUTRAL"], n, speed)
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
		self.synchronize()


	########################################################################################
	########################################################################################


# terms: torso = (Larm + Rarm) + waist
# The Robot_Torso groups the 2 arms with the waist motor for macro-control. This is totally isolated from the 6 legs
# in the Hex_Walker object. This contains the "motion functions" for things like dancing and pointing, as well as the
# driver functions to execute these motions. Note that both arms and the waist are still technically "Leg" objects.
# Most func accept optional arg "durr" to specify the duration of the transition; if missing, default is self.speed.
# Most func accept optional arg "masklist" to specify the legs being set or waited on.
# It has synchronize() and abort() just like the Hex_Walker object, and they work just the same.
# do_moveset() takes a list of indices within ARMS_POSITIONS array, along with the waist-rotations to use for each.
# set_torso_position() calls both set_arms_position() and set_waist_position(), thats it.
# set_arms_position() will set LARM/RARM/both poses from an Arms_Position object or index within ARMS_POSITIONS.
# set_waist_position() will set the waist pose from an angle(degrees) or a Leg_Position object.
# do_set_torso_position() will set any combination of legs' poses from a Leg_Position object.
class Robot_Torso(object):
	# list of functions:
	# __init__
	# print_self
	# set_speed
	# synchronize
	# abort
	# do_moveset
	# set_torso_position
	# set_arms_position
	# set_waist_position
	# do_set_torso_position
	# + assorted "motion" functions
	def __init__(self, right_arm: Leg, left_arm: Leg, rotator: Rotator):
		# individual member variables
		self.left_arm = left_arm
		self.right_arm = right_arm
		self.rotator = rotator
		
		# list form (must subtract ARM_L from ID before indexing into this list, may change to dict in the future)
		self.leglist = [left_arm, right_arm, rotator]
		
		# set default speed
		self.speed = NORMAL_SPEED
		# go to default pose, arms and rotation
		self.torso_neutral()


	def print_self(self):
		print("torso object: speed=" + str(self.speed))
		for L in self.leglist:
			L.print_self()


	def set_speed(self, n):
		self.speed = n


	## synchronize the legs with the main thread by not returning until all of the specified legs are done moving
	# masklist accepts list, set, int (treated as single-element set)
	# if not given any arg, default is GROUP_ALL_TORSO
	# depending on USE_THREADING, either simply sleep or do the actual wait
	def synchronize(self, masklist=GROUP_ALL_TORSO):
		if USE_THREADING:
			# if given a single index rather than an iteratable, make it into a set
			mask = {masklist} if isinstance(masklist, int) else set(masklist)
			for leg in [self.leglist[n - ARM_L] for n in mask]:
				# wait until the leg is done, if it is already done this returns immediately
				leg.idle_flag.wait()
		else:
			time.sleep(self.speed)


	# abort all queued leg thread movements, and wait a bit to ensure they all actually stopped.
	# their "current angle/pwm" variables should still be correct, unless it was trying to move beyond its range somehow.
	def abort(self):
		# first clear all the queues
		for leg in self.leglist:
			leg.abort()
		# then wait until all legs returned to "sleeping" state
		self.synchronize()
		# then wait for 3x the interpolate time, just to be safe
		time.sleep(INTERPOLATE_TIME * 3)


	## takes a list of indices within ARMS_POSITIONS array, along with the waist-rotations to use for each.
	# sets arms and waist at same time, waits until each change is done with synchronize()
	# previously do_moveset(self, positions, rotations, sleeps, repetitions):
	def do_moveset(self, position_indices, rotations, repeat=1, masklist=GROUP_ALL_LEGS, durr=None):
		if len(position_indices) != len(rotations):
			print("ERR: len(position_indices) != len(rotations)")
			return INV_PARAM
		for j in range(repeat):
			for pose_idx, rot in zip(position_indices, rotations):
				self.set_arms_position(pose_idx, masklist=masklist, durr=durr)
				self.set_waist_position(rot, durr=durr)
				self.synchronize()
		return SUCCESS


	## do both set_arms_position and set_waist_position, thats it. no mask ability
	def set_torso_position(self, arms_pose_idx, rotation, durr=None):
		self.set_arms_position(arms_pose_idx, masklist=GROUP_ALL_ARMS, durr=durr)
		self.set_waist_position(rotation, durr=durr)


	## set LARM/RARM/both poses from an Arms_Position object or index within ARMS_POSITIONS.
	# take mask of arm or arms, default is both arms (cannot set the waist from this function)
	# previously set_torso_position(self, torso_position_number, rotation)
	def set_arms_position(self, arms_pose_idx, masklist=GROUP_ALL_ARMS, durr=None):
		# if given a single index rather than an iteratable, make it into a set
		mask = {masklist} if isinstance(masklist, int) else set(masklist)
		# if given arms_pose_idx as an index, convert to Arms_Position object via lookup
		arms_pose_obj = arms_pose_idx if isinstance(arms_pose_idx, Arms_Position) else ARMS_POSITIONS[arms_pose_idx]

		# check which arms are in mask and extract appropriate leg-pose from the arms-obj
		for n in mask:
			self.do_set_torso_position(arms_pose_obj.list[n], masklist=n, durr=durr)
	
	## set the waist pose from an angle(degrees) or a Leg_Position object.
	# one-to-one: no mask needed
	# previously set_torso_rotation(self, rotation):
	def set_waist_position(self, waist_rot, durr=None):
		# if given waist_rot as raw angle, convert to a leg-object
		waist_rot_obj = waist_rot if isinstance(waist_rot, Leg_Position) else Leg_Position(waist_rot, waist_rot, waist_rot)
		self.do_set_torso_position(waist_rot_obj, masklist=WAIST, durr=durr)


	## set any combination of legs' poses from a Leg_Position object.
	# take a Leg_Position (extracted from Arms_Position or built from waist rotation angle)
	# take a masklist: specify any combination of L/R/W, probably not useful to set multiple at once tho
	# previously do_set_torso_position(self, torso_position, rotation)
	def do_set_torso_position(self, legobj, masklist=GROUP_ALL_TORSO, durr=None):
		# default time if not given is self.speed, can't put "self" in default args tho
		durr = self.speed if durr is None else durr
		# if given a single index rather than an iteratable, make it into a set
		mask = {masklist} if isinstance(masklist, int) else set(masklist)
		for leg in [self.leglist[n - ARM_L] for n in mask]:
			if USE_THREADING:
				leg.set_leg_position_thread(legobj, durr) # threading version
			else:
				leg.set_leg_position(legobj) # non-threading version


	########################################################################################
	########################################################################################
	# torso movement functions
	
	# TODO: change these to not use do_moveset function, put it in the queue and synchronize()
	
	# ????, then reset
	def monkey(self, repetitions):
		moves = [ARMS_MONKEY_RIGHT_UP,
				 ARMS_MONKEY_LEFT_UP]
		# duplicate this a total of 8 times
		moves = moves * 8
		rotations = [45] * 8 + [135] * 8
		self.do_moveset(moves, rotations, repeat=repetitions, durr=0.1)
		# then go to the neutral position
		self.torso_neutral()


	# beat the chest, then reset
	def king_kong(self, rotation, repetitions):
		moves = [ARMS_DANCE_FRONT_LEFT_OUT,
				 ARMS_DANCE_FRONT_RIGHT_OUT]
		rotations = [rotation] * 2
		self.do_moveset(moves, rotations, repeat=repetitions, durr=0.4)
		# then go to the neutral position
		self.torso_neutral()


	# do handshake sequence (which hand?), then reset
	def hand_shake(self, rotation, repetitions):
		moves = [ARMS_SHAKE_DOWN,
				 ARMS_SHAKE_MID,
				 ARMS_SHAKE_UP,
				 ARMS_SHAKE_MID]
		rotations = [rotation] * 4
		self.do_moveset(moves, rotations, repeat=repetitions, durr=0.1)
		# then go to the neutral position
		self.torso_neutral()


	# do waving sequence (which hand?), then reset
	def wave(self, rotation, repetitions):
		moves = [ARMS_WAVE_DOWN,
				 ARMS_WAVE_UP]
		rotations = [rotation] * 2
		self.do_moveset(moves, rotations, repeat=repetitions, durr=0.4)
		# then go to the neutral position
		self.torso_neutral()


	# ????, then hold
	def look(self):
		self.set_torso_position(ARMS_LOOKING, 90)
		self.synchronize()


	# point with left arm or right arm in the specified direction, then hold
	def point(self, hand, direction):
		if(hand == RIGHT):
			self.set_torso_position(ARMS_POINTING_RIGHT, direction)
		elif(hand == LEFT):
			self.set_torso_position(ARMS_POINTING_LEFT, direction)
		self.synchronize()


	# direction is from 0-359, will pick leftarm/rightarm to point in the chosen direction
	# 0/360 = front
	# this does not control the waist at all, just the arms
	# !!! also demonstrates more dynamic control over the poses !!!
	def point_better(self, direction):
		direction = clamp(direction, 0, 359)
		if direction >= 180:
			# use left arm to point: dynamically create the leg-pose to have the angle i want
			armspos = ARMS_POSITIONS[ARMS_POINTING_FWD_LEFT].copy()
			# translate direction=[180=back, 270=left, 360=fwd] to [180=back, 90=out, 0=fwd]
			armspos.left_arm.list[MID_SERVO] = (-(direction-180))+180
			self.set_arms_position(armspos)
		else:
			# use right arm to point
			armspos = ARMS_POSITIONS[ARMS_POINTING_FWD_RIGHT].copy()
			# translate direction=[0=fwd, 90=right, 180=back] to [0=fwd, 90=out, 180=back], no translation
			armspos.right_arm.list[MID_SERVO] = direction
			self.set_arms_position(armspos)
		self.synchronize()


	# extend left arm straight out and turn maximum right, then hold
	# no args needed
	# TODO: add arguments and change pose to allow height/LR control
	def stab(self):
		self.set_torso_position(ARMS_POINTING_FWD_LEFT, 90)
		self.synchronize()


	# go to default arms & default waist
	def torso_neutral(self):
		self.set_speed(NORMAL_SPEED)
		self.set_torso_position(ARMS_NEUTRAL, 90)
		self.synchronize()
	# go to default arms, doesn't change waist
	def arms_neutral(self):
		self.set_speed(NORMAL_SPEED)
		self.set_arms_position(ARMS_NEUTRAL)
		self.synchronize()
	# go to default waist, doesn't change arms
	def rotate_neutral(self):
		self.set_speed(NORMAL_SPEED)
		self.set_waist_position(90)
		self.synchronize()

	########################################################################################
	########################################################################################

