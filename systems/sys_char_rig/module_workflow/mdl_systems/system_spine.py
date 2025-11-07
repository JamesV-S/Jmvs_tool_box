


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

class SystemSpine:
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
        print(f"SystemSpine -> dat_manager = {data_manager}")


    # Phase 2 - Module-specific class functions in 'System[ModuleName]'
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
        joint_grp = f"grp_joints_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        utils.cr_node_if_not_exists(0, "transform", joint_grp)
        for skn in skn_start_end_ls:
            cmds.parent(skn, joint_grp)
        for skn in skn_jnt_chain_ls: 
            cmds.parent(skn[0], joint_grp)

        return joint_grp


    def add_custom_input_attr(self, inputs_grp, jnt_num):
        '''
        # Description:
            Add module uniwue attributes to the input group.
        # Attributes:
            inputs_grp (string): Outputgrpup for this module.
        # Returns: N/A
        '''
        for x in range(jnt_num):
            utils.add_float_attrib(inputs_grp, [f"{self.dm.mdl_nm}{x}_Stretch_Volume"], [1.0, 1.0], False)
            cmds.setAttr(f"{inputs_grp}.{self.dm.mdl_nm}{x}_Stretch_Volume", keyable=1, channelBox=1)
            cmds.setAttr(f"{inputs_grp}.{self.dm.mdl_nm}{x}_Stretch_Volume", -0.5)


    def wire_spine_ctrls(self, input_grp, fk_ctrl_ls, inv_ctrl_ls, ik_ctrl_ls):
        '''
        TO DO:
            Add rotation data too w/ 'self.dm.fk_rot_dict (dict)' & 'self.dm.ik_rot_dict (dict)'.
        # Description:
            Sets up the control's relationship, positions them using matrix data 
            as well as how the 3 states work together:
            - Fk controls setup.
            - InverseFK control setup.
            - End fk controls Top ik ctrl.
            - End fkInv controls Bottom ik ctrl.
            - IK Top & Bottom controls share the control over the middle control.
            This works by using the data of 'self.dm.fk_pos_dict (dict)' & 'self.dm.ik_pos_dict (dict)'
            but not any rotation values are applied atm. 
        # Attributes:
            input_grp (string): Group for input data for this module.
        # Returns: N/A
        '''
        # ---------------------------------------------------------------------
        # FK & Inv ctrl setup
        # Initalise inv pos & rot dicts by reversing the values. 
        inv_pos_dict = utils.reverse_dict(self.dm.fk_pos_dict)
        inv_rot_dict = utils.reverse_dict(self.dm.fk_rot_dict)

        # Create the first [0] fk & inv utility nodes 
        MM_fk_0 = f"MM_{fk_ctrl_ls[0]}"
        MM_inv_0 = f"MM_{inv_ctrl_ls[0]}"
            # cr the MM nodes
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_fk_0)
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_inv_0)
            # append their names to the list
        print(f"MM_fk_ls = `{MM_fk_0}`")
        print(f"MM_inv_ls = `{MM_inv_0}`")

        # wire the fk & inv 0 MMs
        utils.set_transformation_matrix(list(self.dm.fk_pos_dict.values())[0], list(self.dm.fk_rot_dict.values())[0], f"{MM_fk_0}{utils.Plg.mtx_ins[0]}")
        utils.set_transformation_matrix(list(inv_pos_dict.values())[0], list(inv_rot_dict.values())[0], f"{MM_inv_0}{utils.Plg.mtx_ins[0]}")
    
        utils.connect_attr(f"{input_grp}.hook_mtx", f"{MM_fk_0}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{input_grp}.hook_mtx", f"{MM_inv_0}{utils.Plg.mtx_ins[1]}")

        utils.connect_attr(f"{MM_fk_0}{utils.Plg.mtx_sum_plg}", f"{fk_ctrl_ls[0]}{utils.Plg.opm_plg}")
        utils.connect_attr(f"{MM_inv_0}{utils.Plg.mtx_sum_plg}", f"{inv_ctrl_ls[0]}{utils.Plg.opm_plg}")

        ''''''
        # cr temp locators for FK & Inv ctrls local space. 
        fk_temp_loc_ls = []
        for (key, pos_val), (key, rot_val) in zip(self.dm.fk_pos_dict.items(), self.dm.fk_rot_dict.items()):
            loc_name = key.replace('ctrl_fk_', 'loc_tempFk_')# "ctrl_fk_bipedArm_'first parent'_0_L"
            fk_temp_loc_ls.append(loc_name)
            cmds.spaceLocator(n=loc_name)
            cmds.xform(loc_name, t=pos_val, ws=1)
            cmds.xform(loc_name, rotation=rot_val, ws=1)
        try:
            for i in range(len(fk_temp_loc_ls)):
                cmds.parent(fk_temp_loc_ls[i+1],fk_temp_loc_ls[i])
        except IndexError:
            pass
        
        inv_temp_loc_ls = []
        for (key, pos_val), (key, rot_val) in zip(inv_pos_dict.items(), inv_rot_dict.items()):
            loc_name = key.replace('ctrl_fk_', 'loc_tempInv_')# "ctrl_fk_bipedArm_'first parent'_0_L"
            inv_temp_loc_ls.append(loc_name)
            cmds.spaceLocator(n=loc_name)
            cmds.xform(loc_name, t=pos_val, ws=1)
            cmds.xform(loc_name, rotation=rot_val, ws=1)
        try:
            for i in range(len(inv_temp_loc_ls)):
                cmds.parent(inv_temp_loc_ls[i+1],inv_temp_loc_ls[i])
        except IndexError:
            pass

        # Foward kinematic matrix setup w/ temp locators
        for x in range(1, len(self.dm.fk_ctrl_list)):
            utils.matrix_control_FowardKinematic_setup(fk_ctrl_ls[x-1], fk_ctrl_ls[x], fk_temp_loc_ls[x])
        
        print(f"inv_ctrl_ls = `{inv_ctrl_ls}`")
        for x in range(1, len(inv_ctrl_ls)):
            utils.matrix_control_FowardKinematic_setup(inv_ctrl_ls[x-1], inv_ctrl_ls[x], inv_temp_loc_ls[x])

        cmds.delete(fk_temp_loc_ls[0], inv_temp_loc_ls[0])

        # ---------------------------------------------------------------------
        # IK ctrl top & bottom setup
        # wire hierarchy: FK > IK_Top | Inv > IK_Bott | IK_top/bott > IK_mid
            # cr the MM for ik ctrls!
        MM_ik_ls = []
        # ik_ctrl_ls = []
        for ik_ctrl_name in self.dm.ik_pos_dict.keys():
            # ik_ctrl_ls.append(ik_ctrl_name)
            MM_ik_name = f"MM_{ik_ctrl_name}"
            utils.cr_node_if_not_exists(1, 'multMatrix', MM_ik_name)
            MM_ik_ls.append(MM_ik_name)
        # add squash attr to top ik ctrl
        utils.add_locked_attrib(ik_ctrl_ls[-1], ["Attributes"])
        utils.add_float_attrib(ik_ctrl_ls[-1], [f"{self.dm.mdl_nm}_Stretch_State"], [0, 1], True)
        utils.add_float_attrib(ik_ctrl_ls[-1], [f"{self.dm.mdl_nm}_Stretch_Anchor"], [0, 1], True)
        utils.add_float_attrib(ik_ctrl_ls[-1], [f"{self.dm.mdl_nm}_Stretch_Volume"], [0, 1], True)

        # proxy the stretch attributes to the other ikctrls!
        for remaining_ik_ctrl in ik_ctrl_ls[:-1]:
            utils.proxy_attr_list(ik_ctrl_ls[-1], remaining_ik_ctrl, "attributes_dvdr")
            utils.proxy_attr_list(ik_ctrl_ls[-1], remaining_ik_ctrl, f"{self.dm.mdl_nm}_Stretch_State")
            utils.proxy_attr_list(ik_ctrl_ls[-1], remaining_ik_ctrl, f"{self.dm.mdl_nm}_Stretch_Anchor")
            utils.proxy_attr_list(ik_ctrl_ls[-1], remaining_ik_ctrl, f"{self.dm.mdl_nm}_Stretch_Volume")

        # top > matrixIn[0]/[1]
        utils.wire_ofs_mtxIn0_1_to_1([self.dm.fk_pos_dict, self.dm.fk_rot_dict], 
                               [self.dm.ik_pos_dict, self.dm.ik_rot_dict],
                               [-1], [-1],
                               MM_ik_ls[-1])
        utils.connect_attr(f"{fk_ctrl_ls[-1]}{utils.Plg.wld_mtx_plg}", f"{MM_ik_ls[-1]}{utils.Plg.mtx_ins[1]}") # MM_ik_top
        
        # bottom > matrixIn[0]/[1]
        utils.wire_ofs_mtxIn0_1_to_1([inv_pos_dict, inv_rot_dict], 
                               [self.dm.ik_pos_dict, self.dm.ik_rot_dict],
                               [-1], [0],
                               MM_ik_ls[0])
        utils.connect_attr(f"{inv_ctrl_ls[-1]}{utils.Plg.wld_mtx_plg}", f"{MM_ik_ls[0]}{utils.Plg.mtx_ins[1]}") # MM_ik_bottom
        
        # IK middle ctrl wires ------------------------------------------------
        twist_axis = self.dm.prim_axis
        # calc this by the givin rotation values)
            # Blend matrix for pos between top & bottom
            # 2 flt nodes, 1 aim matracies & 1 CM for twisting
        BM_ik_mid = f"BM_{ik_ctrl_ls[1]}"
        utils.cr_node_if_not_exists(1, "blendMatrix", BM_ik_mid)
        AM_ik_mid =  f"AM_sub_{ik_ctrl_ls[1]}"
        if twist_axis == "X":
            utils.cr_node_if_not_exists(0, "aimMatrix", AM_ik_mid) 
        elif twist_axis == "Y":
            utils.cr_node_if_not_exists(0, "aimMatrix", AM_ik_mid, {f"primaryInputAxis{twist_axis}":1, "primaryInputAxisX":0}) 
        FM_ik_mid_sub = f"FM_sub_{ik_ctrl_ls[1]}"
        FM_ik_mid_div = f"FM_div_{ik_ctrl_ls[1]}"
        utils.cr_node_if_not_exists(1, "floatMath", FM_ik_mid_sub, {"operation":1})
        utils.cr_node_if_not_exists(1, "floatMath", FM_ik_mid_div, {"operation":2, "floatB":0.5}) 
        CM_ik_mid =  f"CM_{ik_ctrl_ls[1]}"
        utils.cr_node_if_not_exists(1, "composeMatrix", CM_ik_mid)

        # Connections
        bot_ik_ctrl = ik_ctrl_ls[0]
        top_ik_ctrl = ik_ctrl_ls[-1]
            # for MM_mid_ctrl -> matrixIn[0]
        utils.connect_attr(f"{bot_ik_ctrl}.rotate{twist_axis}", f"{FM_ik_mid_sub}{utils.Plg.flt_A}")
        utils.connect_attr(f"{top_ik_ctrl}.rotate{twist_axis}", f"{FM_ik_mid_sub}{utils.Plg.flt_B}")
        utils.connect_attr(f"{FM_ik_mid_sub}{utils.Plg.out_flt}", f"{FM_ik_mid_div}{utils.Plg.flt_A}")
        utils.connect_attr(f"{FM_ik_mid_div}{utils.Plg.out_flt}", f"{CM_ik_mid}.inputRotate{twist_axis}")
        utils.connect_attr(f"{CM_ik_mid}{utils.Plg.out_mtx_plg}", f"{MM_ik_ls[1]}{utils.Plg.mtx_ins[0]}")
            # # for MM_mid_ctrl -> matrixIn[1]
        utils.connect_attr(f"{bot_ik_ctrl}{utils.Plg.wld_mtx_plg}", f"{BM_ik_mid}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{top_ik_ctrl}{utils.Plg.wld_mtx_plg}", f"{BM_ik_mid}{utils.Plg.target_mtx[0]}")
        cmds.setAttr(f"{BM_ik_mid}.target[0].translateWeight", 0.5)
        utils.connect_attr(f"{BM_ik_mid}{utils.Plg.out_mtx_plg}", f"{AM_ik_mid}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{top_ik_ctrl}{utils.Plg.wld_mtx_plg}", f"{AM_ik_mid}.primaryTargetMatrix")
        utils.connect_attr(f"{top_ik_ctrl}{utils.Plg.wld_mtx_plg}", f"{AM_ik_mid}.secondaryTargetMatrix")
        utils.connect_attr(f"{AM_ik_mid}{utils.Plg.out_mtx_plg}", f"{MM_ik_ls[1]}{utils.Plg.mtx_ins[1]}")

        # connect all MMs to all ik ctrls
        for x in range(len(MM_ik_ls)):
            utils.connect_attr(f"{MM_ik_ls[x]}{utils.Plg.mtx_sum_plg}", f"{ik_ctrl_ls[x]}{utils.Plg.opm_plg}")
        

    def cr_logic_elements(self, fk_pos, fk_rot, ik_pos, ik_rot, fw_jnt_lists, bw_jnt_lists, rig_jnt_lists):
        '''        
        # Description:
            Creates all new logic joints (fk, inv, ik) & organises them into new 
            logic groups that are created here as well as the other logic joint 
            chains such as fw_jnt_chain's, bw_jnt_chain's and rig_jnt_chain's. 
        # Attributes:
            fk_pos (dict): key = fk ctrl name, value = positonal data.
            fk_rot (dict): key = fk ctrl name, value = rotational data.
            ik_pos (dict): key = ik ctrl name, value = positonal data.
            ik_rot (dict): key = ik ctrl name, value = rotational data.
            fw_jnt_lists (list): contains the 2 fw joint chain lists (str & nonStr).
            bw_jnt_lists (list): contains the 2 bw joint chain lists (str & nonStr).
            rig_jnt_ls (list): contains the 2 rig joint chain lists (str & nonStr).
        # Returns:
            logic_grp (string): Logic group for this module stores all logic elements in rig. 
            fk_logic_ls (list): The list of fk logic joints created. 
            inv_logic_ls (list): The list of fkInv logic joints created. 
            ik_logic_ls (list): The list of ik logic joints created. 
            jnt_mid_hold (string): The ik middle hold logic joint created. 
        '''
        # establish the inv dictionary's
        # inv_pos_values = list(fk_pos.values())[::-1]
        # inv_rot_values = list(fk_rot.values())[::-1]
        # inv_pos = {key: inv_pos_values[i] for i, key in enumerate(fk_pos.keys())}
        # inv_rot = {key: inv_rot_values[i] for i, key in enumerate(fk_pos.keys())}
        # cr 6 groups to organise the joints into:
        logic_grp = f"grp_logic_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        fk_grp = f"grp_jnts_fk_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        inv_grp = f"grp_jnts_inv_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        ik_grp = f"grp_jnts_ik_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        ikFw_grp = f"grp_ikFw_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        ikBw_grp = f"grp_ikBw_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        utils.cr_node_if_not_exists(0, "transform", logic_grp)
        utils.cr_node_if_not_exists(0, "transform", fk_grp)
        utils.cr_node_if_not_exists(0, "transform", inv_grp)
        utils.cr_node_if_not_exists(0, "transform", ik_grp)
        utils.cr_node_if_not_exists(0, "transform", ikFw_grp)
        utils.cr_node_if_not_exists(0, "transform", ikBw_grp)
        
        fk_logic_ls = []
        inv_logic_ls = []
        ik_logic_ls = []
        # cr the logic joints!
        for spn_name in fk_pos:
            cmds.select(cl=1)
            fk_name = spn_name.replace("ctrl_", "jnt_") # ctrl_fk_{self.dm.mdl_nm}0
            fk_logic_ls.append(fk_name)
            inv_name = spn_name.replace("ctrl_fk_", "jnt_inv_") # ctrl_fk_{self.dm.mdl_nm}0
            inv_logic_ls.append(inv_name)
            cmds.joint(n=fk_name)
            cmds.select(cl=1)
            cmds.joint(n=inv_name)
            cmds.makeIdentity(fk_name, a=1, t=0, r=1, s=0, n=0, pn=1)
            cmds.makeIdentity(inv_name, a=1, t=0, r=1, s=0, n=0, pn=1)

        for spn_name in ik_pos:
            cmds.select(cl=1)
            ik_name = spn_name.replace("ctrl_", "jnt_")
            ik_logic_ls.append(ik_name)    
            cmds.joint(n=ik_name)
            cmds.makeIdentity(ik_name, a=1, t=0, r=1, s=0, n=0, pn=1)
        
        # Create the jnt_ik_middleHold 
        jnt_mid_hold = cmds.joint(n=f"jnt_ik_{self.dm.mdl_nm}_middleHold")

        # Parent the joints into the right groups:
        cmds.parent(fk_logic_ls, fk_grp)
        cmds.parent(inv_logic_ls, inv_grp)
        cmds.parent(ik_logic_ls, jnt_mid_hold, ik_grp)
        for fw, bw, rig in zip(fw_jnt_lists, bw_jnt_lists, rig_jnt_lists):
            cmds.parent(fw[0], ikFw_grp)
            cmds.parent(bw[0], ikBw_grp)
            cmds.parent(rig[0], logic_grp)
        cmds.parent(fk_grp, inv_grp, ik_grp, ikFw_grp, ikBw_grp, logic_grp)
    
        return logic_grp, fk_logic_ls, inv_logic_ls, ik_logic_ls, jnt_mid_hold


    def cr_logic_curve(self, pref, skeleton_pos_dict, logic_grp, backwards=False):
        '''        
        # Description:
            Creates a new logic curve & organises it into the logic_grp. 
        # Attributes:
            pref (string): name of the joint chain type.
            skeleton_pos_dict (dict): key = name of spine iteration (spine#), value = positonal data.
            backwards (bool): If True, the curve direction is reversed (0-1).
        # Returns:
            logic_curve (string): The name of the new curve created. 
        '''
        logic_curve = f"crv_{pref}_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        positions = list(skeleton_pos_dict.values())
        cmds.curve(n=logic_curve, d=3, p=positions)
        cmds.rebuildCurve(logic_curve, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=0, kt=0, s=1, d=3, tol=0.01)
        if backwards:
            ''' reverse the dirtection of the curve '''
            cmds.reverseCurve(logic_curve, constructionHistory=True, replaceOriginal=True)
        cmds.parent(logic_curve, logic_grp)

        return logic_curve


    def wire_ik_curve_setup(self, jnt_pref, logic_curve, input_grp):
        '''        
        # Description:
            Connects the data from provided curve & using utility nodes, retrieves 
            neccessary data for driving the joints to follow the curve, joints stretch, etc. 
        # Attributes:
            jnt_pref (string): name of the joint chai direction (Fw or Bw).
            logic_curve (string): The name of the new curve created.
            input_grp (string): Group for input data for this module.
        # Returns:
            CvInfo (utility): curve_info node of the curve. 
            FM_spine_global (utility): Float math node of the arclenght and 'globalScale' passed to this module. 
        '''
        # Curve shape name & cluster!
        crv_logic_shape = cmds.listRelatives(logic_curve, s=1)[0]

        print(f"crv_logic_shape = {crv_logic_shape}")
        # curve util nodes 
        CvInfo = f"CI_{jnt_pref}_{self.dm.mdl_nm}_{self.dm.unique_id}"
        utils.cr_node_if_not_exists(1, "curveInfo", CvInfo)
        utils.connect_attr(f"{crv_logic_shape}{utils.Plg.wld_space_plg}", 
                           f"{CvInfo}{utils.Plg.inp_curve_plg}")
        FM_spine_global = f"FM_{jnt_pref}_{self.dm.mdl_nm}_global_div_{self.dm.unique_id}"
        utils.cr_node_if_not_exists(1, "floatMath", FM_spine_global, {"operation": 3})
        # connections
            # global FM
        utils.connect_attr(f"{CvInfo}{utils.Plg.arc_len_plg}", f"{FM_spine_global}{utils.Plg.flt_A}")
        utils.connect_attr(f"{input_grp}.globalScale", f"{FM_spine_global}{utils.Plg.flt_B}")

        return CvInfo, FM_spine_global


    def wire_ctrl_to_jnt_logic(self, fk_ctrl_ls, inv_ctrl_ls, ik_ctrl_ls, 
                                    fk_logic_ls, inv_logic_ls, ik_logic_ls):
        '''        
        # Description:            
            Connects all control's to their corresponding logic joint using 
            matrix data. For this to work, I wrote a utility function that creates 
            a MultMatrix to directly connect the ctrl's mtx to joints' mtx. The 
            MultMatrix is if any offsets want to be included in the future, but 
            by default it has none. So becomes a derict connection essentially.  
        # Attributes: N/A
        # Returns: N/A
        '''
        for fk_ctrl, inv_ctrl, ik_ctrl, fk_logic, inv_logic, ik_logic in zip(
            fk_ctrl_ls, inv_ctrl_ls, ik_ctrl_ls, 
            fk_logic_ls, inv_logic_ls, ik_logic_ls
            ):
            print(f"fk_ctrl = {fk_ctrl} | {fk_logic}")
            print(f"inv_ctrl = {inv_ctrl} | {inv_logic}")
            print(f"fk_ctrl = {ik_ctrl} | {ik_logic}")
            MM_fk_logic = utils.mtxCon_no_ofs(fk_ctrl, fk_logic)
            MM_inv_logic = utils.mtxCon_no_ofs(inv_ctrl, inv_logic)
            MM_ik_logic = utils.mtxCon_no_ofs(ik_ctrl, ik_logic)


    def wire_ik_bott_top_logic_to_skn(self, jnt_pref, skeleton_pos_dict, 
                                            ik_logic_ls, ik_ctrl_ls):
        '''
        # Description:            
            This function drives the Top & Bottom skin joints important for 
            deforming the top and bottom of the spine module. 
            Using Logic joints (top & bot) matrix's rotation data.
            Using skin joint chain's (top & bot) matrix's translation data.
            This seperated method is important to provide the best deformation 
            repective of the animator's control over the rig.  
        # Attributes:
            jnt_pref (string): name of the joint chain type -> needs to be 'skn'.
            skeleton_pos_dict (dict): key = name of spine iteration (spine#), value = positonal data.
        # Returns: N/A
        '''
        skn_skel_keys = list(skeleton_pos_dict.keys())
        skn_skel_positions = [int(re.search(r'\d+', s).group()) for s in skn_skel_keys][::-1]
        print(f"skn_skel_positions = `{skn_skel_positions}`")
        
        skn_top_jnt = ik_logic_ls[-1].replace('ik', jnt_pref)
        skn_bot_jnt = ik_logic_ls[0].replace('ik', jnt_pref)
        cmds.setAttr(f"{skn_top_jnt}.radius", 3)
        cmds.setAttr(f"{skn_bot_jnt}.radius", 3)

        # check if skn has none default values
        if not utils.check_non_default_transforms(skn_bot_jnt) or utils.check_non_default_transforms(skn_top_jnt):
            print(f"{skn_bot_jnt} & {skn_top_jnt} have none default values and require cleaning")
            utils.clean_opm([skn_bot_jnt, skn_top_jnt])

        # get the names of the top ik_jnt & skn_chain joint
        top_ik_jnt = ik_logic_ls[-1]
        bottom_ik_jnt = ik_logic_ls[0]
        # 'output_skn_jnt' refers to the skn joint chain!
        top_output_skn_jnt = f"jnt_{jnt_pref}_{self.dm.mdl_nm}_spine{skn_skel_positions[0]}_{self.dm.unique_id}_{self.dm.side}"
        bottom_output_skn_jnt = f"jnt_{jnt_pref}_{self.dm.mdl_nm}_spine{skn_skel_positions[-1]}_{self.dm.unique_id}_{self.dm.side}"
        
        top_ik_ctrl = ik_ctrl_ls[-1]
        bottom_ik_ctrl = ik_ctrl_ls[0]

        # cr two decompose matrix nodes & a compMatrix node for each jnt_skn_top/bottom
        top_translate_skn_dcM = f"DCM_translate_top_{top_output_skn_jnt}"
        top_rotate_dcM = f"DCM_rotate_top_{top_ik_jnt}"
        top_cM = f"CM_driver_{skn_top_jnt}"
        bottom_translate_dcM = f"DCM_translate_bot_{bottom_output_skn_jnt}"
        bottom_rotate_dcM = f"DCM_rotate_bot_{bottom_ik_jnt}"
        bottom_cM = f"CM_driver_{skn_bot_jnt}"
        utils.cr_node_if_not_exists(0, "decomposeMatrix", top_translate_skn_dcM)
        utils.cr_node_if_not_exists(0, "decomposeMatrix", top_rotate_dcM)
        utils.cr_node_if_not_exists(0, "composeMatrix", top_cM)
        utils.cr_node_if_not_exists(0, "decomposeMatrix", bottom_translate_dcM)
        utils.cr_node_if_not_exists(0, "decomposeMatrix", bottom_rotate_dcM)
        utils.cr_node_if_not_exists(0, "composeMatrix", bottom_cM)

        # two new utility nodes for the translate data to compose to the skin joint. 
            # translate is a switch between 2 objects: 'top_output_skn_jnt' & 'ik_ctrl_ls[-1]' depending(SecondTerm) on the stretch_state atribute 
            # DCM for ik_ctrl_ls[-1]
        top_translate_ctrl_dcM = f"DCM_translate_top_{top_ik_ctrl}"
        top_translate_cond = f"DCM_translate_top_{skn_top_jnt}"
        bottom_translate_ctrl_dcM = f"DCM_translate_bot_{bottom_ik_ctrl}"
        bottom_translate_cond = f"DCM_translate_bot_{skn_bot_jnt}"
        
        utils.cr_node_if_not_exists(0, "decomposeMatrix", top_translate_ctrl_dcM)
        utils.cr_node_if_not_exists(0, "condition", top_translate_cond, {"operation":5, "firstTerm": 0.95})        
        utils.cr_node_if_not_exists(0, "decomposeMatrix", bottom_translate_ctrl_dcM)
        utils.cr_node_if_not_exists(0, "condition", bottom_translate_cond, {"operation":5, "firstTerm": 0.95})    

        # wire top
            # > DCM.inputMatrix
        utils.connect_attr(f"{top_output_skn_jnt}{utils.Plg.wld_mtx_plg}", f"{top_translate_skn_dcM}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{top_ik_ctrl}{utils.Plg.wld_mtx_plg}", f"{top_translate_ctrl_dcM}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{top_ik_jnt}{utils.Plg.wld_mtx_plg}", f"{top_rotate_dcM}{utils.Plg.inp_mtx_plg}")
            # > top_translate_cond
        utils.connect_attr(f"{top_ik_ctrl}.{self.dm.mdl_nm}_Stretch_State", f"{top_translate_cond}.secondTerm")
        utils.connect_attr(f"{top_translate_ctrl_dcM}{utils.Plg.outT_plug}", f"{top_translate_cond}.colorIfTrue")
        utils.connect_attr(f"{top_translate_skn_dcM}{utils.Plg.outT_plug}", f"{top_translate_cond}.colorIfFalse")
            # > CM.inputTranslate/Rotate
        utils.connect_attr(f"{top_translate_cond}.outColor", f"{top_cM}{utils.Plg.inputT_plug}")
        utils.connect_attr(f"{top_rotate_dcM}{utils.Plg.outR_plug}", f"{top_cM}{utils.Plg.inputR_plug}")
            # > skn_top_jnt.OPM
        utils.connect_attr(f"{top_cM}{utils.Plg.out_mtx_plg}", f"{skn_top_jnt}{utils.Plg.opm_plg}")

        # wire bottom
        utils.connect_attr(f"{bottom_output_skn_jnt}{utils.Plg.wld_mtx_plg}", f"{bottom_translate_dcM}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{bottom_ik_ctrl}{utils.Plg.wld_mtx_plg}", f"{bottom_translate_ctrl_dcM}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{bottom_ik_jnt}{utils.Plg.wld_mtx_plg}", f"{bottom_rotate_dcM}{utils.Plg.inp_mtx_plg}")

        utils.connect_attr(f"{bottom_ik_ctrl}.{self.dm.mdl_nm}_Stretch_State", f"{bottom_translate_cond}.secondTerm")
        utils.connect_attr(f"{bottom_translate_ctrl_dcM}{utils.Plg.outT_plug}", f"{bottom_translate_cond}.colorIfTrue")
        utils.connect_attr(f"{bottom_translate_dcM}{utils.Plg.outT_plug}", f"{bottom_translate_cond}.colorIfFalse")
        
        utils.connect_attr(f"{bottom_translate_cond}.outColor", f"{bottom_cM}{utils.Plg.inputT_plug}")
        utils.connect_attr(f"{bottom_rotate_dcM}{utils.Plg.outR_plug}", f"{bottom_cM}{utils.Plg.inputR_plug}")
        
        utils.connect_attr(f"{bottom_cM}{utils.Plg.out_mtx_plg}", f"{skn_bot_jnt}{utils.Plg.opm_plg}")

    
    def wire_ik_stretch_setup(self, jnt_pref, logic_curve, skeleton_pos_dict, fm_global_curve, 
                                    ik_logic_ls, ik_ctrl_ls, jnt_mid_hold, backwards=False):
        '''
        # Description:            
            Creates stretch setup on specified joint chain with an ik spline setup. 
            Intentionally keeping the stretch on at all time & not connecting the stretch_state attr.
        # Attributes:
            jnt_pref (string): name of the joint chain to cr stretch setup on.
            logic_curve (string): The name of the new curve created.
            skeleton_pos_dict (dict): key = name of spine iteration (spine#), value = positonal data.
            fm_global_curve (utility): Float math node of the arclenght and 'globalScale' passed to this module.
            backwards (bool): If True, the curve direction is reversed (0-1).
        # Returns: N/A
        '''
        jnt_skeleton_ls = [f"jnt_{jnt_pref}_{self.dm.mdl_nm}_{j}_{self.dm.unique_id}_{self.dm.side}" for j in skeleton_pos_dict.keys()]
        num_squash_jnts = len(skeleton_pos_dict.keys())-1
        
        print(f"jnt_skeleton_ls = `{jnt_skeleton_ls}`")
        print(f"num_squash_jnts = `{num_squash_jnts}`")

        '''
        correct: 

        this: 

        '''

        # curve skinning method: skin the top & bottom ik skn joints to curve skin 
        # the middle & hold logic joints create inversmatrix, > plug middle MM into inversmatrix
        # > plug inversematrix into bind bind pre-matrix on the 2nd skincluster!
        jnt_ik_logic_mid = ik_logic_ls[1]
        cmds.skinCluster([ik_logic_ls[0], ik_logic_ls[-1]], logic_curve, tsb=True, wd=1)[0]
        # # Create the second skinCluster
        middle_skincluster = cmds.skinCluster([jnt_ik_logic_mid, jnt_mid_hold], logic_curve, tsb=True, wd=1, multi=1)[0]
        cmds.skinPercent( middle_skincluster, f"{logic_curve}.cv[0]", f"{logic_curve}.cv[3]", tv=[(jnt_mid_hold, 1)])
        # skinPercent -tv jnt_hold  1 skinCluster4 curve1.cv[0:1] curve1.cv[4:5]

        inv_mtx = f"IM_{jnt_ik_logic_mid}"
        utils.cr_node_if_not_exists(1, "inverseMatrix", inv_mtx)
        utils.connect_attr(f"MM_{ik_ctrl_ls[1]}{utils.Plg.mtx_sum_plg}", f"{inv_mtx}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{inv_mtx}{utils.Plg.out_mtx_plg}", f"{middle_skincluster}.bindPreMatrix[0]")
        
        # Util nodes for stretch setup
        FM_spine_joints = f"FM_{jnt_pref}_{self.dm.mdl_nm}_joints_div_{self.dm.unique_id}"
        BC_spine_squash = F"BC_{jnt_pref}_{self.dm.mdl_nm}_stretchVolume_{self.dm.unique_id}"

        utils.cr_node_if_not_exists(1, "floatMath", FM_spine_joints, {"operation": 3, "floatB": num_squash_jnts})
        utils.cr_node_if_not_exists(1, "blendColors", BC_spine_squash, {"color1G": 1, "color2R": 1, "color2G": 1, "color2B": 1})
       
           # joints FM
        utils.connect_attr(f"{fm_global_curve}{utils.Plg.out_flt}", f"{FM_spine_joints}{utils.Plg.flt_A}")
        
        # This provides the stretch effect by moving the joints. 
        #---- skeleton transaltion PRIMARY AXIS joint!
        # get FM_spine_joints_div.floatA attr and set it to new 
        still_stretch_dividend = cmds.getAttr(f"{FM_spine_joints}{utils.Plg.flt_A}")
        # cr utility nodes neccessary to blend a smooth on & off of the stretch
        FM_trans_still = f"FM_{jnt_pref}_{self.dm.mdl_nm}_joints_div_still_{self.dm.unique_id}"
        BC_stretch_active = F"BC_{jnt_pref}_{self.dm.mdl_nm}_activeStretch_{self.dm.unique_id}"
        BC_stretch_still = F"BC_{jnt_pref}_{self.dm.mdl_nm}_stillStretchLength_{self.dm.unique_id}"
        BC_stretch_output = F"BC_{jnt_pref}_{self.dm.mdl_nm}_translateStretchOutput_{self.dm.unique_id}"
        utils.cr_node_if_not_exists(1, "floatMath", FM_trans_still, {"operation": 3, "floatA": still_stretch_dividend, "floatB": num_squash_jnts})
        utils.cr_node_if_not_exists(1, "blendColors", BC_stretch_active, {"blender":1, "color1G": 1, "color2R": 1, "color2G": 1, "color2B": 1})
        utils.cr_node_if_not_exists(1, "blendColors", BC_stretch_still, {"blender":1, "color1G": 1, "color2R": 1, "color2G": 1, "color2B": 1})
        utils.cr_node_if_not_exists(1, "blendColors", BC_stretch_output, {"blender":1, "color1G": 1, "color2R": 1, "color2G": 1, "color2B": 1})
        
        # connect FM to child BC's
        utils.connect_attr(f"{FM_spine_joints}{utils.Plg.out_flt}", f"{BC_stretch_active}{utils.Plg.color1_plg[0]}")
        utils.connect_attr(f"{FM_trans_still}{utils.Plg.out_flt}", f"{BC_stretch_still}{utils.Plg.color1_plg[0]}")
        # connect child BC's to parent BC  
        utils.connect_attr(f"{BC_stretch_active}{utils.Plg.out_letter[0]}", f"{BC_stretch_output}{utils.Plg.color1_plg[0]}")
        utils.connect_attr(f"{BC_stretch_still}{utils.Plg.out_letter[0]}", f"{BC_stretch_output}{utils.Plg.color2_plg[0]}")
        # Connect 'stetch' attrib to parent BC blender.
        # utils.connect_attr(f"{ik_ctrl_ls[-1]}.{self.dm.mdl_nm}_Stretch_State", f"{BC_stretch_output}{utils.Plg.blndr_plg}")
        
        if backwards:
            # cr negative MD
            md_negative = f"MD_{jnt_pref}_{self.dm.mdl_nm}_negativeStretchOutput_{self.dm.unique_id}"
            utils.cr_node_if_not_exists(1, "multiplyDivide", md_negative, {"operation": 1, "input1X":-1})
            # connect parent BC to negative MD            
            utils.connect_attr(f"{BC_stretch_output}{utils.Plg.out_letter[0]}", f"{md_negative}{utils.Plg.input2_val[0]}")
            for x in range(1, len(skeleton_pos_dict.keys())):  
                # connect negative MD to skeleton translatePrimaryAxis. 
                utils.connect_attr(f"{md_negative}{utils.Plg.out_axis[0]}", f"{jnt_skeleton_ls[x]}.translate{self.dm.prim_axis}")
        else:
            for x in range(1, len(skeleton_pos_dict.keys())):  
                # connect BC_spine_StretchOutput to skeleton translatePrimaryAxis. 
                utils.connect_attr(f"{BC_stretch_output}{utils.Plg.out_letter[0]}", f"{jnt_skeleton_ls[x]}.translate{self.dm.prim_axis}")
        
        # ---------------
        # ik spline setup w/ advanced twist on ik handle
        print(f"ikHandle: jnt_pref = `{jnt_pref}`, jnt_skeleton_ls[-1] = {jnt_skeleton_ls[-1]}, jnt_skeleton_ls[0] = {jnt_skeleton_ls[0]},")
        
        hdl_spine_name = f"hdl_{jnt_pref}_{self.dm.mdl_nm}_spline_{self.dm.unique_id}_{self.dm.side}"
        cmds.ikHandle( n=hdl_spine_name, sol="ikSplineSolver", c=logic_curve, sj=jnt_skeleton_ls[0], ee=jnt_skeleton_ls[-1], ccv=False, pcv=False)
        cmds.parent(hdl_spine_name, f"grp_logic_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}")
        # Enable advanced twist options on hdl_spine_name
        cmds.setAttr(  f"{hdl_spine_name}.dTwistControlEnable", 1 )
        cmds.setAttr( f"{hdl_spine_name}.dWorldUpType", 4 )              
        
        
        if self.dm.prim_axis == "X":
            if backwards:
                dForwardAxis = 1 # negativeX
            else:
                dForwardAxis = 0 # positiveX
            dWorldUpAxis = 0 # PositiveY
            dWorldUpVectorX = 0
            dWorldUpVectorY = 1
            dWorldUpVectorZ = 0

        elif self.dm.prim_axis == "Y":
            if backwards:
                dForwardAxis = 3 # negativeY
            else:
                dForwardAxis = 2 # positiveY
            dWorldUpAxis = 3 # PositiveZ
            dWorldUpVectorX = 0
            dWorldUpVectorY = 0
            dWorldUpVectorZ = 1

        cmds.setAttr(f"{hdl_spine_name}.dForwardAxis", dForwardAxis)
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpAxis", dWorldUpAxis )
        # Xvals
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpVectorX", dWorldUpVectorX)
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpVectorEndX", dWorldUpVectorX)
        # Yvals
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpVectorY", dWorldUpVectorY)
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpVectorEndY", dWorldUpVectorY)
        # Zvals
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpVectorZ", dWorldUpVectorZ)
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpVectorEndZ", dWorldUpVectorZ)

        if backwards:
            # Set the 'World Up Object' to the controller the is driving the first joint of the chain. (ctrl_ik_pelvis)
            utils.connect_attr(f"{ik_ctrl_ls[-1]}{utils.Plg.wld_mtx_plg}", f"{hdl_spine_name}.dWorldUpMatrix")
            utils.connect_attr(f"{ik_ctrl_ls[0]}{utils.Plg.wld_mtx_plg}", f"{hdl_spine_name}.dWorldUpMatrixEnd")
        else:
            utils.connect_attr(f"{ik_ctrl_ls[0]}{utils.Plg.wld_mtx_plg}", f"{hdl_spine_name}.dWorldUpMatrix")
            utils.connect_attr(f"{ik_ctrl_ls[-1]}{utils.Plg.wld_mtx_plg}", f"{hdl_spine_name}.dWorldUpMatrixEnd")
                  

    def wire_ik_volume_setup(self, jnt_pref, skeleton_pos_dict, input_grp, cv_info_node, fm_global_curve, ik_ctrl_ls):
        '''
        # Description:            
            Wires the data from the Input grp to the skin joint's scale attr to 
            control Volume preservation when the joint's stretch.
        # Attributes:
            jnt_pref (string): name of the joint chain to cr stretch setup on.
            skeleton_pos_dict (dict): key = name of spine iteration (spine#), value = positonal data.
            input_grp (string): Group for input data for this module.
            fm_global_curve (utility): Float math node of the arclenght and 'globalScale' passed to this module.
        # Returns: N/A
        '''
        cv_arc_length = cmds.getAttr(f"{cv_info_node}{utils.Plg.arc_len_plg}")

        FM_spine_norm = F"FM_{self.dm.mdl_nm}_norm_{self.dm.unique_id}"
        BC_spine_squash = F"BC_{self.dm.mdl_nm}_stretchVolume_{self.dm.unique_id}"        
        utils.cr_node_if_not_exists(1, "floatMath", FM_spine_norm, {"operation": 3, "floatB": cv_arc_length})
        utils.cr_node_if_not_exists(1, "blendColors", BC_spine_squash, {"color1G": 1, "color2R": 1, "color2G": 1, "color2B": 1})
        
        jnt_skeleton_ls = [f"jnt_{jnt_pref}_{self.dm.mdl_nm}_{j}_{self.dm.unique_id}_{self.dm.side}" for j in skeleton_pos_dict.keys()]
        MD_skeleton_ls = []
        for jnt in jnt_skeleton_ls:
            md_name = f"MD_{jnt}"
            utils.cr_node_if_not_exists(1, "multiplyDivide", md_name, {"operation": 3})
            MD_skeleton_ls.append(md_name)

        utils.connect_attr(f"{fm_global_curve}{utils.Plg.out_flt}", f"{FM_spine_norm}{utils.Plg.flt_A}")
        utils.connect_attr(f"{ik_ctrl_ls[-1]}.{self.dm.mdl_nm}_Stretch_Volume", f"{BC_spine_squash}{utils.Plg.blndr_plg}")
        utils.connect_attr(f"{FM_spine_norm}{utils.Plg.out_flt}", f"{BC_spine_squash}{utils.Plg.color1_plg[0]}")
        utils.connect_attr(f"{FM_spine_norm}{utils.Plg.out_flt}", f"{BC_spine_squash}{utils.Plg.color1_plg[2]}")
        
        for x in range(len(skeleton_pos_dict.keys())):
                # MD
            utils.connect_attr(f"{BC_spine_squash}{utils.Plg.out_letter[0]}", f"{MD_skeleton_ls[x]}{utils.Plg.input1_val[0]}")
            utils.connect_attr(f"{BC_spine_squash}{utils.Plg.out_letter[2]}", f"{MD_skeleton_ls[x]}{utils.Plg.input1_val[2]}")
            utils.connect_attr(f"{input_grp}.{self.dm.mdl_nm}{x}_Stretch_Volume", f"{MD_skeleton_ls[x]}{utils.Plg.input2_val[0]}")
            utils.connect_attr(f"{input_grp}.{self.dm.mdl_nm}{x}_Stretch_Volume", f"{MD_skeleton_ls[x]}{utils.Plg.input2_val[2]}")
                # skeleton scale joint!
            utils.connect_attr(f"{MD_skeleton_ls[x]}{utils.Plg.out_axis[0]}", f"{jnt_skeleton_ls[x]}.scaleX")
            utils.connect_attr(f"{MD_skeleton_ls[x]}{utils.Plg.out_axis[-1]}", f"{jnt_skeleton_ls[x]}.scaleZ")

    
    def nonStr_match_setup(self, nonStr_jnt_chain, Str_jnt_chain):
        '''
        # Description:            
            The 'non' joint chain now follow it's corresponding 'Str' joint chain 
        # Attributes:
            nonStr_jnt_chain (list): non stretch joint chain.
            Str_jnt_chain (lsit): stretch joint chain.
        # Returns: N/A
        '''
        # parentconstrain first parent joint of nonStr chain to first parent joint of it's corresbpomnding str chain
        pcon_nonStr_parent_name = f"Pcon_nonStr_{nonStr_jnt_chain[0]}"
        cmds.parentConstraint(Str_jnt_chain[0], nonStr_jnt_chain[0], n=pcon_nonStr_parent_name) #,  mo=1
        cmds.setAttr(f"{pcon_nonStr_parent_name}.interpType", 2)

        # orient constrain the remaining items in the list of chains
        child_nonStr_jnt_chain = nonStr_jnt_chain[1:]
        child_Str_jnt_chain_ls = Str_jnt_chain[1:]
        for x in range(len(child_nonStr_jnt_chain)):
            ocon_nonStr_name = f"Ocon_nonStr_{child_nonStr_jnt_chain[x]}"
            cmds.orientConstraint(child_Str_jnt_chain_ls[x], child_nonStr_jnt_chain[x], n=ocon_nonStr_name)
            cmds.setAttr(f"{ocon_nonStr_name}.interpType", 2)


    def blend_fw_bw_states_to_skin_chain(self, strFw_chain, strBw_chain, rigStr, 
                                         nonstrFw_chain, nonstrBw_chain, nonrigStr,
                                         skn_chain, ik_ctrl_ls):
        '''
        # Description:            
            This function blends the forward & backward joint chains to drive 
            the skin joint chain with constraints. It wires up the Stretch_State 
            & Stretch_Anchor attr to the constraint's weights.
            Pcon:(strFw_chain, strBw_chain) > rigStr.
            Pcon:(nonstrFw_chain, nonstrBw_chain) > nonrigStr.
            Pcon:(rigStr, nonrigStr) > skn_chain.
        # Attributes:
            strFw_chain (list): foward jnt stretch chain.
            strBw_chain (list): backward jnt stretch chain.
            rigStr (list): rig jnt stretch chain.
            nonstrFw_chain (list): foward jnt NON-stretch chain.
            nonstrBw_chain (list): backward jnt NON-stretch chain.
            nonrigStr (list): rig jnt NON-stretch chain.
            skn_chain (list): skin jnt chain.
        # Returns: N/A
        '''
        # Pcon rigStr by strFw_chain & strBw_chain
        strBw_chain.reverse()
        for x in range(len(rigStr)):
            print(f"ORDER Bw: {strFw_chain[x]}, {strBw_chain[x]}, {rigStr[x]}")
            pcon_FwBw_name = f"Pcon_FwBw_{rigStr[x]}"
            cmds.parentConstraint(strFw_chain[x], strBw_chain[x], rigStr[x], n=pcon_FwBw_name)# , n=f"Pcon_FwBw_{rigStr}")
            cmds.setAttr(f"{pcon_FwBw_name}.interpType", 2)
        cmds.select(cl=1)

        # Pcon nonrigStr by nonstrFw_chain & nonstrBw_chain
        nonstrBw_chain.reverse()
        for x in range(len(nonrigStr)):
            print(f"ORDER rev nonBw: {nonstrFw_chain[x]}, {nonstrBw_chain[x]}, {nonrigStr[x]}")
            pcon_nonFwBw_name = f"Pcon_nonFwBw_{nonrigStr[x]}"
            cmds.parentConstraint(nonstrFw_chain[x], nonstrBw_chain[x], nonrigStr[x], n=pcon_nonFwBw_name)#, n=f"Pcon_FwBw_{nonrigStr}")
            cmds.setAttr(f"{pcon_nonFwBw_name}.interpType", 2)
        cmds.select(cl=1)
        
        # Pcon skn_chain by rigStr & nonrigStr
        for x in range(len(skn_chain)):
            pcon_str_name = f"Pcon_StrRig_nonStrRig_{skn_chain[x]}"
            print(f"{rigStr[x]}, {nonrigStr[x]}, {skn_chain[x]}, n={pcon_str_name}")
            cmds.parentConstraint(rigStr[x], nonrigStr[x], skn_chain[x], n=pcon_str_name)
            cmds.setAttr(f"{pcon_str_name}.interpType", 2)
            
        # wire up the Stretch_Anchor attrib.
        rev_skn_str = f"Rev_sknStr_{self.dm.mdl_nm}_{self.dm.unique_id}"
        rev_strAnchor = f"Rev_stretchAnchor_{self.dm.mdl_nm}_{self.dm.unique_id}"
        utils.cr_node_if_not_exists(1, "reverse", rev_skn_str)
        utils.cr_node_if_not_exists(1, "reverse", rev_strAnchor)
        
        # skn chain rev
        utils.connect_attr(f"{ik_ctrl_ls[-1]}.{self.dm.mdl_nm}_Stretch_State", f"{rev_skn_str}.inputX")
        # strAnchor rev
        utils.connect_attr(f"{ik_ctrl_ls[-1]}.{self.dm.mdl_nm}_Stretch_Anchor", f"{rev_strAnchor}.inputX")
        backward_indexes = [i for i, _ in enumerate(skn_chain)][::-1]
        print(f"backward_indexes = {backward_indexes}")
        for x in range(len(skn_chain)):
            # skn chain
            utils.connect_attr(f"{ik_ctrl_ls[-1]}.{self.dm.mdl_nm}_Stretch_State", 
                               f"Pcon_StrRig_nonStrRig_{skn_chain[x]}.jnt_StrRig_{self.dm.mdl_nm}_spine{x}_{self.dm.unique_id}_MW0")
            utils.connect_attr(f"{rev_skn_str}{utils.Plg.out_axis[0]}", 
                               f"Pcon_StrRig_nonStrRig_{skn_chain[x]}.jnt_nonStrRig_{self.dm.mdl_nm}_spine{x}_{self.dm.unique_id}_MW1")
            
            # rigStr chain
            utils.connect_attr(f"{rev_strAnchor}{utils.Plg.out_axis[0]}", 
                               f"Pcon_FwBw_{rigStr[x]}.jnt_StrFw_{self.dm.mdl_nm}_spine{x}_{self.dm.unique_id}_MW0")
            # jnt_StrFw_spine_spine9_0_MW0            
            utils.connect_attr(f"{ik_ctrl_ls[-1]}.{self.dm.mdl_nm}_Stretch_Anchor", 
                               f"Pcon_FwBw_{rigStr[x]}.jnt_StrBw_{self.dm.mdl_nm}_spine{backward_indexes[x]}_{self.dm.unique_id}_MW1")
          
            # nonRigStr chain
            utils.connect_attr(f"{rev_strAnchor}{utils.Plg.out_axis[0]}", 
                               f"Pcon_nonFwBw_{nonrigStr[x]}.jnt_nonStrFw_{self.dm.mdl_nm}_spine{x}_{self.dm.unique_id}_MW0")
            utils.connect_attr(f"{ik_ctrl_ls[-1]}.{self.dm.mdl_nm}_Stretch_Anchor", 
                               f"Pcon_nonFwBw_{nonrigStr[x]}.jnt_nonStrBw_{self.dm.mdl_nm}_spine{backward_indexes[x]}_{self.dm.unique_id}_MW1")
   