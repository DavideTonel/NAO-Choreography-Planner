NAO Challenge – Planning Project
================================

Team Members
------------
- Davide Tonelli – davide.tonelli8@studio.unibo.it


Project Overview
----------------
This project implements an automatic choreography generator and executor 
for the NAO robot. The choreography is produced using an A* search 
planner that inserts intermediate movements between mandatory poses while:

- respecting postural constraints (standing / sitting),
- not exceeding a time budget per step,
- encouraging variety using a repetition penalty in the cost function.

The workflow:

1. The main script (`main.py`) defines:
   - the mandatory poses,
   - tunable hyperparameters,
   - the available intermediate moves,
   - the total time slot.

2. For each pair of consecutive mandatory poses:
   - a dedicated A* subproblem is created using `NaoProblem`,
   - the planner fills the time slot with intermediate moves,
   - moves are penalized if repeated too many times.

3. The full choreography is printed, validated, and then executed:
   - background music is played through VLC,
   - each move is executed via a Python2 script inside `./NaoMoves/`,
   - Choregraphe (or a real NAO robot) must be running.


Folder Structure
----------------
Recommended structure of the submitted folder:

NAO-Choreography-Planner/
│
├── main.py
├── utils.py
├── nao_problem.py
│
├── info/
│   └── statistics.py
│
├── NaoMoves/                        (Python2 movement scripts)
│   ├── <MoveName>.py
│   └── ...
│
├── aima/                            (folder containing aima's library files)
│   └── ...
│
├── Wii_Sports.mp3                   (background music file)
└── readme.txt                       (this file)


Requirements
-----------------------------------
### External Softwares
- VLC Media Player  
  VLC must be installed.

### Python 3
- python-vlc  
  Required to play music during dance execution.  

### Python 2.7
- **NAOqi Python2 SDK**, included with Choregraphe

### NAO Robot Requirements
The system must run with either:
- a **virtual NAO** in Choregraphe, or  
- a **real NAO robot** connected to the same network.

Default connection:
- IP: `127.0.0.1` (virtual robot)
- Port: `9559` or another port displayed by Choregraphe


How to Run (Virtual NAO)
------------------------
1. Open Choregraphe and start the virtual robot.
2. Note the robot IP (typically: `127.0.0.1`) and port (e.g., `9559`).
3. From a terminal with Python3 go inside the NAO-Choreography-Planner directory and run:

      python3 main.py [IP] [PORT]
