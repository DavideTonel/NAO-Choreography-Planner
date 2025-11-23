# NAO Challenge – Planning Project

## Team Members
- **Davide Tonelli** – davide.tonelli8@studio.unibo.it

---

## Project Overview
This project implements an automatic choreography generator and executor  
for the NAO humanoid robot. A full choreography is generated using an  
**A\*** search planner capable of inserting intermediate moves between  
mandatory positions while:

- respecting postural constraints (standing / sitting),
- keeping the time for each step within the allowed budget,
- encouraging movement variety through a repetition penalty.

### **Workflow Summary**
1. **main.py**
   - defines mandatory poses and tunable parameters,
   - sets available intermediate moves,
   - splits the global time into planning segments.

2. For each pair of mandatory poses:
   - an A\* subproblem is created (`NaoProblem`),
   - the planner fills the time slot with valid intermediate moves,
   - repetition penalties guide the search toward diverse solutions.

3. The final choreography is:
   - printed and validated,
   - executed on the robot via Python2 movement scripts,
   - synchronized with background music (via VLC).

---

## 📁 Folder Structure
```
NAO-Choreography-Planner/
│
├── main.py
├── utils.py
├── nao_problem.py
│
├── info/
│ └── statistics.py
│
├── NaoMoves/ # Python2 movement scripts
│ ├── <MoveName>.py
│ └── ...
│
├── aima/ # AIMA search library (if included)
│ └── ...
│
├── Wii_Sports.mp3 # Background music
└── README.md # This file
```

---


---

## 📦 Requirements

### **External Software**
- **VLC Media Player**  
  Required for background music playback using the `python-vlc` module.

---

### **Python 3**

Install the required libraries with:

```bash
pip install python-vlc
```

### **Python 2.7**

Required to run movement scripts inside `NaoMoves/`:

- **NAOqi Python2 SDK** (included with Choregraphe)

Movement scripts accept the following format:

```bash
python2 <MoveName>.py <robot_ip> <port>
```

### **NAO Robot Requirements**

The choreography can be executed on:

- A **virtual NAO** inside Choregraphe (recommended for testing), or  
- A **real NAO robot** on the same network.

Default configuration:

- **IP:** `127.0.0.1`  
- **Port:** `9559` (or the port provided by Choregraphe)

---

## ▶️ How to Run (Virtual NAO)

1. Open **Choregraphe** and start the virtual NAO.  
2. Verify the robot’s IP (typically `127.0.0.1`) and port (`9559`).  
3. Navigate to the project folder and run:

```bash
python3 main.py [IP] [PORT]
```
