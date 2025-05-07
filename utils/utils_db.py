
import maya.cmds as cmds

def cr_curve_info_dictionary(FK_ctrl_dict, IK_ctrl_dict, unique_id, side):
    # Create a dictionary using FK and IK dictionaries as starting point
    curve_info_dict = {}
    for fk_name in FK_ctrl_dict.keys():
        ctrl_fk_name = f"ctrl_{fk_name}_{unique_id}_{side}"
        curve_info_dict[ctrl_fk_name] = {}
    
    for ik_name in IK_ctrl_dict.keys():
        ctrl_ik_name = f"ctrl_{ik_name}_{unique_id}_{side}"
        curve_info_dict[ctrl_ik_name] = {}
    
    return curve_info_dict