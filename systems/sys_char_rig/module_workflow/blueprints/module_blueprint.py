
import importlib
import maya.cmds as cmds

''' in 'main.py' set the directory of the four folders for this workflow '''
from systems.sys_char_rig.module_workflow.data_managers import module_data_manager

from utils import (
    utils
)

importlib.reload(module_data_manager)
importlib.reload(utils)

class ModuleBP:
    def __init__(self, data_manager):
        # print(f"ModuleBP -> data_manager = {data_manager}")
        
        # self.dm = module_data_manager.ModuleDataManager("ModuleBP", data_manager) # data_manager
        self.dm: module_data_manager.ModuleDataManager = data_manager
        # print(f"ModuleBP -> data_manager = {data_manager}")


    # Phase 1 - foundation
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
        input_grp = f"grp_Inputs_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        outputs_grp = f"grp_Outputs_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        utils.cr_node_if_not_exists(0, "transform", input_grp)
        utils.cr_node_if_not_exists(0, "transform", outputs_grp)
        
        # Input grp
        utils.add_float_attrib(input_grp, [self.dm.global_scale_attr], [0.01, 999], True) 
        cmds.setAttr(f"{input_grp}.{self.dm.global_scale_attr}", 1, keyable=0, channelBox=0)
        utils.add_attr_if_not_exists(input_grp, "base_mtx", 'matrix', False)
        utils.add_attr_if_not_exists(input_grp, "hook_mtx", 'matrix', False)
        
        if output_global:
            utils.add_float_attrib(outputs_grp, [self.dm.global_scale_attr], [0.01, 999], True)
            cmds.setAttr(f"{outputs_grp}.{self.dm.global_scale_attr}", 1, keyable=0, channelBox=0)
        
        return input_grp, outputs_grp
    

    def add_outputs_matrix_attr(self, outputs_grp, output_hook_atr_list):
        '''
        # Description:
            Add custom matrix to ouptut group -> this matrix lets other modules follow.
        # Attributes:
            outputs_grp (string): Outputgrpup for this module. 
            output_hook_atr_list (list): List of names for matrix attr.
        # Returns: N/A
        '''
        for mtx_name in output_hook_atr_list:
            utils.add_attr_if_not_exists(outputs_grp, 
                                         f"mtx_{self.dm.mdl_nm}_{mtx_name}", 
                                        'matrix', False)

    # Module setup
    def wire_input_grp(self, input_grp, global_scale_plg, base_mtx_plg, hook_mtx_plg):
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
        # connect the global scale
        utils.connect_attr(global_scale_plg, f"{input_grp}.globalScale")
        # connect the base plug
        utils.connect_attr(base_mtx_plg, f"{input_grp}.base_mtx")
        # connect the hook plug
        utils.connect_attr(hook_mtx_plg, f"{input_grp}.hook_mtx")


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
        module_control_grp = f"grp_ctrls_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        if not cmds.objExists(module_control_grp):
            utils.cr_node_if_not_exists(0, "transform", module_control_grp)

        child_ctrl_grp = f"grp_ctrl_{ctrl_type}_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        utils.cr_node_if_not_exists(0, "transform", child_ctrl_grp)

        for ctrl in ctrl_ls:
            cmds.parent(ctrl, child_ctrl_grp)
        cmds.parent(child_ctrl_grp, module_control_grp)
        cmds.select(cl=1)

        return child_ctrl_grp

    # Phase 2 - Module operations shared by multiple modules but not all
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
            jnt_ls (list): The list of joints within the chain.
        '''
        cmds.select(cl=True)
        jnt_chain_ls = []
        # reverse the positon data
        # need to figure out how I need to flip or minus the rotate values (for when they have just 0.0 or a value.)
        # That'll consist of flipping the primary axis & 
        
        for name in skeleton_pos_dict:
            jnt_nm = f"jnt_{pref}_{self.dm.mdl_nm}_{name}_{self.dm.unique_id}_{self.dm.side}"
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

        return jnt_chain_ls

    
    def logic_jnt_distances(self, skel_num, skel_pos_dict):
        '''
        # Description:
            Need to store the distances of the the limb, (to be used for PINNING! & More).
            Stored in a dictionary with each item being the distance going through the list of skel positions.
            Last item in dict is 'start to end' distance
        # Attributes:
            skel_num (int): number of joints in the module's skeleton.
            skel_pos_dict (dict): key=Name skel pos component, value=Positional data.
        # Returns:
            d_skel_dict (dict): key=Name '*component_*component', value= Int length.
        '''
        # print(f"skel_num = {skel_num}")
        d_skel_dict = {}
        for x in range(skel_num):
            # get distances through the skel pos dict and add to the dictionary. 
            try:
                # print(f"{list(skel_pos_dict.keys())[x]}, {list(skel_pos_dict.keys())[x+1]}")
                d = utils.get_distance(f"skel_jnt_sequence_{x}", list(skel_pos_dict.values())[x], list(skel_pos_dict.values())[x+1])
                d_skel_dict[f"{list(skel_pos_dict.keys())[x]}_{list(skel_pos_dict.keys())[x+1]}"] = d
            except IndexError:
                pass
        # Add start end distance to dictionary -> hip_ankle
        d_start_end = utils.get_distance("start_end", list(skel_pos_dict.values())[0], list(skel_pos_dict.values())[3])
        d_skel_dict[f"{list(skel_pos_dict.keys())[0]}_{list(skel_pos_dict.keys())[3]}"] = d_start_end
        print(d_skel_dict)

        '''{
        'hip_knee': 29.73453085918653, 
        'knee_calf': 29.79762073881076, 
        'calf_ankle': 14.904801745021047, 
        'ankle_ball': 5.432754706587857, 
        'ball_end': 6.2893240637222405, 
        'hip_ankle': 67.50895722456278
        }'''

        return d_skel_dict


    def wire_fk_ctrl_setup(self, inputs_grp, limbRt_ctrl, fk_ctrl_list, fk_pos_dict, fk_rot_dict):
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
        # Add follow attr to fk 'first parent' ctrl.
        follow_attr = f"Follow_{self.dm.mdl_nm}_Rot"
        utils.add_locked_attrib(fk_ctrl_list[0], ["Follows"])
        utils.add_float_attrib(fk_ctrl_list[0], [follow_attr], [0.0, 1.0], True)
        cmds.setAttr(f"{fk_ctrl_list[0]}.{follow_attr}", 1)
        # cr blendMatrix setup to feed to fk ctrl/rigJnt 'first parent'. 
        MM_limbBase = f"MM_{self.dm.mdl_nm}_fklimb_Base_{self.dm.unique_id}_{self.dm.side}"
        MM_limbRtCtrl = f"MM_{self.dm.mdl_nm}_fklimb_rootCtrl_{self.dm.unique_id}_{self.dm.side}"
        BM_limb = f"BM_{self.dm.mdl_nm}__fklimb_blend_{self.dm.unique_id}_{self.dm.side}"
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_limbBase)
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_limbRtCtrl)
        utils.cr_node_if_not_exists(1, 'blendMatrix', BM_limb, 
                                    {"target[0].scaleWeight":0, 
                                     "target[0].shearWeight":0})
        
        # wire to the limbRtBAse -> It's going into the fk 'first parent', so need it's pos(fk 'first parent'). 
        utils.set_transformation_matrix(list(fk_pos_dict.values())[0], list(fk_rot_dict.values())[0], f"{MM_limbBase}{utils.Plg.mtx_ins[0]}")
        utils.connect_attr(f"{inputs_grp}.base_mtx", f"{MM_limbBase}{utils.Plg.mtx_ins[1]}")
            # MM_limbRtCtrl
        utils.set_transformation_matrix([0.0, 0.0, 0.0], list(fk_rot_dict.values())[0], f"{MM_limbRtCtrl}{utils.Plg.mtx_ins[0]}")
        utils.connect_attr(f"{limbRt_ctrl}{utils.Plg.wld_mtx_plg}", f"{MM_limbRtCtrl}{utils.Plg.mtx_ins[1]}")
            # BM_limb
        utils.connect_attr(f"{MM_limbBase}{utils.Plg.mtx_sum_plg}", f"{BM_limb}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{MM_limbRtCtrl}{utils.Plg.mtx_sum_plg}", f"{BM_limb}{utils.Plg.target_mtx[0]}")
        utils.connect_attr(f"{fk_ctrl_list[0]}.{follow_attr}", f"{BM_limb}.target[0].rotateWeight")
        utils.connect_attr(f"{BM_limb}{utils.Plg.out_mtx_plg}", f"{fk_ctrl_list[0]}{utils.Plg.opm_plg}")
        # create temp locators
        temp_loc_ls = []
        for (key, pos_val), (key, rot_val) in zip(fk_pos_dict.items(), fk_rot_dict.items()):
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
        
        # iterate through the fk ctrl list with rule: 
            # > Skip first iteration (first fk ctrl is done above with limbRt ctrl)
            # > fk_source_ctrl[x-1], fk_target_ctrl[x], fk_local_object[x]
        for x in range(1, len(fk_ctrl_list)):
            utils.matrix_control_FowardKinematic_setup(fk_ctrl_list[x-1], fk_ctrl_list[x], temp_loc_ls[x])

        # delete the locators
        cmds.delete(temp_loc_ls[0])
        
        return BM_limb


    def wire_ik_ctrl_end(self, inputs_grp, limbRt_ctrl, ik_ctrl_list):
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
        ik_tgt_nm = ik_ctrl_target.split('_')[-3]

        # Add follow attr to fk shoulder ctrl
        follow_attr = f"Follow_{self.dm.mdl_nm}"
        utils.add_locked_attrib(ik_ctrl_target, ["Follows"])
        utils.add_float_attrib(ik_ctrl_target, [follow_attr], [0.0, 1.0], True)
        cmds.setAttr(f"{ik_ctrl_target}.{follow_attr}", 1)
        # cr blendMatrix seyup to feed to fk ctrl/rigJnt shoulder. 
        MM_ikBase = f"MM_{self.dm.mdl_nm}_{ik_tgt_nm}Ik_limbRtBase_{self.dm.unique_id}_{self.dm.side}"
        MM_iklimbRt = f"MM_{self.dm.mdl_nm}_{ik_tgt_nm}Ik_limbRtCtrl_{self.dm.unique_id}_{self.dm.side}"
        BM_ik = f"BM_{self.dm.mdl_nm}_{ik_tgt_nm}Ik_limbRtBlend_{self.dm.unique_id}_{self.dm.side}"
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_ikBase)
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_iklimbRt)
        utils.cr_node_if_not_exists(1, 'blendMatrix', BM_ik, 
                                    {"target[0].scaleWeight":0, 
                                     "target[0].shearWeight":0})
        
        # MM_Base
        utils.set_transformation_matrix(list(self.dm.ik_pos_dict.values())[-1], list(self.dm.ik_rot_dict.values())[-1], f"{MM_ikBase}{utils.Plg.mtx_ins[0]}")         
        utils.connect_attr(f"{inputs_grp}.base_mtx", f"{MM_ikBase}{utils.Plg.mtx_ins[1]}")        
            # Setting Rotation is involved!
        # MM_iklimbRt
        tgt_local_object = f"temp_loc_{ik_ctrl_target}"
        cmds.spaceLocator(n=tgt_local_object)
        cmds.xform(tgt_local_object, t=self.dm.ik_pos_dict[ik_ctrl_target], ws=1)
        cmds.xform(tgt_local_object, rotation=self.dm.ik_rot_dict[ik_ctrl_target], ws=1)
        cmds.parent(tgt_local_object, limbRt_ctrl)
        get_local_matrix = cmds.getAttr(f"{tgt_local_object}.matrix")

        cmds.setAttr(f"{MM_iklimbRt}{utils.Plg.mtx_ins[0]}", *get_local_matrix, type="matrix")    
        utils.connect_attr(f"{limbRt_ctrl}{utils.Plg.wld_mtx_plg}", f"{MM_iklimbRt}{utils.Plg.mtx_ins[1]}")
        cmds.delete(tgt_local_object)
        
        # BM_ik
        utils.connect_attr(f"{MM_ikBase}{utils.Plg.mtx_sum_plg}", f"{BM_ik}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{MM_iklimbRt}{utils.Plg.mtx_sum_plg}", f"{BM_ik}{utils.Plg.target_mtx[0]}")
        utils.connect_attr(f"{ik_ctrl_target}.{follow_attr}", f"{BM_ik}.target[0].translateWeight")
        utils.connect_attr(f"{ik_ctrl_target}.{follow_attr}", f"{BM_ik}.target[0].rotateWeight")
        utils.connect_attr(f"{BM_ik}{utils.Plg.out_mtx_plg}", f"{ik_ctrl_target}{utils.Plg.opm_plg}")


    def wire_ik_ctrl_pv(self, inputs_grp, target_index, ik_ctrl_list, ctrl_external_fol):
        '''
        # Description:
            Positions & wires the follow swapping of the pv ctrl too
        # Attributes:
            inputs_grp (string): Group for input data for this module.
            ik_ctrl_list (list): Contains 4 ik control names.
            ctrl_external_fol (string): Name of Ext modules top ik control.
        # Returns: N/A 
        '''
        #establish the target control:
        ik_ctrl_target = ik_ctrl_list[target_index]
        ik_tgt_nm = ik_ctrl_target.split('_')[-3]
        print(f"pv ik_tgt_nm = `{ik_tgt_nm}`")

        ext_fol_split = ctrl_external_fol.split('_')[3:-2]
        ext_fol_nm = "".join(ext_fol_split)
        print(f"pv ik_tgt_nm = `{ext_fol_nm}`")
        
        # Add follow attr to fk shoulder ctrl
        ext_fol_atr = f"Follow_{ext_fol_nm}"
        end_fol_atr = "Follow_End_ik"

        utils.add_locked_attrib(ik_ctrl_target, ["Follows"])
        utils.add_float_attrib(ik_ctrl_target, [ext_fol_atr], [0.0, 1.0], True)
        utils.add_float_attrib(ik_ctrl_target, [end_fol_atr], [0.0, 1.0], True)
        # cr blendMatrix seyup to feed to fk ctrl/rigJnt shoulder. 
        MM_pvBase = f"MM_ikPv_{self.dm.mdl_nm}_base_{self.dm.unique_id}_{self.dm.side}"
        MM_pvExterernal = f"MM_ikPv_{self.dm.mdl_nm}_{ext_fol_nm}Hook_{self.dm.unique_id}_{self.dm.side}"
        MM_pvEndIk = f"MM_ikPv_{self.dm.mdl_nm}_EndIkCtrl_{self.dm.unique_id}_{self.dm.side}"
        BM_pv = f"BM_ikPv_{self.dm.mdl_nm}_blend_{self.dm.unique_id}_{self.dm.side}"
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_pvBase)
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_pvExterernal)
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_pvEndIk)
        utils.cr_node_if_not_exists(1, 'blendMatrix', BM_pv, {
            "target[0].scaleWeight":0, 
            "target[0].shearWeight":0})
        # MM_pvBase
        utils.set_transformation_matrix(list(self.dm.ik_pos_dict.values())[target_index], list(self.dm.ik_rot_dict.values())[target_index], f"{MM_pvBase}{utils.Plg.mtx_ins[0]}")         
        utils.connect_attr(f"{inputs_grp}.base_mtx", f"{MM_pvBase}{utils.Plg.mtx_ins[1]}")
        
        # MM_pvExterernal
        pvExt_local_object = f"temp_loc_Ext{ik_ctrl_target}"
        cmds.spaceLocator(n=pvExt_local_object)
        cmds.xform(pvExt_local_object, t=self.dm.ik_pos_dict[ik_ctrl_target], ws=1)
        cmds.xform(pvExt_local_object, rotation=self.dm.ik_rot_dict[ik_ctrl_target], ws=1)
        cmds.parent(pvExt_local_object, ctrl_external_fol)
        get_Ext_local_matrix = cmds.getAttr(f"{pvExt_local_object}{utils.Plg.wld_mtx_plg}")
        cmds.setAttr(f"{MM_pvExterernal}{utils.Plg.mtx_ins[0]}", *get_Ext_local_matrix, type="matrix") 
        utils.connect_attr(f"{inputs_grp}.hook_mtx", f"{MM_pvExterernal}{utils.Plg.mtx_ins[1]}")
        cmds.delete(pvExt_local_object)
        
        # MM_pvEndIk
        pvEnd_local_object = f"temp_loc_pvEnd{ik_ctrl_target}"
        cmds.spaceLocator(n=pvEnd_local_object)
        cmds.xform(pvEnd_local_object, t=self.dm.ik_pos_dict[ik_ctrl_target], ws=1)
        cmds.xform(pvEnd_local_object, rotation=self.dm.ik_rot_dict[ik_ctrl_target], ws=1)
        cmds.parent(pvEnd_local_object, ik_ctrl_list[-1])
        get_End_local_matrix = cmds.getAttr(f"{pvEnd_local_object}.matrix")
        cmds.setAttr(f"{MM_pvEndIk}{utils.Plg.mtx_ins[0]}", *get_End_local_matrix, type="matrix")    
        utils.connect_attr(f"{ik_ctrl_list[-1]}{utils.Plg.wld_mtx_plg}", f"{MM_pvEndIk}{utils.Plg.mtx_ins[1]}")
        cmds.delete(pvEnd_local_object)

        # BM_pv
        utils.connect_attr(f"{MM_pvBase}{utils.Plg.mtx_sum_plg}", f"{BM_pv}{utils.Plg.inp_mtx_plg}")
        utils.connect_attr(f"{MM_pvExterernal}{utils.Plg.mtx_sum_plg}", f"{BM_pv}{utils.Plg.target_mtx[0]}")
        utils.connect_attr(f"{MM_pvEndIk}{utils.Plg.mtx_sum_plg}", f"{BM_pv}{utils.Plg.target_mtx[1]}")
            # space swap atribs
        utils.connect_attr(f"{ik_ctrl_target}.{ext_fol_atr}", f"{BM_pv}.target[0].translateWeight")
        utils.connect_attr(f"{ik_ctrl_target}.{ext_fol_atr}", f"{BM_pv}.target[0].rotateWeight")
        utils.connect_attr(f"{ik_ctrl_target}.{end_fol_atr}", f"{BM_pv}.target[1].translateWeight")
        utils.connect_attr(f"{ik_ctrl_target}.{end_fol_atr}", f"{BM_pv}.target[1].rotateWeight")
            # output plug
        utils.connect_attr(f"{BM_pv}{utils.Plg.out_mtx_plg}", f"{ik_ctrl_target}{utils.Plg.opm_plg}")


    def wire_pv_reference_curve(self, pv_ctrl, pv_jnt, ik_ctrl_grp):
        '''
        # Description:
            Create and wire a reference curve to from the jnt_elbow to the ctrl_elbow 
        # Attributes:
        # Returns: N/A
        '''
        # build control
        ref_curve = f"crv_ik_{self.dm.mdl_nm}_ref_{self.dm.unique_id}_{self.dm.side}"
        cmds.curve(n=ref_curve, d=1, 
                   p=[(0, 0, 0), (0, 0, 3)], 
                   k=[0, 1])
        cmds.parent(ref_curve, ik_ctrl_grp)
        cmds.setAttr(f"{ref_curve}{utils.Plg.ovrride_plg}", 1)
        cmds.setAttr(f"{ref_curve}{utils.Plg.dispTyp_plg}", 2)
        
        ref_curve_shape = cmds.listRelatives(ref_curve, s=1)[0]

        # cr util nodes
        pmm_ctrl = f"PMM_Crv0_{self.dm.mdl_nm}_{pv_ctrl}_{self.dm.unique_id}_{self.dm.side}"
        pmm_jnt = f"PMM_Crv1_{self.dm.mdl_nm}_{pv_jnt}_{self.dm.unique_id}_{self.dm.side}"
        utils.cr_node_if_not_exists(1, 'pointMatrixMult', pmm_ctrl)
        utils.cr_node_if_not_exists(1, 'pointMatrixMult', pmm_jnt)
        
        utils.connect_attr(f"{pv_ctrl}{utils.Plg.wld_mtx_plg}", f"{pmm_ctrl}{utils.Plg.inMtx_plg}")
        utils.connect_attr(f"{pv_jnt}{utils.Plg.wld_mtx_plg}", f"{pmm_jnt}{utils.Plg.inMtx_plg}")
        utils.connect_attr(f"{pmm_ctrl}{utils.Plg.output_plg}", f"{ref_curve_shape}.controlPoints[0]")
        utils.connect_attr(f"{pmm_jnt}{utils.Plg.output_plg}", f"{ref_curve_shape}.controlPoints[1]")


    def wire_parent_skn_twist_joint_matrix(self, upp_jnt_chain, low_jnt_chain, limbRt_ctrl, logic_jnt_list, skel_pos_dict, skel_rot_dict):
        '''
        # Description:
            The parent of each joint chain (Upper/Lower) has driven OPM.
            - Upper prnt driven by 'arm root control' 
            - lower prnt driven by 'jnt logic elbow' 
        # Arguments:
            
        # Returns: N/A
        '''
        jnt_skn_upp_parent = upp_jnt_chain[0]
        jnt_skn_low_parent = low_jnt_chain[0]
        mm_skn_upp_parent = f"mm_{jnt_skn_upp_parent}"
        mm_skn_low_parent = f"mm_{jnt_skn_low_parent}"
        utils.cr_node_if_not_exists(1, 'multMatrix', mm_skn_upp_parent)
        utils.cr_node_if_not_exists(1, 'multMatrix', mm_skn_low_parent)
        
        utils.clean_opm(jnt_skn_upp_parent)
        utils.clean_opm(jnt_skn_low_parent)

        # wire upper
            # > mm_skn_upp_parent
        utils.set_transformation_matrix(list(skel_pos_dict.values())[0], list(skel_rot_dict.values())[0], f"{mm_skn_upp_parent}{utils.Plg.mtx_ins[0]}")
        utils.connect_attr(f"{limbRt_ctrl}{utils.Plg.wld_mtx_plg}", f"{mm_skn_upp_parent}{utils.Plg.mtx_ins[1]}")
            # > jnt_skn_upp_parent
        utils.connect_attr(f"{mm_skn_upp_parent}{utils.Plg.mtx_sum_plg}", f"{jnt_skn_upp_parent}{utils.Plg.opm_plg}")
        
        # wire lower
            # > mm_skn_low_parent
        utils.set_transformation_matrix(list(skel_pos_dict.values())[1], [0.0, 0.0, 0.0], f"{mm_skn_low_parent}{utils.Plg.mtx_ins[0]}")
        utils.connect_attr(f"{logic_jnt_list[1]}{utils.Plg.wld_mtx_plg}", f"{mm_skn_low_parent}{utils.Plg.mtx_ins[1]}")
            # > jnt_skn_low_parent
        utils.connect_attr(f"{mm_skn_low_parent}{utils.Plg.mtx_sum_plg}", f"{jnt_skn_low_parent}{utils.Plg.opm_plg}")


    def wire_rotations_on_twist_joints(self, skn_jnt_end, ctrl_limb_root, jnt_logic_upper, jnt_logic_lower, hdl_upper, hdl_lower):
        '''
        # Description:
            Twisting of the upper & lower skn joint chains are driven by their 
            ik handle's .twist attribute.
            - Upper handle twisting is driven by jnt_logic_upper & jnt_logic_lower  
            - lower handle twisting is driven by jnt_logic_lower & jnt_skn_end
        # Arguments:
            
        # Returns:
            hdl_upper_name (string): name of upper spring solver ik handle 
            hdl_lower_name (string): name of lower spring solver ik handle
        '''
        # jnt_logic_upper = logic_jnt_list[0]
        # jnt_logic_lower = logic_jnt_list[1]

        # upper 7 utility nodes
        im_upp_fk_twist = f"IM_twist_fkNonRoll_{hdl_upper}"
        mm_upp_fk_twist = f"MM_twist_fkNonRoll_{hdl_upper}"
        dm_upp_fk_twist = f"DM_twist_fkNonRoll_{hdl_upper}"
        quatToEuler_upp_fk_twist = f"QTE_twist_fkNonRoll_{hdl_upper}"
        mm_upp_twist = f"MM_twist_NonRoll_{hdl_upper}"
        dm_upp_twist = f"DM_twist_NonRoll_{hdl_upper}"
        quatToEuler_upp_twist = f"QTE_twist_NonRoll_{hdl_upper}"
        fm_upp_twist = f"FM_jntTwistValue_add_{hdl_upper}"

        utils.cr_node_if_not_exists(1, 'inverseMatrix', im_upp_fk_twist)
        utils.cr_node_if_not_exists(1, 'multMatrix', mm_upp_fk_twist)
        utils.cr_node_if_not_exists(1, 'decomposeMatrix', dm_upp_fk_twist)
        utils.cr_node_if_not_exists(1, 'quatToEuler', quatToEuler_upp_fk_twist)
        utils.cr_node_if_not_exists(1, 'multMatrix', mm_upp_twist)
        utils.cr_node_if_not_exists(1, 'decomposeMatrix', dm_upp_twist)
        utils.cr_node_if_not_exists(1, 'quatToEuler', quatToEuler_upp_twist)
        utils.cr_node_if_not_exists(1, 'floatMath', fm_upp_twist, {"operation":0})

        # temp locator ( to compare 'jnt_logic_upper' with its own initial rotation state inverted. )
        temp_loc_upper = f"loc_temp_upper_{ctrl_limb_root.replace('ctrl_', 'loc_')}"
        cmds.spaceLocator(n=temp_loc_upper)
        cmds.matchTransform(temp_loc_upper, jnt_logic_upper, pos=1, scl=0, rot=1)
        cmds.parent(temp_loc_upper, ctrl_limb_root)
        get_matrix = cmds.getAttr(f"{temp_loc_upper}.matrix")
        cmds.setAttr(f"{im_upp_fk_twist}{utils.Plg.inp_mtx_plg}", *get_matrix, type="matrix")

        # wire Upper 
            # fk_nonRoll
            # > mm_upp_fk_twist
        utils.connect_attr(f"{jnt_logic_upper}{utils.Plg.wld_mtx_plg}", f"{mm_upp_fk_twist}{utils.Plg.mtx_ins[0]}")
        utils.connect_attr(f"{im_upp_fk_twist}{utils.Plg.out_mtx_plg}", f"{mm_upp_fk_twist}{utils.Plg.mtx_ins[1]}")
            # > dm_upp_fk_twist
        utils.connect_attr(f"{mm_upp_fk_twist}{utils.Plg.mtx_sum_plg}", f"{dm_upp_fk_twist}{utils.Plg.inp_mtx_plg}")
            # > quatToEuler_upp_fk_twist
        utils.connect_attr(f"{dm_upp_fk_twist}.outputQuatX", f"{quatToEuler_upp_fk_twist}.inputQuatX")
        utils.connect_attr(f"{dm_upp_fk_twist}.outputQuatW", f"{quatToEuler_upp_fk_twist}.inputQuatW")
            # nonRoll
            # > mm_upp_twist
        utils.connect_attr(f"{jnt_logic_lower}{utils.Plg.wld_mtx_plg}", f"{mm_upp_twist}{utils.Plg.mtx_ins[0]}")
        utils.connect_attr(f"{jnt_logic_upper}{utils.Plg.wld_inv_mtx_plg}", f"{mm_upp_twist}{utils.Plg.mtx_ins[1]}")
            # > dm_upp_twist
        utils.connect_attr(f"{mm_upp_twist}{utils.Plg.mtx_sum_plg}", f"{dm_upp_twist}{utils.Plg.inp_mtx_plg}")
            # > quatToEuler_upp_twist
        utils.connect_attr(f"{dm_upp_twist}.outputQuatX", f"{quatToEuler_upp_twist}.inputQuatX")
        utils.connect_attr(f"{dm_upp_twist}.outputQuatW", f"{quatToEuler_upp_twist}.inputQuatW")
            # > fm_upp_twist
        utils.connect_attr(f"{quatToEuler_upp_fk_twist}.outputRotateX", f"{fm_upp_twist}{utils.Plg.flt_A}")
        utils.connect_attr(f"{quatToEuler_upp_twist}.outputRotateX", f"{fm_upp_twist}{utils.Plg.flt_B}")
            # > hdl_upper.twist
        utils.connect_attr(f"{fm_upp_twist}{utils.Plg.out_flt}", f"{hdl_upper}.twist")
        cmds.delete(temp_loc_upper)

        # lower 3 utility nodes
        # im_low_twis = f"IM_twist_NonRoll_{hdl_lower}"
        mm_low_twist = f"MM_twist_NonRoll_{hdl_lower}"
        # pm_low_twist = f"PMtx_twist_NonRoll_{hdl_lower}"
        dm_low_twist = f"DM_twist_NonRoll_{hdl_lower}"
        quatToEuler_low_twist = f"QTE_twist_NonRoll_{hdl_lower}"

        utils.cr_node_if_not_exists(1, 'multMatrix', mm_low_twist)
        # utils.cr_node_if_not_exists(1, 'inverseMatrix', im_low_twis)
        utils.cr_node_if_not_exists(1, 'decomposeMatrix', dm_low_twist)
        utils.cr_node_if_not_exists(1, 'quatToEuler', quatToEuler_low_twist)

        # temp locator ( to compare 'jnt_logic_upper' with its own initial rotation state inverted. )
        # temp_loc_lower = f"loc_temp_lower_{ctrl_limb_root.replace('ctrl_', 'loc_')}"
        # cmds.spaceLocator(n=temp_loc_lower)
        # cmds.matchTransform(temp_loc_lower, skn_jnt_end, pos=1, scl=0, rot=1)
        # cmds.parent(temp_loc_lower, ctrl_limb_root)
        # get_matrix = cmds.getAttr(f"{temp_loc_lower}.matrix")
        # cmds.setAttr(f"{im_low_twis}{utils.Plg.inp_mtx_plg}", *get_matrix, type="matrix")

        # wire lower 
            # > mm_low_twist
        utils.connect_attr(f"{skn_jnt_end}{utils.Plg.wld_mtx_plg}", f"{mm_low_twist}{utils.Plg.mtx_ins[0]}")
        utils.connect_attr(f"{jnt_logic_lower}{utils.Plg.wld_inv_mtx_plg}", f"{mm_low_twist}{utils.Plg.mtx_ins[1]}")

            # > dm_low_twist
        utils.connect_attr(f"{mm_low_twist}{utils.Plg.mtx_sum_plg}", f"{dm_low_twist}{utils.Plg.inp_mtx_plg}")
            # > quatToEuler_upp_twist
        utils.connect_attr(f"{dm_low_twist}.outputQuatX", f"{quatToEuler_low_twist}.inputQuatX")
        utils.connect_attr(f"{dm_low_twist}.outputQuatW", f"{quatToEuler_low_twist}.inputQuatW")
            # > hdl_lower.twist
        utils.connect_attr(f"{quatToEuler_low_twist}.outputRotateX", f"{hdl_lower}.twist")
        # cmds.delete(temp_loc_lower)


    # Phase 3 - Finalising ( Phase 2 - Module-specific class functions in 'System[ModuleName]' )
    def output_group_setup(self, output_hook_atr_list):
        '''
        # Description:
            Iterate through the two lists:
                Connects the object to attributes on this module's output group 
                so another module's inpout group can have incoming plugs to allow
                it to follow!
        # Attributes:
            mdl_output_grp (str): Name of this module's output group
            object_name_ls (list): Name of object that is what matrix data is 
                                    coming from for this attribute on the output 
                                    grp(could be derived from the dict...)
            output_hook_atr_list (list): Name of the corresponding matrix 
                                        atttribute to connect to that exists on 
                                        the output grp.
        # Returns: N/A
        # Future updates:
            Problem -> Handle the attrib names on the Input & Output grps in a way that can be shared between the other modules.
            Solution -> Store this data in the database & access it from there when neccessary by encoding it in a dictionary!
        '''



        # for obj_name, mtx_obj_name in zip(object_name_ls, output_hook_atr_list): # _top_mtx
        #     MM_output_top = f"MM_output_{obj_name}"
        #         # cr the MM nodes
        #     utils.cr_node_if_not_exists(1, 'multMatrix', MM_output_top)
        #     top_inverse_mtx = cmds.getAttr(f"{obj_name}{utils.Plg.wld_inv_mtx_plg}")
        #         # > MM's
        #     cmds.setAttr(f"{MM_output_top}{utils.Plg.mtx_ins[0]}", *top_inverse_mtx, type="matrix")
        #     utils.connect_attr(f"{obj_name}{utils.Plg.wld_mtx_plg}", f"{MM_output_top}{utils.Plg.mtx_ins[1]}")
        #         # > mdl_output_grp.mtx_obj_name
        #     utils.connect_attr(f"{MM_output_top}{utils.Plg.mtx_sum_plg}", f"{mdl_output_grp}.mtx_{self.dm.mdl_nm}_{mtx_obj_name}")


        for output_hook_atr in output_hook_atr_list: # _top_mtx
            obj_name = utils.return_output_hook_object(output_hook_atr)
            output_hook_mtx_plg = utils.return_module_output_hook_plug(
                                output_hook_atr, 
                                self.dm.mdl_nm, 
                                self.dm.unique_id, 
                                self.dm.side
                                )
            
            MM_output_top = f"MM_output_{obj_name}"
                # cr the MM nodes
            utils.cr_node_if_not_exists(1, 'multMatrix', MM_output_top)
            top_inverse_mtx = cmds.getAttr(f"{obj_name}{utils.Plg.wld_inv_mtx_plg}")
                # > MM's
            cmds.setAttr(f"{MM_output_top}{utils.Plg.mtx_ins[0]}", *top_inverse_mtx, type="matrix")
            utils.connect_attr(f"{obj_name}{utils.Plg.wld_mtx_plg}", f"{MM_output_top}{utils.Plg.mtx_ins[1]}")
                # > mdl_output_grp.mtx_obj_name
            utils.connect_attr(f"{MM_output_top}{utils.Plg.mtx_sum_plg}", output_hook_mtx_plg)


    def group_module(self, module_name, unique_id, side, input_grp, output_grp, ctrl_grp=None, joint_grp=None, logic_grp=None):
            '''
            # Description: 
                Coordinates the hierarchy of all elements included in a module 
                and setup the hierarchy into a single grp node. 
            # Attributes: N/A
            # Returns: N/A
            '''
            grp_module_name = f"grp_mdl_{module_name}_{unique_id}_{side}"
            if not cmds.objExists(grp_module_name):
                cmds.group(n=grp_module_name, em=1)
            
            if cmds.objExists(input_grp) and cmds.objExists(output_grp):
                cmds.parent(input_grp, output_grp, grp_module_name)

            # check if the ctrl grp name provided exists in the scene!
            if ctrl_grp:
                if cmds.objExists(ctrl_grp):
                    try:
                        cmds.parent(ctrl_grp, grp_module_name)
                    except Warning:
                        pass
                else:
                    print(f"No module child group `{ctrl_grp}` exists in the scene")

            if joint_grp:
                if cmds.objExists(joint_grp):
                    cmds.parent(joint_grp, grp_module_name)
                else:
                    print(f"No module child group `{joint_grp}` exists in the scene")

            if logic_grp:
                if cmds.objExists(logic_grp):
                    cmds.parent(logic_grp, grp_module_name)
                    cmds.hide(logic_grp)
                else:
                    print(f"No module child group `{logic_grp}` exists in the scene")
            cmds.select(cl=1)
            print(F"Grouped Module: {module_name}_{unique_id}_{side}")