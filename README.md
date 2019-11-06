# ECE578 - Inteligent Robotics 1 Repo   
## Authors    
* [Aron Schwartz](https://github.com/aronjschwartz)  
* [Meshal Albaiz](https://github.com/mish3albaiz)  
* [Tristan Cunderla](https://github.com/tristancunderla)    
* [Brian Henson](https://github.com/Nuthouse01)  
## Angel/Demon Game   
Located in /ECE_578_Fall_2019/Angel_Demon_Game/  
### Description  
In this game, the demon wants to detonate a bomb and the angel is trying to prevent that. The robot reads the light with a webcam and sends the light levels to the quantum circuit along with the angel/demon turn. The quantum circuit returns probabilities of the what action the robot will take, it either follows the command of the player or disobeys. Based on player control, the angel can move up or make no move, the demon can move up to the right or move right. The angel wins if it moves above the bomb on the y-axis or beyond it on the x-axis, it performs a dance when it wins. The demon wins when it goes to the bomb, it pops a balloon with a pin attached to its arm. Each player is allowed 5 moves, when both players run out of moves the angel wins the game. The number of moves allowed is configurable.
### Files  
* angel_demon.py: Top level game code/logic   
* quantum_circuit.py:  Simulates quantum circuit and produces robot "mood"  
* sensor_input.py: Uses webcam to determine brightness in front of the robot  
## Driver Updates: Interpolation & Threading  
Located in /ECE_578_Fall_2019/project_files/robot_drivers/ 
### Description  
### Files  
* hex_util.py   
* hex_walker_constants.py   
* hex_walker_driver_v2.py  
* leg_thread.py  
* pwm_wrapper.py  

(Note: other files within this path were not changed from previous years projects)  
### Videos  
[Before Driver Updates](https://youtu.be/p2TAcD7aNjc)  
[After Driver Updates](https://youtu.be/fD-FDFSJfj8)    

