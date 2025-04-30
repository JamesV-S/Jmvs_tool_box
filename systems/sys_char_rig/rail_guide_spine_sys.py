
import importlib

from utils import (
    utils
)
from systems.sys_char_rig import (
    cr_ctrl
)
from utils import utils_os
importlib.reload(utils_os)
importlib.reload(utils)
importlib.reload(cr_ctrl)
import maya.cmds as cmds

def spine_guide_setup(module_name, unique_id, side, component_pos):
    gd_curve = f"crv_gd_{module_name}_{unique_id}_{side}"
    spine_shape = f"{gd_curve}Shape"

    # cr curve
    cmds.curve(n=gd_curve, d=3, p=[(-45, 0, 0), (-16.666667, 0, 0), (11.666667, 0, 0), (40, 0, 0)], k=[0, 0, 0, 1, 1, 1])

    # Rebuild it 
    cmds.rebuildCurve(gd_curve, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=0, kt=0, s=2, d=3, tol=0.01)

    # Cluster the CVs
    # gather all cvs on the curve
    crv_shape = cmds.listRelatives(gd_curve, shapes=True)[0]
    num_of_cvs = cmds.getAttr(f"{gd_curve}.spans") + cmds.getAttr(f"{gd_curve}.degree")
    gd_curve_cvs = [f"{gd_curve}.cv[{i}]" for i in range(num_of_cvs)]
    
    # Create Rail & rename shape nodes: 
    rail_gd_curve = f"crv_gdRail_{module_name}_{unique_id}_{side}"
    rail_shape = f"crv_gdRail_{module_name}_{unique_id}_{side}Shape"
    cmds.rename(cmds.duplicate(gd_curve, rc=1), rail_gd_curve, ignoreShape=0)

    # rename shapes
    cmds.rename(cmds.listRelatives(rail_gd_curve, s=1)[0], rail_shape)
    cmds.rename(cmds.listRelatives(gd_curve, s=1)[0], spine_shape)
    
    cmds.move(-10, 0, 0, rail_gd_curve, r=True)

    rail_clusters = []
    for x in range(num_of_cvs):
        cls_rail_handle = cmds.cluster(f"{rail_gd_curve}.cv[{x}]", n=f"cls{x}_rail_{module_name}_{unique_id}_{side}")[1]
        rail_clusters.append(cls_rail_handle)
    
    spine_clusters = []
    for x in range(num_of_cvs):
        cls_spine_handle = cmds.cluster(f"{gd_curve}.cv[{x}]", n=f"cls{x}_guide_{module_name}_{unique_id}_{side}")[1] # rail_gd_curve
        spine_clusters.append(cls_spine_handle)
    
    # Create the controls!
    spine_guides = []
    for x in range(num_of_cvs):
            temp_guide = cmds.circle()
            guide_name = f"xfm_guide_{module_name}_{x}_{unique_id}_{side}"
            spine_guides.append(cmds.rename(temp_guide[0], guide_name))
            print(f"@@ > spine_guides IN LOOP = {guide_name}")
    print(f"spine_guides = {spine_guides}")
    
    # Replace control shapes
    for temp_gd in spine_guides:
        parts = temp_gd.split('_')[-3]
        print(f"PARTS of guide name = {parts}")
        if parts == "0":
            utils.replace_control("imp_xfmSpine", temp_gd, 17, 1.5)
        elif parts == "1" or parts == "3":
            print(f"#_Prism_# temp_gd == {temp_gd}")
            utils.replace_control("imp_prism", temp_gd, 29, 0.5)
        elif parts == "2" or parts == "4":
            utils.replace_control("imp_orb", temp_gd, 25)

    # position the guides to the spine_clusters
    for cluster, guide in zip(spine_clusters, spine_guides):
        # cluster_pos = cmds.xform(cluster, q=True, ws=True, t=True)
        cmds.matchTransform(guide, cluster, pos=1, rot=0, scl=0)

    # parent spine_clusters under control
    if spine_clusters and spine_guides:
        try:
            for x in range(num_of_cvs):
                cmds.parent(spine_clusters[x], spine_guides[x])
                cmds.parent(rail_clusters[x], spine_guides[x])
        except Exception as e:
            print(f"Error during parenting: {e}")
    else:
        print("Either spine_clusters or spine_guides list is empty.")
    
    # position the guides:
    guide_pos = []
    for key, pos in component_pos.items():
            guide_pos.append(pos)
    
    print(f"guide_pos = {guide_pos} & spine_guides = {spine_guides}")
    for x in range(num_of_cvs):
            cmds.xform(spine_guides[x], translation=guide_pos[x], worldSpace=1)
    
    # Build Joints
    node_name_convention = f"_{module_name}_{unique_id}_{side}"

    # create all nodes first for constant
    crvInfo = f"INFO{node_name_convention}"
    utils.cr_node_if_not_exists(1, "curveInfo", crvInfo)# util_type, node_type, node_name, set_attrs=None)
    lenRatio = f"MD_lenRatio{node_name_convention}" # .operation" 2
    utils.cr_node_if_not_exists(1, "multiplyDivide", lenRatio, {"operation": 2})
    
    # Make constant connections
    utils.connect_attr(f"{spine_shape}.worldSpace[0]", f"{crvInfo}.inputCurve")
    utils.connect_attr(f"{crvInfo}.arcLength", f"{lenRatio}.input2X")
    arclength = cmds.getAttr(f"{crvInfo}.arcLength")
    print(f"arclength = {arclength}")
    cmds.setAttr(f"{lenRatio}.input1X", arclength)

    # connection for each ddj joint (after root)
    # calculate the addative fraction needed for the nodes

    # Example:
        # 5 joints -> -1 = 4 -> VAL = 1/4 = 0.25 -> first joint = VAL 0.25 -> rest of joints = previous value + 0.25 -> End joint = 1
    # Establish number of joints
    temp_jnt_number = 10
    ddj_spine_jnts = []
    
    for x in range(temp_jnt_number):
        joint_name = f"ddj_{x}{node_name_convention}"
        cmds.joint(n=joint_name)
        ddj_spine_jnts.append(joint_name)
    
    # parent joint to a group " origin"
    ddj_parent_grp = "grp_component_misc"
    if not cmds.objExists(ddj_parent_grp):
        cmds.group(n=ddj_parent_grp, em=1)
    cmds.parent(rail_gd_curve, gd_curve, ddj_spine_jnts[0], ddj_parent_grp)

    # first joint connection:
    mm_initialJoint = f"MD_0{node_name_convention}"
    utils.cr_node_if_not_exists(1, "multMatrix", mm_initialJoint)
    utils.connect_attr(f"{spine_guides[0]}.worldMatrix[0]", f"{mm_initialJoint}.matrixIn[0]")
    utils.connect_attr(f"{ddj_parent_grp}.worldInverseMatrix[0]", f"{mm_initialJoint}.matrixIn[1]") # matrixSum
    utils.connect_attr(f"{mm_initialJoint}.matrixSum", f"{ddj_spine_jnts[0]}.offsetParentMatrix")
    
    # Ignore the first joint:
    ddj_spine_jnts[1:]
    print(f"skipped joint: {ddj_spine_jnts[1:]}")
    
    ls_strechMulth = []
    ls_remapVal = []
    ls_condition = []
    ls_moRailPath = []
    ls_cmRail = []
    ls_moPath = []
    ls_cmSpine = []
    ls_MM_ddj = []
    
    for x in range(len(ddj_spine_jnts)):
        # cr stretchMult
        strechMult = f"MD_{x}_stretch{node_name_convention}"
        utils.cr_node_if_not_exists(1, "multiplyDivide", strechMult)
        ls_strechMulth.append(strechMult)

        remapVal = f"RVAL_{x}{node_name_convention}"
        utils.cr_node_if_not_exists(1, "remapValue", remapVal, {"inputValue":1})
        ls_remapVal.append(remapVal)

        condition = f"COND_{x}{node_name_convention}"
        utils.cr_node_if_not_exists(1, "condition", condition, {"operation":2, "secondTerm":1})
        ls_condition.append(condition)

        moRailPath = f"MPATH_{x}_rail{node_name_convention}"
        utils.cr_node_if_not_exists(0, "motionPath", moRailPath)
        ls_moRailPath.append(moRailPath)

        cmRail = f"CM_{x}_rail{node_name_convention}"
        utils.cr_node_if_not_exists(0, "composeMatrix", cmRail)
        ls_cmRail.append(cmRail)

        moPath = f"MPATH_{x}{node_name_convention}"
        utils.cr_node_if_not_exists(0, "motionPath", moPath, {"follow": 1, "worldUpType":1, "frontAxis": 0})
        ls_moPath.append(moPath)

        cmSpine = f"CM_{x}{node_name_convention}"
        utils.cr_node_if_not_exists(0, "composeMatrix", cmSpine) # multMatrix
        ls_cmSpine.append(cmSpine)
        
        MM_ddj =  f"MM_{x}{node_name_convention}"
        utils.cr_node_if_not_exists(1, "multMatrix", MM_ddj)
        ls_MM_ddj.append(MM_ddj)

    # Connect signals
    
    for x in range(len(ddj_spine_jnts)):
        utils.connect_attr(f"{lenRatio}.outputX", f"{ls_strechMulth[x]}.input2X")
        utils.connect_attr(f"{ls_strechMulth[x]}.outputX", f"{ls_remapVal[x]}.outputMin")
        utils.connect_attr(f"{lenRatio}.outputX", f"{ls_condition[x]}.firstTerm")
        utils.connect_attr(f"{ls_remapVal[x]}.outValue", f"{ls_condition[x]}.colorIfFalseR")
        utils.connect_attr(f"{ls_condition[x]}.outColorR", f"{ls_moRailPath[x]}.uValue")
        utils.connect_attr(f"{rail_shape}.worldSpace[0]", f"{ls_moRailPath[x]}.geometryPath")
        utils.connect_attr(f"{ls_moRailPath[x]}.allCoordinates", f"{ls_cmRail[x]}.inputTranslate")
        utils.connect_attr(f"{ls_condition[x]}.outColorR", f"{ls_moPath[x]}.uValue")
        utils.connect_attr(f"{spine_shape}.worldSpace[0]", f"{ls_moPath[x]}.geometryPath")
        utils.connect_attr(f"{ls_cmRail[x]}.outputMatrix", f"{ls_moPath[x]}.worldUpMatrix")
        utils.connect_attr(f"{ls_moPath[x]}.allCoordinates", f"{ls_cmSpine[x]}.inputTranslate")
        utils.connect_attr(f"{ls_moPath[x]}.rotate", f"{ls_cmSpine[x]}.inputRotate")
        utils.connect_attr(f"{ls_cmSpine[x]}.outputMatrix", f"{ls_MM_ddj[x]}.matrixIn[0]")
        # mm into Current current joint
        utils.connect_attr(f"{ls_MM_ddj[x]}.matrixSum", f"{ddj_spine_jnts[x]}.offsetParentMatrix")

    # Connect joint_0.worldInverseMatrix[0] to ls_MM_ddj[0].matrixIn[1]
    utils.connect_attr(f"ddj_0{node_name_convention}.worldInverseMatrix[0]", f"{ls_MM_ddj[0]}.matrixIn[1]")

    # Connect each ls_MM_ddj[x] to the previous joint's worldInverseMatrix
    for x in range(1, len(ddj_spine_jnts)):  
        utils.connect_attr(f"{ddj_spine_jnts[x-1]}.worldInverseMatrix[0]", f"{ls_MM_ddj[x]}.matrixIn[1]")

    increment_value = 1.0 / (temp_jnt_number - 1)  # (10-1) = 9, so 1/9 = 0.111...
    # Set attribute values progressively
    print(f"NUM stretchMULT = {len(ls_strechMulth)}")
    value_list = []
    for x in range(len(ls_strechMulth)):
        value = (x + 1) * increment_value  # First = 0.1, Second = 0.2, etc.
        value_list.append(value) 
        cmds.setAttr(f"{ls_strechMulth[x]}.input1X", value) # ls_remapVal
        cmds.setAttr(f"{ls_remapVal[x]}.outputMax", value)
        cmds.setAttr(f"{ls_condition[x]}.colorIfTrueR", value)
    print(f"VALUE INCRMENT LIST == {value_list}")
    '''
    VALUE INCRMENT LIST == [
        0.1111111111111111, 
        0.2222222222222222, 
        0.3333333333333333, 
        0.4444444444444444, 
        0.5555555555555556, 
        0.6666666666666666, 
        0.7777777777777777, 
        0.8888888888888888, 
        1.0, 
        1.1111111111111112]

    '''
    # set value attribute
    
    return spine_guides

spine_guide_setup("spine", "0", "M", {'spine1': [0.0, 144.03905123892466, 0.0], 
                    'spine2': [-1.2281763474396059e-14, 153.44444274902344, 0.0], 
                    'spine3': [-1.2281763474396059e-14, 159.88888549804688, 0.0], 
                    'spine4': [-1.2281763474396059e-14, 166.3333282470703, 0.0], 
                    'spine5': [-1.2281763474396059e-14, 172.77777099609375, 0.0], 
                    'spine6': [-1.2281763474396059e-14, 179.22222900390625, 0.0], 
                    'spine7': [-1.2281763474396059e-14, 185.6666717529297, 0.0], 
                    'spine8': [-1.2281763474396059e-14, 192.11111450195312, 0.0], 
                    'spine9': [-1.2281763474396059e-14, 198.55555725097656, 0.0], 
                    'spine10': [0.0, 206.02795168683824, 0.0]}
                    )
        
