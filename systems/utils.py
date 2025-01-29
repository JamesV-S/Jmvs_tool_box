
import maya.cmds as cmds
import os
import re


def get_first_tree_index(tree_view):
        selection_model = tree_view.selectionModel()
        selected_indexes = selection_model.selectedIndexes()

        # is there an item selected?
        if selected_indexes:
            # for the time being get the first selected index (I could change this to handle multiple selections)
            selected_index = selected_indexes[0]
            return selected_index


def find_directory(db_name, root_directory):
            for dirpath, dirnames, filenames in os.walk(root_directory):
                if db_name in filenames:
                    return dirpath
            raise FileNotFoundError(f"Database '{db_name}' not found starting from '{root_directory}'.")


def delete_existing_ui(ui_name):
    if cmds.window(ui_name, exists=True):
        cmds.deleteUI(ui_name, window=True)


def create_rig_group(name):
    hi_name_list = [name, 'grp_controls', 'grp_geo', 
                'grp_skeleton', 'DO_NOT_TOUCH', 'grp_rig_systems', 
                'grp_blendshapes', 'grp_components', 'grp_misc'
                ]
    def create_group_hierarchy(the_range=range(len(hi_name_list))):
        hi_list = []
        for i in the_range:
            grp = cmds.group(em=1, n=hi_name_list[i])
            hi_list.append(grp)        
        return hi_list
    grp_list = create_group_hierarchy()
    # parent 'grp_controls', 'rig_buffer', 'grp_geo', 'grp_skeleton', 'DO_NOT_TOUCH' to 'JMVS_rig'
    cmds.parent(grp_list[1:5], grp_list[0])
        # parent 'grp_rig_systems', 'grp_blendshapes', 'grp_components', 'grp_misc' to 'DO_NOT_TOUCH'
    cmds.parent(grp_list[5:10], grp_list[4])

    cmds.select(cl=1)


def select_set_displayType(name, checkBox, reference):
        cmds.select(name)
        objects = cmds.ls(sl=1, type="transform")
        if checkBox:
            for obj in objects:
                cmds.setAttr(f"{obj}.overrideEnabled", 1)
                if reference:
                    cmds.setAttr(f"{obj}.overrideDisplayType", 2)
                else:
                    cmds.setAttr(f"{obj}.overrideDisplayType", 1)
        else:
            for obj in objects:
                cmds.setAttr(f"{obj}.overrideEnabled", 1)
                cmds.setAttr(f"{obj}.overrideDisplayType", 0)
        cmds.select(cl=1)


def get_selection_trans_dict(selection, side):    
    translation_pos = {}
    for sel in selection:
        trans_ls = cmds.xform(sel, q=1, translation=1, worldSpace=1)
        if side == 'R':
            trans_ls[0] = -trans_ls[0]
        translation_pos[sel] = list(trans_ls)
    # if the component is on the right side, move it to the exact oposite, which means x is reversed!!
    
    return translation_pos


def get_selection_trans_rots_dictionary():
    selection = cmds.ls(sl=1, type="transform")
    
    translation_pos = {}
    rotation_pos = {}
    
    for sel in selection:
        trans_ls = cmds.getAttr(f"{sel}.translate")[0]
        rot_ls = cmds.getAttr(f"{sel}.rotate")[0]
        
        translation_pos[sel] = trans_ls
        rotation_pos[sel] = rot_ls
        
    print("Trans dictionary: ", translation_pos)
    print("Rots dictionary: ", rotation_pos)
    
    return translation_pos, rotation_pos
   
# get_selection_trans_rots_dictionary()

system_pos = {"spine_1": [0,150,0],"spine_2": [0, 165, 3.771372431203975],"spine_3": [0, 185, 6.626589870023061],"spine_4": [0, 204, 5.4509520093959845],"spine_5": [0.0, 231.0, 0.0150903206755304]}
system_rot = {"spine_1": [13.832579598094327, 0, 0],"spine_2":[8.04621385323777, 0, 0],"spine_3":[-3.330793760291316, 0, 0],"spine_4":[-11.225661138926666, 0, 0],"spine_5":[0,0,0]}

def set_transformations(translation_dict, rotation_dict):
    for obj in translation_dict:
        # check if object exists in scene
        if not cmds.objExists(obj):
            print(f"Object: '{obj}' doesn't exist in the scene")
            continue

        current_trans = cmds.getAttr(f"{obj}.translate")[0]
        current_rot = cmds.getAttr(f"{obj}.rotate")[0]

        # check if the object is alreadyu at the specified positions
        if current_trans == translation_dict[obj] and current_rot == rotation_dict[obj]:
            print(f"Object: '{obj}' is already in the specified position")
            continue

        # Set the trans & rot values
        cmds.setAttr(f"{obj}.translate", *translation_dict[obj])
        cmds.setAttr(f"{obj}.rotate", *rotation_dict[obj])
        print(f"Set the trans & rot values for '{obj}' ")

# set_transformations(system_pos, system_rot)

def colour_guide_custom_shape(custom_crv):
    # Firstly, from the 'custom_crv' select all shapes in it & set their overrideEnabled!
    shape_list = cmds.listRelatives(custom_crv, shapes=1)
    for shape in shape_list:
        cmds.setAttr(f"{shape}.overrideEnabled", 1)
        
    # Create lists for shapes with specific patterns in their names!
    yellow_shape = [shape for shape in shape_list if custom_crv in shape]
    for shape in yellow_shape:
        cmds.setAttr(f"{shape}.overrideColor", 22) # 17

    red_shape = [shape for shape in shape_list if "X" in shape]
    for shape in red_shape:
        cmds.setAttr(f"{shape}.overrideColor", 13)

    green_shape = [shape for shape in shape_list if "Y" in shape]
    for shape in green_shape:
        cmds.setAttr(f"{shape}.overrideColor", 14)

    blue_shape = [shape for shape in shape_list if "Z" in shape]
    for shape in blue_shape:
        cmds.setAttr(f"{shape}.overrideColor", 6)

    black_shape = [shape for shape in shape_list if "guidePivot" in shape]
    for shape in black_shape:
        cmds.setAttr(f"{shape}.overrideColor", 1)

# colour_custom_shape("crv_custom_guide")

def colour_COG_control(custom_crv):
    print(f"Colour_cog = {custom_crv}")
    # Firstly, from the 'custom_crv' select all shapes in it & set their overrideEnabled!
    shape_list = cmds.listRelatives(custom_crv, shapes=1)
    for shape in shape_list:
        cmds.setAttr(f"{shape}.overrideEnabled", 1)
        cmds.setAttr(f"{shape}.overrideColor", 18)
        
    # Create lists for shapes with specific patterns in their names!
    grey_shape = [shape for shape in shape_list if "kite" in shape]
    for shape in grey_shape:
        cmds.setAttr(f"{shape}.overrideColor", 3)
# colour_COG_control("ctrl_COG")

def colour_root_control(custom_crv):
    
    # Firstly, from the 'custom_crv' select all shapes in it & set their overrideEnabled!
    shape_list = cmds.listRelatives(custom_crv, shapes=1)
    for shape in shape_list:
        cmds.setAttr(f"{shape}.overrideEnabled", 1)
        cmds.setAttr(f"{shape}.overrideColor", 17)
        
    # Create lists for shapes with specific patterns in their names!
    white_shape = [shape for shape in shape_list if "white" in shape]
    for shape in white_shape:
        cmds.setAttr(f"{shape}.overrideColor", 16)
# colour_root_control("ctrl_root")


def cr_node_if_not_exists(util_type, node_type, node_name, set_attrs=None):
    if not cmds.objExists(node_name):
        if util_type:
            cmds.shadingNode(node_type, au=1, n=node_name)
        else:
            cmds.createNode(node_type, n=node_name)
        if set_attrs:
            for attr, value in set_attrs.items():
                cmds.setAttr(f"{node_name}.{attr}", value)


def connect_attr(source_attr, target_attr):
    connections = cmds.listConnections(target_attr, destination=False ,source=True)
    #print(f"here is the listed connection: {connections}")
    if not connections:
        cmds.connectAttr(source_attr, target_attr, force=True)
    else:
        print(f" CON {source_attr} is already connected to {target_attr} ")


def add_locked_attrib(ctrl, en):              
    dividerNN = "------------" 
    atrrType = "enum"
    
    for attr in en:
        # Generate the long name for the attribute
        ln = f"{attr.lower()}_dvdr"
        attr.upper() 

        #check if the attribute already exists
        if not cmds.attributeQuery(ln, node=ctrl, exists=True):
            try:
                # add the attributes
                cmds.addAttr(ctrl, longName=ln, niceName=dividerNN, 
                            attributeType=atrrType, enumName=attr, k=True
                            )
                
                cmds.setAttr(f"{ctrl}.{ln}", lock=True, keyable=False, 
                            channelBox=True
                            )
                print(f"Added locked attr {attr} on {ctrl}")
            except Exception as e:
                print(f"Failed to add locked attr {attr} on {ctrl}: {e}")
        else:
            print(f"Attribute {attr} already exists on {ctrl}")


def add_float_attrib(ctrl, flt, val, limited):
    MinVal = val[0]
    MaxVal = val[1]
    
    for target in [ctrl]:
        for attr in flt:
            if not cmds.attributeQuery(attr, node=target, exists=True):
                if limited:                            
                    cmds.addAttr(target, longName=attr, at='double', dv=MinVal, 
                                min= MinVal, max = MaxVal)
                    cmds.setAttr(f"{target}.{attr}", e=1, k=1 )
                else:
                    cmds.addAttr(target, longName=attr, at='double', dv=0, 
                                )
                    cmds.setAttr(f"{target}.{attr}", e=1, k=1 )
            else:
                print(f"Attribute {attr} already exists on {target}")


def proxy_attr_list(master_ctrl, ctrl_list, N_of_Attr):
    ctrls = cmds.ls(sl=1, type="transform")

    for target in [ctrl_list]:
        cmds.addAttr( target, ln=N_of_Attr, proxy=f"{master_ctrl}.{N_of_Attr}" )


def custom_enum_attr(ctrl, enm_lng_nm, CtrlEnmOptions):
    print("In util the control is: ", ctrl)
    print("In util the attr is: ", enm_lng_nm)
    for target in [ctrl]:
        if not cmds.attributeQuery(enm_lng_nm, node=target, exists=True):
            cmds.addAttr(target, longName=enm_lng_nm, at="enum", enumName=CtrlEnmOptions )
            print(f"{target}.{enm_lng_nm}")
            cmds.setAttr( f"{target}.{enm_lng_nm}", e=1, k=1 )
#custom_enum_attr( "James", "Thuki:Arron:Harv")

def constrain_2_items(output_item, input_item, con_type, values):
    parent_prefix = "pCon"
    point_prefix = "pointCon"

    translate_axes = ["X", "Y", "Z"]

    skip_translate = []
    # roate automatically skipped
    skip_rotate = ["x", "y", "z"]

    if values != "all": # Apply rotates if 'all' is specified
        for axis in translate_axes:
            if axis not in values:
                skip_translate.append(axis.lower())
    else: skip_rotate = [] 

    if con_type == "parent":
        constraint_name = f"{parent_prefix}_{input_item}"
    elif con_type == "point":
        constraint_name = f"{point_prefix}_{input_item}"

    # Check for existing constraints of the same type and delete them if so
    existing_constraints = cmds.listRelatives(input_item, type='constraint', allDescendents=False) or []
    
    for constraint in existing_constraints:
        if cmds.objectType(constraint) == 'parentConstraint' and con_type == 'parent':
            cmds.delete(constraint)
        elif cmds.objectType(constraint) == 'pointConstraint' and con_type == 'point':
            cmds.delete(constraint)
    
    # cr the new constraint !
    if con_type == "parent":
        cmds.parentConstraint(
            output_item, input_item, n=constraint_name, mo=1,
            skipTranslate=skip_translate, skipRotate=skip_rotate
        )

    elif con_type == "point":
        cmds.pointConstraint(
            output_item, input_item, n=constraint_name, mo=1,
            skip=skip_translate
        )

# necessary order:
# constrain_2_items("output", "input", "point", ["X", "Z"])
# constrain_2_items("output", "input", "parent", ["Y"])

# constrain_2_items("output", "input", "parent", 'all')

def connect_guide(start_guide, end_guide):
        cmds.select(cl=1)
        joint_1 = cmds.joint(n=f"ddj_start_{start_guide.replace('xfm_guide_', '')}")
        joint_2 = cmds.joint(n=f"ddj_end_{start_guide.replace('xfm_guide_', '')}")
        cmds.select(cl=1)
        cmds.matchTransform(joint_1, start_guide, pos=1, scl=0, rot=0)
        cmds.matchTransform(joint_2, end_guide, pos=1, scl=0, rot=0)
        
        jnt_1_xform = cmds.xform(joint_1, q=1, rotatePivot=1, ws=1)
        jnt_2_xform = cmds.xform(joint_2, q=1, rotatePivot=1, ws=1)
        
        # constrain the joints!
        cmds.pointConstraint(start_guide, joint_1, n=f"pointCon_str_{start_guide.replace('xfm_guide_', '')}", w=1)
        cmds.pointConstraint(end_guide, joint_2, n=f"pointCon_end_{start_guide.replace('xfm_guide_', '')}", w=1)

        curve_name = f"cv_{start_guide.replace('xfm_', '')}"
        cmds.curve(d=1, n=curve_name, p=[jnt_1_xform, jnt_2_xform])
        cmds.setAttr(f"{curve_name}.overrideEnabled", 1)
        cmds.setAttr(f"{curve_name}.overrideDisplayType", 2)
        
        if not cmds.objExists("grp_component_misc"):
            cmds.group(n=f"grp_component_misc", em=1)
        cmds.parent(curve_name, joint_1, "grp_component_misc")

        # cluster the curve
        start_cluster = cmds.cluster(f"{curve_name}.cv[0]", n=f"cls_{start_guide.replace('xfm_guide_', '')}_cv0")
        end_cluster = cmds.cluster(f"{curve_name}.cv[1]", n=f"cls_{start_guide.replace('xfm_guide_', '')}_cv1")
        
        #for x in range(2):
        try:
            cmds.parent(start_cluster, start_guide)
            cmds.parent(end_cluster, end_guide)
        except cmds.warning():
            pass
        
        clusters = cmds.ls(type="cluster")
        for x in clusters:
            cmds.setAttr(f"{x}Handle.hiddenInOutliner", 1)
            cmds.hide(f"{x}Handle")
        # arguments: 2 guides
        # create: 2 joints / black linear curve / 
        # methods: cr curve to go from start_guide to end_guide 
        # > create cluster on each cv > parent correct cv to xfm_guide 
        # > joint1 @ start_guide, joint2 @ end_guide > pointConstrain joint to xfm_guid


    

