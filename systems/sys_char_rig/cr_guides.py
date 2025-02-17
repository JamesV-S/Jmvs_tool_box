
import maya.cmds as cmds
import importlib
import sys
import os

from systems import (
    os_custom_directory_utils,
    utils
)
from systems.sys_char_rig import (
    cr_ctrl
)
importlib.reload(os_custom_directory_utils)
importlib.reload(utils)
importlib.reload(cr_ctrl)

class CreateXfmGuides():
    def __init__(self, database_componment_dict):
        # 1) write an example dictionary to pass to this to make it work, then 
        # 2) write funtions in `char_ui` to gather necessary data from database, 
        # based off the selection in the ui!
        '''
        database_componment_dict = {
            "module_name":"bipedArm", 
            "unique_id":0,
            "side":"L", 
            "component_pos":{'clavicle': [3.9705319404602006, 230.650634765625, 2.762230157852166], 
                            'shoulder': [28.9705319404602, 230.650634765625, 2.762230157852166], 
                            'elbow': [49.96195602416994, 192.91743469238278, -8.43144416809082], 
                            'wrist': [72.36534118652347, 164.23757934570304, 15.064828872680739]
                            },
            "controls":{'FK_ctrls': 
                                {'fk_clavicle': 'circle', 'fk_shoulder': 'circle', 'fk_elbow': 'circle', 'fk_wrist': 'circle'}, 
                        'IK_ctrls': 
                                {'ik_clavicle': 'cube', 'ik_shoulder': 'cube', 'ik_elbow': 'pv', 'ik_wrist': 'cube'}
                        }                
            }
        '''
        print(f"crerating guide component for {database_componment_dict}")
        # self.component_pos_dict = {} 
        self.module_name = database_componment_dict['module_name']
        self.unique_id = database_componment_dict['unique_id']
        self.side = database_componment_dict['side']
        self.component_pos_dict = database_componment_dict['component_pos']
        self.component_controls_dict = database_componment_dict['controls']

        print(f"Working on `self.module_name`: {self.module_name}, `self.unique_id`: {self.unique_id}, `self.side`: {self.side}, `self.component_pos_dict`:{self.component_pos_dict}")
        self.guides = self.build_guide_components(self.module_name, self.unique_id, self.side, self.component_pos_dict, self.component_controls_dict)
        
        # self.build_control_components(self.guides, self.module_name, self.unique_id, self.side, self.component_controls_dict)


    def build_guide_components(self, module_name, unique_id, side, component_pos, component_ctrls):
        self.guide_import_dir =  os.path.join(os_custom_directory_utils.create_directory("Jmvs_tool_box", "imports" ), "imp_component_guide.abc")# 
        
        # import the guide & distribbute it to all necessary guides!    
        guides = []
        
        if module_name == "spine":
            print(f"Spine module detected: {module_name}")
            spine_guide_names = self.spine_guide_setup(module_name, unique_id, side, component_pos, component_ctrls)
            
        else:
            (f"Other module: {module_name}")
            for key, pos in component_pos.items():
                imported_guide = cmds.file(self.guide_import_dir, i=1, ns="component_guide", rnn=1)
                # esyablish guides, check for root module that acts differently
                if module_name == "root":
                    if cmds.objExists(f"xfm_guide_{module_name}"):
                        guide_name = f"xfm_guide_COG" # cog guide
                    else: # root guide
                        guide_name = f"xfm_guide_{module_name}"
                else:
                    guide_name = f"xfm_guide_{module_name}_{key}_{unique_id}_{side}"
                guides.append(cmds.rename(imported_guide[0], guide_name))
                cmds.xform(guide_name, translation=pos, worldSpace=1)
            
            ''''''
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

            # lock & hide scale & visibilty 
            for x in range(len(guides)):
                cmds.setAttr(f"{guides[x]}.sx", lock=1, keyable=0, channelBox=0)
                cmds.setAttr(f"{guides[x]}.sy", lock=1, keyable=0, channelBox=0)
                cmds.setAttr(f"{guides[x]}.sz", lock=1, keyable=0, channelBox=0)
                cmds.setAttr(f"{guides[x]}.v", lock=1, keyable=0, channelBox=0) 

            # ankle has extra guide helper for positioning    
            if module_name == "bipedLeg":
                leg_imp_ctrl = cr_ctrl.CreateControl(
                    type="bvSquare", name=f"xfm_guide_{module_name}_foot_{unique_id}_{side}")
                ankle_helper_ctrl = leg_imp_ctrl.retrun_ctrl()
                cmds.matchTransform(ankle_helper_ctrl, guides[2], pos=1, scl=0, rot=0)
                cmds.setAttr(f"{ankle_helper_ctrl}.translateY", 0)
                guides.append(ankle_helper_ctrl)
            
            guide_grp_list = []
            # group every Guide
            for guide in guides:
                offset_grp = cmds.group(n=f"offset_{guide}", em=1)
                print(f"{offset_grp} < {guide}")
                cmds.matchTransform(offset_grp, guide, pos=1, scl=0, rot=0)
                cmds.parent(guide, offset_grp)
                guide_grp_list.append(offset_grp)
            
            print(f"imported_guide = {imported_guide[0]}")

            #----------------------------------------------------------------------
            # group guides 
            gd_master_group = f"grp_xfm_components"
            if module_name == "root": 
                gd_component_grp_name = f"xfm_grp_{module_name}_component_{unique_id}_M"
            else:
                gd_component_grp_name = f"xfm_grp_{module_name}_component_{unique_id}_{side}"
            if not cmds.objExists(gd_component_grp_name):
                cmds.group(n=gd_component_grp_name, em=1)
            if not cmds.objExists(gd_master_group):
                cmds.group(n=gd_master_group, em=1)
            cmds.parent(guide_grp_list, gd_component_grp_name)
            cmds.parent(gd_component_grp_name, gd_master_group)
            cmds.select(cl=1)
            ''''''
        return guides

        
    def build_control_components(self, guides, module_name, unique_id, side, component_ctrls):
        #----------------------------------------------------------------------
        # create controls ontop
        # have a function that given the name of the control, creates it!
        ctrl_name_list = []
        ctrl_grp_list = []
        fk_ctrl_list = []
        for ctrl_type, ctrl_dict in component_ctrls.items():
            for ctrl_name, ctrl_shape in ctrl_dict.items():
                if module_name == "root":
                    whole_ctrl_name = f"ctrl_{ctrl_name}"
                else:
                    whole_ctrl_name = f"ctrl_{ctrl_name}_{unique_id}_{side}" # ctrl_fk_clavicle_0_L
                ctrl_name_list.append(whole_ctrl_name)
                import_ctrl = cr_ctrl.CreateControl(type=ctrl_shape, name=whole_ctrl_name)
                ctrl = import_ctrl.retrun_ctrl()
                print(f"CONTROL == {ctrl}")
                # scale up the ctrl for time being
                # cmds.scale(15, 15, 15, ctrl)
                # cmds.makeIdentity(ctrl, a=1, t=0, r=0, s=1, n=0, pn=1)

                # match the ctrl to the appropriate guide!F
                if module_name == "root":
                    ctrl_suffix = ctrl_name
                    print(f"ROOT mdl ctrl_suffix = {ctrl_suffix}")
                else:
                    ctrl_suffix = f"{ctrl_name[3:]}_{unique_id}_{side}"
                for guide in guides:
                    if guide.endswith(ctrl_suffix):
                        print(f"XFORM CTRL: {ctrl}")
                        guide_pos = cmds.xform(guide, q=1, t=1, worldSpace=1)
                        cmds.xform(ctrl, t=guide_pos, worldSpace=1)
                        print(f"ctrl to guide: {ctrl} > {guide}")
                        break
                
                # group all ctrls!
                cmds.group(ctrl, n=f"gd_{whole_ctrl_name}")
                ctrl_grp_list.append(f"gd_{whole_ctrl_name}")
                # point constrain the groups to the guides to follow
                # if not module_name == "root":
                for guide in guides:
                    if guide.endswith(ctrl_suffix):
                        print(f"HERE: gd_{whole_ctrl_name}", guide)
                        cmds.pointConstraint(guide, f"gd_{whole_ctrl_name}",  n=f"pCon_gd_{whole_ctrl_name}")
                        if ctrl_type == "FK_ctrls":
                            print(f" fk ctrls = {ctrl}")

                        break

                if ctrl_type == "FK_ctrls":
                    print(f" FK ctrls = {ctrl}")
                    fk_ctrl_list.append(ctrl)

        fk_ctrl_list0000 = ['ctrl_fk_clavicle_0_L', 'ctrl_fk_shoulder_0_L', 'ctrl_fk_elbow_0_L', 'ctrl_fk_wrist_0_L']
        guide_list = ['xfm_guide_bipedArm_clavicle_0_L', 'xfm_guide_bipedArm_shoulder_0_L', 'xfm_guide_bipedArm_elbow_0_L', 'xfm_guide_bipedArm_wrist_0_L']

        # xfm_guide_bipedArm
        print(f"ctrl_name_list = {ctrl_name_list}")
        print(f"fk ctrl_name_list = {fk_ctrl_list}")
        print(f"guides list = {guides}")
        if not module_name == "root":
            try:
                # aim constraint the groups of ctrls to guides so fk controls keep correct positions!
                for x in range(len(fk_ctrl_list)):
                    print(f"aim constrain {fk_ctrl_list[:-1][x]}, {guides[x+1]}")
                    cmds.aimConstraint(guides[x+1], f"gd_{fk_ctrl_list[:-1][x]}", n=f"pAim_{guides[x+1]}")
            except:
                pass
            # match end ctrl's grp to parent ctrl orientation.
            cmds.matchTransform(f"gd_{fk_ctrl_list[-1]}", fk_ctrl_list[-2], pos=0, rot=1, scl=0)
            cmds.orientConstraint(fk_ctrl_list[-2], f"gd_{fk_ctrl_list[-1]}")
            print(f"MATCH orientation gd_{fk_ctrl_list[-1]} TO:", fk_ctrl_list[-2])

        # colour
        for x in range(len(ctrl_name_list)):
            if not module_name == "root":
                if side == "L":
                    cmds.setAttr(f"{ctrl_name_list[x]}.overrideEnabled", 1)
                    cmds.setAttr(f"{ctrl_name_list[x]}.overrideColor", 13)
                elif side == "R":
                    cmds.setAttr(f"{ctrl_name_list[x]}.overrideEnabled", 1)
                    cmds.setAttr(f"{ctrl_name_list[x]}.overrideColor", 6)
                elif side == "M":
                    cmds.setAttr(f"{ctrl_name_list[x]}.overrideEnabled", 1)
                    cmds.setAttr(f"{ctrl_name_list[x]}.overrideColor", 17)
        if module_name == "root":
            pass # > do this at system 
            #utils.colour_root_control(fk_ctrl_list[0])
            #utils.colour_COG_control(fk_ctrl_list[1])
        
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
        

    def spine_guide_setup(self, module_name, unique_id, side, component_pos, component_ctrls):
        gd_curve = f"cv_guide_{module_name}_{unique_id}_{side}"
        # cr curve
        cmds.curve(n=gd_curve, d=3, p=[(-45, 0, 0), (-16.666667, 0, 0), (11.666667, 0, 0), (40, 0, 0)], k=[0, 0, 0, 1, 1, 1])
        #curve -d 3 -p -45 0 0 -p -16.666667 0 0 -p 11.666667 0 0 -p 40 0 0 -k 0 -k 0 -k 0 -k 1 -k 1 -k 1;
        
        #rebuildCurve -ch 1 -rpo 1 -rt 0 -end 1 -kr 0 -kcp 0 -kep 1 -kt 0 -s 3 -d 3 -tol 0.01 "curve1";
        # Rebuild it 
        cmds.rebuildCurve(gd_curve, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=0, kt=0, s=3, d=3, tol=0.01)

        
        # Cluster the CVs
        # gather all cvs on the curve
        crv_shape = cmds.listRelatives(gd_curve, shapes=True)[0]
        num_of_cvs = cmds.getAttr(f"{gd_curve}.spans") + cmds.getAttr(f"{gd_curve}.degree")
        gd_curve_cvs = [f"{gd_curve}.cv[{i}]" for i in range(num_of_cvs)]
        '''
        ['cv_guide_spine_0_M.cv[0]', 'cv_guide_spine_0_M.cv[1]', 
        'cv_guide_spine_0_M.cv[2]', 'cv_guide_spine_0_M.cv[3]', 
        'cv_guide_spine_0_M.cv[4]', 'cv_guide_spine_0_M.cv[5]']
        '''
        clusters = []
        for x in range(num_of_cvs):
            cluster_handle = cmds.cluster(f"{gd_curve}.cv[{x}]", n=f"cls{x}_guide_{module_name}_{unique_id}_{side}")[1]
            clusters.append(cluster_handle)
        print(f"clusters = {clusters}")

        # Create the controls!
        spine_guides = []
        for x in range(num_of_cvs):
                imported_guide = cmds.file(self.guide_import_dir, i=1, ns="component_guide", rnn=1)
                # esyablish guides, check for root module that acts differently
                guide_name = f"xfm_guide_{module_name}_{x}_{unique_id}_{side}"
                spine_guides.append(cmds.rename(imported_guide[0], guide_name))
        print(f"spine_guides = {spine_guides}")

        # position the guides to the clusters
        for cluster, guide in zip(clusters, spine_guides):
            cluster_pos = cmds.xform(cluster, q=True, ws=True, t=True)
            cmds.matchTransform(guide, cluster, pos=1, rot=0, scl=0)

        # parent the controls!
        # Check if lists are not empty and have expected values
        
        # parent clusters under control
        if clusters and spine_guides:
            try:
                for x in range(num_of_cvs):
                    cmds.parent(clusters[x], spine_guides[x])
            except Exception as e:
                print(f"Error during parenting: {e}")
        else:
            print("Either clusters or spine_guides list is empty.")
        
        # position the guides:
        guide_pos = []
        for key, pos in component_pos.items():
                guide_pos.append(pos)

        print(f"guide_pos = {guide_pos} & spine_guides = {spine_guides}")
        for x in range(num_of_cvs):
                cmds.xform(spine_guides[x], translation=guide_pos[x], worldSpace=1)

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
        // Parent the clusters to the guides
        // Move the guides to deisred position

        // Don't use 'connect_guide()', make the curve drive the ddj
        // Curve drive the fk & ik ctrls
        // the rail curve should be controled by 1 ctrl for the aiming of joints & ctrl orientation!
        '''
     

        