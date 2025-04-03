import importlib
import maya.cmds as cmds
from systems import (
    utils
)
from systems.sys_char_rig import (
    cr_ctrl
)
importlib.reload(utils)
importlib.reload(cr_ctrl)

'''
database_componment_dict = {
    "module_name":"bipedArm", 
    "unique_id":0,
    "side":"L", 
    "component_pos":{'clavicle': [3.9705319404602006, 230.650634765625, 2.762230157852166], 
                    'shoulder': [28.9705319404602, 230.650634765625, 2.762230157852166], 
                    'elbow': [49.96195602416994, 192.91743469238278, -8.43144416809082], 
                    'wrist': [72.36534118652347, 164.23757934570304, 15.064828872680739]
                    },
    "controls":{'FK_ctrls': 
                        {'fk_clavicle': 'circle', 'fk_shoulder': 'circle', 'fk_elbow': 'circle', 'fk_wrist': 'circle'}, 
                'IK_ctrls': 
                        {'ik_clavicle': 'cube', 'ik_shoulder': 'cube', 'ik_elbow': 'pv', 'ik_wrist': 'cube'}
                }   
    }
    'IK_ctrls': = {"ik_spine1": "cube", "ik_spine2": null, "ik_spine3": "cube", "ik_spine4": null, "ik_spine5": "cube"}
    '''

class Spine_System():
    def __init__(self, root_outputs_grp, skeleton_dict, fk_dict, ik_dict):
        skeleton_pos = skeleton_dict["spine_pos"]
        skeleton_rot = skeleton_dict["spine_rot"]
        self.fk_pos = fk_dict["fk_pos"]
        self.ik_pos = ik_dict["ik_pos"]
        fk_rot = fk_dict["fk_rot"]
        ik_rot = ik_dict["ik_rot"]
        
        # gather the number of values in the dict
        num_jnts = len(skeleton_pos.keys())
        print(f"num_jnts = {num_jnts}")

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

        print(f"MM_SPINE_TOP_0{utils.Plg.mtx_sum_plg}")

        # Create the controls temporarily (they will already exist with char_Layout tool)
        fk_ctrl_ls, inv_ctrl_ls, ik_ctrl_ls = self.build_ctrls(self.fk_pos, self.ik_pos)
        self.group_ctrls(fk_ctrl_ls, inv_ctrl_ls, ik_ctrl_ls)

        # create the joints
        bott_name, top_name = self.cr_jnt_sys_bt_tp(self.ik_pos)
        skeleton_ls = self.cr_jnt_sys_skeleton(skeleton_pos, skeleton_rot)
        self.group_jnts_sys(bott_name, top_name, skeleton_ls)
        self.logic_elements(skeleton_pos, self.fk_pos, fk_rot, self.ik_pos, ik_rot)

        # input & output groups
        input_grp, output_grp = self.input_output_groups(10)

        # make connections for the spine setup!
        self.spine_ctrl_wires(root_outputs_grp, input_grp, output_grp)


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
            cmds.makeIdentity(fk_name, a=1, t=0, r=1, s=0, n=0, pn=1)
            # cmds.xform(fk_name, translation=spn_pos, worldSpace=True)
            utils.colour_object(fk_name, 17)
            

        for spn_name, spn_pos in inv_fk_pos.items():
            inv_name = spn_name.replace("_fk_", "_inv_")
            inv_ctrl_ls.append(inv_name)
            inv_import_ctrl = cr_ctrl.CreateControl(type="bvSquare", name=inv_name)
            inv_import_ctrl.retrun_ctrl()
            # cmds.xform(inv_name, translation=spn_pos, worldSpace=True)
            utils.colour_object(inv_name, 21)

        # ik ctrls
        for spn_name, spn_pos in ik_pos.items():
            ik_name = f"{spn_name}"
            ik_ctrl_ls.append(ik_name)
            ik_import_ctrl = cr_ctrl.CreateControl(type="octogan", name=ik_name)
            ik_import_ctrl.retrun_ctrl()
            cmds.rotate(0, 0, 90, ik_name)
            cmds.scale(1.5, 1.5, 1.5, ik_name)
            cmds.makeIdentity(ik_name, a=1, t=0, r=1, s=1, n=0, pn=1)
            # cmds.xform(ik_name, translation=spn_pos, worldSpace=True)
            utils.colour_object(ik_name, 17)
            
        return fk_ctrl_ls, inv_ctrl_ls, ik_ctrl_ls
    

    def group_ctrls(self, fk_ctrl_ls, inv_ctrl_ls, ik_ctrl_ls):
        ctrls_grp = f"grp_ctrls_spine"
        fk_grp = f"grp_ctrl_fk_spine"
        inv_grp = f"grp_ctrl_inv_spine"
        ik_grp = f"grp_ctrl_ik_spine" 
        utils.cr_node_if_not_exists(0, "transform", ctrls_grp)
        utils.cr_node_if_not_exists(0, "transform", fk_grp)
        utils.cr_node_if_not_exists(0, "transform", inv_grp)
        utils.cr_node_if_not_exists(0, "transform", ik_grp)
        cmds.parent(fk_grp, inv_grp, ik_grp, ctrls_grp)
        cmds.parent(fk_ctrl_ls, fk_grp)
        cmds.parent(inv_ctrl_ls, inv_grp)
        cmds.parent(ik_ctrl_ls, ik_grp)

    
    def cr_jnt_sys_bt_tp(self, ik_pos):
        names = [key for key in ik_pos.keys()]
        pos = [value for value in ik_pos.values()]
        bott_name = names[0].replace("ctrl_ik_", "jnt_sys_")
        top_name = names[-1].replace("ctrl_ik_", "jnt_sys_")
        bott_pos = pos[0]
        top_pos = pos[-1]

        for jnt_nm, jnt_ps in zip([bott_name, top_name], [bott_pos, top_pos]):
            cmds.select(cl=True) 
            cmds.joint(n=jnt_nm)
            cmds.xform(jnt_nm, translation=jnt_ps, worldSpace=True)
            cmds.makeIdentity(jnt_nm, a=1, t=0, r=1, s=1, n=0, pn=1)
        
        return bott_name, top_name


    def cr_jnt_sys_skeleton(self, skeleton_pos, skeleton_rot):
        cmds.select(cl=True)
        jnt_ls = []
        for name in skeleton_pos:
            jnt_nm = f"jnt_sys_{name}"
            jnt_ls.append(jnt_nm)
            cmds.joint(n=jnt_nm)
            cmds.xform(jnt_nm, translation=skeleton_pos[name], worldSpace=True)
            cmds.xform(jnt_nm, rotation=skeleton_rot[name], worldSpace=True)
            cmds.makeIdentity(jnt_nm, a=1, t=0, r=1, s=0, n=0, pn=1)

        return jnt_ls


    def group_jnts_sys(self, bott_name, top_name, skeleton_name):
        joint_grp = f"grp_joints_spine"
        skeleton_grp = f"grp_skeleton_spine"
        utils.cr_node_if_not_exists(0, "transform", joint_grp)
        utils.cr_node_if_not_exists(0, "transform", skeleton_grp)
        cmds.parent(skeleton_name[0], skeleton_grp)
        cmds.parent(bott_name, top_name, skeleton_grp, joint_grp)


    def logic_elements(self, skeleton_pos, fk_pos, fk_rot, ik_pos, ik_rot):
        # establish the inv dictionary's
        inv_pos_values = list(fk_pos.values())[::-1]
        inv_rot_values = list(fk_rot.values())[::-1]
        inv_pos = {key: inv_pos_values[i] for i, key in enumerate(fk_pos.keys())}
        inv_rot = {key: inv_rot_values[i] for i, key in enumerate(fk_pos.keys())}
        # 4 groups
        logic_grp = f"grp_logic_sys_spine"
        fk_grp = f"grp_jnts_fk_spine"
        inv_grp = f"grp_jnts_inv_spine"
        ik_grp = f"grp_jnts_ik_spine" 
        utils.cr_node_if_not_exists(0, "transform", logic_grp)
        utils.cr_node_if_not_exists(0, "transform", fk_grp)
        utils.cr_node_if_not_exists(0, "transform", inv_grp)
        utils.cr_node_if_not_exists(0, "transform", ik_grp)
        cmds.parent(fk_grp, inv_grp, ik_grp, logic_grp)
        
        fk_logic_ls = []
        inv_logic_ls = []
        ik_logic_ls = []
        # cr the logic joints!
        for spn_name in fk_pos:
            cmds.select(cl=1)
            fk_name = spn_name.replace("ctrl_", "jnt_") # ctrl_fk_spine0
            fk_logic_ls.append(fk_name)
            inv_name = spn_name.replace("ctrl_fk_", "jnt_inv_") # ctrl_fk_spine0
            inv_logic_ls.append(inv_name)
            cmds.joint(n=fk_name)
            cmds.select(cl=1)
            cmds.joint(n=inv_name)
            cmds.xform(fk_name, translation=fk_pos[spn_name], worldSpace=True)
            cmds.xform(inv_name, translation=inv_pos[spn_name], worldSpace=True)
            cmds.xform(fk_name, rotation=fk_rot[spn_name], worldSpace=True)
            cmds.xform(inv_name, rotation=inv_rot[spn_name], worldSpace=True)
            cmds.makeIdentity(fk_name, a=1, t=0, r=1, s=0, n=0, pn=1)
            cmds.makeIdentity(inv_name, a=1, t=0, r=1, s=0, n=0, pn=1)

        for spn_name in ik_pos:
            cmds.select(cl=1)
            ik_name = spn_name.replace("ctrl_", "jnt_")
            ik_logic_ls.append(ik_name)    
            cmds.joint(n=ik_name)
            cmds.xform(ik_name, translation=ik_pos[spn_name], worldSpace=True)
            cmds.xform(ik_name, rotation=ik_rot[spn_name], worldSpace=True)
            cmds.makeIdentity(ik_name, a=1, t=0, r=1, s=0, n=0, pn=1)

        # THE CURVE IS CREATED WITH THE IK SPLINE OPPTIONALLY - build the curve for the ik spline
        # logic_curve = f"crv_spine"
        # positions = list(skeleton_pos.values())
        # cmds.curve(n=logic_curve, d=3, p=positions)
        # cmds.rebuildCurve(logic_curve, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=0, kt=0, s=len(positions) - 3, d=3, tol=0.01)

        # organise the joints into the right groups
        # cmds.parent(logic_curve, logic_grp)
        cmds.parent(fk_logic_ls, fk_grp)
        cmds.parent(inv_logic_ls, inv_grp)
        cmds.parent(ik_logic_ls, ik_grp)
    

    def input_output_groups(self, jnt_num):
        # create input & output groups
        inputs_grp = f"grp_spineInputs"
        outputs_grp = f"grp_spineOutputs"
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
            utils.add_float_attrib(inputs_grp, [f"Spine{x}_Squash_Value"], [1.0, 1.0], False)
            cmds.setAttr(f"{inputs_grp}.Spine{x}_Squash_Value", keyable=1, channelBox=1)
            cmds.setAttr(f"{inputs_grp}.Spine{x}_Squash_Value", -0.5)

        utils.add_attr_if_not_exists(outputs_grp, "ctrl_spine_bottom_mtx", 
                                     'matrix', False) # for upper body module to follow
        utils.add_attr_if_not_exists(outputs_grp, "ctrl_spine_top_mtx", 
                                     'matrix', False) # for lower body module to follow

        return inputs_grp, outputs_grp


    def spine_ctrl_wires(self, root_outputs_grp, input_grp, output_grp):
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
        #secondaryTargetMatrix


skeleton_dict = {
    "spine_pos":{
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
    "spine_rot":{
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

Spine_System("grp_rootOutputs", skeleton_dict, fk_spine_dict, ik_spine_dict)

