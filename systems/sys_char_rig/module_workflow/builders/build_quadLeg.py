

# import the two parent classes to inherit from
import importlib
import maya.cmds as cmds

# from data_managers import module_data_manager
from systems.sys_char_rig.module_workflow.blueprints import module_blueprint
from systems.sys_char_rig.module_workflow.mdl_systems import system_quadLeg

from utils import (
    utils
)
from systems.sys_char_rig import (
    cr_ctrl
)

importlib.reload(module_blueprint)
importlib.reload(system_quadLeg)
importlib.reload(utils)
importlib.reload(cr_ctrl)


class BuildQuadLeg(module_blueprint.ModuleBP, system_quadLeg.SystemQuadLeg):
    def __init__(self, data_manager):
        module_blueprint.ModuleBP.__init__(self, data_manager)
        system_quadLeg.SystemQuadLeg.__init__(self, data_manager) 


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


        # Phase 1 - Foundation
        input_grp, output_grp = self.cr_input_output_groups()
        self.add_outputs_matrix_attr(output_grp, self.dm.output_hook_mtx_list)
        if cmds.objExists(self.dm.external_plg_dict['global_scale_grp']):# cmds.objExists(self.dm.external_plg_dict['base_plg_grp']) and cmds.objExists(self.dm.external_plg_dict['hook_plg_grp']):
            print(F"running 'wire_input_grp()'")
            self.wire_input_grp(input_grp, self.dm.GLOBAL_SCALE_PLG, self.dm.BASE_MTX_PLG, self.dm.HOOK_MTX_PLG)

        fk_ctrl_grp = self.group_ctrls(self.dm.fk_ctrl_list, "fk")
        ik_ctrl_grp = self.group_ctrls(self.dm.ik_ctrl_list, "ik")

        fk_logic_jnt_ls = self.cr_typ_jnt_chain("fk", self.dm.skel_pos_dict, self.dm.skel_rot_dict)
        ik_logic_jnt_ls = self.cr_typ_jnt_chain("ik", self.dm.skel_pos_dict, self.dm.skel_rot_dict)
        skin_jnt_ls = self.cr_typ_jnt_chain("skn", self.dm.skel_pos_dict, self.dm.skel_rot_dict)

        # Phase 2 - Module-specific class functions in 'System[ModuleName]'
        self.logic_jnt_distances(self.dm.skel_pos_num, self.dm.skel_pos_dict)
        self.wire_hook_limbRoot_setup(input_grp, self.dm.ik_ctrl_list, self.dm.ik_pos_dict, self.dm.ik_rot_dict)
        
        BM_limbRt_node = self.wire_fk_ctrl_setup(input_grp, self.dm.ik_ctrl_list[0], self.dm.fk_ctrl_list, self.dm.fk_pos_dict, self.dm.fk_rot_dict)
        self.wire_fk_logic_joints(self.dm.fk_ctrl_list, fk_logic_jnt_ls, BM_limbRt_node)

        self.wire_ik_ctrl_end(input_grp, self.dm.ik_ctrl_list[0], self.dm.ik_ctrl_list)

        ctrl_extrenal = self.return_external_ik_control(self.dm.HOOK_MTX_PLG) # f"ctrl_ik_spine_bottom_0_M"
        print(f"ctrl_extrenal = `{ctrl_extrenal}`")
        self.wire_ik_ctrl_pv(input_grp, 1, self.dm.ik_ctrl_list, ctrl_extrenal)
        
        ''' call function to position calf control here! '''

        self.wire_pv_reference_curve(self.dm.ik_ctrl_list[1], ik_logic_jnt_ls[1], ik_ctrl_grp)
        
        jnt_aim_ls = self.cr_ik_aim_logic_joints(self.dm.ik_pos_dict, self.dm.ik_rot_dict, self.dm.ik_ctrl_list, ik_logic_jnt_ls)
        
        # ik setup
        self.wire_logic_ik_handles(input_grp, ik_logic_jnt_ls, self.dm.ik_ctrl_list, 
                                   self.dm.ik_pos_dict, self.dm.ik_rot_dict)

        # limbRoot control drive ik hip joint. 
        self.wire_limbRt_ik_chain_root(self.dm.ik_ctrl_list, ik_logic_jnt_ls, self.dm.ik_pos_dict, self.dm.ik_rot_dict)

        ''' Work '''
        temp_lion_foot_piv_dict = {
            "piv_out": [[14.085709571838375, 0.1273138374090239, -39.837726593017564],[0.0, 11.1360043694971, 0.0]],
            "piv_in": [[4.575018405914303, 0.72316294908524, -37.60049057006834],[0.0, 11.136004369497094, 0.0]],
            "piv_toe": [[10.154307365417475, -0.0607974529266313, -34.73563385009764],[0.0, 11.136004369497106, 0.0]],
            "piv_heel": [[7.941305160522457, -0.008862497514643838, -44.297607421874986],[0.0, 11.136004369497092, 0.0]],
        }
        ik_ankle_trans_data = [list(self.dm.ik_pos_dict.values())[-1], list(self.dm.ik_rot_dict.values())[-1]]
        self.wire_ik_logic_hierarchy(temp_lion_foot_piv_dict, ik_ankle_trans_data)
        self.pv_ik_hdl_leg_setup(self.dm.ik_ctrl_list[1])
        self.position_ik_ctrl_calf(self.dm.ik_ctrl_list[2], list(self.dm.ik_pos_dict.values()), list(self.dm.ik_rot_dict.values()))
        self.wire_calf_aim_setup(jnt_aim_ls, self.dm.ik_ctrl_list, ik_logic_jnt_ls )

        mdl_settings_ctrl, ikfk_plug = self.wire_mdl_setting_ctrl(skin_jnt_ls[3])
        self.blend_ik_fk_states_to_skin_chain(ik_logic_jnt_ls, fk_logic_jnt_ls, skin_jnt_ls, mdl_settings_ctrl, ikfk_plug)
        
        # foot
        foot_piv_atr_list = self.cr_foot_atr(self.dm.ik_ctrl_list)
        self.wire_foot_atr(foot_piv_atr_list, self.dm.ik_ctrl_list)

        # # Phase 3 - Finalising
        # self.group_module(self.dm.mdl_nm, self.dm.unique_id, self.dm.side,
        #                    input_grp, output_grp, 
        #                    f"grp_ctrls_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}", 
        #                    f"grp_joints_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}", 
        #                    f"grp_logic_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}")