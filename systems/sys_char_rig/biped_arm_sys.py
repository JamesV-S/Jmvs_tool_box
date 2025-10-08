
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
    def __init__(self, module_name, external_plg_dict, skeleton_dict, fk_dict, ik_dict, prim_axis, shaper_dict=None):
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
        skeleton_pos_dict = skeleton_dict["skel_pos"]
        skeleton_rot_dict = skeleton_dict["skel_rot"]
        self.fk_pos_dict = fk_dict["fk_pos"]
        self.fk_rot_dict = fk_dict["fk_rot"]
        self.ik_pos_dict = ik_dict["ik_pos"]
        self.ik_rot_dict = ik_dict["ik_rot"]
        self.prim_axis = prim_axis

        # return lists for storing control names!
        fk_ctrl_list = [key for key in self.fk_pos_dict.keys()]
        ik_ctrl_list = [key for key in self.ik_pos_dict.keys()]
        
        self.mdl_nm = module_name
        self.unique_id = fk_ctrl_list[0].split('_')[-2]
        self.side = fk_ctrl_list[0].split('_')[-1]
        
        # gather the number of values in the dict
        num_jnts = len(skeleton_pos_dict.keys())

        # Plg data from 'external_plg_dict'.
        GLOBAL_SCALE_PLG = f"{external_plg_dict['global_scale_grp']}.{external_plg_dict['global_scale_attr']}" # grp_Outputs_root_0_M.globalScale
        BASE_MTX_PLG = f"{external_plg_dict['base_plg_grp']}.{external_plg_dict['base_plg_atr']}" # grp_Outputs_root_0_M.ctrl_centre_mtx
        HOOK_MTX_PLG = f"{external_plg_dict['hook_plg_grp']}.{external_plg_dict['hook_plg_atr']}" # grp_Outputs_spine_0_M.ctrl_spine_top_mtx
        self.global_scale_attr = external_plg_dict['global_scale_attr']
        
        # Input & Output grp setup
        inputs_grp, outputs_grp = self.cr_input_output_groups()
        self.add_outputs_matrix_attr(outputs_grp, ["wrist"])
        if cmds.objExists(external_plg_dict['global_scale_grp']):
            self.wire_inputs_grp(inputs_grp, GLOBAL_SCALE_PLG, BASE_MTX_PLG, HOOK_MTX_PLG)

        # Group the controls!
        fk_ctrl_grp = self.group_ctrls(fk_ctrl_list, "fk")
        ik_ctrl_grp = self.group_ctrls(ik_ctrl_list, "ik")

        # cr skn joints
        skn_jnt_clav, skn_jnt_wrist = self.cr_jnt_skn_start_end(self.ik_pos_dict)
        sknUpper_jnt_chain = self.cr_skn_twist_joint_chain("upper", 
                                                           skeleton_pos_dict['shoulder'], 
                                                           skeleton_pos_dict['elbow'])
        sknLower_jnt_chain = self.cr_skn_twist_joint_chain("lower", 
                                                           skeleton_pos_dict['elbow'], 
                                                           skeleton_pos_dict['wrist'])
        self.group_jnts_skn([skn_jnt_clav, skn_jnt_wrist], [sknUpper_jnt_chain, sknLower_jnt_chain])
        
        self.add_custom_input_attr(inputs_grp)

        # wire connections
        self.wire_clav_armRt_setup(inputs_grp, [ik_ctrl_list[0], ik_ctrl_list[1]], skn_jnt_clav, self.ik_pos_dict, self.ik_rot_dict)
        
        blend_armRoot_node = self.wire_fk_ctrl_setup(inputs_grp, ik_ctrl_list[1], fk_ctrl_list, self.fk_pos_dict, self.fk_rot_dict)
        logic_jnt_list = self.cr_logic_rig_joints(fk_ctrl_list, self.fk_pos_dict, self.fk_rot_dict)

        self.wire_fk_ctrl_stretch_setup(fk_ctrl_list, self.fk_pos_dict)
        self.wire_fk_ctrl_to_logic_joint(blend_armRoot_node, fk_ctrl_list, logic_jnt_list)

        self.wire_ctrl_ik_wrist(inputs_grp, ik_ctrl_list)

        print(f"{external_plg_dict['hook_plg_grp'].split('_')[-2]}")
        print(f"{external_plg_dict['hook_plg_grp'].split('_')[-1]}")
        spine_top_name = f"ctrl_ik_spine_spine_top_{external_plg_dict['hook_plg_grp'].split('_')[-2]}_{external_plg_dict['hook_plg_grp'].split('_')[-1]}"
        # temp_spine_name = f"ctrl_ik_spine_top"
        
        self.wire_ctrl_ik_elbow(inputs_grp, ik_ctrl_list, spine_top_name)

        cv_upper = self.cr_logic_curves("upper")
        cv_lower = self.cr_logic_curves("lower")

        self.d_shld_wrist, self.d_shld_elb, self.d_elb_wrist = self.logic_jnt_distances(self.fk_pos_dict)
        bc_ikfk_stretch, logic_ik_hdl = self.wire_ik_logic_elements(inputs_grp, logic_jnt_list, ik_ctrl_list)
        self.group_logic_elements(logic_jnt_list, logic_ik_hdl, [cv_upper, cv_lower])

        skn_jnt_wrist_ik_plg, skn_jnt_wrist_fk_plg = self.wire_jnt_skn_wrist(skn_jnt_wrist, logic_jnt_list, fk_ctrl_list, ik_ctrl_list)

        mdl_settings_ctrl, ikfk_plug, stretch_plug, shaper_plug  = self.cr_mdl_setting_ctrl(skn_jnt_wrist, ik_ctrl_list)
        self.wire_IKFK_switch(skn_jnt_wrist_ik_plg, skn_jnt_wrist_fk_plg, 
                              mdl_settings_ctrl, ikfk_plug, 
                              bc_ikfk_stretch, logic_ik_hdl, 
                              fk_ctrl_grp, ik_ctrl_grp)
        
        '''TEMP shaper_ctrl_list'''
        shaper_ctrl_list = ["ctrl_shp_bipedArm_main_0_L", "ctrl_shp_bipedArm_middle_0_L", 
                            "ctrl_shp_bipedArm_upper_0_L", "ctrl_shp_bipedArm_lower_0_L"]
        shaper_ctrl_grp = self.group_ctrls(shaper_ctrl_list, "shaper")
        self.wire_shaper_ctrls(shaper_ctrl_list, logic_jnt_list, ik_ctrl_list, shaper_plug, shaper_ctrl_grp)

        self.parent_ik_ctrls_out(ik_ctrl_list)

        # # group the module
        # utils.group_module(module_name=module_name, unique_id=self.unique_id, 
        #                    side=self.side ,input_grp=inputs_grp, output_grp=outputs_grp, 
        #                    ctrl_grp=None, joint_grp=joint_grp, logic_grp=None)
    

    def cr_input_output_groups(self, output_global=False):
        inputs_grp = f"grp_Inputs_{self.mdl_nm}_{self.unique_id}_{self.side}"
        outputs_grp = f"grp_Outputs_{self.mdl_nm}_{self.unique_id}_{self.side}"
        utils.cr_node_if_not_exists(0, "transform", inputs_grp)
        utils.cr_node_if_not_exists(0, "transform", outputs_grp)

        # Input grp
        utils.add_float_attrib(inputs_grp, [self.global_scale_attr], [0.01, 999], True)
        cmds.setAttr(f"{inputs_grp}.{self.global_scale_attr}", 1, keyable=0, channelBox=0)
        utils.add_attr_if_not_exists(inputs_grp, "base_mtx", 'matrix', False)
        utils.add_attr_if_not_exists(inputs_grp, "hook_mtx", 'matrix', False)

        if output_global:
            utils.add_float_attrib(outputs_grp, [self.global_scale_attr], [0.01, 999], True)
            cmds.setAttr(f"{outputs_grp}.{self.global_scale_attr}", 1, keyable=0, channelBox=0)

        return inputs_grp, outputs_grp
    

    def add_outputs_matrix_attr(self, outputs_grp, out_matrix_name_list):
        '''
        # Description:
            Add custom matrix to ouptut group -> this matrix lets other modules follow.
        # Attributes:
            outputs_grp (string): Outputgrpup for this module. 
            out_matrix_name_list (list): List of names for matrix attr.
        # Returns: N/A
        '''
        for mtx_name in out_matrix_name_list:
            utils.add_attr_if_not_exists(outputs_grp, f"ctrl_{self.mdl_nm}_{mtx_name}_mtx", 
                                    'matrix', False) # for upper body module to follow


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
        # Returns:
            child_ctrl_grp (string): Name of ctrl child grp
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
        cmds.select(cl=1)

        return child_ctrl_grp
    

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


    def cr_skn_twist_joint_chain(self, twist_name, start_pos, end_pos):
        '''
        TO DO: Test wether the twist joints should always be 6 or the number I calcualte?
        # Description:
           Creates a basic desired joint chain, naming, NO position data. Use 
           distance to provide a reasonable number of joints to put there, they 
           must be an even number!
           The chain will always be a straight chain, it's position is determined 
           by the 'ctrl_ik_bipedArm_shoulder_0_L'.  
           Naming convention = jnt_skn_bipedArm_upper#/lower#_0_L
        # Attributes:
            twist_name (string): Name of the twist chain (upper#/lower#).
            start_pos (list): Position data for start of the chain.
            end_pos (list): Position data for end of the chain.
        # Returns:
            skn_jnt_chain (list): The list of joints within the chain.
        '''
        # need the number of joints. 
            # need the front & end position for the chain to span across.
            # cr temp locators, positon them there, & calculate the distance between them. 
            # distance/6 = number of joints(number MUST be EVEN , so round to the best one.)
        print(f"testting: `cr_skn_twist_joint_chain()`")
        temp_start_locator = f"loc_{twist_name}_start_pos_{self.mdl_nm}_{self.unique_id}_{self.side}"
        temp_end_locator = f"loc_{twist_name}_end_pos_{self.mdl_nm}_{self.unique_id}_{self.side}"
        cmds.spaceLocator(n=temp_start_locator)
        cmds.spaceLocator(n=temp_end_locator)
        cmds.xform(temp_start_locator, t=start_pos, ws=True)
        cmds.xform(temp_end_locator, t=end_pos, ws=True)

        # cr distance between node & wire the locators!
        db_node = f"DB_{twist_name}_distance_{self.mdl_nm}_{self.unique_id}_{self.side}"
        divide_node = f"DIV_{twist_name}_output_{self.mdl_nm}_{self.unique_id}_{self.side}"
        utils.cr_node_if_not_exists(1, "distanceBetween", db_node)
        utils.cr_node_if_not_exists(1, "divide", divide_node, {"input2":6})
        utils.connect_attr(f"{temp_start_locator}{utils.Plg.wld_mtx_plg}", f"{db_node}{utils.Plg.inMatrixs[1]}")
        utils.connect_attr(f"{temp_end_locator}{utils.Plg.wld_mtx_plg}", f"{db_node}{utils.Plg.inMatrixs[2]}")
        utils.connect_attr(f"{db_node}{utils.Plg.distance_plg}", f"{divide_node}.input1")
        
        # get the raw number from the calculation.
        raw_number = cmds.getAttr(f"{divide_node}.output")
        print(f"Twist {twist_name}: raw_number = {raw_number}")
        jnt_num = utils.round_to_even(raw_number)
        print(f"Twist {twist_name}: jnt_num = {jnt_num}")
        
        # Now delete the temp data
        cmds.delete(temp_start_locator, temp_end_locator, db_node, divide_node)

        jnt_chain_ls = []
        # build the joint chain
        for x in range(jnt_num):
            jnt_nm = f"jnt_skn_{self.mdl_nm}_{twist_name}{x}_{self.unique_id}_{self.side}"
            jnt_chain_ls.append(jnt_nm)
            cmds.joint(n=jnt_nm)
            cmds.makeIdentity(jnt_nm, a=1, t=0, r=1, s=0, n=0, pn=1)

        return jnt_chain_ls
        
    ''''''
    def cr_jnt_type_chain(self, pref, skeleton_pos, skeleton_rot, reverse_direction=False):
        '''
        # Description:
           Creates a basic desired joint chain, naming, position and direction all 
           taken care of. 
        # Attributes:
            pref (string): name of the joint chain type.
            skeleton_pos (dict): key = name of spine iteration (spine#), value = positonal data.
            skeleton_rot (dict): key = name of spine iteration (spine#), value = rotational data.
            reverse_direction (bool): If True, the joint chain is reversed.
        # Returns:
            jnt_ls (list): The list of joints within the chain.
        '''
        cmds.select(cl=True)
        jnt_chain_ls = []
        # reverse the positon data
        # need to figure out how I need to flip or minus the rotate values (for when they have just 0.0 or a value.)
        # That'll consist of flipping the primary axis & 
        print(f"skeleton_rot = {skeleton_rot}")
        rev_skel_pos = utils.reverse_pos_values_dict(skeleton_pos)
        rev_skel_rot = utils.reverse_rot_values_dict(skeleton_rot)
        for name in skeleton_pos:
            jnt_nm = f"jnt_{pref}_{self.mdl_nm}_{name}_{self.unique_id}_{self.side}"
            jnt_chain_ls.append(jnt_nm)
            cmds.joint(n=jnt_nm)
            if reverse_direction:
                cmds.xform(jnt_nm, translation=rev_skel_pos[name], worldSpace=True)
                cmds.xform(jnt_nm, rotation=skeleton_rot[name], worldSpace=True)
            else:
                cmds.xform(jnt_nm, translation=skeleton_pos[name], worldSpace=True)
                cmds.xform(jnt_nm, rotation=skeleton_rot[name], worldSpace=True)
            cmds.makeIdentity(jnt_nm, a=1, t=0, r=1, s=0, n=0, pn=1)
        utils.clean_opm(jnt_chain_ls[0])

        return jnt_chain_ls
    ''''''

    def group_jnts_skn(self, skn_start_end_ls, skn_jnt_chain_ls):
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
        for skn in skn_jnt_chain_ls: 
            cmds.parent(skn[0], joint_grp)

        return joint_grp


    def add_custom_input_attr(self, inputs_grp):
        '''
        # Description:
            Add module uniwue attributes to the input group.
        # Attributes:
            inputs_grp (string): Outputgrpup for this module.
        # Returns: N/A
        '''
        utils.add_float_attrib(inputs_grp, [f"Squash_Value"], [1.0, 1.0], False)
        cmds.setAttr(f"{inputs_grp}.Squash_Value", keyable=1, channelBox=1)
        cmds.setAttr(f"{inputs_grp}.Squash_Value", -0.5)

    # Ctrl mtx setup
    def wire_clav_armRt_setup(self, inputs_grp, ctrl_list, skn_jnt_clav, ik_pos_dict, ik_rot_dict):
        '''
        # Description:
            The 'clavicle control' drives the 'clavicle skn_joint' > which drives 
            the 'arm root control' which will then be the root of the rest of the 
            arm module: Both FK & IK follow it.  
        # Attributes:
            input_grp (string): Group for input data for this module.
            ctrl_list (list): Contains ik_clavicle & ik_shoulder(armRoot) control names.
            skn_jnt_clav (string): Clavicle skin joint name.
            ik_pos_dict (dict): key=Name of ik controls, value=Positional data.
            ik_rot_dict (dict): key=Name of ik controls, value=Rotational data.
        # Returns: N/A
        '''
        ctrl_clav = ctrl_list[0]
        ctrl_armRt = ctrl_list[1]
        # Lock the armRt rotate attr
        for axis in (['x', 'y', 'z']):
                cmds.setAttr(f"{ctrl_armRt}.r{axis}", lock=1, keyable=0, cb=1)

        # ctrl_clavicle setup
        # module_hook_mtx into ctrl_clavicle     
        mm_ctrl_clav = f"MM_{ctrl_clav}"
        utils.cr_node_if_not_exists(1, 'multMatrix', mm_ctrl_clav)
            # set matrix offset value to MM[0]
        clav_pos = list(ik_pos_dict.values())[0]
        clav_rot = list(ik_rot_dict.values())[0]
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
        armRt_pos = list(ik_pos_dict.values())[1]
        armRt_rot = list(ik_rot_dict.values())[1]
        armRt_offset_pos = [x - y for x, y in zip(armRt_pos, clav_pos)]
        armRt_offset_rot = [x - y for x, y in zip(armRt_rot, clav_rot)]
        print(f"armRt_offset == {armRt_offset_pos}")
        # utils.set_transformation_matrix(armRt_offset_pos, armRt_offset_rot, f"{mm_ctrl_armRoot}{utils.Plg.mtx_ins[0]}")
        utils.set_matrix(armRt_offset_pos, f"{mm_ctrl_armRoot}{utils.Plg.mtx_ins[0]}")
        utils.connect_attr(f"{skn_jnt_clav}{utils.Plg.wld_mtx_plg}", f"{mm_ctrl_armRoot}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{mm_ctrl_armRoot}{utils.Plg.mtx_sum_plg}", f"{ctrl_armRt}{utils.Plg.opm_plg}")
       
    
    def wire_fk_ctrl_setup(self, inputs_grp, armRt_ctrl, fk_ctrl_list, fk_pos_dict, fk_rot_dict):
        '''
        # Description:
            FK logic setup:
                - cr 3 logic rig joints. 
                - base & armRt to multMatrix each > blendMatrix.
                - setup the fk controls with MM method. 
                - connect ctrl rotates to rig joints rotates
        # Attributes:
            input_grp (string): Group for input data for this module.
            fk_ctrl_list (list): Contains 3 fk control names.
            fk_pos_dict (dict): key=Name of fk controls, value=Positional data.
            fk_rot_dict (dict): key=Name of fk controls, value=Rotational data.
        # Returns:
            BM_shld (utility): Arm root ctrl's (ik_shoulder) matrix follow. 
        '''
        # Add follow attr to fk shoulder ctrl
        utils.add_locked_attrib(fk_ctrl_list[0], ["Follows"])
        utils.add_float_attrib(fk_ctrl_list[0], ["Follow_Arm_Rot"], [0.0, 1.0], True)
        cmds.setAttr(f"{fk_ctrl_list[0]}.Follow_Arm_Rot", 1)
        # cr blendMatrix seyup to feed to fk ctrl/rigJnt shoulder. 
        MM_shldBase = f"MM_{self.mdl_nm}_fkShld_Base_{self.unique_id}_{self.side}"
        MM_shldRtCtrl = f"MM_{self.mdl_nm}_fkShld_rootCtrl_{self.unique_id}_{self.side}"
        BM_shld = f"BM_{self.mdl_nm}__fkShld_blend_{self.unique_id}_{self.side}"
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_shldBase)
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_shldRtCtrl)
        utils.cr_node_if_not_exists(1, 'blendMatrix', BM_shld, 
                                    {"target[0].scaleWeight":0, 
                                     "target[0].shearWeight":0})
        
        # Shoulder
            # wire to the armRtBAse -> It's going into the fk shoulder, so need it's pos(fk shoulder). 
        # utils.set_matrix(list(self.fk_pos_dict.values())[0], f"{MM_wristBase}{utils.Plg.mtx_ins[0]}")
        utils.set_transformation_matrix(list(fk_pos_dict.values())[0], list(fk_rot_dict.values())[0], f"{MM_shldBase}{utils.Plg.mtx_ins[0]}")
        utils.connect_attr(f"{inputs_grp}.base_mtx", f"{MM_shldBase}{utils.Plg.mtx_ins[1]}")
            # MM_shldRtCtrl
        utils.set_transformation_matrix([0.0, 0.0, 0.0], list(fk_rot_dict.values())[0], f"{MM_shldRtCtrl}{utils.Plg.mtx_ins[0]}")
        utils.connect_attr(f"{armRt_ctrl}{utils.Plg.wld_mtx_plg}", f"{MM_shldRtCtrl}{utils.Plg.mtx_ins[1]}")
            # BM_shld
        utils.connect_attr(f"{MM_shldBase}{utils.Plg.mtx_sum_plg}", f"{BM_shld}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{MM_shldRtCtrl}{utils.Plg.mtx_sum_plg}", f"{BM_shld}{utils.Plg.target_mtx[0]}")
        utils.connect_attr(f"{fk_ctrl_list[0]}.Follow_Arm_Rot", f"{BM_shld}.target[0].rotateWeight")
        utils.connect_attr(f"{BM_shld}{utils.Plg.out_mtx_plg}", f"{fk_ctrl_list[0]}{utils.Plg.opm_plg}")
        # create temp locators
        temp_loc_ls = []
        for (key, pos_val), (key, rot_val) in zip(fk_pos_dict.items(), fk_rot_dict.items()):
            loc_name = key.replace('ctrl_fk_', 'loc_temp_')# "ctrl_fk_bipedArm_shoulder_0_L"
            temp_loc_ls.append(loc_name)
            cmds.spaceLocator(n=loc_name)
            cmds.xform(loc_name, t=pos_val, ws=1)
            cmds.xform(loc_name, rotation=rot_val, ws=1)
            
        print(temp_loc_ls)
        try:
            for i in range(len(temp_loc_ls)):
                cmds.parent(temp_loc_ls[i+1],temp_loc_ls[i])
        except IndexError:
            pass
        # cmds.select(cl=1)

        # elbow
        utils.matrix_control_FowardKinematic_setup(fk_ctrl_list[0], fk_ctrl_list[1], temp_loc_ls[1])
        # wrist
        utils.matrix_control_FowardKinematic_setup(fk_ctrl_list[1], fk_ctrl_list[2], temp_loc_ls[2])
        
        # delete the locators
        cmds.delete(temp_loc_ls[0])
        
        return BM_shld


    def cr_logic_rig_joints(self, fk_ctrl_list, fk_pos_dict, fk_rot_dict):
        '''
        # Description:
            Cr 3 logic rig joints. Used for both fk & ik systems.  
        # Attributes:
            fk_ctrl_list (list): Contains 3 fk control names.
            fk_pos_dict (dict): key=Name of fk controls, value=Positional data.
        # Returns: N/A
            jnt_rig_logic_ls (list): list of arm logic joints. 
        '''
        # cr a list of the 'jnt_rig_fk' items
        rig_jnt_list = [ctrl.replace('ctrl_fk_', 'jnt_rig_') for ctrl in fk_ctrl_list]
        print(f"rig_jnt_list = {rig_jnt_list}")
        jnt_rig_logic_ls = []
        for (key, pos_val), (key, rot_val) in zip(fk_pos_dict.items(), fk_rot_dict.items()):
            jnt_nm = key.replace('ctrl_fk_', 'jnt_rig_')
            jnt_rig_logic_ls.append(jnt_nm)
            cmds.joint(n=jnt_nm)
            cmds.xform(jnt_nm, t=pos_val, ws=1)
            cmds.xform(jnt_nm, rotation=rot_val, ws=1)
            
        cmds.select(cl=1)
        
        for axis in (["X", "Y", "Z"]):
            cmds.setAttr(f"{jnt_rig_logic_ls[0]}.translate{axis}", 0)
            cmds.setAttr(f"{jnt_rig_logic_ls[0]}.rotate{axis}", 0)

        cmds.makeIdentity(jnt_rig_logic_ls[1], a=1, t=0, r=1, s=0, n=0, pn=1)
        cmds.makeIdentity(jnt_rig_logic_ls[2], a=1, t=0, r=1, s=0, n=0, pn=1)

        return jnt_rig_logic_ls
        
    
    def wire_fk_ctrl_stretch_setup(self, fk_ctrl_list, fk_pos_dict):
        '''
        # Description:
            - stretches the fk ctrl's by lengthening the control in front. So to 
            stretch the shoulder, the elbow is translated away.
            - This also acts as the default translation position of the fk ctrls. 
        # Attributes:
            fk_ctrl_list (list): Contains 3 fk control names.
            fk_pos_dict (dict): key=Name of fk controls, value=Positional data.
        # Returns: N/A
        '''
        for ctrl in fk_ctrl_list[:-1]:
            utils.add_locked_attrib(ctrl, ["Attributes"])
            utils.add_float_attrib(ctrl, ["Stretch"], [0.01, 999.0], True)
            cmds.setAttr(f"{ctrl}.Stretch", 1)
            
        fk_shld_stretch_distance = utils.get_distance(fk_ctrl_list[0], list(fk_pos_dict.values())[0], list(fk_pos_dict.values())[1])
        fk_elbow_stretch_distance = utils.get_distance(fk_ctrl_list[1], list(fk_pos_dict.values())[1], list(fk_pos_dict.values())[2])
        print(f"--------")
        print(f"fk_shld_elb_stretch_distance = `{fk_shld_stretch_distance}`")
        print(f"--------")
        print(f"fk_elb_wrist_stretch_distance = `{fk_elbow_stretch_distance}`")
        print(f"--------")

        # shoulder stretch
        fm_shld_stretch_mult = f"FM_upFkStretchMult_{self.mdl_nm}_{self.unique_id}_{self.side}"
        fm_shld_stretch_sub = f"FM_upFkStretchSub_{self.mdl_nm}_{self.unique_id}_{self.side}"
        utils.cr_node_if_not_exists(1, "floatMath", fm_shld_stretch_mult, {"operation":2, "floatA":fk_shld_stretch_distance})
        utils.cr_node_if_not_exists(1, "floatMath", fm_shld_stretch_sub, {"operation":1, "floatB":fk_shld_stretch_distance})
        
        utils.connect_attr(f"{fk_ctrl_list[0]}.Stretch", f"{fm_shld_stretch_mult}{utils.Plg.flt_B}")
        utils.connect_attr(f"{fm_shld_stretch_mult}{utils.Plg.out_flt}", f"{fm_shld_stretch_sub}{utils.Plg.flt_A}")
        utils.connect_attr(f"{fm_shld_stretch_sub}{utils.Plg.out_flt}", f"{fk_ctrl_list[1]}.translate{self.prim_axis}")
        
        # elbow stretch
        fm_elb_stretch_mult = f"FM_lowFkStretchMult_{self.mdl_nm}_{self.unique_id}_{self.side}"
        fm_elb_stretch_sub = f"FM_lowFkStretchSub_{self.mdl_nm}_{self.unique_id}_{self.side}"
        utils.cr_node_if_not_exists(1, "floatMath", fm_elb_stretch_mult, {"operation":2, "floatA":fk_elbow_stretch_distance})
        utils.cr_node_if_not_exists(1, "floatMath", fm_elb_stretch_sub, {"operation":1, "floatB":fk_elbow_stretch_distance})
        
        utils.connect_attr(f"{fk_ctrl_list[1]}.Stretch", f"{fm_elb_stretch_mult}{utils.Plg.flt_B}")
        utils.connect_attr(f"{fm_elb_stretch_mult}{utils.Plg.out_flt}", f"{fm_elb_stretch_sub}{utils.Plg.flt_A}")
        utils.connect_attr(f"{fm_elb_stretch_sub}{utils.Plg.out_flt}", f"{fk_ctrl_list[2]}.translate{self.prim_axis}")
        
        return 


    def wire_fk_ctrl_to_logic_joint(self, blend_armRoot_node, fk_ctrl_list, logic_jnt_list):
        '''
        # Description:
            driving the logic joints:
                - parent logic joint is driven by arnRoot ctrl w/ 'blend_armRoot_node'
                - child logic joints are driven by fk ctrl's direct rotations.
        # Attributes:
            blend_armRoot_node (utility): Arm root ctrl's (ik_shoulder) matrix follow.
            fk_ctrl_list (list): Contains 3 fk control names.
            logic_jnt_list (list): list of arm logic joints. 
        # Returns: N/A
        '''
        # connect the BM armRoot node to parent logic joint opm. & zero out the translatevalues!
        utils.connect_attr(f"{blend_armRoot_node}{utils.Plg.out_mtx_plg}", f"{logic_jnt_list[0]}{utils.Plg.opm_plg}")
        for axis in (["X", "Y", "Z"]):
            cmds.setAttr(f"{logic_jnt_list[0]}.translate{axis}", 0)
        # connect rotations of child arm fk ctrls to child logic jnts 
        for ctrl, jnt in zip(fk_ctrl_list, logic_jnt_list):
            utils.connect_attr(f"{ctrl}.rotateX", f"{jnt}.rotateX")
            utils.connect_attr(f"{ctrl}.rotateY", f"{jnt}.rotateY")
            utils.connect_attr(f"{ctrl}.rotateZ", f"{jnt}.rotateZ")


    def wire_ctrl_ik_wrist(self, inputs_grp, ik_ctrl_list):
        '''
        # Description:
            driving the logic joints:
                - parent logic joint is driven by arnRoot ctrl w/ 'blend_armRoot_node'
                - child logic joints are driven by fk ctrl's direct rotations.
        # Attributes:
            inputs_grp (string): Group for input data for this module.
            ik_ctrl_list (list): Contains 4 ik control names.
        # Returns: N/A 
        '''
        ik_ctrl_target = ik_ctrl_list[-1]

        # Add follow attr to fk shoulder ctrl
        utils.add_locked_attrib(ik_ctrl_target, ["Follows"])
        utils.add_float_attrib(ik_ctrl_target, ["Follow_Arm"], [0.0, 1.0], True)
        cmds.setAttr(f"{ik_ctrl_target}.Follow_Arm", 1)
        # cr blendMatrix seyup to feed to fk ctrl/rigJnt shoulder. 
        MM_wristBase = f"MM_{self.mdl_nm}_ikWrist_armRootBase_{self.unique_id}_{self.side}"
        MM_armRootIk = f"MM_{self.mdl_nm}_ikWrist_armRootCtrl_{self.unique_id}_{self.side}"
        BM_wristIk = f"BM_{self.mdl_nm}_ikWrist_armRootBlend_{self.unique_id}_{self.side}"
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_wristBase)
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_armRootIk)
        utils.cr_node_if_not_exists(1, 'blendMatrix', BM_wristIk, 
                                    {"target[0].scaleWeight":0, 
                                     "target[0].shearWeight":0})
        
        # MM_Base
        utils.set_transformation_matrix(list(self.ik_pos_dict.values())[-1], list(self.ik_rot_dict.values())[-1], f"{MM_wristBase}{utils.Plg.mtx_ins[0]}")         
        utils.connect_attr(f"{inputs_grp}.base_mtx", f"{MM_wristBase}{utils.Plg.mtx_ins[1]}")        
            # Setting Rotation is involved!
        # MM_armRootIk
        wrist_local_object = f"temp_loc_{ik_ctrl_target}"
        cmds.spaceLocator(n=wrist_local_object)
        cmds.xform(wrist_local_object, t=self.ik_pos_dict[ik_ctrl_target], ws=1)
        cmds.xform(wrist_local_object, rotation=self.ik_rot_dict[ik_ctrl_target], ws=1)
        cmds.parent(wrist_local_object, ik_ctrl_list[1])
        get_local_matrix = cmds.getAttr(f"{wrist_local_object}.matrix")

        cmds.setAttr(f"{MM_armRootIk}{utils.Plg.mtx_ins[0]}", *get_local_matrix, type="matrix")    
        utils.connect_attr(f"{ik_ctrl_list[1]}{utils.Plg.wld_mtx_plg}", f"{MM_armRootIk}{utils.Plg.mtx_ins[1]}")
        cmds.delete(wrist_local_object)
        
        # BM_wristIK
        utils.connect_attr(f"{MM_wristBase}{utils.Plg.mtx_sum_plg}", f"{BM_wristIk}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{MM_armRootIk}{utils.Plg.mtx_sum_plg}", f"{BM_wristIk}{utils.Plg.target_mtx[0]}")
        utils.connect_attr(f"{ik_ctrl_target}.Follow_Arm", f"{BM_wristIk}.target[0].translateWeight")
        utils.connect_attr(f"{ik_ctrl_target}.Follow_Arm", f"{BM_wristIk}.target[0].rotateWeight")
        utils.connect_attr(f"{BM_wristIk}{utils.Plg.out_mtx_plg}", f"{ik_ctrl_target}{utils.Plg.opm_plg}")
        
    
    def wire_ctrl_ik_elbow(self, inputs_grp, ik_ctrl_list, ik_spine_top_ctrl):
        '''
        # Description:
            Positions & wires the follow swapping of the pv ctrl too
        # Attributes:
            inputs_grp (string): Group for input data for this module.
            ik_ctrl_list (list): Contains 4 ik control names.
            ik_spine_top_ctrl (string): Name of SPINE modules top ik control.
        # Returns: N/A 
        '''
        #establish the target control:
        ik_ctrl_target = ik_ctrl_list[2]

        # Add follow attr to fk shoulder ctrl
        utils.add_locked_attrib(ik_ctrl_target, ["Follows"])
        utils.add_float_attrib(ik_ctrl_target, ["Follow_Spine_top"], [0.0, 1.0], True)
        utils.add_float_attrib(ik_ctrl_target, ["Follow_Wrist_ik"], [0.0, 1.0], True)
        # cr blendMatrix seyup to feed to fk ctrl/rigJnt shoulder. 
        MM_pvBase = f"MM_ikPv_{self.mdl_nm}_base_{self.unique_id}_{self.side}"
        MM_pvSpineTop = f"MM_ikPv_{self.mdl_nm}_spineTopHook_{self.unique_id}_{self.side}"
        MM_pvWristIk = f"MM_ikPv_{self.mdl_nm}_wristIkCtrl_{self.unique_id}_{self.side}"
        BM_pv = f"BM_ikPv_{self.mdl_nm}_blend_{self.unique_id}_{self.side}"
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_pvBase)
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_pvSpineTop)
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_pvWristIk)
        utils.cr_node_if_not_exists(1, 'blendMatrix', BM_pv, {
            "target[0].scaleWeight":0, 
            "target[0].shearWeight":0})
        # MM_pvBase
        utils.set_transformation_matrix(list(self.ik_pos_dict.values())[2], list(self.ik_rot_dict.values())[2], f"{MM_pvBase}{utils.Plg.mtx_ins[0]}")         
        utils.connect_attr(f"{inputs_grp}.base_mtx", f"{MM_pvBase}{utils.Plg.mtx_ins[1]}")
        
        # MM_pvSpineTop
        pvSpine_local_object = f"temp_loc_Spine{ik_ctrl_target}"
        cmds.spaceLocator(n=pvSpine_local_object)
        cmds.xform(pvSpine_local_object, t=self.ik_pos_dict[ik_ctrl_target], ws=1)
        cmds.xform(pvSpine_local_object, rotation=self.ik_rot_dict[ik_ctrl_target], ws=1)
        cmds.parent(pvSpine_local_object, ik_spine_top_ctrl)
        get_spine_localM = cmds.getAttr(f"{pvSpine_local_object}{utils.Plg.wld_mtx_plg}")
        cmds.setAttr(f"{MM_pvSpineTop}{utils.Plg.mtx_ins[0]}", *get_spine_localM, type="matrix") 
        utils.connect_attr(f"{inputs_grp}.hook_mtx", f"{MM_pvSpineTop}{utils.Plg.mtx_ins[1]}")
        cmds.delete(pvSpine_local_object)
        
        # MM_pvWristIk
        pvWrist_local_object = f"temp_loc_pvWrist{ik_ctrl_target}"
        cmds.spaceLocator(n=pvWrist_local_object)
        cmds.xform(pvWrist_local_object, t=self.ik_pos_dict[ik_ctrl_target], ws=1)
        cmds.xform(pvWrist_local_object, rotation=self.ik_rot_dict[ik_ctrl_target], ws=1)
        cmds.parent(pvWrist_local_object, ik_ctrl_list[-1])
        get_wrist_localM = cmds.getAttr(f"{pvWrist_local_object}.matrix")
        cmds.setAttr(f"{MM_pvWristIk}{utils.Plg.mtx_ins[0]}", *get_wrist_localM, type="matrix")    
        utils.connect_attr(f"{ik_ctrl_list[-1]}{utils.Plg.wld_mtx_plg}", f"{MM_pvWristIk}{utils.Plg.mtx_ins[1]}")
        cmds.delete(pvWrist_local_object)

        # BM_pv
        utils.connect_attr(f"{MM_pvBase}{utils.Plg.mtx_sum_plg}", f"{BM_pv}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{MM_pvSpineTop}{utils.Plg.mtx_sum_plg}", f"{BM_pv}{utils.Plg.target_mtx[0]}")
        utils.connect_attr(f"{MM_pvWristIk}{utils.Plg.mtx_sum_plg}", f"{BM_pv}{utils.Plg.target_mtx[1]}")
            # space swap atribs
        utils.connect_attr(f"{ik_ctrl_target}.Follow_Spine_top", f"{BM_pv}.target[0].translateWeight")
        utils.connect_attr(f"{ik_ctrl_target}.Follow_Spine_top", f"{BM_pv}.target[0].rotateWeight")
        utils.connect_attr(f"{ik_ctrl_target}.Follow_Wrist_ik", f"{BM_pv}.target[1].translateWeight")
        utils.connect_attr(f"{ik_ctrl_target}.Follow_Wrist_ik", f"{BM_pv}.target[1].rotateWeight")
            # output plug
        utils.connect_attr(f"{BM_pv}{utils.Plg.out_mtx_plg}", f"{ik_ctrl_target}{utils.Plg.opm_plg}")
        

    def cr_logic_curves(self, pref):
        '''
        # Description:
            Creates a logic curve, to be used for twisting & bending.
        # Attributes:
            pref (string): The name of this logic curve [upper/lower]
        # Returns:
            logic_curve (string): The logic curve created. 
        '''
        # 'psotions is irrrelavant becuase its pos will be determined by shaper ctrls.'
        logic_curve = f"crv_{self.mdl_nm}_{pref}_{self.unique_id}_{self.side}"
        cmds.curve(n=logic_curve, d=3, p=[[0.0, 0.0, 0.0], [5.0, 0.0, 0.0], [10.0, 0.0, 0.0], [15.0, 0.0, 0.0]])
        cmds.rebuildCurve(logic_curve, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=0, kt=0, s=1, d=3, tol=0.01)
        
        return logic_curve
    
    
    def logic_jnt_distances(self, fk_pos_dict):
        '''
        # Description:
            Need to store the distances of the the limb, to be used for PINNING!!!
        # Attributes:
            fk_pos_dict (dict): key=Name of fk controls, value=Positional data.
        # Returns:
            d_shld_wrist (string): distance of shoulder to wrist [whole limb]. 
            d_shld_elb (string): distance of shoulder to elbow [upper]. 
            d_elb_wrist (string): distance of elbow to wrist [lower].
        '''
        d_shld_wrist = utils.get_distance("shld_elb", list(fk_pos_dict.values())[0], list(fk_pos_dict.values())[2])
        d_shld_elb = utils.get_distance("shld_elb", list(fk_pos_dict.values())[0], list(fk_pos_dict.values())[1])
        d_elb_wrist = utils.get_distance("elb_wrist", list(fk_pos_dict.values())[1], list(fk_pos_dict.values())[2])
        
        print(f"d_shld_wrist = `{d_shld_wrist}`")
        print(f"d_shld_elb = `{d_shld_elb}`")
        print(f"d_elb_wrist = `{d_elb_wrist}`")

        return d_shld_wrist, d_shld_elb, d_elb_wrist


    def wire_ik_logic_elements(self, input_grp, logic_jnt_list, ik_ctrl_list):
        '''
        # Description:
            Create Ik_handle on the logic joints(Ik RPSolver on logic joints w/ pole vector.), 
            wire the pin arm setup, wire the ikfkStretch setup from pin setup, 
            wire into ik handle from ikfkstretch. skn_wrist drives Ik_handle.opm. 
        # Attributes:
            inputs_grp (string): Group for input data for this module.
            logic_jnt_list (list): list of arm logic joints. 
            ik_ctrl_list (list): Contains 4 ik control names.
        # Returns:
            bc_ikfk_stretch (utility): blendColors node returned so IKFK_Switch drives it.
            logic_hdl (string): logic Ik_handle name.
        '''
        # cr Ik_handle on the logic joints
        logic_hdl = f"hdl_{self.mdl_nm}_logic_{self.unique_id}_{self.side}" # hdl_bipedArm_0_L
        cmds.ikHandle( n=logic_hdl, sol="ikRPsolver", sj=logic_jnt_list[0], ee=logic_jnt_list[2], ccv=False, pcv=False)

        # add ik pv ctrl mtx data to Ik_handle OPM to drive it!
        mm_pv_ik_hdl = f"MM_hdlPv_{self.mdl_nm}_{self.unique_id}_{self.side}"
        pm_pv_ik_hdl = f"PM_hdlPv_{self.mdl_nm}_{self.unique_id}_{self.side}"
        utils.cr_node_if_not_exists(1, 'multMatrix', mm_pv_ik_hdl)
        utils.cr_node_if_not_exists(1, 'pickMatrix', pm_pv_ik_hdl, {"useRotate":0, "useScale":0, "useShear":0})
            # add opm from ik wrist ctrl to the mm_pv_ik_hdl
        utils.connect_attr(f"{ik_ctrl_list[-1]}{utils.Plg.wld_mtx_plg}", f"{mm_pv_ik_hdl}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{mm_pv_ik_hdl}{utils.Plg.mtx_sum_plg}", f"{pm_pv_ik_hdl}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{pm_pv_ik_hdl}{utils.Plg.out_mtx_plg}", f"{logic_hdl}{utils.Plg.opm_plg}")
            # zero out the hdl attr
        for axis in ["X", "Y", "Z"]:
            cmds.setAttr(f"{logic_hdl}.translate{axis}", 0, lock=1)
            cmds.setAttr(f"{logic_hdl}.rotate{axis}", 0, lock=1)

        # Pin arm >drives> ik logic joints stretch. 
        # ik logic joints stretch >drives> Ik_handle.poleVector plug
        utils.add_locked_attrib(ik_ctrl_list[2], ["Attributes"])
        utils.add_float_attrib(ik_ctrl_list[2], ["Pin_Arm"], [0.0, 1.0], True)

        db_shld_wrist = f"DB_ik_{self.mdl_nm}_{self.unique_id}_{self.side}"
        db_shld_elb = f"DB_ikUpper_{self.mdl_nm}_{self.unique_id}_{self.side}"
        db_elb_wrist = f"DB_ikLower_{self.mdl_nm}_{self.unique_id}_{self.side}"
        fm_global = f"FM_byGlobal_{self.mdl_nm}_{self.unique_id}_{self.side}"
        fm_max = f"FM_max_{self.mdl_nm}_{self.unique_id}_{self.side}"
        fm_upPercent_div = f"FM_upPercentageDiv_{self.mdl_nm}_{self.unique_id}_{self.side}"
        fm_upPercentTotal_mult = f"FM_upPercentageTotalMult_{self.mdl_nm}_{self.unique_id}_{self.side}"
        fm_lowPercent_div = f"FM_lowPercentageDiv_{self.mdl_nm}_{self.unique_id}_{self.side}"
        fm_lowPercentTotal_mult = f"FM_lowPercentageTotalMult_{self.mdl_nm}_{self.unique_id}_{self.side}"
        bc_pin_limb = f"BC_pin_{self.mdl_nm}_{self.unique_id}_{self.side}"
        for db_name in [db_shld_wrist, db_shld_elb, db_elb_wrist]:
            utils.cr_node_if_not_exists(1, "distanceBetween", db_name)
        utils.cr_node_if_not_exists(1, "floatMath", fm_max, {"operation":5})
        for fm_div_name in [fm_upPercent_div, fm_lowPercent_div]:
            utils.cr_node_if_not_exists(1, "floatMath", fm_div_name, {"operation":3})
        for fm_mult_name in [fm_global, fm_upPercentTotal_mult, fm_lowPercentTotal_mult]:
            utils.cr_node_if_not_exists(1, "floatMath", fm_mult_name, {"operation":2})
        utils.cr_node_if_not_exists(1, "blendColors", bc_pin_limb)

            # db_shld_wrist > max
        utils.connect_attr(f"{ik_ctrl_list[1]}{utils.Plg.wld_mtx_plg}", f"{db_shld_wrist}{utils.Plg.inMatrixs[1]}")
        utils.connect_attr(f"{ik_ctrl_list[-1]}{utils.Plg.wld_mtx_plg}", f"{db_shld_wrist}{utils.Plg.inMatrixs[2]}")
        utils.connect_attr(f"{db_shld_wrist}{utils.Plg.distance_plg}", f"{fm_max}{utils.Plg.flt_A}")
        
            # db_shld_elb > bc.color1R
        utils.connect_attr(f"{ik_ctrl_list[1]}{utils.Plg.wld_mtx_plg}", f"{db_shld_elb}{utils.Plg.inMatrixs[1]}")
        utils.connect_attr(f"{ik_ctrl_list[2]}{utils.Plg.wld_mtx_plg}", f"{db_shld_elb}{utils.Plg.inMatrixs[2]}")
        utils.connect_attr(f"{db_shld_elb}{utils.Plg.distance_plg}", f"{bc_pin_limb}{utils.Plg.color1_plg[0]}")
            # db_elb_wrist > bc.color1G
        utils.connect_attr(f"{ik_ctrl_list[2]}{utils.Plg.wld_mtx_plg}", f"{db_elb_wrist}{utils.Plg.inMatrixs[1]}")
        utils.connect_attr(f"{ik_ctrl_list[-1]}{utils.Plg.wld_mtx_plg}", f"{db_elb_wrist}{utils.Plg.inMatrixs[2]}")
        utils.connect_attr(f"{db_elb_wrist}{utils.Plg.distance_plg}", f"{bc_pin_limb}{utils.Plg.color1_plg[1]}")

            # > fm_global > fm_max.flt_B
        cmds.setAttr(f"{fm_global}{utils.Plg.flt_A}", self.d_shld_wrist)
        utils.connect_attr(f"{input_grp}.{self.global_scale_attr}", f"{fm_global}{utils.Plg.flt_B}")
        utils.connect_attr(f"{fm_global}{utils.Plg.out_flt}", f"{fm_max}{utils.Plg.flt_B}")

            # fm_upPercent_div > fm_upPercentTotal_mult.flt_A
        cmds.setAttr(f"{fm_upPercent_div}{utils.Plg.flt_A}", self.d_shld_elb)
        cmds.setAttr(f"{fm_upPercent_div}{utils.Plg.flt_B}", self.d_shld_wrist)
        utils.connect_attr(f"{fm_upPercent_div}{utils.Plg.out_flt}", f"{fm_upPercentTotal_mult}{utils.Plg.flt_A}")
            # fm_lowPercent_div > fm_lowPercentTotal_mult.flt_A
        cmds.setAttr(f"{fm_lowPercent_div}{utils.Plg.flt_A}", self.d_elb_wrist)
        cmds.setAttr(f"{fm_lowPercent_div}{utils.Plg.flt_B}", self.d_shld_wrist)
        utils.connect_attr(f"{fm_lowPercent_div}{utils.Plg.out_flt}", f"{fm_lowPercentTotal_mult}{utils.Plg.flt_A}")
        
            # fm_upPercentTotal_mult > bc.color2R
        utils.connect_attr(f"{fm_max}{utils.Plg.out_flt}", f"{fm_upPercentTotal_mult}{utils.Plg.flt_B}")
        utils.connect_attr(f"{fm_upPercentTotal_mult}{utils.Plg.out_flt}", f"{bc_pin_limb}{utils.Plg.color2_plg[0]}")
            # fm_lowPercentTotal_mult > bc.color2G
        utils.connect_attr(f"{fm_max}{utils.Plg.out_flt}", f"{fm_lowPercentTotal_mult}{utils.Plg.flt_B}")
        utils.connect_attr(f"{fm_lowPercentTotal_mult}{utils.Plg.out_flt}", f"{bc_pin_limb}{utils.Plg.color2_plg[1]}")
        
            # pv.Pin_Arm > bc.blender
        utils.connect_attr(f"{ik_ctrl_list[2]}.Pin_Arm", f"{bc_pin_limb}{utils.Plg.blndr_plg}")

        # Initalise ik stretch logic
        fm_up_fkStretch = f"FM_upFkStretchMult_{self.mdl_nm}_{self.unique_id}_{self.side}"
        fm_low_fkStretch = f"FM_lowFkStretchMult_{self.mdl_nm}_{self.unique_id}_{self.side}"
        fm_up_fkStretchGlobal = f"FM_upFkStretchGlobalMult_{self.mdl_nm}_{self.unique_id}_{self.side}"
        fm_low_fkStretchGlobal = f"FM_lowFkStretchGlobalMult_{self.mdl_nm}_{self.unique_id}_{self.side}"
        bc_ikfk_stretch = f"BC_ikfkStretch_{self.mdl_nm}_{self.unique_id}_{self.side}"
        for fm_mult_nm in [fm_up_fkStretchGlobal, fm_low_fkStretchGlobal]:
            utils.cr_node_if_not_exists(1, "floatMath", fm_mult_nm, {"operation":2})
        utils.cr_node_if_not_exists(1, "blendColors", bc_ikfk_stretch, {"blender":1})
        
            # fm_up/low_fkStretch.out_flt > fm_up/low_global.flt_A
        utils.connect_attr(f"{fm_up_fkStretch}{utils.Plg.out_flt}", f"{fm_up_fkStretchGlobal}{utils.Plg.flt_A}")
        utils.connect_attr(f"{fm_low_fkStretch}{utils.Plg.out_flt}", f"{fm_low_fkStretchGlobal}{utils.Plg.flt_A}")
        
            # input_grp.globalScale > fm_up/low_global.flt_B
        utils.connect_attr(f"{input_grp}.{self.global_scale_attr}", f"{fm_up_fkStretchGlobal}{utils.Plg.flt_B}")
        utils.connect_attr(f"{input_grp}.{self.global_scale_attr}", f"{fm_low_fkStretchGlobal}{utils.Plg.flt_B}")
        
            # bc_pin_arm > bc_ikfk_stretch.color2
        utils.connect_attr(f"{bc_pin_limb}{utils.Plg.out_letter[0]}", f"{bc_ikfk_stretch}{utils.Plg.color1_plg[0]}")
        utils.connect_attr(f"{bc_pin_limb}{utils.Plg.out_letter[1]}", f"{bc_ikfk_stretch}{utils.Plg.color1_plg[1]}")
        
            # fm_up/low_global > bc_ikfk_stretch.color1#
        utils.connect_attr(f"{fm_up_fkStretchGlobal}{utils.Plg.out_flt}", f"{bc_ikfk_stretch}{utils.Plg.color2_plg[0]}")
        utils.connect_attr(f"{fm_low_fkStretchGlobal}{utils.Plg.out_flt}", f"{bc_ikfk_stretch}{utils.Plg.color2_plg[1]}")
        
        # Plug into the logic joints!
        md_ikfk_stretch = f"MD_ikfkStretch_{self.mdl_nm}_{self.unique_id}_{self.side}"
        utils.cr_node_if_not_exists(1, "multiplyDivide", md_ikfk_stretch, {"operation":2})
            # bc_ikfk_stretch.outColor# > md_ikfk_stretch.input1#
        utils.connect_attr(f"{bc_ikfk_stretch}{utils.Plg.out_letter[0]}", f"{md_ikfk_stretch}{utils.Plg.input1_val[0]}")
        utils.connect_attr(f"{bc_ikfk_stretch}{utils.Plg.out_letter[1]}", f"{md_ikfk_stretch}{utils.Plg.input1_val[1]}")
            # input_grp.globalScale > md_ikfk_stretch.input2#
        utils.connect_attr(f"{input_grp}.{self.global_scale_attr}", f"{md_ikfk_stretch}{utils.Plg.input2_val[0]}")
        utils.connect_attr(f"{input_grp}.{self.global_scale_attr}", f"{md_ikfk_stretch}{utils.Plg.input2_val[1]}")
            # md_ikfk_stretch.out# > logic_jnt.translate prim axis
        utils.connect_attr(f"{md_ikfk_stretch}{utils.Plg.out_axis[0]}", f"{logic_jnt_list[1]}.translate{self.prim_axis}")
        utils.connect_attr(f"{md_ikfk_stretch}{utils.Plg.out_axis[1]}", f"{logic_jnt_list[2]}.translate{self.prim_axis}")

        # wire to the ikHandle.poleVector plug
        pMM_shld = f"PMM_shld_{self.mdl_nm}_{self.unique_id}_{self.side}"
        cM_shld = f"CM_shld_{self.mdl_nm}_{self.unique_id}_{self.side}"
        iM_shld = f"IM_shld_{self.mdl_nm}_{self.unique_id}_{self.side}"
        mm_pv = f"MM_poleVector_{self.mdl_nm}_{self.unique_id}_{self.side}"
        dm_pv = f"DM_poleVector_{self.mdl_nm}_{self.unique_id}_{self.side}"
        utils.cr_node_if_not_exists(1, "pointMatrixMult", pMM_shld)
        utils.cr_node_if_not_exists(0, "composeMatrix", cM_shld)
        utils.cr_node_if_not_exists(1, "inverseMatrix", iM_shld)
        utils.cr_node_if_not_exists(1, "multMatrix", mm_pv)
        utils.cr_node_if_not_exists(0, "decomposeMatrix", dm_pv)
            # > pMM_shld
        utils.connect_attr(f"{logic_jnt_list[0]}{utils.Plg.prt_plg}", f"{pMM_shld}.inMatrix")
        utils.connect_attr(f"{logic_jnt_list[0]}.translate", f"{pMM_shld}.inPoint")
            # > compM_shld
        utils.connect_attr(f"{pMM_shld}{utils.Plg.output_plg}", f"{cM_shld}{utils.Plg.inputT_plug}")
            # > iM_shld
        utils.connect_attr(f"{cM_shld}{utils.Plg.out_mtx_plg}", f"{iM_shld}{utils.Plg.inp_mtx_plg}")
            # > mm_pv
        utils.connect_attr(f"{ik_ctrl_list[2]}{utils.Plg.wld_mtx_plg}", f"{mm_pv}{utils.Plg.mtx_ins[0]}")
        utils.connect_attr(f"{iM_shld}{utils.Plg.out_mtx_plg}", f"{mm_pv}{utils.Plg.mtx_ins[1]}")
            # > mm_pv
        utils.connect_attr(f"{mm_pv}{utils.Plg.mtx_sum_plg}", f"{dm_pv}{utils.Plg.inp_mtx_plg}")
            # > hdl.poleVector
        utils.connect_attr(f"{dm_pv}{utils.Plg.outT_plug}", f"{logic_hdl}.poleVector")
        
        return bc_ikfk_stretch, logic_hdl
        

    def group_logic_elements(self, logic_jnt_list, logic_hdl, logic_curve_list):
        '''
        # Description:
            Creates logic group for this module.
        # Attributes:
            logic_jnt_list (list): logic joints.
            logic_hdl (string): Logic ik handle.
            logic_curve_list (list): twist logic curves list.
        # Returns:
            logic_grp (string): logic group.
        '''
        logic_grp = f"grp_logic_{self.mdl_nm}_{self.unique_id}_{self.side}"
        utils.cr_node_if_not_exists(0, "transform", logic_grp)
        cmds.parent(logic_jnt_list[0], logic_hdl, logic_grp)
        for crv in logic_curve_list: 
            cmds.parent(crv, logic_grp)

        return logic_grp


    def wire_jnt_skn_wrist(self, skn_jnt_wrist, logic_jnt_list, fk_ctrl_list, ik_ctrl_list):
        '''
        # Description:
            Drive the 'skn_jnt_wrist', blending between 'ik wrist ctrl' & 'fk_wrist ctrl'.
            adding special follow ikfk attributes on the skn joint that drive the blending!  
        # Attributes:
            skn_jnt_wrist (string): Name of the wrist skin joint.
            logic_jnt_list (list): list of arm logic joints. 
            ik_ctrl_list (list): Contains 4 ik control names.
        # Returns:
            skn_jnt_wrist_ik_plg (plug): ik follow plug SO the 
                                        ctrl_settings.IKFK_Switch drives the blending.
            skn_jnt_wrist_fk_plg (plug): fk follow plug SO the 
                                        ctrl_settings.IKFK_Switch drives the blending 
        '''
        utils.add_locked_attrib(skn_jnt_wrist, ["Follows"])
        fk_attr = f"Follow_FK_Wrist_{self.mdl_nm}_{self.unique_id}_Rot"
        ik_attr = f"Follow_IK_Wrist_{self.mdl_nm}_{self.unique_id}"
        skn_jnt_wrist_ik_plg = f"{skn_jnt_wrist}.{ik_attr}"
        skn_jnt_wrist_fk_plg = f"{skn_jnt_wrist}.{fk_attr}"
        
        utils.add_float_attrib(skn_jnt_wrist, [fk_attr], [0.0, 1.0], True)
        utils.add_float_attrib(skn_jnt_wrist, [ik_attr], [0.0, 1.0], True)
        cmds.setAttr(skn_jnt_wrist_fk_plg, 0)
        cmds.setAttr(skn_jnt_wrist_ik_plg, 1)

        mm_logic_wrist = f"mm_{logic_jnt_list[-1]}"
        mm_ctrlFk_wrist = f"mm_{fk_ctrl_list[-1]}"
        mm_ctrlIk_wrist = f"mm_{ik_ctrl_list[-1]}"
        bm_skn_wrist = f"bm_{skn_jnt_wrist}"
        for mm_name in [mm_logic_wrist, mm_ctrlFk_wrist, mm_ctrlIk_wrist]:
            utils.cr_node_if_not_exists(1, 'multMatrix', mm_name)
        utils.cr_node_if_not_exists(1, 'blendMatrix', bm_skn_wrist, 
                                    {"target[0].scaleWeight":0,
                                     "target[0].translateWeight":0, 
                                     "target[0].shearWeight":0,
                                     "target[1].scaleWeight":0, 
                                     "target[1].shearWeight":0})
        # > mm_logic_wrist
        utils.set_transformation_matrix([0.0, 0.0, 0.0], [0.0, 0.0, 0.0], f"{mm_logic_wrist}{utils.Plg.mtx_ins[0]}")         
        utils.connect_attr(f"{logic_jnt_list[-1]}{utils.Plg.wld_mtx_plg}", f"{mm_logic_wrist}{utils.Plg.mtx_ins[1]}")

        # > mm_ctrlFk_wrist
        utils.set_transformation_matrix([0.0, 0.0, 0.0], [0.0, 0.0, 0.0], f"{mm_ctrlFk_wrist}{utils.Plg.mtx_ins[0]}")         
        utils.connect_attr(f"{fk_ctrl_list[-1]}{utils.Plg.wld_mtx_plg}", f"{mm_ctrlFk_wrist}{utils.Plg.mtx_ins[1]}")

        # > mm_ctrlIk_wrist
        utils.set_transformation_matrix([0.0, 0.0, 0.0], [0.0, 0.0, 0.0], f"{mm_ctrlIk_wrist}{utils.Plg.mtx_ins[0]}")         
        utils.connect_attr(f"{ik_ctrl_list[-1]}{utils.Plg.wld_mtx_plg}", f"{mm_ctrlIk_wrist}{utils.Plg.mtx_ins[1]}")

        #> bm_skn_wrist
        utils.connect_attr(f"{mm_logic_wrist}{utils.Plg.mtx_sum_plg}", f"{bm_skn_wrist}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{mm_ctrlFk_wrist}{utils.Plg.mtx_sum_plg}", f"{bm_skn_wrist}{utils.Plg.target_mtx[0]}")
        utils.connect_attr(f"{mm_ctrlIk_wrist}{utils.Plg.mtx_sum_plg}", f"{bm_skn_wrist}{utils.Plg.target_mtx[1]}")
        utils.connect_attr(skn_jnt_wrist_fk_plg, f"{bm_skn_wrist}.target[0].rotateWeight")
        utils.connect_attr(skn_jnt_wrist_ik_plg, f"{bm_skn_wrist}.target[1].translateWeight")
        utils.connect_attr(skn_jnt_wrist_ik_plg, f"{bm_skn_wrist}.target[1].rotateWeight")
        utils.connect_attr(f"{bm_skn_wrist}{utils.Plg.out_mtx_plg}", f"{skn_jnt_wrist}{utils.Plg.opm_plg}")
        
        return skn_jnt_wrist_ik_plg, skn_jnt_wrist_fk_plg


    def cr_mdl_setting_ctrl(self, skn_jnt_wrist, ik_ctrl_list):
        '''
        # Description:
            Create the Settings Control w/ all it's attributes!
        # Attributes: 
            skn_jnt_wrist (string): Name of the wrist skin joint.
            ik_ctrl_list (list): Contains 4 ik control names.
        # Returns:
            mdl_settings_ctrl (string): Name of the settings control.
            ikfk_plug (plug): 'ikfk_switch' control attribute plug for consitancy.
            stretch_volume_plug (plug): 'stretch_volume' control attribute plug for consitancy.
            shaper_plug (plug): 'shaper_visibility' control attribute plug for consitancy.
        '''
        ''' TEMPORARY -> ADD settings control to this module's database data! '''
        # duplicate the ik_shoudler ctrl when it is made, before it's posisioned
        mdl_settings_ctrl = f"ctrl_settings_{self.mdl_nm}_{self.unique_id}_{self.side}"
        cmds.duplicate(ik_ctrl_list[1], n=mdl_settings_ctrl, rc=1)
        # Colour the settings ctrl a pale version of the current colour. 
        if self.side == "L":
            utils.colour_object(mdl_settings_ctrl, 4)
        elif self.side == "R":
            utils.colour_object(mdl_settings_ctrl, 18)
        cmds.parent(mdl_settings_ctrl, f"grp_ctrls_{self.mdl_nm}_{self.unique_id}_{self.side}")
        
        ikfk_switch_attr = "IK_FK_Switch"
        auto_stretch_attr = "Stretch_Volume"
        shaper_attr = "Vis_Shapers"
        utils.add_locked_attrib(mdl_settings_ctrl, ["Attributes"])
        utils.add_float_attrib(mdl_settings_ctrl, [f"{ikfk_switch_attr}", f"{auto_stretch_attr}"], [0.0, 1.0], True)
        # utils.add_float_attrib(root_ctrl, [f"Auto_Stretch"], [0.0, 1.0], True)

        utils.add_locked_attrib(mdl_settings_ctrl, ["Visibility"])
        utils.add_float_attrib(mdl_settings_ctrl, [f"{shaper_attr}"], [0.0, 1.0], True)

        # wire 'skn_jnt_wrist' to  'mdl_settings_ctrl.OPM'
        mm_settings = f"MM_{mdl_settings_ctrl}"
        utils.cr_node_if_not_exists(1, 'multMatrix', mm_settings)
        utils.connect_attr(f"{skn_jnt_wrist}{utils.Plg.wld_mtx_plg}", f"{mm_settings}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{mm_settings}{utils.Plg.mtx_sum_plg}", f"{mdl_settings_ctrl}{utils.Plg.opm_plg}")
        
        ikfk_plug = f"{mdl_settings_ctrl}.{ikfk_switch_attr}"
        stretch_volume_plug = f"{mdl_settings_ctrl}.{auto_stretch_attr}"
        shaper_plug = f"{mdl_settings_ctrl}.{shaper_attr}"

        return mdl_settings_ctrl, ikfk_plug, stretch_volume_plug, shaper_plug
        
        
    def wire_IKFK_switch(self, skn_jnt_wrist_ik_plg, skn_jnt_wrist_fk_plg, 
                         mdl_settings_ctrl, ikfk_plug, 
                         bc_ikfkStretch, logic_hdl,
                         fk_ctrl_grp, ik_ctrl_grp):
        '''
        # Description:
            Wire the connections for all ikfk switch attributes:
            > reverse.inputX > .outputX -> skn_jnt_wrist.{f"Follow_FK_Wrist_{self.mdl_nm}_{self.unique_id}_Rot"}
            > skn_jnt_wrist.{f"Follow_IK_Wrist_{self.mdl_nm}_{self.unique_id}"}
            > bc_ikfkStretch.blender
            > hdl.ik_blend
        # Attributes:
            skn_jnt_wrist_ik_plg (plug): ik follow plug SO the 
                                        ctrl_settings.IKFK_Switch drives the blending.
            skn_jnt_wrist_fk_plg (plug): fk follow plug SO the 
                                        ctrl_settings.IKFK_Switch drives the blending 
            mdl_settings_ctrl (string): Name of the settings control.
            ikfk_plug (plug): 'ikfk_switch' control attribute plug for consitancy.
            bc_ikfk_stretch (utility): blendColors node returned so IKFK_Switch drives it.
            logic_hdl (string): logic Ik_handle name.
            fk_ctrl_grp (string): Name of fk ctrl grp.
            ik_ctrl_grp (string): Name of ik ctrl grp.
        # Returns: N/A
        '''
        # cr rev node
        rev_ikfk = f"rev_{mdl_settings_ctrl}"
        utils.cr_node_if_not_exists(1, 'reverse', rev_ikfk)
        # > skn_jnt_wrist.inputX
        utils.connect_attr(ikfk_plug, f"{rev_ikfk}.inputX")
        utils.connect_attr(f"{rev_ikfk}{utils.Plg.out_axis[0]}", skn_jnt_wrist_fk_plg)
        utils.connect_attr(ikfk_plug, skn_jnt_wrist_ik_plg)

        # > bc_ikfkStretch.blender
        utils.connect_attr(ikfk_plug, f"{bc_ikfkStretch}{utils.Plg.blndr_plg}")
        
        # > hdl.ik_blend
        utils.connect_attr(ikfk_plug, f"{logic_hdl}.ikBlend")

        # > ctrl ik/fk groups.visibility
        utils.connect_attr(f"{rev_ikfk}{utils.Plg.out_axis[0]}", f"{fk_ctrl_grp}{utils.Plg.vis_plg}")
        utils.connect_attr(ikfk_plug, f"{ik_ctrl_grp}{utils.Plg.vis_plg}")


    def wire_shaper_ctrls(self, shaper_ctrl_list, logic_jnt_list, ik_ctrl_list, 
                          shaper_plug, shaper_ctrl_grp):
        '''
        # Description:
            Wire the connections for all shaper controls so they are positioned. 
            'shaper_main' control drives all other shaper controls. Positons are 
            all sorted with matrix's and DO NOT need pos or rot data for them.
        # Attributes:
            shaper_ctrl_list (list) Contains 4 shaper contol names. 
            logic_jnt_list (list): list of arm logic joints. 
            ik_ctrl_list (list): Contains 4 ik control names.
            shaper_plug (plug): 'shaper_visibility' control attribute plug for consitancy.
            shaper_ctrl_grp (string): Name of shaper ctrl grp.
        # Returns: N/A
        '''
        # add ikfk_switch attr to 
        # gather each control into variables to maje sure i'm working on the right 
        # control becuase the order isn't consitant atm
        for shaper in shaper_ctrl_list:
            if "main" in shaper:
                shaper_main = shaper
            elif "upper" in shaper:
                shaper_upper = shaper
            elif "middle" in shaper:
                shaper_mid = shaper
            elif "lower" in shaper:
                shaper_lower = shaper
        new_shaper_ctrl_list = [shaper_main, shaper_upper, shaper_mid, shaper_lower]

        # > shaper_main.opm
        mm_shaper_main = f"MM_{shaper_main}"
        utils.cr_node_if_not_exists(1, 'multMatrix', mm_shaper_main)
        utils.connect_attr(f"{logic_jnt_list[1]}{utils.Plg.wld_mtx_plg}", f"{mm_shaper_main}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{mm_shaper_main}{utils.Plg.mtx_sum_plg}", f"{shaper_main}{utils.Plg.opm_plg}")
        
        # > shaper_middle.opm
        mm_shaper_mid = f"MM_{shaper_mid}"
        utils.cr_node_if_not_exists(1, 'multMatrix', mm_shaper_mid)
        utils.connect_attr(f"{shaper_main}{utils.Plg.wld_mtx_plg}", f"{mm_shaper_mid}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{mm_shaper_mid}{utils.Plg.mtx_sum_plg}", f"{shaper_mid}{utils.Plg.opm_plg}")

        # > shaper_upper.opm
        bm_shaper_upper = f"BM_{shaper_upper}"
        am_shaper_upper = f"AM_{shaper_upper}"
        utils.cr_node_if_not_exists(0, 'blendMatrix', bm_shaper_upper, 
                                    {"target[0].scaleWeight":0,
                                     "target[0].translateWeight":0.5,
                                     "target[0].rotateWeight":0, 
                                     "target[0].shearWeight":0})
        utils.cr_node_if_not_exists(0, 'aimMatrix', am_shaper_upper)
            # ik_shoulder.opm > bm_shaper_upper.inputMatrix plug
        utils.connect_attr(f"{ik_ctrl_list[1]}{utils.Plg.wld_mtx_plg}", f"{bm_shaper_upper}{utils.Plg.inp_mtx_plg}")
            # shaper_main.opm > bm_shaper_upper.target[0].targetMatrix plug
        utils.connect_attr(f"{shaper_main}{utils.Plg.wld_mtx_plg}", f"{bm_shaper_upper}{utils.Plg.target_mtx[0]}")
            # bm_shaper_upper.outputMatrix > am_shaper_upper.inputMatrix plug
        utils.connect_attr(f"{bm_shaper_upper}{utils.Plg.out_mtx_plg}", f"{am_shaper_upper}{utils.Plg.inp_mtx_plg}")
            # shaper_main.opm > am_shaper_upper.primaryTargetMatrix plug
        utils.connect_attr(f"{shaper_main}{utils.Plg.wld_mtx_plg}", f"{am_shaper_upper}.primaryTargetMatrix")
            # am_shaper_upper.outputMatrix > shaper_upper.opm
        utils.connect_attr(f"{am_shaper_upper}{utils.Plg.out_mtx_plg}", f"{shaper_upper}{utils.Plg.opm_plg}")

        # > shaper_lower.opm
        bm_shaper_lower = f"BM_{shaper_lower}"
        am_shaper_lower = f"AM_{shaper_lower}"
        utils.cr_node_if_not_exists(0, 'blendMatrix', bm_shaper_lower, 
                                    {"target[0].scaleWeight":0,
                                     "target[0].translateWeight":0.5,
                                     "target[0].rotateWeight":0, 
                                     "target[0].shearWeight":0})
        utils.cr_node_if_not_exists(0, 'aimMatrix', am_shaper_lower)
            # ik_shoulder.opm > bm_shaper_lower.inputMatrix plug
        utils.connect_attr(f"{shaper_main}{utils.Plg.wld_mtx_plg}", f"{bm_shaper_lower}{utils.Plg.inp_mtx_plg}")
            # shaper_main.opm > bm_shaper_lower.target[0].targetMatrix plug
        utils.connect_attr(f"{logic_jnt_list[-1]}{utils.Plg.wld_mtx_plg}", f"{bm_shaper_lower}{utils.Plg.target_mtx[0]}")
            # bm_shaper_lower.outputMatrix > am_shaper_lower.inputMatrix plug
        utils.connect_attr(f"{bm_shaper_lower}{utils.Plg.out_mtx_plg}", f"{am_shaper_lower}{utils.Plg.inp_mtx_plg}")
            # shaper_main.opm > am_shaper_lower.primaryTargetMatrix plug
        utils.connect_attr(f"{shaper_main}{utils.Plg.wld_mtx_plg}", f"{am_shaper_lower}.primaryTargetMatrix")
            # am_shaper_lower.outputMatrix > shaper_lower.opm
        utils.connect_attr(f"{am_shaper_lower}{utils.Plg.out_mtx_plg}", f"{shaper_lower}{utils.Plg.opm_plg}")

        # wire the visibility attr on ctrl_setting
        utils.connect_attr(shaper_plug, f"{shaper_ctrl_grp}{utils.Plg.vis_plg}")
        ''' TEMP below'''
        cmds.setAttr(shaper_plug, 1)


    def wire_shaper_ctrls_to_curves(self):
        '''
        TO DO:
            - Shaper controls drive the Curve's control points.
        '''


    def wire_skn_twist_joints_stretch(self):
        '''
        TO DO:
            - Wire curves to the twist skin joints.
            - Arm pinning.
            - This function is the Stretch connection. 
        '''


    def wire_skn_twist_joints_volume(self):
        '''
        TO DO:
            - Wire curves to the twist skin joints.
            - This function is the Volume preservation connection.
        '''
    
        
    def wire_ikfk_settings(self):
        '''
        TO DO:
            - Add attributes the ikfk switch / Auto squash / vis shapers
            - Wire these functionality's. 
        '''

    
    def parent_ik_ctrls_out(self, ik_ctrl_list):
        '''
        # Description:
            parent the 'ik clavicle & ik shoulder' controls to the parent ctrl grp 
            so 'they' don't get hidden with ikfk switch
        # Attributes:
            ik_ctrl_list (list): Contains 4 ik control names.
        # Returns: N/A
        '''
        cmds.parent(ik_ctrl_list[0], ik_ctrl_list[1], f"grp_ctrls_{self.mdl_nm}_{self.unique_id}_{self.side}")
        cmds.select(cl=1)


    def lock_ctrl_attributes(self, fk_ctrl_list):
        '''
        # Description:
            Lock an assortment of ctrls of the module to make it animator friendly.
            (For testing of controls toggle this function).
        # Attributes:
            fk_ctrl_list (list): Contains 3 fk control names.
        # Returns: N/A
        '''
        for ctrl in fk_ctrl_list:
            cmds.setAttr(f"{ctrl}.translateX", lock=1)
            cmds.setAttr(f"{ctrl}.translateY", lock=1)
            cmds.setAttr(f"{ctrl}.translateZ", lock=1)
#-----------------------

'''
'ex_external_plg_dict' is an important dictionary that should be intiilaised by 
a seprate script just used for creating attributes. In the same script this 
dctionary is sent to the databaase!
'''
ex_external_plg_dict = {
    "global_scale_grp":"grp_Outputs_root_0_M",
    "global_scale_attr":"globalScale",
    "base_plg_grp":"grp_Outputs_root_0_M",
    "base_plg_atr":"ctrl_root_centre_mtx",
    "hook_plg_grp":"grp_Outputs_spine_0_M", 
    "hook_plg_atr":"ctrl_spine_top_mtx"
    }
# Do I need 'skeleton_dict' arg?
ex_skeleton_dict = {
    "skel_pos":{
        "clavicle":[2.44448507146776, 154.57145295222426, 4.459872829725054], 
        "shoulder":[19.021108627319336, 152.5847778320312, -3.6705198287963885],
        "elbow":[51.95222091674805, 151.27154541015625, -7.411651611328125],
        "wrist":[82.27891540527344, 151.65419006347656, -0.65576171875]
    },
    "skel_rot":{
        "clavicle":[-3.0037333819801293, 25.96554559489243, -6.834187725057292],
        "shoulder":[-0.2577070326177839, 6.4761835670879035, -2.2836406890784096], 
        "elbow":[-0.15718070963992195, -12.557766678467543, 0.7228865771539283],
        "wrist":[-0.04691076638914411, -12.440289615750016, -3.1178613803887054]
    }
} 

ex_fk_dict = {
    "fk_pos":{
        'ctrl_fk_bipedArm_shoulder_0_L':[19.021108627319336, 152.5847778320312, -3.6705198287963885],
        'ctrl_fk_bipedArm_elbow_0_L':[51.95222091674805, 151.27154541015625, -7.411651611328125],
        'ctrl_fk_bipedArm_wrist_0_L':[82.27891540527344, 151.65419006347656, -0.65576171875]
        },
    "fk_rot":{
        'ctrl_fk_bipedArm_shoulder_0_L':[-0.2577070326177839, 6.4761835670879035, -2.2836406890784096], 
        'ctrl_fk_bipedArm_elbow_0_L':[-0.15718070963992195, -12.557766678467543, 0.7228865771539283],
        'ctrl_fk_bipedArm_wrist_0_L':[-0.04691076638914411, -12.440289615750016, -3.1178613803887054]
        }
    }
ex_ik_dict = {
    "ik_pos":{
        'ctrl_ik_bipedArm_clavicle_0_L':[2.44448507146776, 154.57145295222426, 4.459872829725054],
        'ctrl_ik_bipedArm_shoulder_0_L':[19.021108627319336, 152.5847778320312, -3.6705198287963885],
        'ctrl_ik_bipedArm_elbow_0_L':[53.17503418460073, 147.03618221256727, -34.37697986989994],#[53.20349106420788, 146.93758915899517, -35.0046944229159],
        'ctrl_ik_bipedArm_wrist_0_L':[82.27891540527344, 151.65419006347656, -0.65576171875]
        },
    "ik_rot":{
        'ctrl_ik_bipedArm_clavicle_0_L':[0.0, 0.0, 0.0], #
        'ctrl_ik_bipedArm_shoulder_0_L':[0.0, 0.0, 0.0], # 
        'ctrl_ik_bipedArm_elbow_0_L':[-72.84109068999213, 80.71528988472048, -73.89575036760148], # [-72.84121454033736, 80.71529613638319, -73.89587586207297],
        'ctrl_ik_bipedArm_wrist_0_L':[-0.04691076638914411, -12.440289615750016, -3.1178613803887054]
        }
    }

ex_shaper_dict = {

}

ArmSystem("bipedArm", ex_external_plg_dict, ex_skeleton_dict, ex_fk_dict, ex_ik_dict, "X")

pos = {"clavicle": [3.0937706746970637, 211.9463944293447, -3.981268190856912], 
 "shoulder": [47.19038675793399, 202.90135192871094, -8.067196952221522], 
 "elbow": [86.67167131661598, 202.90135192871094, -8.067196952221524], 
 "wrist": [122.01356659109904, 202.9013566591099, -8.067197667477195]}

rot = {"clavicle": [-1.062264791699132, 5.186453236323401, -11.591655208873357], 
       "shoulder": [0.0, 0.0, 0.0], 
       "elbow": [0.0, 0.0, 0.0], 
       "wrist": [0.0, 0.0, 0.0]}