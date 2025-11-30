
import importlib
import maya.cmds as cmds
from utils import (
    utils)

importlib.reload(utils)

'''
Prerequisites:
    - Current FACS face rig must have a 'target_character' 
        (Character I want the rig to be transferred to!).
        working on the base FACS rig. 

Purpose for this method: 
    -  Be able to create 'target_character' new/corrective 
        blendshapes to fix deformation issues.

How this has to be done:
    - Need to create unconnected FACS blendshapes from the 
        target_character transfer.
    - Add them to the target_character base geo with a new 
        blendshape.
    - Wire existing FACS rig setup with new FACS blendshape set. 
'''
source_bld_name = "face_blendShape"
target_name = "mosslyite"

# retrieve each blendshape in FACS blendshape Setup & their incoming connections
def get_blendshape_plug(blendshape_name):
    '''
    Docstring for get_blendshape_plug
    # Description: 
        Retrieve the incoming connection for each blednshape shape in the given 
        blendshape node. 
    # Args:
        blendshape_name (string): Name of the blendshape on the base FACS rig. 
    # Return:
        source_bld_dict (dict): {Keys="*blendshape_name.*shape_name": values=*input_plug}
    '''
    source_bld_dict = {}

    # check if there are any connections
    if cmds.listConnections(f"{blendshape_name}.weight", c=1):
        source_list = cmds.listConnections(f"{blendshape_name}.weight", c=1)[::2]
        plug_list = cmds.listConnections(f"{blendshape_name}.weight", p=1)

        for key, val in zip(source_list, plug_list):
            source_bld_dict[key] = val
        
        print(f"source_bld_dict = {source_bld_dict}")
    
        return source_bld_dict
    else:
        return {}


source_bld_dict = get_blendshape_plug(source_bld_name)

'''
source_bld_dict = {
    'faceblendshape.base_blend': 'ctrl_control_M.translateY', 
    'faceblendshape.base_blendshape': 'ctrl_up_M.translateX'}

'''

'''
connectAttr -f ctrl_control_M.translateY faceblendshape.base_blend;
'''

def cr_bld_groups(target_name):
    # Group organisation.
    bld_master_group = f"grp_bld_{target_name}"
    if not cmds.objExists(bld_master_group):
        utils.cr_node_if_not_exists(0, "transform", bld_master_group)
    bld_target_shapes_grp = f"grp_tgt_{target_name}_shapes"
    if not cmds.objExists(bld_target_shapes_grp):
        utils.cr_node_if_not_exists(0, "transform", bld_target_shapes_grp)
        try:
            cmds.parent(bld_target_shapes_grp, bld_master_group)
            cmds.select(cl=1)
        except: pass

    return bld_master_group, bld_target_shapes_grp

bld_master_group, bld_target_shapes_grp = cr_bld_groups(target_name)


def get_source_geometry(source_bld_dict):
    '''
    geo (string): Name of the mesh with blednshape node on it. 
    '''
    bld_plg = list(source_bld_dict.keys())[0]
    blendshape = bld_plg.split(".")[0]
    geo = cmds.deformer(blendshape, query=True, geometry=True)[0]
    print(f"geo = {geo}")

    return geo
source_geo = get_source_geometry(source_bld_dict)


def cr_target_base_mesh(source_geo, target_name):
    # Make the target base geo.
    target_base_mesh = f"geo_{target_name}_base"
    cmds.duplicate(source_geo, n=target_base_mesh)
    cmds.parent(target_base_mesh, bld_master_group)
    cmds.select(cl=1)
    return target_base_mesh

target_base_mesh = cr_target_base_mesh(source_geo, target_name)

# Create copy's of all shapes in blendshape
    # Use dict data!
def copy_target_char_facs_blendshapes(source_geo, target_name, source_bld_dict):
    '''
    Docstring for copy_target_char_facs_blendshapes
    # Description: 
        Create copy's of all shapes in the blendshape deternmined by 
        param: source_bld_dict
    # Args:
        target_name (string): Name of the 'Target_character'.
        source_bld_dict (dict): {keys="*blendshape_name.*shape_name": values=*input_plug}
    # Return:
        target_bld_dict (dict): {keys='*target_shape_name' : values=*input_plug}
    '''
    target_bld_dict = {} 

    # break break shape's connection.
    for source_bld_plg, input_connection_plg in source_bld_dict.items():
        # cr new target blendshape name.
        side_part = source_bld_plg.split('_')[0]
        remaining_parts_joined = '_'.join(source_bld_plg.split('_')[1:])
        if  side_part == "L":
            target_blendshape = f"bld_{target_name}_{remaining_parts_joined}_{side_part}"
        else:
            target_blendshape = f"bld_{target_name}_{source_bld_plg.split('.')[-1]}"
        # target_blendshape = f"bld_{target_name}_{source_bld_plg.split('.')[-1]}"

        # break shape connections on source blendshape.
        cmds.delete(source_bld_plg,  icn=1)
        # set to 1
        cmds.setAttr(source_bld_plg, 1)
        # duplicate the geo
        cmds.duplicate(source_geo, n=target_blendshape)
        # set to 0
        cmds.setAttr(source_bld_plg, 0)
        # freezeAll
        cmds.makeIdentity(target_blendshape, a=1, t=1, r=1, s=1, n=0, pn=1)
        # parent to group
        cmds.parent(target_blendshape, bld_target_shapes_grp)
        cmds.select(cl=1)

        target_bld_dict[target_blendshape] = input_connection_plg

    print(f"target_bld_dict = {target_bld_dict}")

    return target_bld_dict 
       
target_bld_dict = copy_target_char_facs_blendshapes(source_geo, target_name, source_bld_dict)


# cr new blendShape on target base mesh w/ new target blendshapes
def cr_target_facs(target_base_mesh, target_name, target_bld_dict):
    target_blenshape_name = f"bld_{target_name}_facs"
    target_shape_ls = list(target_bld_dict)
    cmds.blendShape(target_shape_ls, target_base_mesh, n=target_blenshape_name)
    return target_blenshape_name
    

target_blenshape_name = cr_target_facs(target_base_mesh, target_name, target_bld_dict)


def wire_target_facs(target_blenshape_name, target_bld_dict):
    for target_shape_name, input_plg in target_bld_dict.items():
        utils.connect_attr(f"{input_plg}",  f"{target_blenshape_name}.{target_shape_name}")

wire_target_facs(target_blenshape_name, target_bld_dict)