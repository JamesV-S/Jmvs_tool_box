

# import the two parent classes to inherit from
import importlib
import maya.cmds as cmds

# from data_managers import module_data_manager
from systems.sys_char_rig.module_workflow.blueprints import module_blueprint
from systems.sys_char_rig.module_workflow.mdl_systems import system_root

from utils import (
    utils
)
from systems.sys_char_rig import (
    cr_ctrl
)

importlib.reload(module_blueprint)
importlib.reload(system_root)
importlib.reload(utils)
importlib.reload(cr_ctrl)

class BuildRoot(module_blueprint.ModuleBP, system_root.SystemRoot):
    def __init__(self, data_manager):
        module_blueprint.ModuleBP.__init__(self, data_manager)
        system_root.SystemRoot.__init__(self, data_manager)
        print(f"-------  -------  --------  -------")
        print(f"Declared Build{self.dm.mdl_nm}")


    def build(self):
        '''
        # Description:
            Build Sequence to call:
            1. Foundation (ModuleBP)
            2. Module-specific (SystemRoot)
            3. Finalising (ModuleBP)
        # Attributes:
            module_name (string): name of this module.
            root_outputs_grp (string): 'Output' grp from other module for this one to follow.
            skeleton_dict (dict): (dict): key="skel_pos/rot"(string), value="skel_pos/rot"(dict).
            fk_dict (dict): (dict): key="fk_pos/rot"(string), value="fk_pos/rot"(dict).
            ik_dict (dict): (dict): key="ik_pos/rot"(string), value="ik_pos/rot"(dict).
        # Returns:N/A
        '''
        print(f"Running Build{self.dm.mdl_nm}.build()")
        
        # Phase 1 - Foundation
        root_input_grp, root_output_grp = self.cr_input_output_groups(True)
        self.add_outputs_matrix_attr(root_output_grp, ["ctrlCentre", "ctrlCOG"])
        self.group_ctrls(self.dm.fk_ctrl_list, "fk")

        # Phase 2 - Module-specific
        self.wire_root_setup(root_input_grp, self.dm.fk_ctrl_list, self.dm.skel_pos_dict, self.dm.skel_rot_dict)
        self.root_output_group_setup(self.dm.GLOBAL_SCALE_PLG, self.dm.BASE_MTX_PLG, self.dm.HOOK_MTX_PLG, self.dm.fk_ctrl_list[0], self.dm.fk_ctrl_list[1], self.dm.fk_ctrl_list[-1])
        
        # Phase 3 - Finalising
        self.group_module(module_name=self.dm.mdl_nm, unique_id=self.dm.unique_id, side=self.dm.side,
                           input_grp=root_input_grp, output_grp=root_output_grp,
                           ctrl_grp=f"grp_ctrls_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}", 
                           joint_grp=None,
                           logic_grp=None)

