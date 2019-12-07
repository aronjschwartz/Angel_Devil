#Program: Measures the angle of the central blue grid line, calcuates the angle, and outputs a recommended "correction"


import numpy as np
import math
import os
import cv2
from scipy import ndimage



# TODO: seriously clean up and optimize and comment the code
# TODO: add debug switches
# TODO: consider how to transform from 2d angle with in the image to 3d spacial rotation of robot
# TODO: implement some way of sorting the slopes of the detected lines and searching for groupings, to determine outliers
# TODO: implement some way of sorting the lines by their vertical height and building groups, to hopefully find two clusters and discard the top cluster

# TODO: investigate how using a black-and-white image is handled differently by Canny than a blue-and-black image


#Display image with cv
def display_image(image):
	cv2.imshow("TEST", image)
	cv2.waitKey(0)

#Simple function to read an image with cv
def read_image(image):
	pic = cv2.imread(image, flags=cv2.IMREAD_COLOR)
	return pic

#https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines
def findIntersection(x1,y1,x2,y2,x3,y3,x4,y4):
	px= ( (x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4) ) / ( (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) )
	py= ( (x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4) ) / ( (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) )
	return (int(px), int(py))

#This function takes an angle and outputs a recommend correction code
def interpret_angle_for_rotation_code(angle):
	
	return angle
	# correction_code = 0
	# if ((angle >= 5) and (angle < 15.0)):
	#     correction_code = 1 # move left
	# elif ((angle >= 15.0) and (angle < 30.0)):
	#     correction_code = 2
	# elif ((angle >= 30.0) and (angle < 45.0)):
	#     correction_code = 3
	# elif ((angle < -5) and (angle > -15.0)):
	#     correction_code = -1 #move right
	# elif ((angle <= -15.0) and (angle > -30.0)):
	#     correction_code = -2
	# elif ((angle <= -30.0) and (angle > -45.0)):
	#     correction_code = -3
	# return correction_code

def get_rho_theta_horizontals(hough_lines_list, img):
	horizontals = []
	thetas = []
	rhos = []
	for line in hough_lines_list:
		for rho, theta in line:
			#Get the x,y,slope values from polar coordinates
			x1, y1, x2, y2, slope = get_xy_values(rho, theta)
			#Horizontal line
			slope_threshold = 0.4
			if ((-slope_threshold < slope) and (slope < slope_threshold)):
				cv2.line(img,(x1, y1),(x2, y2),(0,0,255),2)
				print(slope)
				horizontals.append(slope)
				thetas.append(theta)
				rhos.append(rho)
	cv2.imwrite('lines_on_canny' + '.jpg',img)
	return horizontals, thetas, rhos

def get_xy_values(rho, theta):
	a = np.cos(theta)
	b = np.sin(theta)
	x0 = a*rho
	y0 = b*rho
	x1 = int(x0 + 1000*(-b))
	y1 = int(y0 + 1000*(a))
	x2 = int(x0 - 1000*(-b))
	y2 = int(y0 - 1000*(a))
	try:
		slope = float(((y2-y1)/(x2-x1)))
	except ZeroDivisionError:
		slope = 9999
	return [x1, y1, x2, y2, slope]


def process_image():
	
	#Resize the image for consistency
	img = cv2.VideoCapture(0)
	ret, img = img.read()
	img = cv2.resize(img, (300, 240))
	#img = cv2.resize(img, (1200, 960))
	#Display original image
	#Crop the portion of the photo we care about
	height = img.shape[0]
	width = img.shape[1]
	width_fourth = int(width/4)
	
	#y range, x range for cropping
	#Top portion used for rotation adjustment
	upper_cropped = img[0:height, width_fourth:width - width_fourth]
	
	
	#Set filter bounds to all blue colors
	lower_bound = np.array([30,0,0])
	upper_bound = np.array([225,80,80])
	
	#Apply the blue mask to the cropped image
	blue_mask_upper = cv2.inRange(upper_cropped, lower_bound, upper_bound)
	
	#reduce non-blue stuff to be black, keep blue as blue
	# result_upper =  cv2.bitwise_and(upper_cropped, upper_cropped, mask=blue_mask_upper)
	# reduce the image to black and white
	result_upper = np.stack((blue_mask_upper,blue_mask_upper,blue_mask_upper), axis=2)
	
	cv2.imwrite('masked_image' + '.jpg',result_upper)
	
	
	#Apply canny edge detection to the result image
	edges_upper = cv2.Canny(result_upper,25,150,apertureSize = 3)
	
	
	# Copy edges to the images that will display the results in BGR
	cdst = cv2.cvtColor(edges_upper, cv2.COLOR_GRAY2BGR)
	cv2.imwrite('canny_result' + '.jpg',cdst)
	
	cdstP = np.copy(cdst)
	
	# these parameters do nothing? maybe used in probabalistic transofrm but not normal version???
	minLineLength = 500#20
	maxLineGap = 0#30
	
	#Apply the hough lines transform to the canny results
	lines_upper = cv2.HoughLines(edges_upper,
								 5,   # rho, resolution of parameter r in pixels
								 np.pi/180,
								 70,   # threshold
								 minLineLength,
								 maxLineGap)
	
	
	if lines_upper is not None:
		for i in range(0, len(lines_upper)):
			rho = lines_upper[i][0][0]
			theta = lines_upper[i][0][1]
			a = math.cos(theta)
			b = math.sin(theta)
			x0 = a * rho
			y0 = b * rho
			pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
			pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
			cv2.line(cdst, pt1, pt2, (0,0,255), 3, cv2.LINE_AA)
		cv2.imwrite('hough_result' + '.jpg',cdst)
	
	
	#Upper crop line parameter lists
	horizontals_upper = []
	verticals_upper = []
	theta_list_upper = []
	rho_list_upper = []
	
	#Only analyze images with valid lines found, should be always
	if lines_upper is None:
		return None
	elif len(lines_upper) <= 1:
		return None
	else:
		upper_horizontals, upper_thetas, upper_rhos = get_rho_theta_horizontals(lines_upper, cdstP)
		
		angle_sum = 0.0
		rho_sum = 0.0
		#Get the average angle of the horizontal lines
		for angle in upper_thetas:
			angle_sum += angle
		avg_theta = float(angle_sum/len(upper_thetas))
		
		#Get average length of lines
		for val in upper_rhos:
			rho_sum += val
		
		avg_rho = float(rho_sum/len(upper_rhos))
		avg_line_parameters = get_xy_values(avg_rho, avg_theta)
		x1 = avg_line_parameters[0]
		y1 = avg_line_parameters[1]
		x2 = avg_line_parameters[2]
		y2 = avg_line_parameters[3]
		
		#Calculate the angle with respect to horizontal for the average line
		radians = math.atan2(y1-y2, x2-x1)
		true_angle = math.degrees(radians)
		# rotation_correction_code = interpret_angle_for_rotation_code(true_angle)
		
		cv2.line(result_upper,(x1, y1),(x2, y2),(0,0,255),2)
		
		cv2.imwrite('upper_result_final' + '.jpg',result_upper)
		return true_angle
	
	#print("File: ", str(file), " analysis: Rotation correction: ", str(rotation_correction_code), " Forward/Back code: ", forward_back_code)
    
