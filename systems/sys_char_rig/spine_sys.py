
import importlib
import re
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
from Jmvs_tool_box.systems.sys_char_rig import spine_sys

importlib.reload(spine_sys)
'''

class SpineSystem():
    def __init__(self, module_name, root_outputs_grp, skeleton_dict, fk_dict, ik_dict, prim_axis):
        '''
        # Description:
            Class Module: Creates a spine 3 states: fk/Inverse fk/ik. The two fk 
            states drive the Ik controls, and ik can be animated at the same time.
            The spine has 3 Stretch ability's: Stretch/Anchor(allows the direction 
            of the spine to reverse & make the top and bottom follow each other)
            /volume preservation.
        # Attributes:
            module_name (string): name of this module.
            root_outputs_grp (string): 'Output' grp from other module for this one to follow.
            skeleton_dict (dict): (dict): key="skel_pos/rot"(string), value="skel_pos/rot"(dict).
            fk_dict (dict): (dict): key="fk_pos/rot"(string), value="fk_pos/rot"(dict).
            ik_dict (dict): (dict): key="ik_pos/rot"(string), value="ik_pos/rot"(dict).
        # Returns:N/A
        '''
        skeleton_pos = skeleton_dict["skel_pos"]
        skeleton_rot = skeleton_dict["skel_rot"]
        self.fk_pos = fk_dict["fk_pos"]
        self.ik_pos = ik_dict["ik_pos"]
        self.fk_rot = fk_dict["fk_rot"]
        self.ik_rot = ik_dict["ik_rot"]
        self.prim_axis = prim_axis
        
        self.mdl_nm = module_name
        self.unique_id = [key for key in self.fk_pos.keys()][0].split('_')[-2]
        self.side = [key for key in self.fk_pos.keys()][0].split('_')[-1]

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
        
        # cr StrFw_jnt / nonStrFw / StrBw_jnt / nonStrBw in this script.
        strFw_jnt_chain = self.cr_jnt_type_chain("StrFw", skeleton_pos, skeleton_rot)
        nonstrFw_jnt_chain = self.cr_jnt_type_chain("nonStrFw", skeleton_pos, skeleton_rot)
        strBw_jnt_chain = self.cr_jnt_type_chain("StrBw", skeleton_pos, skeleton_rot, True)
        nonstrBw_jnt_chain = self.cr_jnt_type_chain("nonStrBw", skeleton_pos, skeleton_rot, True)
        strRig_jnt_chain = self.cr_jnt_type_chain("StrRig", skeleton_pos, skeleton_rot)
        nonStrRig_jnt_chain = self.cr_jnt_type_chain("nonStrRig", skeleton_pos, skeleton_rot)
        skn_jnt_chain = self.cr_jnt_type_chain("skn", skeleton_pos, skeleton_rot)
        # Temporarily cr skin_jnt chain!
        joint_grp = self.group_jnts_skn(bott_name, top_name, skn_jnt_chain)
        #----------------------------------------------------------------------
        
        # ORDER: inp_out grps | ctrl mtx setup | logic setup
        # input & output groups
        input_grp, output_grp = self.cr_input_output_groups(num_jnts)
        # CTRL connections for the spine setup!
        self.fk_ctrl_ls, self.inv_ctrl_ls, self.ik_ctrl_ls = self.wire_spine_ctrls(root_outputs_grp, input_grp)
        
        # Logic setup (joints and hdl_spine_names)
        
        self.logic_grp, self.fk_logic_ls, self.inv_logic_ls, self.ik_logic_ls, self.jnt_mid_hold = self.cr_logic_elements(self.fk_pos, self.fk_rot, self.ik_pos, self.ik_rot, 
                                                                                                                          [strFw_jnt_chain, nonstrFw_jnt_chain], [strBw_jnt_chain, nonstrBw_jnt_chain],
                                                                                                                        [strRig_jnt_chain, nonStrRig_jnt_chain])
        # curve creation
        logic_FWcurve = self.cr_logic_curve("StrFw", skeleton_pos)
        logic_BWcurve = self.cr_logic_curve("StrBw", skeleton_pos, True)
        # global curve ik setup
        cv_info_FWnode, fm_global_FWnode = self.wire_ik_curve_setup("StrFw", logic_FWcurve, input_grp)
        cv_info_BWnode, fm_global_BWnode = self.wire_ik_curve_setup("StrBw", logic_BWcurve, input_grp)
        
        # control to logic setup
        self.wire_ctrl_to_jnt_logic()
        self.wire_ik_bott_top_logic_to_skn('skn', skeleton_pos)
        
        ''''''
        # stretch ik setup 
        self.wire_ik_stretch_setup("StrFw", logic_FWcurve, skeleton_pos, fm_global_FWnode)
        self.wire_ik_stretch_setup("StrBw", logic_BWcurve, skeleton_pos, fm_global_BWnode, True)

        # volume presevation
        self.wire_ik_volume_setup("skn", skeleton_pos, input_grp, cv_info_FWnode, fm_global_FWnode)

        # nonStr matching Str chain
        self.nonStr_match_setup(nonstrFw_jnt_chain, strFw_jnt_chain)
        self.nonStr_match_setup(nonstrBw_jnt_chain, strBw_jnt_chain)

        self.blend_fw_bw_states_to_skin_chain(strFw_jnt_chain, strBw_jnt_chain, strRig_jnt_chain,
                                              nonstrFw_jnt_chain, nonstrBw_jnt_chain, nonStrRig_jnt_chain,
                                              skn_jnt_chain)
        
        self.output_group_setup(output_grp, self.ik_pos, self.ik_ctrl_ls[-1], self.ik_ctrl_ls[0])

        # group the module into a consitent hierarchy structure for my modules.
        utils.group_module(self.mdl_nm, self.unique_id, self.side ,input_grp, output_grp, F"grp_ctrls_{self.mdl_nm}", f"grp_joints_{self.mdl_nm}", f"grp_logic_{self.mdl_nm}")
        ''''''
    
    # Temporary functions for skn joints & ctrl creation ----------------------
    def build_ctrls(self, fk_pos, ik_pos):
        '''
        # Description:
            For temporary use; builds the 3 sets of controls for this module. 
            FK / IK / InvFK. They are positioned at the world for the time being.
        # Attributes:
            fk_pos (dict): key = fk ctrl name, value = positonal data.
            ik_pos (dict): key = ik ctrl name, value = positonal data.
        # Returns:
            List of FK / InvFK / IK controls.
        '''
        inv_values = list(fk_pos.values())[::-1]
        # Create a new dictionary with the reversed values.
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
            fk_scl = 1
            cmds.scale(fk_scl, fk_scl, fk_scl, fk_name)
            cmds.makeIdentity(fk_name, a=1, t=0, r=1, s=1, n=0, pn=1)
            # cmds.xform(fk_name, translation=spn_pos, worldSpace=True)
            utils.colour_object(fk_name, 17)
            for axis in (['x', 'y', 'z']):
                cmds.setAttr(f"{fk_name}.s{axis}", lock=1, keyable=0, cb=0)
            
        for spn_name, spn_pos in inv_fk_pos.items():
            inv_name = spn_name.replace("_fk_", "_inv_")
            inv_ctrl_ls.append(inv_name)
            inv_import_ctrl = cr_ctrl.CreateControl(type="bvSquare", name=inv_name)
            inv_import_ctrl.retrun_ctrl()
            inv_scl = 1
            cmds.scale(inv_scl, inv_scl, inv_scl, inv_name)
            cmds.makeIdentity(inv_name, a=1, t=0, r=1, s=1, n=0, pn=1)
            # cmds.xform(inv_name, translation=spn_pos, worldSpace=True)
            utils.colour_object(inv_name, 21)
            for axis in (['x', 'y', 'z']):
                cmds.setAttr(f"{inv_name}.s{axis}", lock=1, keyable=0, cb=0)

        # ik ctrls
        for spn_name, spn_pos in ik_pos.items():
            ik_name = f"{spn_name}"
            ik_ctrl_ls.append(ik_name)
            ik_import_ctrl = cr_ctrl.CreateControl(type="octogan", name=ik_name)
            ik_import_ctrl.retrun_ctrl()
            cmds.rotate(0, 0, 90, ik_name)
            cmds.scale(1.5, 1.5, 1.5, ik_name)
            # cmds.scale(0.25, 0.25, 0.25, ik_name)
            cmds.makeIdentity(ik_name, a=1, t=0, r=1, s=1, n=0, pn=1)
            # cmds.xform(ik_name, translation=spn_pos, worldSpace=True)
            utils.colour_object(ik_name, 17)
            for axis in (['x', 'y', 'z']):
                cmds.setAttr(f"{ik_name}.s{axis}", lock=1, keyable=0, cb=0)

        return fk_ctrl_ls, inv_ctrl_ls, ik_ctrl_ls
    

    def group_ctrls(self, fk_ctrl_ls, inv_ctrl_ls, ik_ctrl_ls):
        '''
        # Description:
            Creates control groups for this module.
        # Attributes:
            fk_ctrl_ls (list): list of fk controls.
            inv_ctrl_ls (list): list of Invfk controls.
            ik_ctrl_ls (list): list of ik controls.
        # Returns:N/A
        '''
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
        '''
        # Description:
            Creates top & bottom skin joints which are intended to be driven by
            their respective control & drive the geometry with skincluster.
        # Attributes:
            ik_pos (dict): key = fk ctrl name, value = positonal data.
        # Returns:
            bott_name (string): bott skin joint name.
            top_name (string): top skin joint name.
        '''
        names = [key for key in ik_pos.keys()]
        pos = [value for value in ik_pos.values()]
        bott_name = names[0].replace("ctrl_ik_", "jnt_skn_")
        top_name = names[-1].replace("ctrl_ik_", "jnt_skn_")
        bott_pos = pos[0]
        top_pos = pos[-1]

        for jnt_nm in [bott_name, top_name]:
            cmds.select(cl=True) 
            cmds.joint(n=jnt_nm)

        return bott_name, top_name


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


    def group_jnts_skn(self, bott_name, top_name, skn_jnt_chain):
        '''
        # Description:
            Creates joint group for this module.
        # Attributes:
            bott_name (string): skin bottom joint.
            top_name (string): skin top joint. 
            skn_jnt_chain (list): list of skin joint chain.
        # Returns:
            joint_grp (string): Joint group.
        '''
        joint_grp = f"grp_joints_{self.mdl_nm}"
        utils.cr_node_if_not_exists(0, "transform", joint_grp)
        cmds.parent(bott_name, top_name, skn_jnt_chain[0], joint_grp)

        return joint_grp


    def cr_input_output_groups(self, jnt_num):
        '''
        # Description:
            Creates the 'Input' & 'Output' groups for this module. These are 
            specialised nodes that store custom matrix data to allow the module 
            to be driven(Input) or be the driver(Output) for other modules, etc. 
        # Attributes:
            jnt_num (int): number of joints in the module - used for the 
            stretchVolume attr on Input group.
        # Returns:
            inputs_grp (string): Group for input data for this module.
            outputs_grp (string): Group for Ouput data for this module.
        '''
        # create input & output groups
        inputs_grp = f"grp_{self.mdl_nm}Inputs"
        outputs_grp = f"grp_{self.mdl_nm}Outputs"
        utils.cr_node_if_not_exists(0, "transform", inputs_grp)
        utils.cr_node_if_not_exists(0, "transform", outputs_grp)
        
        # custom atr on 'input group'
            # - "Global_Scale" (flt)
            # - "Base_Matrix" (matrix)
            # - "Hook_Matrix" (matrix)
            # - "Spine0-9_Stretch_Volume" (flt) = -0.5

        # custom atr on 'output group'
            # - "ctrl_spine_bottom" (matrix)
            # - "ctrl_spine_top" (matrix)
        utils.add_float_attrib(inputs_grp, ["globalScale"], [0.01, 999], True) 
        cmds.setAttr(f"{inputs_grp}.globalScale", 1, keyable=0, channelBox=0)
        utils.add_attr_if_not_exists(inputs_grp, "base_mtx", 'matrix', False)
        utils.add_attr_if_not_exists(inputs_grp, "hook_mtx", 'matrix', False)
        for x in range(jnt_num):
            utils.add_float_attrib(inputs_grp, [f"{self.mdl_nm}{x}_Stretch_Volume"], [1.0, 1.0], False)
            cmds.setAttr(f"{inputs_grp}.{self.mdl_nm}{x}_Stretch_Volume", keyable=1, channelBox=1)
            cmds.setAttr(f"{inputs_grp}.{self.mdl_nm}{x}_Stretch_Volume", -0.5)

        utils.add_attr_if_not_exists(outputs_grp, f"ctrl_{self.mdl_nm}_bottom_mtx", 
                                    'matrix', False) # for upper body module to follow
        utils.add_attr_if_not_exists(outputs_grp, f"ctrl_{self.mdl_nm}_top_mtx", 
                                    'matrix', False) # for lower body module to follow

        return inputs_grp, outputs_grp


    def wire_spine_ctrls(self, root_outputs_grp, input_grp):
        '''
        TO DO:
            Add rotation data too w/ 'self.fk_rot (dict)' & 'self.ik_rot (dict)'.
        # Description:
            Sets up the control's relationship, positions them using matrix data 
            as well as how the 3 states work together:
            - Fk controls setup.
            - InverseFK control setup.
            - End fk controls Top ik ctrl.
            - End fkInv controls Bottom ik ctrl.
            - IK Top & Bottom controls share the control over the middle control.
            This works by using the data of 'self.fk_pos (dict)' & 'self.ik_pos (dict)'
            but not any rotation values are applied atm. 
        # Attributes:
            root_outputs_grp (string): 'Output' grp from other module for this one to follow.
            input_grp (string): Group for input data for this module.
        # Returns:
            fk_ctrl_ls (list): list of fk controls.
            inv_ctrl_ls (list): list of fkInv controls.
            ik_ctrl_ls (list): list of ik controls.
        '''
        # connect the root module to the spine module with inputs group nodes!
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
        fk_previous_pos = None
        inv_previous_pos = None
        reversed_fk_pos = utils.reverse_dict(self.fk_pos) # reverse the pos so the maths offset equation works!
        for i, ((fk_ctrl_name, fk_pos), (inv_name, inv_pos)) in enumerate(zip(self.fk_pos.items(), reversed_fk_pos.items())):
            inv_ctrl_name = inv_name.replace('fk', 'inv')
            fk_ctrl_ls.append(fk_ctrl_name)
            inv_ctrl_ls.append(inv_ctrl_name)
                # cr MM names
            MM_fk_name = f"MM_{fk_ctrl_name}"
            MM_inv_name = f"MM_{inv_ctrl_name}"
                # cr the MM nodes
            utils.cr_node_if_not_exists(1, 'multMatrix', MM_fk_name)
            utils.cr_node_if_not_exists(1, 'multMatrix', MM_inv_name)
                # append their names to the list
            MM_fk_ls.append(MM_fk_name)
            MM_inv_ls.append(MM_inv_name)
                # Calculate the offset for the next control
            if fk_previous_pos is not None:
                fk_offset = [p2 - p1 for p1, p2 in zip(fk_previous_pos, fk_pos)]
                utils.set_matrix(fk_offset, f"{MM_fk_name}{utils.Plg.mtx_ins[0]}")
            if inv_previous_pos is not None:
                inv_offset = [p2 - p1 for p1, p2 in zip(inv_previous_pos, inv_pos)]
                utils.set_matrix(inv_offset, f"{MM_inv_name}{utils.Plg.mtx_ins[0]}")
            fk_previous_pos = fk_pos
            inv_previous_pos = inv_pos
       
        # connect the MMs
            # iniitial inputs
        print(f"inv_0, list(self.fk_pos.values())[-1] = {list(self.fk_pos.values())[-1]}")
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
        utils.add_float_attrib(ik_ctrl_ls[-1], [f"{self.mdl_nm}_Stretch_State"], [0, 1], True)
        utils.add_float_attrib(ik_ctrl_ls[-1], [f"{self.mdl_nm}_Stretch_Anchor"], [0, 1], True)
        utils.add_float_attrib(ik_ctrl_ls[-1], [f"{self.mdl_nm}_Stretch_Volume"], [0, 1], True)

        # proxy the stretch attributes to the other ikctrls!
        for remaining_ik_ctrl in ik_ctrl_ls[:-1]:
            utils.proxy_attr_list(ik_ctrl_ls[-1], remaining_ik_ctrl, f"Attributes")
            utils.proxy_attr_list(ik_ctrl_ls[-1], remaining_ik_ctrl, f"{self.mdl_nm}_Stretch_State")
            utils.proxy_attr_list(ik_ctrl_ls[-1], remaining_ik_ctrl, f"{self.mdl_nm}_Stretch_Anchor")
            utils.proxy_attr_list(ik_ctrl_ls[-1], remaining_ik_ctrl, f"{self.mdl_nm}_Stretch_Volume")

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
        logic_grp = f"grp_logic_{self.mdl_nm}"
        fk_grp = f"grp_jnts_fk_{self.mdl_nm}"
        inv_grp = f"grp_jnts_inv_{self.mdl_nm}"
        ik_grp = f"grp_jnts_ik_{self.mdl_nm}"
        ikFw_grp = f"grp_ikFw_{self.mdl_nm}_{self.unique_id}_{self.side}"
        ikBw_grp = f"grp_ikBw_{self.mdl_nm}_{self.unique_id}_{self.side}"
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


    def cr_logic_curve(self, pref, skeleton_pos, backwards=False):
        '''        
        # Description:
            Creates a new logic curve & organises it into the logic_grp. 
        # Attributes:
            pref (string): name of the joint chain type.
            skeleton_pos (dict): key = name of spine iteration (spine#), value = positonal data.
            backwards (bool): If True, the curve direction is reversed (0-1).
        # Returns:
            logic_curve (string): The name of the new curve created. 
        '''
        logic_curve = f"crv_{pref}_{self.mdl_nm}"
        positions = list(skeleton_pos.values())
        cmds.curve(n=logic_curve, d=3, p=positions)
        cmds.rebuildCurve(logic_curve, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=0, kt=0, s=1, d=3, tol=0.01)
        if backwards:
            ''' reverse the dirtection of the curve '''
            cmds.reverseCurve(logic_curve, constructionHistory=True, replaceOriginal=True)
        cmds.parent(logic_curve, self.logic_grp)

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
        CvInfo = f"CI_{jnt_pref}_{self.mdl_nm}_{self.unique_id}"
        utils.cr_node_if_not_exists(1, "curveInfo", CvInfo)
        utils.connect_attr(f"{crv_logic_shape}{utils.Plg.wld_space_plg}", 
                           f"{CvInfo}{utils.Plg.inp_curve_plg}")
        FM_spine_global = f"FM_{jnt_pref}_{self.mdl_nm}_global_div_{self.unique_id}"
        utils.cr_node_if_not_exists(1, "floatMath", FM_spine_global, {"operation": 3})
        # connections
            # global FM
        utils.connect_attr(f"{CvInfo}{utils.Plg.arc_len_plg}", f"{FM_spine_global}{utils.Plg.flt_A}")
        utils.connect_attr(f"{input_grp}.globalScale", f"{FM_spine_global}{utils.Plg.flt_B}")

        return CvInfo, FM_spine_global


    def wire_ctrl_to_jnt_logic(self):
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
            self.fk_ctrl_ls, self.inv_ctrl_ls, self.ik_ctrl_ls, 
            self.fk_logic_ls, self.inv_logic_ls, self.ik_logic_ls
            ):
            print(f"fk_ctrl = {fk_ctrl} | {fk_logic}")
            print(f"inv_ctrl = {inv_ctrl} | {inv_logic}")
            print(f"fk_ctrl = {ik_ctrl} | {ik_logic}")
            MM_fk_logic = utils.mtxCon_no_ofs(fk_ctrl, fk_logic)
            MM_inv_logic = utils.mtxCon_no_ofs(inv_ctrl, inv_logic)
            MM_ik_logic = utils.mtxCon_no_ofs(ik_ctrl, ik_logic)


    def wire_ik_bott_top_logic_to_skn(self, jnt_pref, skeleton_pos):
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
            skeleton_pos (dict): key = name of spine iteration (spine#), value = positonal data.
        # Returns: N/A
        '''
        skn_skel_keys = list(skeleton_pos.keys())
        skn_skel_positions = [int(re.search(r'\d+', s).group()) for s in skn_skel_keys][::-1]
        print(f"skn_skel_positions = `{skn_skel_positions}`")
        
        skn_top_jnt = self.ik_logic_ls[-1].replace('ik', jnt_pref)
        skn_bot_jnt = self.ik_logic_ls[0].replace('ik', jnt_pref)
        cmds.setAttr(f"{skn_top_jnt}.radius", 3)
        cmds.setAttr(f"{skn_bot_jnt}.radius", 3)

        # check if skn has none default values
        if not utils.check_non_default_transforms(skn_bot_jnt) or utils.check_non_default_transforms(skn_top_jnt):
            print(f"{skn_bot_jnt} & {skn_top_jnt} have none default values and require cleaning")
            utils.clean_opm([skn_bot_jnt, skn_top_jnt])

        # get the names of the top ik_jnt & skn_chain joint
        top_ik_jnt = self.ik_logic_ls[-1]
        bottom_ik_jnt = self.ik_logic_ls[0]
        # 'output_skn_jnt' refers to the skn joint chain!
        top_output_skn_jnt = f"jnt_{jnt_pref}_{self.mdl_nm}_spine{skn_skel_positions[0]}_{self.unique_id}_{self.side}"
        bottom_output_skn_jnt = f"jnt_{jnt_pref}_{self.mdl_nm}_spine{skn_skel_positions[-1]}_{self.unique_id}_{self.side}"

        # cr two decompose matrix nodes & a compMatrix node for each jnt_skn_top/bottom
        top_translate_dcM = f"DCM_translate_top_{top_output_skn_jnt}"
        top_rotate_dcM = f"DCM_rotate_top_{top_ik_jnt}"
        top_cM = f"CM_driver_{skn_top_jnt}"
        bottom_translate_dcM = f"DCM_translate_bot_{bottom_output_skn_jnt}"
        bottom_rotate_dcM = f"DCM_rotate_bot_{bottom_ik_jnt}"
        bottom_cM = f"CM_driver_{skn_bot_jnt}"
        utils.cr_node_if_not_exists(0, "decomposeMatrix", top_translate_dcM)
        utils.cr_node_if_not_exists(0, "decomposeMatrix", top_rotate_dcM)
        utils.cr_node_if_not_exists(0, "composeMatrix", top_cM)
        utils.cr_node_if_not_exists(0, "decomposeMatrix", bottom_translate_dcM)
        utils.cr_node_if_not_exists(0, "decomposeMatrix", bottom_rotate_dcM)
        utils.cr_node_if_not_exists(0, "composeMatrix", bottom_cM)

        # wire connections
        utils.connect_attr(f"{top_ik_jnt}{utils.Plg.wld_mtx_plg}", f"{top_rotate_dcM}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{top_output_skn_jnt}{utils.Plg.wld_mtx_plg}", f"{top_translate_dcM}{utils.Plg.inp_mtx_plg}")

        utils.connect_attr(f"{bottom_ik_jnt}{utils.Plg.wld_mtx_plg}", f"{bottom_rotate_dcM}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{bottom_output_skn_jnt}{utils.Plg.wld_mtx_plg}", f"{bottom_translate_dcM}{utils.Plg.inp_mtx_plg}")

        utils.connect_attr(f"{top_translate_dcM}.outputTranslate", f"{top_cM}.inputTranslate")
        utils.connect_attr(f"{top_rotate_dcM}.outputRotate", f"{top_cM}.inputRotate")
        utils.connect_attr(f"{bottom_translate_dcM}.outputTranslate", f"{bottom_cM}.inputTranslate")
        utils.connect_attr(f"{bottom_rotate_dcM}.outputRotate", f"{bottom_cM}.inputRotate")
        
        utils.connect_attr(f"{top_cM}{utils.Plg.out_mtx_plg}", f"{skn_top_jnt}{utils.Plg.opm_plg}")
        utils.connect_attr(f"{bottom_cM}{utils.Plg.out_mtx_plg}", f"{skn_bot_jnt}{utils.Plg.opm_plg}")

    
    def wire_ik_stretch_setup(self, jnt_pref, logic_curve, skeleton_pos, fm_global_curve, backwards=False):
        '''
        # Description:            
            Creates stretch setup on specified joint chain with an ik spline setup. 
            Intentionally keeping the stretch on at all time & not connecting the stretch_state attr.
        # Attributes:
            jnt_pref (string): name of the joint chain to cr stretch setup on.
            logic_curve (string): The name of the new curve created.
            skeleton_pos (dict): key = name of spine iteration (spine#), value = positonal data.
            fm_global_curve (utility): Float math node of the arclenght and 'globalScale' passed to this module.
            backwards (bool): If True, the curve direction is reversed (0-1).
        # Returns: N/A
        '''
        jnt_skeleton_ls = [f"jnt_{jnt_pref}_{self.mdl_nm}_{j}_{self.unique_id}_{self.side}" for j in skeleton_pos.keys()]
        num_squash_jnts = len(skeleton_pos.keys())-1
        
        # curve skinning method: skin the top & bottom ik skn joints to curve skin 
        # the middle & hold logic joints create inversmatrix, > plug middle MM into inversmatrix
        # > plug inversematrix into bind bind pre-matrix on the 2nd skincluster!
        jnt_ik_logic_mid = self.ik_logic_ls[1]
        cmds.skinCluster([self.ik_logic_ls[0], self.ik_logic_ls[-1]], logic_curve, tsb=True, wd=1)[0]
        # # Create the second skinCluster
        middle_skincluster = cmds.skinCluster([jnt_ik_logic_mid, self.jnt_mid_hold], logic_curve, tsb=True, wd=1, multi=1)[0]
        cmds.skinPercent( middle_skincluster, f"{logic_curve}.cv[0]", f"{logic_curve}.cv[3]", tv=[(self.jnt_mid_hold, 1)])
        # skinPercent -tv jnt_hold  1 skinCluster4 curve1.cv[0:1] curve1.cv[4:5]

        inv_mtx = f"IM_{jnt_ik_logic_mid}"
        utils.cr_node_if_not_exists(1, "inverseMatrix", inv_mtx)
        utils.connect_attr(f"MM_{self.ik_ctrl_ls[1]}{utils.Plg.mtx_sum_plg}", f"{inv_mtx}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{inv_mtx}{utils.Plg.out_mtx_plg}", f"{middle_skincluster}.bindPreMatrix[0]")
        
        # Util nodes for stretch setup
        FM_spine_joints = f"FM_{jnt_pref}_{self.mdl_nm}_joints_div_{self.unique_id}"
        BC_spine_squash = F"BC_{jnt_pref}_{self.mdl_nm}_stretchVolume_{self.unique_id}"

        utils.cr_node_if_not_exists(1, "floatMath", FM_spine_joints, {"operation": 3, "floatB": num_squash_jnts})
        utils.cr_node_if_not_exists(1, "blendColors", BC_spine_squash, {"color1G": 1, "color2R": 1, "color2G": 1, "color2B": 1})
       
           # joints FM
        utils.connect_attr(f"{fm_global_curve}{utils.Plg.out_flt}", f"{FM_spine_joints}{utils.Plg.flt_A}")
        
        # This provides the stretch effect by moving the joints. 
        #---- skeleton transaltion PRIMARY AXIS joint!
        # get FM_spine_joints_div.floatA attr and set it to new 
        still_stretch_dividend = cmds.getAttr(f"{FM_spine_joints}{utils.Plg.flt_A}")
        # cr utility nodes neccessary to blend a smooth on & off of the stretch
        FM_trans_still = f"FM_{jnt_pref}_{self.mdl_nm}_joints_div_still_{self.unique_id}"
        BC_stretch_active = F"BC_{jnt_pref}_{self.mdl_nm}_activeStretch_{self.unique_id}"
        BC_stretch_still = F"BC_{jnt_pref}_{self.mdl_nm}_stillStretchLength_{self.unique_id}"
        BC_stretch_output = F"BC_{jnt_pref}_{self.mdl_nm}_translateStretchOutput_{self.unique_id}"
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
        # utils.connect_attr(f"{self.ik_ctrl_ls[-1]}.{self.mdl_nm}_Stretch_State", f"{BC_stretch_output}{utils.Plg.blndr_plg}")
        
        if backwards:
            # cr negative MD
            md_negative = f"MD_{jnt_pref}_{self.mdl_nm}_negativeStretchOutput_{self.unique_id}"
            utils.cr_node_if_not_exists(1, "multiplyDivide", md_negative, {"operation": 1, "input1X":-1})
            # connect parent BC to negative MD            
            utils.connect_attr(f"{BC_stretch_output}{utils.Plg.out_letter[0]}", f"{md_negative}{utils.Plg.input2_val[0]}")
            for x in range(1, len(skeleton_pos.keys())):  
                # connect negative MD to skeleton translatePrimaryAxis. 
                utils.connect_attr(f"{md_negative}{utils.Plg.out_axis[0]}", f"{jnt_skeleton_ls[x]}.translate{self.prim_axis}")
        else:
            for x in range(1, len(skeleton_pos.keys())):  
                # connect BC_spine_StretchOutput to skeleton translatePrimaryAxis. 
                utils.connect_attr(f"{BC_stretch_output}{utils.Plg.out_letter[0]}", f"{jnt_skeleton_ls[x]}.translate{self.prim_axis}")
        
        # ---------------
        # ik spline setup w/ advanced twist on ik handle
        print(f"ikHandle: jnt_pref = `{jnt_pref}`, jnt_skeleton_ls[-1] = {jnt_skeleton_ls[-1]}, jnt_skeleton_ls[0] = {jnt_skeleton_ls[0]},")
        
        hdl_spine_name = f"hdl_{jnt_pref}_{self.mdl_nm}_spline_{self.unique_id}_{self.side}"
        cmds.ikHandle( n=hdl_spine_name, sol="ikSplineSolver", c=logic_curve, sj=jnt_skeleton_ls[0], ee=jnt_skeleton_ls[-1], ccv=False, pcv=False)
        cmds.parent(hdl_spine_name, f"grp_logic_{self.mdl_nm}")
        # Enable advanced twist options on hdl_spine_name
        cmds.setAttr(  f"{hdl_spine_name}.dTwistControlEnable", 1 )
        cmds.setAttr( f"{hdl_spine_name}.dWorldUpType", 4 )              
        
        positive_y = 2
        negative_y = 3
        if backwards:
            cmds.setAttr(f"{hdl_spine_name}.dForwardAxis", negative_y)
            # Set the 'World Up Object' to the controller the is driving the first joint of the chain. (ctrl_ik_pelvis)
            utils.connect_attr(f"{self.ik_ctrl_ls[-1]}{utils.Plg.wld_mtx_plg}", f"{hdl_spine_name}.dWorldUpMatrix")
            utils.connect_attr(f"{self.ik_ctrl_ls[0]}{utils.Plg.wld_mtx_plg}", f"{hdl_spine_name}.dWorldUpMatrixEnd")
        else:
            cmds.setAttr(f"{hdl_spine_name}.dForwardAxis", positive_y)
            utils.connect_attr(f"{self.ik_ctrl_ls[0]}{utils.Plg.wld_mtx_plg}", f"{hdl_spine_name}.dWorldUpMatrix")
            utils.connect_attr(f"{self.ik_ctrl_ls[-1]}{utils.Plg.wld_mtx_plg}", f"{hdl_spine_name}.dWorldUpMatrixEnd")
       
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpAxis", 3 ) # neg x
        # Xvals
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpVectorX", 0)
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpVectorEndX", 0)
        # Yvals
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpVectorY", 0)
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpVectorEndY", 0)
        # Zvals
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpVectorZ", 1)
        cmds.setAttr(f"{hdl_spine_name}.dWorldUpVectorEndZ", 1)


    def wire_ik_volume_setup(self, jnt_pref, skeleton_pos, input_grp, cv_info_node, fm_global_curve):
        '''
        # Description:            
            Wires the data from the Input grp to the skin joint's scale attr to 
            control Volume preservation when the joint's stretch.
        # Attributes:
            jnt_pref (string): name of the joint chain to cr stretch setup on.
            skeleton_pos (dict): key = name of spine iteration (spine#), value = positonal data.
            input_grp (string): Group for input data for this module.
            fm_global_curve (utility): Float math node of the arclenght and 'globalScale' passed to this module.
        # Returns: N/A
        '''
        cv_arc_length = cmds.getAttr(f"{cv_info_node}{utils.Plg.arc_len_plg}")

        FM_spine_norm = F"FM_{self.mdl_nm}_norm_{self.unique_id}"
        BC_spine_squash = F"BC_{self.mdl_nm}_stretchVolume_{self.unique_id}"        
        utils.cr_node_if_not_exists(1, "floatMath", FM_spine_norm, {"operation": 3, "floatB": cv_arc_length})
        utils.cr_node_if_not_exists(1, "blendColors", BC_spine_squash, {"color1G": 1, "color2R": 1, "color2G": 1, "color2B": 1})
        
        jnt_skeleton_ls = [f"jnt_{jnt_pref}_{self.mdl_nm}_{j}_{self.unique_id}_{self.side}" for j in skeleton_pos.keys()]
        MD_skeleton_ls = []
        for jnt in jnt_skeleton_ls:
            md_name = f"MD_{jnt}"
            utils.cr_node_if_not_exists(1, "multiplyDivide", md_name, {"operation": 3})
            MD_skeleton_ls.append(md_name)

        utils.connect_attr(f"{fm_global_curve}{utils.Plg.out_flt}", f"{FM_spine_norm}{utils.Plg.flt_A}")
        utils.connect_attr(f"{self.ik_ctrl_ls[-1]}.{self.mdl_nm}_Stretch_Volume", f"{BC_spine_squash}{utils.Plg.blndr_plg}")
        utils.connect_attr(f"{FM_spine_norm}{utils.Plg.out_flt}", f"{BC_spine_squash}{utils.Plg.color1_plg[0]}")
        utils.connect_attr(f"{FM_spine_norm}{utils.Plg.out_flt}", f"{BC_spine_squash}{utils.Plg.color1_plg[2]}")
        
        for x in range(len(skeleton_pos.keys())):
                # MD
            utils.connect_attr(f"{BC_spine_squash}{utils.Plg.out_letter[0]}", f"{MD_skeleton_ls[x]}{utils.Plg.input1_val[0]}")
            utils.connect_attr(f"{BC_spine_squash}{utils.Plg.out_letter[2]}", f"{MD_skeleton_ls[x]}{utils.Plg.input1_val[2]}")
            utils.connect_attr(f"{input_grp}.{self.mdl_nm}{x}_Stretch_Volume", f"{MD_skeleton_ls[x]}{utils.Plg.input2_val[0]}")
            utils.connect_attr(f"{input_grp}.{self.mdl_nm}{x}_Stretch_Volume", f"{MD_skeleton_ls[x]}{utils.Plg.input2_val[2]}")
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
        cmds.parentConstraint(Str_jnt_chain[0], nonStr_jnt_chain[0], mo=1)

        # orient constrain the remaining items in the list of chains
        child_nonStr_jnt_chain = nonStr_jnt_chain[1:]
        child_Str_jnt_chain_ls = Str_jnt_chain[1:]
        for x in range(len(child_nonStr_jnt_chain)):
            cmds.orientConstraint(child_Str_jnt_chain_ls[x], child_nonStr_jnt_chain[x])


    def blend_fw_bw_states_to_skin_chain(self, strFw_chain, strBw_chain, rigStr, 
                                         nonstrFw_chain, nonstrBw_chain, nonrigStr,
                                         skn_chain):
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
            cmds.parentConstraint(strFw_chain[x], strBw_chain[x], rigStr[x], n=f"Pcon_FwBw_{rigStr[x]}")# , n=f"Pcon_FwBw_{rigStr}")
        cmds.select(cl=1)
        # Pcon nonrigStr by nonstrFw_chain & nonstrBw_chain
        nonstrBw_chain.reverse()
        for x in range(len(nonrigStr)):
            print(f"ORDER rev nonBw: {nonstrFw_chain[x]}, {nonstrBw_chain[x]}, {nonrigStr[x]}")
            cmds.parentConstraint(nonstrFw_chain[x], nonstrBw_chain[x], nonrigStr[x], n=f"Pcon_nonFwBw_{nonrigStr[x]}")#, n=f"Pcon_FwBw_{nonrigStr}")
        cmds.select(cl=1)
        # Pcon skn_chain by rigStr & nonrigStr
        for x in range(len(skn_chain)):
            print(f"{rigStr[x]}, {nonrigStr[x]}, {skn_chain[x]}, n=Pcon_StrRig_nonStrRig_{skn_chain}")
            cmds.parentConstraint(rigStr[x], nonrigStr[x], skn_chain[x], n=f"Pcon_StrRig_nonStrRig_{skn_chain[x]}")

        # wire up the Stretch_Anchor attrib.
        rev_skn_str = f"Rev_sknStr_{self.mdl_nm}_{self.unique_id}"
        rev_strAnchor = f"Rev_stretchAnchor_{self.mdl_nm}_{self.unique_id}"
        utils.cr_node_if_not_exists(1, "reverse", rev_skn_str)
        utils.cr_node_if_not_exists(1, "reverse", rev_strAnchor)
        
        # skn chain rev
        utils.connect_attr(f"{self.ik_ctrl_ls[-1]}.{self.mdl_nm}_Stretch_State", f"{rev_skn_str}.inputX")
        # strAnchor rev
        utils.connect_attr(f"{self.ik_ctrl_ls[-1]}.{self.mdl_nm}_Stretch_Anchor", f"{rev_strAnchor}.inputX")
        backward_indexes = [i for i, _ in enumerate(skn_chain)][::-1]
        print(f"backward_indexes = {backward_indexes}")
        for x in range(len(skn_chain)):
            # skn chain
            utils.connect_attr(f"{self.ik_ctrl_ls[-1]}.{self.mdl_nm}_Stretch_State", 
                               f"Pcon_StrRig_nonStrRig_{skn_chain[x]}.jnt_StrRig_{self.mdl_nm}_spine{x}_{self.unique_id}_MW0")
            utils.connect_attr(f"{rev_skn_str}{utils.Plg.out_axis[0]}", 
                               f"Pcon_StrRig_nonStrRig_{skn_chain[x]}.jnt_nonStrRig_{self.mdl_nm}_spine{x}_{self.unique_id}_MW1")
            
            # rigStr chain
            utils.connect_attr(f"{rev_strAnchor}{utils.Plg.out_axis[0]}", 
                               f"Pcon_FwBw_{rigStr[x]}.jnt_StrFw_{self.mdl_nm}_spine{x}_{self.unique_id}_MW0")
            # jnt_StrFw_spine_spine9_0_MW0            
            utils.connect_attr(f"{self.ik_ctrl_ls[-1]}.{self.mdl_nm}_Stretch_Anchor", 
                               f"Pcon_FwBw_{rigStr[x]}.jnt_StrBw_{self.mdl_nm}_spine{backward_indexes[x]}_{self.unique_id}_MW1")
          
            # nonRigStr chain
            utils.connect_attr(f"{rev_strAnchor}{utils.Plg.out_axis[0]}", 
                               f"Pcon_nonFwBw_{nonrigStr[x]}.jnt_nonStrFw_{self.mdl_nm}_spine{x}_{self.unique_id}_MW0")
            utils.connect_attr(f"{self.ik_ctrl_ls[-1]}.{self.mdl_nm}_Stretch_Anchor", 
                               f"Pcon_nonFwBw_{nonrigStr[x]}.jnt_nonStrBw_{self.mdl_nm}_spine{backward_indexes[x]}_{self.unique_id}_MW1")
   

    def output_group_setup(self, mdl_output_grp, ik_pos_dict, ctrl_spine_top, ctrl_spine_bottom):
        '''
        # Description:
            Connects the top & bottom ik controls to attributes on this module's
            output group so another module's inpout group can have incoming plugs to allow it to follow!
            Example: spine output grp (this module) plugs into arm input grp (external/other module) 
                     so it arm can follow the spine! 
        # Attributes:
            mdl_output_grp (str): name of this module's output group
            ik_pos_dict (dict): dict of the ik control's pos
            ctrl_spine_top (str): control name of IK top (could be derived from the dict...)
            ctrl_spine_bottom (str): control name of IK bottom (could be derived from the dict...)
        # Returns: N/A
        # Future updates:
            Problem -> Handle the attrib names on the Input & Output grps in a way that can be shared between the other modules.
            Solution -> Store this data in the database & access it from there when neccessary by encoding it in a dictionary!
        '''
        # cr two multMatrixs
        MM_output_top = f"MM_output_{ctrl_spine_top}"
        MM_output_bot = f"MM_output_{ctrl_spine_bottom}"
            # cr the MM nodes
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_output_top)
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_output_bot)
        # get the offset
        # put the dict into a list & index the correct pos and make it negative
        ik_pos_list = [value for value in list(ik_pos_dict.values())]
        top_offset = [x if x == 0 else -x for x in ik_pos_list[-1]]
        bottom_offset =  [x if x == 0 else -x for x in ik_pos_list[0]]
        print(f"top_offset = {top_offset} | bottom_offset = {bottom_offset}")
        # Plugs - connect ik ctrl's to MM's
        utils.set_matrix(top_offset, f"{MM_output_top}{utils.Plg.mtx_ins[0]}")
        utils.set_matrix(bottom_offset, f"{MM_output_bot}{utils.Plg.mtx_ins[0]}")
        utils.connect_attr(f"{ctrl_spine_top}{utils.Plg.wld_mtx_plg}", f"{MM_output_top}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{ctrl_spine_bottom}{utils.Plg.wld_mtx_plg}", f"{MM_output_bot}{utils.Plg.mtx_ins[1]}")
        # Plugs - connect the MM to the spine output's attribs!  
        utils.connect_attr(f"{MM_output_top}{utils.Plg.mtx_sum_plg}", f"{mdl_output_grp}.ctrl_{self.mdl_nm}_top_mtx")
        utils.connect_attr(f"{MM_output_bot}{utils.Plg.mtx_sum_plg}", f"{mdl_output_grp}.ctrl_{self.mdl_nm}_bottom_mtx")
        
        print("3rd test type shit.")

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
        'ctrl_fk_spine_spine0_0_M': [0.0, 147.0, 0.0], 
        'ctrl_fk_spine_spine1_0_M': [0.0, 167.29999965429306, 0.0], 
        'ctrl_fk_spine_spine2_0_M': [0.0, 187.59999930858612, 0.0]
        },
    "fk_rot":{
        'ctrl_fk_spine_spine0_0_M': [0.0, 0.0, 0.0], 
        'ctrl_fk_spine_spine1_0_M': [0.0, 0.0, 0.0], 
        'ctrl_fk_spine_spine2_0_M': [0.0, 0.0, 0.0]
        }
    }
# Always 3 ctrls!
ik_spine_dict = {
    "ik_pos":{
        'ctrl_ik_spine_spine_bottom_0_M': [0.0, 147.0, 0.0], 
        'ctrl_ik_spine_spine_middle_0_M': [0.0, 176.0, 0.0], 
        'ctrl_ik_spine_spine_top_0_M': [0.0, 205.0, 0.0]
        },
    "ik_rot":{
        'ctrl_ik_spine_spine_bottom_0_M': [0.0, 0.0, 0.0], 
        'ctrl_ik_spine_spine_middle_0_M': [0.0, 0.0, 0.0], 
        'ctrl_ik_spine_spine_top_0_M': [0.0, 0.0, 0.0]
        }
    }

# ------
skeleton_dict_002 = {
    "skel_pos":{
        'spine0': [0.0, 149.99404907226562, 0.0], 
        'spine1': [0.0, 163.67609956253224, 0.5505454896913743], 
        'spine2': [0.0, 176.51040956536684, 0.47938506129239655], 
        'spine3': [0.0, 188.63961008683742, -0.2503962985531877], 
        'spine4': [0.0, 200.24069727159255, -1.6490033326717328], 
        'spine5': [0.0, 212.28094266250034, -3.112293946922094], 
        'spine6': [0.0, 226.51790858442743, -3.421781291403731], 
        'spine7': [0.0, 244.74351501464844, -1.3322676420211792]
        },
    "skel_rot":{
        'spine0': [0.0, 0.0, 0.0], 
        'spine1': [0.0, 0.0, 0.0], 
        'spine2': [0.0, 0.0, 0.0], 
        'spine3': [0.0, 0.0, 0.0], 
        'spine4': [0.0, 0.0, 0.0], 
        'spine5': [0.0, 0.0, 0.0], 
        'spine6': [0.0, 0.0, 0.0], 
        'spine7': [0.0, 0.0, 0.0]
        }
    }
'''
"skel_rot":{
        'spine0': [0.0, 0.0, 0.0], 
        'spine1': [-90.0, -1.0642156226575015, 90.0], 
        'spine2': [-90.0, 1.8129130531688165, 90.0], 
        'spine3': [-90.0, 5.17746565181425, 90.0], 
        'spine4': [-90.0, 8.016548074258269, 90.0], 
        'spine5': [-90.0, 4.869653596501576, 90.0], 
        'spine6': [-90.0, -2.4527863792809406, 90.0], 
        'spine7': [-90.0, -10.089238271081271, 90.0]
        }
'''
''' ---These outputs will be determined by Char_Layout tool! 
        (place joints, choose num of ctrls, position ctrls, shape ctrls)--- '''
# I want this to be changable (3 by default)
fk_spine_dict_002 = {
    "fk_pos":{
        'ctrl_fk_spine_spine0_0_M': [0.0, 149.99404907226562, 0.0], 
        'ctrl_fk_spine_spine1_0_M': [0.0, 176.51040956536684, 0.47938506129239655], 
        'ctrl_fk_spine_spine2_0_M': [0.0, 212.28094266250034, -3.112293946922094]
        },
    "fk_rot":{
        'ctrl_fk_spine_spine0_0_M': [0.0, 0.0, 0.0], 
        'ctrl_fk_spine_spine1_0_M': [-90.0, 1.8129130531688165, 90.0], 
        'ctrl_fk_spine_spine2_0_M': [-90.0, 4.869653596501576, 90.0]
        }
    }
# Always 3 ctrls!
ik_spine_dict_002 = {
    "ik_pos":{
        'ctrl_ik_spine_spine_bottom_0_M': [0.0, 149.99404907226562, 0.0], 
        'ctrl_ik_spine_spine_middle_0_M': [0.0, 176.51040956536684, 0.47938506129239655], 
        'ctrl_ik_spine_spine_top_0_M': [0.0, 244.74351501464844, -1.3322676420211792]
        },
    "ik_rot":{
        'ctrl_ik_spine_spine_bottom_0_M': [0.0, 0.0, 0.0], 
        'ctrl_ik_spine_spine_middle_0_M': [-90.0, 1.8129130531688165, 90.0], 
        'ctrl_ik_spine_spine_top_0_M': [-90.0, -10.089238271081271, 90.0]
        }
    }

SpineSystem("spine", "grp_rootOutputs", skeleton_dict, fk_spine_dict, ik_spine_dict, "Y")
# SpineSystem("spine", "grp_rootOutputs", skeleton_dict_002, fk_spine_dict_002, ik_spine_dict_002, "X")

'''
correct ori backwards{
        'spine0': [0.0, 149.99404907226562, 0.0],
        'spine1': [-1.5777218104420236e-30, 163.67609956253227, 0.5505454896913758], 
        'spine2': [5.4329662066347425e-15, 176.51040956536687, 0.4793850612923948], 
        'spine3': [1.0261634202060544e-14, 188.63961008683745, -0.2503962985531931], 
        'spine4': [1.4556671875674994e-14, 200.24069727159258, -1.6490033326717561], 
        'spine5': [1.9008879104396965e-14, 212.2809426625003, -3.1122939469221054], 
        'spine6': [2.4929193343529772e-14, 226.5179085844274, -3.421781291403751], 
        'spine7': [3.3655513459783803e-14, 244.74351501464847, -1.332267642021204]
        },

# Snake middle body example:
# skel_midBody_dict = {
#     "skel_pos":{
#         'midBody0': [0.0, 0.0, -20.0], 
#         'midBody1': [0.0, 0.0, -18.0], 
#         'midBody2': [0.0, 0.0, -16.0], 
#         'midBody3': [0.0, 0.0, -14.0], 
#         'midBody4': [0.0, 0.0, -12.0], 
#         'midBody5': [0.0, 0.0, -10.0], 
#         'midBody6': [0.0, 0.0, -8.0], 
#         'midBody7': [0.0, 0.0, -6.0], 
#         'midBody8': [0.0, 0.0, -4.0], 
#         'midBody9': [0.0, 0.0, -2.0], 
#         'midBody10': [0.0, 0.0, 0.0], 
#         'midBody11': [0.0, 0.0, 2.0], 
#         'midBody12': [0.0, 0.0, 4.0], 
#         'midBody13': [0.0, 0.0, 6.0], 
#         'midBody14': [0.0, 0.0, 8.0], 
#         'midBody15': [0.0, 0.0, 10.0], 
#         'midBody16': [0.0, 0.0, 12.0], 
#         'midBody17': [0.0, 0.0, 14.0],
#         'midBody18': [0.0, 0.0, 16.0]
#         },
#     "skel_rot":{'midBody0': [90.0, 0.0, 0.0], 'midBody1': [90.0, 0.0, 0.0], 'midBody2': [90.0, 0.0, 0.0], 'midBody3': [90.0, 0.0, 0.0], 'midBody4': [90.0, 0.0, 0.0], 'midBody5': [90.0, 0.0, 0.0], 'midBody6': [90.0, 0.0, 0.0], 'midBody7': [90.0, 0.0, 0.0], 'midBody8': [90.0, 0.0, 0.0], 'midBody9': [90.0, 0.0, 0.0], 'midBody10': [90.0, 0.0, 0.0], 'midBody11': [90.0, 0.0, 0.0], 'midBody12': [90.0, 0.0, 0.0], 'midBody13': [90.0, 0.0, 0.0], 'midBody14': [90.0, 0.0, 0.0], 'midBody15': [90.0, 0.0, 0.0], 'midBody16': [90.0, 0.0, 0.0], 'midBody17': [90.0, 0.0, 0.0], 'midBody18': [90.0, 0.0, 0.0]}
# }
# fk_midBody_dict = { 
#     "fk_pos":{
#         'ctrl_fk_midBody0': [0.0, 0.0, -20.0], 
#         'ctrl_fk_midBody1': [0.0, 0.0, -16.0], 
#         'ctrl_fk_midBody2': [0.0, 0.0, -12.0], 
#         'ctrl_fk_midBody3': [0.0, 0.0, -8.0], 
#         'ctrl_fk_midBody4': [0.0, 0.0, -4.0], 
#         'ctrl_fk_midBody5': [0.0, 0.0, 0.0], 
#         'ctrl_fk_midBody6': [0.0, 0.0, 4.0], 
#         'ctrl_fk_midBody7': [0.0, 0.0, 8.0], 
#         'ctrl_fk_midBody8': [0.0, 0.0, 12.0], 
#         'ctrl_fk_midBody9': [0.0, 0.0, 16.0]
#         },
#     "fk_rot":{'ctrl_fk_midBody0': [90.0, 0.0, 0.0], 'ctrl_fk_midBody1': [90.0, 0.0, 0.0], 'ctrl_fk_midBody2': [90.0, 0.0, 0.0], 'ctrl_fk_midBody3': [90.0, 0.0, 0.0], 'ctrl_fk_midBody4': [90.0, 0.0, 0.0], 'ctrl_fk_midBody5': [90.0, 0.0, 0.0], 'ctrl_fk_midBody6': [90.0, 0.0, 0.0], 'ctrl_fk_midBody7': [90.0, 0.0, 0.0], 'ctrl_fk_midBody8': [90.0, 0.0, 0.0], 'ctrl_fk_midBody9': [90.0, 0.0, 0.0]}

# }
# ik_midBody_dict = {
#     "ik_pos":{'ctrl_ik_midBody_bottom': [0.0, 0.0, -20.0], 'ctrl_ik_midBody_mid': [0.0, 0.0, -2.0], 'ctrl_ik_midBody_top': [0.0, 0.0, 16.0]},
#     "ik_rot":{'ctrl_ik_midBody_bottom': [90.0, 0.0, 0.0], 'ctrl_ik_midBody_mid': [90.0, 0.0, 0.0], 'ctrl_ik_midBody_top': [90.0, 0.0, 0.0]}

# }
# SpineSystem("midBody", "grp_rootOutputs", skel_midBody_dict, fk_midBody_dict, ik_midBody_dict)
'''