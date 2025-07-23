
import importlib
import maya.cmds as cmds
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

importlib.reload(utils)
importlib.reload(utils_os)
importlib.reload(cr_ctrl)
importlib.reload(database_schema_002)

class BuildOrientation():
    def __init__(self, comp_pos_dict, rig_db_directory, module, unique_id, side):
        pass
        # Need:
        # module name
        # unique id
        # side
        # component pos dict

        # build group named grp_ori_*_*_*_* (grp_ori_bipedArm_clavicle_0_L)
        # return this group!

        self.comp_pos_dict, self.rig_db_directory, self.module, self.unique_id, self.side = comp_pos_dict, rig_db_directory, module, unique_id, side
        retrieve_rot_data = database_schema_002.retrieveSpecificComponentdata(
            self.rig_db_directory, self.module, self.unique_id, self.side)
        self.comp_rot_dict = retrieve_rot_data.return_rot_component_dict()
        print(f"BuildOrientation: module = `{module}`/ unique_id = `{unique_id}` / side = `{side}` / comp_rot_dict = `{self.comp_rot_dict}`")
        
        # Initialise group hierarchy
        ori_master_grp = f"grp_ori_components"
        if not cmds.objExists(ori_master_grp):
            cmds.group(n=ori_master_grp, em=1)
        ori_module_group = f"grp_ori_{self.module}_{self.unique_id}_{self.side}"
        
        ori_parent_grp_list, ori_guide_list = self.cr_ori_guide()
        self.position_ori_groups(ori_module_group, ori_parent_grp_list)
        self.constrain_ori_groups(ori_parent_grp_list)
        ori_scale_attr = self.ori_guide_attributes(ori_guide_list)
        self.orient_guides(ori_guide_list)
        
        # parent module ori group to master ori grop in hierarchy!
        cmds.parent(ori_module_group, ori_master_grp)
        
        planes_dict = self.cr_geo_planes()
        plane_grp_list = self.group_geo_planes(planes_dict, ori_parent_grp_list)
        self.geo_plane_orient_connection(ori_guide_list, plane_grp_list)
        self.geo_planes_adjusting_length(planes_dict, ori_parent_grp_list, ori_scale_attr)
        self.locking_objects(ori_guide_list, plane_grp_list)

    def cr_ori_guide(self):
        ori_parent_grp_list = []
        ori_guide_list = []
        # for key, rot in self.comp_rot_dict.items():
        items = list(self.comp_rot_dict.items())
        for key, rot in items[:-1]:
            ori_guide = f"ori_{self.module}_{key}_{self.unique_id}_{self.side}"
            cr_ctrl.CreateControl(type="orb", name=ori_guide)
            utils.colour_object(ori_guide, 1)
            ori_guide_list.append(ori_guide)
            cmds.setAttr(f"{ori_guide}.displayLocalAxis", 1 )

            # group the ori guides idiviually
            ori_parent_grp = f"grp_ori_{self.module}_{key}_{self.unique_id}_{self.side}"
            cmds.group(ori_guide, n=ori_parent_grp)
            ori_parent_grp_list.append(ori_parent_grp)

        return ori_parent_grp_list, ori_guide_list


    def position_ori_groups(self, ori_module_group, ori_parent_grp_list):        
        # move ori_guides to match corresponding guide positions
        for ori_parent_grp in ori_parent_grp_list:
            for key, pos in self.comp_pos_dict.items():
                if key in ori_parent_grp:
                    cmds.xform(ori_parent_grp, translation=pos, worldSpace=1)

        # Add the ori groups to a parent grp
        if not cmds.objExists(ori_module_group):
                cmds.group(n=ori_module_group, em=1)
        for x in range(len(ori_parent_grp_list)):
            cmds.parent(ori_parent_grp_list[x], ori_module_group)


    def constrain_ori_groups(self, ori_parent_grp_list):       
        aim_guide_keys = [key for key, rot in list(self.comp_rot_dict.items())[1:]]
        point_guide_keys = [key for key, rot in list(self.comp_rot_dict.items())[:-1]]
        for x in range(len(ori_parent_grp_list)):
            a_guide_name = f"xfm_guide_{self.module}_{aim_guide_keys[x]}_{self.unique_id}_{self.side}"
            cmds.aimConstraint(a_guide_name, ori_parent_grp_list[x], n=f"pAim_{ori_parent_grp_list[x]}")

            p_guide_name = f"xfm_guide_{self.module}_{point_guide_keys[x]}_{self.unique_id}_{self.side}"
            cmds.pointConstraint(p_guide_name, ori_parent_grp_list[x],  n=f"pCon_gd_{ori_parent_grp_list[x]}")


    def ori_guide_attributes(self, ori_guide_list):
        planes_attr_name = f"Planes_Scale"
        for x in range(len(ori_guide_list)):
            utils.add_locked_attrib(ori_guide_list[x], ["ORI"])
            utils.add_float_attrib(ori_guide_list[x], [f"{planes_attr_name}"], [0.1, 999], True)
            cmds.setAttr(f"{ori_guide_list[x]}.{planes_attr_name}", 6)

        return planes_attr_name

    
    def orient_guides(self, ori_guide_list):
        for ori_guide in ori_guide_list:
            for key, rot in self.comp_rot_dict.items():
                if not rot == [0.0, 0.0, 0.0]:
                    if key in ori_guide:
                        cmds.xform(ori_guide, rotation=rot, worldSpace=1)

    
    def cr_geo_planes(self):
        # polyPlane -w 1 -h 1 -sx 1 -sy 1 -ax 0 0 1 -cuv 2 -ch 1;
        items = list(self.comp_rot_dict.items())
        planes_dict = {}
        print()
        for key, rot in items[:-1]:
            plane_A = f"pln_A_{self.module}_{key}_{self.unique_id}_{self.side}"
            plane_B = f"pln_B_{self.module}_{key}_{self.unique_id}_{self.side}"
            planes_dict[key] = [plane_A, plane_B]
            cmds.polyPlane(n=plane_A, w=1, h=1, sx=1, sy=1, ax=(0,0,1), cuv=2, ch=1)
            cmds.polyPlane(n=plane_B, w=1, h=1, sx=1, sy=1, ax=(0,1,0), cuv=2, ch=1)
            cmds.xform(plane_A, pivots=(-.5,0,0), ws=True)
            cmds.xform(plane_B, pivots=(-.5,0,0), ws=True)

        print(f"ORI Planes = {planes_dict}")
        return planes_dict
    
    
    def group_geo_planes(self, planes_dict, ori_parent_grp_list):
        print(F"GROUP GEO PLANES")
        # ori_parent_grp_list = ori_parent_grp_list[:-1]
        # create the groups for each key & match planes to corresponding ori grp
        plane_grp_list = []
        for key, plane_list in planes_dict.items():
            for ori_prnt in ori_parent_grp_list:
                print(f"key = `{key}` & ori_prnt = `{ori_prnt}`")
                if key in ori_prnt:
                    # make groups for key planes
                    pln_grp_name = f"grp_pln_{self.module}_{key}_{self.unique_id}_{self.side}"
                    plane_grp_list.append(pln_grp_name)
                    cmds.group(n=pln_grp_name, em=1)
                    cmds.matchTransform(pln_grp_name, ori_prnt)
                    cmds.parent(pln_grp_name, ori_prnt)

                    # match planes to the corresponding ori_parent ws
                    for plane in plane_list:
                        cmds.matchTransform(plane, pln_grp_name)
                        cmds.parent(plane, pln_grp_name)
                    print(f"plane_list = `{plane_list}`")
        
        print(f"plane_grp_list == `{plane_grp_list}`")
        # `['grp_pln_bipedArm_clavicle_0_L', 'grp_pln_bipedArm_shoulder_0_L', 'grp_pln_bipedArm_elbow_0_L']`
        return plane_grp_list
    

    def geo_plane_orient_connection(self, ori_guide_list, plane_grp_list):
        for x in range(len(ori_guide_list)):
            utils.connect_attr(f"{ori_guide_list[x]}.rotateX", f"{plane_grp_list[x]}.rotateX")


    def geo_planes_adjusting_length(self, planes_dict, ori_parent_grp_list, attrib):
        # needed data: | xfm_guides | distancebetween node | key planes
        current_xfm_keys = [key for key in list(planes_dict.keys())]
        next_xfm_keys = [key for key in list(self.comp_rot_dict.keys())[1:]]
        xfm_distance_guide_dict = {}
        for x in range(len(ori_parent_grp_list)):
            current_xfm = f"xfm_guide_{self.module}_{current_xfm_keys[x]}_{self.unique_id}_{self.side}"
            next_xfm = f"xfm_guide_{self.module}_{next_xfm_keys[x]}_{self.unique_id}_{self.side}"

            xfm_distance_guide_dict[current_xfm_keys[x]] = [current_xfm, next_xfm]
        
        '''
        {   key                                  Value
        'clavicle': ['pln_A_bipedArm_clavicle_0_L', 'pln_B_bipedArm_clavicle_0_L'], 
        'shoulder': ['pln_A_bipedArm_shoulder_0_L', 'pln_B_bipedArm_shoulder_0_L'], 
        'elbow': ['pln_A_bipedArm_elbow_0_L', 'pln_B_bipedArm_elbow_0_L']
        }
        
        NEED: | xfm_distance_guide_dict |
        {   key                                  Value
        'clavicle': [xfm_guide_bipedArm_clavicle_0_L', 'xfm_guide_bipedArm_shoulder_0_L'], 
        'shoulder': [xfm_guide_bipedArm_shoulder_0_L', 'xfm_guide_bipedArm_elbow_0_L'], 
        'elbow': [xfm_guide_bipedArm_elbow_0_L', 'xfm_guide_bipedArm_wrist_0_L']
        }

        '''
        
        # for each key, make distancebetween node!
        print(f"ORI: planes_dict = `{planes_dict}`")
        for (pln_key, pln_list_val), (xfm_key, xfm_list_val) in zip(planes_dict.items(), xfm_distance_guide_dict.items()):
            ori_guide = f"ori_{self.module}_{pln_key}_{self.unique_id}_{self.side}"
            # cr distancebetween
            dist_node = f"DIST_{self.module}_{pln_key}_{self.unique_id}_{self.side}"
            utils.cr_node_if_not_exists(1, "distanceBetween", dist_node)
            # connect distance up!
            inMatrix_index = [1, 2]
            for x in range(2):
                utils.connect_attr(f"{xfm_list_val[x]}{utils.Plg.wld_mtx_plg}", f"{dist_node}{utils.Plg.inMatrixs[inMatrix_index[x]]}")
                utils.connect_attr(f"{dist_node}{utils.Plg.distance_plg}", f"{pln_list_val[x]}.scaleX")
                # scale connection
                if "pln_A_" in pln_list_val[x]:
                    utils.connect_attr(f"{ori_guide}.{attrib}", f"{pln_list_val[x]}.scaleY")
                else:
                    utils.connect_attr(f"{ori_guide}.{attrib}", f"{pln_list_val[x]}.scaleZ")
                
 
    def locking_objects(self, ori_guide_list, plane_grp_list):
        AXIS = ['X', 'Y', 'Z']
        for ori_guide in ori_guide_list:
            for x in range(len(AXIS)):
                cmds.setAttr(f"{ori_guide}.translate{AXIS[x]}", lock=True, keyable=False, channelBox=False)
                cmds.setAttr(f"{ori_guide}.scale{AXIS[x]}", lock=True, keyable=False, channelBox=False)
            cmds.setAttr(f"{ori_guide}.rotateY", lock=True, keyable=False, channelBox=False)
            cmds.setAttr(f"{ori_guide}.rotateZ", lock=True, keyable=False, channelBox=False)
            cmds.setAttr(f"{ori_guide}.visibility", lock=True, keyable=False, channelBox=False)

        for plane_grp in plane_grp_list:
            cmds.setAttr(f"{plane_grp}.overrideEnabled", 1)
            cmds.setAttr(f"{plane_grp}.overrideDisplayType", 2)

