# leg thread:

# member of the leg object, launched when leg object is created.
# connects to the leg object("frame queue", running_flag/sleeping_flag, do_set_servo_angle())
# each frame is a sub-pose interpolated between poses.
# "frame format" = [ TIP, MID, ROT, time ]

# exactly 1 thread per leg, reusable. locks exist on pwm object, per-leg frame_queue, per-leg state flags, and per-leg do_set_servo_angle.
# this thread MUST be launched as a "daemon" because this thread should run forever and never actually finish.
# if not a daemon then the python program would never return to the command line until all threads finish, and since this thread runs inside while(true)...
# daemon means "kill this thread when the main thread is terminated" which solves the problem.


import time
import threading
from hex_walker_constants import *
# from hex_walker_driver_v2 import *
# from hex_util import *

# TODO: change debug prints to use "logging" module?


# function:
def Frame_Thread_Func(leg, DEBUG):
	# looping forever
	while(True):
	
		# wait until leg."running" event is set by leg object
		leg.running_flag.wait()

		if DEBUG and leg.uid == 0:
			print(str(leg.framethread.name) + ": thread wakeup")

		while(True):
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
			# use the unprotected leg member function: also updates the position stored in the leg
			leg.do_set_servo_angle(frame[TIP_MOTOR], TIP_MOTOR)
			leg.do_set_servo_angle(frame[MID_MOTOR], MID_MOTOR)
			leg.do_set_servo_angle(frame[ROT_MOTOR], ROT_MOTOR)
			
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
			leg.sleeping_flag.set()
		# loop back to top, wait until running_flag is set again
		pass
	pass



