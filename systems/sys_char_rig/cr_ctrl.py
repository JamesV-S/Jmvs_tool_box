
import maya.cmds as cmds
import importlib
import sys
import os

from utils import (
    utils,
    utils_os
)

importlib.reload(utils_os)
importlib.reload(utils)

class CreateControl():
    def __init__(self, type, name):
        self.import_directory = utils_os.create_directory(
            "Jmvs_tool_box", "imports" 
            )
        self.ctrl = self.circle_type(type, name)

    def circle_type(self, ctrl_type, ctrl_name):
        if ctrl_type == "circle":
            ctrl = self.import_control("imp_circle", ctrl_name)
        elif ctrl_type == "cube":
            ctrl = self.import_control("imp_cube", ctrl_name)
        elif ctrl_type == "pv":
            ctrl = self.import_control("imp_star", ctrl_name)
        elif ctrl_type == "bvSquare":
            ctrl = self.import_control("imp_beveledSquare", ctrl_name)
        elif ctrl_type == "bvRectangle":
            ctrl = self.import_control("imp_beveledRectangle", ctrl_name)
        elif ctrl_type == "square":
            ctrl = self.import_control("imp_square", ctrl_name)
        elif ctrl_type == "orb":
            ctrl = self.import_control("imp_orb", ctrl_name)
        elif ctrl_type == "octogan":
            ctrl = self.import_control("imp_octogan", ctrl_name)
        elif ctrl_type == "cog":
            ctrl = self.import_control("imp_cog_002", ctrl_name)
        elif ctrl_type == "root":
            ctrl = self.import_control("imp_root_octagon_02", ctrl_name)
        elif ctrl_type == "arrow":
            ctrl = self.import_control("imp_arrow", ctrl_name)
        elif ctrl_type == "imp_cg_arm_L":
            ctrl = self.import_control("imp_cg_arm_L", ctrl_name)
        elif ctrl_type == "imp_cg_arm_R":
            ctrl = self.import_control("imp_cg_arm_R", ctrl_name)
        elif ctrl_type == "imp_cg_leg_L":
            ctrl = self.import_control("imp_cg_leg_L", ctrl_name)
        elif ctrl_type == "imp_cg_leg_R":
            ctrl = self.import_control("imp_cg_leg_R", ctrl_name)
        elif ctrl_type == "imp_cg_spine":
            ctrl = self.import_control("imp_cg_spine", ctrl_name)
        elif ctrl_type == "imp_cg_root":
            ctrl = self.import_control("imp_cg_root", ctrl_name)
        elif ctrl_type == "prism":
            ctrl = self.import_control("imp_prism", ctrl_name)
        elif ctrl_type == "bridge":
            ctrl = self.import_control("imp_bridge", ctrl_name)
        elif ctrl_type == "None":
            ctrl = self.import_control("imp_prism", ctrl_name)
        else:
            ctrl = cmds.spaceLocator(n=ctrl_name)

        return ctrl

    
    def import_control(self, import_name, ctrl_name):
        import_dir = os.path.join(self.import_directory, 
                                        f"{import_name}.abc")
        imported_guide = cmds.file(import_dir, i=1, 
                                    ns=import_name, rnn=1)
        ctrl = cmds.rename(imported_guide[0], ctrl_name)
        return ctrl


    def retrun_ctrl(self):
        return self.ctrl