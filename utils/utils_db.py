
import os
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


def get_database_name_path(db_directory, database_name ):
    db_directory = os.path.expanduser(db_directory)
    os.makedirs(db_directory, exist_ok=1)
    if not ".db" in database_name:
        database_name = f"DB_{database_name}.db"
    # db_name must include the entire path too!
    db_path = os.path.join(db_directory, database_name)
    
    return db_path


def cr_ori_plane_dict(object_list, default_value):
    # Need the names of the object names! in the module, (ignoring the last one)
    ori_plane_dict = {name:default_value for name in object_list}
    return ori_plane_dict