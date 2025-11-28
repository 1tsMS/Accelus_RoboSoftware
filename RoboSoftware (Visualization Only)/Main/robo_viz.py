from urdfpy import URDF
import numpy as np
import pyvista as pv
from pyvistaqt import QtInteractor
from PyQt5 import QtWidgets, QtCore
import os

# Patch numpy deprecated alias
if not hasattr(np, "float"):
    np.float = float

class RobotVisualizer(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        # PyVista Qt interactor
        self.plotter = QtInteractor(self)
        self.plotter.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.plotter.setMinimumSize(300, 300)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.plotter.interactor)
        self.setLayout(layout)

        # Load URDF
        urdf_path = "Main/Models/ur5_g.urdf"
        if not os.path.exists(urdf_path):
            print(f"❌ FATAL ERROR: URDF file not found at {urdf_path}")
            print(f"Current directory is: {os.getcwd()}")
            self.robot = None
            return
        
        self.robot = URDF.load(urdf_path)

        # --- UPDATED LOGIC ---
        # This dictionary stores the permanent offsets needed to align the model's
        # zero-pose with the physical robot's home (all-zero) position.
        self.zero_pose_offsets = {
            "shoulder_pan_joint": 0.0,
            "shoulder_lift_joint": -np.pi / 2,
            "elbow_joint": np.pi / 2,
            "wrist_1_joint": -np.pi/2,
            "wrist_2_joint": -np.pi/2,
            "wrist_3_joint": 0.0,
        }

        # This will store the FINAL calculated angles for the FK solver.
        # It's initialized with the offset values for the first draw.
        self.current_joint_angles = self.zero_pose_offsets.copy()

        # Dict to hold the actors for updating the scene
        self.meshes = {}

        self._setup_scene()

    def _setup_scene(self):
        if self.robot is None:
            return
            
        self.plotter.set_background("white")
        # First draw using the initial (offset) angles
        self.update_robot()
        # Axes/grid
        self.plotter.add_axes()
        self.plotter.show_grid()
        self.plotter.reset_camera()

    def update_robot(self):
        """
        Updates robot mesh positions smoothly and correctly using stored base meshes.
        Prevents flicker and cumulative transformations.
        """
        try:
            fk = self.robot.link_fk(cfg=self.current_joint_angles)
        except Exception as e:
            print(f"FK calculation error: {e}")
            return

        for link in self.robot.links:
            if not link.visuals:
                continue

            for idx, visual in enumerate(link.visuals):
                geom = visual.geometry
                if geom.mesh is None:
                    continue

                key = f"{link.name}_{idx}"

                try:
                    T_link = fk[link]
                    T_visual = visual.origin if visual.origin is not None else np.eye(4)
                    T = T_link @ T_visual

                    # --- CASE 1: Already loaded (reuse base mesh) ---
                    if key in self.meshes:
                        actor, base_mesh = self.meshes[key]
                        # Create transformed copy from the original (untransformed) mesh
                        transformed_mesh = base_mesh.copy()
                        transformed_mesh.transform(T, inplace=True)
                        actor.mapper.SetInputData(transformed_mesh)

                    # --- CASE 2: First time load ---
                    else:
                        mesh_file = geom.mesh.filename
                        base_mesh = pv.read(mesh_file)
                        transformed_mesh = base_mesh.copy()
                        transformed_mesh.transform(T, inplace=True)
                        actor = self.plotter.add_mesh(transformed_mesh, color="lightgrey", show_edges=False)

                        # Store original untransformed mesh
                        self.meshes[key] = (actor, base_mesh)

                except Exception as e:
                    print(f"Could not load/update mesh for {link.name}: {e}")

        self.plotter.render()

    
    def set_joint_angles(self, incoming_angles_dict):
        """
        Applies the zero-pose offset to the incoming robot angles 
        and then triggers a refresh of the scene.
        """
        # --- UPDATED LOGIC ---
        # Calculate the final angles by adding the offset to the incoming values.
        for joint_name in self.zero_pose_offsets:
            if joint_name in incoming_angles_dict:
                # Final Angle = Offset Angle + Real Robot Angle
                self.current_joint_angles[joint_name] = (
                    self.zero_pose_offsets[joint_name] - incoming_angles_dict[joint_name]
                )
        
        # Now update the visualization with the correctly offset angles
        self.update_robot()
        self.plotter.render()