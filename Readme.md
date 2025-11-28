# RoboSoftware

RoboSoftware is a GUI-based control suite for 6-axis industrial robotic arms.  
It provides manual jogging, speed control, servo control, and a built-in Blockly visual programming editor for creating robot programs without writing code.

---

## 🚀 Features

### 🖥️ GUI Interface
- Modern PyQt5 interface  
- Live robot connection and servo status  
- Speed slider (0–100)  
- Joint values and position displays  
- Connect/Disconnect controls  

---

### 🤖 Manual Robot Control
- **Joint Jog:** Move J1–J6 by adjustable degrees  
- **Linear Jog:** Move along X, Y, or Z axes  
- **Servo Control:** Lock / Unlock robot servos  
- **Go Home:** Manual and Library home modes  
- **Safe movement limits** (handled by backend)

---

### 🧱 Blockly Visual Programming
- Integrated Blockly editor inside the app  
- Drag-and-drop block programming  
- Run and Clear workspace options  
- Supported blocks:
  - Connect Robot  
  - Set Servo State  
  - Set Speed  
  - Jog Joint  
  - Jog Linear  
  - Move Home  
  - Delay  
  - If Condition (robot connected / servo locked)

---

## 📁 Project Contents
- PyQt GUI application  
- Embedded HTML + JS Blockly editor  
- Python execution layer for visual programs  
- Robot command API integration (`functions.py`)  

---

## 📌 Project Status
Personal robotics project — actively expanding block support, UI improvements, and overall functionality.
---

This project (Add o
