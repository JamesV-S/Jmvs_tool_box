


import importlib
import maya.cmds as cmds

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

class SystemRoot:
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
        print(f"SystemRoot -> dataa_manager = {data_manager}")
        

    # Phase 2 - Module-specific class functions in 'System[ModuleName]'
    def wire_root_setup(self, input_grp , fk_ctrl_ls, skeleton_pos_dict, skeleton_rot_dict):
        root_ctrl, centre_ctrl, cog_ctrl = fk_ctrl_ls
        
        # add custom attr scale
        utils.add_float_attrib(root_ctrl, [self.dm.global_scale_attr], [0.01, 999], True)
        cmds.setAttr(f"{root_ctrl}.{self.dm.global_scale_attr}", 1, keyable=1, channelBox=1)

        # create utility's
        fm_global_scale = f"FM_root_{self.dm.global_scale_attr}"
        utils.cr_node_if_not_exists(1, "floatMath", fm_global_scale, {"operation":2})
            # 4 MM
        MM_centre = f"MM_ctrl_centre"
        MM_cog = f"MM_ctrl_cog"
        
        MM_list = [MM_centre, MM_cog]
        for node_name in MM_list:
            utils.cr_node_if_not_exists(1, "multMatrix", node_name)

        # connections
        utils.connect_attr(f"{input_grp}.{self.dm.global_scale_attr}", f"{fm_global_scale}{utils.Plg.flt_A}")
        utils.connect_attr(f"{root_ctrl}.{self.dm.global_scale_attr}", f"{fm_global_scale}{utils.Plg.flt_B}")

        # root
        for x in range(3):
            utils.connect_attr(f"{fm_global_scale}{utils.Plg.out_flt}", f"{root_ctrl}.scale{utils.Plg.axis[x]}")

        # centre
        utils.connect_attr(f"{root_ctrl}{utils.Plg.wld_mtx_plg}", f"{MM_centre}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{MM_centre}{utils.Plg.mtx_sum_plg}", f"{centre_ctrl}{utils.Plg.opm_plg}")

        # cog
            # Set the matrixIn[0]
        # get_cog_wld_mtx = cmds.getAttr(f"{cog_ctrl}{utils.Plg.wld_mtx_plg}")
        # cmds.setAttr(f"{MM_cog}{utils.Plg.mtx_ins[0]}", *get_cog_wld_mtx, type="matrix")
        utils.set_transformation_matrix(skeleton_pos_dict["COG"], skeleton_rot_dict["COG"], f"{MM_cog}{utils.Plg.mtx_ins[0]}")
        utils.connect_attr(f"{centre_ctrl}{utils.Plg.wld_mtx_plg}", f"{MM_cog}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{MM_cog}{utils.Plg.mtx_sum_plg}", f"{cog_ctrl}{utils.Plg.opm_plg}")


    def root_output_group_setup(self, global_scale_plg, glabal_scale_ctrl, output_hook_atr_list):
        '''
        # Description:
            A uniqye funtion for the root module, since it's the root!
            Connects the base and hook attributes on this module's output group 
            so another module's input group can have incoming plugs to allow it to follow!
        # Arguments:
            global_scale_plg (constant): external glabal scale matrix plug.
            output_hook_atr_list (lsit): This module's ouput hook matrix list of attrs. ["fk_centre", "fk_COG"]
            glabal_scale_ctrl (string): The control name that has the global scale attr on it! (= the root control).
        # Returns: N/A
        '''
        
        '''
        "grp_Outputs_root_0_M.mtx_root_ctrlCOG"
        '''
        # `output_base_obj_name` = ctrl_centre
        # `output_hook_obj_name` = ctrl_cog
        obj_output_base = utils.return_output_hook_object(output_hook_atr_list[0])
        obj_output_hook = utils.return_output_hook_object(output_hook_atr_list[1])
        print(f"obj_output_base (ctrl_centre) = `{obj_output_base}`")
        print(f"obj_output_base (ctrl_cog) = `{obj_output_hook}`")

        # output_base_mtx_plg (constant): ouput base matrix plug = output_hook_atr_list[0] -> "fk_centre"
        output_base_mtx_plg  = utils.return_module_output_hook_plug(
                                output_hook_atr_list[0], 
                                self.dm.mdl_nm, 
                                self.dm.unique_id, 
                                self.dm.side
                                )

        # output hook matrix plug = output_hook_atr_list[1] -> "fk_COG"
        output_hook_mtx_plg  = utils.return_module_output_hook_plug(
                                output_hook_atr_list[1], 
                                self.dm.mdl_nm, 
                                self.dm.unique_id, 
                                self.dm.side
                                )
        

        # cr two multMatrixs
        # MM_output_top = f"MM_output_{ctrl_spine_top}"
        # MM_output_bot = f"MM_output_{ctrl_spine_bottom}"
        MM_output_base = f"MM_output_{obj_output_base}"
        MM_output_hook = f"MM_output_{obj_output_hook}"
            
            # cr the MM nodes
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_output_base)
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_output_hook)
        centre_inverse_mtx = cmds.getAttr(f"{obj_output_base}{utils.Plg.wld_inv_mtx_plg}")
        cog_inverse_mtx = cmds.getAttr(f"{obj_output_hook}{utils.Plg.wld_inv_mtx_plg}")
        # Plugs - connect ik ctrl's to MM's
        cmds.setAttr(f"{MM_output_base}{utils.Plg.mtx_ins[0]}", *centre_inverse_mtx, type="matrix")
        cmds.setAttr(f"{MM_output_hook}{utils.Plg.mtx_ins[0]}", *cog_inverse_mtx, type="matrix")
        utils.connect_attr(f"{obj_output_base}{utils.Plg.wld_mtx_plg}", f"{MM_output_base}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{obj_output_hook}{utils.Plg.wld_mtx_plg}", f"{MM_output_hook}{utils.Plg.mtx_ins[1]}")
        # Plugs - connect the MM to the spine output's attribs!  
        utils.connect_attr(f"{MM_output_base}{utils.Plg.mtx_sum_plg}", output_base_mtx_plg)
        utils.connect_attr(f"{MM_output_hook}{utils.Plg.mtx_sum_plg}", output_hook_mtx_plg)
        utils.connect_attr(f"{glabal_scale_ctrl}.{self.dm.global_scale_attr}", global_scale_plg)