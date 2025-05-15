
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
        self.guides, jnt_u_list = self.build_guide_components(self.module_name, self.unique_id, self.side, self.component_pos_dict, self.component_controls_dict)
        
        self.build_control_components(self.guides, self.module_name, self.unique_id, self.side, self.component_controls_dict, jnt_u_list)


    def build_guide_components(self, module_name, unique_id, side, component_pos, component_ctrls):
        self.guide_import_dir =  os.path.join(utils_os.create_directory("Jmvs_tool_box", "imports" ), "imp_component_guide.abc")# 
        
        # import the guide & distribbute it to all necessary guides!    
        # guides = []
        
        if module_name == "spine" or module_name == "tail" or module_name == "neck":
            print(f"rail module detected: {module_name}")
            guides, jnt_u_list = self.rail_guide_setup(module_name, unique_id, side, component_pos, component_ctrls)
        else:
            guides = self.guide_setup(module_name, unique_id, side, component_pos, component_ctrls)
            jnt_u_list = []
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

        return guides, jnt_u_list

        
    def build_control_components(self, guides, module_name, unique_id, side, component_ctrls, jnt_u_list):
        # create controls ontop
        # have a function that given the name of the control, creates it!
        ctrl_name_list = []
        ctrl_grp_list = []
        fk_ctrl_list = []

        curve_info_data = database_schema_002.CurveInfoData(self.rig_db_directory, module_name, unique_id, side)
        curve_info_dict = curve_info_data.return_curve_info_dict()

        # If the module is tail -> make fk ctrl for every joint. 
        # cr a list fk name ctrls. 

        if module_name == "spine" or module_name == "neck":
            self.cr_ctrls_rail_driven("IK", component_ctrls, ctrl_name_list, ctrl_grp_list, curve_info_dict, module_name, unique_id, side)
            self.cr_ctrls_rail_driven("FK", component_ctrls, ctrl_name_list, ctrl_grp_list, curve_info_dict, module_name, unique_id, side)
        elif module_name == "tail": # jnt_u_list
            self.cr_ctrls_rail_driven("IK", component_ctrls, ctrl_name_list, ctrl_grp_list, curve_info_dict, module_name, unique_id, side)
            self.cr_ctrls_rail_driven("FK", component_ctrls, ctrl_name_list, ctrl_grp_list, curve_info_dict, module_name, unique_id, side, jnt_u_list)
        else:
            self.cr_ik_fk_controls(
                component_ctrls, ctrl_name_list, ctrl_grp_list, fk_ctrl_list, 
                guides, curve_info_dict, module_name, unique_id, side
                )
        
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
        rail_guides = []
        for x in range(num_of_cvs):
                temp_guide = cmds.circle()
                            # xfm_guide_spine_spine0_0_M
                guide_name = f"xfm_guide_{module_name}_{module_name}{x}_{unique_id}_{side}"
                rail_guides.append(cmds.rename(temp_guide[0], guide_name))
                print(f"@@ > rail_guides IN LOOP = {guide_name}")
        print(f"rail_guides = {rail_guides}")
        
        # Replace control shapes
        for temp_gd in rail_guides:
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
        for cluster, guide in zip(spine_clusters, rail_guides):
            # cluster_pos = cmds.xform(cluster, q=True, ws=True, t=True)
            cmds.matchTransform(guide, cluster, pos=1, rot=0, scl=0)

        # parent spine_clusters under control
        if spine_clusters and rail_guides:
            try:
                for x in range(num_of_cvs):
                    cmds.parent(spine_clusters[x], rail_guides[x])
                    cmds.parent(rail_clusters[x], rail_guides[x])
            except Exception as e:
                print(f"Error during parenting: {e}")
        else:
            print("Either spine_clusters or rail_guides list is empty.")
        
        # position the guides:
        guide_pos = []
        for key, pos in component_pos.items():
                guide_pos.append(pos)
        
        print(f"guide_pos = {guide_pos} & rail_guides = {rail_guides}")
        for x in range(num_of_cvs):
                cmds.xform(rail_guides[x], translation=guide_pos[x], worldSpace=1)
        
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
        utils.connect_attr(f"{rail_guides[0]}.worldMatrix[0]", f"{mm_initialJoint}.matrixIn[0]")
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
        
        # -------
        u_list = self.get_u_value_list(gd_curve, jnt_num, node_name_convention)
        print(f"JJJJJJJ Module: `{module_name}` u_list = {u_list}")
        self.set_joint_values(jnt_num, u_list, ls_strechMulth, ls_remapVal, ls_condition)
        
        for curves in [gd_curve, rail_gd_curve]:
            cmds.hide(curves)
        
        return rail_guides, u_list


    def set_joint_values(self, jnt_num, u_list, ls_strechMulth, ls_remapVal, ls_condition):
        for x in range(jnt_num):
            cmds.setAttr(f"{ls_strechMulth[x]}.input1X", u_list[x])
            cmds.setAttr(f"{ls_remapVal[x]}.outputMax", u_list[x])
            cmds.setAttr(f"{ls_condition[x]}.colorIfTrueR", u_list[x])


    def get_u_value_list(self, curve, jnt_num, node_name_convention):
        u_list = []
        for x in range(0, jnt_num):
            cmds.select(cl=1)
            temp_jnt_name = f"temp_{x}{node_name_convention}"
            cmds.joint(n=temp_jnt_name)
            temp_moPath = cmds.pathAnimation( temp_jnt_name, c=curve, fractionMode=1 )
            cmds.cutKey( temp_moPath + ".u", time=() )
            cmds.setAttr((temp_moPath + ".u"), x * (1.0/(jnt_num-1)))
            u_val = cmds.getAttr(temp_moPath + ".u")
            u_list.append(u_val)
            cmds.delete( temp_jnt_name + ".tx", icn=1 )
            cmds.delete( temp_jnt_name + ".ty", icn=1 )
            cmds.delete( temp_jnt_name + ".tz", icn=1 )
            cmds.delete(temp_moPath)
            cmds.delete(temp_jnt_name)
        return u_list


    def cr_ctrls_rail_driven(
            self, typ, component_ctrls, ctrl_name_list, ctrl_grp_list, 
            curve_info_dict, module_name, unique_id, side, jnt_u_list=None):
        typ = f"{typ}_ctrls"
        ctrl_dict = component_ctrls[typ]

        node_name_convention = f"_{module_name}_{unique_id}_{side}"
        gd_curve = f"crv_gd{node_name_convention}"
        rail_gd_curve = f"crv_gdRail{node_name_convention}"
        
        ctrls_not_to_be_made = []
        current_ctrl_list = []
        current_grp_list = []
        
        for ctrl_name, ctrl_shape in ctrl_dict.items():
            if ctrl_shape == None:
                ctrls_not_to_be_made.append(ctrl_name)
            else:
                print(f"ctrl_shape:{ctrl_shape}")
                whole_ctrl_name = f"ctrl_{ctrl_name}_{unique_id}_{side}" # ctrl_fk_clavicle_0_L
                ctrl_name_list.append(whole_ctrl_name)
                import_ctrl = cr_ctrl.CreateControl(type=ctrl_shape, name=whole_ctrl_name)
                ctrl = import_ctrl.retrun_ctrl()
                current_ctrl_list.append(ctrl)                 
                
                # add Adjust_Pos attr!
                utils.add_float_attrib(ctrl, [f"Adjust_Pos"], [0, 1], True)

                moPath = f"MPATH_{ctrl_name}_{node_name_convention}"
                rail_moPath = f"MPATH_rail_{ctrl_name}_{node_name_convention}"
                utils.cr_node_if_not_exists(0, "motionPath", moPath, {"follow": 1, "worldUpType":1, "frontAxis": 0})
                utils.cr_node_if_not_exists(0, "motionPath", rail_moPath)

                compM = f"CM_{ctrl_name}_{node_name_convention}"
                rail_compM = f"CM_rail_{ctrl_name}_{node_name_convention}"
                utils.cr_node_if_not_exists(0, "composeMatrix", compM)
                utils.cr_node_if_not_exists(0, "composeMatrix", rail_compM)
                
                grp_name = n=f"gd_{whole_ctrl_name}"
                cmds.group(n=grp_name, em=1)

                # connect them (set uv value )
                print(f">> RAILmopath = {rail_moPath}")
                utils.connect_attr(f"{ctrl}.Adjust_Pos", f"{moPath}{utils.Plg.u_plg}")
                utils.connect_attr(f"{ctrl}.Adjust_Pos", f"{rail_moPath}{utils.Plg.u_plg}")

                utils.connect_attr(f"{gd_curve}{utils.Plg.wld_space_plg}", f"{moPath}{utils.Plg.geopath_plg}")
                utils.connect_attr(f"{rail_gd_curve}{utils.Plg.wld_space_plg}", f"{rail_moPath}{utils.Plg.geopath_plg}")
                
                utils.connect_attr(f"{rail_moPath}{utils.Plg.cmpM_ac_plg}", f"{rail_compM}{utils.Plg.inputT_plug}")
                utils.connect_attr(f"{rail_compM}{utils.Plg.out_mtx_plg}", f"{moPath}{utils.Plg.wld_up_mtx_plg}")
                
                utils.connect_attr(f"{moPath}{utils.Plg.cmpM_ac_plg}", f"{compM}{utils.Plg.inputT_plug}")
                utils.connect_attr(f"{moPath}{utils.Plg.rot_plg}", f"{compM}{utils.Plg.inputR_plug}")

                utils.connect_attr(f"{compM}{utils.Plg.out_mtx_plg}", f"{grp_name}{utils.Plg.opm_plg}")

                utils.colour_ctrls(ctrl_name_list, side)
                
                if ctrl_shape == "circle" or ctrl_shape == "octogan":
                    pass
                    # cmds.setAttr(f"{grp_name}.rotateZ", 90)
                
                # cmds.group(ctrl, n=grp_name)
                ctrl_grp_list.append(grp_name)
                current_grp_list.append(grp_name)
               
        # get the u value and set it!
        if jnt_u_list:
            print(f"o>>>>> CR ctrl typ = {typ} -> jnt_u_list == {jnt_u_list}")
            u_list = jnt_u_list
        else:
            print(f"o>>>>> CR ctrl typ = {typ} -> jnt_u_list == {jnt_u_list}")
            u_list = self.get_u_value_list(gd_curve, len(current_ctrl_list), node_name_convention)
        for x in range(len(current_ctrl_list)):
            cmds.setAttr(f"{current_ctrl_list[x]}.Adjust_Pos", u_list[x])
            cmds.matchTransform(current_ctrl_list[x], current_grp_list[x], pos=1, rot=1, scl=0)
            cmds.parent(current_ctrl_list[x], current_grp_list[x])
        
        for key, value_dict in curve_info_dict.items():
                utils.rebuild_ctrl(key, value_dict)


    def cr_ik_fk_controls(
            self, component_ctrls, ctrl_name_list, ctrl_grp_list, fk_ctrl_list, 
            guides, curve_info_dict, module_name, unique_id, side
            ):
        for ctrl_type, ctrl_dict in component_ctrls.items():
            for ctrl_name, ctrl_shape in ctrl_dict.items():
                whole_ctrl_name = f"ctrl_{ctrl_name}_{unique_id}_{side}" # ctrl_fk_clavicle_0_L
                ctrl_name_list.append(whole_ctrl_name)
                import_ctrl = cr_ctrl.CreateControl(type=ctrl_shape, name=whole_ctrl_name)
                ctrl = import_ctrl.retrun_ctrl()

                ctrl_part = utils.get_last_two_items_of_name(ctrl_name)
                ctrl_suffix = f"{ctrl_part}_{unique_id}_{side}"
                print(f"guides = {guides}")
                for guide in guides:
                    if guide.endswith(ctrl_suffix):
                        guide_pos = cmds.xform(guide, q=1, t=1, worldSpace=1)
                        cmds.xform(ctrl, t=guide_pos, worldSpace=1)
                        break
                print(f"ctrl suffix = {ctrl_suffix}") # xfm_guide_*bipedLeg_hip_0_L*

                utils.colour_ctrls(ctrl_name_list, side)

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

        # Rebuild the control:
        for key, value_dict in curve_info_dict.items():
            utils.rebuild_ctrl(key, value_dict)

        print(f"<>CTRL: without gd_{fk_ctrl_list[:-1]}") # gd_ctrl_fk_bpdHip_0_L
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




       


