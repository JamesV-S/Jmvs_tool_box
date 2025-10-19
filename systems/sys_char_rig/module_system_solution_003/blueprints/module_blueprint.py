
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


    def group_module(module_name, unique_id, side, input_grp, output_grp, ctrl_grp=None, joint_grp=None, logic_grp=None):
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