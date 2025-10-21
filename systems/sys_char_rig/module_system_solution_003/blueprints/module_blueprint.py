
import importlib
import maya.cmds as cmds

''' in 'main.py' set the directory of the four folders for this workflow '''
from systems.sys_char_rig.module_system_solution_003.data_managers import module_data_manager

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
        # Returns:N/A
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

    # Module operations sharedf by multiple modules but not all
    def cr_jnt_type_chain(self, pref, skeleton_pos_dict, skeleton_rot_dict, reverse_direction=False):
        '''
        # Description:
           Creates a basic desired joint chain, naming, position and direction all 
           taken care of. 
        # Attributes:
            pref (string): name of the joint chain type.
            skeleton_pos_dict (dict): key = name of spine iteration (spine#), value = positonal data.
            skeleton_rot_dict (dict): key = name of spine iteration (spine#), value = rotational data.
            reverse_direction (bool): If True, the joint chain is reversed.
        # Returns:
            jnt_ls (list): The list of joints within the chain.
        '''
        cmds.select(cl=True)
        jnt_chain_ls = []
        # reverse the positon data
        # need to figure out how I need to flip or minus the rotate values (for when they have just 0.0 or a value.)
        # That'll consist of flipping the primary axis & 
        print(f"skeleton_rot_dict = {skeleton_rot_dict}")
        rev_skel_pos = utils.reverse_pos_values_dict(skeleton_pos_dict)
        rev_skel_rot = utils.reverse_rot_values_dict(skeleton_rot_dict)
        for name in skeleton_pos_dict:
            jnt_nm = f"jnt_{pref}_{self.dm.mdl_nm}_{name}_{self.dm.unique_id}_{self.dm.side}"
            jnt_chain_ls.append(jnt_nm)
            cmds.joint(n=jnt_nm)
            if reverse_direction:
                cmds.xform(jnt_nm, translation=rev_skel_pos[name], worldSpace=True)
                cmds.xform(jnt_nm, rotation=skeleton_rot_dict[name], worldSpace=True)
            else:
                cmds.xform(jnt_nm, translation=skeleton_pos_dict[name], worldSpace=True)
                cmds.xform(jnt_nm, rotation=skeleton_rot_dict[name], worldSpace=True)
            cmds.makeIdentity(jnt_nm, a=1, t=0, r=1, s=0, n=0, pn=1)
        utils.clean_opm(jnt_chain_ls[0])

        return jnt_chain_ls
    

    def wire_fk_ctrl_setup(self, inputs_grp, limbRt_ctrl, fk_ctrl_list, fk_pos_dict, fk_rot_dict):
        '''
        # Description:
            FK logic setup:
                - need corresponding fk joints (jnt_logic or jnt_fk -> depends on the module setup)
                - base & limbRt to multMatrix each > blendMatrix.
                - setup the fk controls with MM method. 
                - connect ctrl rotates to fk joints rotates (direct or constraint -> depends on the module setup)
                Temporary loactors are used to position the fk control's with 
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



    # Phase 3 - Finalising ( Phase 2 - Module-specific class functions in 'System[ModuleName]' )
    def output_group_setup(self, mdl_output_grp, object_name_ls, out_matrix_name_list):
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
            out_matrix_name_list (list): Name of the corresponding matrix 
                                        atttribute to connect to that exists on 
                                        the output grp.
        # Returns: N/A
        # Future updates:
            Problem -> Handle the attrib names on the Input & Output grps in a way that can be shared between the other modules.
            Solution -> Store this data in the database & access it from there when neccessary by encoding it in a dictionary!
        '''
        for obj_name, mtx_obj_name in zip(object_name_ls, out_matrix_name_list): # _top_mtx
            MM_output_top = f"MM_output_{obj_name}"
                # cr the MM nodes
            utils.cr_node_if_not_exists(1, 'multMatrix', MM_output_top)
            top_inverse_mtx = cmds.getAttr(f"{obj_name}{utils.Plg.wld_inv_mtx_plg}")
                # > MM's
            cmds.setAttr(f"{MM_output_top}{utils.Plg.mtx_ins[0]}", *top_inverse_mtx, type="matrix")
            utils.connect_attr(f"{obj_name}{utils.Plg.wld_mtx_plg}", f"{MM_output_top}{utils.Plg.mtx_ins[1]}")
                # > mdl_output_grp.mtx_obj_name
            utils.connect_attr(f"{MM_output_top}{utils.Plg.mtx_sum_plg}", f"{mdl_output_grp}.mtx_{self.dm.mdl_nm}_{mtx_obj_name}")


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