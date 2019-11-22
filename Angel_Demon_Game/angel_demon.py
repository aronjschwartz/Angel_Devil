
#**********************************************************************************************
#*														                                      *
#*	   Program: Implements the Angel/Demon game with a quantum-based decision making          *
#*														                                      *
#**********************************************************************************************

import sys
sys.path.append("../project_files/robot_drivers/")

#Import libraries
import time
import numpy as np
import sensor_input
import random
import quantum_circuit
import rotation_corrector
import forward_back_corrector
import pyttsx3

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

# let the robot move nice and slow to show off the new smoothness
#hex_walker.set_speed(0.5)

stab_angle = 150

class Voice:
    def __init__(self, voice_num):
        self.tts = pyttsx3.init()
        voices = self.tts.getProperty('voices')
        self.tts.setProperty('voice', voices[voice_num].id)

    def say(self, message):
        self.tts.say(message)
        self.tts.runAndWait()

class Angel_Demon_Game():

	def __init__(self, turns_max, hex_walker):

		#Angel variables to track whos turn it is and if the angel has won
		self.angel_turn = 0 #random.randint(0,1)
		self.angel_victory = False

		#Devil variables to track if the devil has won
		self.devil_victory = False

		#Hexapod variable to hold the move to be executed by the hexapod
		self.hexapod_move = ""
		#Variable to hold the state ------------->  [TURN_BIT, LIGHT_BIT_0, LIGHT_BIT_1]
		self.state = [0,0,0]


		#Game variables to track the current turn and maximum amount of turns
		self.turn_num = 0
		self.max_turns = turns_max


		#Game board initialization with configurable heighth and width
		self.game_width = 4
		self.game_height = 7
		self.game_grid = [["   " for x in range(self.game_width)] for y in range(self.game_height)]


		#Initialize the bomb starting position
		self.bomb_y_pos = 2
		self.bomb_x_pos = 0
		self.game_grid[self.bomb_y_pos][self.bomb_x_pos] = "BOMB"


		#Initialize the bot starting position
		self.game_grid[self.game_height - 1][0] = "BOT"

		#Booleans for correction modes
		self.rotation_correction = False
		self.forward_back_correction = False
		voice = Voice(12)
		voice.say("Hello")

	#Function to clear the board.  Writes all values in the grid to a 1-character empty string
	def clear_board(self):
		for i in range(0, self.game_width):
			for j in range(0, self.game_height):
				self.game_grid[i][j] = " "

	#Function to move the bot up one square
	def move_board_bot_up(self):
		#Status code to track results of the attempted move.  0 = valid, 1 = devil victory, 2 = out of bounds rejection
		status = 0
		#Tracker boolean for easier loop control
		done = False
		#Loop through the rows and columns to find the bot location
		for i in range(0, self.game_height):
			for j in range(0, self.game_width):
				#Bot found
				if (self.game_grid[i][j] == "BOT"):
					#i = 0 corresponds to the top row, therefore cant move up more
					if (i == 0):
						#Set status to "out of bounds" and break
						status = 2
						done = True
						break
					else:
						#If the move is not out of bounds, see if it will result in the bot hitting the bomb
						try:
							self.game_grid[i][j] = "    "
							if (self.game_grid[i-1][j] == "BOMB"):
								#Set status to bomb detonation
								status = 1
								done = True
								break
							else:
								#Otherwise just move the bot and status remains at "0"
								self.game_grid[i-1][j] = "BOT"
								done = True
								break
						#Capture index errors for code safety
						except IndexError:
							status = 2
							done = True
							break

			if (done == True):
				break
		return status

	#Function to move the bot right one square
	def move_board_bot_right(self):
		#Status code to track results of the attempted move.  0 = valid, 1 = devil victory, 2 = out of bounds rejection
		status = 0
		#Tracker boolean for easier loop control
		done = False
		#Loop through the rows and columns to find the bot location
		for i in range(0, self.game_height):
			for j in range(0, self.game_width):

				#Bot found
				if (self.game_grid[i][j] == "BOT"):
					#j = (width - 1) corresponds to the right column, therefore cant move more right
					if (j == (self.game_width - 1)):
						#Set status to out-of-bounds and break
						status = 2
						done = True
						break
					else:
						#If the move is not out of bounds, see if it will result in the bot hitting the bomb
						try:
							self.game_grid[i][j] = "    "
							if (self.game_grid[i][j+1] == "BOMB"):
								#Set status to bomb detonation
								status = 1
								done = True
								break
							else:
								#Otherwise just move the bot and status remains at "0"
								self.game_grid[i][j+1] = "BOT"
								done = True
								break
						#Capture index errors for code safety
						except IndexError:
							status = 2
							done = True
							break

			if (done == True):
				break
		return status

	#Function to move the bot up-right one square
	def move_board_bot_up_right(self):
		#Status code to track results of the attempted move.  0 = valid, 1 = devil victory, 2 = out of bounds rejection
		status = 0
		#Tracker boolean for easier loop control
		done = False
		#Loop through the rows and columns to find the bot location
		for i in range(0, self.game_height):
			for j in range(0, self.game_width):

				#Bot found
				if (self.game_grid[i][j] == "BOT"):
					#Check if top row (i = 0) OR right column (j = width -1)
					#Reject move as out of bounds if either occurs
					if ((i == 0) or (j == (self.game_width - 1))):
						status = 2
						done = True
						break
					else:
						try:
							#If the move is not out of bounds, see if it will result in the bot hitting the bomb
							self.game_grid[i][j] = "    "
							if (self.game_grid[i-1][j+1] == "BOMB"):
								#Set status to bomb detonation
								status = 1
								done = True
								break
							else:
								#Otherwise just move the bot and status remains at "0"
								self.game_grid[i-1][j+1] = "BOT"
								done = True
								break

						except IndexError:
							status = 2
							done = True
							break

			if (done == True):
				break
		return status

	#Function to display the game board.  Uses np.matrix for easy 2d visualization
	def show_game_board(self):
		print()
		print(np.matrix(self.game_grid))
		print()

	#Function to execute the angel wins dance and console output
	def angel_wins(self):
		print()
		print("THE ANGEL WINS!!!")
		print()
		hex_walker.bounce(.3, 4)

	#Function to execute the devil wins dance and console output
	def devil_wins(self):
		print()
		print("THE DEVIL WINS!!! BOOM!")
		print()
		torso.king_kong(90, 4)

	#Function to prompt and obtain the angel desired move
	def select_move_angel(self):
		#Show possible moves
		choice = ""
		print("1 - No movement ")
		print("2 - Up ")
		choice = input("Enter choice: ")
		#Loop until valid input entered
		while(1):
			if (choice == "1"):
				choice = 1
				break
			elif (choice == "2"):
				choice = 2
				break
			#Reject if not valid input and re-prompt
			else:
				print("Invalid choice")
				choice = input("Enter choice: ")
		return choice

	#Function to prompt and obtain the devil desired move
	def select_move_devil(self):
		#Show possible moves
		choice = ""
		print("1 - Right ")
		print("2 - Up-Right ")
		choice = input("Enter choice: ")
		#Loop until valid input entered
		while(1):
			if (choice == "1"):
				choice = 1
				break
			elif (choice == "2"):
				choice = 2
				break
			#Reject if not valid and re-prompt
			else:
				print("Invalid choice")
				choice = input("Enter choice: ")
		return choice


	#Function to pass the state vector into the quantum module and return a resulting move code
	#Takes the 3 bit state as input -------------> [TURN_BIT, LIGHT_BIT_0, LIGHT_BIT_1]
	def quantum_translate(self, state):
		move_code = quantum_circuit.run_circuit(state[0], state[1], state[2])
		return move_code

	#Function to determine the light state and return a vector.  Vector is one of the four possible light zones (00, 01, 10, 11)
	def determine_state(self):
		vector = []
		vector = sensor_input.run_input()
		return vector

	#This function checks if it is still possible for the devil to win, meaning the bomb is still up and/or right of the bot
	def check_game_possibility(self):
		status = 0
		for y in range(0, self.game_height):
			for x in range(0, self.game_width):
				#Locate the bot
				if (self.game_grid[y][x] == "BOT"):
					#Ensure bot position allows possibility of devil still winning.  Return status = 1 if so
					if ((self.bomb_y_pos > y) or (self.bomb_x_pos < x)):
						status = 1
						return status
					#Otherwise return standard status indicating game is still on
					else:
						return status

	#Function to execute physical movement of the bot based on move code
	def move_hexapod(self, move_code):
		if (move_code == "N"):
			print("No movement")

		elif (move_code == "UP"):
			print("Move up")
			hex_walker.walk(20, DIR_F)

		elif (move_code == "UR"):
			print("Move up right")
			hex_walker.walk(20, DIR_F)
			time.sleep(0.1)
			hex_walker.rotate(5, RIGHT)
			time.sleep(0.1)
			hex_walker.walk(20, DIR_F)
			time.sleep(0.1)
			hex_walker.rotate(5, LEFT)

		elif (move_code == "R"):
			print("Move right")
			hex_walker.rotate(5, RIGHT)
			time.sleep(0.1)
			hex_walker.walk(20, DIR_F)
			time.sleep(0.1)
			hex_walker.rotate(5,LEFT)

	#Primary function to run the angel demon game
	def run_game(self):
		#Welcome message
		print("**************************************************************")
		print("*                                                            *")
		print("*       Welcome to the Angel-Devil QUANTUM robot game!       *")
		print("*                                                            *")
		print("**************************************************************")

		#Main game loop

		while(1):
			print("\n********* Starting turn ", self.turn_num, " **********\n")

			#Reset the move status (used to track if the move results in hitting the bomb)
			move_status = 0


			#Check whos turn it is
			if (self.angel_turn == 1):

				win_status = self.check_game_possibility()

				if (win_status == 1):
					self.angel_victory = True
					break
				print("***** Angels Turn *****")
				self.show_game_board()

				#Prompt user to select desired move
				move = self.select_move_angel()

				#Desired move is to do nothing
				if (move == 1):
					#Get the current light state
					partial_state = []
					partial_state = self.determine_state()

					print("Obtained state from sensors: ", partial_state)
					self.state = [self.angel_turn, partial_state[0], partial_state[1]]

					#Roll the quantum dice
					print("Sending total state to quantum: ", self.state)
					quantum = self.quantum_translate(self.state)

					#Depending on the quantum outcome, the bot listens or disobeys
					if (quantum == 0):
						print("Angel successfully tells bot to stay still")

					elif (quantum == 1):
						print("Angel disobeys neutrally and moves up!")
						move_status = self.move_board_bot_up()
						#Return code of '1' means we hit the bomb
						if (move_status == 1):
							torso.stab(stab_angle, 1)
							self.move_hexapod("UP")
							self.devil_victory = True
							break
						elif(move_status == 2):
							print("Out of bounds move! Bot staying still")
						else:
							self.move_hexapod("UP")
					elif (quantum == 2): #Disobeys
						print("Bot disoboeys the Angel and moves right!")

						move_status = self.move_board_bot_right()

						#Return code of '1' means we hit the bomb
						if (move_status == 1):
							torso.stab(stab_angle ,1)
							self.move_hexapod("R")
							self.devil_victory = True
							break
						elif(move_status == 2):
							print("Out of bounds move! Bot staying still")

						else:
							self.move_hexapod("R")

				#Desired move is to go up
				elif (move == 2):
					#Get the current light state
					partial_state = []
					partial_state = self.determine_state()

					print("Obtained state from sensors: ", partial_state)
					self.state = [self.angel_turn, partial_state[0], partial_state[1]]
					print("Sending total state to quantum: ", self.state)
					quantum = self.quantum_translate(self.state)

					#Depending on the quantum outcome, the bot listens or disobeys (CHANCE TO BE ULTIMATELY INFLUENCED BY LIGHT LEVEL)
					if (quantum == 0):
						print("Angel successfully tells bot to move up!")
						move_status = self.move_board_bot_up()
						#Return code of '1' means we hit the bomb
						if (move_status == 1):
							torso.stab(stab_angle ,1)
							self.move_hexapod("UP")
							self.devil_victory = True
							break
						elif(move_status == 2):
							print("Out of bounds move! Bot staying still")
						else:
							self.move_hexapod("UP")
					elif (quantum == 1):
						print("Angel disobeys neutrally and stays still!")

					elif (quantum == 2): #Disobeys
						print("Bot disoboeys the Angel and moves up-right!")

						#move_status = self.move_board_bot_up_right()
						move_status = self.move_board_bot_up()

						#Return code of '1' means we hit the bomb
						if (move_status == 1):
							torso.stab(stab_angle ,1)
							self.move_hexapod("UP")
							self.devil_victory = True
							break
						elif(move_status == 2):
							print("Out of bounds move! Bot staying still")
						else:
							self.move_hexapod("UP")

						if(move_status != 1 and move_status != 2):
							move_status = self.move_board_bot_right()

							#Return code of '1' means we hit the bomb
							if (move_status == 1):
								torso.stab(stab_angle ,1)
								self.move_hexapod("R")
								self.devil_victory = True
								break
							elif(move_status == 2):
								print("Out of bounds move! Bot staying still")
							else:
								self.move_hexapod("R")

				self.angel_turn = 0
				self.turn_num +=1

				if (self.rotation_correction == True):
					rotation_check_code = rotation_corrector.process_image()
					print("Rotation code needed: ", str(rotation_check_code))
					if (rotation_check_code < 0):
						hex_walker.rotate(-1*(rotation_check_code), RIGHT)
					elif(rotation_check_code > 0):
						hex_walker.rotate(rotation_check_code, LEFT)

				if (self.forward_back_correction == True):
					forward_back_code = forward_back_corrector.process_image()
					print("Forward/back code needed: ", str(forward_back_code))
					if (forward_back_code < 0):
						hex_walker.walk(1, DIR_B)
					elif(forward_back_code > 0):
						hex_walker.rotate(1, 0)

				if (self.turn_num == self.max_turns):
					print("MAX TURNS REACHED, Angel wins!!")
					self.angel_victory = True
					break

			#Devils Turn
			elif(self.angel_turn == 0):

				win_status = self.check_game_possibility()

				if (win_status == 1):
					self.angel_victory = True
					break
				print("****** Devils Turn *****")
				self.show_game_board()

				#Prompt user to select desired move
				move = self.select_move_devil()

				#Desired move is to move right
				if (move == 1):
					#Get the current light state
					partial_state = []
					partial_state = self.determine_state()

					print("Obtained state from sensors: ", partial_state)
					self.state = [self.angel_turn, partial_state[0], partial_state[1]]
					#Roll the quantum dice
					print("Sending total state to quantum: ", self.state)
					quantum = self.quantum_translate(self.state)

					#Depending on the quantum outcome, the bot listens or disobeys
					if (quantum == 0):
						print("Devil successfully tells bot to move right!")
						move_status = self.move_board_bot_right()

						#Return code of '1' means we hit the bomb
						if (move_status == 1):
							torso.stab(stab_angle ,1)
							self.move_hexapod("R")
							self.devil_victory = True
							break
						elif(move_status == 2):
							print("Out of bounds move! Bot staying still")
						else:
							self.move_hexapod("R")
					elif (quantum == 1):
						print("Devil disobeys neutrally and moves up-right!")

						#move_status = self.move_board_bot_up_right()
						move_status = self.move_board_bot_up()

						#Return code of '1' means we hit the bomb
						if (move_status == 1):
							torso.stab(stab_angle,1)
							self.move_hexapod("UP")
							self.devil_victory = True
							break
						elif(move_status == 2):
							print("Out of bounds move! Bot staying still")
						else:
							self.move_hexapod("UP")

						if(move_status != 1 and move_status != 2):
							move_status = self.move_board_bot_right()

							#Return code of '1' means we hit the bomb
							if (move_status == 1):
								torso.stab(stab_angle ,1)
								self.move_hexapod("R")
								self.devil_victory = True
								break
							elif(move_status == 2):
								print("Out of bounds move! Bot staying still")
							else:
								self.move_hexapod("R")

					elif (quantum == 2): #Disobeys
						print("Bot disoboeys the Devil and moves up!")

						move_status = self.move_board_bot_up()

						#Return code of '1' means we hit the bomb
						if (move_status == 1):
							torso.stab(stab_angle ,1)
							self.move_hexapod("UP")
							self.devil_victory = True
							break
						elif(move_status == 2):
							print("Out of bounds move! Bot staying still")

						else:
							self.move_hexapod("UP")
				#Desired move to move up-right
				elif (move == 2):
					#Get the current light state
					partial_state = []
					partial_state = self.determine_state()

					print("Obtained state from sensors: ", partial_state)
					self.state = [self.angel_turn, partial_state[0], partial_state[1]]

					#Roll the quantum dice
					print("Sending total state to quantum: ", self.state)
					quantum = self.quantum_translate(self.state)

					#Depending on the quantum outcome, the bot listens or disobeys (CHANCE TO BE ULTIMATELY INFLUENCED BY LIGHT LEVEL)
					if (quantum == 0):
						print("Devil successfully tells bot to move up-right!")

						#move_status = self.move_board_bot_up_right()
						move_status = self.move_board_bot_up()

						#Return code of '1' means we hit the bomb
						if (move_status == 1):
							torso.stab(stab_angle ,1)
							self.move_hexapod("UP")
							self.devil_victory = True
							break
						elif(move_status == 2):
							print("Out of bounds move! Bot staying still")
						else:
							self.move_hexapod("UP")

						if(move_status != 1 and move_status != 2):
							move_status = self.move_board_bot_right()

							#Return code of '1' means we hit the bomb
							if (move_status == 1):
								torso.stab(stab_angle ,1)
								self.move_hexapod("R")
								self.devil_victory = True
								break
							elif(move_status == 2):
								print("Out of bounds move! Bot staying still")
							else:
								self.move_hexapod("R")
					elif (quantum == 1):
						print("Devil disobeys neutrally and moves right!")
						move_status = self.move_board_bot_right()

						#Return code of '1' means we hit the bomb
						if (move_status == 1):
							torso.stab(stab_angle ,1)
							self.move_hexapod("R")
							self.devil_victory = True
							break
						elif(move_status == 2):
							print("Out of bounds move! Bot staying still")
						else:
							self.move_hexapod("R")
					elif (quantum == 2): #Disobeys
						print("Bot disoboeys the Devil and stays still!")


				self.angel_turn = 1
				self.turn_num +=1
				if (self.rotation_correction == True):
					rotation_check_code = rotation_corrector.process_image()
					print("Rotation code needed: ", str(rotation_check_code))
					if (rotation_check_code < 0):
						hex_walker.rotate(-1*(rotation_check_code), RIGHT)
					elif(rotation_check_code > 0):
						hex_walker.rotate(rotation_check_code, LEFT)


				if (self.forward_back_correction == True):
					forward_back_code = forward_back_corrector.process_image()
					print("Forward/back code needed: ", str(forward_back_code))
					if (forward_back_code < 0):
						hex_walker.walk(1, DIR_B)
					elif(forward_back_code > 0):
						hex_walker.rotate(1, 0)

				#Running out of turns is automatic win for the angel
				if (self.turn_num == self.max_turns):
					print("MAX TURNS REACHED, Angel wins!!")
					self.angel_victory = True
					break



		#If we break the loop and get here, check who won and execute the appropriate "victory" function
		if (self.angel_victory == True):
			self.angel_wins()

		elif (self.devil_victory == True):
			self.devil_wins()


#Main function to execute the game
def main():
	game = Angel_Demon_Game(30, "test")
	game.run_game()

#Call the main function
main()
