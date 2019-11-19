
# Brian Henson

# member of the leg object, launched when leg object is created.
# connects to the leg object, accessses several of its members & functions
# each frame is a sub-pose interpolated between poses.
# "frame format" = [ TIP, MID, ROT, time ]

# exactly 1 thread per leg, reusable. locks exist on pwm object, per-leg frame_queue, per-leg state flags, and per-leg do_set_servo_angle.

# this thread MUST be launched as a "daemon" because this thread should run forever and never actually finish.
# if not a daemon then the python program would never return to the command line until all threads finish, and since this thread runs inside while(true)...
# daemon means "kill this thread when the main thread is terminated" which solves the problem.

# interpolate() actually happens in the main thread but because it is used only for this background thread it makes sense to define it here.

import time
from hex_walker_constants import *

# TODO: change debug prints to use "logging" module?


# uses the following members of "leg": 
# running_flag
# idle_flag
# _state_flag_lock
# frame_queue
# _frame_queue_lock
# framethread (debugging)
# uid (debugging)
# do_set_servo_angle()
def Frame_Thread_Func(leg, DEBUG):
	# looping forever
	while True:
	
		# wait until leg."running" event is set by leg object
		leg.running_flag.wait()

		if DEBUG and leg.uid == 0:
			print(str(leg.framethread.name) + ": thread wakeup")

		while True:
			frame = []
			# if there are frames in the frame queue, pop one off (with lock). otherwise, break.
			# if an abort happened while sleeping, the queue will be empty and it will exit, no separate event needed.
			with leg._frame_queue_lock:
				if len(leg.frame_queue) > 0:
					frame = leg.frame_queue.pop(0)
			if frame == []:   # "else" but outside of the lock block
				break
				
			if DEBUG and leg.uid == 0:
				print(str(leg.framethread.name) + ": execute frame " + str(frame))
			
			# set the leg to the pose indicated by the frame
			# skip the safety checks in set_servo_angle or set_leg_position because safety is checked before interpolating
			# use the unprotected leg member function: also updates the position stored in the leg
			for s in GROUP_ALL_SERVOS:
				leg.do_set_servo_angle(frame[s], s)
			
			# sleep for frame-delay
			time.sleep(frame[3])
			pass
			
		# now frame queue is empty!
		if DEBUG and leg.uid == 0:
			print(str(leg.framethread.name) + ": thread sleep")
			
		with leg._state_flag_lock:
			# clear "running" event, does not trigger anything (note: clear before set)
			leg.running_flag.clear()
			# set the "sleeping" event, this may trigger other waiting tasks
			leg.idle_flag.set()
		# loop back to top, wait until running_flag is set again
		pass
	pass



# return a list of lists
# interpolating in angle space, so its all floating-point inputs/outputs
# inputs: dest[ A, B, C ], curr[ A, B, C ], dur
# the TIP/MID/ROT order doesnt matter, as long as the order is the same for dest and curr, the output will match
# time between interpolated poses is very close to INTERPOLATE_TIME but not exactly
# num_frames * frame_time exactly equals requested duration
# minimum duration is INTERPOLATE_TIME, rounds up if it is less
def interpolate(dest, curr, dur):
	# find the delta(s)
	delta = [dest[0] - curr[0], dest[1] - curr[1], dest[2] - curr[2]]
	# total time must not be less than INTERPOLATE_TIME
	dur = max(dur, INTERPOLATE_TIME)
	# determine how many sections this time must be broken into: round up/down to nearest whole number
	num_frames = round(dur / INTERPOLATE_TIME)
	# from number of frames, calculate the time between each frame (should be very close to INTERPOLATE_TIME)
	frame_time = dur / num_frames
	# initialize the list with the proper number of entries so I dont have to keep appending
	frame_list = [[0,0,0,frame_time] for i in range(num_frames)]
	for i in range(num_frames):
		# math is ((i+1)/num_frames * delta) + curr
		# the +1 is because the first frame should NOT be curr, and the final frame SHOULD be dest (curr+delta)
		for z in range(3):
			frame_list[i][z] = ((i+1)/num_frames * delta[z]) + curr[z]
		pass
	# done building the frame-list
	return frame_list

