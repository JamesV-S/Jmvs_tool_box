
# import the two parent classes to inherit from
import importlib
import maya.cmds as cmds

# from data_managers import module_data_manager
from systems.sys_char_rig.module_workflow.blueprints import module_blueprint
from systems.sys_char_rig.module_workflow.mdl_systems import system_bipedLeg

from utils import (
    utils
)
from systems.sys_char_rig import (
    cr_ctrl
)

importlib.reload(module_blueprint)
importlib.reload(system_bipedLeg)
importlib.reload(utils)
importlib.reload(cr_ctrl)

class BuildBipedLeg(module_blueprint.ModuleBP, system_bipedLeg.SystemBipedLeg):
    def __init__(self, data_manager):
        module_blueprint.ModuleBP.__init__(self, data_manager)
        system_bipedLeg.SystemBipedLeg.__init__(self, data_manager)
        
        print(f"-------  -------  --------  -------")
        print(f"Declared Build{self.dm.mdl_nm}")

    def build(self):
        print(f"running Build BipedLeg")
        # - - - - - - -
        # phase 1 - foundation
            # Input & Output grp setup
        input_grp, output_grp = self.cr_input_output_groups()
        self.add_outputs_matrix_attr(output_grp, self.dm.output_hook_mtx_list)
        if cmds.objExists(self.dm.external_plg_dict['global_scale_grp']):
            self.wire_input_grp(input_grp, self.dm.GLOBAL_SCALE_PLG, self.dm.BASE_MTX_PLG, self.dm.HOOK_MTX_PLG)

        # # Group the controls!
        fk_ctrl_grp = self.group_ctrls(self.dm.fk_ctrl_list, "fk")
        ik_ctrl_grp = self.group_ctrls(self.dm.ik_ctrl_list, "ik")
        
        logic_grp = self.cr_logic_group()
        joint_grp = self.cr_joint_group()

        # - - - - - - -
        # Phase 2 - Module-specific
            # # cr skn joints
        skn_jnt_ankle, skn_jnt_ball = self.cr_jnt_skn_individual(self.dm.fk_pos_dict)
        self.add_custom_input_attr(input_grp)
            # wire connections
        self.wire_hook_limbRt_setup(input_grp, self.dm.ik_ctrl_list, self.dm.ik_pos_dict, self.dm.ik_rot_dict)
        
        #------
        # fk setup
        blend_armRoot_node = self.wire_fk_ctrl_setup(input_grp, self.dm.ik_ctrl_list[0], self.dm.fk_ctrl_list[:-1], self.dm.fk_pos_dict, self.dm.fk_rot_dict)
        logic_jnt_list = self.cr_logic_rig_joints(self.dm.fk_ctrl_list[:-1], self.dm.fk_pos_dict, self.dm.fk_rot_dict)
        
        d_skel_dict = self.logic_jnt_distances(self.dm.skel_pos_num, self.dm.skel_pos_dict)
        print(f"d_skel_dict = {d_skel_dict}")
        db_hip_ankle = utils.get_distance("hip_kne", list(self.dm.fk_pos_dict.values())[0], list(self.dm.fk_pos_dict.values())[2])
        db_hip_kne, db_kne_akl = d_skel_dict['hip_knee'], d_skel_dict['knee_ankle']
        self.wire_fk_ctrl_stretch_setup(self.dm.fk_ctrl_list, db_hip_kne, db_kne_akl)
        self.wire_fk_ctrl_to_logic_joint(blend_armRoot_node, self.dm.fk_ctrl_list, logic_jnt_list)

        self.wire_ctrl_ik_ankle(input_grp, self.dm.ik_ctrl_list)

        ctrl_extrenal = self.return_external_ik_control(self.dm.HOOK_MTX_PLG)
        self.wire_ik_ctrl_pv(input_grp, 1, self.dm.ik_ctrl_list, ctrl_extrenal)
        self.wire_pv_reference_curve(self.dm.ik_ctrl_list[1], logic_jnt_list[1], ik_ctrl_grp)
        
        bc_ikfk_stretch, logic_ik_hdl = self.wire_ik_logic_elements(input_grp, logic_jnt_list, self.dm.ik_ctrl_list, db_hip_ankle, db_hip_kne, db_kne_akl)

        skn_jnt_ankle_ik_plg, skn_jnt_ankle_fk_plg = self.wire_jnt_skn_wrist(skn_jnt_ankle, logic_jnt_list, self.dm.fk_ctrl_list[:-1], self.dm.ik_ctrl_list)

        mdl_settings_ctrl, ikfk_plug, stretch_state_plug, stretch_vol_plug, shaper_plug  = self.wire_mdl_setting_ctrl(skn_jnt_ankle)
        
        self.wire_IKFK_switch(skn_jnt_ankle_ik_plg, skn_jnt_ankle_fk_plg, 
                            mdl_settings_ctrl, ikfk_plug, stretch_state_plug,
                            bc_ikfk_stretch, logic_ik_hdl,
                            fk_ctrl_grp, ik_ctrl_grp)
        #------
        # twist limb setup
            # cr twist curves & skn joints
        cv_upper, upper_cv_intermediate_pos_ls = self.cr_logic_curves("upper", self.dm.skel_pos_dict['hip'], self.dm.skel_pos_dict['knee'])
        cv_lower, lower_cv_intermediate_pos_ls = self.cr_logic_curves("lower", self.dm.skel_pos_dict['knee'], self.dm.skel_pos_dict['ankle'])
        
        sknUpper_jnt_chain = self.cr_skn_twist_joint_chain("upper", cv_upper, logic_jnt_list[0], 'zup')
        sknLower_jnt_chain = self.cr_skn_twist_joint_chain("lower", cv_lower, logic_jnt_list[1], 'zup')

            # shaper controls:
        unorganised_shaper_ctrl_list = ["ctrl_shp_bipedLeg_main_0_L", "ctrl_shp_bipedLeg_middle_0_L", 
                            "ctrl_shp_bipedLeg_upper_0_L", "ctrl_shp_bipedLeg_lower_0_L"]
        shaper_ctrl_list = self.organise_ctrl_shaper_list(unorganised_shaper_ctrl_list)
        shaper_ctrl_grp = self.group_ctrls(shaper_ctrl_list, "shaper")
        self.wire_shaper_ctrls(shaper_ctrl_list, logic_jnt_list, self.dm.ik_ctrl_list, shaper_plug, shaper_ctrl_grp)
        self.wire_shaper_ctrls_to_curves(shaper_ctrl_list, cv_upper, cv_lower, upper_cv_intermediate_pos_ls, lower_cv_intermediate_pos_ls, logic_jnt_list)

            # twist operations
        hdl_upper, hdl_lower = self.cr_twist_ik_spline(logic_grp, sknUpper_jnt_chain, sknLower_jnt_chain, cv_upper, cv_lower)
        self.wire_parent_skn_twist_joint_matrix(sknUpper_jnt_chain, sknLower_jnt_chain, self.dm.ik_ctrl_list[0], logic_jnt_list[1], self.dm.skel_pos_dict, self.dm.skel_rot_dict)
        fm_upp_global, fm_low_global = self.wire_skn_twist_joints_stretch(input_grp, sknUpper_jnt_chain, sknLower_jnt_chain, cv_upper, cv_lower)
        self.wire_skn_twist_joints_volume(input_grp, sknUpper_jnt_chain, sknLower_jnt_chain, cv_upper, cv_lower, stretch_vol_plug, fm_upp_global, fm_low_global, db_hip_kne, db_kne_akl)
        self.wire_rotations_on_twist_joints(self.dm.ik_ctrl_list[0], logic_jnt_list[0], logic_jnt_list[1], skn_jnt_ankle, hdl_upper, hdl_lower)

        # - - - - - - -
        # Phase 3 - finalising
        self.group_jnts_skn(joint_grp, [skn_jnt_ankle, skn_jnt_ball], [sknUpper_jnt_chain, sknLower_jnt_chain])
        self.group_logic_elements(logic_grp, logic_jnt_list, logic_ik_hdl, [cv_upper, cv_lower])

        self.parent_ik_ctrls_out(self.dm.ik_ctrl_list, self.dm.fk_ctrl_list)
        self.lock_ctrl_attributes(self.dm.fk_ctrl_list)
        
        self.output_group_setup(self.dm.output_hook_mtx_list)

        self.group_module(self.dm.mdl_nm, self.dm.unique_id, self.dm.side,
                    input_grp, output_grp, 
                    f"grp_ctrls_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}", 
                    f"grp_joints_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}", 
                    f"grp_logic_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}")
        
        cmds.setAttr("ctrl_bipedLeg_settings_0_L.Vis_Shapers", 0)