import numpy as np
import cv2
from PIL import Image
from PIL import ImageStat

cap = cv2.VideoCapture(0)
threshold_value = []
font = cv2.FONT_HERSHEY_SIMPLEX

x_start = 50
y_start = 50
x_width = 110
y_height = 125

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

def brightness( im_file ):
   im = Image.open(im_file).convert('L')
   stat = ImageStat.Stat(im)
   return stat.mean[0]

def threshold(sensor, input_value):
   global threshold_value
   if sensor == 0:
      if  threshold_value[0] > input_value:
         motor_dir = 0
      else:
         motor_dir = 1
   elif sensor == 1:
      if  threshold_value[1] > input_value:
         motor_dir = 0
      else:
         motor_dir = 1
   return motor_dir

def motor_set(input_string):
   if input_string == "Below threshold":
      motor = 0
   else:
      motor = 1
   return int(motor)
   

def getBrightness( im_file, x_start, x_end, y_start, y_end):
   im = Image.open(im_file).convert('RGB')
   total = 0
   count = 0
   current_x = x_start
   current_y = y_start
   
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
   average_brightness = total/count
   return average_brightness

def movement(inA,inB):
   motorA = int(inA)
   motorB = int(inB)
   if motorA == 1 and motorB == 1:
      out_string = "Forward"
   elif motorA == 1 and motorB == 0:
      out_string = "Turn Right"
   elif motorA == 0 and motorB == 1:
      out_string = "Turn Left"
   else:
      out_string = "Not Moving"
   return out_string

def get_value(im_file):
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

   brightness_values.sort()
   max_value = len(brightness_values)
   brightness_values.pop(max_value-1)
   brightness_values.pop(0)
   total = 0
   for value in brightness_values:
      total = total + value
   average_brightness = (total/len(brightness_values))

   if ((0 <= average_brightness) and (average_brightness <= 99)):
      zone = [0,0]
   elif ((99 < average_brightness) and ( average_brightness<= 125)):
      zone = [0,1]
   elif ((125 < average_brightness) and (average_brightness <= 152)):
      zone = [1,0]
   else:
      zone = [1,1]
   print("Avg brightness: ", average_brightness)
   return zone
   
         
        
def startup():
    global threshold_value
    count = 0
    totalA = 0
    totalB = 0
    threshold_offset = 20
    while count != 10:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imwrite("NewPicture.jpg",frame)
        brightA = getSensorA("NewPicture.jpg")
        brightB = getSensorB("NewPicture.jpg")
        totalA = totalA + brightA
        totalB = totalB + brightB
        count = count + 1
    thresholdA = totalA/count + threshold_offset
    thresholdB = totalB/count + threshold_offset
    threshold_value = [thresholdA,thresholdB]
    return threshold_value

def run_input():

   global A_x_start, A_x_end, A_y_start, A_y_end
   motors = []
   #startup()
   while(True):
       # Capture frame-by-frame
       ret, frame = cap.read()

       # Our operations on the frame come here
       gray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

       # info to display on screen
       cv2.imwrite("update.jpg",gray)
       
       # Display rectangles and text on screen
       
       #cv2.putText(gray,'Sensor A',(80,215), font, 1, (0,0, 255), 2, cv2.LINE_AA)
       #cv2.putText(gray,'Sensor B',(380,215), font, 1, (255,0, 0), 2, cv2.LINE_AA)
       #cv2.putText(gray,sensorA_threshold,(10,30), font, 0.7, (0,0, 255), 2, cv2.LINE_AA)
       #cv2.putText(gray,sensorB_threshold,(400,30), font, 0.7, (255,0, 0), 2, cv2.LINE_AA)
       #cv2.putText(gray,sensorA_value,(110,350), font, 0.7, (0,0, 255), 2, cv2.LINE_AA)
       #cv2.putText(gray,sensorB_value,(410,350), font, 0.7, (255,0, 0), 2, cv2.LINE_AA)

       # row 1
       cv2.rectangle(gray,(A_x_start,A_y_start),(A_x_end,A_y_end),(0,0,0),3)
       cv2.rectangle(gray,(B_x_start,B_y_start),(B_x_end,B_y_end),(0,0,0),3)
       cv2.rectangle(gray,(C_x_start,C_y_start),(C_x_end,C_y_end),(0,0,0),3)
       cv2.rectangle(gray,(D_x_start,D_y_start),(D_x_end,D_y_end),(0,0,0),3)
       cv2.rectangle(gray,(E_x_start,E_y_start),(E_x_end,E_y_end),(0,0,0),3)

       #row 2
       cv2.rectangle(gray,(F_x_start,F_y_start),(F_x_end,F_y_end),(0,0,0),3)
       cv2.rectangle(gray,(G_x_start,G_y_start),(G_x_end,G_y_end),(0,0,0),3)
       cv2.rectangle(gray,(H_x_start,H_y_start),(H_x_end,H_y_end),(0,0,0),3)
       cv2.rectangle(gray,(I_x_start,I_y_start),(I_x_end,I_y_end),(0,0,0),3)
       cv2.rectangle(gray,(J_x_start,J_y_start),(J_x_end,J_y_end),(0,0,0),3)

       #row 3
       cv2.rectangle(gray,(K_x_start,K_y_start),(K_x_end,K_y_end),(0,0,0),3)
       cv2.rectangle(gray,(L_x_start,L_y_start),(L_x_end,L_y_end),(0,0,0),3)
       cv2.rectangle(gray,(M_x_start,M_y_start),(M_x_end,M_y_end),(0,0,0),3)
       cv2.rectangle(gray,(N_x_start,N_y_start),(N_x_end,N_y_end),(0,0,0),3)
       cv2.rectangle(gray,(O_x_start,O_y_start),(O_x_end,O_y_end),(0,0,0),3)

       # Display the resulting frame
       cv2.imshow('frame',gray)
       k = cv2.waitKey(1)
       
       # escape key exits
       if k%256 == 27:
           break
       #space key takes photo
       elif k%256 == 32:
           cv2.imwrite("NewPicture.jpg",frame)
           light_zone = get_value("NewPicture.jpg")
           return light_zone
           break
           

          

   # When everything done, release the capture
   cap.release()
   cv2.destroyAllWindows()


#print(run_input())
