import importlib
import maya.cmds as cmds
from systems import (
    utils
)
from systems.sys_char_rig import (
    cr_ctrl
)
importlib.reload(utils)
importlib.reload(cr_ctrl)

def root_system(cog_pos):
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
    cog_x = cog_pos[0]
    cog_y = cog_pos[1]
    cog_z = cog_pos[2]
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

    # plugs
    axis_plgs = ['X', 'Y', 'Z']
    mtx_in_plgs_ls = []
    for x in range(3):
        plg = f".matrixIn[{x}]"
        mtx_in_plgs_ls.append(plg)
    input2_val_plgs_ls = []
    for x in range(3):
        plg = f".input2{axis_plgs[x]}"
        input2_val_plgs_ls.append(plg)
    output_plg = ".output"
    inputT_plug = ".inputTranslate"
    mtx_sum_plg = ".matrixSum"
    wld_mtx_plg = ".worldMatrix[0]"
    wld_inv_mtx_plg = ".worldInverseMatrix[0]"
    inp_mtx_plg = ".inputMatrix"
    out_mtx_plg = ".outputMatrix"
    opm_plg = ".offsetParentMatrix"
    flt_A = ".floatA"
    flt_B = ".floatB"
    out_flt = ".outFloat"

    # ctrl creation
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
        cmds.setAttr(f"{centre_ctrl}.scale{axis_plgs[x]}", 5.5)
    cmds.makeIdentity(centre_ctrl, a=1, t=1, r=1, s=1, n=0, pn=1)
        # Colour ctrls
    utils.colour_root_control(root_ctrl)
    cmds.setAttr(f"{centre_ctrl}.overrideEnabled", 1)
    cmds.setAttr(f"{centre_ctrl}.overrideColor", 25)
    utils.colour_COG_control(cog_ctrl)

    # create input & output groups
    root_input_grp = f"grp_rootInputs"
    root_outputs_grp = f"grp_rootOutputs"
    utils.cr_node_if_not_exists(0, "transform", root_input_grp)
    utils.cr_node_if_not_exists(0, "transform", root_outputs_grp)

    # create utility's
    fm_global_scale = f"FM_root_globalScale"
    utils.cr_node_if_not_exists(1, "floatMath", fm_global_scale, {"operation":2})
        # 4 MM
    MM_centre = f"MM_ctrl_centre"
    MM_cog = f"MM_ctrl_cog"
    MM_centre_outputs = f"MM_ctrl_centre_outputs"
    MM_cog_outputs = f"MM_ctrl_cog_outputs"
    MM_list = [MM_centre, MM_cog, MM_centre_outputs, MM_cog_outputs]
    for node_name in MM_list:
        utils.cr_node_if_not_exists(1, "multMatrix", node_name)
    cmds.setAttr(f"{MM_cog}{mtx_in_plgs_ls[0]}", *cog_mtxVal, type="matrix")
    cmds.setAttr(f"{MM_cog_outputs}{mtx_in_plgs_ls[0]}", *minus_cog_mtxVal, type="matrix")

        # Cog offset ctrls
    MD_cog_ofs = f"MD_ctrl_cog_offset"
    rev_cog_ofs = f"R_ctrl_cog_offset"
    CM_cog_ofs = f"CM_ctrl_cog_offset"
    CM_inv_cog_ofs = f"CM_inv_ctrl_cog_offset"
    utils.cr_node_if_not_exists(1, "multiplyDivide", MD_cog_ofs, {"input1Y" : cog_y})
    utils.cr_node_if_not_exists(1, "reverse", rev_cog_ofs)
    utils.cr_node_if_not_exists(1, "composeMatrix", CM_cog_ofs)
    utils.cr_node_if_not_exists(1, "composeMatrix", CM_inv_cog_ofs)
    if cog_x == 0:
        cmds.setAttr(f"{MD_cog_ofs}.input1X", 10)
    else:
        cmds.setAttr(f"{MD_cog_ofs}.input1X", cog_x)
    if cog_z == 0:
        cmds.setAttr(f"{MD_cog_ofs}.input1Z", 10)
    else:
        cmds.setAttr(f"{MD_cog_ofs}.input1Z", cog_z)

    # add custom attributes
        # Input & Output groups
    utils.add_float_attrib(root_input_grp, ["globalScale"], [0.01, 999], True) 
    utils.add_float_attrib(root_outputs_grp, ["globalScale"], [0.01, 999], True)
    utils.add_attr_if_not_exists(root_outputs_grp, "ctrl_centre_mtx", 'matrix', False)
    utils.add_attr_if_not_exists(root_outputs_grp, "ctrl_cog_mtx", 'matrix', False)
    cmds.setAttr(f"{root_input_grp}.globalScale", 1, keyable=0, channelBox=0)
    cmds.setAttr(f"{root_outputs_grp}.globalScale", 1, keyable=0, channelBox=0)
        # ctrls
    utils.add_locked_attrib(root_ctrl, ["Attributes"])
    utils.add_float_attrib(root_ctrl, ["globalScale"], [0.01, 999], True)
    cmds.setAttr(f"{root_ctrl}.globalScale", 1)
        # cog offset
    utils.add_locked_attrib(cog_ctrl, ["Cog_Pivot"])
    offset_piv__attr_list = ["Offset_pivot_X", "Offset_pivot_Y", "Offset_pivot_Z"]
    utils.add_float_attrib(cog_ctrl, [offset_piv__attr_list[0]], [0, 1], False)
    utils.add_float_attrib(cog_ctrl, [offset_piv__attr_list[1]], [0, 1], False)
    utils.add_float_attrib(cog_ctrl, [offset_piv__attr_list[2]], [0, 1], False)
    cmds.setAttr(f"{cog_ctrl}.{offset_piv__attr_list[1]}", 1)

    # connections
    utils.connect_attr(f"{root_input_grp}.globalScale", f"{fm_global_scale}{flt_A}")
    utils.connect_attr(f"{root_ctrl}.globalScale", f"{fm_global_scale}{flt_B}")

    # root
    for x in range(3):
        utils.connect_attr(f"{fm_global_scale}{out_flt}", f"{root_ctrl}.scale{axis_plgs[x]}")

    # centre
    utils.connect_attr(f"{root_ctrl}{wld_mtx_plg}", f"{MM_centre}{mtx_in_plgs_ls[1]}")
    utils.connect_attr(f"{MM_centre}{mtx_sum_plg}", f"{centre_ctrl}{opm_plg}")

    # cog
    utils.connect_attr(f"{centre_ctrl}{wld_mtx_plg}", f"{MM_cog}{mtx_in_plgs_ls[1]}")
    utils.connect_attr(f"{MM_cog}{mtx_sum_plg}", f"{cog_ctrl}{opm_plg}")

    # centre outputs
    utils.connect_attr(f"{centre_ctrl}{wld_mtx_plg}", f"{MM_centre_outputs}{mtx_in_plgs_ls[1]}")
    utils.connect_attr(f"{cog_ctrl}{wld_mtx_plg}", f"{MM_cog_outputs}{mtx_in_plgs_ls[1]}")

    # cog offset option]
    for x in range(3):
        utils.connect_attr(f"{cog_ctrl}.{offset_piv__attr_list[x]}", f"{MD_cog_ofs}{input2_val_plgs_ls[x]}")
    utils.connect_attr(f"{MD_cog_ofs}{output_plg}", f"{CM_cog_ofs}{inputT_plug}")
    utils.connect_attr(f"{CM_cog_ofs}{out_mtx_plg}", f"{MM_cog}{mtx_in_plgs_ls[0]}")
        # reverse
    utils.connect_attr(f"{MD_cog_ofs}{output_plg}", f"{rev_cog_ofs}.input")
    utils.connect_attr(f"{rev_cog_ofs}{output_plg}", f"{CM_inv_cog_ofs}{inputT_plug}")
    utils.connect_attr(f"{CM_inv_cog_ofs}{out_mtx_plg}", f"{MM_cog_outputs}{mtx_in_plgs_ls[0]}")

    # cog outputs
    utils.connect_attr(f"{fm_global_scale}{out_flt}", f"{root_outputs_grp}.globalScale")
    utils.connect_attr(f"{MM_centre_outputs}{mtx_sum_plg}", f"{root_outputs_grp}.ctrl_centre_mtx")
    utils.connect_attr(f"{MM_cog_outputs}{mtx_sum_plg}", f"{root_outputs_grp}.ctrl_cog_mtx")

# -----------------------------------------------------------------------------
cog_position_dict = {
        "root": [0, 0, 0],
        "COG": [0, 147, 0]
        }
cog_pos = cog_position_dict["COG"]
print(cog_pos)
root_system(cog_pos)