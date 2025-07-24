
import importlib
import maya.cmds as cmds
from utils import (
    utils
)
from systems.sys_char_rig import (
    cr_ctrl
)
importlib.reload(utils)
importlib.reload(cr_ctrl)


class ArmSystem():
    def __init__(self, module_name, external_output_dict, skeleton_dict, fk_dict, ik_dict):
        pass
        '''
        neccesary groups for the workflow
        grp_input:
            where does this data come from? = 'external_output_dict'
            dict formated like: 
                {global_scale_grp:"grp_rootOutputs", hook_outpt_grp:"ctrl_spine_bottom_mtx"}
            - Key 'global_scale_grp' = the global scale attrib plug (basically from the root output grp)
            - Key 'hook_outpt_grp' = the output attr from the module(spine) this module(arm) is following (arm hooking into the spine)
        grp_output:
            This is has NO attributes but I will pug the wrist joint's worldSpace data to it so something like and object can follow it!
        


        '''