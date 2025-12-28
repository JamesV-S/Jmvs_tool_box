import importlib
import maya.cmds as cmds
from utils import (
    utils,
    utils_os,
    utils_json,
    utils_QTree
)
from databases.char_databases import (
    database_schema_002
    )
importlib.reload(utils)
importlib.reload(utils_os)
importlib.reload(database_schema_002)
'''
import importlib
from Jmvs_tool_box.systems.sys_char_rig import raw_data_module_manager

importlib.reload(raw_data_module_manager)
'''

'''
To Pass to the class:
- Component module name like bipedArm_0_L. 
- Rig folder directory. 

> Searches rig folder directory for appropriate database to retrieve raw data 
    from.
'''

class RawDataDict:
    def __init__(self, mdl_component_name, rig_folder):
        ''' 
        The template for the raw data dict.
        '''
        # store module name
        # store unique_id
        # store side
        self.rig_folder = rig_folder
        self.mdl_name, self.unique_id, self.side = utils.get_name_id_data_from_component(mdl_component_name) 

        print(f"self.mdl_name = {self.mdl_name}")
        print(f"self.unique_id = {self.unique_id}")
        print(f"self.side = {self.side}")

        self.raw_data = {
            "module_name":"",
            "external_plg_dict": {
                "global_scale_grp":"",
                "global_scale_atr":"",
                "base_plg_grp":"",
                "base_plg_atr":"",
                "hook_plg_grp":"",
                "hook_plg_atr":""
                },
            "output_hook_mtx_list": [],
            "skeleton_dict":{
                "skel_pos":{},
                "skel_rot":{}
                },
            "fk_dict":{
                "fk_pos":{},
                "fk_rot":{}
                },
            "ik_dict":{
                "ik_pos":{},
                "ik_rot":{}
                },
            "axis_dict":{
                "prim":"X", "scnd":"Y", "wld":"Z"
                }
        }


class CheckModulesData(RawDataDict): # check the data with 'modules' tab, if they're the same then continue with the process. 
    def __init__(self, mdl_component_name, rig_folder):
        super().__init__(mdl_component_name, rig_folder)
        '''
        Get external_plg_dict data.
        - 
        '''


class GetExternalPlgDict(RawDataDict): 
    def __init__(self, mdl_component_name, rig_folder):
        super().__init__(mdl_component_name, rig_folder)
        '''
        Get neccesarry data.
        '''
        self.ext_plg_dict = self.raw_data['external_plg_dict']
        print(f"ext_plg_dict = {self.ext_plg_dict}")

        self.set_global_scale_plg()
        self.set_base_plg()
        self.set_hook_plg()
    
    def set_global_scale_plg(self):
        # global scale plug: 
        self.ext_plg_dict['global_scale_grp'] = "grp_Outputs_root_0_M"
        self.ext_plg_dict['global_scale_atr'] = "globalScale"


    def set_base_plg(self):
        # base mtx plg
        if not self.mdl_name == 'root':
            self.ext_plg_dict['base_plg_grp'] = "grp_Outputs_root_0_M"
            self.ext_plg_dict['base_plg_atr'] = "mtx_root_ctrl_fk_centre"
        else:
            self.ext_plg_dict['base_plg_grp'] = None
            self.ext_plg_dict['base_plg_atr'] = None


    def set_hook_plg(self):
        # hook mtx plg
        if self.mdl_name == 'root':
            self.ext_plg_dict['hook_plg_grp'] = None
            self.ext_plg_dict['hook_plg_atr'] = None
        else:
            # get the hook data from the db!
            rig_db_directory = utils_os.create_directory(
                "Jmvs_tool_box", "databases", "char_databases", 
                "db_rig_storage", self.rig_folder
                )
            get_mtx_mdl_data = database_schema_002.RetrieveMtxModuleData(
                rig_db_directory, self.mdl_name, self.unique_id, self.side
                )
            db_inp_hook_mtx_ls = get_mtx_mdl_data.return_inp_hk_mtx()

            print(f"db_inp_hook_mtx_ls = {db_inp_hook_mtx_ls}") # ['spine.jnt_skn_bottom']

            # retrieve the data from the inp_mtx_plg_list(there can be more than 1)
            hook_grp_ls = []
            hook_atr_ls = []
            for inp_plg in db_inp_hook_mtx_ls:
                split = inp_plg.split('.')
                hook_grp = f"grp_Outputs_{split[0]}_0_M" # &! '_0_M' is temp and should be a part of the name regardless
                hook_atr = f"mtx_{split[0]}_{split[-1]}"
                hook_grp_ls.append(hook_grp)
                hook_atr_ls.append(hook_atr)

            print(f"hook_grp_ls = {hook_grp_ls}")
            print(f"hook_grp_ls = {hook_atr_ls}")

            # if ls > 1: add data into lists [for the moduleBluePrint to check for (if is list then there r mu;ltiple hook_mtx's)].
            # else: just add the string. 
            hook_plg_grp = ""
            hook_plg_atr = ""
            if len(hook_grp_ls) > 1 or len(hook_atr_ls) > 1:
                hook_plg_grp = []
                hook_plg_atr = []
                for x in range(len(hook_grp_ls)):
                    hook_plg_grp.append(hook_grp_ls[x])
                    hook_plg_atr.append(hook_atr_ls[x])
            else:
                hook_plg_grp = hook_grp_ls[0]
                hook_plg_atr = hook_atr_ls[0]

            # Add the hook data to the 'external_plg_dict'.
            self.ext_plg_dict['hook_plg_grp'] = hook_plg_grp
            self.ext_plg_dict['hook_plg_atr'] = hook_plg_atr

            
    def return_ext_plg_dict(self):
        return self.ext_plg_dict


class GetOutputPlgList(RawDataDict):
    def __init__(self, mdl_component_name, rig_folder):
        super().__init__(mdl_component_name, rig_folder)

        self.output_hook_mtx_list = self.raw_data['output_hook_mtx_list']

        # self.output_hook_mtx_list = [f"Hello.there"]
        self.set_out_plg()


    def set_out_plg(self):
            rig_db_directory = utils_os.create_directory(
                "Jmvs_tool_box", "databases", "char_databases", 
                "db_rig_storage", self.rig_folder
                )
            get_mtx_mdl_data = database_schema_002.RetrieveMtxModuleData(
                rig_db_directory, self.mdl_name, self.unique_id, self.side
                )
            self.output_hook_mtx_list = get_mtx_mdl_data.return_out_hk_mtx()


    def return_output_hook_mtx_list(self):
        return self.output_hook_mtx_list


class GetSkelDicts(RawDataDict):
    def __init__(self, mdl_component_name, rig_folder):
        super().__init__(mdl_component_name, rig_folder)
        
        self.skel_dict = self.raw_data['skeleton_dict']
        self.set_skel_pos_rot()


    def set_skel_pos_rot(self):
        rig_db_directory = utils_os.create_directory(
                "Jmvs_tool_box", "databases", "char_databases", 
                "db_rig_storage", self.rig_folder
                )
        get_comp_pos_data = database_schema_002.RetrievePlacementData(
            rig_db_directory, self.mdl_name, self.unique_id, self.side
            )
        self.skel_dict['skel_pos'] = get_comp_pos_data.return_existing_pos_dict()
        self.skel_dict['skel_rot'] = get_comp_pos_data.return_existing_rot_dict()
        print(f"skel_pos = {self.skel_dict['skel_pos']}")
        print(f"skel_rot = {self.skel_dict['skel_rot']}")

    def return_skel_dict(self):
        return self.skel_dict


class GetFkIkDicts(RawDataDict):
    def __init__(self, mdl_component_name, rig_folder):
        super().__init__(mdl_component_name, rig_folder)
        
        self.fk_dict = self.raw_data['fk_dict']
        self.ik_dict = self.raw_data['ik_dict']

        rig_db_directory = utils_os.create_directory(
                        "Jmvs_tool_box", "databases", "char_databases", 
                        "db_rig_storage", self.rig_folder
                        )
        self.get_control_data = database_schema_002.RetrieveControlsData(
            rig_db_directory, self.mdl_name, self.unique_id, self.side
            )
        
        self.set_fk_pos_rot()
        self.set_ik_pos_rot()

    def set_fk_pos_rot(self):
        # get the base dicts.
        fk_pos = self.get_control_data.return_fk_pos_dict()
        fk_rot = self.get_control_data.return_fk_rot_dict()
        # Add correct namespace.
        fk_pos = {f"ctrl_{k}_{self.unique_id}_{self.side}": v for k, v in fk_pos.items()}
        fk_rot = {f"ctrl_{k}_{self.unique_id}_{self.side}": v for k, v in fk_rot.items()}
        # add to raw_data dict.
        self.fk_dict['fk_pos'] = fk_pos
        self.fk_dict['fk_rot'] = fk_rot
    
        print(f"& fk_pos :: {self.fk_dict['fk_pos']} ")
        print(f"& fk_pos :: {self.fk_dict['fk_rot']} ")


    def set_ik_pos_rot(self):
        # get the base dicts.
        ik_pos = self.get_control_data.return_ik_pos_dict()
        ik_rot = self.get_control_data.return_ik_rot_dict()
        # Add correct namespace.
        ik_pos = {f"ctrl_{k}_{self.unique_id}_{self.side}": v for k, v in ik_pos.items()}
        ik_rot = {f"ctrl_{k}_{self.unique_id}_{self.side}": v for k, v in ik_rot.items()}
        # add to raw_data dict.
        self.ik_dict['ik_pos'] = ik_pos
        self.ik_dict['ik_rot'] = ik_rot
    
        print(f"& ik_pos :: {self.ik_dict['ik_pos']} ")
        print(f"& ik_pos :: {self.ik_dict['ik_rot']} ")


    def return_fk_ik_pos_rot(self):
        return self.fk_dict, self.ik_dict


class RawDataManager(RawDataDict):
    def __init__(self, mdl_component_name, rig_folder):
        super().__init__(mdl_component_name, rig_folder)
        '''
        Add the various data to 'self.raw_data'.
        '''
        print("--------------------------------------------------------------")
        
        # go down the dicrionary & update it. 
        self.raw_data['module_name'] = self.mdl_name
        print(f"*RD raw data module_name = {self.raw_data['module_name']}")
        
        get_ext_plg_dict = GetExternalPlgDict(mdl_component_name, rig_folder)
        self.raw_data['external_plg_dict'] = get_ext_plg_dict.return_ext_plg_dict()
        print(f"*RD ext_plg_dict = {self.raw_data['external_plg_dict']}")
        
        get_out_mtx_list = GetOutputPlgList(mdl_component_name, rig_folder)
        self.raw_data['output_hook_mtx_list'] = get_out_mtx_list.return_output_hook_mtx_list()
        print(f"*RD output_hook_mtx_list = {self.raw_data['output_hook_mtx_list']}")

        get_skel_dicts = GetSkelDicts(mdl_component_name, rig_folder)
        skeleton_dict = get_skel_dicts.return_skel_dict()
        self.raw_data['skeleton_dict'] = skeleton_dict

        fkik_posrot = GetFkIkDicts(mdl_component_name, rig_folder)
        fk_dict, ik_dict = fkik_posrot.return_fk_ik_pos_rot()
        self.raw_data['fk_dict'] = fk_dict
        self.raw_data['ik_dict'] = ik_dict
        
        print(f"*RD raw_data_{self.mdl_name}_{self.unique_id}_{self.side} = {self.raw_data}")


RawDataManager("bipedArm_0_L", "DB_jmvs_testing_rig")

# Fixes to raw_data_ikfk_posrot script:
    # - [0.0, 0.0, 0.0] on ik_clav & ik_rot (all limb modules).
    # - remove fk clavicle from fk pos (biped/QuadArm) .