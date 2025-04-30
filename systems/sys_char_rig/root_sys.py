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

class root_system():
    def __init__(self, cog_pos):
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
        # cog matrix val
        self.cog_x = cog_pos[0]
        self.cog_y = cog_pos[1]
        self.cog_z = cog_pos[2]
        self.cog_mtxVal = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        self.cog_x, self.cog_y, self.cog_z, 1
        ]
        self.minus_cog_mtxVal = [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        -self.cog_x, -self.cog_y, -self.cog_z, 1
        ]

        self.offset_piv__attr_list = ["Offset_pivot_X", "Offset_pivot_Y", "Offset_pivot_Z"]

        # ctrl creation
        self.root_ctrl, self.centre_ctrl, self.cog_ctrl, grp_ctrl_name = self.cr_root_ctrls()
        self.root_input_grp, self.root_output_grp = self.cr_input_outputs_nodes()
        self.cr_utilitys()
        self.add_custom_attributes()
        self.Wire_root_connections()
        # group the module
        utils.group_module("root", self.root_input_grp, self.root_output_grp, grp_ctrl_name)


    '''''' 
    def cr_root_ctrls(self):
        root_ctrl = f"ctrl_root"
        centre_ctrl = f"ctrl_centre"
        cog_ctrl = f"ctrl_cog"

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
        grp_ctrl_name = f"grp_ctrls_root"
        cmds.group(n=grp_ctrl_name, em=1)
        cmds.parent(root_ctrl, centre_ctrl, cog_ctrl, grp_ctrl_name)

        return root_ctrl, centre_ctrl, cog_ctrl, grp_ctrl_name
        

    def cr_input_outputs_nodes(self):
        # create input & output groups
        root_input_grp = f"grp_rootInputs"
        root_output_grp = f"grp_rootOutputs"
        utils.cr_node_if_not_exists(0, "transform", root_input_grp)
        utils.cr_node_if_not_exists(0, "transform", root_output_grp)
        
        return root_input_grp, root_output_grp
    
    def cr_utilitys(self):
        # create utility's
        self.fm_global_scale = f"FM_root_globalScale"
        utils.cr_node_if_not_exists(1, "floatMath", self.fm_global_scale, {"operation":2})
            # 4 MM
        self.MM_centre = f"MM_ctrl_centre"
        self.MM_cog = f"MM_ctrl_cog"
        self.MM_centre_outputs = f"MM_ctrl_centre_outputs"
        self.MM_cog_outputs = f"MM_ctrl_cog_outputs"
        MM_list = [self.MM_centre, self.MM_cog, self.MM_centre_outputs, self.MM_cog_outputs]
        for node_name in MM_list:
            utils.cr_node_if_not_exists(1, "multMatrix", node_name)
        cmds.setAttr(f"{self.MM_cog}{utils.Plg.mtx_ins[0]}", *self.cog_mtxVal, type="matrix")
        cmds.setAttr(f"{self.MM_cog_outputs}{utils.Plg.mtx_ins[0]}", *self.minus_cog_mtxVal, type="matrix")

            # Cog offset ctrls
        self.MD_cog_ofs = f"MD_ctrl_cog_offset"
        self.MD_rev_cog_ofs = f"MD_ctrl_cog_offset_rev"
        self.CM_cog_ofs = f"CM_ctrl_cog_offset"
        self.CM_inv_cog_ofs = f"CM_inv_ctrl_cog_offset"
        utils.cr_node_if_not_exists(1, "multiplyDivide", self.MD_cog_ofs, {"input1Y" : self.cog_y})
        utils.cr_node_if_not_exists(1, "multiplyDivide", self.MD_rev_cog_ofs, {"input1X":-1, "input1Y":-1, "input1Z":-1})
        utils.cr_node_if_not_exists(1, "composeMatrix", self.CM_cog_ofs)
        utils.cr_node_if_not_exists(1, "composeMatrix", self.CM_inv_cog_ofs)
        if self.cog_x == 0:
            cmds.setAttr(f"{self.MD_cog_ofs}.input1X", 10)
        else:
            cmds.setAttr(f"{self.MD_cog_ofs}.input1X", self.cog_x)
        if self.cog_z == 0:
            cmds.setAttr(f"{self.MD_cog_ofs}.input1Z", 10)
        else:
            cmds.setAttr(f"{self.MD_cog_ofs}.input1Z", self.cog_z)

    
    def add_custom_attributes(self):
        # add custom attributes
            # Input & Output groups
        utils.add_float_attrib(self.root_input_grp, ["globalScale"], [0.01, 999], True) 
        utils.add_float_attrib(self.root_output_grp, ["globalScale"], [0.01, 999], True)
        cmds.setAttr(f"{self.root_input_grp}.globalScale", 1, keyable=0, channelBox=0)
        cmds.setAttr(f"{self.root_output_grp}.globalScale", 1, keyable=0, channelBox=0)
        utils.add_attr_if_not_exists(self.root_output_grp, "ctrl_centre_mtx", 'matrix', False)
        utils.add_attr_if_not_exists(self.root_output_grp, "ctrl_cog_mtx", 'matrix', False)
            # ctrls
        utils.add_locked_attrib(self.root_ctrl, ["Attributes"])
        utils.add_float_attrib(self.root_ctrl, ["globalScale"], [0.01, 999], True)
        cmds.setAttr(f"{self.root_ctrl}.globalScale", 1)
            # cog offset
        utils.add_locked_attrib(self.cog_ctrl, ["Cog_Pivot"])
        utils.add_float_attrib(self.cog_ctrl, [self.offset_piv__attr_list[0]], [0, 1], False)
        utils.add_float_attrib(self.cog_ctrl, [self.offset_piv__attr_list[1]], [0, 1], False)
        utils.add_float_attrib(self.cog_ctrl, [self.offset_piv__attr_list[2]], [0, 1], False)
        cmds.setAttr(f"{self.cog_ctrl}.{self.offset_piv__attr_list[1]}", 1)
    
    
    def Wire_root_connections(self):
        # connections
        utils.connect_attr(f"{self.root_input_grp}.globalScale", f"{self.fm_global_scale}{utils.Plg.flt_A}")
        utils.connect_attr(f"{self.root_ctrl}.globalScale", f"{self.fm_global_scale}{utils.Plg.flt_B}")

        # root
        for x in range(3):
            utils.connect_attr(f"{self.fm_global_scale}{utils.Plg.out_flt}", f"{self.root_ctrl}.scale{utils.Plg.axis[x]}")

        # centre
        utils.connect_attr(f"{self.root_ctrl}{utils.Plg.wld_mtx_plg}", f"{self.MM_centre}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{self.MM_centre}{utils.Plg.mtx_sum_plg}", f"{self.centre_ctrl}{utils.Plg.opm_plg}")

        # cog
        utils.connect_attr(f"{self.centre_ctrl}{utils.Plg.wld_mtx_plg}", f"{self.MM_cog}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{self.MM_cog}{utils.Plg.mtx_sum_plg}", f"{self.cog_ctrl}{utils.Plg.opm_plg}")

        # centre outputs
        utils.connect_attr(f"{self.centre_ctrl}{utils.Plg.wld_mtx_plg}", f"{self.MM_centre_outputs}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{self.cog_ctrl}{utils.Plg.wld_mtx_plg}", f"{self.MM_cog_outputs}{utils.Plg.mtx_ins[1]}")

        # cog offset option]
        for x in range(3):
            utils.connect_attr(f"{self.cog_ctrl}.{self.offset_piv__attr_list[x]}", f"{self.MD_cog_ofs}{utils.Plg.input2_val[x]}")
        utils.connect_attr(f"{self.MD_cog_ofs}{utils.Plg.output_plg}", f"{self.CM_cog_ofs}{utils.Plg.inputT_plug}")
        utils.connect_attr(f"{self.CM_cog_ofs}{utils.Plg.out_mtx_plg}", f"{self.MM_cog}{utils.Plg.mtx_ins[0]}")
            # reverse
        utils.connect_attr(f"{self.MD_cog_ofs}{utils.Plg.output_plg}", f"{self.MD_rev_cog_ofs}.input2")
        utils.connect_attr(f"{self.MD_rev_cog_ofs}{utils.Plg.output_plg}", f"{self.CM_inv_cog_ofs}{utils.Plg.inputT_plug}")
        utils.connect_attr(f"{self.CM_inv_cog_ofs}{utils.Plg.out_mtx_plg}", f"{self.MM_cog_outputs}{utils.Plg.mtx_ins[0]}")

        # cog outputs
        utils.connect_attr(f"{self.fm_global_scale}{utils.Plg.out_flt}", f"{self.root_output_grp}.globalScale")
        utils.connect_attr(f"{self.MM_centre_outputs}{utils.Plg.mtx_sum_plg}", f"{self.root_output_grp}.ctrl_centre_mtx")
        utils.connect_attr(f"{self.MM_cog_outputs}{utils.Plg.mtx_sum_plg}", f"{self.root_output_grp}.ctrl_cog_mtx")

    ''''''
# -----------------------------------------------------------------------------
cog_position_dict = {
        "root": [0, 0, 0],
        "COG": [0, 150, 0]
        }
cog_pos = cog_position_dict["COG"]
print(cog_pos)
root_system(cog_pos)