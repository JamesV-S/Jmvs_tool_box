
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
    def __init__(self, module_name, external_plg_dict, skeleton_dict, fk_dict, ik_dict):
        '''
        *(%) IS THE SYMBOL REPRESENTING SYSTEMS IN THE MODULE I THINK SHOULD BE 
        BUILT IN A SEPERATE CLASS OR FUNCTION ENITRELY

        (&): Limb Stretch | Space Swap | Twist | Bendy 

        neccesary groups for the workflow
        grp_input:
            where does this data come from? = 'external_output_dict'
            dict formated like: 
                {
                "global_scale_grp":"grp_rootOutputs",
                "hook_plg_grp":"grp_Outputs_spine_0_M", 
                "hook_plg_atr":"ctrl_spine_top_mtx"
                }
            - Key 'global_scale_grp' = the global scale attrib plug (basically 
                from the root output grp)
            - Key 'hook_plg_grp' = the output grp of the external grp!
            - Key 'hook_plg_atr' = the output attr from the module(spine) 
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
                
                * only have 1 ik clavicle, never fK clavicle * 

            ex_fk_dict = {
                "fk_pos":{
                    'ctrl_fk_bipedArm_shoulder_0_L': [#.#, #.#, #.#], 
                    'ctrl_fk_bipedArm_elbow_0_L': [#.#, #.#, #.#],
                    'ctrl_fk_bipedArm_wrist_0_L': [#.#, #.#, #.#]
                    },
                "fk_rot":{
                    'ctrl_fk_bipedArm_shoulder_0_L': [#.#, #.#, #.#], 
                    'ctrl_fk_bipedArm_elbow_0_L': [#.#, #.#, #.#],
                    'ctrl_fk_bipedArm_wrist_0_L': [#.#, #.#, #.#]
                    }
                }
            ex_ik_dict = {
                "ik_pos":{
                    'ctrl_ik_bipedArm_clavicle_0_L': [#.#, #.#, #.#], 
                    'ctrl_ik_bipedArm_shoudler_0_L': [#.#, #.#, #.#], 
                    'ctrl_ik_bipedArm_elbow_0_L': [#.#, #.#, #.#],
                    'ctrl_ik_bipedArm_wrist_0_L': [#.#, #.#, #.#]
                    },
                "ik_rot":{
                    'ctrl_ik_bipedArm_clavicle_0_L': [#.#, #.#, #.#], 
                    'ctrl_ik_bipedArm_shoudler_0_L': [#.#, #.#, #.#], 
                    'ctrl_ik_bipedArm_elbow_0_L': [#.#, #.#, #.#],
                    'ctrl_ik_bipedArm_wrist_0_L': [#.#, #.#, #.#]
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
        # Get the pos & rot dicts for fk & ik
        fk_pos_dict = fk_dict["fk_pos"]
        fk_rot_dict = fk_dict["fk_rot"]
        ik_pos_dict = ik_dict["ik_pos"]
        ik_rot_dict = ik_dict["ik_rot"]

        fk_ctrl_list = [key for key in fk_pos_dict.keys()]
        ik_ctrl_list = [key for key in ik_pos_dict.keys()]
        
        unique_id = fk_ctrl_list[0].split('_')[-2]
        side = fk_ctrl_list[0].split('_')[-1]

        clavicle_ctrl = ik_ctrl_list[0]
        arm_root_ctrl = ik_ctrl_list[1]

        ctrl_grp = f"grp_ctrl_{module_name}_{unique_id}_{side}"
        skeleton_grp = f"grp_joints_{module_name}_{unique_id}_{side}"
        logic_grp = f"grp_logic_{module_name}_{unique_id}_{side}"

        print(f"fk_ctrl_list = `{fk_ctrl_list}` | ik_ctrl_list = `{ik_ctrl_list}`")
        print(f"unique_id = `{unique_id}` | side = `{side}`")
        print(f"clavicle_ctrl = `{clavicle_ctrl}` | arm_root_ctrl = `{arm_root_ctrl}`")
        
        inputs_grp, outputs_grp = self.cr_input_output_groups(module_name, unique_id, side)
        self.wire_inputs_grp(inputs_grp, external_plg_dict)
        # temp - add skeleton_grp
        utils.group_module(module_name, unique_id, side ,inputs_grp, outputs_grp)
    

    def cr_input_output_groups(self, module_name, unique_id, side):
        inputs_grp = f"grp_Inputs_{module_name}_{unique_id}_{side}"
        outputs_grp = f"grp_Outputs_{module_name}_{unique_id}_{side}"
        utils.cr_node_if_not_exists(0, "transform", inputs_grp)
        utils.cr_node_if_not_exists(0, "transform", outputs_grp)

        # Input grp
        utils.add_float_attrib(inputs_grp, ["globalScale"], [0.01, 999], True) 
        cmds.setAttr(f"{inputs_grp}.globalScale", 1, keyable=0, channelBox=0)
        utils.add_attr_if_not_exists(inputs_grp, "base_mtx", 'matrix', False)
        utils.add_attr_if_not_exists(inputs_grp, "hook_mtx", 'matrix', False)
        utils.add_float_attrib(inputs_grp, [f"Squash_Value"], [1.0, 1.0], False)
        cmds.setAttr(f"{inputs_grp}.Squash_Value", keyable=1, channelBox=1)
        cmds.setAttr(f"{inputs_grp}.Squash_Value", -0.5)

        # Output grp - for hand module to follow
        utils.add_attr_if_not_exists(outputs_grp, f"ctrl_{module_name}_wrist_mtx", 
                                        'matrix', False)
        
        return inputs_grp, outputs_grp
    

    def wire_inputs_grp(self, inputs_grp, external_plg_dict):
        global_scale_grp = external_plg_dict["global_scale_grp"]
        base_plg_grp = external_plg_dict["base_plg_grp"]
        hook_plg_grp = external_plg_dict["hook_plg_grp"]
        base_plg_atr = external_plg_dict["base_plg_atr"]
        hook_plg_atr = external_plg_dict["hook_plg_atr"]
        
        # connect the global scale
        utils.connect_attr(f"{global_scale_grp}.globalScale", f"{inputs_grp}.globalScale")
        
        # connect the base plug
        utils.connect_attr(f"{base_plg_grp}.{base_plg_atr}", f"{inputs_grp}.base_mtx")

        # connect the hook plug
        utils.connect_attr(f"{hook_plg_grp}.{hook_plg_atr}", f"{inputs_grp}.hook_mtx")


    def cr_skeleton_grp(self):
        pass


    def cr_clavicle_hand_skin_joints(self, ik_ctrl_list):
        skn_clavicle_jnt = f"{ik_ctrl_list[0].replace('ctrl_ik_', 'jnt_skn_')}" # ctrl_ik_bipedArm_clavicle_0_L
        skn_hand_jnt = f"{ik_ctrl_list[-1].replace('ctrl_ik_', 'jnt_skn_')}" # ctrl_ik_bipedArm_clavicle_0_L
        
        for skn_jnt_name in [skn_clavicle_jnt, skn_hand_jnt]:
            cmds.joint(n=skn_jnt_name)
            cmds.select(cl=1)
        return skn_clavicle_jnt, skn_hand_jnt
        

ex_external_plg_dict = {
    "global_scale_grp":"grp_Outputs_root_0_M",
    "base_plg_grp":"grp_Outputs_root_0_M",
    "base_plg_atr":"ctrl_centre_mtx",
    "hook_plg_grp":"grp_Outputs_spine_0_M", 
    "hook_plg_atr":"ctrl_spine_top_mtx"
    }
# Do I need 'skeleton_dict' arg?
ex_skeleton_dict = {} # -> maybe if I want to be able to do deformations at any stage of the game. 

ex_fk_dict = {
    "fk_pos":{
        'ctrl_fk_bipedArm_shoulder_0_L': [47.19038675793399, 202.90135192871094, -8.067196952221522], 
        'ctrl_fk_bipedArm_elbow_0_L': [86.67167131661598, 202.90135192871094, -8.067196952221524],
        'ctrl_fk_bipedArm_wrist_0_L': [122.01356659109904, 202.9013566591099, -8.067197667477195]
        },
    "fk_rot":{
        'ctrl_fk_bipedArm_shoulder_0_L': [0.0, 0.0, 0.0], 
        'ctrl_fk_bipedArm_elbow_0_L': [0.0, 0.0, 0.0],
        'ctrl_fk_bipedArm_wrist_0_L': [0.0, 0.0, 0.0]
        }
    }
ex_ik_dict = {
    "ik_pos":{
        'ctrl_ik_bipedArm_clavicle_0_L': [3.0937706746970637, 211.9463944293447, -3.981268190856912],
        'ctrl_ik_bipedArm_shoudler_0_L': [47.19038675793399, 202.90135192871094, -8.067196952221522], 
        'ctrl_ik_bipedArm_elbow_0_L': [86.67167131661598, 202.90135192871094, -8.067196952221524],
        'ctrl_ik_bipedArm_wrist_0_L': [122.01356659109904, 202.9013566591099, -8.067197667477195]
        },
    "ik_rot":{
        'ctrl_ik_bipedArm_clavicle_0_L': [0.0, 0.0, 0.0],
        'ctrl_ik_bipedArm_shoudler_0_L': [0.0, 0.0, 0.0], 
        'ctrl_ik_bipedArm_elbow_0_L': [0.0, 0.0, 0.0],
        'ctrl_ik_bipedArm_wrist_0_L': [0.0, 0.0, 0.0]
        }
    }

ArmSystem("bipedArm", ex_external_plg_dict, ex_skeleton_dict, ex_fk_dict, ex_ik_dict)

pos = {"clavicle": [3.0937706746970637, 211.9463944293447, -3.981268190856912], 
 "shoulder": [47.19038675793399, 202.90135192871094, -8.067196952221522], 
 "elbow": [86.67167131661598, 202.90135192871094, -8.067196952221524], 
 "wrist": [122.01356659109904, 202.9013566591099, -8.067197667477195]}

rot = {"clavicle": [-1.062264791699132, 5.186453236323401, -11.591655208873357], 
       "shoulder": [0.0, 0.0, 0.0], 
       "elbow": [0.0, 0.0, 0.0], 
       "wrist": [0.0, 0.0, 0.0]}