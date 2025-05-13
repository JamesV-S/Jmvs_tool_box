
import maya.cmds as cmds
import importlib
import sys
import os

from utils import (
    utils, 
    utils_os
)
from systems.sys_char_rig import (
    cr_ctrl
)
from databases.char_databases import (
    database_schema_002
)

importlib.reload(utils_os)
importlib.reload(utils)
importlib.reload(cr_ctrl)
importlib.reload(database_schema_002)

class CreateXfmGuides():
    def __init__(self, database_componment_dict, val_availableRigComboBox):
        rig_folder_name = val_availableRigComboBox
        self.rig_db_directory = utils_os.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", 
            "db_rig_storage", rig_folder_name
            )

        print(f"crerating guide component for {database_componment_dict}")
        self.module_name = database_componment_dict['module_name']
        self.unique_id = database_componment_dict['unique_id']
        self.side = database_componment_dict['side']
        self.component_pos_dict = database_componment_dict['component_pos']
        self.component_controls_dict = database_componment_dict['controls']
        

        print(f"Working on `self.module_name`: {self.module_name}, `self.unique_id`: {self.unique_id}, `self.side`: {self.side}, `self.component_pos_dict`:{self.component_pos_dict}")
        self.guides = self.build_guide_components(self.module_name, self.unique_id, self.side, self.component_pos_dict, self.component_controls_dict)
        
        self.build_control_components(self.guides, self.module_name, self.unique_id, self.side, self.component_controls_dict)


    def build_guide_components(self, module_name, unique_id, side, component_pos, component_ctrls):
        self.guide_import_dir =  os.path.join(utils_os.create_directory("Jmvs_tool_box", "imports" ), "imp_component_guide.abc")# 
        
        # import the guide & distribbute it to all necessary guides!    
        # guides = []
        
        if module_name == "spine" or module_name == "tail" or module_name == "neck":
            print(f"Spine module detected: {module_name}")
            guides = self.rail_guide_setup(module_name, unique_id, side, component_pos, component_ctrls)
        else:
            guides = self.guide_setup(module_name, unique_id, side, component_pos, component_ctrls)

        #----------------------------------------------------------------------
        # lock & hide scale & visibilty
        for x in range(len(guides)):
            cmds.setAttr(f"{guides[x]}.sx", lock=1, keyable=0, channelBox=0)
            cmds.setAttr(f"{guides[x]}.sy", lock=1, keyable=0, channelBox=0)
            cmds.setAttr(f"{guides[x]}.sz", lock=1, keyable=0, channelBox=0)
            cmds.setAttr(f"{guides[x]}.v", lock=1, keyable=0, channelBox=0)

        # Hide clusters in outliner           
        clusters = cmds.ls(type="cluster")
        for x in clusters:
            cmds.setAttr(f"{x}Handle.hiddenInOutliner", 0)
            cmds.hide(f"{x}Handle")

        guide_grp_list = []
        # group every Guide
        for guide in guides:
            offset_grp = cmds.group(n=f"offset_{guide}", em=1)
            cmds.matchTransform(offset_grp, guide, pos=1, scl=0, rot=0)
            cmds.parent(guide, offset_grp)
            guide_grp_list.append(offset_grp)
        
        # group guides 
        gd_master_group = f"grp_xfm_components"
        gd_component_grp_name = f"xfm_grp_{module_name}_component_{unique_id}_{side}"
        if not cmds.objExists(gd_component_grp_name):
            cmds.group(n=gd_component_grp_name, em=1)
        if not cmds.objExists(gd_master_group):
            cmds.group(n=gd_master_group, em=1)
        cmds.parent(guide_grp_list, gd_component_grp_name)
        cmds.parent(gd_component_grp_name, gd_master_group)
        cmds.select(cl=1)

        return guides

        
    def build_control_components(self, guides, module_name, unique_id, side, component_ctrls):
        # create controls ontop
        # have a function that given the name of the control, creates it!
        ctrl_name_list = []
        ctrl_grp_list = []
        fk_ctrl_list = []

        
        curve_info_data = database_schema_002.CurveInfoData(self.rig_db_directory, module_name, unique_id, side)
        curve_info_dict = curve_info_data.return_curve_info_dict()

        for ctrl_type, ctrl_dict in component_ctrls.items():
            for ctrl_name, ctrl_shape in ctrl_dict.items():
                whole_ctrl_name = f"ctrl_{ctrl_name}_{unique_id}_{side}" # ctrl_fk_clavicle_0_L
                ctrl_name_list.append(whole_ctrl_name)
                import_ctrl = cr_ctrl.CreateControl(type=ctrl_shape, name=whole_ctrl_name)
                ctrl = import_ctrl.retrun_ctrl()
                # scale up the ctrl for time being
                # cmds.scale(15, 15, 15, ctrl)
                # cmds.makeIdentity(ctrl, a=1, t=0, r=0, s=1, n=0, pn=1)

                if "root" in module_name:
                    ctrl_suffix = f"{ctrl_name}_{unique_id}_{side}"
                else:
                    ctrl_suffix = f"{ctrl_name[3:]}_{unique_id}_{side}"
                for guide in guides:
                    if guide.endswith(ctrl_suffix):
                        guide_pos = cmds.xform(guide, q=1, t=1, worldSpace=1)
                        cmds.xform(ctrl, t=guide_pos, worldSpace=1)
                        break
                
                # colour
                for x in range(len(ctrl_name_list)):
                    cmds.setAttr(f"{ctrl_name_list[x]}.overrideEnabled", 1)
                    if side == "L":
                        cmds.setAttr(f"{ctrl_name_list[x]}.overrideColor", 13)
                    elif side == "R":
                        cmds.setAttr(f"{ctrl_name_list[x]}.overrideColor", 6)
                    elif side == "M":
                        cmds.setAttr(f"{ctrl_name_list[x]}.overrideColor", 17)

                # Rebuild the control:
                for key, value_dict in curve_info_dict.items():
                    utils.rebuild_ctrl(key, value_dict)

                # group all ctrls!
                cmds.group(ctrl, n=f"gd_{whole_ctrl_name}")
                ctrl_grp_list.append(f"gd_{whole_ctrl_name}")
                # point constrain the groups to the guides to follow
                # if not module_name == "root":
                for guide in guides:
                    if guide.endswith(ctrl_suffix):
                        cmds.pointConstraint(guide, f"gd_{whole_ctrl_name}",  n=f"pCon_gd_{whole_ctrl_name}")
                        # if ctrl_type == "FK_ctrls":
                        #     print(f" fk ctrls = {ctrl}")
                        break
                if ctrl_type == "FK_ctrls":
                    fk_ctrl_list.append(ctrl)

        # xfm_guide_bipedArm
        if not module_name == "root":
            try:
                # aim constraint the groups of ctrls to guides so fk controls keep correct positions!
                for x in range(len(fk_ctrl_list)):
                    cmds.aimConstraint(guides[x+1], f"gd_{fk_ctrl_list[:-1][x]}", n=f"pAim_{guides[x+1]}")
            except:
                pass
            # match end ctrl's grp to parent ctrl orientation.
            cmds.matchTransform(f"gd_{fk_ctrl_list[-1]}", fk_ctrl_list[-2], pos=0, rot=1, scl=0)
            cmds.orientConstraint(fk_ctrl_list[-2], f"gd_{fk_ctrl_list[-1]}")
        
        #----------------------------------------------------------------------
        # group ctrls
        master_group = f"grp_ctrl_components"
        grp_name = f"ctrl_{module_name}_grp_component_{side}"
        if not cmds.objExists(grp_name):
            cmds.group(n=grp_name, em=1)
        if not cmds.objExists(master_group):
            cmds.group(n=master_group, em=1)
        cmds.parent(ctrl_grp_list, grp_name)
        cmds.parent(grp_name, master_group)
        cmds.select(cl=1)
        

    def guide_setup(self, module_name, unique_id, side, component_pos, component_ctrls):
        (f"Other module: {module_name}")
        guides = []
        for key, pos in component_pos.items():
            imported_guide = cmds.file(self.guide_import_dir, i=1, ns="component_guide", rnn=1)
            # esyablish guides, check for root module that acts differently
            # if module_name == "root":
            #     if cmds.objExists(f"xfm_guide_{module_name}_root"):
            #         guide_name = f"xfm_guide_{module_name}_COG" # cog guide
            #     else: # root guide
            #         guide_name = f"xfm_guide_{module_name}_root"
            # else:
            #     guide_name = f"xfm_guide_{module_name}_{key}_{unique_id}_{side}"
            guide_name = f"xfm_guide_{module_name}_{key}_{unique_id}_{side}"
            guides.append(cmds.rename(imported_guide[0], guide_name))
            cmds.xform(guide_name, translation=pos, worldSpace=1)
        
        if side == "R":
            temp_grp = cmds.group(n=f"temp_grp_{module_name}_{unique_id}_{side}", em=1)
            for guide in guides:
                cmds.parent(guide, temp_grp)
            cmds.setAttr(f"{temp_grp}.scaleX", -1)
            for guide in guides:
                cmds.parent(guide, w=1)
                cmds.makeIdentity(guide, t=0, r=1, s=1)
            cmds.delete(temp_grp)
            cmds.select(cl=1)
        
        for x in range(len(guides)):
            try:
                cmds.setAttr(f"{guides[x]}.overrideEnabled", 1)
                cmds.setAttr(f"{guides[x]}.overrideColor", 25)
                # PARENTING THE GUIDES IS TEMPORARY!
                # cmds.parent(guides[x+1], guides[x])
                utils.connect_guide(guides[x], guides[x+1])
            except:
                pass
        
        # ankle has extra guide helper for positioning    
        if module_name == "bipedLeg":
            leg_imp_ctrl = cr_ctrl.CreateControl(
                type="bvSquare", name=f"xfm_guide_{module_name}_foot_{unique_id}_{side}")
            ankle_helper_ctrl = leg_imp_ctrl.retrun_ctrl()
            cmds.matchTransform(ankle_helper_ctrl, guides[2], pos=1, scl=0, rot=0)
            cmds.setAttr(f"{ankle_helper_ctrl}.translateY", 0)
            guides.append(ankle_helper_ctrl)
        
        return guides


    def rail_guide_setup(self, module_name, unique_id, side, component_pos, component_ctrls):
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
                            # xfm_guide_spine_spine0_0_M
                guide_name = f"xfm_guide_{module_name}_{module_name}{x}_{unique_id}_{side}"
                spine_guides.append(cmds.rename(temp_guide[0], guide_name))
                print(f"@@ > spine_guides IN LOOP = {guide_name}")
        print(f"spine_guides = {spine_guides}")
        
        # Replace control shapes
        for temp_gd in spine_guides:
            parts = temp_gd.split('_')[-3][-1]
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
        db_data = database_schema_002.RetrieveSpecificData(self.rig_db_directory, module_name, unique_id, side)
        jnt_num = db_data.return_get_jnt_num()
        ddj_spine_jnts = []
        for x in range(jnt_num):
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
        
        self.set_joint_values(jnt_num, ls_strechMulth, ls_remapVal, ls_condition)
        return spine_guides

    def set_joint_values(self, jnt_num, ls_strechMulth, ls_remapVal, ls_condition):
        increment_value = 1.0/(jnt_num - 1)  # Calculate the correct increment

        for x in range(1, jnt_num):  # Start from 1 to skip the root joint
            value = x * increment_value
            cmds.setAttr(f"{ls_strechMulth[x-1]}.input1X", value)
            cmds.setAttr(f"{ls_remapVal[x-1]}.outputMax", value)
            cmds.setAttr(f"{ls_condition[x-1]}.colorIfTrueR", value)
        '''
        
        spine_guides = ['xfm_guide_spine_0_0_M', 'xfm_guide_spine_1_0_M', 'xfm_guide_spine_2_0_M', 
                        'xfm_guide_spine_3_0_M', 'xfm_guide_spine_4_0_M', 'xfm_guide_spine_5_0_M']
        guide_pos = [[0.0, 150.0, 0.0], 
                        [-1.0302985026792348e-14, 165.3182830810547, 2.138536453247061], 
                        [-2.3043808310802754e-14, 185.50926208496094, 2.8292100429534632], 
                        [-3.3364796818449844e-14, 204.27308654785156, -0.3802546262741595], 
                        [-5.1020985278054485e-14, 237.46397399902344, -8.25034904479989]]
        
        '''
            
        '''
        // Cluster the CVs 
        // Create 6 guides
        // Match pos for each curve's CVs 
        // Parent the spine_clusters to the guides
        // Move the guides to deisred position

        // Don't use 'connect_guide()', make the curve drive the ddj
        // Curve drive the fk & ik ctrls
        // the rail curve should be controled by 1 ctrl for the aiming of joints & ctrl orientation!
        '''
     

        