

# import the two parent classes to inherit from
import importlib
import maya.cmds as cmds

# from data_managers import module_data_manager
from systems.sys_char_rig.module_system_solution_003.blueprints import module_blueprint
from systems.sys_char_rig.module_system_solution_003.mdl_systems import system_quadLeg

from utils import (
    utils
)
from systems.sys_char_rig import (
    cr_ctrl
)

importlib.reload(module_blueprint)
importlib.reload(system_quadLeg)
importlib.reload(utils)
importlib.reload(cr_ctrl)

class BuildQuadLeg(module_blueprint.ModuleBP, system_quadLeg.SystemQuadLeg):
    def __init__(self, data_manager):
        module_blueprint.ModuleBP.__init__(self, data_manager)
        system_quadLeg.SystemQuadLeg.__init__(self, data_manager)
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
        input_grp, output_grp = self.cr_input_output_groups()
        self.add_outputs_matrix_attr(output_grp, ["sknAnkle", "twistAnkle"])
        if cmds.objExists(self.dm.external_plg_dict['base_plg_grp']) and cmds.objExists(self.dm.external_plg_dict['hook_plg_grp']):
            print(F"running 'wire_input_grp()'")
            self.wire_input_grp(input_grp, self.dm.GLOBAL_SCALE_PLG, self.dm.BASE_MTX_PLG, self.dm.HOOK_MTX_PLG)

        self.group_ctrls(self.dm.fk_ctrl_list, "fk")
        self.group_ctrls(self.dm.ik_ctrl_list, "ik")

        self.cr_jnt_type_chain("fk", self.dm.skel_pos_dict, self.dm.skel_rot_dict)
        self.cr_jnt_type_chain("ik", self.dm.skel_pos_dict, self.dm.skel_rot_dict)

        # Phase 2 - Module-specific class functions in 'System[ModuleName]'
        self.wire_hook_limbRoot_setup(input_grp, self.dm.ik_ctrl_list, self.dm.ik_pos_dict, self.dm.ik_rot_dict)
        self.wire_fk_ctrl_setup(input_grp, self.dm.ik_ctrl_list[0], self.dm.fk_ctrl_list, self.dm.fk_pos_dict, self.dm.fk_rot_dict)
        
        self.logic_jnt_distances()
        # Phase 3 - Finalising
        # self.group_module(self.dm.mdl_nm, self.dm.unique_id, self.dm.side,
        #                    input_grp, output_grp, 
        #                    f"grp_ctrls_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}", 
        #                    f"grp_joints_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}", 
        #                    f"grp_logic_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}")