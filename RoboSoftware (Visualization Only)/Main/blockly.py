import json
import os

from PyQt5.QtCore import QObject, QEventLoop, QTimer, QUrl, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QFileDialog, QVBoxLayout

import functions


class BlocklyBridge(QObject):
    """Bridge object exposed to the embedded Blockly web view."""

    programRequested = pyqtSignal(str)
    saveRequested = pyqtSignal(str)

    @pyqtSlot(str)
    def runProgram(self, program_json: str):
        self.programRequested.emit(program_json)

    @pyqtSlot(str)
    def saveProgram(self, program_state_json: str):
        self.saveRequested.emit(program_state_json)


class BlocklyManager(QObject):
    """Encapsulates Blockly UI embedding and robot command execution."""

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.blockly_view = None
        self.blockly_channel = None
        self.blockly_bridge = BlocklyBridge()
        self.blockly_bridge.programRequested.connect(self.handle_blockly_program)
        self.blockly_bridge.saveRequested.connect(self.handle_blockly_save)

    def setup(self):
        container = self.app.ui.blocklyContainer
        layout = container.layout()
        if layout is None:
            layout = QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)

        self.blockly_view = QWebEngineView(container)
        layout.addWidget(self.blockly_view)

        self.blockly_channel = QWebChannel(self.blockly_view.page())
        self.blockly_channel.registerObject("blocklyBridge", self.blockly_bridge)
        self.blockly_view.page().setWebChannel(self.blockly_channel)

        blockly_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blockly", "index.html")
        if not os.path.exists(blockly_file):
            print(f"Warning: Blockly UI not found at {blockly_file}")
            return

        self.blockly_view.load(QUrl.fromLocalFile(blockly_file))

    def handle_blockly_program(self, program_json: str):
        try:
            steps = json.loads(program_json)
        except json.JSONDecodeError as exc:
            print(f"Failed to parse Blockly program: {exc}")
            return

        if not steps:
            print("Blockly program is empty.")
            return

        runtime = {"variables": {}}
        self.run_blockly_steps(steps, runtime=runtime)

    def handle_blockly_save(self, program_state_json: str):
        path, _ = QFileDialog.getSaveFileName(
            self.app,
            "Save Blockly Script",
            "",
            "Blockly JSON (*.json);;All Files (*)",
        )

        if not path:
            print("[Blockly] Save canceled.")
            return

        final_path = path if path.lower().endswith(".json") else f"{path}.json"

        try:
            with open(final_path, "w", encoding="utf-8") as handle:
                handle.write(program_state_json)
            print(f"[Blockly] ✅ Script saved to {final_path}")
        except Exception as exc:
            print(f"[Blockly] ❌ Failed to save script: {exc}")

    def run_blockly_steps(self, steps, runtime, context_label="[Blockly]"):
        for index, step in enumerate(steps, start=1):
            default_ip, default_port, default_name = self.app.get_robot_config()
            action = step.get("type")
            prefix = f"{context_label} Step {index}"

            if action == "connect_robot":
                ip = (step.get("ip") or "").strip() or default_ip
                port = (step.get("port") or "").strip() or default_port
                name = (step.get("name") or "").strip() or default_name
                print(f"{prefix}: connect {name} at {ip}:{port}")
                self.apply_blockly_connect(ip, port, name)
            elif action == "disconnect_robot":
                print(f"{prefix}: disconnect robot")
                self.apply_blockly_disconnect()
            elif action == "set_servo_state":
                state = step.get("state", "lock")
                print(f"{prefix}: set servo {state}")
                self.apply_blockly_servo(state)
            elif action == "set_speed":
                value = self.resolve_value(step.get("value"), runtime, expected_type="number")
                if value is None:
                    value = self.app.get_current_speed()
                print(f"{prefix}: set speed to {value}")
                self.apply_blockly_speed(value)
            elif action == "set_variable":
                name = (step.get("name") or "").strip()
                value = self.resolve_value(step.get("value"), runtime)
                self.apply_blockly_set_variable(name, value, runtime, prefix)
            elif action == "print":
                message = self.resolve_value(step.get("message"), runtime)
                self.apply_blockly_print(message, prefix)
            elif action == "jog_joint":
                joint = step.get("joint")
                delta = self.resolve_value(step.get("delta"), runtime, expected_type="number")
                if delta is None:
                    print(f"{prefix}: ⚠️ Joint delta is undefined.")
                    continue
                print(f"{prefix}: jog joint {joint} by {delta}")
                self.apply_blockly_jog_joint(joint, delta)
            elif action == "jog_linear":
                axis = step.get("axis")
                delta = self.resolve_value(step.get("delta"), runtime, expected_type="number")
                if delta is None:
                    print(f"{prefix}: ⚠️ Linear delta is undefined.")
                    continue
                print(f"{prefix}: jog axis {axis} by {delta}")
                self.apply_blockly_jog_linear(axis, delta)
            elif action == "move_joint_absolute":
                joint = step.get("joint")
                angle = self.resolve_value(step.get("angle"), runtime, expected_type="number")
                if angle is None:
                    print(f"{prefix}: ⚠️ Target angle is undefined.")
                    continue
                print(f"{prefix}: move joint {joint} to {angle}")
                self.apply_blockly_move_joint_absolute(joint, angle)
            elif action == "move_linear_absolute":
                mode = step.get("mode", "tool")
                coords = {
                    "x": self.resolve_value(step.get("x"), runtime, expected_type="number"),
                    "y": self.resolve_value(step.get("y"), runtime, expected_type="number"),
                    "z": self.resolve_value(step.get("z"), runtime, expected_type="number"),
                    "rx": self.resolve_value(step.get("rx"), runtime, expected_type="number"),
                    "ry": self.resolve_value(step.get("ry"), runtime, expected_type="number"),
                    "rz": self.resolve_value(step.get("rz"), runtime, expected_type="number"),
                }
                print(f"{prefix}: move linearly in {mode} frame to {coords}")
                self.apply_blockly_move_linear_absolute(mode, coords)
            elif action == "go_home":
                mode = step.get("mode", "manual")
                use_library = mode == "library"
                print(f"{prefix}: move home ({mode})")
                self.apply_blockly_home(use_library)
            elif action == "delay":
                duration = self.resolve_value(step.get("duration"), runtime, expected_type="number")
                if duration is None:
                    print(f"{prefix}: ⚠️ Delay duration is undefined.")
                    continue
                print(f"{prefix}: delay {duration} sec")
                self.apply_blockly_delay(duration)
            elif action == "repeat_loop":
                count = self.resolve_value(step.get("count"), runtime, expected_type="number")
                body = step.get("body") or []
                self.apply_blockly_repeat(count, body, runtime, prefix)
            elif action == "if_condition":
                condition = step.get("condition", {})
                print(f"{prefix}: if condition {condition}")
                self.apply_blockly_if(condition, runtime, context_label=prefix)
            elif action == "if_variable_compare":
                name = (step.get("name") or "").strip()
                operator = step.get("operator", "EQ")
                value_expr = step.get("value")
                true_branch = step.get("true_branch") or []
                false_branch = step.get("false_branch") or []
                print(f"{prefix}: if variable {name or '<unnamed>'} {operator} ...")
                self.apply_blockly_if_variable(
                    name,
                    operator,
                    value_expr,
                    runtime,
                    prefix,
                    true_branch,
                    false_branch,
                )
            elif action == "get_coordinates":
                mode = step.get("mode", "joint")
                store = (step.get("store") or "").strip()
                self.apply_blockly_get_coordinates(mode, store, runtime, prefix)
            else:
                print(f"{prefix}: unsupported action '{action}'")

    def resolve_value(self, expr, runtime, expected_type=None):
        if expr is None:
            return None

        kind = expr.get("kind")
        if kind == "literal":
            value_type = expr.get("valueType")
            value = expr.get("value")
            if value_type == "number":
                try:
                    number = float(value)
                    if expected_type == "int":
                        return int(number)
                    if expected_type == "number" or expected_type is None:
                        return number
                    if expected_type == "string":
                        return str(number)
                    if expected_type == "boolean":
                        return bool(number)
                    return number
                except (TypeError, ValueError):
                    return None
            if value_type == "boolean":
                boolean_value = bool(value)
                if expected_type == "string":
                    return "True" if boolean_value else "False"
                if expected_type == "number":
                    return 1.0 if boolean_value else 0.0
                return boolean_value
            if value_type == "string" or value_type is None:
                string_value = "" if value is None else str(value)
                if expected_type == "number":
                    try:
                        return float(string_value)
                    except ValueError:
                        return None
                if expected_type == "boolean":
                    return string_value.lower() in {"true", "1", "yes"}
                return string_value
            return value

        if kind == "variable":
            name = (expr.get("name") or "").strip()
            if not name:
                print("⚠️ Variable reference missing name.")
                return None
            value = runtime["variables"].get(name)
            if value is None:
                print(f"⚠️ Variable '{name}' is undefined.")
                return None
            if expected_type == "number":
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return None
            if expected_type == "int":
                try:
                    return int(float(value))
                except (TypeError, ValueError):
                    return None
            if expected_type == "string":
                return str(value)
            if expected_type == "boolean":
                return bool(value)
            return value

        print(f"⚠️ Unsupported value expression {expr}")
        return None

    def apply_blockly_connect(self, ip: str, port: str, name: str):
        self.app.update_robot_config(ip, port, name)

        if self.app.connected:
            print("Robot is already connected; skipping new connect request.")
            return

        self.app.toggle_connection()

    def apply_blockly_servo(self, state: str):
        if not self.app.connected:
            print("❌ Cannot change servo state: robot not connected.")
            return

        desired_lock = state != "unlock"
        if self.app._apply_servo_state(desired_lock):
            label = "LOCKED" if desired_lock else "UNLOCKED"
            emoji = "🔒" if desired_lock else "🔓"
            print(f"{emoji} Servo {label}")

    def apply_blockly_disconnect(self):
        if not self.app.connected:
            print("Robot already disconnected.")
            return
        self.app.toggle_connection()

    def apply_blockly_move_joint_absolute(self, joint, angle):
        if not self.app.ensure_robot_ready(auto_unlock=True, source="blockly joint move"):
            return

        try:
            joint_index = int(joint)
        except (TypeError, ValueError):
            print(f"⚠️ Invalid joint index '{joint}'")
            return

        if not 0 <= joint_index <= 5:
            print(f"⚠️ Joint index {joint_index} out of range (0-5)")
            return

        try:
            target_angle = float(angle)
        except (TypeError, ValueError):
            print(f"⚠️ Invalid joint angle '{angle}'")
            return

        _, _, robot_name = self.app.get_robot_config()

        try:
            joints = functions.get_current_position(robot_name, coord=0)
            joints[joint_index] = target_angle
            status = functions.robot_movej(
                joints,
                vel=self.app.get_current_speed(),
                coord=0,
                acc=30,
                dec=30,
                robot_name=robot_name,
            )
            if status == 0:
                self.app.update_robot_labels()
                print(f"✅ Joint {joint_index + 1} moved to {target_angle}")
            else:
                print(f"❌ robot_movej returned code {status}")
        except Exception as exc:
            print(f"❌ Absolute joint move failed: {exc}")

    def apply_blockly_move_linear_absolute(self, mode: str, coords: dict):
        if not self.app.ensure_robot_ready(auto_unlock=True, source="blockly linear move"):
            return

        mode_key = (mode or "tool").lower()
        coord_map = {"tool": 0, "origin": 1, "base": 2}
        coord_val = coord_map.get(mode_key)
        if coord_val is None:
            print(f"⚠️ Unsupported coordinate mode '{mode}'")
            return

        _, _, robot_name = self.app.get_robot_config()

        try:
            functions.set_current_coord(coord_val, robot_name)
        except Exception as exc:
            print(f"⚠️ Failed to set coordinate mode '{mode}': {exc}")

        try:
            current = functions.get_current_position(robot_name, coord=coord_val)
        except Exception as exc:
            print(f"❌ Failed to read current position: {exc}")
            return

        axis_map = {
            "x": 2,
            "y": 1,
            "z": 0,
            "rx": 3,
            "ry": 4,
            "rz": 5,
        }

        for key, idx in axis_map.items():
            value = coords.get(key)
            if value is None:
                continue
            try:
                current[idx] = float(value)
            except (TypeError, ValueError):
                print(f"⚠️ Invalid value for {key.upper()}: '{value}'")
                return

        # Ensure we have 7 elements for API expectations
        while len(current) < 7:
            current.append(0.0)

        speed = max(1, int(self.app.get_current_speed()))

        try:
            status = functions.robot_movel(
                current,
                vel=speed * 5,
                coord=1,
                acc=30,
                dec=30,
                robot_name=robot_name,
            )
            if status == 0:
                self.app.update_robot_labels()
                print("✅ Linear absolute move executed")
            else:
                print(f"❌ robot_movel returned code {status}")
        except Exception as exc:
            print(f"❌ Linear absolute move failed: {exc}")

    def apply_blockly_speed(self, speed_value):
        if speed_value is None:
            print("⚠️ Speed value is undefined; skipping.")
            return

        try:
            speed_int = int(float(speed_value))
        except (TypeError, ValueError):
            print(f"⚠️ Invalid speed value '{speed_value}', skipping.")
            return

        clamped = max(0, min(100, speed_int))
        self.app.set_speed_value(clamped)
        print(f"Speed set to {clamped}")

    def apply_blockly_jog_joint(self, joint, delta):
        if not self.app.connected:
            print("❌ Cannot jog joint: robot not connected.")
            return

        if delta is None:
            print("⚠️ Joint jog delta is undefined.")
            return

        try:
            joint_index = int(joint)
            delta_val = float(delta)
        except (TypeError, ValueError):
            print(f"⚠️ Invalid joint jog parameters joint={joint}, delta={delta}")
            return

        if not 0 <= joint_index <= 5:
            print(f"⚠️ Joint index {joint_index} is out of range (0-5).")
            return

        if delta_val == 0:
            print("⚠️ Jog delta is zero; skipping joint move.")
            return

        _, _, robot_name = self.app.get_robot_config()
        speed = self.app.get_current_speed()

        try:
            functions.move_joint_relative(
                joint_index=joint_index,
                delta=delta_val,
                vel=speed,
                acc=30,
                dec=30,
                robot_name=robot_name,
            )
            self.app.update_robot_labels()
            print(f"✅ Joint {joint_index + 1} moved by {delta_val}")
        except Exception as exc:
            print(f"❌ Joint jog failed: {exc}")

    def apply_blockly_jog_linear(self, axis, delta):
        if not self.app.connected:
            print("❌ Cannot jog axis: robot not connected.")
            return

        if delta is None:
            print("⚠️ Linear jog delta is undefined.")
            return

        axis_map = {"0": 0, "1": 1, "2": 2, "x": 0, "y": 1, "z": 2}
        axis_index = axis_map.get(str(axis).lower())
        if axis_index is None:
            print(f"⚠️ Invalid axis '{axis}'")
            return

        try:
            delta_val = float(delta)
        except (TypeError, ValueError):
            print(f"⚠️ Invalid linear jog delta '{delta}'")
            return

        if delta_val == 0:
            print("⚠️ Jog delta is zero; skipping linear move.")
            return

        _, _, robot_name = self.app.get_robot_config()
        speed = self.app.get_current_speed()

        try:
            functions.linear_jog(
                axis_index=axis_index,
                delta=delta_val,
                vel=speed * 5,
                acc=30,
                dec=30,
                robot_name=robot_name,
            )
            self.app.update_robot_labels()
            axis_name = "XYZ"[axis_index]
            print(f"✅ Axis {axis_name} moved by {delta_val}")
        except Exception as exc:
            print(f"❌ Linear jog failed: {exc}")

    def apply_blockly_home(self, use_library_home: bool):
        if not self.app.connected:
            print("❌ Cannot move home: robot not connected.")
            return

        self.app.go_home(use_library_home=use_library_home)

    def apply_blockly_delay(self, duration):
        if duration is None:
            print("⚠️ Delay duration is undefined.")
            return

        try:
            seconds = max(0.0, float(duration))
        except (TypeError, ValueError):
            print(f"⚠️ Invalid delay duration '{duration}'")
            return

        print(f"⏳ Waiting for {seconds} seconds...")
        loop = QEventLoop()
        QTimer.singleShot(int(seconds * 1000), loop.quit)
        loop.exec_()

    def apply_blockly_if(self, condition, runtime, context_label="[Blockly]"):
        condition_type = condition.get("type")

        if condition_type == "is_connected":
            expected = bool(condition.get("value", True))
            result = (self.app.connected is True) == expected
        elif condition_type == "servo_locked":
            expected = bool(condition.get("value", True))
            result = (self.app.servo_locked is True) == expected
        else:
            print(f"⚠️ Unsupported condition type '{condition_type}'.")
            return

        branch = condition.get("true_branch") if result else condition.get("false_branch")
        if branch is None:
            branch = []

        if not branch:
            print("ℹ️ Condition branch is empty.")
            return

        branch_label = f"{context_label} {'TRUE' if result else 'FALSE'}"
        print(f"➡️ {branch_label}: executing {len(branch)} step(s)")
        self.run_blockly_steps(branch, runtime, context_label=branch_label)

    def apply_blockly_set_variable(self, name, value, runtime, context_label):
        if not name:
            print(f"{context_label}: ⚠️ Variable name is empty; skipping assignment.")
            return

        runtime["variables"][name] = value
        print(f"{context_label}: 📝 {name} = {value}")

    def apply_blockly_print(self, message, context_label):
        if message is None:
            message = ""
        print(f"{context_label}: 🗒️ {message}")

    def apply_blockly_repeat(self, count, body, runtime, context_label):
        if count is None:
            print(f"{context_label}: ⚠️ Loop count is undefined; skipping.")
            return

        try:
            iterations = max(0, int(float(count)))
        except (TypeError, ValueError):
            print(f"{context_label}: ⚠️ Invalid loop count '{count}'.")
            return

        if iterations <= 0:
            print(f"{context_label}: ℹ️ Loop count is {iterations}; nothing to execute.")
            return

        if not body:
            print(f"{context_label}: ℹ️ Loop body is empty.")
            return

        for loop_index in range(iterations):
            loop_label = f"{context_label} ▶ iteration {loop_index + 1}/{iterations}"
            print(f"🔁 {loop_label}")
            self.run_blockly_steps(body, runtime, context_label=loop_label)

    def apply_blockly_if_variable(self, name, operator, value_expr, runtime, context_label, true_branch, false_branch):
        if not name:
            print(f"{context_label}: ⚠️ Variable name is empty in compare block.")
            return

        true_branch = true_branch or []
        false_branch = false_branch or []

        variable_defined = name in runtime["variables"]
        current_value = runtime["variables"].get(name)
        expected_value = self.resolve_value(value_expr, runtime)

        if not variable_defined:
            print(f"{context_label}: ⚠️ Variable '{name}' is undefined.")

        if expected_value is None and operator not in {"NEQ"}:
            print(f"{context_label}: ⚠️ Comparison value is undefined.")
            return

        result = self.compare_values(current_value, expected_value, operator)
        branch = true_branch if result else false_branch

        symbol_map = {"EQ": "=", "NEQ": "≠", "LT": "<", "LTE": "≤", "GT": ">", "GTE": "≥"}
        branch_label = f"{context_label} {'TRUE' if result else 'FALSE'}"
        print(
            f"{context_label}: compare {current_value} {symbol_map.get(operator, operator)} {expected_value} -> {result}"
        )
        if not branch:
            print(f"{branch_label}: ℹ️ Branch is empty.")
            return

        print(f"➡️ {branch_label}: executing {len(branch)} step(s)")
        self.run_blockly_steps(branch, runtime, context_label=branch_label)

    def apply_blockly_get_coordinates(self, mode, store, runtime, context_label):
        if not self.app.connected:
            print(f"{context_label}: ❌ Cannot read coordinates; robot not connected.")
            return

        mode_lower = (mode or "joint").lower()
        _, _, robot_name = self.app.get_robot_config()

        try:
            if mode_lower == "joint":
                coords = functions.get_current_position(robot_name, coord=0)
            else:
                coord_map = {"tool": 0, "origin": 1, "base": 2}
                coord_val = coord_map.get(mode_lower, 0)
                functions.set_current_coord(coord_val, robot_name)
                coords = functions.get_current_position(robot_name, coord=coord_val)
        except Exception as exc:
            print(f"{context_label}: ⚠️ Failed to read coordinates: {exc}")
            return

        coords_list = list(coords)
        if store:
            runtime["variables"][store] = coords_list
            print(f"{context_label}: 📥 stored {mode_lower} coordinates in '{store}' => {coords_list}")
        else:
            print(f"{context_label}: 📍 {mode_lower} coordinates => {coords_list}")

    @staticmethod
    def compare_values(left, right, operator):
        def try_float(value):
            try:
                return True, float(value)
            except (TypeError, ValueError):
                return False, None

        numeric_left, left_num = try_float(left)
        numeric_right, right_num = try_float(right)

        if numeric_left and numeric_right:
            a, b = left_num, right_num
        else:
            a = "" if left is None else str(left)
            b = "" if right is None else str(right)

        if operator == "EQ":
            return a == b
        if operator == "NEQ":
            return a != b
        if operator == "LT":
            return a < b
        if operator == "LTE":
            return a <= b
        if operator == "GT":
            return a > b
        if operator == "GTE":
            return a >= b
        print(f"⚠️ Unsupported operator '{operator}'")
        return False
