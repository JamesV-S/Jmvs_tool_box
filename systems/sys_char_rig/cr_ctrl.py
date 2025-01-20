
import maya.cmds as cmds
import importlib
import sys
import os

from systems import (
    os_custom_directory_utils,
    utils
)
importlib.reload(os_custom_directory_utils)
importlib.reload(utils)

class CreateControl():
    def __init__(self, type, name):
        self.import_directory = os_custom_directory_utils.create_directory(
            "Jmvs_tool_box", "imports" 
            )
        self.ctrl = self.circle_type(type, name)

    def circle_type(self, ctrl_type, ctrl_name):
        # create curve
        if ctrl_type == "circle":
            guide_import_dir = os.path.join(self.import_directory, 
                                            "imp_circle.abc")
            imported_guide = cmds.file(guide_import_dir, i=1, 
                                       ns="imp_circle", rnn=1)
            ctrl = cmds.rename(imported_guide[0], ctrl_name)
        # create cube
        elif ctrl_type == "cube":
            guide_import_dir = os.path.join(self.import_directory, 
                                            "imp_cube.abc")
            imported_guide = cmds.file(guide_import_dir, i=1, 
                                       ns="imp_cube", rnn=1)
            ctrl = cmds.rename(imported_guide[0], ctrl_name)
        # create pv
        elif ctrl_type == "pv":
            guide_import_dir = os.path.join(self.import_directory, 
                                            "imp_star.abc")
            imported_guide = cmds.file(guide_import_dir, i=1, 
                                       ns="imp_star", rnn=1)
            ctrl = cmds.rename(imported_guide[0], ctrl_name)
        # create roundedSquare
        elif ctrl_type == "roundedSquare":
            guide_import_dir = os.path.join(self.import_directory, 
                                            "imp_roundedSquare.abc")
            imported_guide = cmds.file(guide_import_dir, i=1, 
                                       ns="imp_roundedSquare", rnn=1)
            ctrl = cmds.rename(imported_guide[0], ctrl_name)
        # create square
        elif ctrl_type == "square":
            guide_import_dir = os.path.join(self.import_directory, 
                                            "imp_square.abc")
            imported_guide = cmds.file(guide_import_dir, i=1, 
                                       ns="imp_square", rnn=1)
            ctrl = cmds.rename(imported_guide[0], ctrl_name)
        # create orb
        elif ctrl_type == "orb":
            guide_import_dir = os.path.join(self.import_directory, 
                                            "imp_orb.abc")
            imported_guide = cmds.file(guide_import_dir, i=1, 
                                       ns="imp_orb", rnn=1)
            ctrl = cmds.rename(imported_guide[0], ctrl_name)
        # create octogan
        elif ctrl_type == "octogan":
            guide_import_dir = os.path.join(self.import_directory, 
                                            "imp_octogan.abc")
            imported_guide = cmds.file(guide_import_dir, i=1, 
                                       ns="imp_octogan", rnn=1)
            ctrl = cmds.rename(imported_guide[0], ctrl_name)  
        # create square
        elif ctrl_type == "cog":
            guide_import_dir = os.path.join(self.import_directory, 
                                            "imp_cog_002.abc")
            imported_guide = cmds.file(guide_import_dir, i=1, 
                                       ns="imp_cog_002", rnn=1)
            ctrl = cmds.rename(imported_guide[0], ctrl_name)          
        else:
            # create locator
            ctrl = cmds.spaceLocator(n=ctrl_name)

        return ctrl

    
                #cmds.spaceLocator(n={ctrl_name})
                #cmds.xform(guide_name, translation=pos, worldSpace=1)
        # establish the things I need 
        # Arg: I would like a dictionary with:
            # module, uniqueID, side & part of the mdl/component it's matching to.
        # guide name = "xfm_guide_uniqueID*_mdl*_part*_side*"

        # do I want this function to work on a single dict for mdl/component at a time 
        # or pass a dictionary that contains all.
        # if its a single component then i just need to call it through a loop 
        # allowing for "add_module button". ANS = single dict component at a time 

        # I want the selection of the tree view to dictate the compnents to add.
        # if a component already exists then pass and move on, don't error!

    def retrun_ctrl(self):
        return self.ctrl