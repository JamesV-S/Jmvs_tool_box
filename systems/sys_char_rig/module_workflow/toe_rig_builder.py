
'''
import importlib
from Jmvs_tool_box.systems.sys_char_rig.module_workflow import temp_mian_tyrannosaurusss_builder

importlib.reload(temp_mian_tyrannosaurusss_builder)
#-----------------------------

# THIS SCRIPT
import importlib
from Jmvs_tool_box.systems.sys_char_rig.module_workflow import toe_rig_builder

importlib.reload(toe_rig_builder)

#-----------------------------
jnts = cmds.ls(typ="joint")
for j in jnts:
    cmds.setAttr(f"{j}.radius", 3)
    cmds.setAttr(f"{j}.displayLocalAxis", 1)
'''
# import the two parent classes to inherit from
import importlib
import maya.cmds as cmds

from utils import (
    utils
)

importlib.reload(utils)

class ToeBuilder():
    def __init__(
            self,
            foot_setting_ctrl,
            base_mtx_plg, hook_mtx_plg,
            foot_root_pos, foot_root_rot, 
            skel_pos_dict, skel_rot_dict, 
            pad_pos_dict, pad_rot_dict, 
            mdl_nm, unique_id, side):
        '''
        prerequesits:
            - skel pos & rot dicts {"base_name#":[0.0, 0.0, 0.0], "base_name#":[0.0, 0.0, 0.0],}
            - controls already exist.
                - names are derived from argument passing the fk_ctrl_list.
        Features: 
            - fk setup
            - pad deformers, needs joint positon (joint) (how am i gonna have the controls included)
            - 
        '''
        self.skel_pos_dict = skel_pos_dict
        self.skel_rot_dict = skel_rot_dict
        self.pad_pos_dict = pad_pos_dict
        self.pad_rot_dict = pad_rot_dict
        self.mdl_nm, self.unique_id, self.side = mdl_nm, unique_id, side
        self.XYZ = ["X", "Y", "Z"]
        
        input_grp, output_grp = self.cr_input_output_groups()
        self.wire_input_grp(input_grp, base_mtx_plg, hook_mtx_plg)

        #------
        # foot setting control setup
            # positon control
            # add attributes to control.
        if not cmds.objExists(f"MM_{foot_setting_ctrl}"):
            self.wire_foot_setting_ctrl(input_grp, foot_setting_ctrl, foot_root_pos, foot_root_rot)
            self.lock_ctrl_attributes(foot_setting_ctrl)
        self.cr_foot_setting_ctrl_attr(foot_setting_ctrl)

        #------
        # fk prep
        # get control lists 
            # fk toe control list
        toe_fk_ctrl_list = self.get_fk_control_ls(self.skel_pos_dict.keys())
            # fk pad control list
        pad_fk_ctrl_list = self.get_fk_control_ls(self.pad_pos_dict.keys())
        
        # toe fk jnt list
        jnt_fk_toe_ls = self.cr_typ_jnt_chain("fk", self.skel_pos_dict, self.skel_rot_dict)
        # cr pad jnts & parent to toe jnts based off name match
        jnt_fk_pad_ls = self.cr_pad_jnts("fk", self.pad_pos_dict, self.pad_rot_dict, jnt_fk_toe_ls)
        
        #------
        # fk setup
            # toes
        grp_toe_fk_ctrl_list = self.ofs_grp_to_zero(toe_fk_ctrl_list)
        fk_ctrl_grp = self.group_ctrls(grp_toe_fk_ctrl_list, "fk")

        mm_toe_fk_root = self.wire_toe_fk_ctrl_setup(input_grp, grp_toe_fk_ctrl_list, toe_fk_ctrl_list, self.skel_pos_dict, self.skel_rot_dict)
        self.wire_fk_logic_joints(toe_fk_ctrl_list, jnt_fk_toe_ls, mm_toe_fk_root)
            # pads
        grp_pad_fk_ctrl_list = self.ofs_grp_to_zero(pad_fk_ctrl_list)
        self.group_ctrls(grp_pad_fk_ctrl_list, "fk")
        self.wire_fk_pad_ctrl(toe_fk_ctrl_list, grp_pad_fk_ctrl_list, self.skel_pos_dict, self.skel_rot_dict, self.pad_pos_dict, self.pad_rot_dict,)
        self.wire_fk_pad_joints(pad_fk_ctrl_list, jnt_fk_pad_ls)
        
        #------
        # SDK setup
        curl_driver_atr = f"{foot_setting_ctrl}.Toe_Curl_{self.unique_id}_{self.side}"
        curl_value_pairs=[(-100, -100), (0, 0), (100, 100)]
        for x in range(len(grp_toe_fk_ctrl_list)):
            curl_driven_atr = f"{grp_toe_fk_ctrl_list[x]}.rz"
            self.create_sdk(curl_driver_atr, curl_driven_atr, curl_value_pairs)

        squash_driver_atr = f"{foot_setting_ctrl}.Toe_Squash_{self.unique_id}_{self.side}"
        squash_ty_vp =[(0, 0), (5, 2.5), (10, 5)]
        squash_sz_vp =[(0, 1), (5, 1.25), (10, 1.5)]
        for x in range(len(grp_pad_fk_ctrl_list)):
            squash_driven_atr_ty = f"{grp_pad_fk_ctrl_list[x]}.ty"
            squash_driven_atr_sz = f"{grp_pad_fk_ctrl_list[x]}.sz"
            self.create_sdk(squash_driver_atr, squash_driven_atr_ty, squash_ty_vp)
            self.create_sdk(squash_driver_atr, squash_driven_atr_sz, squash_sz_vp)
        
    def cr_input_output_groups(self, output_global=False):
        '''
        # Description:
            Creates the 'Input' & 'Output' groups for this module. These are 
            specialised nodes that store custom matrix data to allow the module 
            to be driven(Input) or be the driver(Output) for other modules, etc. 
        # Attributes:
            output_global (boolean): If True, add globalScale attr to the output group.
        # Returns:
            input_grp (string): Group for input data for this module.
            outputs_grp (string): Group for Ouput data for this module.
        '''
        # create input & output groups
        input_grp = f"grp_Inputs_{self.mdl_nm}_{self.unique_id}_{self.side}"
        outputs_grp = f"grp_Outputs_{self.mdl_nm}_{self.unique_id}_{self.side}"
        utils.cr_node_if_not_exists(0, "transform", input_grp)
        utils.cr_node_if_not_exists(0, "transform", outputs_grp)
        
        # Input grp
        # utils.add_float_attrib(input_grp, [self.global_scale_attr], [0.01, 999], True) 
        # cmds.setAttr(f"{input_grp}.{self.global_scale_attr}", 1, keyable=0, channelBox=0)
        utils.add_attr_if_not_exists(input_grp, "base_mtx", 'matrix', False)
        utils.add_attr_if_not_exists(input_grp, "hook_mtx", 'matrix', False)
        
        if output_global:
            # utils.add_float_attrib(outputs_grp, [self.global_scale_attr], [0.01, 999], True)
            try:
                print(f"True `output_global`")

                # cmds.setAttr(f"{outputs_grp}.{self.global_scale_attr}", 1, keyable=0, channelBox=0)
            except RuntimeError as e: 
                print(e)

        return input_grp, outputs_grp
    
    
    def wire_foot_setting_ctrl(self, inputs_grp, ctrl, pos, rot):
        ''' position the foot_setting_ctrl'''
        mm = f"MM_{foot_setting_ctrl}"
        utils.cr_node_if_not_exists(1, 'multMatrix', mm)
        utils.set_transformation_matrix(pos, rot, f"{mm}{utils.Plg.mtx_ins[0]}")
        utils.connect_attr(f"{inputs_grp}.hook_mtx", f"{mm}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{mm}{utils.Plg.mtx_sum_plg}", f"{ctrl}{utils.Plg.opm_plg}")
    
    
    def lock_ctrl_attributes(self, ctrl):
        '''
        # Description:
            Lock an assortment of ctrls of the module to make it animator friendly.
            (For testing of controls toggle this function).
        # Arguments:
            fk_ctrl_list (list): Contains fk control names. (5)
            fk_ctrl_list (list): Contains ik control names.
        # Returns: N/A
        '''
        for axis in ['x', 'y', 'z']:
            cmds.setAttr(f"{ctrl}.t{axis}", lock=1, ch=0, k=0)
            cmds.setAttr(f"{ctrl}.r{axis}", lock=1, ch=0, k=0)
            cmds.setAttr(f"{ctrl}.s{axis}", lock=1, ch=0, k=0)  

        # for fk, ik in zip(fk_ctrl_list, ik_ctrl_list):
        #     cmds.setAttr(f"{fk}.visibility", lock=1, ch=0, k=0)
        #     cmds.setAttr(f"{ik}.visibility", lock=1, ch=0, k=0)
        cmds.setAttr(f"{ctrl}.visibility", lock=1, ch=0, k=0)


    def cr_foot_setting_ctrl_attr(self, ctrl):
        atr_curl = f"Toe_Curl_{self.unique_id}_{self.side}"
        atr_squash = f"Toe_Squash_{self.unique_id}_{self.side}"

        foot_atr_list = [
            atr_curl, atr_squash
            ]
        print(f"- foot_atr_list = {foot_atr_list}")
        utils.add_float_attrib(
            ctrl,
            [ f"{atr_curl}"], 
            [0.0, 1.0], False)
        utils.add_float_attrib(ctrl, [f"{atr_squash}"], [0.0, 10.0], True)
        
        return foot_atr_list


    def wire_input_grp(self, input_grp, base_mtx_plg, hook_mtx_plg):
        '''
        # Description:
            Connect the 'global_scale', 'base_mtx', and 'hook_mtx' plugs (retrieved 
            from 'external_plg_dict' and plug into the corresponding plug in the 
            Input grp!)
        # Attributes:
            input_grp (string): Outputgrpup for this module.
            global_scale_plg (plug): External glabal scale attr plug
            base_mtx_plg (plug): External base matrix attr plug
            hook_mtx_plg (plug): External hook matrix attr plug
        # Returns:N/A
        '''
        # connect the base plug
        utils.connect_attr(base_mtx_plg, f"{input_grp}.base_mtx")
        # connect the hook plug
        utils.connect_attr(hook_mtx_plg, f"{input_grp}.hook_mtx")


    def get_fk_control_ls(self, keys):
        ctrl_ls = []
        for obj in keys:
            ctrl = f"ctrl_fk_{self.mdl_nm}_{obj}_{self.unique_id}_{self.side}"
            ctrl_ls.append(ctrl)

        return ctrl_ls


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
    

    def cr_typ_jnt_chain(self, pref, skeleton_pos_dict, skeleton_rot_dict, reverse_direction=False):
        '''
        # Description:
           Creates a basic desired joint chain, naming, position and direction all 
           taken care of. 
        # Attributes:
            pref (string): name of the joint chain type.
            skeleton_pos_dict (dict): key = name of Ext iteration (Ext#), value = positonal data.
            skeleton_rot_dict (dict): key = name of Ext iteration (Ext#), value = rotational data.
            reverse_direction (bool): If True, the joint chain is reversed.
        # Returns:
            jnt_chain_ls (list): The list of joints within the chain.
        '''
        cmds.select(cl=True)
        jnt_chain_ls = []
        # reverse the positon data
        # need to figure out how I need to flip or minus the rotate values (for when they have just 0.0 or a value.)
        # That'll consist of flipping the primary axis & 
        
        for name in skeleton_pos_dict:
            jnt_nm = f"jnt_{pref}_{self.mdl_nm}_{name}_{self.unique_id}_{self.side}"
            jnt_chain_ls.append(jnt_nm)
            cmds.joint(n=jnt_nm)
            if reverse_direction:
                # reverse the rot pos dict 
                print(f"skeleton_pos_dict = {skeleton_pos_dict}")
                print(f"skeleton_rot_dict = {skeleton_rot_dict}")
                rev_skel_pos = utils.reverse_values_dict(skeleton_pos_dict)
                rev_skel_rot = utils.reverse_values_dict(skeleton_rot_dict)
                print(f"rev_skel_pos = {rev_skel_pos}")
                print(f"rev_skel_rot = {rev_skel_rot}")
                cmds.xform(jnt_nm, translation=rev_skel_pos[name], worldSpace=True)
                cmds.xform(jnt_nm, rotation=rev_skel_rot[name], worldSpace=True)
            else:
                cmds.xform(jnt_nm, translation=skeleton_pos_dict[name], worldSpace=True)
                cmds.xform(jnt_nm, rotation=skeleton_rot_dict[name], worldSpace=True)
            cmds.makeIdentity(jnt_nm, a=1, t=0, r=1, s=0, n=0, pn=1)
        utils.clean_opm(jnt_chain_ls[0])
        print(f"jnt_chain_ls = {jnt_chain_ls}")
        return jnt_chain_ls

    
    def cr_pad_jnts(self, pref, pad_pos_dict, pad_rot_dict, jnt_fk_toe_ls):
        '''
        # Description:
           Create joints seperated in the corrrect positions. parent the joint to the toe 
           fk joint with a corresponding jnt name.
        # Attributes:
            pref (string): name of the joint chain type.
            pad_pos_dict (dict): key = name of Ext iteration (Ext#), value = positonal data.
            pad_rot_dict (dict): key = name of Ext iteration (Ext#), value = rotational data.
            jnt_fk_toe_ls (list): Toe joint list.
        # Returns:
            jnt_ls (list): The list of pad joints.
        '''
        # cr jnts
        jnt_ls = []
        pad_name_ls = []
        for name in pad_pos_dict:
            pad_name_ls.append(name)
            jnt_nm = f"jnt_{pref}_{self.mdl_nm}_{name}_{self.unique_id}_{self.side}"
            jnt_ls.append(jnt_nm)
            cmds.joint(n=jnt_nm)
            cmds.xform(jnt_nm, translation=pad_pos_dict[name], worldSpace=True)
            cmds.xform(jnt_nm, rotation=pad_rot_dict[name], worldSpace=True)
            cmds.makeIdentity(jnt_nm, a=1, t=0, r=1, s=0, n=0, pn=1)
            cmds.select(cl=1)
        print(f"jnt_fk_toe_ls = {jnt_fk_toe_ls}")
        print(f"pad_name_ls = {pad_name_ls}")
        for toe, jnt_pad in zip(jnt_fk_toe_ls, jnt_ls):
            for pad in pad_name_ls:
                toe_part = toe.split('_')[-3]
                if pad[-1] == toe_part[-1]:
                    cmds.parent(jnt_pad, toe)
                print(f"pad = {pad}")
                print(f"jnt_pad = {jnt_pad}")
                # print(f"toe = {toe}")
                print(f"toe_part = {toe_part}")
        cmds.select(cl=1)

        return jnt_ls
      

    def wire_toe_fk_ctrl_setup(self, inputs_grp, grp_fk_ctrl_list, fk_ctrl_list, fk_pos_dict, fk_rot_dict):
        '''
        # Description:
            FK logic setup:
                - need corresponding fk joints (jnt_logic or jnt_fk -> depends on the module setup)
                - base & limbRt to multMatrix each > blendMatrix.
                - setup the fk controls with MM method. 
                - connect ctrl rotates to fk joints rotates (direct or constraint -> depends on the module setup)
                Temporary locators are used to position the fk control's with 
                rotation data, using the locators local space matrix as an offset.
                After the data is passed to the control correctly, temp locs r deleted.  
        # Attributes:
            input_grp (string): Group for input data for this module.
            fk_ctrl_list (list): Contains 3 fk control names.
            fk_pos_dict (dict): key=Name of fk controls, value=Positional data.
            fk_rot_dict (dict): key=Name of fk controls, value=Rotational data.
        # Returns:
            BM_limb (utility): Limb root ctrl's matrix follow. 
        '''
        
        fk_root_ctrl = grp_fk_ctrl_list[0]
        print(f"fk_root_ctrl = `{fk_root_ctrl}`")
        mm_fk_root = f"MM_{fk_root_ctrl}"
        utils.cr_node_if_not_exists(1, 'multMatrix', mm_fk_root)
        
        # wire to the limbRtBAse -> It's going into the fk 'first parent', so need it's pos(fk 'first parent'). 
        utils.set_transformation_matrix(list(fk_pos_dict.values())[0], list(fk_rot_dict.values())[0], f"{mm_fk_root}{utils.Plg.mtx_ins[0]}")
        utils.connect_attr(f"{inputs_grp}.hook_mtx", f"{mm_fk_root}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{mm_fk_root}{utils.Plg.mtx_sum_plg}", f"{fk_root_ctrl}{utils.Plg.opm_plg}")
        
        # create temp locators
        temp_loc_ls = []
        for (key, pos_val), (key, rot_val) in zip(fk_pos_dict.items(), fk_rot_dict.items()):
            print(f"key = {key}")
            loc_name = key.replace('ctrl_fk_', 'loc_temp_')# "ctrl_fk_bipedArm_'first parent'_0_L"
            temp_loc_ls.append(loc_name)
            cmds.spaceLocator(n=loc_name)
            cmds.xform(loc_name, t=pos_val, ws=1)
            cmds.xform(loc_name, rotation=rot_val, ws=1)
        try:
            for i in range(len(temp_loc_ls)):
                cmds.parent(temp_loc_ls[i+1],temp_loc_ls[i])
        except IndexError:
            pass
        print(f"temp_loc_ls = {temp_loc_ls}")
        
        # iterate through the fk ctrl list with rule: 
            # > Skip first iteration (first fk ctrl is done above with limbRt ctrl)
            # > fk_source_ctrl[x-1], fk_target_ctrl[x], fk_local_object[x]
        for x in range(1, len(fk_ctrl_list)):
            utils.matrix_control_FowardKinematic_setup(fk_ctrl_list[x-1], grp_fk_ctrl_list[x], temp_loc_ls[x])
        cmds.select(cl=1)
        # # delete the locators
        # for tmp_loc in temp_loc_ls:
            # print(f"tmp_loc = {tmp_loc}")
        cmds.delete(temp_loc_ls[0])

        return mm_fk_root


    def wire_fk_logic_joints(self, fk_ctrl_list, fk_jnt_chain, mm_fk_root):
        '''
        # Description:
            bm_limbRt output drives fk_ctrl_list[0] translate
            Drive fk_jnt_chain.rotations with fk_ctrl_list.rotations.
        # Attributes:
            fk_ctrl_list (list): fk control names.
            fk_jnt_chain (list): fk joint names.
            bm_limbRt (utility) BlendMatrix node drives the positional transform for fk joints
        # Returns:
        '''
        #  bm_limbRt.outMatrix > fk_jnt_chain[0].opm
        # utils.connect_attr(f"{mm_fk_root}{utils.Plg.mtx_sum_plg}", f"{fk_jnt_chain[0]}{utils.Plg.opm_plg}")

        # direct connection of ctrl to joint
        # for x, i in ((x, i) for x in range(len(fk_ctrl_list)) for i in range(len(self.XYZ))):

        for x in range(0, len(fk_ctrl_list)):
            pcon_name = f"Pcon_{fk_ctrl_list[x]}"
            cmds.parentConstraint(fk_ctrl_list[x], fk_jnt_chain[x], n=pcon_name, mo=1)
            # utils.connect_attr(f"{fk_ctrl_list[x]}.rotate{self.XYZ[i]}", f"{fk_jnt_chain[x]}.rotate{self.XYZ[i]}")
        

    def ofs_grp_to_zero(self, control_list):
        # selection = cmds.ls(sl=1, type="transform")
        # cmds.select(selection, hi=1)
        # full_sel = cmds.ls(sl=1, type="transform")
        # print(full_sel)
        grp_ctrl_list = []
        for i in range(len(control_list)):
            name = f"grp_ofs_{control_list[i]}"
            offset_grp = cmds.group(n=name, em=1)
            grp_ctrl_list.append(name)
            cmds.matchTransform(offset_grp, control_list[i])
            cmds.parent(control_list[i], offset_grp)

        return grp_ctrl_list
    

    def cr_ofs_grp(self, control_list):
        ''' create the ofs groups, and position them based of control list. DONT parent controls yet.  '''
        grp_ctrl_list = []
        for i in range(len(control_list)):
            name = f"grp_ofs_{control_list[i]}"
            offset_grp = cmds.group(n=name, em=1)
            grp_ctrl_list.append(name)
            # cmds.matchTransform(offset_grp, control_list[i])
            # cmds.parent(control_list[i], offset_grp)

        return grp_ctrl_list


    def wire_fk_pad_ctrl(self, toe_fk_ctrl_list, pad_fk_ctrl_list, toe_pos_dict, toe_rot_dict, pad_pos_dict, pad_rot_dict):
        ''' Using matrix fk method, the toe controls drive the corresposning pad controls. '''
        # for toe, pad, in zip(toe_fk_ctrl_list, pad_fk_ctrl_list):
        pad_mm_list = [f"MM_{name}" for name in pad_fk_ctrl_list] # f"MM_{name}" for name in toe_fk_ctrl_list
        for mm_name in pad_mm_list:
            utils.cr_node_if_not_exists(1, 'multMatrix', mm_name)
        
        utils.wire_TOE_ofs_mtxIn0_1_to_1(
            [toe_pos_dict, toe_rot_dict], 
            [pad_pos_dict, pad_rot_dict],
            [0], [0],
            pad_mm_list[0])
        utils.connect_attr(f"{toe_fk_ctrl_list[0]}{utils.Plg.wld_mtx_plg}", f"{pad_mm_list[0]}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{pad_mm_list[0]}{utils.Plg.mtx_sum_plg}", f"{pad_fk_ctrl_list[0]}{utils.Plg.opm_plg}")
        
        utils.wire_ofs_mtxIn0_1_to_1(
            [toe_pos_dict, toe_rot_dict], 
            [pad_pos_dict, pad_rot_dict],
            [1], [1],
            pad_mm_list[1])
        utils.connect_attr(f"{toe_fk_ctrl_list[1]}{utils.Plg.wld_mtx_plg}", f"{pad_mm_list[1]}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{pad_mm_list[1]}{utils.Plg.mtx_sum_plg}", f"{pad_fk_ctrl_list[1]}{utils.Plg.opm_plg}")
        

    def wire_fk_pad_joints(self, fk_ctrl_list, fk_jnt_chain):
        '''
        # Description:
            controls drive joints with constraints.
        # Attributes:
            fk_ctrl_list (list): fk control names.
            fk_jnt_chain (list): fk joint names.
            bm_limbRt (utility) BlendMatrix node drives the positional transform for fk joints
        # Returns:
        '''
        print(f" * fk_ctrl_list = {fk_ctrl_list}")
        print(f" * fk_jnt_chain = {fk_jnt_chain}")
        # contraint from control to joint
        for x in range(len(fk_ctrl_list)):
            pcon_name = f"Pcon_{fk_ctrl_list[x]}"
            cmds.parentConstraint(fk_ctrl_list[x], fk_jnt_chain[x], n=pcon_name, mo=1)
            cmds.scaleConstraint(fk_ctrl_list[x], fk_jnt_chain[x], n=pcon_name, mo=1)


    def create_sdk(self, driver_attr, driven_attr, value_pairs, tangent_type="auto", infinity_type="constant"):
        """
        Create Set Driven Keys between two attributes without using MEL.
        
        Args:
            driver_attr (str): Full attribute path (e.g. "ctrl.translateX")
            driven_attr (str): Full attribute path (e.g. "group.rotateY")
            value_pairs (list): List of (driver_value, driven_value) tuples
            tangent_type (str): "auto", "linear", "fast", "slow", "flat", "step", "fixed"
            infinity_type (str): "constant", "linear", "cycle", "cycleRelative", "oscillate"
        
        Returns:
            str: Name of the created animCurve node
        """
        if not cmds.objExists(driver_attr):
            raise ValueError(f"Driver attribute does not exist: {driver_attr}")
        if not cmds.objExists(driven_attr):
            raise ValueError(f"Driven attribute does not exist: {driven_attr}")
        
        # Create SDK for each value pair
        for driver_val, driven_val in value_pairs:
            cmds.setDrivenKeyframe(
                driven_attr,
                currentDriver=driver_attr,
                driverValue=driver_val,
                value=driven_val,
                inTangentType=tangent_type,
                outTangentType=tangent_type
            )
        
        # Set infinity type
        cmds.setInfinity(driven_attr, pri=infinity_type, poi=infinity_type)
        
        # Get the created animCurve node
        connections = cmds.listConnections(driven_attr, type="animCurve", destination=False, source=True)
        anim_curve = connections[0] if connections else None
        
        return anim_curve


# foot root ---------------------------------------------------------------------------------------------------
foot_setting_ctrl = "ctrl_foot_settings_L"
ext_base_plg = 'grp_Outputs_root_0_M.mtx_root_ctrl_fk_centre'
ext_hook_plg = 'grp_Outputs_quadLeg_0_L.mtx_quadLeg_jnt_skn_ankle'
foot_root_L_pos_list = [60.374118804931655, 39.7957763671875, -47.196548461914055]
foot_root_L_rot_list = [0.0, 5.8849799203652555, 0.0]

# foot toes in
foot_toe_0_L_skel_pos = {'toe0': [38.52313937538893, 23.179796247152833, -26.12790963669226], 'toe1': [28.90996344459881, 17.947179269556457, -4.076108075261505], 'toe2': [19.56852714730405, 17.2049007945554, 16.192893609089705]}
foot_toe_0_L_skel_rot = {'toe0': [-25.992257492061636, -116.39668384115679, 28.560212745631713], 'toe1': [-4.125349164743576, -114.81231517092596, 4.543225413242678], 'toe2': [175.87465083525663, -65.18768482907404, -175.45677458675732]}
foot_pad_0_L_skel_pos = {'pad0': [39.05141499018504, 10.570109358677179, -27.63910764873875], 'pad1': [20.915877304088923, 5.394577169888443, 13.269419988101548]}
foot_pad_0_L_skel_rot = {'pad0': [0.0, -113.25911975198025, 0.0], 'pad1': [0.0, -114.81267635481203, 0.0]}
ToeBuilder(
    foot_setting_ctrl,
    ext_base_plg, ext_hook_plg,
    foot_root_L_pos_list, foot_root_L_rot_list,
    foot_toe_0_L_skel_pos, foot_toe_0_L_skel_rot,
    foot_pad_0_L_skel_pos, foot_pad_0_L_skel_rot,
    "foot", "0", "L")

# foot toes mid
foot_toe_1_L_skel_pos = {'toe0': [64.20642783821552, 21.547578252255043, -16.32568133128053], 'toe1': [67.00249855107212, 18.619296715462912, 5.638887043633819], 'toe2': [70.37039207167653, 17.65831871120247, 35.420796775264094]}
foot_toe_1_L_skel_rot = {'toe0': [42.517378195328334, -80.13504393193197, -42.94277714478456], 'toe1': [3.9690956665501105, -83.53252639740009, -3.9944349013386895], 'toe2': [15.821788445946044, -83.29290072690294, -15.925304205287562]}
foot_pad_1_L_skel_pos = {'pad0': [63.64051953422487, 6.586856391784469, -24.090721385735307], 'pad1': [69.50943413660316, 4.621891422566739, 27.807441023897102]}
foot_pad_1_L_skel_rot = {'pad0': [3.9690956665501105, -83.53252639740009, -3.9944349013386895], 'pad1': [3.9690956665501105, -83.53252639740009, -3.9944349013386895]}
ToeBuilder(
    foot_setting_ctrl,
    ext_base_plg, ext_hook_plg,
    foot_root_L_pos_list, foot_root_L_rot_list,
    foot_toe_1_L_skel_pos, foot_toe_1_L_skel_rot,
    foot_pad_1_L_skel_pos, foot_pad_1_L_skel_rot,
    "foot", "1", "L")

# foot toes out
foot_toe_2_L_skel_pos = {'toe0': [88.28070315770096, 21.639157934872134, -30.09626053287009], 'toe1': [106.93765224055373, 19.050689236764498, -5.058754555427306], 'toe2': [119.95313713649034, 18.791900327935963, 11.431283233429738]}
foot_toe_2_L_skel_rot = {'toe0': [7.377761952832005, -52.95074514068025, -9.215094165216458], 'toe1': [-2.872682158524188, -51.65926313510713, 3.660651021957857], 'toe2': [0.8940926366595577, -51.71067903998226, -1.1390707971041898]}
foot_pad_2_L_skel_pos = {'pad0': [87.53832115746498, 8.82211984209089, -31.092532414511144], 'pad1': [116.02557126221843, 4.3525210127932645, 7.137118235833568]}
foot_pad_2_L_skel_rot = {'pad0': [0.0, -53.30795242923451, 0.0], 'pad1': [0.0, -53.30795242923451, 0.0]}
ToeBuilder(
    foot_setting_ctrl,
    ext_base_plg, ext_hook_plg,
    foot_root_L_pos_list, foot_root_L_rot_list,
    foot_toe_2_L_skel_pos, foot_toe_2_L_skel_rot,
    foot_pad_2_L_skel_pos, foot_pad_2_L_skel_rot,
    "foot", "2", "L")
