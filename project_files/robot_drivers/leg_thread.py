# leg thread:

# member of the leg object, launched when leg object is created
# connects to the leg object("input command queue", abort event, running event, PWM object, current leg positions)
# command includes the dest pose (3 servo PWM values) + time to reach it

# exactly 1 thread per leg, reusable, no need for locking mechanism

import time
import threading
import hex_walker_constants
import hex_walker_driver_v2
import hex_util

# "frame format" = [ TIP, MID, ROT, time ]

# function:
def leg_interpolate_thread(leg):
	# looping forever
	while(True):
	
		# wait until leg."running" event is set by leg object
		leg.running_flag.wait()
		# if leg.abort event has happened while it was sleeping, it is a mistake, clear it
		if leg.abort_event.is_set():
			leg.abort_event.clear()
		
		while(True):
			# check if abort event has happened (only can be set from leg object)... if so, clear & break
			# the frame queue gets clears before this is set
			if leg.abort_event.is_set():
				leg.abort_event.clear()
				break			
			# if no abort happened, try to get a frame
			
			frame = []
			# if there are frames in the frame queue, pop one off (with lock). otherwise, break.
			with leg._frame_queue_lock:
				if len(leg.frame_queue) > 0:
					frame = leg.frame_queue.pop(0)
			if frame == []:
				break
				
			# set the leg to the pose indicated by the frame
			# use the unprotected leg member function: also updates the position stored in the leg
			leg.do_set_servo_angle(frame[0], TIP_MOTOR)
			leg.do_set_servo_angle(frame[1], MID_MOTOR)
			leg.do_set_servo_angle(frame[2], ROT_MOTOR)
			
			# sleep for frame-delay
			time.sleep(frame[3])
			pass
			
		# now frame queue is empty!
		# clear "running" event, does not trigger anything
		leg.running_flag.clear()
		# set the "sleeping" event, this may trigger other waiting tasks
		leg.sleeping_flag.set()
		# loop back to top, wait until running_flag is set again
		pass
	pass



