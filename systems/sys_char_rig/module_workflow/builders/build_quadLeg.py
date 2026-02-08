

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
        # - - - - - - -
        # phase 1 - foundation
        input_grp, output_grp = self.cr_input_output_groups()
        self.add_outputs_matrix_attr(output_grp, self.dm.output_hook_mtx_list)
        if cmds.objExists(self.dm.external_plg_dict['global_scale_grp']):# cmds.objExists(self.dm.external_plg_dict['base_plg_grp']) and cmds.objExists(self.dm.external_plg_dict['hook_plg_grp']):
            print(F"running 'wire_input_grp()'")
            self.wire_input_grp(input_grp, self.dm.GLOBAL_SCALE_PLG, self.dm.BASE_MTX_PLG, self.dm.HOOK_MTX_PLG)

        fk_ctrl_grp = self.group_ctrls(self.dm.fk_ctrl_list, "fk")
        ik_ctrl_grp = self.group_ctrls(self.dm.ik_ctrl_list, "ik")

        # remove 'rump' (first item) item from `skel pos & rot dicts` (does NOT affect orginal dict)
        temp_skel_pos_dict = utils.pop_first_item_in_dict(self.dm.skel_pos_dict)
        temp_skel_rot_dict = utils.pop_first_item_in_dict(self.dm.skel_rot_dict)

        fk_logic_jnt_ls = self.cr_typ_jnt_chain("fk", temp_skel_pos_dict, temp_skel_rot_dict)
        ik_logic_jnt_ls = self.cr_typ_jnt_chain("ik", temp_skel_pos_dict, temp_skel_rot_dict)
        skin_jnt_ls = self.cr_typ_jnt_chain("skn", temp_skel_pos_dict, temp_skel_rot_dict)

        logic_grp = self.cr_logic_group()
        joint_grp = self.cr_joint_group()

        d_skel_dict = self.logic_jnt_distances(self.dm.skel_pos_num, temp_skel_pos_dict)
        print(f" -* d_skel_dict = {d_skel_dict}")
        
        db_hip_calf = utils.get_distance("hip_calf", list(self.dm.fk_pos_dict.values())[0], list(self.dm.fk_pos_dict.values())[2])
        print(f" -* db_hip_ankle = {db_hip_calf}")

        db_hip_kne, db_kne_clf = d_skel_dict['hip_knee'], d_skel_dict['knee_calf']
        print(f" -* db_hip_kne = `{db_hip_kne}`")
        print(f" -* db_kne_clf = `{db_kne_clf}`")

        # - - - - - - -
        # Phase 2 - Module-specific
        self.add_custom_input_attr(input_grp)
        # self.wire_hook_limbRoot_setup(input_grp, self.dm.ik_ctrl_list[1], self.dm.ik_pos_dict, self.dm.ik_rot_dict)
        self.wire_hook_rump_limbRoot_setup(input_grp, self.dm.ik_ctrl_list, self.dm.ik_pos_dict, self.dm.ik_rot_dict)
        #------
        # fk setup
        BM_limbRt_node = self.wire_fk_ctrl_setup(input_grp, self.dm.ik_ctrl_list[1], self.dm.fk_ctrl_list, self.dm.fk_pos_dict, self.dm.fk_rot_dict)
        self.wire_fk_logic_joints(self.dm.fk_ctrl_list, fk_logic_jnt_ls, BM_limbRt_node)
        
        # #------
        # # ik setup
        self.wire_ik_ctrl_end_no_blend(input_grp, self.dm.ik_ctrl_list[1], self.dm.ik_ctrl_list)

        ctrl_extrenal = self.return_external_ik_control(self.dm.HOOK_MTX_PLG) # f"ctrl_ik_spine_bottom_0_M"
        print(f"ctrl_extrenal = `{ctrl_extrenal}`")
        self.wire_ik_ctrl_pv(input_grp, 2, self.dm.ik_ctrl_list, ctrl_extrenal)
        self.wire_pv_reference_curve(self.dm.ik_ctrl_list[2], ik_logic_jnt_ls[1], ik_ctrl_grp)

        jnt_aim_ls = self.cr_ik_aim_logic_joints(self.dm.ik_pos_dict, self.dm.ik_rot_dict, self.dm.ik_ctrl_list, ik_logic_jnt_ls)
        
        self.wire_logic_ik_handles(input_grp, ik_logic_jnt_ls, self.dm.ik_ctrl_list, 
                                   self.dm.ik_pos_dict, self.dm.ik_rot_dict)
        #     # limbRoot control drive ik hip joint. 
        self.wire_limbRt_ik_chain_root(self.dm.ik_ctrl_list, ik_logic_jnt_ls, self.dm.ik_pos_dict, self.dm.ik_rot_dict)
        temp_lion_foot_piv_dict = {
            "piv_out": [[14.085709571838375, 0.1273138374090239, -39.837726593017564],[0.0, 11.1360043694971, 0.0]],
            "piv_in": [[4.575018405914303, 0.72316294908524, -37.60049057006834],[0.0, 11.136004369497094, 0.0]],
            "piv_toe": [[10.154307365417475, -0.0607974529266313, -34.73563385009764],[0.0, 11.136004369497106, 0.0]],
            "piv_heel": [[7.941305160522457, -0.008862497514643838, -44.297607421874986],[0.0, 11.136004369497092, 0.0]],
        }
        temp_trex_foot_piv_dict = {
            "piv_out": [[100.38125628190824, 0.0, -23.437266211204935], [0.0, 6.897799047713135, 0.0]],
            "piv_in": [[24.759938989748164, 0.005085100521610402, -14.289028733356286],[0.0, 6.897799047713135, 0.0]],
            "piv_toe": [[70.09476741199015, 0.0, 33.15645742422107],[0.0, 6.897799047713135, 0.0]],
            "piv_heel": [[59.66413598122727, 0.0, -53.06540654795396],[0.0, 6.897799047713135, 0.0]],
        }
        ik_ankle_trans_data = [list(self.dm.ik_pos_dict.values())[-1], list(self.dm.ik_rot_dict.values())[-1]]
        grp_ori, grp_hdl_calf = self.wire_ik_logic_hierarchy(temp_trex_foot_piv_dict, ik_ankle_trans_data)
        self.pv_ik_hdl_leg_setup(self.dm.ik_ctrl_list[2])
        self.position_ik_ctrl_calf(self.dm.ik_ctrl_list[3], list(self.dm.ik_pos_dict.values()), list(self.dm.ik_rot_dict.values()))
        grp_logic_aim_hdl = self.wire_calf_aim_setup(jnt_aim_ls, self.dm.ik_ctrl_list, ik_logic_jnt_ls )
        
        #------
        # ikfk switch
        mdl_settings_ctrl, ikfk_plug, stretch_state_plug, stretch_vol_plug, shaper_plug = self.wire_mdl_setting_ctrl(skin_jnt_ls[3])
        self.blend_ik_fk_states_to_skin_chain(ik_logic_jnt_ls, fk_logic_jnt_ls, skin_jnt_ls, mdl_settings_ctrl, ikfk_plug)
        ikfk_rev = self.wire_IKFK_switch(mdl_settings_ctrl, ikfk_plug, fk_ctrl_grp, ik_ctrl_grp, self.dm.ik_ctrl_list[1])
        
        #------
        # rump aim setup
            # func: position & aim 2 rump locators 
        loc_aim_on, loc_aim_off = self.cr_rump_aim_locators(self.dm.ik_ctrl_list)
        self.wire_rump_aim_setup(self.dm.ik_ctrl_list, loc_aim_on, loc_aim_off, ikfk_plug, ikfk_rev)

        #------
        # foot setup
        foot_piv_atr_list = self.cr_foot_atr(self.dm.ik_ctrl_list)
        self.wire_foot_atr(foot_piv_atr_list, self.dm.ik_ctrl_list)
            # function to add roller ofs grp.
        roller_grp_dict = {
            grp_hdl_calf:"rollerAnkle",
            f"piv_toe_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}":"rollerToeEnd", 
            f"piv_heel_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}":"rollerHeel"
            }
        wedged_roller_groups = self.wedge_roller_group(roller_grp_dict)
            # function to wire roller attrs
        self.wire_roller_foot_setup(ik_ctrl_list=self.dm.ik_ctrl_list, 
                                    ankle_grp=wedged_roller_groups[0], 
                                    toe_grp=wedged_roller_groups[1], 
                                    heel_grp=wedged_roller_groups[2])
        
        #------
        # twist limb setup
            # cr twist curves & skn joints
        cv_upper, upper_cv_intermediate_pos_ls = self.cr_logic_curves("upper", temp_skel_pos_dict['hip'], temp_skel_pos_dict['knee'])
        cv_lower, lower_cv_intermediate_pos_ls = self.cr_logic_curves("lower", temp_skel_pos_dict['knee'], temp_skel_pos_dict['calf'])
        
        sknUpper_jnt_chain = self.cr_skn_twist_joint_chain("upper", cv_upper, skin_jnt_ls[0], 'zup')
        sknLower_jnt_chain = self.cr_skn_twist_joint_chain("lower", cv_lower, skin_jnt_ls[1], 'zup')
        
        # shaper controls: (drives the twist joints to follow the rig)
        unorganised_shaper_ctrl_list = ["ctrl_shp_quadLeg_main_0_L", "ctrl_shp_quadLeg_middle_0_L", 
                                    "ctrl_shp_quadLeg_upper_0_L", "ctrl_shp_quadLeg_lower_0_L"]
        shaper_ctrl_list = self.organise_ctrl_shaper_list(unorganised_shaper_ctrl_list)
        shaper_ctrl_grp = self.group_ctrls(shaper_ctrl_list, "shaper")
        self.wire_shaper_ctrls(shaper_ctrl_list, skin_jnt_ls, shaper_plug, shaper_ctrl_grp)
        self.wire_shaper_ctrls_to_curves(shaper_ctrl_list, cv_upper, cv_lower, upper_cv_intermediate_pos_ls, lower_cv_intermediate_pos_ls, skin_jnt_ls)
    
            # twist operations
        hdl_upper, hdl_lower = self.cr_twist_ik_spline(logic_grp, sknUpper_jnt_chain, sknLower_jnt_chain, cv_upper, cv_lower)
        self.wire_parent_skn_twist_joint_matrix(sknUpper_jnt_chain, sknLower_jnt_chain, self.dm.ik_ctrl_list[1], skin_jnt_ls[1], temp_skel_pos_dict, temp_skel_rot_dict)
        fm_upp_global, fm_low_global = self.wire_skn_twist_joints_stretch(input_grp, sknUpper_jnt_chain, sknLower_jnt_chain, cv_upper, cv_lower)
        self.wire_skn_twist_joints_volume(input_grp, sknUpper_jnt_chain, sknLower_jnt_chain, cv_upper, cv_lower, stretch_vol_plug, fm_upp_global, fm_low_global, db_hip_kne, db_kne_clf)
        self.wire_rotations_on_twist_joints(self.dm.ik_ctrl_list[1], skin_jnt_ls[0], skin_jnt_ls[1], skin_jnt_ls[2], hdl_upper, hdl_lower)


        # temp hide data
        self.hide_data_in_scene(fk_ctrl_grp, ik_ctrl_grp, fk_logic_jnt_ls, ik_logic_jnt_ls, skin_jnt_ls, jnt_aim_ls)
        
        # - - - - - - -
        # Phase 3 - finalising

        self.group_jnts_skn(joint_grp, [], [skin_jnt_ls, sknUpper_jnt_chain, sknLower_jnt_chain])
        self.group_quad_logic_elements(logic_grp, [fk_logic_jnt_ls, ik_logic_jnt_ls, jnt_aim_ls], [cv_upper, cv_lower], [grp_ori, grp_logic_aim_hdl])
        self.parent_ik_ctrls_out(self.dm.ik_ctrl_list)
        self.lock_ctrl_attributes(self.dm.fk_ctrl_list, self.dm.ik_ctrl_list, mdl_settings_ctrl)

        self.output_group_setup(self.dm.output_hook_mtx_list)

        self.group_module(self.dm.mdl_nm, self.dm.unique_id, self.dm.side,
                    input_grp, output_grp, 
                    f"grp_ctrls_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}", 
                    joint_grp, 
                    logic_grp)
