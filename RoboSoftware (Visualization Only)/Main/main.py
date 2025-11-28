import csv
import sys

import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog

from ui_main import Ui_MainWindow

import functions  # Ctypes functions

from robo_viz import RobotVisualizer
from blockly import BlocklyManager

# Global variables
ROBOT_NAME = "MyRobot"
ROBOT_IP = "192.168.3.15"
ROBOT_PORT = "6001"
wspeed = 30  # default speed

# For Action Tab
current_step_index = 0
program_running = False

#ICONS
on_path = "E:/College/projects/RoboSoftware/Icons/on.svg"
off_path = "E:/College/projects/RoboSoftware/Icons/off.svg"
lock_path = "E:/College/projects/RoboSoftware/Icons/Lock.svg"
unlock_path = "E:/College/projects/RoboSoftware/Icons/unlock.svg"
# Class to redirect print statements to QPlainTextEdit
class EmittingStream:
    def __init__(self, text_edit):
        self.text_edit = text_edit  # QPlainTextEdit object

    def write(self, text):
        if text.strip() != "":
            self.text_edit.appendPlainText(text.strip())
            # Scroll to the bottom automatically
            self.text_edit.verticalScrollBar().setValue(
                self.text_edit.verticalScrollBar().maximum()
            )

    def flush(self):
        pass  # Needed for compatibility with sys.stdout

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.last_joints = None
        self.last_cart = None
        self.movement_threshold = 0.5  # Only update if change > 0.1 units

        # Icon paths
        self.on_icon_path = on_path
        self.off_icon_path = off_path
        self.lock_icon_path = lock_path
        self.unlock_icon_path = unlock_path

        
        # Redirect stdout to the terminal QPlainTextEdit
        sys.stdout = EmittingStream(self.ui.terminal)
        sys.stderr = EmittingStream(self.ui.terminal)  # optional: capture errors too

        #============/Button Mappings\============#
        # Save config button
        self.ui.config_btn.clicked.connect(self.save_config) 

        #Connect/Disconnect button
        self.connected = False  # Connection state
        self.ui.on_off.setIcon(QIcon("E:/College/projects/RoboSoftware/Icons/onOff.svg"))  # initial blue
        self.ui.on_off.clicked.connect(self.toggle_connection) # Connect/Disconnect button

        #Lock/Unlock button
        self.ui.lock.setIcon(QIcon(self.lock_icon_path))  # initial red
        self.servo_locked = True # Lock state
        self.ui.lock.setEnabled(False)  # no lock control until connected
        self.ui.lock.clicked.connect(self.toggle_servo_lock) # Connect/Disconnect button

        # Emergency Stop button
        self.ui.stop.clicked.connect(self.on_estop_click)

        # Connect coordinate mode change to label update
        self.ui.coord_mode_combo.currentIndexChanged.connect(self.update_robot_labels)


        # Speed Control
        self.ui.current_speed.setText(str(wspeed))
        self.ui.speed_slider.setValue(wspeed)
        self.ui.speed_slider.setMinimum(0)
        self.ui.speed_slider.setMaximum(100)

            #----Connect slider change
        self.ui.speed_slider.valueChanged.connect(self.slider_changed)

            #----Connect buttons
        self.ui.s_m1.clicked.connect(lambda: self.change_speed(-1))
        self.ui.s_m5.clicked.connect(lambda: self.change_speed(-5))
        self.ui.s_m15.clicked.connect(lambda: self.change_speed(-15))
        self.ui.s_m25.clicked.connect(lambda: self.change_speed(-25))

        self.ui.s_p1.clicked.connect(lambda: self.change_speed(1))
        self.ui.s_p5.clicked.connect(lambda: self.change_speed(5))
        self.ui.s_p15.clicked.connect(lambda: self.change_speed(15))
        self.ui.s_p25.clicked.connect(lambda: self.change_speed(25))

        # Control Buttons
            # --------------------
            # Joint Jog Buttons
            # --------------------
        self.ui.j1_p_btn.clicked.connect(lambda: self.jog_joint(0, +1))
        self.ui.j1_n_btn.clicked.connect(lambda: self.jog_joint(0, -1))

        self.ui.j2_p_btn.clicked.connect(lambda: self.jog_joint(1, +1))
        self.ui.j2_n_btn.clicked.connect(lambda: self.jog_joint(1, -1))

        self.ui.j3_p_btn.clicked.connect(lambda: self.jog_joint(2, +1))
        self.ui.j3_n_btn.clicked.connect(lambda: self.jog_joint(2, -1))

        self.ui.j4_p_btn.clicked.connect(lambda: self.jog_joint(3, +1))
        self.ui.j4_n_btn.clicked.connect(lambda: self.jog_joint(3, -1))

        self.ui.j5_p_btn.clicked.connect(lambda: self.jog_joint(4, +1))
        self.ui.j5_n_btn.clicked.connect(lambda: self.jog_joint(4, -1))

        self.ui.j6_p_btn.clicked.connect(lambda: self.jog_joint(5, +1))
        self.ui.j6_n_btn.clicked.connect(lambda: self.jog_joint(5, -1))

            # --------------------
            # Linear Jog Buttons
            # --------------------
        self.ui.x_pos.clicked.connect(lambda: self.jog_linear(0, +1))
        self.ui.x_neg.clicked.connect(lambda: self.jog_linear(0, -1))

        self.ui.y_pos.clicked.connect(lambda: self.jog_linear(1, +1))
        self.ui.y_neg.clicked.connect(lambda: self.jog_linear(1, -1))

        self.ui.z_pos.clicked.connect(lambda: self.jog_linear(2, +1))
        self.ui.z_neg.clicked.connect(lambda: self.jog_linear(2, -1))


        # Go Home button
        self.ui.home_btn.clicked.connect(lambda: self.go_home(use_library_home=False))


        # Clear Error button
        self.ui.clear_error_btn.clicked.connect(self.on_clear_error_click)

        #======|Actions Tab|======#
            # Button connections
        self.ui.save_btn.clicked.connect(self.save_step)
        self.ui.edit_btn.clicked.connect(self.edit_step)
        self.ui.insert_btn.clicked.connect(self.insert_step)
        self.ui.delete_btn.clicked.connect(self.delete_step)
        self.ui.run_btn.clicked.connect(self.run_program)
        self.ui.loop_btn.clicked.connect(self.start_loop)
        self.ui.saveL_btn.clicked.connect(self.save_program)
        self.ui.load_btn.clicked.connect(self.load_program)
        self.ui.clearT_btn.clicked.connect(self.clear_table)

            # Timer for polling robot state
        self.run_timer = QTimer()
        self.run_timer.timeout.connect(self.check_robot_state)

        # Timer for updating labels
        self.label_timer = QTimer()
        self.label_timer.timeout.connect(self.update_robot_labels)
        self.label_timer.start(300)  # update every 300 ms
        

        #===================/Robot Visualization Tab\===================#
        self.robot_viz = RobotVisualizer(self.ui.robot_viz_frame)

        #===================/Blockly Tab\===================#
        self.blockly_manager = BlocklyManager(self)
        self.blockly_manager.setup()

        print("Application started...")  # Test print

    #============/Functions\============#

    def update_robot_config(self, ip: str, port: str, name: str):
        """Update robot connection parameters and mirror them in the UI."""
        global ROBOT_IP, ROBOT_PORT, ROBOT_NAME
        ROBOT_IP = ip
        ROBOT_PORT = port
        ROBOT_NAME = name

        self.ui.ip_address.setText(str(ip))
        self.ui.port_no.setText(str(port))
        self.ui.robot_name.setText(str(name))

    def get_robot_config(self):
        """Return the current robot connection parameters."""
        return ROBOT_IP, ROBOT_PORT, ROBOT_NAME

    def get_current_speed(self) -> int:
        """Return the current speed scalar used for jogging."""
        return wspeed

    def set_speed_value(self, speed_value: int):
        """Force the speed to a specific value and update widgets."""
        global wspeed
        wspeed = max(0, min(100, int(speed_value)))
        self.ui.current_speed.setText(str(wspeed))
        if self.ui.speed_slider.value() != wspeed:
            self.ui.speed_slider.setValue(wspeed)

    def _apply_servo_state(self, locked: bool) -> bool:
        """Set servo state and update UI feedback."""
        try:
            if locked:
                functions.set_servo_state(0, ROBOT_NAME)
                functions.set_servo_poweroff(ROBOT_NAME)
                self.servo_locked = True
                self.ui.lock.setIcon(QIcon(self.lock_icon_path))
            else:
                functions.set_servo_state(1, ROBOT_NAME)
                functions.set_servo_poweron(ROBOT_NAME)
                self.servo_locked = False
                self.ui.lock.setIcon(QIcon(self.unlock_icon_path))
            return True
        except Exception as e:
            action = "lock" if locked else "unlock"
            print(f"⚠️ Servo {action} failed: {e}")
            return False

    def ensure_robot_ready(self, *, auto_unlock: bool = False, source: str = "operation") -> bool:
        """Verify connection/servo state before motion, optionally auto-unlocking."""
        if not self.connected:
            print(f"❌ Cannot {source}: robot not connected.")
            return False

        if self.servo_locked:
            if auto_unlock:
                print(f"⚠️ {source.capitalize()} requires unlocked servo. Unlocking automatically...")
                if not self._apply_servo_state(False):
                    print(f"❌ Cannot {source}: failed to unlock servo.")
                    return False
                print("✅ Servo unlocked automatically.")
            else:
                print(f"❌ Cannot {source}: servo locked. Unlock the robot first.")
                return False

        return True

    # --- Save Configuration Button ---
    def save_config(self):
        global ROBOT_NAME, ROBOT_IP, ROBOT_PORT

        # Replace only if the user entered something
        name = self.ui.robot_name.text().strip()
        ip   = self.ui.ip_address.text().strip()
        port = self.ui.port_no.text().strip()

        if name: ROBOT_NAME = name
        if ip:   ROBOT_IP   = ip
        if port: ROBOT_PORT = port

        print(f"Configuration Saved:")
        print(f"ROBOT_NAME = {ROBOT_NAME}")
        print(f"ROBOT_IP   = {ROBOT_IP}")
        print(f"ROBOT_PORT = {ROBOT_PORT}")
   
    # --- Connect/Disconnect Button ---
    def toggle_connection(self):
        if not self.connected:
            print("Connecting...")
            status = functions.connect_robot(ROBOT_IP, ROBOT_PORT, ROBOT_NAME)
            if status == 0:
                print("✅ Robot connected")
                self.connected = True
                self.ui.on_off.setIcon(QIcon(self.on_icon_path))   # green
                # assume safe state after connect = locked (power OFF) until user unlocks
                self._apply_servo_state(True)
                self.ui.lock.setEnabled(True)

                # 👉 Start model update timer here
                if not hasattr(self, "model_timer"):
                    self.model_timer = QTimer()
                    self.model_timer.timeout.connect(self.update_robot_viz)
                self.model_timer.start(33) # ~30 FPS
            else:
                print("❌ Connect failed")
                self.connected = False
                self.ui.on_off.setIcon(QIcon(self.off_icon_path))  # red
                self.ui.lock.setEnabled(False)
                self.ui.lock.setIcon(QIcon(self.lock_icon_path))
        else:
            # on disconnect, force lock (power OFF), then disconnect
            if not self._apply_servo_state(True):
                print("⚠️ Power-off during disconnect failed")

            functions.disconnect_robot(ROBOT_NAME)
            print("Robot disconnected")
            self.connected = False
            self.ui.on_off.setIcon(QIcon(self.off_icon_path))      # red
            self.ui.lock.setEnabled(False)
            self.ui.lock.setIcon(QIcon(self.lock_icon_path))

            # 👉 Stop model update timer
            if hasattr(self, "model_timer"):
                self.model_timer.stop()

    # --- Lock/Unlock Button ---
    def toggle_servo_lock(self):
        if not self.connected:
            print("⚠️ Cannot toggle lock: robot not connected.")
            return

        if self.servo_locked:
            if self._apply_servo_state(False):
                print("🔓 Servo UNLOCKED (power ON)")
        else:
            if self._apply_servo_state(True):
                print("🔒 Servo LOCKED (power OFF)")

    # --- Emergency Stop Button ---
    def on_estop_click(self):
        if not self.connected:
            print("Cannot use Emergency Stop: Not connected")
            return

        if not hasattr(self, "stop_engaged"):  # Initialize state if not set
            self.stop_engaged = False

        if not self.stop_engaged:
            # Engage stop: Lock servos
            if self._apply_servo_state(True):
                print("Emergency Stop ENGAGED: Servos Locked")

            self.stop_engaged = True
        else:
            # Release stop: Unlock servos
            if self._apply_servo_state(False):
                print("Emergency Stop RELEASED: Servos Unlocked")

            # Remove border (reset style so global stylesheet applies again)
            self.ui.stop.setStyleSheet("")
            self.stop_engaged = False

    # --- Speed Control ---
    def slider_changed(self, value):
        """Update wspeed when slider is moved"""
        global wspeed
        wspeed = value
        self.ui.current_speed.setText(str(wspeed))

    def change_speed(self, delta):
        """Increment/decrement wspeed from buttons"""
        global wspeed
        wspeed += delta
        # Clamp value between 0 and 100
        if wspeed < 0:
            wspeed = 0
        elif wspeed > 100:
            wspeed = 100
        # Update UI
        self.ui.current_speed.setText(str(wspeed))
        self.ui.speed_slider.setValue(wspeed)

    # --- Control Buttons ---
        # --- generic joint jog ---
    def jog_joint(self, joint_index: int, direction: int):
        """
        Jog a single joint by +/-10 units
        """
        if not self.ensure_robot_ready(source="jog joint"):
            return
        try:
            status = functions.move_joint_relative(
                joint_index=joint_index,
                delta=10.0 * direction,
                vel=wspeed,        # use global speed
                acc=30,
                dec=30,
                robot_name=ROBOT_NAME
            )
            # Update labels after jog
            self.update_robot_labels()
            if status == 0:
                print(f"✅ Joint {joint_index+1} moved {10*direction}")
            else:
                print(f"❌ robot_movej failed with code {status}")
        except Exception as e:
            print(f"Error moving Joint {joint_index}:", e)

    # --- generic linear jog ---
    def jog_linear(self, axis_index: int, direction: int):
        """
        Jog linearly along X/Y/Z axis by +/-50 units
        """
        if not self.ensure_robot_ready(source="linear jog"):
            return
        try:
            functions.linear_jog(
                axis_index=axis_index,
                delta=50.0 * direction,
                vel=wspeed * 5,   # linear jog is usually faster, scale it
                acc=30,
                dec=30,
                robot_name=ROBOT_NAME
            )
            # Update labels after jog
            self.update_robot_labels()
            axis_name = ["X", "Y", "Z"][axis_index]
            print(f"✅ {axis_name} {50*direction} units")
        except Exception as e:
            print(f"Error moving axis {axis_index}:", e)

    # --- Update Robot Position Labels ---
    def update_robot_labels(self):
        if not self.connected:
            return

        try:
            mode = self.ui.coord_mode_combo.currentText()
            mode_map = {
                "Tool": 0,
                "Origin": 1,
                "Base": 2,
            }
            coord_val = mode_map.get(mode, 0)
            functions.set_current_coord(coord_val, ROBOT_NAME)

            joints = functions.get_current_position(ROBOT_NAME, coord=0)
            cart = functions.get_current_position(ROBOT_NAME, coord=coord_val)

            # Check for significant movement
            update_needed = False
            if self.last_joints is None or self.last_cart is None:
                update_needed = True
            else:
                for i in range(6):
                    if abs(joints[i] - self.last_joints[i]) > self.movement_threshold:
                        update_needed = True
                        break
                if not update_needed:
                    for i in range(6):
                        if abs(cart[i] - self.last_cart[i]) > self.movement_threshold:
                            update_needed = True
                            break

            if update_needed:
                self.ui.label_num_J1.setText(f"{joints[0]:.2f}")
                self.ui.label_num_J2.setText(f"{joints[1]:.2f}")
                self.ui.label_num_J3.setText(f"{joints[2]:.2f}")
                self.ui.label_num_J4.setText(f"{joints[3]:.2f}")
                self.ui.label_num_J5.setText(f"{joints[4]:.2f}")
                self.ui.label_num_J6.setText(f"{joints[5]:.2f}")

                self.ui.label_num_x.setText(f"{cart[2]:.2f}")
                self.ui.label_num_y.setText(f"{cart[1]:.2f}")
                self.ui.label_num_z.setText(f"{cart[0]:.2f}")
                self.ui.label_num_rx.setText(f"{cart[3]:.2f}")
                self.ui.label_num_ry.setText(f"{cart[4]:.2f}")
                self.ui.label_num_rz.setText(f"{cart[5]:.2f}")

                self.last_joints = joints
                self.last_cart = cart

        except Exception as e:
            print(f"⚠️ Failed to update robot labels: {e}")
            
    # --- Go Home Button ---        
    def go_home(self, use_library_home=False):
        if not self.ensure_robot_ready(source="go home"):
            return

        try:
            if use_library_home:
                functions.robot_go_home(ROBOT_NAME)
                print("✅ Robot moved to home using library function")
            else:
                pos = [0.0]*7
                functions.robot_movej(pos, vel=60, coord=0, acc=30, dec=30, robot_name=ROBOT_NAME)
                print("✅ Robot moved to home (all-zero joints)")
            
            self.update_robot_labels()
        except Exception as e:
            print(f"❌ Failed to move to home: {e}")

    # --- Clear Error Button ---
    def on_clear_error_click(self):
        if not self.connected:
            print("❌ Robot not connected, cannot clear errors")
            return

        try:
            status = functions.clear_error(ROBOT_NAME)
            if status == 0:
                print("✅ Robot errors cleared successfully")
            else:
                print(f"❌ Failed to clear errors, code: {status}")
        except Exception as e:
            print(f"⚠️ Exception while clearing errors: {e}")

    #=======|Action Tab|=======#
        # --- Save Current Position as New Step ---
    def save_step(self):
        if not self.connected:
            print("❌ Cannot save step: robot not connected.")
            return
        row = self.ui.programTable.rowCount()
        self.ui.programTable.insertRow(row)

        step_no = row + 1
        pos = functions.get_current_position(ROBOT_NAME, coord=0)
        # Ensure pos has 7 elements
        while len(pos) < 7:
            pos.append(0.0)

        self.ui.programTable.setItem(row, 0, QtWidgets.QTableWidgetItem(str(step_no)))
        for i, val in enumerate(pos, start=1):
            self.ui.programTable.setItem(row, i, QtWidgets.QTableWidgetItem(f"{val:.2f}"))
        print(f"Step {step_no} saved.")

        # --- Edit Selected Row ---
    def edit_step(self):
        if not self.connected:
            print("❌ Cannot edit step: robot not connected.")
            return
        else:
            row = self.ui.programTable.currentRow()
            if row < 0:
                print(self, "No Selection", "Please select a row to edit.")
                return
            pos = functions.get_current_position(ROBOT_NAME, coord=0)
            for i, val in enumerate(pos, start=1):
                self.ui.programTable.setItem(row, i, QtWidgets.QTableWidgetItem(f"{val:.2f}"))

        # --- Insert Below Selected Row ---
    def insert_step(self):
        if not self.connected:
            print("❌ Cannot insert step: robot not connected.")
            return
        else:
            row = self.ui.programTable.currentRow()
            if row < 0: row = self.ui.programTable.rowCount() - 1
            self.ui.programTable.insertRow(row + 1)

            pos = functions.get_current_position(ROBOT_NAME, coord=0)
            while len(pos) < 7:
                pos.append(0.0)

            self.ui.programTable.setItem(row + 1, 0, QtWidgets.QTableWidgetItem(str(row + 2)))
            for i, val in enumerate(pos, start=1):
                self.ui.programTable.setItem(row + 1, i, QtWidgets.QTableWidgetItem(f"{val:.2f}"))

            self.renumber_steps()

        # --- Delete Selected Row ---
    def delete_step(self):
        if not self.connected:
            print("❌ Cannot delete step: robot not connected.")
            return
        else:
            row = self.ui.programTable.currentRow()
            if row >= 0:
                self.ui.programTable.removeRow(row)
                self.renumber_steps()

        # --- Renumber Steps ---
    def renumber_steps(self):
        for row in range(self.ui.programTable.rowCount()):
            self.ui.programTable.setItem(row, 0, QtWidgets.QTableWidgetItem(str(row + 1)))

        # --- Run Program ---
    def run_program(self):
        if not self.ensure_robot_ready(auto_unlock=True, source="run program"):
            return
        global current_step_index, program_running
        if self.ui.programTable.rowCount() == 0:
            print(self, "No Program", "No steps available.")
            return

        program_running = True
        current_step_index = 0
        self.execute_step(current_step_index)
        self.run_timer.start(200)  # poll every 200 ms

        # --- Execute Step ---
    def execute_step(self, index):
        if not self.ensure_robot_ready(source="execute step"):
            return
        row = index
        pos = []
        for col in range(1, 7):  # J1..J6 (columns 1-7)
            item = self.ui.programTable.item(row, col)
            if item is None or item.text().strip() == "":
                print(f"❌ Step {row+1}, column {col}: missing or empty value.")
                return
            try:
                val = float(item.text())
            except ValueError:
                print(f"❌ Step {row+1}, column {col}: invalid number '{item.text()}'.")
                return
            pos.append(val)

        # Send command to robot
        while len(pos) < 7:
            pos.append(0.0)
        
        functions.robot_movej(pos, vel=wspeed, coord=0, acc=30, dec=30, robot_name=ROBOT_NAME)
       
        # Loop control
    def start_loop(self):
        if not self.ensure_robot_ready(auto_unlock=True, source="start loop"):
            return
        loop_times = self.ui.loop_count.value()
        if loop_times < 1:
            print("❌ Loop count must be at least 1.")
            return
        if self.ui.programTable.rowCount() == 0:
            print("❌ No steps to loop.")
            return

        self.loop_times = loop_times
        self.loop_counter = 0
        self.start_program_loop()
    def start_program_loop(self):
        global current_step_index, program_running
        program_running = True
        current_step_index = 0
        self.loop_counter += 1
        print(f"🔁 Loop {self.loop_counter} of {self.loop_times}")
        self.execute_step(current_step_index)
        self.run_timer.start(200)

        # --- Poll Robot State ---
    def check_robot_state(self):
        if not self.connected:
            print("❌ Cannot check robot state: robot not connected.")
            return
        else:
            global current_step_index, program_running
            if not program_running:
                self.run_timer.stop()
                return

            state = functions.get_robot_running_state(ROBOT_NAME)  # 0=idle,1=running (assumed)
            if state == 0:  # finished current move
                current_step_index += 1
            if current_step_index < self.ui.programTable.rowCount():
                self.execute_step(current_step_index)
            else:
                # Finished all steps, check for loop
                if hasattr(self, 'loop_times') and self.loop_counter < self.loop_times:
                    self.start_program_loop()
                else:
                    program_running = False
                    self.run_timer.stop()
                    print(self, "Program Done", "All steps executed!")
                    # Reset loop variables
                    self.loop_counter = 0
                    self.loop_times = 0

    def save_program(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Program", "", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                for row in range(self.ui.programTable.rowCount()):
                    row_data = []
                    for col in range(self.ui.programTable.columnCount()):
                        item = self.ui.programTable.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
            print(f"✅ Program saved to {path}")
        except Exception as e:
            print(f"❌ Failed to save program: {e}")
    def load_program(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Program", "", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, "r", newline="") as f:
                reader = csv.reader(f)
                self.ui.programTable.setRowCount(0)
                for row_data in reader:
                    row = self.ui.programTable.rowCount()
                    self.ui.programTable.insertRow(row)
                    for col, value in enumerate(row_data):
                        self.ui.programTable.setItem(row, col, QtWidgets.QTableWidgetItem(value))
            print(f"✅ Program loaded from {path}")
            self.renumber_steps()
        except Exception as e:
            print(f"❌ Failed to load program: {e}")
    def clear_table(self):
        self.ui.programTable.setRowCount(0)
        print("✅ Program table cleared.")

    #===================/Robot Visualization Tab\===================#
    def update_robot_viz(self):
        """
        Called by label_timer every 300 ms.
        Reads current joint positions from robot and updates visualization.
        """
        if not self.connected:
            print("❌ Cannot update viz: robot not connected. Showing default pose.")
            return
        
        else:
            try:
               
                pos = functions.get_current_position(ROBOT_NAME, coord=0)  
                #pos = [j1, j2, j3, j4, j5, j6]

                pos_rad = np.radians(pos)
                # Map to URDF joint names
                angles = {
                    "shoulder_pan_joint": pos_rad[0],
                    "shoulder_lift_joint": pos_rad[1],
                    "elbow_joint": pos_rad[2],
                    "wrist_1_joint": pos_rad[3],
                    "wrist_2_joint": pos_rad[4],
                    "wrist_3_joint": pos_rad[5],
                }

                # Send to visualization
                self.robot_viz.set_joint_angles(angles)

            except Exception as e:
                print(f"update_robot_viz error: {e}")


# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())