# directly set the angle/PWM values of a single servo
# use extreme caution, this can easily damage the servos or drain the battery

import sys
sys.path.append("../project_files/robot_drivers/")
import time
import pwm_wrapper
from hex_walker_driver_v2 import *
from hex_walker_constants import *
pwm_bot = pwm_wrapper.Pwm_Wrapper(PWM_ADDR_BOTTOM, PWM_FREQ)
rf = Leg(pwm_bot, LEG_PWM_CHANNEL[LEG_RF], LEG_RF) #0
rm = Leg(pwm_bot, LEG_PWM_CHANNEL[LEG_RM], LEG_RM) #1
rb = Leg(pwm_bot, LEG_PWM_CHANNEL[LEG_RB], LEG_RB) #2
larm = Leg(pwm_bot, LEG_PWM_CHANNEL[ARM_L], ARM_L) #6
# rot = Rotator(0, pwm_bot, LEG_PWM_CHANNEL[WAIST][WAIST_MOTOR]) #8
rot = Rotator(pwm_bot, LEG_PWM_CHANNEL[WAIST], WAIST) #8

pwm_top = pwm_wrapper.Pwm_Wrapper(PWM_ADDR_TOP, PWM_FREQ)
lb = Leg(pwm_top, LEG_PWM_CHANNEL[LEG_LB], LEG_LB) #3
lm = Leg(pwm_top, LEG_PWM_CHANNEL[LEG_LM], LEG_LM) #4
lf = Leg(pwm_top, LEG_PWM_CHANNEL[LEG_LF], LEG_LF) #5
rarm = Leg(pwm_top, LEG_PWM_CHANNEL[ARM_R], ARM_R) #7


all_legs = [rf, rm, rb, lb, lm, lf, larm, rarm, rot]


print("This file is for directly setting the angle/PWM values of given servos to determine their active range.")
print("Both modes ignore the angle/PWM limits listed in the drivers, this means it is easily possible to damage the servos so be extremely careful! This is intended for determining new limits of the servos.")
print("USE EXTREME CAUTION")


# display current pwm value and its tentative limits
# prompt for new input & set, do_set_servo_pwm(), loop until non-numeric value given
def set_pwm_loop(legs, L, S):
		curr = legs[L].curr_servo_pwm[S]
		min = legs[L].SERVO_PWM_LIMITS[S][0]
		max = legs[L].SERVO_PWM_LIMITS[S][1]
		print("Leg="+str(L)+", servo="+str(S)+": curr PWM = "+str(curr)+", tentative range = "+str(min)+"-"+str(max))
		
		while(True):
			# prompt for actual value
			r = input("  PWM:")
			P = -1
			try:
				P = int(r)
			except ValueError:
				# if given non-numeric input, go up a level
				break
			if P < 0 or P > 4095:
				# if invalid numeric input, prompt again
				print("err: input out of range")
				continue
				
			# actually set the PWM
			legs[L].do_set_servo_pwm(P, S)


# display current angle value and its tentative limits
# prompt for new input & set, do_set_servo_angle(), loop until non-numeric value given
def set_angle_loop(legs, L, S):
		curr = legs[L].curr_servo_angle[S]
		min = legs[L].SERVO_ANGLE_LIMITS[S][0]
		max = legs[L].SERVO_ANGLE_LIMITS[S][1]
		print("Leg="+str(L)+", servo="+str(S)+": curr angle = "+str(curr)+", tentative range = "+str(min)+"-"+str(max))
		
		while(True):
			# prompt for actual value
			r = input("  Angle:")
			P = -1
			try:
				P = float(r)
			except ValueError:
				# if given non-numeric input, go up a level
				break
			if P < 0 or P > 360:
				# if invalid numeric input, prompt again
				print("err: input out of range")
				continue
				
			# actually set the PWM
			legs[L].do_set_servo_angle(P, S)




# ask if using PWM or angle mode
mode = -1
while(True):
	print("Running in 0=PWM or 1=ANGLE mode?")
	r = input("  Mode:")
	try:
		mode = int(r)
	except ValueError:
		# if given non-numeric input, ask again
		print("error")
		continue
	if mode < 0 or mode > 1:
		# if invalid numeric input, prompt again
		print("error")
		continue
	# if given valid numeric input, break
	break


# once non-numeric value given, go back one level
print("Enter a non-numeric input to go back up level")

while(True):
	# select which leg/arm: 0-8
	print("Select leg/arm/waist: (0-8) = (rf, rm, rb, lb, lm, lf, 6=larm, 7=rarm, 8=waist)")
	r = input("  Leg:")
	L = -1
	try:
		L = int(r)
	except ValueError:
		# if given non-numeric input, go up a level
		break
	if L < 0 or L > 8:
		# if invalid numeric input, prompt again
		print("err: input out of range")
		continue
		
	while(True):
		# select which joint: 0-2
		S = -1
		print("Leg="+str(L)+", select servo: (0-2) = (tip/waist, mid, rot)")
		r = input("  Servo:")
		try:
			S = int(r)
		except ValueError:
			# if given non-numeric input, go up a level
			break
		if S < 0 or S > 2:
			# if invalid numeric input, prompt again
			print("err: input out of range")
			continue
			
		if mode == 0:
			set_pwm_loop(all_legs, L, S)
		elif mode == 1:
			set_angle_loop(all_legs, L, S)
		#only returns when they want to go up a level, pick a new servo
		
print("exiting")
