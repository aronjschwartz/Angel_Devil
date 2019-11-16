#Program: Measures the angle of the central blue grid line, calcuates the angle, and outputs a recommended "correction"


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
	return cv2.imread(image,1)

#Intersection function from here:
#https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines
def findIntersection(x1,y1,x2,y2,x3,y3,x4,y4):
	px= ( (x1*y2-y1*x2)*(x3-x4)-(x1-x2)*(x3*y4-y3*x4) ) / ( (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) ) 
	py= ( (x1*y2-y1*x2)*(y3-y4)-(y1-y2)*(x3*y4-y3*x4) ) / ( (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4) )
	return (int(px), int(py))


#This function takes an angle and outputs a recommend correction code
def interpret_angle(angle):
	correction_code = 0
	if ((angle >= 0) and (angle < 15.0)):
		correction_code = 1
	elif ((angle >= 15.0) and (angle < 30.0)):
		correction_code = 2
	elif ((angle >= 30.0) and (angle < 45.0)):
		correction_code = 2
	elif ((angle < 0) and (angle > -15.0)):
		correction_code = -1
	elif ((angle <= -15.0) and (angle > -30.0)):
		correction_code = -2
	elif ((angle <= -30.0) and (angle > -45.0)):
		correction_code = -3
	return correction_code


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
	
def process_image():
	
	path = 'C:/Users/aronj/Grad_School_Classwork/Fall_2019/578_Robotics/Hexapod_Robotics1_Fall2018_Project2/blue_square_images/'

	file_count = 0
	display = False
	#Process each file in directory
	for file in os.listdir(path):
		image = os.path.join(path, file)
		img = read_image(image)
		
		#Resize the image for consistency
		img = cv2.resize(img, (1200, 960))
		#Display original image
		if (display):
			display_image(img)
		
		#Crop the portion of the photo we care about
		height = img.shape[0]
		width = img.shape[1]
		width_fourth = int(width/4)
		#y range, x range for cropping
		cropped = img[0:height-200, width_fourth:width - width_fourth]
		
		#Display the cropped image
		if (display):
			display_image(cropped)
		
		#Set filter bounds to all blue colors
		lower_bound = np.array([35,0,0])
		upper_bound = np.array([255,255,180])
		
		#Apply the blue mask to the cropped image
		blue_mask = cv2.inRange(cropped, lower_bound, upper_bound)
		#Display the mask
		if (display):
			display_image(blue_mask)
		#Display the mask combined with the cropped image
		result =  cv2.bitwise_and(cropped, cropped, mask=blue_mask)
		if (display):
			display_image(result)
	
		#Apply canny edge detection to the result image
		edges = cv2.Canny(result,25,150,apertureSize = 3)
		if (display):
			display_image(edges)
		minLineLength = 20
		maxLineGap = 30
		#Apply the hough lines transform to the canny results
		lines = cv2.HoughLines(edges,1,np.pi/180,50,minLineLength,maxLineGap)
		
		#Lists to hold relavent variables
		horizontals = []
		verticals = []
		theta_list = []
		rho_list = []
		#Only analyze images with valid lines found, should be always
		if len(lines) > 1:
			for line in lines:
				for rho, theta in line:
					#Get the x,y,slope values from polar coordinates
					temp = get_xy_values(rho, theta)
					slope = temp[4]
					#Horizontal line
					if ((-0.4 < slope) and (slope < 0.4)):
						horizontals.append(temp)
						theta_list.append(theta)
						rho_list.append(rho)
					#Vertical line
					else:
						verticals.append(temp)
			angle_sum = 0.0
			rho_sum = 0.0
			#Get the average angle of the horizontal lines
			for angle in theta_list:
				angle_sum += angle
			avg_theta = float(angle_sum/len(theta_list))
			
			#Get average length of lines
			for val in rho_list:
				rho_sum += val
				
			avg_rho = float(rho_sum/len(rho_list))
			avg_line_parameters = get_xy_values(avg_rho, avg_theta)
			x1 = avg_line_parameters[0]
			y1 = avg_line_parameters[1]
			x2 = avg_line_parameters[2]
			y2 = avg_line_parameters[3]
			
			#Calculate the angle with respect to horizontal for the average line
			radians = math.atan2(y1-y2, x2-x1)
			true_angle = (radians*180)/(math.pi)
			correction_code = interpret_angle(true_angle)
			print("The true average angle is: ", true_angle, " Correction code needed: ", str(correction_code))
			cv2.line(result,(x1, y1),(x2, y2),(0,0,255),2)
			cv2.imwrite('avg_line_' + str(file_count) + '.jpg',result)
			file_count += 1	
process_image()