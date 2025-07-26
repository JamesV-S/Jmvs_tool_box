
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
        '''
        *(%) IS THE SYMBOL REPRESENTING SYSTEMS IN THE MODULE I THINK SHOULD BE 
        BUILT IN A SEPERATE CLASS OR FUNCTION ENITRELY

        (&): Limb Stretch | Space Swap | Twist | Bendy 

        neccesary groups for the workflow
        grp_input:
            where does this data come from? = 'external_output_dict'
            dict formated like: 
                {global_scale_grp:"grp_rootOutputs", hook_outpt_grp:"ctrl_spine_bottom_mtx"}
            - Key 'global_scale_grp' = the global scale attrib plug (basically 
                from the root output grp)
            - Key 'hook_outpt_grp' = the output attr from the module(spine) 
                this module(arm) is following (arm hooking into the spine)
        grp_output:
            This is has NO attributes but I will pug the wrist joint's worldSpace 
            data to it so something like and object can follow it!
        
        grp_ctrls: (Controls need to be setup within a scene correctly beforhand by my system tool).
            > where does this data come from? = 'fk_dict','ik_dict'
            
            *Char_system tool should utalise a layer effect like this:
            1. Check scene for the correct data, return True(continue process)/False(stop process).
            2. Go through the data in the scene and clean it (group controls properly and clean values).
            3. save scene named appropriatly to folder structure that make sense for rigging.
            4. Gather the data in the neccesary scene (now it has been verified and cleaned).
                Storing it in database(or however I want to pass the fk_dict & ik_dict to this class)
            5. Run this system class that builds the arm system (or any other module system!)
            
            example of 'fk_dict','ik_dict' data structure:
                Containing control_name | control & joint position | 
            fk_dict = {
                "fk_pos":{
                    'ctrl_fk_bipedArm_clavicle_0_L': [0.0, 147.0, 0.0], 
                    'ctrl_fk_bipedArm_clavicle_': [0.0, 167.29999965429306, 0.0], 
                    'ctrl_fk_bipedArm_clavicle_': [0.0, 187.59999930858612, 0.0]
                    },
                "fk_rot":{
                    'ctrl_fk_bipedArm_clavicle_': [0.0, 0.0, 0.0], 
                    'ctrl_fk_bipedArm_clavicle_': [0.0, 0.0, 0.0], 
                    'ctrl_fk_bipedArm_clavicle_': [0.0, 0.0, 0.0]
                    }
                }
            ik_dict = {
                "ik_pos":{
                    'ctrl_fk_bipedArm_clavicle_': [0.0, 147.0, 0.0], 
                    'ctrl_fk_bipedArm_clavicle_': [0.0, 176.0, 0.0], 
                    'ctrl_fk_bipedArm_clavicle_': [0.0, 205.0, 0.0]
                    },
                "ik_rot":{
                    'ctrl_fk_bipedArm_clavicle_': [0.0, 0.0, 0.0], 
                    'ctrl_fk_bipedArm_clavicle_': [0.0, 0.0, 0.0], 
                    'ctrl_fk_bipedArm_clavicle_': [0.0, 0.0, 0.0]
                    }
                }
            
            Important: 'ctrl_ik_bipedArm_shoudler_0_L' acts as the root ctrl of the limb!

            (%) Arm shape controllers should be another class. So the creation 
                function can be placed within a proceeding layer widget in 'char_systems'
                -> the controlls are stored here in this group! 
            
            
        skeleton_grp:
            > where does this data come from? = 'fk_dict','ik_dict' & writing the equivilant joint names!
                Contains SKIN joints for the module. 
                    Including: 
                    clavicle | wrist | (%) twist & bendy joints upperarm and lowerarm chains (6 each)
                
                (%) To deterimine the number of joints needed for the upper & 
                lowerarm twist/bendy skn joints: 
                ->Length of the section (with curve) / 8
                -> answer = round up or down & must be an even number!

                SKIN joints are integrated into this, to be able to work on deformations
                at any stage, make the skn joints in a function that can be shared to char_skeleton tool
                and if it [char_skeleton] finds no skn joints it makes temp ones to save skinning data for.
                Meaning one rigger does defo and the other systems!
        
        logic_grp:
            > where does this data come from? = 'fk_dict','ik_dict' & writing the equivilant joint names!
            Contains: RIG_JOINTS | IK_handles | Constraints like polevector | (%) system obj for stretch sys
            
            rig joints drive the ik system!
            fk is achieved with space matrix's parenting 
        '''

        fk_ctrl_list = [fk_ctrl for fk_ctrl in list(fk_dict.key())]
        ik_ctrl_list = [ik_ctrl for ik_ctrl in list(ik_dict.key())]

        
ex_external_output_dict = {
    "global_scale_grp":"grp_rootOutputs", 
    "hook_outpt_grp":"ctrl_spine_bottom_mtx"
    }
# Do I need 'skeleton_dict' arg?
ex_skeleton_dict = {} # -> maybe if I want to be able to do deformations at any stage of the game. 

ex_fk_dict = {
    "fk_pos":{
        'ctrl_fk_bipedArm_clavicle_0_L': [0.0, 147.0, 0.0], 
        'ctrl_fk_bipedArm_shoulder_0_L': [0.0, 167.29999965429306, 0.0], 
        'ctrl_fk_bipedArm_elbow_0_L': [0.0, 187.59999930858612, 0.0],
        'ctrl_fk_bipedArm_wrist_0_L': [0.0, 187.59999930858612, 0.0]
        },
    "fk_rot":{
        'ctrl_fk_bipedArm_clavicle_0_L': [0.0, 0.0, 0.0], 
        'ctrl_fk_bipedArm_shoulder_0_L': [0.0, 167.29999965429306, 0.0], 
        'ctrl_fk_bipedArm_elbow_0_L': [0.0, 187.59999930858612, 0.0],
        'ctrl_fk_bipedArm_wrist_0_L': [0.0, 0.0, 0.0]
        }
    }
ex_ik_dict = {
    "ik_pos":{
        'ctrl_ik_bipedArm_shoudler_0_L': [0.0, 147.0, 0.0], 
        'ctrl_ik_bipedArm_elbow_0_L': [0.0, 187.59999930858612, 0.0],
        'ctrl_ik_bipedArm_wrist_0_L': [0.0, 0.0, 0.0]
        },
    "ik_rot":{
        'ctrl_ik_bipedArm_shoudler_0_L': [0.0, 0.0, 0.0], 
        'ctrl_ik_bipedArm_elbow_0_L': [0.0, 187.59999930858612, 0.0],
        'ctrl_ik_bipedArm_wrist_0_L': [0.0, 0.0, 0.0]
        }
    }

ArmSystem("bipedArm", ex_external_output_dict, ex_skeleton_dict, ex_fk_dict, ex_ik_dict)