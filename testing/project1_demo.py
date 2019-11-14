# demonstrate the "macro-motion" functions


import sys
sys.path.append("../project_files/robot_drivers/")
import time
import pwm_wrapper as pw
import hex_walker_driver_v2 as hwd
from hex_walker_constants import *
pwm_bot = pw.Pwm_Wrapper(PWM_ADDR_BOTTOM, PWM_FREQ)
rf = hwd.Leg(pwm_bot, PWM_CHANNEL_ARRAY[LEG_RF], LEG_RF) #0
rm = hwd.Leg(pwm_bot, PWM_CHANNEL_ARRAY[LEG_RM], LEG_RM) #1
rb = hwd.Leg(pwm_bot, PWM_CHANNEL_ARRAY[LEG_RB], LEG_RB) #2
larm = hwd.Leg(pwm_bot, PWM_CHANNEL_ARRAY[ARM_L], ARM_L) #6
rot = hwd.Rotator(pwm_bot, PWM_CHANNEL_ARRAY[WAIST], WAIST) #8

pwm_top = pw.Pwm_Wrapper(PWM_ADDR_TOP, PWM_FREQ)
lb = hwd.Leg(pwm_top, PWM_CHANNEL_ARRAY[LEG_LB], LEG_LB) #3
lm = hwd.Leg(pwm_top, PWM_CHANNEL_ARRAY[LEG_LM], LEG_LM) #4
lf = hwd.Leg(pwm_top, PWM_CHANNEL_ARRAY[LEG_LF], LEG_LF) #5
rarm = hwd.Leg(pwm_top, PWM_CHANNEL_ARRAY[ARM_R], ARM_R) #7

#create the hex walker
hex_walker = hwd.Hex_Walker(rf, rm, rb, lb, lm, lf)
# create the torso
torso = hwd.Robot_Torso(rarm, larm, rot)


cmd = 999

while(cmd != 0):
	print("0 - quit")
	print("1 - torso does monkey")
	print("2 - torso waves")
	print("3 - walk 1 step")
	print("4 - walk 4 steps")
	print("5 - walk back 1 step")
	print("6 - walk back 4 step")
	print("7 - walk 120 degrees 1 step")
	print("8 - walk 120 degrees 4 steps")
	print("9 - rotate left 1 step")
	print("10 - rotate left 4 steps")
	print("11 - rotate right 1 step")
	print("12 - rotate right 4 steps")
	print("13 - hand shake")
	print("14 - king kong")
	print("15 - leg wave left")
	print("16 - leg wave right")
	print("17 - bounce down")
	print("18 - fine rotate left")
	print("19 - fine rotate right")
	print("20 - change speed")

	while(True):
		r = input("Choose an option:")
		try:
			cmd = int(r)
		except ValueError:
			# if given non-numeric input, ask again
			print("error")
			continue
		# if given valid numeric input, break
		break

	if(cmd == 0):
		sys.exit()
	if(cmd == 1):
		print("doing the monkey 5 times")
		torso.monkey(5)
	elif(cmd == 2):
		print("waving to the left 3 times")
		torso.wave(45, 3)
	elif(cmd == 3):
		print("walking one step forward")
		hex_walker.walk(1, 0)
	elif(cmd == 4):
		print("walking 4 steps forward")
		hex_walker.walk(4,0)
	elif(cmd == 5):
		print("walking 1 step backward")
		hex_walker.walk(1, 180)
	elif(cmd == 6):
		print("walking 4 steps backward")
		hex_walker.walk(4, 180)
	elif(cmd == 7):
		print("walking 1 step at 120 degrees")
		hex_walker.walk(1, 120)
	elif(cmd == 8):
		print("walking 4 steps at 120 degrees")
		hex_walker.walk(4, 120)
	elif(cmd == 9):
		print("rotate left l step")
		hex_walker.rotate(1, LEFT)
	elif(cmd ==10):
		print("rotate left 4 steps")
		hex_walker.rotate(4, LEFT)
	elif(cmd == 11):
		print("rotate right 1 step")
		hex_walker.rotate(1, RIGHT)
	elif(cmd == 12):
		print("roate right 4 step")
		hex_walker.rotate(4, RIGHT)
	elif(cmd == 13):
		print("hand shake")
		torso.hand_shake(90, 4)
	elif(cmd == 14):
		print("king kong")
		torso.king_kong(90, 4)
	elif(cmd == 15):
		print("leg wave left")
		hex_walker.leg_wave(LEFT, .1, 4)
	elif(cmd == 16):
		print("leg wave right")
		hex_walker.leg_wave(RIGHT, .1, 4)
	elif(cmd == 17):
		print("bounce down")
		hex_walker.bounce(.3, 4)
	elif(cmd == 18):
		print("fine rotate left l step")
		hex_walker.fine_rotate(1, LEFT)
	elif(cmd == 19):
		print("fine rotate right 1 step")
		hex_walker.fine_rotate(1, RIGHT)
	elif(cmd == 20):
		print("change speed")
		s = input("new speed (float): ")
		try:
			f = float(s)
			hex_walker.set_speed(f)
		except ValueError:
			print("failed")
	else:
		print("cmd not recognized")
