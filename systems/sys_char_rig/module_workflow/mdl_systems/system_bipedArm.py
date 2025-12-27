
import importlib
import maya.cmds as cmds
import re

''' in 'main.py' set the directory of the four folders for this workflow '''
from systems.sys_char_rig.module_workflow.data_managers import module_data_manager

from utils import (
    utils
)
from systems.sys_char_rig import (
    cr_ctrl
)

importlib.reload(module_data_manager)
importlib.reload(utils)
importlib.reload(cr_ctrl)

class SystemBipedArm:
    def __init__(self, data_manager):
        '''
        Use type hint checking `variable:type = data` to be able to let VsCode 
        know about autocomplete for `ModuleDataManager` class so i can access 
        the correct variable names with `self.dm.#`

        Pass the data_manager instance to 'self.#' so it can be shared throughout 
        the class functions
        '''
        
        self.dm:module_data_manager.ModuleDataManager = data_manager 
        print("<- - ->")
        print(f"SystemBipedArm -> dat_manager = {data_manager}")
    
    # Phase 2 - Module-specific
    def cr_jnt_skn_start_end(self, ik_pos):
        '''
        # Description:
            Creates start & end skin joints which are intended to be driven by
            their respective control & drive the geometry with skincluster.
        # Arguments:
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
    

    def cr_logic_curves(self, pref, start_pos, end_pos):
        '''
        # Description:
            Creates a perfectly straight 3-degrees curve between two positions 
            ( by evenly spacing the intermediate control verts ). To be used for 
            twisting & bending.
        # Arguments:
            pref (string): The name of this logic curve [upper/lower]
        # Returns:
            logic_curve (string): The logic curve created. 
        '''
        # 
        # start_pos = [20.283844, 152.207993, -2.557748]
        # end_pos = [52.076378, 152.208282, -7.538624]
        logic_curve = f"crv_{self.dm.mdl_nm}_{pref}_{self.dm.unique_id}_{self.dm.side}"
        crv, cv_intermediate_pos_ls = utils.cr_straight_cubic_curve(logic_curve, start_pos, end_pos)
        cmds.select(cl=1)

        return logic_curve, cv_intermediate_pos_ls
    

    def cr_skn_twist_joint_chain(self, twist_name, logic_curve, start_pos, end_pos):
        '''
        TO DO: Test wether the twist joints should always be 6 or the number I calcualte?
        # Description:
           Creates a basic desired joint chain, naming, NO position data. Use 
           distance to provide a reasonable number of joints to put there, they 
           must be an even number!
           The chain will always be a straight chain, it's position is determined 
           by the 'ctrl_ik_bipedArm_shoulder_0_L'.  
           Naming convention = jnt_skn_bipedArm_upper#/lower#_0_L
        # Arguments:
            twist_name (string): Name of the twist chain (upper#/lower#).
            start_pos (list): Position data for start of the chain.
            end_pos (list): Position data for end of the chain.
        # Returns:
            skn_jnt_chain (list): The list of joints within the chain.
        
        * Below is how to automate the number of twist joints. 
        * Standard is 6 for.

        # need the number of joints. 
            # need the front & end position for the chain to span across.
            # cr temp locators, positon them there, & calculate the distance between them. 
            # distance/6 = number of joints(number MUST be EVEN , so round to the best one.)
        temp_start_locator = f"loc_{twist_name}_start_pos_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        temp_end_locator = f"loc_{twist_name}_end_pos_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        cmds.spaceLocator(n=temp_start_locator)
        cmds.spaceLocator(n=temp_end_locator)
        cmds.xform(temp_start_locator, t=start_pos, ws=True)
        cmds.xform(temp_end_locator, t=end_pos, ws=True)

        # cr distance between node & wire the locators!
        db_node = f"DB_{twist_name}_distance_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        divide_node = f"DIV_{twist_name}_output_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        utils.cr_node_if_not_exists(1, "distanceBetween", db_node)
        utils.cr_node_if_not_exists(1, "divide", divide_node, {"input2":6})
        utils.connect_attr(f"{temp_start_locator}{utils.Plg.wld_mtx_plg}", f"{db_node}{utils.Plg.inMatrixs[1]}")
        utils.connect_attr(f"{temp_end_locator}{utils.Plg.wld_mtx_plg}", f"{db_node}{utils.Plg.inMatrixs[2]}")
        utils.connect_attr(f"{db_node}{utils.Plg.distance_plg}", f"{divide_node}.input1")
        
        # get the raw number from the calculation.
        raw_number = cmds.getAttr(f"{divide_node}.output")
        print(f"Twist {twist_name}: raw_number = {raw_number}")
        
        # Now delete the temp data
        cmds.delete(temp_start_locator, temp_end_locator, db_node, divide_node)

        # jnt_num = utils.round_to_even(raw_number)
        '''
        jnt_num = 6
        print(f"Twist {twist_name}: jnt_num = {jnt_num}")

        jnt_chain_ls = []
        u_dict = {}
        prevJnt = ""
        rootJnt = "" # used for orientation in future maybe....
        for x in range(0, jnt_num):
            cmds.select(cl=1)
            jnt_nm = f"jnt_skn_{self.dm.mdl_nm}_{twist_name}{x}_{self.dm.unique_id}_{self.dm.side}"
            newJnts = cmds.joint(n=jnt_nm)
            jnt_chain_ls.append(jnt_nm)

            moPath = cmds.pathAnimation( newJnts, c=logic_curve, fractionMode=1 )
            cmds.cutKey( moPath + ".u", time=() )
            cmds.setAttr((moPath + ".u"), x * (1.0/(jnt_num-1)))
            u = cmds.getAttr(moPath + ".u")
            u_dict[newJnts] = u
            cmds.delete( newJnts + ".tx", icn=1 )
            cmds.delete( newJnts + ".ty", icn=1 )
            cmds.delete( newJnts + ".tz", icn=1 )
            cmds.delete(moPath)
            
            if x == 0:
                prevJnt = newJnts
                rootJnt = newJnts
                continue
            cmds.parent(newJnts, prevJnt)
            prevJnt = newJnts
            cmds.makeIdentity(jnt_nm, a=1, t=0, r=1, s=0, n=0, pn=1)
        
        # Orient the joints!
        cmds.joint(rootJnt, e=1, oj='xyz', secondaryAxisOrient='zdown', ch=1, zso=1 )
        cmds.joint(newJnts, e=1, oj='none', ch=1, zso=1)
        cmds.select(cl=1)

        return jnt_chain_ls
    

    def group_jnts_skn(self, skn_start_end_ls, skn_jnt_chain_ls):
        '''
        # Description:
            Creates joint group for this module.
        # Arguments:
            skn_start_end_ls (list): skin start and end oints.
            skn_jnt_chain (list): list of skin joint chain.
        # Returns:
            joint_grp (string): Joint group.
        '''
        joint_grp = f"grp_joints_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        utils.cr_node_if_not_exists(0, "transform", joint_grp)
        for skn in skn_start_end_ls:
            cmds.parent(skn, joint_grp)
        for skn in skn_jnt_chain_ls: 
            cmds.parent(skn[0], joint_grp)
        cmds.select(cl=1)

        return joint_grp
    

    def add_custom_input_attr(self, inputs_grp):
        '''
        # Description:
            Add module unique attributes to the input group.
        # Arguments:
            inputs_grp (string): Outputgrpup for this module.
        # Returns: N/A
        '''
        utils.add_float_attrib(inputs_grp, [f"Squash_Value"], [1.0, 1.0], False)
        cmds.setAttr(f"{inputs_grp}.Squash_Value", keyable=1, channelBox=1)
        cmds.setAttr(f"{inputs_grp}.Squash_Value", -0.5)


    def wire_hook_clav_armRt_setup(self, inputs_grp, ctrl_list, skn_jnt_clav, ik_pos_dict, ik_rot_dict):
        '''
        # Description:
            The 'clavicle control' drives the 'clavicle skn_joint' > which drives 
            the 'arm root control' which will then be the root of the rest of the 
            arm module: Both FK & IK follow it.  
        # Arguments:
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

    
    def cr_logic_rig_joints(self, fk_ctrl_list, fk_pos_dict, fk_rot_dict):
        '''
        # Description:
            Cr 3 logic rig joints. Used for both fk & ik systems.  
        # Arguments:
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
    

    def wire_fk_ctrl_stretch_setup(self, fk_ctrl_list, d_shld_elb, d_elb_wrist):
        '''
        # Description:
            - stretches the fk ctrl's by translating the control in front. So to 
            "stretch" fk_0, the fk_1 is translated away.
            - This also acts as the default translation position of the fk ctrls. 
        # Arguments:
            fk_ctrl_list (list): Contains 3 fk control names.
        # Returns: N/A
        '''
        for ctrl in fk_ctrl_list[:-1]:
            utils.add_locked_attrib(ctrl, ["Attributes"])
            utils.add_float_attrib(ctrl, ["Stretch"], [0.01, 999.0], True)
            cmds.setAttr(f"{ctrl}.Stretch", 1)
            
        fk_shld_stretch_distance = d_shld_elb
        fk_elbow_stretch_distance = d_elb_wrist
        print(f"--------")
        print(f"fk_shld_elb_stretch_distance = `{fk_shld_stretch_distance}`")
        print(f"--------")
        print(f"fk_elb_wrist_stretch_distance = `{fk_elbow_stretch_distance}`")
        print(f"--------")

        # shoulder stretch
        fm_shld_stretch_mult = f"FM_upFkStretchMult_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        fm_shld_stretch_sub = f"FM_upFkStretchSub_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        utils.cr_node_if_not_exists(1, "floatMath", fm_shld_stretch_mult, {"operation":2, "floatA":fk_shld_stretch_distance})
        utils.cr_node_if_not_exists(1, "floatMath", fm_shld_stretch_sub, {"operation":1, "floatB":fk_shld_stretch_distance})
        
        utils.connect_attr(f"{fk_ctrl_list[0]}.Stretch", f"{fm_shld_stretch_mult}{utils.Plg.flt_B}")
        utils.connect_attr(f"{fm_shld_stretch_mult}{utils.Plg.out_flt}", f"{fm_shld_stretch_sub}{utils.Plg.flt_A}")
        utils.connect_attr(f"{fm_shld_stretch_sub}{utils.Plg.out_flt}", f"{fk_ctrl_list[1]}.translate{self.dm.prim_axis}")
        
        # elbow stretch
        fm_elb_stretch_mult = f"FM_lowFkStretchMult_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        fm_elb_stretch_sub = f"FM_lowFkStretchSub_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        utils.cr_node_if_not_exists(1, "floatMath", fm_elb_stretch_mult, {"operation":2, "floatA":fk_elbow_stretch_distance})
        utils.cr_node_if_not_exists(1, "floatMath", fm_elb_stretch_sub, {"operation":1, "floatB":fk_elbow_stretch_distance})
        
        utils.connect_attr(f"{fk_ctrl_list[1]}.Stretch", f"{fm_elb_stretch_mult}{utils.Plg.flt_B}")
        utils.connect_attr(f"{fm_elb_stretch_mult}{utils.Plg.out_flt}", f"{fm_elb_stretch_sub}{utils.Plg.flt_A}")
        utils.connect_attr(f"{fm_elb_stretch_sub}{utils.Plg.out_flt}", f"{fk_ctrl_list[2]}.translate{self.dm.prim_axis}")
        

    def wire_fk_ctrl_to_logic_joint(self, blend_armRoot_node, fk_ctrl_list, logic_jnt_list):
        '''
        # Description:
            driving the logic joints:
                - parent logic joint is driven by arnRoot ctrl w/ 'blend_armRoot_node'
                - child logic joints are driven by fk ctrl's direct rotations.
        # Arguments:
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
        # Arguments:
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
        MM_wristBase = f"MM_{self.dm.mdl_nm}_ikWrist_armRootBase_{self.dm.unique_id}_{self.dm.side}"
        MM_armRootIk = f"MM_{self.dm.mdl_nm}_ikWrist_armRootCtrl_{self.dm.unique_id}_{self.dm.side}"
        BM_wristIk = f"BM_{self.dm.mdl_nm}_ikWrist_armRootBlend_{self.dm.unique_id}_{self.dm.side}"
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_wristBase)
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_armRootIk)
        utils.cr_node_if_not_exists(1, 'blendMatrix', BM_wristIk, 
                                    {"target[0].scaleWeight":0, 
                                     "target[0].shearWeight":0})
        
        # MM_Base
        utils.set_transformation_matrix(list(self.dm.ik_pos_dict.values())[-1], list(self.dm.ik_rot_dict.values())[-1], f"{MM_wristBase}{utils.Plg.mtx_ins[0]}")         
        utils.connect_attr(f"{inputs_grp}.base_mtx", f"{MM_wristBase}{utils.Plg.mtx_ins[1]}")        
            # Setting Rotation is involved!
        # MM_armRootIk
        wrist_local_object = f"temp_loc_{ik_ctrl_target}"
        cmds.spaceLocator(n=wrist_local_object)
        cmds.xform(wrist_local_object, t=self.dm.ik_pos_dict[ik_ctrl_target], ws=1)
        cmds.xform(wrist_local_object, rotation=self.dm.ik_rot_dict[ik_ctrl_target], ws=1)
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
        # Arguments:
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
        MM_pvBase = f"MM_ikPv_{self.dm.mdl_nm}_base_{self.dm.unique_id}_{self.dm.side}"
        MM_pvSpineTop = f"MM_ikPv_{self.dm.mdl_nm}_spineTopHook_{self.dm.unique_id}_{self.dm.side}"
        MM_pvWristIk = f"MM_ikPv_{self.dm.mdl_nm}_wristIkCtrl_{self.dm.unique_id}_{self.dm.side}"
        BM_pv = f"BM_ikPv_{self.dm.mdl_nm}_blend_{self.dm.unique_id}_{self.dm.side}"
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_pvBase)
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_pvSpineTop)
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_pvWristIk)
        utils.cr_node_if_not_exists(1, 'blendMatrix', BM_pv, {
            "target[0].scaleWeight":0, 
            "target[0].shearWeight":0})
        # MM_pvBase
        utils.set_transformation_matrix(list(self.dm.ik_pos_dict.values())[2], list(self.dm.ik_rot_dict.values())[2], f"{MM_pvBase}{utils.Plg.mtx_ins[0]}")         
        utils.connect_attr(f"{inputs_grp}.base_mtx", f"{MM_pvBase}{utils.Plg.mtx_ins[1]}")
        
        # MM_pvSpineTop
        pvSpine_local_object = f"temp_loc_Spine{ik_ctrl_target}"
        cmds.spaceLocator(n=pvSpine_local_object)
        cmds.xform(pvSpine_local_object, t=self.dm.ik_pos_dict[ik_ctrl_target], ws=1)
        cmds.xform(pvSpine_local_object, rotation=self.dm.ik_rot_dict[ik_ctrl_target], ws=1)
        cmds.parent(pvSpine_local_object, ik_spine_top_ctrl)
        get_spine_localM = cmds.getAttr(f"{pvSpine_local_object}{utils.Plg.wld_mtx_plg}")
        cmds.setAttr(f"{MM_pvSpineTop}{utils.Plg.mtx_ins[0]}", *get_spine_localM, type="matrix") 
        utils.connect_attr(f"{inputs_grp}.hook_mtx", f"{MM_pvSpineTop}{utils.Plg.mtx_ins[1]}")
        cmds.delete(pvSpine_local_object)
        
        # MM_pvWristIk
        pvWrist_local_object = f"temp_loc_pvWrist{ik_ctrl_target}"
        cmds.spaceLocator(n=pvWrist_local_object)
        cmds.xform(pvWrist_local_object, t=self.dm.ik_pos_dict[ik_ctrl_target], ws=1)
        cmds.xform(pvWrist_local_object, rotation=self.dm.ik_rot_dict[ik_ctrl_target], ws=1)
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
    
  
    def wire_ik_logic_elements(self, input_grp, logic_jnt_list, ik_ctrl_list, d_shld_wrist, d_shld_elb, d_elb_wrist):
        '''
        # Description:
            Create Ik_handle on the logic joints(Ik RPSolver on logic joints w/ pole vector.), 
            wire the pin arm setup, wire the ikfkStretch setup from pin setup, 
            wire into ik handle from ikfkstretch. skn_wrist drives Ik_handle.opm. 
        # Arguments:
            inputs_grp (string): Group for input data for this module.
            logic_jnt_list (list): list of arm logic joints. 
            ik_ctrl_list (list): Contains 4 ik control names.
        # Returns:
            bc_ikfk_stretch (utility): blendColors node returned so IKFK_Switch drives it.
            logic_hdl (string): logic Ik_handle name.
        '''
        # cr Ik_handle on the logic joints
        logic_hdl = f"hdl_{self.dm.mdl_nm}_logic_{self.dm.unique_id}_{self.dm.side}" # hdl_bipedArm_0_L
        cmds.ikHandle( n=logic_hdl, sol="ikRPsolver", sj=logic_jnt_list[0], ee=logic_jnt_list[2], ccv=False, pcv=False)

        # add ik pv ctrl mtx data to Ik_handle OPM to drive it!
        mm_pv_ik_hdl = f"MM_hdlPv_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        pm_pv_ik_hdl = f"PM_hdlPv_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
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

        db_shld_wrist = f"DB_ik_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        db_shld_elb = f"DB_ikUpper_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        db_elb_wrist = f"DB_ikLower_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        fm_global = f"FM_byGlobal_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        fm_max = f"FM_max_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        fm_upPercent_div = f"FM_upPercentageDiv_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        fm_upPercentTotal_mult = f"FM_upPercentageTotalMult_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        fm_lowPercent_div = f"FM_lowPercentageDiv_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        fm_lowPercentTotal_mult = f"FM_lowPercentageTotalMult_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        bc_pin_limb = f"BC_pin_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
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
        cmds.setAttr(f"{fm_global}{utils.Plg.flt_A}", d_shld_wrist)
        utils.connect_attr(f"{input_grp}.{self.dm.global_scale_attr}", f"{fm_global}{utils.Plg.flt_B}")
        utils.connect_attr(f"{fm_global}{utils.Plg.out_flt}", f"{fm_max}{utils.Plg.flt_B}")

            # fm_upPercent_div > fm_upPercentTotal_mult.flt_A
        cmds.setAttr(f"{fm_upPercent_div}{utils.Plg.flt_A}", d_shld_elb)
        cmds.setAttr(f"{fm_upPercent_div}{utils.Plg.flt_B}", d_shld_wrist)
        utils.connect_attr(f"{fm_upPercent_div}{utils.Plg.out_flt}", f"{fm_upPercentTotal_mult}{utils.Plg.flt_A}")
            # fm_lowPercent_div > fm_lowPercentTotal_mult.flt_A
        cmds.setAttr(f"{fm_lowPercent_div}{utils.Plg.flt_A}", d_elb_wrist)
        cmds.setAttr(f"{fm_lowPercent_div}{utils.Plg.flt_B}", d_shld_wrist)
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
        fm_up_fkStretch = f"FM_upFkStretchMult_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        fm_low_fkStretch = f"FM_lowFkStretchMult_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        fm_up_fkStretchGlobal = f"FM_upFkStretchGlobalMult_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        fm_low_fkStretchGlobal = f"FM_lowFkStretchGlobalMult_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        bc_ikfk_stretch = f"BC_ikfkStretch_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        for fm_mult_nm in [fm_up_fkStretchGlobal, fm_low_fkStretchGlobal]:
            utils.cr_node_if_not_exists(1, "floatMath", fm_mult_nm, {"operation":2})
        utils.cr_node_if_not_exists(1, "blendColors", bc_ikfk_stretch, {"blender":1})
        
            # fm_up/low_fkStretch.out_flt > fm_up/low_global.flt_A
        utils.connect_attr(f"{fm_up_fkStretch}{utils.Plg.out_flt}", f"{fm_up_fkStretchGlobal}{utils.Plg.flt_A}")
        utils.connect_attr(f"{fm_low_fkStretch}{utils.Plg.out_flt}", f"{fm_low_fkStretchGlobal}{utils.Plg.flt_A}")
        
            # input_grp.globalScale > fm_up/low_global.flt_B
        utils.connect_attr(f"{input_grp}.{self.dm.global_scale_attr}", f"{fm_up_fkStretchGlobal}{utils.Plg.flt_B}")
        utils.connect_attr(f"{input_grp}.{self.dm.global_scale_attr}", f"{fm_low_fkStretchGlobal}{utils.Plg.flt_B}")
        
            # bc_pin_arm > bc_ikfk_stretch.color2
        utils.connect_attr(f"{bc_pin_limb}{utils.Plg.out_letter[0]}", f"{bc_ikfk_stretch}{utils.Plg.color1_plg[0]}")
        utils.connect_attr(f"{bc_pin_limb}{utils.Plg.out_letter[1]}", f"{bc_ikfk_stretch}{utils.Plg.color1_plg[1]}")
        
            # fm_up/low_global > bc_ikfk_stretch.color1#
        utils.connect_attr(f"{fm_up_fkStretchGlobal}{utils.Plg.out_flt}", f"{bc_ikfk_stretch}{utils.Plg.color2_plg[0]}")
        utils.connect_attr(f"{fm_low_fkStretchGlobal}{utils.Plg.out_flt}", f"{bc_ikfk_stretch}{utils.Plg.color2_plg[1]}")
        
        # Plug into the logic joints!
        md_ikfk_stretch = f"MD_ikfkStretch_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        utils.cr_node_if_not_exists(1, "multiplyDivide", md_ikfk_stretch, {"operation":2})
            # bc_ikfk_stretch.outColor# > md_ikfk_stretch.input1#
        utils.connect_attr(f"{bc_ikfk_stretch}{utils.Plg.out_letter[0]}", f"{md_ikfk_stretch}{utils.Plg.input1_val[0]}")
        utils.connect_attr(f"{bc_ikfk_stretch}{utils.Plg.out_letter[1]}", f"{md_ikfk_stretch}{utils.Plg.input1_val[1]}")
            # input_grp.globalScale > md_ikfk_stretch.input2#
        utils.connect_attr(f"{input_grp}.{self.dm.global_scale_attr}", f"{md_ikfk_stretch}{utils.Plg.input2_val[0]}")
        utils.connect_attr(f"{input_grp}.{self.dm.global_scale_attr}", f"{md_ikfk_stretch}{utils.Plg.input2_val[1]}")
            # md_ikfk_stretch.out# > logic_jnt.translate prim axis
        utils.connect_attr(f"{md_ikfk_stretch}{utils.Plg.out_axis[0]}", f"{logic_jnt_list[1]}.translate{self.dm.prim_axis}")
        utils.connect_attr(f"{md_ikfk_stretch}{utils.Plg.out_axis[1]}", f"{logic_jnt_list[2]}.translate{self.dm.prim_axis}")

        # wire to the ikHandle.poleVector plug
        pMM_shld = f"PMM_shld_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        cM_shld = f"CM_shld_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        iM_shld = f"IM_shld_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        mm_pv = f"MM_poleVector_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        dm_pv = f"DM_poleVector_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
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
        # Arguments:
            logic_jnt_list (list): logic joints.
            logic_hdl (string): Logic ik handle.
            logic_curve_list (list): twist logic curves list.
        # Returns:
            logic_grp (string): logic group.
        '''
        logic_grp = f"grp_logic_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
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
        # Arguments:
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
        fk_attr = f"Follow_FK_Wrist_{self.dm.mdl_nm}_{self.dm.unique_id}_Rot"
        ik_attr = f"Follow_IK_Wrist_{self.dm.mdl_nm}_{self.dm.unique_id}"
        skn_jnt_wrist_ik_plg = f"{skn_jnt_wrist}.{ik_attr}"
        skn_jnt_wrist_fk_plg = f"{skn_jnt_wrist}.{fk_attr}"
        
        utils.add_float_attrib(skn_jnt_wrist, [fk_attr], [0.0, 1.0], True)
        utils.add_float_attrib(skn_jnt_wrist, [ik_attr], [0.0, 1.0], True)
        cmds.setAttr(skn_jnt_wrist_fk_plg, 0)
        cmds.setAttr(skn_jnt_wrist_ik_plg, 1)

        mm_logic_wrist = f"MM_sknWrist_{logic_jnt_list[-1]}"
        mm_ctrlFk_wrist = f"MM_sknWrist_{fk_ctrl_list[-1]}"
        mm_ctrlIk_wrist = f"MM_sknWrist_{ik_ctrl_list[-1]}"
        bm_skn_wrist = f"BM_sknWrist_{skn_jnt_wrist}"
        for mm_name in [mm_logic_wrist, mm_ctrlFk_wrist, mm_ctrlIk_wrist]:
            utils.cr_node_if_not_exists(1, 'multMatrix', mm_name)
        utils.cr_node_if_not_exists(1, 'blendMatrix', bm_skn_wrist, 
                                    {"target[0].scaleWeight":0,
                                     "target[0].translateWeight":0, 
                                     "target[0].shearWeight":0,
                                     "target[1].scaleWeight":0, 
                                     "target[1].shearWeight":0})
        
        # Taking a data type form two objects each to combine into a matrix for 'mm_ctrlIk_wrist'
        dm_trans_logic_wrist = f"DM_trans_{logic_jnt_list[-1]}"
        dm_rot_ctrl_wrist = f"DM_rot_{ik_ctrl_list[-1]}"
        cm_ctrl_wrist = f"CM_{ik_ctrl_list[-1]}"
        utils.cr_node_if_not_exists(0, 'decomposeMatrix', dm_trans_logic_wrist)
        utils.cr_node_if_not_exists(0, 'decomposeMatrix', dm_rot_ctrl_wrist)
        utils.cr_node_if_not_exists(0, 'composeMatrix', cm_ctrl_wrist)
        
        # > mm_logic_wrist
        utils.set_transformation_matrix([0.0, 0.0, 0.0], [0.0, 0.0, 0.0], f"{mm_logic_wrist}{utils.Plg.mtx_ins[0]}")         
        utils.connect_attr(f"{logic_jnt_list[-1]}{utils.Plg.wld_mtx_plg}", f"{mm_logic_wrist}{utils.Plg.mtx_ins[1]}")

        # > mm_ctrlFk_wrist
        utils.set_transformation_matrix([0.0, 0.0, 0.0], [0.0, 0.0, 0.0], f"{mm_ctrlFk_wrist}{utils.Plg.mtx_ins[0]}")
        cmds.select(mm_ctrlFk_wrist)
        print(f"{fk_ctrl_list[-1]}{utils.Plg.wld_mtx_plg}", f"{mm_ctrlFk_wrist}{utils.Plg.mtx_ins[1]}")    
        utils.connect_attr(f"{fk_ctrl_list[-1]}{utils.Plg.wld_mtx_plg}", f"{mm_ctrlFk_wrist}{utils.Plg.mtx_ins[1]}")

        # > mm_ctrlIk_wrist
        utils.set_transformation_matrix([0.0, 0.0, 0.0], [0.0, 0.0, 0.0], f"{mm_ctrlIk_wrist}{utils.Plg.mtx_ins[0]}") 
            # > dm_trans_logic_wrist
        utils.connect_attr(f"{logic_jnt_list[-1]}{utils.Plg.wld_mtx_plg}", f"{dm_trans_logic_wrist}{utils.Plg.inp_mtx_plg}")
            # > dm_rot_ctrl_wrist
        utils.connect_attr(f"{ik_ctrl_list[-1]}{utils.Plg.wld_mtx_plg}", f"{dm_rot_ctrl_wrist}{utils.Plg.inp_mtx_plg}")
            # > cm_ctrl_wrist
        utils.connect_attr(f"{dm_trans_logic_wrist}{utils.Plg.outT_plug}", f"{cm_ctrl_wrist}{utils.Plg.inputT_plug}")
        utils.connect_attr(f"{dm_rot_ctrl_wrist}{utils.Plg.outR_plug}", f"{cm_ctrl_wrist}{utils.Plg.inputR_plug}")
        utils.connect_attr(f"{cm_ctrl_wrist}{utils.Plg.out_mtx_plg}", f"{mm_ctrlIk_wrist}{utils.Plg.mtx_ins[1]}")
        
        # utils.connect_attr(f"{ik_ctrl_list[-1]}{utils.Plg.wld_mtx_plg}", f"{mm_ctrlIk_wrist}{utils.Plg.mtx_ins[1]}")

        #> bm_skn_wrist
        utils.connect_attr(f"{mm_logic_wrist}{utils.Plg.mtx_sum_plg}", f"{bm_skn_wrist}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{mm_ctrlFk_wrist}{utils.Plg.mtx_sum_plg}", f"{bm_skn_wrist}{utils.Plg.target_mtx[0]}")
        utils.connect_attr(f"{mm_ctrlIk_wrist}{utils.Plg.mtx_sum_plg}", f"{bm_skn_wrist}{utils.Plg.target_mtx[1]}")
        utils.connect_attr(skn_jnt_wrist_fk_plg, f"{bm_skn_wrist}.target[0].rotateWeight")
        utils.connect_attr(skn_jnt_wrist_ik_plg, f"{bm_skn_wrist}.target[1].translateWeight")
        utils.connect_attr(skn_jnt_wrist_ik_plg, f"{bm_skn_wrist}.target[1].rotateWeight")
        utils.connect_attr(f"{bm_skn_wrist}{utils.Plg.out_mtx_plg}", f"{skn_jnt_wrist}{utils.Plg.opm_plg}")
        
        return skn_jnt_wrist_ik_plg, skn_jnt_wrist_fk_plg
    

    def wire_mdl_setting_ctrl(self, skn_jnt_wrist):
        '''
        # Description:
            Settings Control alr exists in scene so wire its positon & ADD all it's attributes!
        # Arguments: 
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
        mdl_settings_ctrl = f"ctrl_{self.dm.mdl_nm}_settings_{self.dm.unique_id}_{self.dm.side}"
        # Colour the settings ctrl a pale version of the current colour. 
        if self.dm.side == "L":
            utils.colour_object(mdl_settings_ctrl, 4)
        elif self.dm.side == "R":
            utils.colour_object(mdl_settings_ctrl, 18)
        cmds.parent(mdl_settings_ctrl, f"grp_ctrls_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}")
        
        ikfk_switch_attr = "IK_FK_Switch"
        stretch_state_attr = "Stretch_State"
        stretch_vol_attr = "Stretch_Volume"
        shaper_attr = "Vis_Shapers"
        utils.add_locked_attrib(mdl_settings_ctrl, ["Attributes"])
        utils.add_float_attrib(mdl_settings_ctrl, [f"{ikfk_switch_attr}", f"{stretch_state_attr}", f"{stretch_vol_attr}"], [0.0, 1.0], True)
        # utils.add_float_attrib(root_ctrl, [f"Auto_Stretch"], [0.0, 1.0], True)

        utils.add_locked_attrib(mdl_settings_ctrl, ["Visibility"])
        utils.add_float_attrib(mdl_settings_ctrl, [f"{shaper_attr}"], [0.0, 1.0], True)

        # wire 'skn_jnt_wrist' to  'mdl_settings_ctrl.OPM'
        mm_settings = f"MM_{mdl_settings_ctrl}"
        utils.cr_node_if_not_exists(1, 'multMatrix', mm_settings)
        utils.connect_attr(f"{skn_jnt_wrist}{utils.Plg.wld_mtx_plg}", f"{mm_settings}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{mm_settings}{utils.Plg.mtx_sum_plg}", f"{mdl_settings_ctrl}{utils.Plg.opm_plg}")
        
        ikfk_plug = f"{mdl_settings_ctrl}.{ikfk_switch_attr}"
        stretch_state_plug = f"{mdl_settings_ctrl}.{stretch_state_attr}"
        stretch_volume_plug = f"{mdl_settings_ctrl}.{stretch_vol_attr}"
        shaper_plug = f"{mdl_settings_ctrl}.{shaper_attr}"

        return mdl_settings_ctrl, ikfk_plug, stretch_state_plug, stretch_volume_plug, shaper_plug
    

    def wire_IKFK_switch(self, skn_jnt_wrist_ik_plg, skn_jnt_wrist_fk_plg, 
                         mdl_settings_ctrl, ikfk_plug, stretch_state_plug,
                         bc_ikfkStretch, logic_hdl,
                         fk_ctrl_grp, ik_ctrl_grp):
        '''
        # Description:
            Wire the connections for all ikfk switch attributes:
            > reverse.inputX > .outputX -> skn_jnt_wrist.{f"Follow_FK_Wrist_{self.dm.mdl_nm}_{self.dm.unique_id}_Rot"}
            > skn_jnt_wrist.{f"Follow_IK_Wrist_{self.dm.mdl_nm}_{self.dm.unique_id}"}
            > bc_ikfkStretch.blender
            > hdl.ik_blend
        # Arguments:
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
        rev_ikfk = f"REV_{mdl_settings_ctrl}"
        utils.cr_node_if_not_exists(1, 'reverse', rev_ikfk)
        # > skn_jnt_wrist.inputX
        utils.connect_attr(ikfk_plug, f"{rev_ikfk}.inputX")
        utils.connect_attr(f"{rev_ikfk}{utils.Plg.out_axis[0]}", skn_jnt_wrist_fk_plg)
        utils.connect_attr(ikfk_plug, skn_jnt_wrist_ik_plg)

        # 'ikfk_plug' & 'stretch_state_plug' > bc_ikfkStretch.blender
        cond_stretch_state = f"COND_stretchState_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        cond_ikfk = f"COND_ikfk_switch_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        utils.cr_node_if_not_exists(1, 'condition', cond_stretch_state, {"secondTerm":1, "colorIfTrueR":0.9525})
        utils.cr_node_if_not_exists(1, 'condition', cond_ikfk, {"secondTerm":0})
            # > cond_stretch_state
        utils.connect_attr(stretch_state_plug, f"{cond_stretch_state}.firstTerm")
        utils.connect_attr(stretch_state_plug, f"{cond_stretch_state}.colorIfFalseR")
            # > cond_stretch_state
        utils.connect_attr(ikfk_plug, f"{cond_ikfk}.firstTerm")
        utils.connect_attr(f"{cond_stretch_state}.outColorR", f"{cond_ikfk}.colorIfFalseR")
            # > bc_ikfkStretch.blender
        utils.connect_attr(f"{cond_ikfk}.outColorR", f"{bc_ikfkStretch}{utils.Plg.blndr_plg}")
        
        # > hdl.ik_blend
        utils.connect_attr(ikfk_plug, f"{logic_hdl}.ikBlend")

        # > ctrl ik/fk groups.visibility
        utils.connect_attr(f"{rev_ikfk}{utils.Plg.out_axis[0]}", f"{fk_ctrl_grp}{utils.Plg.vis_plg}")
        utils.connect_attr(ikfk_plug, f"{ik_ctrl_grp}{utils.Plg.vis_plg}")


    def organise_ctrl_shaper_list(self, unorganised_shaper_ctrl_list):
        '''
        # Description:
            Gather each control into variables to make sure i'm working on the right 
            control becuase the order is unorganised beforehand.
            Organised order: 'shaper_main', 'shaper_upper', 'shaper_mid', 'shaper_lower'
        # Arguments:
            unorganised_shaper_ctrl_list (list) Contains 4 shaper contol names. (unorganied)
        # Returns:
            organised_shaper_ctrl_list (list) Contains 4 shaper contol names. (organied)
        '''
        for shaper in unorganised_shaper_ctrl_list:
            if "main" in shaper:
                shaper_main = shaper
            elif "upper" in shaper:
                shaper_upper = shaper
            elif "middle" in shaper:
                shaper_mid = shaper
            elif "lower" in shaper:
                shaper_lower = shaper
        organised_shaper_ctrl_list = [shaper_main, shaper_upper, shaper_mid, shaper_lower]

        return organised_shaper_ctrl_list


    def wire_shaper_ctrls(self, shaper_ctrl_list, logic_jnt_list, ik_ctrl_list, 
                          shaper_plug, shaper_ctrl_grp):
        '''
        # Description:
            Wire the connections for all shaper controls so they are positioned. 
            'shaper_main' control drives all other shaper controls. Positons are 
            all sorted with matrix's and DO NOT need pos or rot data for them.
        # Arguments:
            shaper_ctrl_list (list) Contains 4 shaper contol names. (organied)
            logic_jnt_list (list): list of arm logic joints. 
            ik_ctrl_list (list): Contains 4 ik control names.
            shaper_plug (plug): 'shaper_visibility' control attribute plug for consitancy.
            shaper_ctrl_grp (string): Name of shaper ctrl grp.
        # Returns: N/A
        '''
        shaper_main, shaper_upper, shaper_mid, shaper_lower = shaper_ctrl_list

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
        utils.cr_node_if_not_exists(0, 'blendMatrix', bm_shaper_upper)
        for blend_attr in ["scaleWeight", "rotateWeight", "shearWeight"]:
            cmds.setAttr(f"{bm_shaper_upper}.target[0].{blend_attr}", 0)
        cmds.setAttr(f"{bm_shaper_upper}.target[0].translateWeight", 0.5)
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
        utils.cr_node_if_not_exists(0, 'blendMatrix', bm_shaper_lower)
        for blend_attr in ["scaleWeight", "rotateWeight", "shearWeight"]:
            cmds.setAttr(f"{bm_shaper_lower}.target[0].{blend_attr}", 0)
        cmds.setAttr(f"{bm_shaper_lower}.target[0].translateWeight", 0.5)
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


    def wire_shaper_ctrls_to_curves(self, shaper_ctrl_list, upper_curve, lower_curve, 
                                    upper_cv_intermediate_pos_ls, lower_cv_intermediate_pos_ls, 
                                    logic_jnt_list):
        '''
        # Description:
            Wire ctrl_shaper's to the upper & lower curve's (that are going to 
            drive the ik spline afterwards to position the joints)
            - ONLY 'upper', 'middle' & 'lower' shaper controls drive the curves.
            - The intermediate control points of the curves, have an offset in 
              the MM.matrixIn[0]. [#.#, 0.0, 0.0] means Y & Z values should be 
              0.0 to keep the curve straight!
        # Arguments:
            shaper_ctrl_list (list): Contains 4 shaper contol names. (organied)
            upper_curve (string): 
        # Returns: N/A
        '''
        shaper_main, shaper_upper, shaper_mid, shaper_lower = shaper_ctrl_list
        # cr the utility nodes -> each 'set' = multMatrix & pointMatrixMult for each control points (3 'set' for each curve.)
            # upper curve
            # ctrl_upper_shaper drives the CENTRE of crv_upper.controlPoints ([1] & [2])
            # ctrl_middle_shaper drives the END of crv_upper.controlPoints ([3])
        mm_shld_upp_0 = f"MM_Crv0_{logic_jnt_list[0]}"
        mm_shp_upp_1 = f"MM_Crv1_{shaper_upper}"
        mm_shp_upp_2 = f"MM_Crv2_{shaper_upper}"
        mm_shp_upp_3 = f"MM_Crv3_{shaper_mid}"
        pmm_shld_upp_0 = f"PMM_Crv0_{logic_jnt_list[0]}"
        pmm_shp_upp_1 = f"PMM_Crv1_{shaper_upper}"
        pmm_shp_upp_2 = f"PMM_Crv2_{shaper_upper}"
        pmm_shp_upp_3 = f"PMM_Crv3_{shaper_mid}"
        
            # lower curve
            # ctrl_lower_shaper drives the CENTRE of crv_lower.controlPoints ([1] & [2])
            # ctrl_middle_shaper drives the START of crv_lower.controlPoints ([0])
        mm_shp_low_0 = f"MM_Crv0_{shaper_mid}"
        mm_shp_low_1 = f"MM_Crv1_{shaper_lower}"
        mm_shp_low_2 = f"MM_Crv2_{shaper_lower}"
        mm_wrist_low_3 = f"MM_Crv0_{logic_jnt_list[-1]}"
        pmm_shp_low_0 = f"PMM_Crv0_{shaper_mid}"
        pmm_shp_low_1 = f"PMM_Crv1_{shaper_lower}"
        pmm_shp_low_2 = f"PMM_Crv2_{shaper_lower}"
        pmm_wrist_low_3 = f"PMM_Crv0_{logic_jnt_list[-1]}"
        for mm_name, pmm_name in zip([mm_shld_upp_0, mm_shp_upp_1, mm_shp_upp_2, mm_shp_upp_3, mm_shp_low_0, mm_shp_low_1, mm_shp_low_2, mm_wrist_low_3],
                                     [pmm_shld_upp_0, pmm_shp_upp_1, pmm_shp_upp_2, pmm_shp_upp_3, pmm_shp_low_1, pmm_shp_low_2, pmm_shp_low_0, pmm_wrist_low_3]):
            utils.cr_node_if_not_exists(1, 'multMatrix', mm_name)
            utils.cr_node_if_not_exists(1, 'pointMatrixMult', pmm_name)
        # wire connections Upper
            # offset > mm.[1]
        shp_upp_pos = cmds.xform(shaper_upper, q=1, translation=1, ws=1)
        upp_cv_1_offset = [x - y for x, y in zip(upper_cv_intermediate_pos_ls[0], shp_upp_pos)]
        upp_cv_2_offset = [x - y for x, y in zip(upper_cv_intermediate_pos_ls[1], shp_upp_pos)]
        
        # Use Pyhtonic Slicing & Assignment method to set the items after the first index to 0.0 ([#.#, 0.0, 0.0])
        upp_cv_1_offset[1:] = [0.0] * len(upp_cv_1_offset[1:])
        upp_cv_2_offset[1:] = [0.0] * len(upp_cv_2_offset[1:])

        utils.set_pos_mtx(upp_cv_1_offset, f"{mm_shp_upp_1}{utils.Plg.mtx_ins[0]}")
        utils.set_pos_mtx(upp_cv_2_offset, f"{mm_shp_upp_2}{utils.Plg.mtx_ins[0]}")
            # ctrl_shaper > mm.[1]
        utils.connect_attr(f"{logic_jnt_list[0]}{utils.Plg.wld_mtx_plg}", f"{mm_shld_upp_0}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{shaper_upper}{utils.Plg.wld_mtx_plg}", f"{mm_shp_upp_1}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{shaper_upper}{utils.Plg.wld_mtx_plg}", f"{mm_shp_upp_2}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{shaper_mid}{utils.Plg.wld_mtx_plg}", f"{mm_shp_upp_3}{utils.Plg.mtx_ins[1]}")
            # mm > pmm
        utils.connect_attr(f"{mm_shld_upp_0}{utils.Plg.mtx_sum_plg}", f"{pmm_shld_upp_0}{utils.Plg.inMtx_plg}")
        utils.connect_attr(f"{mm_shp_upp_1}{utils.Plg.mtx_sum_plg}", f"{pmm_shp_upp_1}{utils.Plg.inMtx_plg}")
        utils.connect_attr(f"{mm_shp_upp_2}{utils.Plg.mtx_sum_plg}", f"{pmm_shp_upp_2}{utils.Plg.inMtx_plg}")
        utils.connect_attr(f"{mm_shp_upp_3}{utils.Plg.mtx_sum_plg}", f"{pmm_shp_upp_3}{utils.Plg.inMtx_plg}")
            # pmm > contrPoint[#]
        utils.connect_attr(f"{pmm_shld_upp_0}{utils.Plg.output_plg}", f"{upper_curve}.controlPoints[0]")
        utils.connect_attr(f"{pmm_shp_upp_1}{utils.Plg.output_plg}", f"{upper_curve}.controlPoints[1]")
        utils.connect_attr(f"{pmm_shp_upp_2}{utils.Plg.output_plg}", f"{upper_curve}.controlPoints[2]")
        utils.connect_attr(f"{pmm_shp_upp_3}{utils.Plg.output_plg}", f"{upper_curve}.controlPoints[3]")

        # wire connections Upper
            # offset > mm.[1]
        shp_low_pos = cmds.xform(shaper_lower, q=1, translation=1, ws=1)
        low_cv_1_offset = [x - y for x, y in zip(shp_low_pos, lower_cv_intermediate_pos_ls[0])]
        low_cv_2_offset = [x - y for x, y in zip(shp_low_pos, lower_cv_intermediate_pos_ls[1])]

        low_cv_1_offset[1:] = [0.0] * len(low_cv_1_offset[1:])
        low_cv_2_offset[1:] = [0.0] * len(low_cv_2_offset[1:])

        utils.set_pos_mtx(low_cv_1_offset, f"{mm_shp_low_1}{utils.Plg.mtx_ins[0]}")
        utils.set_pos_mtx(low_cv_2_offset, f"{mm_shp_low_2}{utils.Plg.mtx_ins[0]}")
            # ctrl_shaper > mm.[1]
        utils.connect_attr(f"{shaper_lower}{utils.Plg.wld_mtx_plg}", f"{mm_shp_low_1}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{shaper_lower}{utils.Plg.wld_mtx_plg}", f"{mm_shp_low_2}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{shaper_mid}{utils.Plg.wld_mtx_plg}", f"{mm_shp_low_0}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{logic_jnt_list[-1]}{utils.Plg.wld_mtx_plg}", f"{mm_wrist_low_3}{utils.Plg.mtx_ins[1]}")
            # mm > pmm
        utils.connect_attr(f"{mm_shp_low_1}{utils.Plg.mtx_sum_plg}", f"{pmm_shp_low_1}{utils.Plg.inMtx_plg}")
        utils.connect_attr(f"{mm_shp_low_2}{utils.Plg.mtx_sum_plg}", f"{pmm_shp_low_2}{utils.Plg.inMtx_plg}")
        utils.connect_attr(f"{mm_shp_low_0}{utils.Plg.mtx_sum_plg}", f"{pmm_shp_low_0}{utils.Plg.inMtx_plg}")
        utils.connect_attr(f"{mm_wrist_low_3}{utils.Plg.mtx_sum_plg}", f"{pmm_wrist_low_3}{utils.Plg.inMtx_plg}")
            # pmm > contrPoint[#]
        utils.connect_attr(f"{pmm_shp_low_1}{utils.Plg.output_plg}", f"{lower_curve}.controlPoints[1]")
        utils.connect_attr(f"{pmm_shp_low_2}{utils.Plg.output_plg}", f"{lower_curve}.controlPoints[2]")
        utils.connect_attr(f"{pmm_shp_low_0}{utils.Plg.output_plg}", f"{lower_curve}.controlPoints[0]")
        utils.connect_attr(f"{pmm_wrist_low_3}{utils.Plg.output_plg}", f"{lower_curve}.controlPoints[3]")


    def cr_twist_ik_spline(self, upp_jnt_chain, low_jnt_chain, upper_curve, lower_curve):
        '''
        # Description:
            - Twist skin joints & Curves must be positioned first beforehand. 
            - Create IK spline handle for upper & lower joints w/ curves
        # Arguments:
        # Returns:
            hdl_upper_name (string): name of upper spring solver ik handle 
            hdl_lower_name (string): name of lower spring solver ik handle
        '''
        # upper curve ik spline handle
        hdl_upper_name = f"hdl_{self.dm.mdl_nm}_upper_{self.dm.unique_id}_{self.dm.side}"
        hdl_lower_name = f"hdl_{self.dm.mdl_nm}_lower_{self.dm.unique_id}_{self.dm.side}"
        cmds.ikHandle( n=hdl_upper_name, sol="ikSplineSolver", c=upper_curve, sj=upp_jnt_chain[0], ee=upp_jnt_chain[-1], ccv=False, pcv=False)
        cmds.ikHandle( n=hdl_lower_name, sol="ikSplineSolver", c=lower_curve, sj=low_jnt_chain[0], ee=low_jnt_chain[-1], ccv=False, pcv=False)
        
        cmds.parent(hdl_upper_name, hdl_lower_name, f"grp_logic_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}")

        return hdl_upper_name, hdl_lower_name


    # def wire_parent_skn_twist_joint_matrix(self, upp_jnt_chain, low_jnt_chain, armRt_ctrl, logic_jnt_list, skel_pos_dict, skel_rot_dict):
    #     '''
    #     # Description:
    #         The parent of each joint chain (Upper/Lower) has driven OPM.
    #         - Upper prnt driven by 'arm root control' 
    #         - lower prnt driven by 'jnt logic elbow' 
    #     # Arguments:
            
    #     # Returns: N/A
    #     '''
    #     jnt_skn_upp_parent = upp_jnt_chain[0]
    #     jnt_skn_low_parent = low_jnt_chain[0]
    #     mm_skn_upp_parent = f"mm_{jnt_skn_upp_parent}"
    #     mm_skn_low_parent = f"mm_{jnt_skn_low_parent}"
    #     utils.cr_node_if_not_exists(1, 'multMatrix', mm_skn_upp_parent)
    #     utils.cr_node_if_not_exists(1, 'multMatrix', mm_skn_low_parent)
        
    #     utils.clean_opm(jnt_skn_upp_parent)
    #     utils.clean_opm(jnt_skn_low_parent)

    #     # wire upper
    #         # > mm_skn_upp_parent
    #     # utils.set_transformation_matrix([0.0, 0.0, 0.0], [0.0, 0.0, 0.0], f"{mm_skn_upp_parent}{utils.Plg.mtx_ins[0]}") 
    #     utils.set_transformation_matrix(list(skel_pos_dict.values())[0], list(skel_rot_dict.values())[0], f"{mm_skn_upp_parent}{utils.Plg.mtx_ins[0]}")
    #     utils.connect_attr(f"{armRt_ctrl}{utils.Plg.wld_mtx_plg}", f"{mm_skn_upp_parent}{utils.Plg.mtx_ins[1]}")
    #         # > jnt_skn_upp_parent
    #     utils.connect_attr(f"{mm_skn_upp_parent}{utils.Plg.mtx_sum_plg}", f"{jnt_skn_upp_parent}{utils.Plg.opm_plg}")
        
    #     # wire lower
    #         # > mm_skn_low_parent
    #     # utils.set_transformation_matrix([0.0, 0.0, 0.0], [0.0, 0.0, 0.0], f"{mm_skn_low_parent}{utils.Plg.mtx_ins[0]}") 
    #     utils.set_transformation_matrix(list(skel_pos_dict.values())[1], [0.0, 0.0, 0.0], f"{mm_skn_low_parent}{utils.Plg.mtx_ins[0]}")
    #     utils.connect_attr(f"{logic_jnt_list[1]}{utils.Plg.wld_mtx_plg}", f"{mm_skn_low_parent}{utils.Plg.mtx_ins[1]}")
    #         # > jnt_skn_low_parent
    #     utils.connect_attr(f"{mm_skn_low_parent}{utils.Plg.mtx_sum_plg}", f"{jnt_skn_low_parent}{utils.Plg.opm_plg}")
        

    def wire_skn_twist_joints_stretch(self, input_grp, upp_jnt_chain, low_jnt_chain, upper_curve, lower_curve):
        '''
        TO DO:
            - Wire curves to the twist skin joints.
            - Arm pinning.
            - This function is the Stretch connection. 
        '''
        upp_jnt_num = len(upp_jnt_chain)-1
        low_jnt_num = len(low_jnt_chain)-1
        upp_curve_shape = cmds.listRelatives(upper_curve, s=1)[0]
        low_curve_shape = cmds.listRelatives(lower_curve, s=1)[0]

        upp_crv_info = f"INFO_{upper_curve}"
        fm_upp_global = f"FM_global_{upper_curve}"
        fm_upp_div = f"FM_div_{upper_curve}"
        low_crv_info = f"INFO_{lower_curve}"
        fm_low_global = f"FM_global_{lower_curve}"
        fm_low_div = f"FM_div_{lower_curve}"
        utils.cr_node_if_not_exists(1, 'curveInfo', upp_crv_info)
        utils.cr_node_if_not_exists(1, "floatMath", fm_upp_global, {"operation":3})
        utils.cr_node_if_not_exists(1, "floatMath", fm_upp_div, {"operation":3, "floatB":upp_jnt_num})
        utils.cr_node_if_not_exists(1, 'curveInfo', low_crv_info)
        utils.cr_node_if_not_exists(1, "floatMath", fm_low_global, {"operation":3})
        utils.cr_node_if_not_exists(1, "floatMath", fm_low_div, {"operation":3, "floatB":low_jnt_num})

        # wire upper
            # curve > crv_info
        utils.connect_attr(f"{upp_curve_shape}{utils.Plg.wld_space_plg}", f"{upp_crv_info}{utils.Plg.inp_curve_plg}")
            # crv_info > fm_global
        utils.connect_attr(f"{upp_crv_info}{utils.Plg.arc_len_plg}", f"{fm_upp_global}{utils.Plg.flt_A}")
        utils.connect_attr(f"{input_grp}.{self.dm.global_scale_attr}", f"{fm_upp_global}{utils.Plg.flt_B}")
            # fm_global > fm_div
        utils.connect_attr(f"{fm_upp_global}{utils.Plg.out_flt}", f"{fm_upp_div}{utils.Plg.flt_A}")
            # fm_div > twist_jnt.translate
        for jnt in (upp_jnt_chain[1:]):
            utils.connect_attr(f"{fm_upp_div}{utils.Plg.out_flt}", f"{jnt}.translate{self.dm.prim_axis}")
        
        # wire lower the same way
        utils.connect_attr(f"{low_curve_shape}{utils.Plg.wld_space_plg}", f"{low_crv_info}{utils.Plg.inp_curve_plg}")
        utils.connect_attr(f"{low_crv_info}{utils.Plg.arc_len_plg}", f"{fm_low_global}{utils.Plg.flt_A}")
        utils.connect_attr(f"{input_grp}.{self.dm.global_scale_attr}", f"{fm_low_global}{utils.Plg.flt_B}")
        utils.connect_attr(f"{fm_low_global}{utils.Plg.out_flt}", f"{fm_low_div}{utils.Plg.flt_A}")
        for jnt in (low_jnt_chain[1:]):
            utils.connect_attr(f"{fm_low_div}{utils.Plg.out_flt}", f"{jnt}.translate{self.dm.prim_axis}")

        return fm_upp_global, fm_low_global


    def wire_skn_twist_joints_volume(self, input_grp, upp_jnt_chain, low_jnt_chain, upper_curve, lower_curve, 
                                     stretch_vol_plug, fm_upp_global, fm_low_global,
                                     d_shld_elb, d_elb_wrist):
        '''
        TO DO:
            - Wire curves to the twist skin joints.
            - This function is the Volume preservation connection.
        '''
        fm_upp_norm = f"FM_norm_{upper_curve}"
        fm_upp_pow = f"FM_pow_{upper_curve}"
        fm_low_norm = f"FM_norm_{lower_curve}"
        fm_low_pow = f"FM_pow_{lower_curve}"
        bc_stretch_volume = f"BC_stretchVolume_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"

        utils.cr_node_if_not_exists(1, "floatMath", fm_upp_norm, {"operation":3, "floatB":d_shld_elb})
        utils.cr_node_if_not_exists(1, "floatMath", fm_upp_pow, {"operation":6})
        utils.cr_node_if_not_exists(1, "floatMath", fm_low_norm, {"operation":3, "floatB":d_elb_wrist})
        utils.cr_node_if_not_exists(1, "floatMath", fm_low_pow, {"operation":6})
        utils.cr_node_if_not_exists(1, "blendColors", bc_stretch_volume, {"color2R":d_shld_elb, "color2G":d_elb_wrist})
        
        # wire bc_stretch_volume.blender
        utils.connect_attr(stretch_vol_plug, f"{bc_stretch_volume}{utils.Plg.blndr_plg}")
        
        # wire upper
            # > bc_stretch_volume
        utils.connect_attr(f"{fm_upp_global}{utils.Plg.out_flt}", f"{bc_stretch_volume}{utils.Plg.color1_plg[0]}")
            # > fm_upp/low_norm
        utils.connect_attr(f"{bc_stretch_volume}{utils.Plg.out_letter[0]}", f"{fm_upp_norm}{utils.Plg.flt_A}")
            # > fm_upp/low_pow
        utils.connect_attr(f"{fm_upp_norm}{utils.Plg.out_flt}", f"{fm_upp_pow}{utils.Plg.flt_A}")
        utils.connect_attr(f"{input_grp}.Squash_Value", f"{fm_upp_pow}{utils.Plg.flt_B}")
        # > upp/low_jnt_chain
        for jnt in (upp_jnt_chain):
            utils.connect_attr(f"{fm_upp_pow}{utils.Plg.out_flt}", f"{jnt}.scaleY")
            utils.connect_attr(f"{fm_upp_pow}{utils.Plg.out_flt}", f"{jnt}.scaleZ")

        # wire lower
        utils.connect_attr(f"{fm_low_global}{utils.Plg.out_flt}", f"{bc_stretch_volume}{utils.Plg.color1_plg[1]}")
        utils.connect_attr(f"{bc_stretch_volume}{utils.Plg.out_letter[1]}", f"{fm_low_norm}{utils.Plg.flt_A}")
        utils.connect_attr(f"{fm_low_norm}{utils.Plg.out_flt}", f"{fm_low_pow}{utils.Plg.flt_A}")
        utils.connect_attr(f"{input_grp}.Squash_Value", f"{fm_low_pow}{utils.Plg.flt_B}")
        for jnt in (low_jnt_chain):
            utils.connect_attr(f"{fm_low_pow}{utils.Plg.out_flt}", f"{jnt}.scaleY")
            utils.connect_attr(f"{fm_low_pow}{utils.Plg.out_flt}", f"{jnt}.scaleZ")
        
    
    # def wire_rotations_on_twist_joints(self, logic_jnt_list, skn_jnt_wrist, ctrl_arm_root, hdl_upper, hdl_lower):
    #     '''
    #     # Description:
    #         Twisting of the upper & lower skn joint chains are driven by their 
    #         ik handle's .twist attribute.
    #         - Upper handle twisting is driven by jnt_logic_shld & jnt_logic_elbow  
    #         - lower handle twisting is driven by jnt_logic_elbow & jnt_skn_wrist
    #     # Arguments:
            
    #     # Returns:
    #         hdl_upper_name (string): name of upper spring solver ik handle 
    #         hdl_lower_name (string): name of lower spring solver ik handle
    #     '''
    #     jnt_logic_shld = logic_jnt_list[0]
    #     jnt_logic_elbow = logic_jnt_list[1]

    #     # upper 6 utility nodes
    #     mm_upp_fk_twist = f"MM_twist_fkNonRoll_{hdl_upper}"
    #     dm_upp_fk_twist = f"DM_twist_fkNonRoll_{hdl_upper}"
    #     quatToEuler_upp_fk_twist = f"QTE_twist_fkNonRoll_{hdl_upper}"
    #     mm_upp_twist = f"MM_twist_NonRoll_{hdl_upper}"
    #     dm_upp_twist = f"DM_twist_NonRoll_{hdl_upper}"
    #     quatToEuler_upp_twist = f"QTE_twist_NonRoll_{hdl_upper}"
    #     fm_upp_twist = f"FM_jntTwistValue_add_{hdl_upper}"

    #     utils.cr_node_if_not_exists(1, 'multMatrix', mm_upp_fk_twist)
    #     utils.cr_node_if_not_exists(1, 'decomposeMatrix', dm_upp_fk_twist)
    #     utils.cr_node_if_not_exists(1, 'quatToEuler', quatToEuler_upp_fk_twist)
    #     utils.cr_node_if_not_exists(1, 'multMatrix', mm_upp_twist)
    #     utils.cr_node_if_not_exists(1, 'decomposeMatrix', dm_upp_twist)
    #     utils.cr_node_if_not_exists(1, 'quatToEuler', quatToEuler_upp_twist)
    #     utils.cr_node_if_not_exists(1, 'floatMath', fm_upp_twist, {"operation":0})

    #     # wire Upper 
    #         # fk_nonRoll
    #         # > mm_upp_fk_twist
    #     utils.connect_attr(f"{jnt_logic_shld}{utils.Plg.wld_mtx_plg}", f"{mm_upp_fk_twist}{utils.Plg.mtx_ins[0]}")
    #     utils.connect_attr(f"{ctrl_arm_root}{utils.Plg.wld_inv_mtx_plg}", f"{mm_upp_fk_twist}{utils.Plg.mtx_ins[1]}")
    #         # > dm_upp_fk_twist
    #     utils.connect_attr(f"{mm_upp_fk_twist}{utils.Plg.mtx_sum_plg}", f"{dm_upp_fk_twist}{utils.Plg.inp_mtx_plg}")
    #         # > quatToEuler_upp_fk_twist
    #     utils.connect_attr(f"{dm_upp_fk_twist}.outputQuatX", f"{quatToEuler_upp_fk_twist}.inputQuatX")
    #     utils.connect_attr(f"{dm_upp_fk_twist}.outputQuatW", f"{quatToEuler_upp_fk_twist}.inputQuatW")
    #         # nonRoll
    #         # > mm_upp_twist
    #     utils.connect_attr(f"{jnt_logic_elbow}{utils.Plg.wld_mtx_plg}", f"{mm_upp_twist}{utils.Plg.mtx_ins[0]}")
    #     utils.connect_attr(f"{jnt_logic_shld}{utils.Plg.wld_inv_mtx_plg}", f"{mm_upp_twist}{utils.Plg.mtx_ins[1]}")
    #         # > dm_upp_twist
    #     utils.connect_attr(f"{mm_upp_twist}{utils.Plg.mtx_sum_plg}", f"{dm_upp_twist}{utils.Plg.inp_mtx_plg}")
    #         # > quatToEuler_upp_twist
    #     utils.connect_attr(f"{dm_upp_twist}.outputQuatX", f"{quatToEuler_upp_twist}.inputQuatX")
    #     utils.connect_attr(f"{dm_upp_twist}.outputQuatW", f"{quatToEuler_upp_twist}.inputQuatW")
    #         # > fm_upp_twist
    #     utils.connect_attr(f"{quatToEuler_upp_fk_twist}.outputRotateX", f"{fm_upp_twist}{utils.Plg.flt_A}")
    #     utils.connect_attr(f"{quatToEuler_upp_twist}.outputRotateX", f"{fm_upp_twist}{utils.Plg.flt_B}")
    #         # > hdl_upper.twist
    #     utils.connect_attr(f"{fm_upp_twist}{utils.Plg.out_flt}", f"{hdl_upper}.twist")

    #     # lower 3 utility nodes
    #     mm_low_twist = f"MM_twist_NonRoll_{hdl_lower}"
    #     dm_low_twist = f"DM_twist_NonRoll_{hdl_lower}"
    #     quatToEuler_low_twist = f"QTE_twist_NonRoll_{hdl_lower}"

    #     utils.cr_node_if_not_exists(1, 'multMatrix', mm_low_twist)
    #     utils.cr_node_if_not_exists(1, 'decomposeMatrix', dm_low_twist)
    #     utils.cr_node_if_not_exists(1, 'quatToEuler', quatToEuler_low_twist)

    #     # wire lower 
    #         # > mm_low_twist
    #     utils.connect_attr(f"{skn_jnt_wrist}{utils.Plg.wld_mtx_plg}", f"{mm_low_twist}{utils.Plg.mtx_ins[0]}")
    #     utils.connect_attr(f"{jnt_logic_elbow}{utils.Plg.wld_inv_mtx_plg}", f"{mm_low_twist}{utils.Plg.mtx_ins[1]}")
    #         # > dm_low_twist
    #     utils.connect_attr(f"{mm_low_twist}{utils.Plg.mtx_sum_plg}", f"{dm_low_twist}{utils.Plg.inp_mtx_plg}")
    #         # > quatToEuler_upp_twist
    #     utils.connect_attr(f"{dm_low_twist}.outputQuatX", f"{quatToEuler_low_twist}.inputQuatX")
    #     utils.connect_attr(f"{dm_low_twist}.outputQuatW", f"{quatToEuler_low_twist}.inputQuatW")
    #         # > hdl_lower.twist
    #     utils.connect_attr(f"{quatToEuler_low_twist}.outputRotateX", f"{hdl_lower}.twist")


    def parent_ik_ctrls_out(self, ik_ctrl_list):
        '''
        # Description:
            parent the 'ik clavicle & ik shoulder' controls to the parent ctrl grp 
            so 'they' don't get hidden with ikfk switch
        # Arguments:
            ik_ctrl_list (list): Contains 4 ik control names.
        # Returns: N/A
        '''
        cmds.parent(ik_ctrl_list[0], ik_ctrl_list[1], f"grp_ctrls_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}")
        cmds.select(cl=1)


    def lock_ctrl_attributes(self, fk_ctrl_list):
        '''
        # Description:
            Lock an assortment of ctrls of the module to make it animator friendly.
            (For testing of controls toggle this function).
        # Arguments:
            fk_ctrl_list (list): Contains 3 fk control names.
        # Returns: N/A
        '''
        for ctrl in fk_ctrl_list:
            cmds.setAttr(f"{ctrl}.translateX", lock=1)
            cmds.setAttr(f"{ctrl}.translateY", lock=1)
            cmds.setAttr(f"{ctrl}.translateZ", lock=1)