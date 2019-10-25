import cirq
import numpy as np
from cirq.ops import CZ, H, CNOT, X, CCX
import re
import random
import matplotlib

def counter_to_dict(counts_in):
    counts_dict = {}
    counts_string = str(counts_in)
    counts_string = re.sub(r'[a-zA-Z]+', '', counts_string, re.I)
    counts_dict = eval(counts_string[1:-1])
    for key in counts_dict:
        value = counts_dict[key]
        string_key = str(key)
        del counts_dict[key]
        counts_dict[string_key] = value
    return counts_dict

def parse_counts(counts_in):
    list_of_numbers = ""
    total_outcomes = 0
    num_list = []
    shuffled_list = []
    select_random = ""
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
    num_list = list(list_of_numbers)
    random.shuffle(num_list)
    position = random.randrange(0,total_outcomes-1,1)
    select_random = num_list[position]
    return select_random

def determine_state(determined_value):
    if determined_value == "a":
        state = 0
    elif determined_value == "b":
        state = 1
    elif determined_value == "c":
        state = 2
    return state

def get_stats(dict_in):
    total_outcomes = 1000
    stat_string = "\nPOSSIBLE OUTCOMES: \n"
    percent_dict = {}
    identifier = ''
    for key in dict_in:
        counts = float(dict_in[key])
        percent = round(((counts/total_outcomes)*100),1)
        percent_dict[key] = percent
        if key == '(1, 1)':
            if '(0, 0)' in percent_dict:
                percent_dict['(0, 0)'] = float(percent_dict['(0, 0)']) + percent
            else:
                percent_dict['(0, 0)'] = percent
                key = ('(0, 0)')
            del percent_dict['(1, 1)']
    for key in percent_dict:
        if key == '(0, 0)':
            identifier = "follow instructions"
        elif key == '(0, 1)':
            identifier = "be neutral"
        elif key == '(1, 0)':
            identifier = "not follow instructions"
        stat_string = stat_string + key + ": " + str(round(percent_dict[key],2)) + "%" + " chance robot will " + identifier + "\n"
    print(stat_string)

def run_circuit(player, light1, light0):

    results_dict = {}

    q0, q1, q2 = [cirq.GridQubit(i, 0) for i in range(3)]
    circuit = cirq.Circuit()
    simulator = cirq.Simulator()

    # if any of the values are one add an X gate at beginning of circuit for that bit
    if player == 1:
        circuit.append(X(q2))
        
    if light1 == 1:
        circuit.append(X(q1))

    if light0 == 1:
        circuit.append(X(q0))  

    # main circuit construction
    circuit.append(H(q0))
    circuit.append(CNOT(q2,q1))
    circuit.append(X(q1))
    circuit.append(H(q2))
    circuit.append(CNOT(q2,q0))
    circuit.append(CCX(q2,q0,q1))
    circuit.append(X(q1))
    circuit.append(cirq.measure(q0,key='x'))
    circuit.append(cirq.measure(q1,key='y'))

    # print out circuit
   # print(circuit)

    # get results from 1000 runs of circuit
    results = simulator.run(circuit, repetitions = 1000)

    # gets counts for each possible output
    counts = results.multi_measurement_histogram(keys = ['y','x'])

    print(counts)

    results_dict = counter_to_dict(counts)

    get_stats(results_dict)

    letter_choice = parse_counts(results_dict)

    choice = determine_state(letter_choice)

    print("Robot Mood = " + str(choice))
    return choice

run_circuit(0,0,1)
