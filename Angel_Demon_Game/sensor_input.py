#Program: Uses a webcam and OpenCV to determine brightness of a specified area
#Author: Tristan Cunderla
#Last edit: 11/6/2019

import numpy as np
import cv2
from PIL import Image
from PIL import ImageStat
import time

threshold_value = []
font = cv2.FONT_HERSHEY_SIMPLEX

# if True, brightness value will be printed
print_brightness = False
# if True, code will tell you when the image has been taken
print_take_image = False

# these values indicate where to start the first light zone
x_start = 50
y_start = 50
# these values indicate the height and width of each light zone
x_width = 110
y_height = 125

# These values define the borders of each brightness zone (currently this is a 5 by 3 grid)

# row 1

A_x_start = x_start
A_x_end = A_x_start + x_width
A_y_start = y_start
A_y_end = A_y_start + y_height

B_x_start = A_x_end
B_x_end = B_x_start + x_width
B_y_start = A_y_start
B_y_end = B_y_start + y_height

C_x_start = B_x_end
C_x_end = C_x_start + x_width
C_y_start = A_y_start
C_y_end = C_y_start + y_height

D_x_start = C_x_end
D_x_end = D_x_start + x_width
D_y_start = y_start
D_y_end = D_y_start + y_height

E_x_start = D_x_end
E_x_end = E_x_start + x_width
E_y_start = y_start
E_y_end = E_y_start + y_height

# row 2

F_x_start = x_start
F_x_end = F_x_start + x_width
F_y_start = E_y_end
F_y_end = F_y_start + y_height

G_x_start = F_x_end
G_x_end = G_x_start + x_width
G_y_start = F_y_start
G_y_end = G_y_start + y_height

H_x_start = G_x_end
H_x_end = H_x_start + x_width
H_y_start = G_y_start
H_y_end = H_y_start + y_height

I_x_start = H_x_end
I_x_end = I_x_start + x_width
I_y_start = H_y_start
I_y_end = I_y_start + y_height

J_x_start = I_x_end
J_x_end = J_x_start + x_width
J_y_start = I_y_start
J_y_end = J_y_start + y_height

# row 3 (k,l,m,n,o)

K_x_start = x_start
K_x_end = K_x_start + x_width
K_y_start = J_y_end
K_y_end = K_y_start + y_height

L_x_start = K_x_end
L_x_end = L_x_start + x_width
L_y_start = K_y_start
L_y_end = L_y_start + y_height

M_x_start = L_x_end
M_x_end = M_x_start + x_width
M_y_start = L_y_start
M_y_end = M_y_start + y_height

N_x_start = M_x_end
N_x_end = N_x_start + x_width
N_y_start = M_y_start
N_y_end = N_y_start + y_height

O_x_start = N_x_end
O_x_end = O_x_start + x_width
O_y_start = N_y_start
O_y_end = O_y_start + y_height

# get_brightness function -> gets the average brightness within a specified area
def getBrightness( im_file, x_start, x_end, y_start, y_end):
   im = Image.open(im_file).convert('RGB')
   total = 0
   count = 0
   current_x = x_start
   current_y = y_start

   # get the brightness of every pixel in the light zone
   while current_y <= y_end:
      while current_x <= x_end:
         pixelRGB = im.getpixel((current_x,current_y))
         R,G,B = pixelRGB
         brightness = sum([R,G,B])/3
         total = total + brightness
         current_x = current_x + 1
         count = count + 1
      current_y = current_y + 1
      current_x = x_start
   # calculate average brightness
   average_brightness = total/count
   # return average brightness
   return average_brightness

# get_value function -> computes the brightness of each zone and then uses the middle 13 to calculate brightness
def get_value(im_file):
   global print_brightness
   global A_x_start, A_x_end, A_y_start, A_y_end
   global B_x_start, B_x_end, B_y_start, B_y_end
   global C_x_start, C_x_end, C_y_start, C_y_end
   global D_x_start, D_x_end, D_y_start, D_y_end
   global E_x_start, E_x_end, E_y_start, E_y_end
   global F_x_start, F_x_end, F_y_start, F_y_end
   global G_x_start, G_x_end, G_y_start, G_y_end
   global H_x_start, H_x_end, H_y_start, H_y_end
   global I_x_start, I_x_end, I_y_start, I_y_end
   global J_x_start, J_x_end, J_y_start, J_y_end
   global K_x_start, K_x_end, K_y_start, K_y_end
   global L_x_start, L_x_end, L_y_start, L_y_end
   global M_x_start, M_x_end, M_y_start, M_y_end
   global N_x_start, N_x_end, N_y_start, N_y_end
   global O_x_start, O_x_end, O_y_start, O_y_end

   brightness_values = []

   # calculating brightness for each zone
   brightness_values.append(getBrightness(im_file, A_x_start, A_x_end, A_y_start, A_y_end))
   brightness_values.append(getBrightness(im_file, B_x_start, B_x_end, B_y_start, B_y_end))
   brightness_values.append(getBrightness(im_file, C_x_start, C_x_end, C_y_start, C_y_end))
   brightness_values.append(getBrightness(im_file, E_x_start, E_x_end, E_y_start, E_y_end))
   brightness_values.append(getBrightness(im_file, F_x_start, F_x_end, F_y_start, F_y_end))
   brightness_values.append(getBrightness(im_file, G_x_start, G_x_end, G_y_start, G_y_end))
   brightness_values.append(getBrightness(im_file, H_x_start, H_x_end, H_y_start, H_y_end))
   brightness_values.append(getBrightness(im_file, I_x_start, I_x_end, I_y_start, I_y_end))
   brightness_values.append(getBrightness(im_file, J_x_start, J_x_end, J_y_start, J_y_end))
   brightness_values.append(getBrightness(im_file, K_x_start, K_x_end, K_y_start, K_y_end))
   brightness_values.append(getBrightness(im_file, L_x_start, L_x_end, L_y_start, L_y_end))
   brightness_values.append(getBrightness(im_file, M_x_start, M_x_end, M_y_start, M_y_end))
   brightness_values.append(getBrightness(im_file, N_x_start, N_x_end, N_y_start, N_y_end))
   brightness_values.append(getBrightness(im_file, O_x_start, O_x_end, O_y_start, O_y_end))

   # sorting brightness values from min to max
   brightness_values.sort()
   max_value = len(brightness_values)
   # remove max and min values
   brightness_values.pop(max_value-1)
   brightness_values.pop(0)
   total = 0
   # calculate average brightness of remaining zones
   for value in brightness_values:
      total = total + value
   average_brightness = (total/len(brightness_values))

   # determining which zone the robot is in
   if ((0 <= average_brightness) and (average_brightness <= 99)):
      zone = [0,0]
   elif ((99 < average_brightness) and ( average_brightness<= 125)):
      zone = [0,1]
   elif ((125 < average_brightness) and (average_brightness <= 152)):
      zone = [1,0]
   else:
      zone = [1,1]

   # print average brightness value
   if print_brightness == True:
      print("Avg brightness: ", average_brightness)

   # return the light zone
   return zone

# run_input function -> captures the image and calculates the average brightness and determines the light zone        
def run_input():

   global print_take_image

   # take photo to get brightness
   cap = cv2.VideoCapture(0)
   ret, frame = cap.read()
   cv2.imwrite("NewPicture.jpg",frame)

   # indicate the photo was taken
   if print_take_image == True:
      print('imageupdated')

   # get the average brightness
   light_zone = get_value("NewPicture.jpg")
   # release camera
   cap.release()
   # return average brightness
   return light_zone
           
   # When everything done, release the capture
   cap.release()
   cv2.destroyAllWindows()


#print(run_input())
