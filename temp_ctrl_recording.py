import importlib
import maya.cmds as cmds
from utils import (
    utils,
    utils_os,
    utils_json
)

importlib.reload(utils)

# '''
# For each control, have its own dictionary, that either has 

# # Store the data with this structure!
# {
#     "ctrl_fk_clavicle_#_#": {"degree": #, "Periodic": #, "cvs": #, "knot_vector": #, "int_B": #},
#     "ctrl_fk_shoulder_#_#": {"degree": #, "Periodic": #, "cvs": #, "knot_vector": #, "int_B": #},
#     ...
# }

{"ctrl_fk_hip_0_L": {}, "ctrl_fk_knee_0_L": {}, "ctrl_fk_ankle_0_L": {}, "ctrl_fk_ball_0_L": {}, "ctrl_fk_toe_0_L": {}, "ctrl_ik_hip_0_L": {}, "ctrl_ik_knee_0_L": {}, "ctrl_ik_ankle_0_L": {}, "ctrl_ik_ball_0_L": {}, "ctrl_ik_toe_0_L": {}}

# # IN database_schema:
# ADD 'curve_info' collunm to store the control data!

# use component name : `mdl_bipedArm_0_L` to find `db_id`
#     To Find correct row use: `db_id`| `unique_id`| `side`

# '''

# ---- Component constraints ----
def record_ctrl_data(control):
    degree = cmds.getAttr(f"{control}.degree")# control.degree()
    if isinstance(degree, list):
        degree = degree[0]
    form = cmds.getAttr(f"{control}.form")
    if isinstance(form, list):
        form = form[0]
    periodic = True if form == 3 else False
    cvs = cmds.getAttr(f"{control}.controlPoints[*]")
    cvs = [(cv[0], cv[1], cv[2]) for cv in cvs]
    print(f"degree: {degree}, form:{form}, periodic:{periodic}, cvs:{cvs}")
    knot_vector = utils.knot_vector(periodic, cvs, degree)
    scale = cmds.xform(control, q=1, s=1, worldSpace=1) 
    
    data = {
        "crv_name":control, 
        "degree": degree,  
        "periodic": periodic, 
        "points": cvs, 
        "knot": knot_vector,
        "scale": scale
        }
    
    print(f"data = {data}")

    return data


def rebuild_ctrl(control, data):
    print(f"Name = {control}, data = {data}")
    if data["crv_name"] == control:
        cmds.setAttr(f"{control}.degree", data["degree"])
        if data["periodic"]:
            cmds.closeCurve(control, preserveShape=True)
        for i, cv in enumerate(data["points"]):
            cmds.setAttr(f"{control}.controlPoints[{i}]", cv[0], cv[1], cv[2])
        cmds.rebuildCurve(control, degree=data["degree"], keepRange=0, keepControlPoints=True)
        cmds.xform(control, s=data["scale"], worldSpace=1) 
    else:
        print("the provided curve doesn't match the crv_name in the given data")


