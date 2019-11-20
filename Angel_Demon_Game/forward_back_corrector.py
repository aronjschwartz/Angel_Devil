#Program: Measures the y value of the lower line, outputs forward/back correction code


import numpy as np
import math
import os
import cv2
from scipy import ndimage
from skimage.transform import (hough_line, hough_line_peaks)

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

def interpret_y_for_forward_back_code(y_val):
	correction_code = 0
	print("The avg y val is: ", y_val)
	if ((y_val >= 0) and (y_val <= 200)):
		correction_code = -1
	elif ((y_val >= 400) and (y_val <= 600)):
		correction_code = 1
	return correction_code
		

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
	
def process_image(img):
	
	
	#Resize the image for consistency
	img = cv2.resize(img, (1200, 960))
	#Display original image
	#Crop the portion of the photo we care about
	height = img.shape[0]
	width = img.shape[1]
	width_fourth = int(width/4)
	
	#y range, x range for cropping

	lower_cropped = img[height-600:height, width_fourth:width - width_fourth]
	
	#Set filter bounds to all blue colors
	lower_bound = np.array([100,0,0])
	upper_bound = np.array([225,80,80])
	
	blue_mask_lower = cv2.inRange(lower_cropped, lower_bound, upper_bound)
	
	result_lower =  cv2.bitwise_and(lower_cropped, lower_cropped, mask=blue_mask_lower)
	
	edges_lower = cv2.Canny(result_lower,25,150,apertureSize = 3)
	minLineLength = 20
	maxLineGap = 30
	
	lines_lower = cv2.HoughLines(edges_lower,1,np.pi/180,20,minLineLength,maxLineGap)

	
	#Lower crop line parameters lists
	horizontals_lower = []
	verticals_lower = []
	theta_list_lower = []
	rho_list_lower = []
	#Only analyze images with valid lines found, should be always
	
		
	if len(lines_lower) > 1:
		lower_horizontals, lower_thetas, lower_rhos = get_rho_theta_horizontals(lines_lower)

		angle_sum = 0.0
		rho_sum = 0.0
		#Get the average angle of the horizontal lines
		for angle in lower_thetas:
			angle_sum += angle
		avg_theta = float(angle_sum/len(lower_thetas))
		
		#Get average length of lines
		for val in lower_rhos:
			rho_sum += val
			
		avg_rho = float(rho_sum/len(lower_rhos))
		avg_line_parameters = get_xy_values(avg_rho, avg_theta)
		y1 = avg_line_parameters[1]		
		y2 = avg_line_parameters[3]
		avg_y = float((y1 + y2)/2)
		forward_back_code = interpret_y_for_forward_back_code(avg_y)
	
		#cv2.line(result_lower,(x1, y1),(x2, y2),(0,0,255),2)
		#cv2.imwrite('lower_' + str(file_count) + '.jpg',result_lower)
		
	else:
		forward_back_code = -1
		

	return forward_back_code
			
