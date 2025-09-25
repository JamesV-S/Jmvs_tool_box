
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

'''
import importlib
from Jmvs_tool_box.systems.sys_char_rig import biped_arm_sys

importlib.reload(biped_arm_sys)
'''

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
            This is has NO attributes but I will plug the wrist joint's worldSpace 
            data to it so something like and object can follow it!
        
        grp_ctrls:
            Controls for the module need to be present in the scene. They should 
            be at the be at the origin of the world. 'Char_sys' tool should gather 
            the control's from 'char_lay', keeping their shape & colour, so all 
            the module class's like this one just have to positon the control and 
            it should be perfect!

            > where does this data come from? = 'fk_dict','ik_dict'
            
            *Char_system tool should utalise a layer effect like this:
            1. Check scene for the correct data, return True(continue process)/
                False(stop process).
            2. Go through the data in the scene and clean it (group controls properly 
                and be at the origin with no history!).
            3. save scene named appropriatly to folder structure that make sense 
                for rigging.
            4. Gather the data in the neccesary scene (now it has been verified 
                and cleaned). Storing it in database(or however I want to pass 
                the fk_dict & ik_dict to this class)
            5. Run this system class that builds the arm system (or any other 
                module system!)
            
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
                    'ctrl_ik_bipedArm_shoulder_0_L': [#.#, #.#, #.#], 
                    'ctrl_ik_bipedArm_elbow_0_L': [#.#, #.#, #.#],
                    'ctrl_ik_bipedArm_wrist_0_L': [#.#, #.#, #.#]
                    },
                "ik_rot":{
                    'ctrl_ik_bipedArm_clavicle_0_L': [#.#, #.#, #.#], 
                    'ctrl_ik_bipedArm_shoulder_0_L': [#.#, #.#, #.#], 
                    'ctrl_ik_bipedArm_elbow_0_L': [#.#, #.#, #.#],
                    'ctrl_ik_bipedArm_wrist_0_L': [#.#, #.#, #.#]
                    }
                }
            
            Important: 'ctrl_ik_bipedArm_shoulder_0_L' acts as the root ctrl of the limb!

            (%) Arm shape controllers should be another class. So the creation 
                function can be placed within a proceeding layer widget in 'char_systems'
                -> the controlls are stored here in this group!
                -> Could also utalise inheritance with oop now i know it. 
                        
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
        skeleton_pos = skeleton_dict["skel_pos"]
        skeleton_rot = skeleton_dict["skel_rot"]
        # Get the pos & rot dicts for fk & ik
        fk_pos_dict = fk_dict["fk_pos"]
        fk_rot_dict = fk_dict["fk_rot"]
        ik_pos_dict = ik_dict["ik_pos"]
        ik_rot_dict = ik_dict["ik_rot"]
        
        # return lists for storing control names!
        fk_ctrl_list = [key for key in fk_pos_dict.keys()]
        ik_ctrl_list = [key for key in ik_pos_dict.keys()]
        
        self.mdl_nm = module_name
        self.unique_id = fk_ctrl_list[0].split('_')[-2]
        self.side = fk_ctrl_list[0].split('_')[-1]

        # Plg data from 'external_plg_dict'.
        GLOBAL_SCALE_PLG = f"{external_plg_dict['global_scale_grp']}.{external_plg_dict['global_scale_attr']}" # grp_Outputs_root_0_M.globalScale
        BASE_MTX_PLG = f"{external_plg_dict['base_plg_grp']}.{external_plg_dict['base_plg_atr']}" # grp_Outputs_root_0_M.ctrl_centre_mtx
        HOOK_MTX_PLG = f"{external_plg_dict['hook_plg_grp']}.{external_plg_dict['hook_plg_atr']}" # grp_Outputs_spine_0_M.ctrl_spine_top_mtx
        
        # initialise variables for clav & arm_root ctrls. (special controls in the system!) 
        ctrl_clav = ik_ctrl_list[0]
        ctrl_armRt = ik_ctrl_list[1]
        
        # Ini ggroup names!
        ctrl_grp = f"grp_ctrl_{self.mdl_nm}_{self.unique_id}_{self.side}"
        joint_grp = f"grp_joints_{self.mdl_nm}_{self.unique_id}_{self.side}"
        logic_grp = f"grp_logic_{self.mdl_nm}_{self.unique_id}_{self.side}"

        # print(f"fk_ctrl_list = `{fk_ctrl_list}` | ik_ctrl_list = `{ik_ctrl_list}`")
        # print(f"self.unique_id = `{self.unique_id}` | self.side = `{self.side}`")
        # print(f"ctrl_clav = `{ctrl_clav}` | ctrl_armRt = `{ctrl_armRt}`")
        
        # Input & Output grp setup
        inputs_grp, outputs_grp = self.cr_input_output_groups()
        if cmds.objExists(external_plg_dict['global_scale_grp']):
            self.wire_inputs_grp(inputs_grp, GLOBAL_SCALE_PLG, BASE_MTX_PLG, HOOK_MTX_PLG)

        # Group the controls!
        self.group_ctrls(fk_ctrl_list, "fk")
        self.group_ctrls(ik_ctrl_list, "ik")

        # cr skn joints
        skn_jnt_clav, skn_jnt_wrist = self.cr_jnt_skn_start_end(ik_pos_dict)
        # for the two joint chains that are used for twisting, I need to make new pos & rot dicts for them
        upper_skel_pos = ""
        upper_skel_rot = ""
        lower_skel_pos = ""
        lower_skel_rot = ""
        ''' replace with custom one '''
        # sknUpper_jnt_chain = self.cr_jnt_type_chain("skn_Upper", skeleton_pos, skeleton_rot)
        # sknLower_jnt_chain = self.cr_jnt_type_chain("skn_lower", skeleton_pos, skeleton_rot)

        # # wire connections
        # self.wire_clav_armRt_setup(inputs_grp, [ctrl_clav, ctrl_armRt], skn_jnt_clav, ik_pos_dict, ik_rot_dict)
        # fk_blend_dict = {
        #     "fk_base_plg": f"{inputs_grp}.base_mtx", 
        #     "fk_mdlRt_plg":f"{ctrl_armRt}{utils.Plg.wld_mtx_plg}"
        #     }
        # self.fk_logic_setup(fk_blend_dict, fk_ctrl_list, fk_pos_dict, fk_rot_dict, 
        #                     module_name, self.unique_id, self.side)
        # # group the module
        # utils.group_module(module_name=module_name, unique_id=self.unique_id, 
        #                    side=self.side ,input_grp=inputs_grp, output_grp=outputs_grp, 
        #                    ctrl_grp=None, joint_grp=joint_grp, logic_grp=None)
    

    def cr_input_output_groups(self):
        inputs_grp = f"grp_Inputs_{self.mdl_nm}_{self.unique_id}_{self.side}"
        outputs_grp = f"grp_Outputs_{self.mdl_nm}_{self.unique_id}_{self.side}"
        utils.cr_node_if_not_exists(0, "transform", inputs_grp)
        utils.cr_node_if_not_exists(0, "transform", outputs_grp)

        # Input grp
        utils.add_float_attrib(inputs_grp, ["globalScale"], [0.01, 999], True) 
        cmds.setAttr(f"{inputs_grp}.globalScale", 1, keyable=0, channelBox=0)
        utils.add_attr_if_not_exists(inputs_grp, "base_mtx", 'matrix', False)
        utils.add_attr_if_not_exists(inputs_grp, "hook_mtx", 'matrix', False)

        # Output grp - for hand module to follow
        utils.add_attr_if_not_exists(outputs_grp, f"ctrl_{self.mdl_nm}_wrist_mtx", 
                                        'matrix', False)
        
        '''*module dependant data below (basically this data changes depending on the module)'''
        utils.add_float_attrib(inputs_grp, [f"Squash_Value"], [1.0, 1.0], False)
        cmds.setAttr(f"{inputs_grp}.Squash_Value", keyable=1, channelBox=1)
        cmds.setAttr(f"{inputs_grp}.Squash_Value", -0.5)

        return inputs_grp, outputs_grp
    

    def wire_inputs_grp(self, inputs_grp, global_scale_plg, base_mtx_plg, hook_mtx_plg):
        # connect the global scale
        utils.connect_attr(global_scale_plg, f"{inputs_grp}.globalScale")
        # connect the base plug
        utils.connect_attr(base_mtx_plg, f"{inputs_grp}.base_mtx")
        # connect the hook plug
        utils.connect_attr(hook_mtx_plg, f"{inputs_grp}.hook_mtx")


    def group_ctrls(self, ctrl_ls, ctrl_type):
        '''
        # Description:
            Creates control group for a list of ctrls.
        # Attributes:
            ctrl_ls (list): list of given controls.
            ctrl_type (string): Name for the ctrl_grp.
        # Returns:N/A
        '''
        # If the parent ctrl_grp doesn't exist make it:
        module_control_grp = f"grp_ctrls_{self.mdl_nm}_{self.unique_id}_{self.side}"
        if not cmds.objExists(module_control_grp):
            utils.cr_node_if_not_exists(0, "transform", module_control_grp)

        child_ctrl_grp = f"grp_ctrl_{ctrl_type}_{self.mdl_nm}_{self.unique_id}_{self.side}"
        utils.cr_node_if_not_exists(0, "transform", child_ctrl_grp)
        
        for ctrl in ctrl_ls:
            cmds.parent(ctrl, child_ctrl_grp)
        cmds.parent(child_ctrl_grp, module_control_grp)
    

    def cr_jnt_skn_start_end(self, ik_pos):
        '''
        # Description:
            Creates start & end skin joints which are intended to be driven by
            their respective control & drive the geometry with skincluster.
        # Attributes:
            ik_pos (dict): key = fk ctrl name, value = positonal data.
        # Returns:
            skn_start_name (string): start skin joint name. 
            skn_end_name (string): end skin joint name. 
        '''
        names = [key for key in ik_pos.keys()]
        pos = [value for value in ik_pos.values()]
    
        skn_start_name = names[0].replace("ctrl_ik_", "jnt_skn_")
        skn_end_name = names[-1].replace("ctrl_ik_", "jnt_skn_")
        skn_start_pos = pos[0]
        skn_end_pos = pos[-1]

        for jnt_nm in [skn_start_name, skn_end_name]:
            cmds.select(cl=True)
            cmds.joint(n=jnt_nm)

        return skn_start_name, skn_end_name
    
    ''' 
    *Needs to be its own function that:
        - creates upper/lower chain.
        - cr joints between the distance of shoulder & elbow
        - use distance to provide a reasonable number of joints to put there, 
            Must be even number!
        - Their positon & orientation is determined by ik setup, similar to the 
            StrFW or StrBW ik set up with a normal ikhandle.
            
    '''
    # def cr_jnt_type_chain(self, pref, skeleton_pos, skeleton_rot, reverse_direction=False):
    #     '''
    #     # Description:
    #        Creates a basic desired joint chain, naming, position and direction all 
    #        taken care of. 
    #     # Attributes:
    #         pref (string): name of the joint chain type.
    #         skeleton_pos (dict): key = name of spine iteration (spine#), value = positonal data.
    #         skeleton_rot (dict): key = name of spine iteration (spine#), value = rotational data.
    #         reverse_direction (bool): If True, the joint chain is reversed.
    #     # Returns:
    #         jnt_ls (list): The list of joints within the chain.
    #     '''
    #     cmds.select(cl=True)
    #     jnt_chain_ls = []
    #     # reverse the positon data
    #     # need to figure out how I need to flip or minus the rotate values (for when they have just 0.0 or a value.)
    #     # That'll consist of flipping the primary axis & 
    #     print(f"skeleton_rot = {skeleton_rot}")
    #     rev_skel_pos = utils.reverse_pos_values_dict(skeleton_pos)
    #     rev_skel_rot = utils.reverse_rot_values_dict(skeleton_rot)
    #     for name in skeleton_pos:
    #         jnt_nm = f"jnt_{pref}_{self.mdl_nm}_{name}_{self.unique_id}_{self.side}"
    #         jnt_chain_ls.append(jnt_nm)
    #         cmds.joint(n=jnt_nm)
    #         if reverse_direction:
    #             cmds.xform(jnt_nm, translation=rev_skel_pos[name], worldSpace=True)
    #             cmds.xform(jnt_nm, rotation=skeleton_rot[name], worldSpace=True)
    #         else:
    #             cmds.xform(jnt_nm, translation=skeleton_pos[name], worldSpace=True)
    #             cmds.xform(jnt_nm, rotation=skeleton_rot[name], worldSpace=True)
    #         cmds.makeIdentity(jnt_nm, a=1, t=0, r=1, s=0, n=0, pn=1)
    #     utils.clean_opm(jnt_chain_ls[0])

    #     return jnt_chain_ls


    def group_jnts_skn(self, skn_start_end_ls, skn_jnt_chain):
        '''
        # Description:
            Creates joint group for this module.
        # Attributes:
            skn_start_end_ls (list): skin start and end oints.
            skn_jnt_chain (list): list of skin joint chain.
        # Returns:
            joint_grp (string): Joint group.
        '''
        joint_grp = f"grp_joints_{self.mdl_nm}_{self.unique_id}_{self.side}"
        utils.cr_node_if_not_exists(0, "transform", joint_grp)
        for skn in skn_start_end_ls:
            cmds.parent(skn, joint_grp)
        cmds.parent(skn_jnt_chain[0], joint_grp)

        return joint_grp

    # Ctrl mtx setup
    def wire_clav_armRt_setup(self, inputs_grp, ctrl_list, skn_jnt_clav, pos_dict, rot_dict):
        ctrl_clav = ctrl_list[0]
        ctrl_armRt = ctrl_list[1]
        # ctrl_clavicle setup
        # module_hook_mtx into ctrl_clavicle     
        mm_ctrl_clav = f"MM_{ctrl_clav}"
        utils.cr_node_if_not_exists(1, 'multMatrix', mm_ctrl_clav)
            # set matrix offset value to MM[0]
        clav_pos = list(pos_dict.values())[0]
        clav_rot = list(rot_dict.values())[0]
        utils.set_transformation_matrix(clav_pos, clav_rot, f"{mm_ctrl_clav}{utils.Plg.mtx_ins[0]}")
            # plug incoming plug (the one to follow) to MM[1]
        utils.connect_attr(f"{inputs_grp}.hook_mtx", f"{mm_ctrl_clav}{utils.Plg.mtx_ins[1]}")
            # plug MM sum to obj to follow!
        utils.connect_attr(f"{mm_ctrl_clav}{utils.Plg.mtx_sum_plg}", f"{ctrl_clav}{utils.Plg.opm_plg}")
        # clavicle skin joint
        mm_skn_clav = f"MM_{skn_jnt_clav}"
        utils.cr_node_if_not_exists(1, 'multMatrix', mm_skn_clav)
        utils.connect_attr(f"{ctrl_clav}{utils.Plg.wld_mtx_plg}", f"{mm_skn_clav}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{mm_skn_clav}{utils.Plg.mtx_sum_plg}", f"{skn_jnt_clav}{utils.Plg.opm_plg}")
        
        # ctrl arm root (shoulder)
        mm_ctrl_armRoot = f"MM_{ctrl_armRt}"
        utils.cr_node_if_not_exists(1, 'multMatrix', mm_ctrl_armRoot)
        armRt_pos = list(pos_dict.values())[1]
        armRt_rot = list(rot_dict.values())[1]
        armRt_offset_pos = [x - y for x, y in zip(armRt_pos, clav_pos)]
        armRt_offset_rot = [x - y for x, y in zip(armRt_rot, clav_rot)]
        print(f"armRt_offset == {armRt_offset_pos}")
        utils.set_transformation_matrix(armRt_offset_pos, armRt_offset_rot, f"{mm_ctrl_armRoot}{utils.Plg.mtx_ins[0]}")
        utils.connect_attr(f"{skn_jnt_clav}{utils.Plg.wld_mtx_plg}", f"{mm_ctrl_armRoot}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{mm_ctrl_armRoot}{utils.Plg.mtx_sum_plg}", f"{ctrl_armRt}{utils.Plg.opm_plg}")
       
 
    def fk_logic_setup(self, fk_blend_dict, fk_ctrl_list, pos_dict, rot_dict):
        # cr a list of the 'jnt_rig_fk' items
        rig_jnt_list = [ctrl.replace('ctrl_fk_', 'jnt_rig_') for ctrl in fk_ctrl_list]
        print(f"rig_jnt_list = {rig_jnt_list} | fk_blend_dict = {fk_blend_dict}")

        # connect rotations of arm fk to fk ctrls
        for ctrl, jnt in zip(fk_ctrl_list, rig_jnt_list):
            utils.connect_attr(f"{ctrl}.rotateX", f"{jnt}.rotateX")
            utils.connect_attr(f"{ctrl}.rotateY", f"{jnt}.rotateY")
            utils.connect_attr(f"{ctrl}.rotateZ", f"{jnt}.rotateZ")

        # cr MM x2 & BM
        MM_base = f"MM_fk_base_{self.mdl_nm}_{self.unique_id}_{self.side}"
        MM_armRt = f"MM_fk_root_{self.mdl_nm}_{self.unique_id}_{self.side}"
        BM_ctrl_fk_blend = f"BM_fk_blend_{self.mdl_nm}_{self.unique_id}_{self.side}"
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_base)
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_armRt)
        utils.cr_node_if_not_exists(1, 'blendMatrix', BM_ctrl_fk_blend)
            # MM_base wires
        ofs_base_pos = list(pos_dict.values())[0]
        ofs_base_rot = list(rot_dict.values())[0]
        utils.set_transformation_matrix(ofs_base_pos, ofs_base_rot, f"{MM_base}{utils.Plg.mtx_ins[0]}")
        utils.connect_attr(fk_blend_dict["fk_base_plg"], f"{MM_base}{utils.Plg.mtx_ins[1]}")
            # MM_mdlRt (arm root) wires
        utils.connect_attr(fk_blend_dict["fk_mdlRt_plg"], f"{MM_armRt}{utils.Plg.mtx_ins[1]}")
            # BM wires
                # Add (%) follow attr for fk shoulder ctrl!
        utils.add_locked_attrib(fk_ctrl_list[0], ["Locked"])
        utils.add_float_attrib(fk_ctrl_list[0], ["Follow_Arm_Rot"], [0.0, 1.0], True) 
        utils.connect_attr(f"{MM_base}{utils.Plg.mtx_sum_plg}", f"{BM_ctrl_fk_blend}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{MM_armRt}{utils.Plg.mtx_sum_plg}", f"{BM_ctrl_fk_blend}{utils.Plg.target_mtx[0]}")
        utils.connect_attr(f"{fk_ctrl_list[0]}.Follow_Arm_Rot", f"{BM_ctrl_fk_blend}.target[0].rotateWeight")
                # Blend output plug
        utils.connect_attr(f"{BM_ctrl_fk_blend}{utils.Plg.out_mtx_plg}", f"{fk_ctrl_list[0]}{utils.Plg.opm_plg}")
        utils.connect_attr(f"{BM_ctrl_fk_blend}{utils.Plg.out_mtx_plg}", f"{rig_jnt_list[0]}{utils.Plg.opm_plg}")
        
        ''' Optimise '''
        # proceeding fk control matrix parenting (ctrl_elbow following ctrl_shoulder)
        # elbow
        MM_ctrl_fk_1 = f"MM_{fk_ctrl_list[1]}"
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_ctrl_fk_1)
        fk_1_offset_pos = [x - y for x, y in zip(list(pos_dict.values())[1], list(pos_dict.values())[0])]
        fk_1_offset_rot = [x - y for x, y in zip(list(rot_dict.values())[1], list(rot_dict.values())[0])]
        utils.set_transformation_matrix(fk_1_offset_pos, fk_1_offset_rot, f"{MM_ctrl_fk_1}{utils.Plg.mtx_ins[0]}")
        utils.connect_attr(f"{fk_ctrl_list[0]}{utils.Plg.wld_mtx_plg}", f"{MM_ctrl_fk_1}{utils.Plg.mtx_ins[1]}")
            # MM output
        utils.connect_attr(f"{MM_ctrl_fk_1}{utils.Plg.mtx_sum_plg}", f"{fk_ctrl_list[1]}{utils.Plg.opm_plg}")
        # wrist
        MM_ctrl_fk_2 = f"MM_{fk_ctrl_list[2]}"
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_ctrl_fk_2)
        fk_1_offset_pos = [x - y for x, y in zip(list(pos_dict.values())[2], list(pos_dict.values())[1])]
        fk_1_offset_rot = [x - y for x, y in zip(list(rot_dict.values())[2], list(rot_dict.values())[1])]
        utils.set_transformation_matrix(fk_1_offset_pos, fk_1_offset_rot, f"{MM_ctrl_fk_2}{utils.Plg.mtx_ins[0]}")
        utils.connect_attr(f"{fk_ctrl_list[1]}{utils.Plg.wld_mtx_plg}", f"{MM_ctrl_fk_2}{utils.Plg.mtx_ins[1]}")
            # MM output
        utils.connect_attr(f"{MM_ctrl_fk_2}{utils.Plg.mtx_sum_plg}", f"{fk_ctrl_list[2]}{utils.Plg.opm_plg}")
        ''' Optimise '''

'''
'ex_external_plg_dict' is an important dictionary that should be intiilaised by 
a seprate script just used for creating attributes. In the same script this 
dctionary is sent to the databaase!
'''
ex_external_plg_dict = {
    "global_scale_grp":"grp_Outputs_root_0_M",
    "global_scale_attr":"globalScale",
    "base_plg_grp":"grp_Outputs_root_0_M",
    "base_plg_atr":"ctrl_centre_mtx",
    "hook_plg_grp":"grp_Outputs_spine_0_M", 
    "hook_plg_atr":"ctrl_spine_top_mtx"
    }
# Do I need 'skeleton_dict' arg?
ex_skeleton_dict = {
    "skel_pos":{
        "clavicle":[3.0937706746970637, 211.9463944293447, -3.981268190856912],
        "shoulder":[47.19038675793399, 202.90135192871094, -8.067196952221522],
        "elbow":[86.67167131661598, 202.90135192871094, -8.067196952221524],
        "wrist":[122.01356659109904, 202.9013566591099, -8.067197667477195]
    },
    "skel_rot":{
        "clavicle":[],
        "shoulder":[],
        "elbow":[],
        "wrist":[]
    }
} # -> maybe if I want to be able to do deformations at any stage of the game. 

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
        'ctrl_ik_bipedArm_shoulder_0_L': [47.19038675793399, 202.90135192871094, -8.067196952221522], 
        'ctrl_ik_bipedArm_elbow_0_L': [86.67167131661598, 202.90135192871094, -8.067196952221524],
        'ctrl_ik_bipedArm_wrist_0_L': [122.01356659109904, 202.9013566591099, -8.067197667477195]
        },
    "ik_rot":{
        'ctrl_ik_bipedArm_clavicle_0_L': [0.0, 0.0, 0.0],
        'ctrl_ik_bipedArm_shoulder_0_L': [0.0, 0.0, 0.0], 
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