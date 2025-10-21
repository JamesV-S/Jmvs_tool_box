
import importlib
import re
import maya.cmds as cmds
from utils import (
    utils
)
from systems.sys_char_rig import (
    cr_ctrl
)
importlib.reload(utils)
importlib.reload(cr_ctrl)

class ModuleBP:
    def __init__(self, **kwargs):
        '''
        # Description:
            Member functions responsible for consistent operations for all rig 
            modules. They gather data from the class
            - Cr the two input & ouput grp for the mdl.
            - Wire the two input & ouput grp for the mdl. (Called input func at beginning 
                & calls the output grp at the end.)
        # Attributes:
            self._data(dict): Centric data store. 
        # Returns: N/A
        '''

        # self._data = self._data
        self._data = kwargs
        self._validate_data()

        external_plg_dict = self._data['external_plg_dict']
        skeleton_dict = self._data['skeleton_dict']
        fk_dict = self._data['fk_dict']
        ik_dict = self._data['ik_dict']
        axis_dict = self._data['axis_dict']

        skeleton_pos_dict = skeleton_dict["skel_pos"]
        skeleton_rot_dict = skeleton_dict["skel_rot"]
        self.fk_pos_dict = fk_dict["fk_pos"]
        self.ik_pos_dict = ik_dict["ik_pos"]
        self.fk_rot_dict = fk_dict["fk_rot"]
        self.ik_rot_dict = ik_dict["ik_rot"]

        # return lists for storing control names!
        fk_ctrl_list = [key for key in self.fk_pos_dict.keys()]
        ik_ctrl_list = [key for key in self.ik_pos_dict.keys()]

        self.mdl_nm = self._data['module_name']
        self.unique_id = fk_ctrl_list[0].split('_')[-2]
        self.side = fk_ctrl_list[0].split('_')[-1]

        self.prim_axis = axis_dict['prim']

        # Plg data from 'external_plg_dict'.
        GLOBAL_SCALE_PLG = f"{external_plg_dict['global_scale_grp']}.{external_plg_dict['global_scale_attr']}" # grp_Outputs_root_0_M.globalScale
        BASE_MTX_PLG = f"{external_plg_dict['base_plg_grp']}.{external_plg_dict['base_plg_atr']}" # grp_Outputs_root_0_M.ctrl_centre_mtx
        HOOK_MTX_PLG = f"{external_plg_dict['hook_plg_grp']}.{external_plg_dict['hook_plg_atr']}" # grp_Outputs_spine_0_M.ctrl_spine_top_mtx
        self.global_scale_attr = external_plg_dict['global_scale_attr']
        

    def _validate_data(self):
        '''
        # Description:
            Ensures the required data is exists
        # Attributes:
        # Returns:
        '''
        required = ['module_name', 'external_plg_dict', 'skeleton_dict', 
                    'fk_dict', 'ik_dict', 'axis_dict']
        for field in required:
            if field not in self._data:
                raise ValueError(f"ModuleBP Missing field: {field}")


    def cr_input_output_groups(self, output_global=False):
        '''
        # Description:
            Creates the 'Input' & 'Output' groups for this module. These are 
            specialised nodes that store custom matrix data to allow the module 
            to be driven(Input) or be the driver(Output) for other modules, etc. 
        # Attributes:
            output_global (boolean): If True, add globalScale attr to the output group.
        # Returns:
            input_grp (string): Group for input data for this module.
            outputs_grp (string): Group for Ouput data for this module.
        '''
        # create input & output groups
        input_grp = f"grp_Inputs_{self.mdl_nm}_{self.unique_id}_{self.side}"
        outputs_grp = f"grp_Outputs_{self.mdl_nm}_{self.unique_id}_{self.side}"
        utils.cr_node_if_not_exists(0, "transform", input_grp)
        utils.cr_node_if_not_exists(0, "transform", outputs_grp)
        
        # Input grp
        utils.add_float_attrib(input_grp, [self.global_scale_attr], [0.01, 999], True) 
        cmds.setAttr(f"{input_grp}.{self.global_scale_attr}", 1, keyable=0, channelBox=0)
        utils.add_attr_if_not_exists(input_grp, "base_mtx", 'matrix', False)
        utils.add_attr_if_not_exists(input_grp, "hook_mtx", 'matrix', False)
        
        if output_global:
            utils.add_float_attrib(outputs_grp, [self.global_scale_attr], [0.01, 999], True)
            cmds.setAttr(f"{outputs_grp}.{self.global_scale_attr}", 1, keyable=0, channelBox=0)
        
        return input_grp, outputs_grp
    

    def add_outputs_matrix_attr(self, outputs_grp, out_matrix_name_list):
        '''
        # Description:
            Add custom matrix to ouptut group -> this matrix lets other modules follow.
        # Attributes:
            outputs_grp (string): Outputgrpup for this module. 
            out_matrix_name_list (list): List of names for matrix attr.
        # Returns: N/A
        '''
        for mtx_name in out_matrix_name_list:
            utils.add_attr_if_not_exists(outputs_grp, 
                                         f"mtx_{self.mdl_nm}_{mtx_name}", 
                                        'matrix', False)


    def wire_input_grp(self, input_grp, global_scale_plg, base_mtx_plg, hook_mtx_plg):
        '''
        # Description:
            Connect the 'global_scale', 'base_mtx', and 'hook_mtx' plugs (retrieved 
            from 'external_plg_dict' and plug into the corresponding plug in the 
            Input grp!)
        # Attributes:
            input_grp (string): Outputgrpup for this module.
            global_scale_plg (plug): External glabal scale attr plug
            base_mtx_plg (plug): External base matrix attr plug
            hook_mtx_plg (plug): External hook matrix attr plug
        # Returns:N/A
        '''
        # connect the global scale
        utils.connect_attr(global_scale_plg, f"{input_grp}.globalScale")
        # connect the base plug
        utils.connect_attr(base_mtx_plg, f"{input_grp}.base_mtx")
        # connect the hook plug
        utils.connect_attr(hook_mtx_plg, f"{input_grp}.hook_mtx")


    def group_ctrls(self, ctrl_ls, ctrl_type):
        '''
        # Description:
            Creates control group for a list of ctrls.
        # Attributes:
            ctrl_ls (list): list of given controls.
            ctrl_type (string): Name for the ctrl_grp.
        # Returns:N/A
        '''
        # If the parent ctrl_grp doesn't exist make it:
        module_control_grp = f"grp_ctrls_{self.mdl_nm}_{self.unique_id}_{self.side}"
        if not cmds.objExists(module_control_grp):
            utils.cr_node_if_not_exists(0, "transform", module_control_grp)

        child_ctrl_grp = f"grp_ctrl_{ctrl_type}_{self.mdl_nm}_{self.unique_id}_{self.side}"
        utils.cr_node_if_not_exists(0, "transform", child_ctrl_grp)

        for ctrl in ctrl_ls:
            cmds.parent(ctrl, child_ctrl_grp)
        cmds.parent(child_ctrl_grp, module_control_grp)
        cmds.select(cl=1)


# Module-specific data = Dictionary stroring:
    # module_name | external_plg_dict | skeleton_dict 
    # fk_ctrl_dict | ik_ctrl_dict | axis_dict
spine_data = {
    "module_name":"Spine",
    "external_plg_dict": {
        "global_scale_grp":"grp_Outputs_root_0_M",
        "global_scale_attr":"globalScale",
        "base_plg_grp":"grp_Outputs_root_0_M",
        "base_plg_atr":"mtx_root_ctrlCentre",
        "hook_plg_grp":"grp_Outputs_root_0_M", 
        "hook_plg_atr":"mtx_root_ctrlCOG"
        },
    "skeleton_dict":{
        "skel_pos":{
            'spine0' : [0.0, 108.51357426399493, 3.0], 
            'spine1' : [0.0, 114.54568615397002, 3.0],
            'spine2' : [0.0, 119.80152392711072, 3.0],
            'spine3' : [0.0, 124.6437390246307, 3.0],
            'spine4' : [0.0, 129.42469282205994, 3.0],
            'spine5' : [0.0, 134.25999009941637, 3.0],
            'spine6' : [0.0, 139.02848563616715, 3.0],
            'spine7' : [0.0, 143.59873962402344, 3.0]
            },
        "skel_rot":{
            'spine0' : [0.0, 0.0, 0.0], 
            'spine1' : [0.0, 0.0, 0.0], 
            'spine2' : [0.0, 0.0, 0.0], 
            'spine3' : [0.0, 0.0, 0.0], 
            'spine4' : [0.0, 0.0, 0.0], 
            'spine5' : [0.0, 0.0, 0.0], 
            'spine6' : [0.0, 0.0, 0.0], 
            'spine7' : [0.0, 0.0, 0.0], 
            'spine8' : [0.0, 0.0, 0.0], 
            'spine9' : [0.0, 0.0, 0.0]
            }
        },
    "fk_dict":{
        "fk_pos":{
            'ctrl_fk_spine_spine0_0_M': [0.0, 108.51357426399493, 3.0], 
            'ctrl_fk_spine_spine1_0_M': [0.0, 119.80152392711072, 3.0], 
            'ctrl_fk_spine_spine2_0_M': [0.0, 129.42469282205994, 3.0]
            },
        "fk_rot":{
            'ctrl_fk_spine_spine0_0_M': [0.0, 0.0, 0.0], 
            'ctrl_fk_spine_spine1_0_M': [0.0, 0.0, 0.0], 
            'ctrl_fk_spine_spine2_0_M': [0.0, 0.0, 0.0]
            }
        },
    "ik_dict":{
        "ik_pos":{
            'ctrl_ik_spine_spine_bottom_0_M': [0.0, 108.51357426399493, 3.0], 
            'ctrl_ik_spine_spine_middle_0_M': [0.0, 128.5, 3.0], 
            'ctrl_ik_spine_spine_top_0_M': [0.0, 143.59873962402344, 3.0]
            },
        "ik_rot":{
            'ctrl_ik_spine_spine_bottom_0_M': [0.0, 0.0, 0.0], 
            'ctrl_ik_spine_spine_middle_0_M': [0.0, 0.0, 0.0], 
            'ctrl_ik_spine_spine_top_0_M': [0.0, 0.0, 0.0]
            }
        },
    "axis_dict":{
        "prim":"X", "scnd":"Y", "wld":"Z"
        }
}