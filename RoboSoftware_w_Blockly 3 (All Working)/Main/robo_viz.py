import uaibot as ub
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from functions import get_current_position

class RobotVizWidget(QWidget):
    def __init__(self, robot_name: str, coord: int = 0, parent=None):
        super().__init__(parent)
        self.robot_name = robot_name
        self.coord = coord

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # UAIbot Simulation widget
        self.sim = ub.Simulation()
        self.layout.addWidget(self.sim)

        self.robot = ub.Robot.create_epson_t6(color="gray")
        self.sim.add(self.robot)

        # Timer to update robot position
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_robot_position)
        self.timer.start(100)  # Update every 100 ms

    def update_robot_position(self):
        joint_angles = get_current_position(self.robot_name, self.coord)
        if joint_angles:
            self.robot.set_joint_angles(joint_angles)
            self.sim.render()
