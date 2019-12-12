#File: Measures the approximate forward/back adjustment needed using Canny Edge detection and hough line filtering

#Package imports
import numpy as np
import math
import os
import cv2
from scipy import ndimage


#Display image with cv
def display_image(image):
	cv2.imshow("TEST", image)
	cv2.waitKey(0)

#Simple function to read an image with cv
def read_image(image):
	pic = cv2.imread(image, flags=cv2.IMREAD_COLOR)
	return pic

#Function to find the intersection of two lines, obtained from:
#https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines
def findIntersection(x1,y1,x2,y2,x3,y3,x4,y4):
	px= ( (x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4) ) / ( (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) ) 
	py= ( (x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4) ) / ( (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) )
	return (int(px), int(py))

#Function to return a forward/back correction code from an average y-value input
def interpret_y_for_forward_back_code(y_val):
	correction_code = 0
	print("The avg y val is: ", y_val)
	if ((y_val >= 0) and (y_val <= 200)):
		correction_code = -1
	elif ((y_val >= 400) and (y_val <= 600)):
		correction_code = 1
	return correction_code
		
#Function to obtain all lines within a slope threshold from a hough lines list
def get_rho_theta_horizontals(hough_lines_list):
	horizontals = []
	thetas = []
	rhos = []
	for line in hough_lines_list:
		for rho, theta in line:
			#Get the x,y,slope values from polar coordinates
			temp = get_xy_values(rho, theta)
			slope = temp[4]
			#Horizontal line
			if ((-0.4 < slope) and (slope < 0.4)):
				horizontals.append(temp)
				thetas.append(theta)
				rhos.append(rho)
	return horizontals, thetas, rhos

#Function to obtain the X, Y values of a line from polar coordinates
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
		slope = 0
	return [x1, y1, x2, y2, slope]
	
#Primary function to process an image and obtain the approximate rotation offset
def process_image():
	#Take a fresh capture
	img = cv2.VideoCapture(0)
	#Read into proper format
	ret, img = img.read()
	#Resize the image for consistency
	img = cv2.resize(img, (300, 240))
	
	#Crop the portion of the photo we care about
	height = img.shape[0]
	width = img.shape[1]
	width_fourth = int(width/4)
	
	#y range, x range for cropping
	upper_cropped = img[0:height, width_fourth:width - width_fourth]
	
	#Set filter bounds to all blue colors
	lower_bound = np.array([30,0,0])
	upper_bound = np.array([225,80,80])
	
	#Apply the blue mask to the cropped image
	blue_mask_upper = cv2.inRange(upper_cropped, lower_bound, upper_bound)
	
	#Reduce non-blue pixels to be black, keep blue as blue
	#Reduce the image to black and white
	result_upper = np.stack((blue_mask_upper,blue_mask_upper,blue_mask_upper), axis=2)
	
	cv2.imwrite('masked_image' + '.jpg',result_upper)
	
	#Apply canny edge detection to the result image
	edges_upper = cv2.Canny(result_upper,25,150,apertureSize = 3)
	
	# Copy edges to the images that will display the results in BGR
	cdst = cv2.cvtColor(edges_upper, cv2.COLOR_GRAY2BGR)
	cv2.imwrite('canny_result' + '.jpg',cdst)
	
	cdstP = np.copy(cdst)
	
	#Hough line parameters
	minLineLength = 500#20
	maxLineGap = 0#30
	
	#Apply the hough lines transform to the canny results
	lines_upper = cv2.HoughLines(edges_upper,
								 5,   # rho, resolution of parameter r in pixels
								 np.pi/180,
								 70,   # threshold
								 minLineLength,
								 maxLineGap)
	
	#Extract information from lines list
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
		#Translate lines
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
		
		#Create the "average" line
		avg_rho = float(rho_sum/len(upper_rhos))
		avg_line_parameters = get_xy_values(avg_rho, avg_theta)
		x1 = avg_line_parameters[0]
		y1 = avg_line_parameters[1]
		x2 = avg_line_parameters[2]
		y2 = avg_line_parameters[3]
		avg_y = float((y1 + y2)/2)
		#Interpret average y for a correction code
		forward_back_code = interpret_y_for_forward_back_code(avg_y)
	
		cv2.line(result_lower,(x1, y1),(x2, y2),(0,0,255),2)
		cv2.imwrite('lower_result' + '.jpg',result_lower)
		
	else:
		forward_back_code = None
	#Return the correction code
	return forward_back_code
			
