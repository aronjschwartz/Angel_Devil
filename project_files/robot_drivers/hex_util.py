
# Brian Henson

# "mathy" utility functions that aren't really intrinsic to any one place
# i just didn't want them cluttering up the class definitions in hex_walker_driver_v2


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


# input is angle 0-359, but only multiples of 60 are valid
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

