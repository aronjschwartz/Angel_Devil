
# "mathy" utility functions that aren't really intrinsic to any one place

import hex_walker_constants
import math


# helper functions
# returns slope given two points
def slope(x1, y1, x2, y2):
	return (y2 - y1) / (x2 - x1)
def intercept(x2, y2, slope):
	return y2 - slope * x2
def linear_map(x1, y1, x2, y2, x_in_val):
	m = slope(x1, y1, x2, y2)
	b = intercept(x2, y2, m)
	return x_in_val * m + b

# basic clamp
def clamp(value, lower, upper):
    return lower if value < lower else upper if value > upper else value
# clamp where you dont know the relative order of a and b
def bidirectional_clamp(val, a, b):
	return clamp(val, a, b) if a < b else clamp(val, b, a)


def get_front_from_direction(direction):
	if(direction == 0):
		return "5-0"
	elif(direction == 60):
		return "0-1"
	elif(direction == 120):
		return "1-2"
	elif(direction == 180):
		return "2-3"
	elif(direction == 240):
		return "3-4"
	elif(direction == 300):
		return "4-5"
	else:
		return "5-0"




# return a list of lists
# interpolating in angle space, so its all floating-point if that matters
# inputs: dest[ TIP, MID, ROT, time ], curr_tip, curr_mid, curr_rot
# time between interpolated poses is known constant, number of interpolated poses is dynamic
	# might change this in the future tho so i will return the time between poses anyway
def interpolate(cmd, curr):
	# find the delta(s)
	delta = [curr[0] - cmd[0], curr[1] - cmd[1], curr[2] - cmd[2]]
	# determine how many sections this time must be broken into
	# total time is rounded up to next multiple of command time... i.e. # of frames is rounded up
	num_frames = math.ceil(cmd[3] / INTERPOLATE_TIME)
	# initialize the list with the proper number of entries so I dont have to keep appending
	frame_list = [[0,0,0,0]] * num_frames
	for i in range(num_frames):
		# set frame_list[i]
		# math is ((i+1)/num_frames * delta) + curr
		# the +1 is because the first frame should NOT be curr, and the final frame SHOULD be dest (curr+delta)
		for z in range(3):
			frame_list[i][z] = ((i+1)/num_frames * delta[z]) + curr[z]
		frame_list[i][3] = INTERPOLATE_TIME
		pass
	# done building the frame-list
	return frame_list

