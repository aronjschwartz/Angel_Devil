#Program: Implements quantum circuit and determines robot "mood"
#Author: Tristan Cunderla
#Last edit: 11/6/2019

import cirq
import numpy as np
from cirq.ops import CZ, H, CNOT, X, CCX
import re
import random
import matplotlib

# empty string to hold the outputs of the simulation that can be passed between different functions
letter_string = ""

# PRINT VARIABLES -> used to print out specfic cricuit values

# if True, circuit counts will be printed
print_counts = False
# if True, counts stats will be printed
print_stats = False
# if True, circuit will be printed
print_circuit = False
# if True, robot mood will be printed out
print_mood = False


# counter_to_dict function -> takes the counter created by circuit simulator and tranfers values to dictionary
def counter_to_dict(counts_in):
    counts_dict = {}
    counts_string = str(counts_in)
    # remove any nonsense characters that are not relevent to the circuit
    counts_string = re.sub(r'[a-zA-Z]+', '', counts_string, re.I)
    counts_dict = eval(counts_string[1:-1])
    # sort counter values into dictionary
    for key in counts_dict:
        value = counts_dict[key]
        string_key = str(key)
        del counts_dict[key]
        counts_dict[string_key] = value
    return counts_dict

# parse_counts function -> gets counts dictionary and selects one of the counts to be the robot mood
def parse_counts(counts_in):
    global letter_string
    list_of_numbers = ""
    total_outcomes = 0
    num_list = []
    shuffled_list = []
    select_random = ""
    # creating string that holds all the possible output values
    # letter values are used because it is easier to concatenate a string
    for key in counts_in:
        multiplier = 0
        add_digits = ""
        if key == '(1, 1)' or key == '(0, 0)':
            multiplier = counts_in[key]
            total_outcomes = total_outcomes + multiplier
            add_digits = multiplier * "a"
            list_of_numbers = list_of_numbers + add_digits
        elif key == '(0, 1)':
            multiplier = counts_in[key]
            total_outcomes = total_outcomes + multiplier
            add_digits = multiplier * "b"
            list_of_numbers = list_of_numbers + add_digits
        elif key == '(1, 0)':
            multiplier = counts_in[key]
            total_outcomes = total_outcomes + multiplier
            add_digits = multiplier * "c"
            list_of_numbers = list_of_numbers + add_digits
    # save output string
    letter_string = list_of_numbers
    # convert string to list
    num_list = list(list_of_numbers)
    # shuffle the list
    random.shuffle(num_list)
    # pick random index from list
    position = random.randrange(0,total_outcomes-1,1)
    # select value from list
    select_random = num_list[position]
    # return mood value
    return select_random

# determine_state -> takes letter value from parse_counts and translates it to a mood state number
def determine_state(determined_value):
    # translate string value to number mood value
    if determined_value == "a":
        state = 0
    elif determined_value == "b":
        state = 1
    elif determined_value == "c":
        state = 2
    return state

# get_stats function -> prints out the chance of getting each robot mood
def get_stats():
    
    global letter_string
    obey_number = 0
    neutral_number = 0
    disobey_number = 0

    # determining how many times each output occurs, character by character
    for element in range(0,len(letter_string)):
        current_element = letter_string[element]
        if current_element == 'a':
            obey_number  = obey_number + 1
        elif current_element == 'b':
            neutral_number = neutral_number + 1
        else:
            disobey_number = disobey_number + 1

    # printing out percentage values
    print("\nMOOD PERCENTAGES")
    if obey_number > 0:
        obey_percentage = round((obey_number/10),2)
        print("Obey Percentage: " + str(obey_percentage) + "%")
    if neutral_number > 0:
        neutral_percentage = round((neutral_number/10),2)
        print("Neutral Percentage: " + str(neutral_percentage) + "%")
    if disobey_number > 0:
        disobey_percentage = round((disobey_number/10),2)
        print("Disobey Percentage: " + str(disobey_percentage) + "%")
        
# runs_circuit function -> creates and simulates the quantum circuit
def run_circuit(player, light1, light0):

    results_dict = {}

    # define qubits for circuit
    q0, q1, q2 = [cirq.GridQubit(i, 0) for i in range(3)]

    # define quantum circuit
    circuit = cirq.Circuit()

    # define quantuum simulator
    simulator = cirq.Simulator()

    # if any of the values are one add an X gate at beginning of circuit for that bit
    if player == 1:
        circuit.append(X(q2))
        
    if light1 == 1:
        circuit.append(X(q1))

    if light0 == 1:
        circuit.append(X(q0))  

    # main circuit construction
    # H ->Hadamard gate
    # CNOT -> Feynman gate
    # X -> Pauli X gate (inverter)
    # CCX -> CCNOT gate
    circuit.append(H(q0))
    circuit.append(CNOT(q2,q1))
    circuit.append(X(q1))
    circuit.append(H(q2))
    circuit.append(CNOT(q2,q0))
    circuit.append(CCX(q2,q0,q1))
    circuit.append(X(q1))
    circuit.append(cirq.measure(q0,key='x'))
    circuit.append(cirq.measure(q1,key='y'))

    # get results from 1000 runs of circuit
    results = simulator.run(circuit, repetitions = 1000)

    # gets counts for each possible output
    counts = results.multi_measurement_histogram(keys = ['y','x'])

    # place count values from circuit simlation into dictionary
    results_dict = counter_to_dict(counts)

    # obtain 1 letter value that corresponds to 1 selected output value out of 1000 possiblities 
    letter_choice = parse_counts(results_dict)

    # translate the letter value into a mood value
    choice = determine_state(letter_choice)

    # print statements that can be set with boolean
    if print_circuit == True:
        print(circuit)
    if print_counts == True:
        print(counts)
    if print_stats == True:
        get_stats()
    if print_mood == True:
        print("Robot Mood = " + str(choice))

    # return the choice of the robot
    return choice

#run_circuit(1,0,1)
