

# import the two parent classes to inherit from
import importlib
import maya.cmds as cmds

# from data_managers import module_data_manager
from systems.sys_char_rig.module_system_solution_003.blueprints import module_blueprint
from systems.sys_char_rig.module_system_solution_003.mdl_systems import system_spine

from utils import (
    utils
)
from systems.sys_char_rig import (
    cr_ctrl
)

importlib.reload(module_blueprint)
importlib.reload(system_spine)
importlib.reload(utils)
importlib.reload(cr_ctrl)

class BuildSpine(module_blueprint.ModuleBP, system_spine.SystemSpine):
    def __init__(self, data_manager):
        module_blueprint.ModuleBP.__init__(self, data_manager)
        # system_spine.SystemSpine.__init__(self, data_manager)
        print(f"-------  -------  --------  -------")
        print(f"Declared Build{self.dm.mdl_nm}")


    def build(self):
        '''
        # Description:
            Build Sequence to call:
            1. Foundation (ModuleBP)
            2. Module-specific (SystemRoot)
            3. Finalising (ModuleBP)
        # Attributes:
            module_name (string): name of this module.
            root_outputs_grp (string): 'Output' grp from other module for this one to follow.
            skeleton_dict (dict): (dict): key="skel_pos/rot"(string), value="skel_pos/rot"(dict).
            fk_dict (dict): (dict): key="fk_pos/rot"(string), value="fk_pos/rot"(dict).
            ik_dict (dict): (dict): key="ik_pos/rot"(string), value="ik_pos/rot"(dict).
        # Returns:N/A
        '''
        print(f"Running Build{self.dm.mdl_nm}.build()")

        inv_ctrl_ls = [key.replace("_fk_", "_inv_") for key in self.dm.fk_pos_dict.keys()]

        # Phase 1 - Foundation
        input_grp, output_grp = self.cr_input_output_groups()
        self.add_outputs_matrix_attr(output_grp, ["bottom", "top"])
        if cmds.objExists(self.dm.external_plg_dict['global_scale_grp']):
            self.wire_input_grp(input_grp, self.dm.GLOBAL_SCALE_PLG, self.dm.BASE_MTX_PLG, self.dm.HOOK_MTX_PLG)

        self.group_ctrls(self.dm.fk_ctrl_list, "fk")
        self.group_ctrls(self.dm.ik_ctrl_list, "ik")
        self.group_ctrls(inv_ctrl_ls, "inv")

        # # cr StrFw_jnt / nonStrFw / StrBw_jnt / nonStrBw in this script.
        strFw_jnt_chain = self.cr_typ_jnt_chain("StrFw", self.dm.skel_pos_dict, self.dm.skel_rot_dict)
        nonstrFw_jnt_chain = self.cr_typ_jnt_chain("nonStrFw", self.dm.skel_pos_dict, self.dm.skel_rot_dict)
        strBw_jnt_chain = self.cr_typ_jnt_chain("StrBw", self.dm.skel_pos_dict, self.dm.skel_rot_dict, True)
        nonstrBw_jnt_chain = self.cr_typ_jnt_chain("nonStrBw", self.dm.skel_pos_dict, self.dm.skel_rot_dict, True)
        strRig_jnt_chain = self.cr_typ_jnt_chain("StrRig", self.dm.skel_pos_dict, self.dm.skel_rot_dict)
        nonStrRig_jnt_chain = self.cr_typ_jnt_chain("nonStrRig", self.dm.skel_pos_dict, self.dm.skel_rot_dict)
        skn_jnt_chain = self.cr_typ_jnt_chain("skn", self.dm.skel_pos_dict, self.dm.skel_rot_dict)

        # Phase 2 - Module-specific
        skn_bott_name, skn_top_name = self.cr_jnt_skn_start_end(self.dm.ik_pos_dict)
        
        # Temporarily cr skin_jnt chain!
        self.group_jnts_skn([skn_bott_name, skn_top_name], [skn_jnt_chain])
        
        # custom attr on Outputs or inputs grp
        self.add_custom_input_attr(input_grp, self.dm.skel_pos_num)

        # CTRL connections for the spine setup!
        self.wire_spine_ctrls(input_grp, self.dm.fk_ctrl_list, inv_ctrl_ls, self.dm.ik_ctrl_list)
        
        # Logic setup (joints and hdl_spine_names)
        logic_grp, fk_logic_ls, inv_logic_ls, ik_logic_ls, jnt_mid_hold = self.cr_logic_elements(self.dm.fk_pos_dict, self.dm.fk_rot_dict, self.dm.ik_pos_dict, self.dm.ik_rot_dict, 
                                                                                                                          [strFw_jnt_chain, nonstrFw_jnt_chain], [strBw_jnt_chain, nonstrBw_jnt_chain],
                                                                                                                        [strRig_jnt_chain, nonStrRig_jnt_chain])
        # curve creation
        logic_FWcurve = self.cr_logic_curve("StrFw", self.dm.skel_pos_dict, logic_grp)
        logic_BWcurve = self.cr_logic_curve("StrBw", self.dm.skel_pos_dict, logic_grp, True)
        # global curve ik setup
        cv_info_FWnode, fm_global_FWnode = self.wire_ik_curve_setup("StrFw", logic_FWcurve, input_grp)
        cv_info_BWnode, fm_global_BWnode = self.wire_ik_curve_setup("StrBw", logic_BWcurve, input_grp)
        
        # # control to logic setup
        self.wire_ctrl_to_jnt_logic(self.dm.fk_ctrl_list, inv_ctrl_ls, self.dm.ik_ctrl_list, 
                                    fk_logic_ls, inv_logic_ls, ik_logic_ls)
        self.wire_ik_bott_top_logic_to_skn('skn', self.dm.skel_pos_dict, ik_logic_ls, self.dm.ik_ctrl_list)
        
        ''''''
        # stretch ik setup 
        self.wire_ik_stretch_setup("StrFw", logic_FWcurve, self.dm.skel_pos_dict, fm_global_FWnode, 
                                   ik_logic_ls, self.dm.ik_ctrl_list, jnt_mid_hold)
        self.wire_ik_stretch_setup("StrBw", logic_BWcurve, self.dm.skel_pos_dict, fm_global_BWnode, 
                                   ik_logic_ls, self.dm.ik_ctrl_list, jnt_mid_hold, True)

        # volume presevation
        self.wire_ik_volume_setup("skn", self.dm.skel_pos_dict, input_grp, 
                                  cv_info_FWnode, fm_global_FWnode, self.dm.ik_ctrl_list)

        # nonStr matching Str chain
        self.nonStr_match_setup(nonstrFw_jnt_chain, strFw_jnt_chain)
        self.nonStr_match_setup(nonstrBw_jnt_chain, strBw_jnt_chain)

        self.blend_fw_bw_states_to_skin_chain(strFw_jnt_chain, strBw_jnt_chain, strRig_jnt_chain,
                                              nonstrFw_jnt_chain, nonstrBw_jnt_chain, nonStrRig_jnt_chain,
                                              skn_jnt_chain, self.dm.ik_ctrl_list)

        # Phase 3 - Finalising
        self.output_group_setup(output_grp, [skn_bott_name, skn_top_name], ["bottom", "top"])

        self.group_module(self.dm.mdl_nm, self.dm.unique_id, self.dm.side,
                           input_grp, output_grp, 
                           f"grp_ctrls_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}", 
                           f"grp_joints_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}", 
                           f"grp_logic_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}")