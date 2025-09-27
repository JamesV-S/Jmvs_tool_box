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

        self.root_input_grp, self.root_output_grp = self.cr_input_output_groups()

        self.group_ctrls(fk_ctrl_list, "fk")

        self.cr_utilitys(skeleton_pos_dict)
        
        print(f"fk_ctrl_ls = `{fk_ctrl_list}`")
        cog_offset_list = self.add_custom_attributes(fk_ctrl_ls=fk_ctrl_list)

        self.Wire_root_connections(global_scale_plg=GLOBAL_SCALE_PLG, base_mtx_plg=BASE_MTX_PLG, 
                                   hook_mtx_plg=HOOK_MTX_PLG, fk_ctrl_ls=fk_ctrl_list, 
                                   cog_offset_list=cog_offset_list)
        # # group the module
        # utils.group_module("root", self.root_input_grp, self.root_output_grp, grp_ctrl_name)
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
        
    
    def cr_input_output_groups(self):
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
        utils.add_float_attrib(outputs_grp, [self.global_scale_attr], [0.01, 999], True)
        cmds.setAttr(f"{outputs_grp}.{self.global_scale_attr}", 1, keyable=0, channelBox=0)
        utils.add_attr_if_not_exists(outputs_grp, f"ctrl_{self.mdl_nm}_centre_mtx", 
                                        'matrix', False)
        utils.add_attr_if_not_exists(outputs_grp, f"ctrl_{self.mdl_nm}_COG_mtx",
                                        'matrix', False)

        return inputs_grp, outputs_grp


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


    def cr_utilitys(self, skeleton_pos_dict):
        cog_x = skeleton_pos_dict["COG"][0]
        cog_y = skeleton_pos_dict["COG"][1]
        cog_z = skeleton_pos_dict["COG"][2]
        
        print(f"cog_x: {cog_x}, cog_y: {cog_y}, cog_z: {cog_z}")
        # cog_x = cog_pos[0]
        # cog_y = cog_pos[1]
        # cog_z = cog_pos[2]
        cog_mtxVal = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        cog_x, cog_y, cog_z, 1
        ]
        minus_cog_mtxVal = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        -cog_x, -cog_y, -cog_z, 1
        ]
        
        # return cog_mtxVal, minus_cog_mtxVal

        # create utility's
        self.fm_global_scale = f"FM_root_{self.global_scale_attr}"
        utils.cr_node_if_not_exists(1, "floatMath", self.fm_global_scale, {"operation":2})
            # 4 MM
        self.MM_centre = f"MM_ctrl_centre"
        self.MM_cog = f"MM_ctrl_cog"
        self.MM_centre_outputs = f"MM_ctrl_centre_outputs"
        self.MM_cog_outputs = f"MM_ctrl_cog_outputs"
        MM_list = [self.MM_centre, self.MM_cog, self.MM_centre_outputs, self.MM_cog_outputs]
        for node_name in MM_list:
            utils.cr_node_if_not_exists(1, "multMatrix", node_name)
        cmds.setAttr(f"{self.MM_cog}{utils.Plg.mtx_ins[0]}", *cog_mtxVal, type="matrix")
        cmds.setAttr(f"{self.MM_cog_outputs}{utils.Plg.mtx_ins[0]}", *minus_cog_mtxVal, type="matrix")

            # Cog offset ctrls
        self.MD_cog_ofs = f"MD_ctrl_cog_offset"
        self.MD_rev_cog_ofs = f"MD_ctrl_cog_offset_rev"
        self.CM_cog_ofs = f"CM_ctrl_cog_offset"
        self.CM_inv_cog_ofs = f"CM_inv_ctrl_cog_offset"
        utils.cr_node_if_not_exists(1, "multiplyDivide", self.MD_cog_ofs, {"input1Y" : cog_y})
        utils.cr_node_if_not_exists(1, "multiplyDivide", self.MD_rev_cog_ofs, {"input1X":-1, "input1Y":-1, "input1Z":-1})
        utils.cr_node_if_not_exists(1, "composeMatrix", self.CM_cog_ofs)
        utils.cr_node_if_not_exists(1, "composeMatrix", self.CM_inv_cog_ofs)
        if cog_x == 0:
            cmds.setAttr(f"{self.MD_cog_ofs}.input1X", 10)
        else:
            cmds.setAttr(f"{self.MD_cog_ofs}.input1X", cog_x)
        if cog_z == 0:
            cmds.setAttr(f"{self.MD_cog_ofs}.input1Z", 10)
        else:
            cmds.setAttr(f"{self.MD_cog_ofs}.input1Z", cog_z)

    
    def add_custom_attributes(self, fk_ctrl_ls):
        root_ctrl = fk_ctrl_ls[0]
        cog_ctrl = fk_ctrl_ls[-1]
        # add Root attributes
        utils.add_locked_attrib(root_ctrl, ["Attributes"])
        utils.add_float_attrib(root_ctrl, [self.global_scale_attr], [0.01, 999], True)
        cmds.setAttr(f"{root_ctrl}.{self.global_scale_attr}", 1)

        # add COG attributes
        cog_offset_list = ["Offset_pivot_X", "Offset_pivot_Y", "Offset_pivot_Z"]
        utils.add_locked_attrib(cog_ctrl, ["Cog_Pivot"])
        utils.add_float_attrib(cog_ctrl, [cog_offset_list[0]], [0, 1], False)
        utils.add_float_attrib(cog_ctrl, [cog_offset_list[1]], [0, 1], False)
        utils.add_float_attrib(cog_ctrl, [cog_offset_list[2]], [0, 1], False)
        cmds.setAttr(f"{cog_ctrl}.{cog_offset_list[1]}", 1)

        return cog_offset_list
    
    
    def Wire_root_connections(self, global_scale_plg, base_mtx_plg, hook_mtx_plg, fk_ctrl_ls, cog_offset_list):
        root_ctrl, centre_ctrl, cog_ctrl = fk_ctrl_ls
        # connections
        utils.connect_attr(f"{self.root_input_grp}.{self.global_scale_attr}", f"{self.fm_global_scale}{utils.Plg.flt_A}")
        utils.connect_attr(f"{root_ctrl}.{self.global_scale_attr}", f"{self.fm_global_scale}{utils.Plg.flt_B}")

        # root
        for x in range(3):
            utils.connect_attr(f"{self.fm_global_scale}{utils.Plg.out_flt}", f"{root_ctrl}.scale{utils.Plg.axis[x]}")

        # centre
        utils.connect_attr(f"{root_ctrl}{utils.Plg.wld_mtx_plg}", f"{self.MM_centre}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{self.MM_centre}{utils.Plg.mtx_sum_plg}", f"{centre_ctrl}{utils.Plg.opm_plg}")

        # cog
        utils.connect_attr(f"{centre_ctrl}{utils.Plg.wld_mtx_plg}", f"{self.MM_cog}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{self.MM_cog}{utils.Plg.mtx_sum_plg}", f"{cog_ctrl}{utils.Plg.opm_plg}")

        # centre outputs
        utils.connect_attr(f"{centre_ctrl}{utils.Plg.wld_mtx_plg}", f"{self.MM_centre_outputs}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{cog_ctrl}{utils.Plg.wld_mtx_plg}", f"{self.MM_cog_outputs}{utils.Plg.mtx_ins[1]}")

        # cog offset option]
        for x in range(3):
            utils.connect_attr(f"{cog_ctrl}.{cog_offset_list[x]}", f"{self.MD_cog_ofs}{utils.Plg.input2_val[x]}")
        utils.connect_attr(f"{self.MD_cog_ofs}{utils.Plg.output_plg}", f"{self.CM_cog_ofs}{utils.Plg.inputT_plug}")
        utils.connect_attr(f"{self.CM_cog_ofs}{utils.Plg.out_mtx_plg}", f"{self.MM_cog}{utils.Plg.mtx_ins[0]}")
            # reverse
        utils.connect_attr(f"{self.MD_cog_ofs}{utils.Plg.output_plg}", f"{self.MD_rev_cog_ofs}.input2")
        utils.connect_attr(f"{self.MD_rev_cog_ofs}{utils.Plg.output_plg}", f"{self.CM_inv_cog_ofs}{utils.Plg.inputT_plug}")
        utils.connect_attr(f"{self.CM_inv_cog_ofs}{utils.Plg.out_mtx_plg}", f"{self.MM_cog_outputs}{utils.Plg.mtx_ins[0]}")

        # cog outputs
        # utils.connect_attr(f"{self.fm_global_scale}{utils.Plg.out_flt}", f"{self.root_output_grp}.{self.global_scale_attr}")
        # utils.connect_attr(f"{self.MM_centre_outputs}{utils.Plg.mtx_sum_plg}", f"{self.root_output_grp}.ctrl_centre_mtx")
        # utils.connect_attr(f"{self.MM_cog_outputs}{utils.Plg.mtx_sum_plg}", f"{self.root_output_grp}.ctrl_cog_mtx")
        
        utils.connect_attr(f"{self.fm_global_scale}{utils.Plg.out_flt}", global_scale_plg)
        utils.connect_attr(f"{self.MM_centre_outputs}{utils.Plg.mtx_sum_plg}", base_mtx_plg)
        utils.connect_attr(f"{self.MM_cog_outputs}{utils.Plg.mtx_sum_plg}", hook_mtx_plg)
        
        
skeleton_dict = {
    "skel_pos":{
        "root":[0.0, 0.0, 0.0],
        "centre": [0.0, 0.0, 0.0],
        "COG":[0.0, 147.0, 0.0]
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
        "ctrl_fk_root_COG_0_M":[0.0, 147.0, 0.0]
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