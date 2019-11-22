
# Brian Henson

# "mathy" utility functions that aren't really intrinsic to any one place
# i just didn't want them cluttering up the class definitions in hex_walker_driver_v2


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
