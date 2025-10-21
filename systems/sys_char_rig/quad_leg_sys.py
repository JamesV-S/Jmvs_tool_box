
import importlib
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
from Jmvs_tool_box.systems.sys_char_rig import quad_leg_sys

importlib.reload(quad_leg_sys)
'''

class QuadLegSystem():
    def __init__(self, module_name, external_plg_dict, skeleton_dict, fk_dict, ik_dict, prim_axis, shaper_dict=None):
        skeleton_pos_dict = skeleton_dict["skel_pos"]
        skeleton_rot_dict = skeleton_dict["skel_rot"]
        self.fk_pos_dict = fk_dict["fk_pos"]
        self.fk_rot_dict = fk_dict["fk_rot"]
        self.ik_pos_dict = ik_dict["ik_pos"]
        self.ik_rot_dict = ik_dict["ik_rot"]
        self.prim_axis = prim_axis

        # return lists for storing control names!
        fk_ctrl_list = [key for key in self.fk_pos_dict.keys()]
        ik_ctrl_list = [key for key in self.ik_pos_dict.keys()]
        
        self.mdl_nm = module_name
        self.unique_id = fk_ctrl_list[0].split('_')[-2]
        self.side = fk_ctrl_list[0].split('_')[-1]
        
        # gather the number of values in the dict
        num_jnts = len(skeleton_pos_dict.keys())

        # Plg data from 'external_plg_dict'.
        GLOBAL_SCALE_PLG = f"{external_plg_dict['global_scale_grp']}.{external_plg_dict['global_scale_attr']}" # grp_Outputs_root_0_M.globalScale
        BASE_MTX_PLG = f"{external_plg_dict['base_plg_grp']}.{external_plg_dict['base_plg_atr']}" # grp_Outputs_root_0_M.ctrl_centre_mtx
        HOOK_MTX_PLG = f"{external_plg_dict['hook_plg_grp']}.{external_plg_dict['hook_plg_atr']}" # grp_Outputs_spine_0_M.ctrl_spine_top_mtx
        self.global_scale_attr = external_plg_dict['global_scale_attr']
        
        # Input & Output grp setup
        inputs_grp, outputs_grp = self.cr_input_output_groups()
        self.add_outputs_matrix_attr(outputs_grp, ["sknWrist", "twistWrist"])
        if cmds.objExists(external_plg_dict['global_scale_grp']):
            self.wire_inputs_grp(inputs_grp, GLOBAL_SCALE_PLG, BASE_MTX_PLG, HOOK_MTX_PLG)

        # Group the controls!
        fk_ctrl_grp = self.group_ctrls(fk_ctrl_list, "fk")
        ik_ctrl_grp = self.group_ctrls(ik_ctrl_list, "ik")

        # # cr skn joints
        # skn_jnt_clav, skn_jnt_wrist = self.cr_jnt_skn_start_end(self.ik_pos_dict)
        
        # # cr twist curves & skn joints
        # cv_upper, upper_cv_intermediate_pos_ls = self.cr_logic_curves("upper", skeleton_pos_dict['shoulder'], skeleton_pos_dict['elbow'])
        # cv_lower, lower_cv_intermediate_pos_ls = self.cr_logic_curves("lower", skeleton_pos_dict['elbow'], skeleton_pos_dict['wrist'])
        
        # sknUpper_jnt_chain = self.cr_skn_twist_joint_chain("upper", cv_upper,
        #                                                    skeleton_pos_dict['shoulder'], 
        #                                                    skeleton_pos_dict['elbow'])
        # sknLower_jnt_chain = self.cr_skn_twist_joint_chain("lower", cv_lower,
        #                                                    skeleton_pos_dict['elbow'], 
        #                                                    skeleton_pos_dict['wrist'])
        # self.group_jnts_skn([skn_jnt_clav, skn_jnt_wrist], [sknUpper_jnt_chain, sknLower_jnt_chain])
        
        # self.add_custom_input_attr(inputs_grp)

        # # wire connections
        # self.wire_clav_armRt_setup(inputs_grp, [ik_ctrl_list[0], ik_ctrl_list[1]], skn_jnt_clav, self.ik_pos_dict, self.ik_rot_dict)
        
        # blend_armRoot_node = self.wire_fk_ctrl_setup(inputs_grp, ik_ctrl_list[1], fk_ctrl_list, self.fk_pos_dict, self.fk_rot_dict)
        # logic_jnt_list = self.cr_logic_rig_joints(fk_ctrl_list, self.fk_pos_dict, self.fk_rot_dict)
        
        # self.d_shld_wrist, self.d_shld_elb, self.d_elb_wrist = self.logic_jnt_distances(self.fk_pos_dict)
        # self.wire_fk_ctrl_stretch_setup(fk_ctrl_list, self.fk_pos_dict)
        # self.wire_fk_ctrl_to_logic_joint(blend_armRoot_node, fk_ctrl_list, logic_jnt_list)

        # self.wire_ctrl_ik_wrist(inputs_grp, ik_ctrl_list)

        # spine_top_name = f"ctrl_ik_spine_spine_top_{external_plg_dict['hook_plg_grp'].split('_')[-2]}_{external_plg_dict['hook_plg_grp'].split('_')[-1]}"
        # # temp_spine_name = f"ctrl_ik_spine_top"
        
        # self.wire_ctrl_ik_elbow(inputs_grp, ik_ctrl_list, spine_top_name)
        
        # bc_ikfk_stretch, logic_ik_hdl = self.wire_ik_logic_elements(inputs_grp, logic_jnt_list, ik_ctrl_list)
        # self.group_logic_elements(logic_jnt_list, logic_ik_hdl, [cv_upper, cv_lower])

        # skn_jnt_wrist_ik_plg, skn_jnt_wrist_fk_plg = self.wire_jnt_skn_wrist(skn_jnt_wrist, logic_jnt_list, fk_ctrl_list, ik_ctrl_list)

        # mdl_settings_ctrl, ikfk_plug, stretch_state_plug, stretch_vol_plug, shaper_plug  = self.cr_mdl_setting_ctrl(skn_jnt_wrist, ik_ctrl_list)
        
        # self.wire_IKFK_switch(skn_jnt_wrist_ik_plg, skn_jnt_wrist_fk_plg, 
        #                     mdl_settings_ctrl, ikfk_plug, stretch_state_plug,
        #                     bc_ikfk_stretch, logic_ik_hdl,
        #                     fk_ctrl_grp, ik_ctrl_grp)
        
        # '''TEMP shaper_ctrl_list'''
        # unorganised_shaper_ctrl_list = ["ctrl_shp_bipedArm_main_0_L", "ctrl_shp_bipedArm_middle_0_L", 
        #                     "ctrl_shp_bipedArm_upper_0_L", "ctrl_shp_bipedArm_lower_0_L"]
        # shaper_ctrl_list = self.organise_ctrl_shaper_list(unorganised_shaper_ctrl_list)
        # shaper_ctrl_grp = self.group_ctrls(shaper_ctrl_list, "shaper")
        # self.wire_shaper_ctrls(shaper_ctrl_list, logic_jnt_list, ik_ctrl_list, shaper_plug, shaper_ctrl_grp)

        # self.wire_shaper_ctrls_to_curves(shaper_ctrl_list, cv_upper, cv_lower, upper_cv_intermediate_pos_ls, lower_cv_intermediate_pos_ls, logic_jnt_list)

        # hdl_upper, hdl_lower = self.cr_twist_ik_spline(sknUpper_jnt_chain, sknLower_jnt_chain, cv_upper, cv_lower)
        # self.wire_parent_skn_twist_joint_matrix(sknUpper_jnt_chain, sknLower_jnt_chain, ik_ctrl_list[1], logic_jnt_list)
        # fm_upp_global, fm_low_global = self.wire_skn_twist_joints_stretch(inputs_grp, sknUpper_jnt_chain, sknLower_jnt_chain, cv_upper, cv_lower)
        # self.wire_skn_twist_joints_volume(inputs_grp, sknUpper_jnt_chain, sknLower_jnt_chain, cv_upper, cv_lower, stretch_vol_plug, fm_upp_global, fm_low_global)
        # self.wire_rotations_on_twist_joints(logic_jnt_list, skn_jnt_wrist, ik_ctrl_list[1], hdl_upper, hdl_lower)

        # self.parent_ik_ctrls_out(ik_ctrl_list)
        # self.wire_pv_reference_curve(ik_ctrl_list[2], logic_jnt_list[1], ik_ctrl_grp)
        # self.lock_ctrl_attributes(fk_ctrl_list)

        # self.output_group_setup(outputs_grp, [skn_jnt_wrist, sknLower_jnt_chain[-1]], ["sknWrist", "twistWrist"])

        # # group the module
        # utils.group_module(module_name=module_name, unique_id=self.unique_id, 
        #                    side=self.side ,input_grp=inputs_grp, output_grp=outputs_grp, 
        #                    ctrl_grp=f"grp_ctrls_{self.mdl_nm}_{self.unique_id}_{self.side}", 
        #                    joint_grp=f"grp_joints_{self.mdl_nm}_{self.unique_id}_{self.side}", 
        #                    logic_grp=f"grp_logic_{self.mdl_nm}_{self.unique_id}_{self.side}")
    

    def cr_input_output_groups(self, output_global=False):
        inputs_grp = f"grp_Inputs_{self.mdl_nm}_{self.unique_id}_{self.side}"
        outputs_grp = f"grp_Outputs_{self.mdl_nm}_{self.unique_id}_{self.side}"
        utils.cr_node_if_not_exists(0, "transform", inputs_grp)
        utils.cr_node_if_not_exists(0, "transform", outputs_grp)

        # Input grp
        utils.add_float_attrib(inputs_grp, [self.global_scale_attr], [0.01, 999], True)
        cmds.setAttr(f"{inputs_grp}.{self.global_scale_attr}", 1, keyable=0, channelBox=0)
        utils.add_attr_if_not_exists(inputs_grp, "base_mtx", 'matrix', False)
        utils.add_attr_if_not_exists(inputs_grp, "hook_mtx", 'matrix', False)

        if output_global:
            utils.add_float_attrib(outputs_grp, [self.global_scale_attr], [0.01, 999], True)
            cmds.setAttr(f"{outputs_grp}.{self.global_scale_attr}", 1, keyable=0, channelBox=0)

        return inputs_grp, outputs_grp
    

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
            utils.add_attr_if_not_exists(outputs_grp, f"mtx_{self.mdl_nm}_{mtx_name}", 
                                    'matrix', False) # for upper body module to follow


    def wire_inputs_grp(self, inputs_grp, global_scale_plg, base_mtx_plg, hook_mtx_plg):
        # connect the global scale
        utils.connect_attr(global_scale_plg, f"{inputs_grp}.globalScale")
        # connect the base plug
        utils.connect_attr(base_mtx_plg, f"{inputs_grp}.base_mtx")
        # connect the hook plug
        utils.connect_attr(hook_mtx_plg, f"{inputs_grp}.hook_mtx")


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
    

#-----------------------

'''
'ex_external_plg_dict' is an important dictionary that should be intiilaised by 
a seprate script just used for creating attributes. In the same script this 
dctionary is sent to the databaase!
'''
ex_external_plg_dict = {
    "global_scale_grp":"grp_Outputs_root_0_M",
    "global_scale_attr":"globalScale",
    "base_plg_grp":"grp_Outputs_root_0_M",
    "base_plg_atr":"mtx_root_ctrlCentre",
    "hook_plg_grp":"grp_Outputs_spine_0_M", 
    "hook_plg_atr":"mtx_spine_bottom"
    }
# Do I need 'skeleton_dict' arg?
ex_skeleton_dict = {
    "skel_pos":{
        'hip': [9.427100479531633, 73.17778605595966, -41.283461318628305], 
        'knee': [10.34594475222716, 45.31456132216192, -30.942341550811438], 
        'calf': [8.381440943844233, 20.335971998048286, -47.07023669736204], 
        'ankle': [8.17389538574193, 5.737959787060513, -44.06889043484146], 
        'ball': [9.241848087805904, 4.592991784562416, -38.86664582300684], 
        'end': [10.15430720015248, -0.06079745326662156, -34.735633685929784]
    },
    "skel_rot":{
        'hip': [84.952120068356, -20.35168168884181, -88.11124419294283], 
        'knee': [83.51738586220513, 32.768618974963445, -94.49691374978813], 
        'calf': [81.68986907996045, -11.616952223402174, -90.81454127018631], 
        'ankle': [46.74101795216688, -73.24979121317386, -46.99323518291281], 
        'ball': [74.81562730475041, -41.05850090352503, -78.90685296138632], 
        'end': [74.81562730475041, -41.05850090352503, -78.90685296138632]
    }

} 

ex_fk_dict = {
    "fk_pos":{
        'ctrl_fk_quadLeg_hip_0_L':[0.0, 0.0, 0.0], 
        'ctrl_fk_quadLeg_knee_0_L':[0.0, 0.0, 0.0],
        'ctrl_fk_quadLeg_calf_0_L':[0.0, 0.0, 0.0],
        'ctrl_fk_quadLeg_ankle_0_L':[0.0, 0.0, 0.0],
        'ctrl_fk_quadLeg_ball_0_L':[0.0, 0.0, 0.0]
        },
    "fk_rot":{
        'ctrl_fk_quadLeg_hip_0_L':[0.0, 0.0, 0.0], 
        'ctrl_fk_quadLeg_knee_0_L':[0.0, 0.0, 0.0],
        'ctrl_fk_quadLeg_calf_0_L':[0.0, 0.0, 0.0],
        'ctrl_fk_quadLeg_ankle_0_L':[0.0, 0.0, 0.0],
        'ctrl_fk_quadLeg_ball_0_L':[0.0, 0.0, 0.0]
        }
    }
ex_ik_dict = {
    "ik_pos":{
        'ctrl_ik_quadLeg_hip_0_L':[0.0, 0.0, 0.0],
        'ctrl_ik_quadLeg_knee_0_L':[0.0, 0.0, 0.0],
        'ctrl_ik_quadLeg_calf_0_L':[0.0, 0.0, 0.0],
        'ctrl_ik_quadLeg_ankle_0_L':[0.0, 0.0, 0.0],
        },
    "ik_rot":{
        'ctrl_ik_quadLeg_hip_0_L':[0.0, 0.0, 0.0],
        'ctrl_ik_quadLeg_knee_0_L':[0.0, 0.0, 0.0],
        'ctrl_ik_quadLeg_calf_0_L':[0.0, 0.0, 0.0],
        'ctrl_ik_quadLeg_ankle_0_L':[0.0, 0.0, 0.0],
        }
    }

ex_shaper_dict = {

}

QuadLegSystem("quadLeg", ex_external_plg_dict, ex_skeleton_dict, ex_fk_dict, ex_ik_dict, "X")

pos = {
    'hip': [9.427100479531633, 73.17778605595966, -41.283461318628305], 
    'knee': [10.34594475222716, 45.31456132216192, -30.942341550811438], 
    'calf': [8.381440943844233, 20.335971998048286, -47.07023669736204], 
    'ankle': [8.17389538574193, 5.737959787060513, -44.06889043484146], 
    'ball': [9.241848087805904, 4.592991784562416, -38.86664582300684], 
    'end': [10.15430720015248, -0.06079745326662156, -34.735633685929784]
    }


rot = {
    'hip': [84.952120068356, -20.35168168884181, -88.11124419294283], 
    'knee': [83.51738586220513, 32.768618974963445, -94.49691374978813], 
    'calf': [81.68986907996045, -11.616952223402174, -90.81454127018631], 
    'ankle': [46.74101795216688, -73.24979121317386, -46.99323518291281], 
    'ball': [74.81562730475041, -41.05850090352503, -78.90685296138632], 
    'end': [74.81562730475041, -41.05850090352503, -78.90685296138632]
    }


ik_pos =  {
    'ctrl_ik_quadLeg_knee_0_L': [12.659764496445849, 42.94222489523101, -9.697506258361376],
    'ctrl_ik_quadLeg_calf_0_L': [8.38144094384424, 20.335971998048272, -47.07023669736192],
    'ctrl_ik_quadLeg_ankle_0_L': [8.173895385741938, 5.737959787060494, -44.068890434841336]
    }

ik_rot =  {
    'ctrl_ik_quadLeg_knee_0_L': [134.9261066953834, -81.13417480632245, -45.715423170008286],
    'ctrl_ik_quadLeg_calf_0_L': [0.0, 11.136004369497108, 0.0],
    'ctrl_ik_quadLeg_ankle_0_L': [0.0, 11.136004369497108, 0.0]
    }

