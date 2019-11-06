# ECE578 - Inteligent Robotics 1 Repo   
## Authors    
* [Aron Schwartz](https://github.com/aronjschwartz)  
* [Meshal Albaiz](https://github.com/mish3albaiz)  
* [Tristan Cunderla](https://github.com/tristancunderla)    
* [Brian Henson](https://github.com/Nuthouse01)  
## Angel/Demon Game   
Repository Location: [/ECE_578_Fall_2019/Angel_Demon_Game/](https://github.com/aronjschwartz/ECE_578_Fall_2019/tree/master/Angel_Demon_Game)  
### Description  
In this game, the demon wants to detonate a bomb and the angel is trying to prevent that. The robot reads the light with a webcam and sends the light levels to the quantum circuit along with the angel/demon turn. The quantum circuit returns probabilities of the what action the robot will take, it either follows the command of the player or disobeys. Based on player control, the angel can move up or make no move, the demon can move up to the right or move right. The angel wins if it moves above the bomb on the y-axis or beyond it on the x-axis, it performs a dance when it wins. The demon wins when it goes to the bomb, it pops a balloon with a pin attached to its arm. Each player is allowed 5 moves, when both players run out of moves the angel wins the game. The number of moves allowed is configurable.
### Files  
* angel_demon.py: Top level game code/logic   
* quantum_circuit.py:  Simulates quantum circuit and produces robot "mood"  
* sensor_input.py: Uses webcam to determine brightness in front of the robot 
### Playing the Game  
#### Prerequisites  
*Python Libraries:*  
* OpenCV
* Cirq  
* Numpy  
* Time  
* Regular Expression  
* Random  
* MatPlotLib  
* PIL  
* Threading  

*Hardware:*  
* Raspberry Pi  
* USB Webcam  
* ECE578 Feynman Bot*  

*Note: Feynman bot is not needed for playing the game but if you would like to expierience the full effect of the game using the bot is recommended.  
#### Playing the Game
1. Download repo to Pi 
2. VNC into Raspberry Pi
3. Using the terminal on the Pi, navigate to the directory where the angel_demon.py file is located and type the following text into the command line.  
```
python angel_demon.py
```
## Driver Updates: Interpolation & Threading  
Repository Location: [/ECE_578_Fall_2019/project_files/robot_drivers/](https://github.com/aronjschwartz/ECE_578_Fall_2019/tree/master/project_files/robot_drivers) 
### Description  
### Files  
* hex_util.py   
* hex_walker_constants.py   
* hex_walker_driver_v2.py  
* leg_thread.py  
* pwm_wrapper.py  

*Note: other files within this path were not changed from previous years projects  
### Videos  
[Before Driver Updates](https://youtu.be/p2TAcD7aNjc)  
[After Driver Updates](https://youtu.be/fD-FDFSJfj8)    

