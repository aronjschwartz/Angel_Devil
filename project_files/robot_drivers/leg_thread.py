# leg thread:

# member of the leg object, launched when leg object is created
# connects to the leg object("input command queue", abort event, running event, do_set_servo_angle())
# command includes the dest pose (3 servo PWM values) + time to reach it

# exactly 1 thread per leg, reusable, no need for locking mechanism

import time
import threading
from hex_walker_constants import *
from hex_walker_driver_v2 import *
from hex_util import *

# "frame format" = [ TIP, MID, ROT, time ]

# function:
def leg_interpolate_thread(leg, DEBUG):
	# looping forever
	while(True):
	
		# wait until leg."running" event is set by leg object
		leg.running_flag.wait()
		while(True):
			frame = []
			# if there are frames in the frame queue, pop one off (with lock). otherwise, break.
			# if an abort happened while sleeping, the queue will be empty and it will exit, no separate event needed
			with leg._frame_queue_lock:
				if len(leg.frame_queue) > 0:
					frame = leg.frame_queue.pop(0)
			if frame == []:
				break
				
			if DEBUG and leg.legthread.name == "legthread_0":
				print(str(leg.legthread.name) + ": execute frame " + str(frame))
			
			# set the leg to the pose indicated by the frame
			# use the unprotected leg member function: also updates the position stored in the leg
			leg.do_set_servo_angle(frame[0], TIP_MOTOR)
			leg.do_set_servo_angle(frame[1], MID_MOTOR)
			leg.do_set_servo_angle(frame[2], ROT_MOTOR)
			
			# sleep for frame-delay
			time.sleep(frame[3])
			pass
			
		# now frame queue is empty!
		if DEBUG:
			print(str(leg.legthread.name) + ": exhausted frame queue")
			
		# clear "running" event, does not trigger anything
		leg.running_flag.clear()
		# set the "sleeping" event, this may trigger other waiting tasks
		leg.sleeping_flag.set()
		# loop back to top, wait until running_flag is set again
		pass
	pass



