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


class Spine_System():
    def __init__(self, module_name, root_outputs_grp, skeleton_dict, fk_dict, ik_dict):
        '''
        IN ESSENSE, with 3 types of controls active at once, 
        FK & FKInv are the drivers > IK is THE driven that help bring the spine to life. 

        What this system consists of: 
        ----- CTRLS ------
        9 Sets of controlls : [all bottom [0] are in same pos / 
                            mid [1] are positoned exact middle of corresponding ctrls /
                            top fk[2] & fkInv[2] r pos same place, top IK[2] is a bit higher(at very top of joint chain!) )
            IK_ctrls
                ctrl_ik_spine_0 (bottom)
                ctrl_ik_spine_1 (mid)
                ctrl_ik_spine_3 (top)
            fk_ctrls
                ctrl_fk_spine_0 
                ctrl_fk_spine_1 
                ctrl_fk_spine_3 
            fkInv_ctrls
                ctrl_fk_spine_0
                ctrl_fk_spine_1 
                ctrl_fk_spine_3
        
        ----- JOINTS ------
        GRP_SKELETON
            ----- SYSTEM JOINTS ------
            > Jnt_rig_bottomSpine / Jnt_rig_topSpine
            ----- SKN JOINTS ------
            > jnt_skn_spine_0-9 (it's NOT a ctrl for each joint)
        GRP_spineLogic
            ----- SYSTEM JOINTS ------
            > GRP_jnt_ik_spine
                jnt_ik_spine_0 (bottom)
                jnt_ik_spine_1 (mid)
                jnt_ik_spine_3 (top)
                jnt_ik_spine_hold (I think this is all other weights like a root joint...)
            > GRP_jnt_fk_spine
                jnt_fk_spine_0-3
            > GRP_jnt_fkInv_spine
                jnt_fkInv_spine_0-3
        '''
        self.mdl_nm = module_name

        skeleton_pos = skeleton_dict["skel_pos"]
        skeleton_rot = skeleton_dict["skel_rot"]
        self.fk_pos = fk_dict["fk_pos"]
        self.ik_pos = ik_dict["ik_pos"]
        self.fk_rot = fk_dict["fk_rot"]
        self.ik_rot = ik_dict["ik_rot"]
        
        # gather the number of values in the dict
        num_jnts = len(skeleton_pos.keys())
        print(f"num_jnts = {num_jnts}")

        #----------------------------------------------------------------------
        # Create the controls temporarily (they will already exist with char_Layout tool)
        fk_ctrl_ls, inv_ctrl_ls, ik_ctrl_ls = self.build_ctrls(self.fk_pos, self.ik_pos)
        self.group_ctrls(fk_ctrl_ls, inv_ctrl_ls, ik_ctrl_ls)
        #----------------------------------------------------------------------
        
        #----------------------------------------------------------------------
        # create skn the joints temporarily for testing
        bott_name, top_name = self.cr_jnt_skn_ik(self.ik_pos)
        skeleton_ls = self.cr_jnt_skn_skeleton(skeleton_pos, skeleton_rot)
        joint_grp = self.group_jnts_skn(bott_name, top_name, skeleton_ls)
        #----------------------------------------------------------------------
        ''''''
        # ORDER: inp_out grps | ctrl mtx setup | logic setup
        # input & output groups
        input_grp, output_grp = self.input_output_groups(num_jnts)
        # CTRL connections for the spine setup!
        self.fk_ctrl_ls, self.inv_ctrl_ls, self.ik_ctrl_ls = self.wire_spine_ctrls(root_outputs_grp, input_grp, output_grp)
        
        # Logic setup (joints and hdl_spine_names)
        self.fk_logic_ls, self.inv_logic_ls, self.ik_logic_ls, self.logic_curve, self.jnt_mid_hold = self.cr_logic_elements(skeleton_pos, self.fk_pos, self.fk_rot, self.ik_pos, self.ik_rot)
        self.wire_ctrl_to_jnt_logic()
        self.wire_ik_bott_top_logic_to_skn('skn')
        self.wire_ik_spline('skn', skeleton_pos, input_grp)
        self.group_module(self.mdl_nm, input_grp, output_grp, F"grp_ctrls_{self.mdl_nm}", f"grp_skn_joints_{self.mdl_nm}", f"grp_logic_{self.mdl_nm}")
        ''''''
    
    # Temporary functions for skn joints & ctrl creation ----------------------
    def build_ctrls(self, fk_pos, ik_pos):
        inv_values = list(fk_pos.values())[::-1]
        # Create a new dictionary with the reversed values
        inv_fk_pos = {key: inv_values[i] for i, key in enumerate(fk_pos.keys())}
        
        print(f"inv_pos = {inv_fk_pos}")
        fk_ctrl_ls = []
        inv_ctrl_ls = []
        ik_ctrl_ls = []

        # fk & fkInv ctrls
        for spn_name, spn_pos in fk_pos.items():
            fk_name = f"{spn_name}"
            fk_ctrl_ls.append(fk_name)
            fk_import_ctrl = cr_ctrl.CreateControl(type="circle", name=fk_name)
            fk_import_ctrl.retrun_ctrl()
            cmds.rotate(0, 0, 90, fk_name)
            cmds.scale(0.25, 0.25, 0.25, fk_name)
            cmds.makeIdentity(fk_name, a=1, t=0, r=1, s=1, n=0, pn=1)
            # cmds.xform(fk_name, translation=spn_pos, worldSpace=True)
            utils.colour_object(fk_name, 17)
            

        for spn_name, spn_pos in inv_fk_pos.items():
            inv_name = spn_name.replace("_fk_", "_inv_")
            inv_ctrl_ls.append(inv_name)
            inv_import_ctrl = cr_ctrl.CreateControl(type="bvSquare", name=inv_name)
            inv_import_ctrl.retrun_ctrl()
            cmds.scale(0.25, 0.25, 0.25, inv_name)
            cmds.makeIdentity(inv_name, a=1, t=0, r=1, s=1, n=0, pn=1)
            # cmds.xform(inv_name, translation=spn_pos, worldSpace=True)
            utils.colour_object(inv_name, 21)

        # ik ctrls
        for spn_name, spn_pos in ik_pos.items():
            ik_name = f"{spn_name}"
            ik_ctrl_ls.append(ik_name)
            ik_import_ctrl = cr_ctrl.CreateControl(type="octogan", name=ik_name)
            ik_import_ctrl.retrun_ctrl()
            cmds.rotate(0, 0, 90, ik_name)
            # cmds.scale(1.5, 1.5, 1.5, ik_name)
            cmds.scale(0.25, 0.25, 0.25, ik_name)
            cmds.makeIdentity(ik_name, a=1, t=0, r=1, s=1, n=0, pn=1)
            # cmds.xform(ik_name, translation=spn_pos, worldSpace=True)
            utils.colour_object(ik_name, 17)
            
        return fk_ctrl_ls, inv_ctrl_ls, ik_ctrl_ls
    

    def group_ctrls(self, fk_ctrl_ls, inv_ctrl_ls, ik_ctrl_ls):
        ctrls_grp = f"grp_ctrls_{self.mdl_nm}"
        fk_grp = f"grp_ctrl_fk_{self.mdl_nm}"
        inv_grp = f"grp_ctrl_inv_{self.mdl_nm}"
        ik_grp = f"grp_ctrl_ik_{self.mdl_nm}" 
        utils.cr_node_if_not_exists(0, "transform", ctrls_grp)
        utils.cr_node_if_not_exists(0, "transform", fk_grp)
        utils.cr_node_if_not_exists(0, "transform", inv_grp)
        utils.cr_node_if_not_exists(0, "transform", ik_grp)
        cmds.parent(fk_grp, inv_grp, ik_grp, ctrls_grp)
        cmds.parent(fk_ctrl_ls, fk_grp)
        cmds.parent(inv_ctrl_ls, inv_grp)
        cmds.parent(ik_ctrl_ls, ik_grp)

    
    def cr_jnt_skn_ik(self, ik_pos):
        names = [key for key in ik_pos.keys()]
        pos = [value for value in ik_pos.values()]
        bott_name = names[0].replace("ctrl_ik_", "jnt_skn_")
        top_name = names[-1].replace("ctrl_ik_", "jnt_skn_")
        bott_pos = pos[0]
        top_pos = pos[-1]

        for jnt_nm, jnt_ps in zip([bott_name, top_name], [bott_pos, top_pos]):
            cmds.select(cl=True) 
            cmds.joint(n=jnt_nm)
            cmds.xform(jnt_nm, translation=jnt_ps, worldSpace=True)
            cmds.makeIdentity(jnt_nm, a=1, t=0, r=1, s=1, n=0, pn=1)
        
        return bott_name, top_name


    def cr_jnt_skn_skeleton(self, skeleton_pos, skeleton_rot):
        cmds.select(cl=True)
        jnt_ls = []
        for name in skeleton_pos:
            jnt_nm = f"jnt_skn_{name}"
            jnt_ls.append(jnt_nm)
            cmds.joint(n=jnt_nm)
            cmds.xform(jnt_nm, translation=skeleton_pos[name], worldSpace=True)
            cmds.xform(jnt_nm, rotation=skeleton_rot[name], worldSpace=True)
            cmds.makeIdentity(jnt_nm, a=1, t=0, r=1, s=0, n=0, pn=1)
        utils.clean_opm(jnt_ls[0])
        return jnt_ls


    def group_jnts_skn(self, bott_name, top_name, skeleton_name):
        joint_grp = f"grp_skn_joints_{self.mdl_nm}"
        skeleton_grp = f"grp_skeleton_{self.mdl_nm}"
        utils.cr_node_if_not_exists(0, "transform", joint_grp)
        utils.cr_node_if_not_exists(0, "transform", skeleton_grp)
        cmds.parent(skeleton_name[0], skeleton_grp)
        cmds.parent(bott_name, top_name, skeleton_grp, joint_grp)

        return joint_grp

    ''' I WANT same offset on cog ctrl for the last inv_ctrl '''
    # input & output groups ---------------------------------------------------
    def input_output_groups(self, jnt_num):
            # create input & output groups
            inputs_grp = f"grp_{self.mdl_nm}Inputs"
            outputs_grp = f"grp_{self.mdl_nm}Outputs"
            utils.cr_node_if_not_exists(0, "transform", inputs_grp)
            utils.cr_node_if_not_exists(0, "transform", outputs_grp)
            
            # custom atr on 'input group'
                # - "Global_Scale" (flt)
                # - "Base_Matrix" (matrix)
                # - "Hook_Matrix" (matrix)
                # - "Spine0-9_Squash_Value" (flt) = -0.5

            # custom atr on 'output group'
                # - "ctrl_spine_bottom" (matrix)
                # - "ctrl_spine_top" (matrix)
            utils.add_float_attrib(inputs_grp, ["globalScale"], [0.01, 999], True) 
            cmds.setAttr(f"{inputs_grp}.globalScale", 1, keyable=0, channelBox=0)
            utils.add_attr_if_not_exists(inputs_grp, "base_mtx", 'matrix', False)
            utils.add_attr_if_not_exists(inputs_grp, "hook_mtx", 'matrix', False)
            for x in range(jnt_num):
                utils.add_float_attrib(inputs_grp, [f"{self.mdl_nm}{x}_Squash_Value"], [1.0, 1.0], False)
                cmds.setAttr(f"{inputs_grp}.{self.mdl_nm}{x}_Squash_Value", keyable=1, channelBox=1)
                cmds.setAttr(f"{inputs_grp}.{self.mdl_nm}{x}_Squash_Value", -0.5)

            utils.add_attr_if_not_exists(outputs_grp, f"ctrl_{self.mdl_nm}_bottom_mtx", 
                                        'matrix', False) # for upper body module to follow
            utils.add_attr_if_not_exists(outputs_grp, f"ctrl_{self.mdl_nm}_top_mtx", 
                                        'matrix', False) # for lower body module to follow

            return inputs_grp, outputs_grp

    # Ctrl mtx setup ----------------------------------------------------------
    def wire_spine_ctrls(self, root_outputs_grp, input_grp, output_grp):
        # connect ghe root module to the spine module with inputs group nodes!
        if cmds.objExists(root_outputs_grp):
            utils.connect_attr(f"{root_outputs_grp}.ctrl_centre_mtx", f"{input_grp}.base_mtx")
            utils.connect_attr(f"{root_outputs_grp}.ctrl_cog_mtx", f"{input_grp}.hook_mtx")
            utils.connect_attr(f"{root_outputs_grp}.globalScale", f"{input_grp}.globalScale")
        
        # ---------------------------------------------------------------------------------
        ''' This is my first attempt at making controls follow without parenting, 
         Using their matrix's & adding the offset to keep their distance!!! '''
        # fk ctrl setup = Constraining the controls in canon, with MMs to achieve the neccesary offset: 
            # MM's
        MM_fk_ls = []
        MM_inv_ls = []
        fk_ctrl_ls = []
        inv_ctrl_ls = []
        previous_pos = None
        print(f"FK_rot ======================================================== {self.fk_rot.items()}")
        for i, (fk_ctrl_name, pos) in enumerate(self.fk_pos.items()):
                # append the ctrls to the list
            fk_ctrl_ls.append(fk_ctrl_name)
            inv_ctrl_ls.append(fk_ctrl_name.replace('fk', 'inv'))
                # cr MM names
            MM_fk_name = f"MM_{fk_ctrl_name}"
            MM_inv_name = f"MM_{fk_ctrl_name.replace('fk', 'inv')}"
                # cr the MM nodes
            utils.cr_node_if_not_exists(1, 'multMatrix', MM_fk_name)
            utils.cr_node_if_not_exists(1, 'multMatrix', MM_inv_name)
                # append their names to the list
            MM_fk_ls.append(MM_fk_name)
            MM_inv_ls.append(MM_inv_name)
            
                # Calculate the offset for the next control
            if previous_pos is not None:
                fk_offset = [p2 - p1 for p1, p2 in zip(previous_pos, pos)]
                inv_offset = [-(p2 - p1) for p1, p2 in zip(previous_pos, pos)]
                # set the offset to the MM's inMatrix[0]
                utils.set_matrix(fk_offset, f"{MM_fk_name}{utils.Plg.mtx_ins[0]}")
                utils.set_matrix(inv_offset, f"{MM_inv_name}{utils.Plg.mtx_ins[0]}")
            previous_pos = pos
    
        # connect the MMs
            # iniitial inputs
        utils.set_matrix(list(self.fk_pos.values())[0], f"{MM_fk_ls[0]}{utils.Plg.mtx_ins[0]}")
        utils.set_matrix(list(self.fk_pos.values())[-1], f"{MM_inv_ls[0]}{utils.Plg.mtx_ins[0]}")
        utils.connect_attr(f"{input_grp}.hook_mtx", f"{MM_fk_ls[0]}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{input_grp}.hook_mtx", f"{MM_inv_ls[0]}{utils.Plg.mtx_ins[1]}")
        # connect remaining FK & INV matrices ORDER:
            # connect the MM to corresponding ctrl
        for x in range(len(MM_fk_ls)):
            utils.connect_attr(f"{MM_fk_ls[x]}{utils.Plg.mtx_sum_plg}", f"{fk_ctrl_ls[x]}{utils.Plg.opm_plg}")
            utils.connect_attr(f"{MM_inv_ls[x]}{utils.Plg.mtx_sum_plg}", f"{inv_ctrl_ls[x]}{utils.Plg.opm_plg}")
            # connect the ctrls to MM to create the sequence
        for x in range(1, len(MM_fk_ls)):
            utils.connect_attr(f"{fk_ctrl_ls[x-1]}{utils.Plg.wld_mtx_plg}", f"{MM_fk_ls[x]}{utils.Plg.mtx_ins[1]}")
            utils.connect_attr(f"{inv_ctrl_ls[x-1]}{utils.Plg.wld_mtx_plg}", f"{MM_inv_ls[x]}{utils.Plg.mtx_ins[1]}")
        
        # ---------------------------------------------------------------------------------
        # IK ctrl setup
        # wire hierarchy: FK > IK_Top | Inv > IK_Bott | IK_top/bott > IK_mid
            # cr the MM for ik ctrls!
        MM_ik_ls = []
        ik_ctrl_ls = []
        for ik_ctrl_name in self.ik_pos.keys():
            ik_ctrl_ls.append(ik_ctrl_name)
            MM_ik_name = f"MM_{ik_ctrl_name}"
            utils.cr_node_if_not_exists(1, 'multMatrix', MM_ik_name)
            MM_ik_ls.append(MM_ik_name)
        # add squash attr to top ik ctrl
        utils.add_locked_attrib(ik_ctrl_ls[-1], ["Attributes"])
        utils.add_float_attrib(ik_ctrl_ls[-1], [f"{self.mdl_nm}_Squash"], [0, 1], True)
            # Only IK_top ctrl needs its offset claculated!
        last_fk_pos = list(self.fk_pos.values())[-1]
        ik_top_ofs = utils.calculate_matrix_offset(last_fk_pos, list(self.ik_pos.values())[-1])
        utils.set_matrix(ik_top_ofs, f"{MM_ik_ls[-1]}{utils.Plg.mtx_ins[0]}")
            # two end fk & inv ctrls into ik MM top & bottom
        utils.connect_attr(f"{fk_ctrl_ls[-1]}{utils.Plg.wld_mtx_plg}", f"{MM_ik_ls[-1]}{utils.Plg.mtx_ins[1]}") # MM_ik_top
        utils.connect_attr(f"{inv_ctrl_ls[-1]}{utils.Plg.wld_mtx_plg}", f"{MM_ik_ls[0]}{utils.Plg.mtx_ins[1]}") # MM_ik_bottom
            # connect the MMs to ctrls
        for x in range(len(MM_ik_ls)):
            utils.connect_attr(f"{MM_ik_ls[x]}{utils.Plg.mtx_sum_plg}", f"{ik_ctrl_ls[x]}{utils.Plg.opm_plg}")
        
        # IK middle ctrl wires: (twisting axis in this scenario is 'Y' >
        twist_axis = "Y" 
        # calc this by the givin rotation values)
            # Blend matrix for pos between top & bottom
            # 2 flt nodes, 1 aim matracies & 1 CM for twisting
        BM_ik_mid = f"BM_{ik_ctrl_ls[1]}"
        utils.cr_node_if_not_exists(1, "blendMatrix", BM_ik_mid)
        AM_ik_mid =  f"AM_sub_{ik_ctrl_ls[1]}"
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

        return fk_ctrl_ls, inv_ctrl_ls, ik_ctrl_ls

    # Logic setup -------------------------------------------------------------
    def cr_logic_elements(self, skeleton_pos, fk_pos, fk_rot, ik_pos, ik_rot):
        # establish the inv dictionary's
        # inv_pos_values = list(fk_pos.values())[::-1]
        # inv_rot_values = list(fk_rot.values())[::-1]
        # inv_pos = {key: inv_pos_values[i] for i, key in enumerate(fk_pos.keys())}
        # inv_rot = {key: inv_rot_values[i] for i, key in enumerate(fk_pos.keys())}
        # 4 groups
        logic_grp = f"grp_logic_{self.mdl_nm}"
        fk_grp = f"grp_jnts_fk_{self.mdl_nm}"
        inv_grp = f"grp_jnts_inv_{self.mdl_nm}"
        ik_grp = f"grp_jnts_ik_{self.mdl_nm}" 
        utils.cr_node_if_not_exists(0, "transform", logic_grp)
        utils.cr_node_if_not_exists(0, "transform", fk_grp)
        utils.cr_node_if_not_exists(0, "transform", inv_grp)
        utils.cr_node_if_not_exists(0, "transform", ik_grp)
        
        # build the curve for the ik spline
        logic_curve = f"crv_{self.mdl_nm}"
        positions = list(skeleton_pos.values())
        cmds.curve(n=logic_curve, d=3, p=positions)
        cmds.rebuildCurve(logic_curve, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=0, kt=0, s=1, d=3, tol=0.01)

        cmds.parent(fk_grp, inv_grp, ik_grp, logic_curve, logic_grp)
        
        fk_logic_ls = []
        inv_logic_ls = []
        ik_logic_ls = []
        # cr the logic joints!
        for spn_name in fk_pos:
            cmds.select(cl=1)
            fk_name = spn_name.replace("ctrl_", "jnt_") # ctrl_fk_{self.mdl_nm}0
            fk_logic_ls.append(fk_name)
            inv_name = spn_name.replace("ctrl_fk_", "jnt_inv_") # ctrl_fk_{self.mdl_nm}0
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
        jnt_mid_hold = cmds.joint(n=f"jnt_ik_{self.mdl_nm}_middleHold")

        # organise the joints into the right groups
        cmds.parent(fk_logic_ls, fk_grp)
        cmds.parent(inv_logic_ls, inv_grp)
        cmds.parent(ik_logic_ls, jnt_mid_hold, ik_grp)
    
        return fk_logic_ls, inv_logic_ls, ik_logic_ls, logic_curve, jnt_mid_hold


    def wire_ctrl_to_jnt_logic(self):
        for fk_ctrl, inv_ctrl, ik_ctrl, fk_logic, inv_logic, ik_logic in zip(
            self.fk_ctrl_ls, self.inv_ctrl_ls, self.ik_ctrl_ls, 
            self.fk_logic_ls, self.inv_logic_ls, self.ik_logic_ls
            ):
            print(f"fk_ctrl = {fk_ctrl} | {fk_logic}")
            print(f"inv_ctrl = {inv_ctrl} | {inv_logic}")
            print(f"fk_ctrl = {ik_ctrl} | {ik_logic}")
            MM_fk_logic = utils.mtxCon_no_ofs(fk_ctrl, fk_logic)
            MM_inv_logic = utils.mtxCon_no_ofs(inv_ctrl, inv_logic)
            MM_ik_logic = utils.mtxCon_no_ofs(ik_ctrl, ik_logic)


    def wire_ik_bott_top_logic_to_skn(self, jnt_pref):
        ''' ISSUE in the future, this direct connection going to the skn joints 
        means it moves the joint cus it will have values 
        = so u have to make sure OPM is already set on the skn joint.  '''
        skn_bot_jnt = self.ik_logic_ls[0].replace('ik', jnt_pref)
        skn_top_jnt = self.ik_logic_ls[-1].replace('ik', jnt_pref)
        # check if skn has none default values
        if not utils.check_non_default_transforms(skn_bot_jnt) or utils.check_non_default_transforms(skn_top_jnt):
            print(f"{skn_bot_jnt} & {skn_top_jnt} have none default values and require cleaning")
            utils.clean_opm([skn_bot_jnt, skn_top_jnt])

        utils.connect_attr(f"{self.ik_logic_ls[0]}{utils.Plg.wld_mtx_plg}", f"{skn_bot_jnt}{utils.Plg.opm_plg}")
        utils.connect_attr(f"{self.ik_logic_ls[-1]}{utils.Plg.wld_mtx_plg}", f"{skn_top_jnt}{utils.Plg.opm_plg}")


    def wire_ik_spline(self, jnt_pref, skeleton_pos, input_grp):
        jnt_skeleton_ls = [f"jnt_{jnt_pref}_{j}" for j in skeleton_pos.keys()]
        num_squash_jnts = len(skeleton_pos.keys())-1
        
        # Curve shape name & cluster!
        jnt_ik_logic_mid = self.ik_logic_ls[1]
        crv_logic_shape = cmds.listRelatives(self.logic_curve, s=1)[0]
        
        print(f"crv_logic_shape = {crv_logic_shape}")
        # curve util nodes 
        CvInfo = f"Cinfo_{self.mdl_nm}"
        utils.cr_node_if_not_exists(1, "curveInfo", CvInfo)
        utils.connect_attr(f"{crv_logic_shape}{utils.Plg.wld_space_plg}", 
                           f"{CvInfo}{utils.Plg.inp_curve_plg}")
        cv_arc_length = cmds.getAttr(f"{CvInfo}{utils.Plg.arc_len_plg}")

        FM_spine_global = f"FM_{self.mdl_nm}_global_div"
        FM_spine_joints = f"FM_{self.mdl_nm}_joints_div"
        FM_spine_norm = F"FM_{self.mdl_nm}_norm"
        BC_spine_squash = F"BC_{self.mdl_nm}_squash"
        utils.cr_node_if_not_exists(1, "floatMath", FM_spine_global, {"operation": 3})
        utils.cr_node_if_not_exists(1, "floatMath", FM_spine_joints, {"operation": 3, "floatB": num_squash_jnts})
        utils.cr_node_if_not_exists(1, "floatMath", FM_spine_norm, {"operation": 3, "floatB": cv_arc_length})
        utils.cr_node_if_not_exists(1, "blendColors", BC_spine_squash, {"color1G": 1, "color2R": 1, "color2G": 1, "color2B": 1})
        utils.cr_node_if_not_exists(1, "blendColors", BC_spine_squash, {"color1G": 1, "color2R": 1, "color2G": 1, "color2B": 1})

        MD_skeleton_ls = []
        for jnt in jnt_skeleton_ls:
            md_name = f"MD_{jnt}"
            utils.cr_node_if_not_exists(1, "multiplyDivide", md_name, {"operation": 3})
            MD_skeleton_ls.append(md_name)
        
        # skinning method
            # skin the top & bottom  ik skn joints to curve
            # skin the middle & hold logic jonts
            # create inversmatric, 
            # plug middle MM into inversmatrix
            # plug inversematrix into bind bind pre-matrix on the 2nd skincluster!
        cmds.skinCluster([self.ik_logic_ls[0], self.ik_logic_ls[-1]], self.logic_curve, tsb=True, wd=1)[0]
        # # Create the second skinCluster
        middle_skincluster = cmds.skinCluster([jnt_ik_logic_mid, self.jnt_mid_hold], self.logic_curve, tsb=True, wd=1, multi=1)[0]
        cmds.skinPercent( middle_skincluster, f"{self.logic_curve}.cv[0]", f"{self.logic_curve}.cv[3]", tv=[(self.jnt_mid_hold, 1)])
        # skinPercent -tv jnt_hold  1 skinCluster4 curve1.cv[0:1] curve1.cv[4:5]
    
        inv_mtx = f"IM_{jnt_ik_logic_mid}"
        utils.cr_node_if_not_exists(1, "inverseMatrix", inv_mtx)
        utils.connect_attr(f"MM_{self.ik_ctrl_ls[1]}{utils.Plg.mtx_sum_plg}", f"{inv_mtx}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{inv_mtx}{utils.Plg.out_mtx_plg}", f"{middle_skincluster}.bindPreMatrix[0]")

        # connections
            # global FM
        utils.connect_attr(f"{CvInfo}{utils.Plg.arc_len_plg}", f"{FM_spine_global}{utils.Plg.flt_A}")
        utils.connect_attr(f"{input_grp}.globalScale", f"{FM_spine_global}{utils.Plg.flt_B}")
            # joints FM
        utils.connect_attr(f"{FM_spine_global}{utils.Plg.out_flt}", f"{FM_spine_joints}{utils.Plg.flt_A}")
            # norm FM
        utils.connect_attr(f"{FM_spine_global}{utils.Plg.out_flt}", f"{FM_spine_norm}{utils.Plg.flt_A}")
            # squash BC
        utils.connect_attr(f"{self.ik_ctrl_ls[-1]}.{self.mdl_nm}_Squash", f"{BC_spine_squash}{utils.Plg.blndr_plg}")
        utils.connect_attr(f"{FM_spine_norm}{utils.Plg.out_flt}", f"{BC_spine_squash}{utils.Plg.color1_plg[0]}")
        utils.connect_attr(f"{FM_spine_norm}{utils.Plg.out_flt}", f"{BC_spine_squash}{utils.Plg.color1_plg[2]}")
            
        ''' the following connections into the MD are dependant on the orientation of the joints! '''
        for x in range(len(skeleton_pos.keys())):
                # MD
            utils.connect_attr(f"{BC_spine_squash}{utils.Plg.out_letter[0]}", f"{MD_skeleton_ls[x]}{utils.Plg.input1_val[0]}")
            utils.connect_attr(f"{BC_spine_squash}{utils.Plg.out_letter[2]}", f"{MD_skeleton_ls[x]}{utils.Plg.input1_val[2]}")
            utils.connect_attr(f"{input_grp}.{self.mdl_nm}{x}_Squash_Value", f"{MD_skeleton_ls[x]}{utils.Plg.input2_val[0]}")
            utils.connect_attr(f"{input_grp}.{self.mdl_nm}{x}_Squash_Value", f"{MD_skeleton_ls[x]}{utils.Plg.input2_val[2]}")
                # skeleton scale joint!
            utils.connect_attr(f"{MD_skeleton_ls[x]}{utils.Plg.out_axis[0]}", f"{jnt_skeleton_ls[x]}.scaleX")
            utils.connect_attr(f"{MD_skeleton_ls[x]}{utils.Plg.out_axis[-1]}", f"{jnt_skeleton_ls[x]}.scaleZ")
                # skeleton transaltion PRIMARY AXIS joint!
        for x in range(1, len(skeleton_pos.keys())):  
            utils.connect_attr(f"{FM_spine_joints}{utils.Plg.out_flt}", f"{jnt_skeleton_ls[x]}.translateY")

        # ik spline setup
        hdl_spine_name = f"hdl_{self.mdl_nm}_spline"
        cmds.ikHandle( n=hdl_spine_name, sol="ikSplineSolver", c=self.logic_curve, sj=jnt_skeleton_ls[0], ee=jnt_skeleton_ls[-1], ccv=False, pcv=False)
        cmds.parent(hdl_spine_name, f"grp_logic_{self.mdl_nm}")
        # Enable advanced twist options on hdl_spine_name
        cmds.setAttr(  f"{hdl_spine_name}.dTwistControlEnable", 1 )
        cmds.setAttr( f"{hdl_spine_name}.dWorldUpType", 4 )              
        positive_z = 3
        positive_y = 2
        cmds.setAttr(f"{hdl_spine_name}.dForwardAxis", positive_y)
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpAxis", positive_z )
        # Xvals
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpVectorX", 0)
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpVectorEndX", 0)
        # Yvals
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpVectorY", 0)
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpVectorEndY", 0)
        # Zvals
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpVectorZ", 1)
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpVectorEndZ", 1)
        # Set the 'World Up Object' to the controller the is driving the first joint of the chain. (ctrl_ik_pelvis)
        utils.connect_attr(f"{self.ik_ctrl_ls[0]}{utils.Plg.wld_mtx_plg}", f"{hdl_spine_name}.dWorldUpMatrix")
        utils.connect_attr(f"{self.ik_ctrl_ls[-1]}{utils.Plg.wld_mtx_plg}", f"{hdl_spine_name}.dWorldUpMatrixEnd")


    def group_module(self, module_name, input_grp, output_grp, ctrl_grp, joint_grp, logic_grp):
        grp_module_name = f"grp_module_{module_name}"
        cmds.group(n=grp_module_name, em=1)
        cmds.parent(input_grp, output_grp, ctrl_grp, joint_grp, logic_grp, 
                    grp_module_name)
        cmds.hide(logic_grp)
        

# Basic spine example: 
skeleton_dict = {
    "skel_pos":{
        'spine0' : [0.0, 147.00000000000003, 0.0], 
        'spine1' : [0.0, 153.4444446563721, 0.0], 
        'spine2' : [0.0, 159.88888931274417, 0.0], 
        'spine3' : [0.0, 166.33333396911624, 0.0], 
        'spine4' : [0.0, 172.7777786254883, 0.0], 
        'spine5' : [0.0, 179.22222328186038, 0.0], 
        'spine6' : [0.0, 185.66666793823245, 0.0], 
        'spine7' : [0.0, 192.11111259460452, 0.0], 
        'spine8' : [0.0, 198.5555572509766, 0.0], 
        'spine9' : [0.0, 205.00000190734866, 0.0]
    },
    "skel_rot":{
        'spine0' : [0.0, 0.0, 0.0], 
        'spine1' : [0.0, 0.0, 0.0], 
        'spine2' : [0.0, 0.0, 0.0], 
        'spine3' : [0.0, 0.0, 0.0], 
        'spine4' : [0.0, 0.0, 0.0], 
        'spine5' : [0.0, 0.0, 0.0], 
        'spine6' : [0.0, 0.0, 0.0], 
        'spine7' : [0.0, 0.0, 0.0], 
        'spine8' : [0.0, 0.0, 0.0], 
        'spine9' : [0.0, 0.0, 0.0]
    } 

    }

''' ---These outputs will be determined by Char_Layout tool! 
        (place joints, choose num of ctrls, position ctrls, shape ctrls)--- '''
# I want this to be changable (3 by default)
fk_spine_dict = {
    "fk_pos":{
        'ctrl_fk_spine0': [0.0, 147.0, 0.0], 
        'ctrl_fk_spine1': [0.0, 167.29999965429306, 0.0], 
        'ctrl_fk_spine2': [0.0, 187.59999930858612, 0.0]
        },
    "fk_rot":{
        'ctrl_fk_spine0': [0.0, 0.0, 0.0], 
        'ctrl_fk_spine1': [0.0, 0.0, 0.0], 
        'ctrl_fk_spine2': [0.0, 0.0, 0.0]
        }
    }
# Always 3 ctrls!
ik_spine_dict = {
    "ik_pos":{
        'ctrl_ik_spine_bottom': [0.0, 147.0, 0.0], 
        'ctrl_ik_spine_middle': [0.0, 176.0, 0.0], 
        'ctrl_ik_spine_top': [0.0, 205.0, 0.0]
        },
    "ik_rot":{
        'ctrl_ik_spine_bottom': [0.0, 0.0, 0.0], 
        'ctrl_ik_spine_middle': [0.0, 0.0, 0.0], 
        'ctrl_ik_spine_top': [0.0, 0.0, 0.0]
        }
    }

Spine_System("spine", "grp_rootOutputs", skeleton_dict, fk_spine_dict, ik_spine_dict)

# Snake middle body example:
skel_midBody_dict = {
    "skel_pos":{
        'midBody0': [0.0, 0.0, -20.0], 
        'midBody1': [0.0, 0.0, -18.0], 
        'midBody2': [0.0, 0.0, -16.0], 
        'midBody3': [0.0, 0.0, -14.0], 
        'midBody4': [0.0, 0.0, -12.0], 
        'midBody5': [0.0, 0.0, -10.0], 
        'midBody6': [0.0, 0.0, -8.0], 
        'midBody7': [0.0, 0.0, -6.0], 
        'midBody8': [0.0, 0.0, -4.0], 
        'midBody9': [0.0, 0.0, -2.0], 
        'midBody10': [0.0, 0.0, 0.0], 
        'midBody11': [0.0, 0.0, 2.0], 
        'midBody12': [0.0, 0.0, 4.0], 
        'midBody13': [0.0, 0.0, 6.0], 
        'midBody14': [0.0, 0.0, 8.0], 
        'midBody15': [0.0, 0.0, 10.0], 
        'midBody16': [0.0, 0.0, 12.0], 
        'midBody17': [0.0, 0.0, 14.0],
        'midBody18': [0.0, 0.0, 16.0]
        },
    "skel_rot":{'midBody0': [90.0, 0.0, 0.0], 'midBody1': [90.0, 0.0, 0.0], 'midBody2': [90.0, 0.0, 0.0], 'midBody3': [90.0, 0.0, 0.0], 'midBody4': [90.0, 0.0, 0.0], 'midBody5': [90.0, 0.0, 0.0], 'midBody6': [90.0, 0.0, 0.0], 'midBody7': [90.0, 0.0, 0.0], 'midBody8': [90.0, 0.0, 0.0], 'midBody9': [90.0, 0.0, 0.0], 'midBody10': [90.0, 0.0, 0.0], 'midBody11': [90.0, 0.0, 0.0], 'midBody12': [90.0, 0.0, 0.0], 'midBody13': [90.0, 0.0, 0.0], 'midBody14': [90.0, 0.0, 0.0], 'midBody15': [90.0, 0.0, 0.0], 'midBody16': [90.0, 0.0, 0.0], 'midBody17': [90.0, 0.0, 0.0], 'midBody18': [90.0, 0.0, 0.0]}
}
fk_midBody_dict = { 
    "fk_pos":{
        'ctrl_fk_midBody0': [0.0, 0.0, -20.0], 
        'ctrl_fk_midBody1': [0.0, 0.0, -16.0], 
        'ctrl_fk_midBody2': [0.0, 0.0, -12.0], 
        'ctrl_fk_midBody3': [0.0, 0.0, -8.0], 
        'ctrl_fk_midBody4': [0.0, 0.0, -4.0], 
        'ctrl_fk_midBody5': [0.0, 0.0, 0.0], 
        'ctrl_fk_midBody6': [0.0, 0.0, 4.0], 
        'ctrl_fk_midBody7': [0.0, 0.0, 8.0], 
        'ctrl_fk_midBody8': [0.0, 0.0, 12.0], 
        'ctrl_fk_midBody9': [0.0, 0.0, 16.0]
        },
    "fk_rot":{'ctrl_fk_midBody0': [90.0, 0.0, 0.0], 'ctrl_fk_midBody1': [90.0, 0.0, 0.0], 'ctrl_fk_midBody2': [90.0, 0.0, 0.0], 'ctrl_fk_midBody3': [90.0, 0.0, 0.0], 'ctrl_fk_midBody4': [90.0, 0.0, 0.0], 'ctrl_fk_midBody5': [90.0, 0.0, 0.0], 'ctrl_fk_midBody6': [90.0, 0.0, 0.0], 'ctrl_fk_midBody7': [90.0, 0.0, 0.0], 'ctrl_fk_midBody8': [90.0, 0.0, 0.0], 'ctrl_fk_midBody9': [90.0, 0.0, 0.0]}

}
ik_midBody_dict = {
    "ik_pos":{'ctrl_ik_midBody_bottom': [0.0, 0.0, -20.0], 'ctrl_ik_midBody_mid': [0.0, 0.0, -2.0], 'ctrl_ik_midBody_top': [0.0, 0.0, 16.0]},
    "ik_rot":{'ctrl_ik_midBody_bottom': [90.0, 0.0, 0.0], 'ctrl_ik_midBody_mid': [90.0, 0.0, 0.0], 'ctrl_ik_midBody_top': [90.0, 0.0, 0.0]}

}
# Spine_System("midBody", "grp_rootOutputs", skel_midBody_dict, fk_midBody_dict, ik_midBody_dict)