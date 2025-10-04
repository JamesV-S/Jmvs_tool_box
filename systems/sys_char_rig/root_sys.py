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
from Jmvs_tool_box.systems.sys_char_rig import root_sys

importlib.reload(root_sys)
'''

class root_system():
    def __init__(self, module_name, external_plg_dict, skeleton_dict, fk_dict, ik_dict, prim_axis):
        '''
        With this MM system, there's opportunity to add dynamic pivots to the cog's 
        ctrl for different types of posing around the character's centre of gravity

        3 controls: 
            ctrl_general (Main root > attr = GlobalScale)
            ctrl_centre (Char piv)
            ctrl_root (works exactly like COG)

        2 Important groups:
            grp_rootInputs
            grp_rootOutputs
        '''
        skeleton_pos_dict = skeleton_dict["skel_pos"]
        skeleton_rot_dict = skeleton_dict["skel_rot"]
        self.fk_pos_dict = fk_dict["fk_pos"]
        self.fk_rot_dict = fk_dict["fk_rot"]
        self.ik_pos_dict = ik_dict["ik_pos"]
        self.ik_rot_dict = ik_dict["ik_rot"]
        
        fk_ctrl_list = [key for key in self.fk_pos_dict.keys()]
        ik_ctrl_list = [key for key in self.ik_pos_dict.keys()]

        self.mdl_nm = module_name
        self.unique_id = fk_ctrl_list[0].split('_')[-2]
        self.side = fk_ctrl_list[0].split('_')[-1]

        GLOBAL_SCALE_PLG = f"{external_plg_dict['global_scale_grp']}.{external_plg_dict['global_scale_attr']}"
        BASE_MTX_PLG = f"{external_plg_dict['base_plg_grp']}.{external_plg_dict['base_plg_atr']}"
        HOOK_MTX_PLG = f"{external_plg_dict['hook_plg_grp']}.{external_plg_dict['hook_plg_atr']}"
        self.global_scale_attr = external_plg_dict['global_scale_attr']
        #----------------------------------------------------------------------
        self.cr_root_ctrls("fk")
        #----------------------------------------------------------------------

        self.root_input_grp, self.root_output_grp = self.cr_input_output_groups(True)
        self.add_outputs_matrix_attr(self.root_output_grp, ["centre", "COG"])
        self.group_ctrls(fk_ctrl_list, "fk")

        self.wire_root_setup(fk_ctrl_list, skeleton_pos_dict, skeleton_rot_dict)
        self.output_group_setup(GLOBAL_SCALE_PLG, BASE_MTX_PLG, HOOK_MTX_PLG, fk_ctrl_list[0], fk_ctrl_list[1], fk_ctrl_list[-1])
        
        # # group the module
        utils.group_module(module_name="root", unique_id=self.unique_id, side=self.side,
                           input_grp=self.root_input_grp, output_grp=self.root_output_grp,
                           ctrl_grp=f"grp_ctrls_{self.mdl_nm}_{self.unique_id}_{self.side}", 
                           joint_grp=None,
                           logic_grp=None)


     
    def cr_root_ctrls(self, pref):
        root_ctrl = f"ctrl_{pref}_{self.mdl_nm}_root_{self.unique_id}_{self.side}"
        centre_ctrl = f"ctrl_{pref}_{self.mdl_nm}_centre_{self.unique_id}_{self.side}"
        cog_ctrl = f"ctrl_{pref}_{self.mdl_nm}_COG_{self.unique_id}_{self.side}"

        root_import_ctrl = cr_ctrl.CreateControl(type="root", name=root_ctrl)
        root_import_ctrl.retrun_ctrl()
        centre_import_ctrl = cr_ctrl.CreateControl(type="circle", name=centre_ctrl)
        centre_import_ctrl.retrun_ctrl()
        cog_import_ctrl = cr_ctrl.CreateControl(type="cog", name=cog_ctrl)
        cog_import_ctrl.retrun_ctrl()
        cmds.setAttr(f"{centre_ctrl}.rotateZ", 90)
        for x in range(3):
            cmds.setAttr(f"{centre_ctrl}.scale{utils.Plg.axis[x]}", 5.5)
        cmds.makeIdentity(centre_ctrl, a=1, t=1, r=1, s=1, n=0, pn=1)
            # Colour ctrls
        utils.colour_root_control(root_ctrl)
        cmds.setAttr(f"{centre_ctrl}.overrideEnabled", 1)
        cmds.setAttr(f"{centre_ctrl}.overrideColor", 25)
        utils.colour_COG_control(cog_ctrl)
        for axis in ['x', 'y', 'z']:
                cmds.setAttr(f"{root_ctrl}.s{axis}", lock=0, keyable=0, cb=0)
                cmds.setAttr(f"{centre_ctrl}.s{axis}", lock=1, keyable=0, cb=0)
                cmds.setAttr(f"{cog_ctrl}.s{axis}", lock=1, keyable=0, cb=0)
        
    
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

        # Output grp - for hand module to follow
        if output_global:
            print("Running add global scale to output grp")
            utils.add_float_attrib(outputs_grp, [self.global_scale_attr], [0.01, 999], True)
            cmds.setAttr(f"{outputs_grp}.{self.global_scale_attr}", 1, keyable=0, channelBox=0)

        return inputs_grp, outputs_grp


    def add_outputs_matrix_attr(self, outputs_grp, out_matrix_name_list):
        # Output grp
        for mtx_name in out_matrix_name_list:
            utils.add_attr_if_not_exists(outputs_grp, 
                                         f"ctrl_{self.mdl_nm}_{mtx_name}_mtx", 
                                        'matrix', False)


    def group_ctrls(self, ctrl_ls, ctrl_type):
        '''
        # Description:
            Creates control group for a list of ctrls.
        # Attributes:
            ctrl_ls (list): list of given controls.
            ctrl_type (string): Name for the ctrl_grp.
        # Returns:N/A
        '''
        print(f"ctrl_ls = `{ctrl_ls}`")
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


    def wire_root_setup(self, fk_ctrl_ls, skeleton_pos_dict, skeleton_rot_dict):
        root_ctrl, centre_ctrl, cog_ctrl = fk_ctrl_ls
        
        # add custom attr scale
        utils.add_float_attrib(root_ctrl, [self.global_scale_attr], [0.01, 999], True)
        cmds.setAttr(f"{root_ctrl}.{self.global_scale_attr}", 1, keyable=1, channelBox=1)

        # create utility's
        fm_global_scale = f"FM_root_{self.global_scale_attr}"
        utils.cr_node_if_not_exists(1, "floatMath", fm_global_scale, {"operation":2})
            # 4 MM
        MM_centre = f"MM_ctrl_centre"
        MM_cog = f"MM_ctrl_cog"
        
        MM_list = [MM_centre, MM_cog]
        for node_name in MM_list:
            utils.cr_node_if_not_exists(1, "multMatrix", node_name)

        # def cog_offset_ctrls():
            # self.MD_cog_ofs = f"MD_ctrl_cog_offset"
            # self.MD_rev_cog_ofs = f"MD_ctrl_cog_offset_rev"
            # self.CM_cog_ofs = f"CM_ctrl_cog_offset"
            # self.CM_inv_cog_ofs = f"CM_inv_ctrl_cog_offset"
            # utils.cr_node_if_not_exists(1, "multiplyDivide", self.MD_cog_ofs, {"input1Y" : cog_y})
            # utils.cr_node_if_not_exists(1, "multiplyDivide", self.MD_rev_cog_ofs, {"input1X":-1, "input1Y":-1, "input1Z":-1})
            # utils.cr_node_if_not_exists(1, "composeMatrix", self.CM_cog_ofs)
            # utils.cr_node_if_not_exists(1, "composeMatrix", self.CM_inv_cog_ofs)
            # if cog_x == 0:
            #     cmds.setAttr(f"{self.MD_cog_ofs}.input1X", 10)
            # else:
            #     cmds.setAttr(f"{self.MD_cog_ofs}.input1X", cog_x)
            # if cog_z == 0:
            #     cmds.setAttr(f"{self.MD_cog_ofs}.input1Z", 10)
            # else:
            #     cmds.setAttr(f"{self.MD_cog_ofs}.input1Z", cog_z)

        # connections
        utils.connect_attr(f"{self.root_input_grp}.{self.global_scale_attr}", f"{fm_global_scale}{utils.Plg.flt_A}")
        utils.connect_attr(f"{root_ctrl}.{self.global_scale_attr}", f"{fm_global_scale}{utils.Plg.flt_B}")

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

    
    def add_custom_attributes(self, fk_ctrl_ls):
        # add COG attributes
        cog_ctrl = fk_ctrl_ls[-1]
        cog_offset_list = ["Offset_pivot_X", "Offset_pivot_Y", "Offset_pivot_Z"]
        utils.add_locked_attrib(cog_ctrl, ["Cog_Pivot"])
        utils.add_float_attrib(cog_ctrl, [cog_offset_list[0]], [0, 1], False)
        utils.add_float_attrib(cog_ctrl, [cog_offset_list[1]], [0, 1], False)
        utils.add_float_attrib(cog_ctrl, [cog_offset_list[2]], [0, 1], False)
        cmds.setAttr(f"{cog_ctrl}.{cog_offset_list[1]}", 1)

        return cog_offset_list
    
    
    def output_group_setup(self, global_scale_plg, base_mtx_plg, hook_mtx_plg, ctrl_root, ctrl_centre, ctrl_cog):
        '''
        # Description:
            Connects the base and hook attributes on this module's output group 
            so another module's input group can have incoming plugs to allow it to follow!
        # Attributes:
            global_scale_plg (constant): base matrix plug
            base_mtx_plg (constant): base matrix plug
            hook_mtx_plg (constant): hook matrix plug
            ctrl_centre (str): centre control name .
            ctrl_cog (str): cog control name.
        # Returns: N/A
        '''
        # cr two multMatrixs
        # MM_output_top = f"MM_output_{ctrl_spine_top}"
        # MM_output_bot = f"MM_output_{ctrl_spine_bottom}"
        MM_output_centre = f"MM_output_{ctrl_centre}"
        MM_output_cog = f"MM_output_{ctrl_cog}"
            
            # cr the MM nodes
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_output_centre)
        utils.cr_node_if_not_exists(1, 'multMatrix', MM_output_cog)
        centre_inverse_mtx = cmds.getAttr(f"{ctrl_centre}{utils.Plg.wld_inv_mtx_plg}")
        cog_inverse_mtx = cmds.getAttr(f"{ctrl_cog}{utils.Plg.wld_inv_mtx_plg}")
        # Plugs - connect ik ctrl's to MM's
        cmds.setAttr(f"{MM_output_centre}{utils.Plg.mtx_ins[0]}", *centre_inverse_mtx, type="matrix")
        cmds.setAttr(f"{MM_output_cog}{utils.Plg.mtx_ins[0]}", *cog_inverse_mtx, type="matrix")
        utils.connect_attr(f"{ctrl_centre}{utils.Plg.wld_mtx_plg}", f"{MM_output_centre}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{ctrl_cog}{utils.Plg.wld_mtx_plg}", f"{MM_output_cog}{utils.Plg.mtx_ins[1]}")
        # Plugs - connect the MM to the spine output's attribs!  
        utils.connect_attr(f"{MM_output_centre}{utils.Plg.mtx_sum_plg}", base_mtx_plg)
        utils.connect_attr(f"{MM_output_cog}{utils.Plg.mtx_sum_plg}", hook_mtx_plg)
        utils.connect_attr(f"{ctrl_root}.{self.global_scale_attr}", global_scale_plg)
    
    
        
skeleton_dict = {
    "skel_pos":{
        "root":[0.0, 0.0, 0.0],
        "centre": [0.0, 0.0, 0.0],
        "COG":[0.0, 110.94277350608388, 3.4263498874367455]
    },
    "skel_rot":{
        "root":[0.0, 0.0, 0.0],
        "centre": [0.0, 0.0, 0.0],
        "COG":[0.0, 0.0, 0.0]
    }
}

fk_dict = {
    "fk_pos":{
        "ctrl_fk_root_root_0_M":[0.0, 0.0, 0.0],
        "ctrl_fk_root_centre_0_M": [0.0, 0.0, 0.0],
        "ctrl_fk_root_COG_0_M":[0.0, 110.94277350608388, 3.4263498874367455]
    },
    "fk_rot":{
        "ctrl_fk_root_root_0_M":[0.0, 0.0, 0.0],
        "ctrl_fk_root_centre_0_M": [0.0, 0.0, 0.0],
        "ctrl_fk_root_COG_0_M":[0.0, 0.0, 0.0]
    }
    }
ik_dict = {
    "ik_pos":{
        "ctrl_fk_root_root_0_M": False,
        "ctrl_fk_root_centre_0_M": False,
        "ctrl_fk_root_COG_0_M": False
    },
    "ik_rot":{
        "ctrl_fk_root_root_0_M": False,
        "ctrl_fk_root_centre_0_M": False,
        "ctrl_fk_root_COG_0_M": False
    }
    }

external_plg_dict = {
    "global_scale_grp":"grp_Outputs_root_0_M",
    "global_scale_attr":"globalScale",
    "base_plg_grp":"grp_Outputs_root_0_M",
    "base_plg_atr":"ctrl_root_centre_mtx",
    "hook_plg_grp":"grp_Outputs_root_0_M",
    "hook_plg_atr":"ctrl_root_COG_mtx"
    }

root_system("root", external_plg_dict, skeleton_dict, fk_dict, ik_dict, "Y")