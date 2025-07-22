
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
        
        # parent module ori group to master ori grop in hierarchy!
        cmds.parent(ori_module_group, ori_master_grp)
    

    def cr_ori_guide(self):
        ori_parent_grp_list = []
        ori_guide_list = []
        for key, rot in self.comp_rot_dict.items():
            ori_guide = f"ori_{key}_{self.unique_id}_{self.side}"
            cr_ctrl.CreateControl(type="orb", name=ori_guide)
            utils.colour_object(ori_guide, 1)
            ori_guide_list.append(ori_guide)

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
        pass


    def ori_guide_attributes(self):
        pass
    

        