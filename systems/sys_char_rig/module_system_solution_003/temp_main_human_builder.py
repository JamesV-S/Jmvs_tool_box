
''' Without the Registry (single module build at a time)'''
'''
import importlib
from Jmvs_tool_box.systems.sys_char_rig.module_system_solution_003 import temp_main_human_builder

importlib.reload(temp_main_human_builder)
'''

# import the right classes
import importlib

# from data_managers import (module_data_manager)
from systems.sys_char_rig.module_system_solution_003.data_managers import (module_data_manager)
from systems.sys_char_rig.module_system_solution_003.builders import (
    build_root,
    build_spine 
    )

importlib.reload(module_data_manager)
importlib.reload(build_root)
importlib.reload(build_spine)

# raw module-specific data
root_data = {
    "module_name":"root",
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
            "root":[0.0, 0.0, 0.0],
            "centre": [0.0, 0.0, 0.0],
            "COG":[0.0, 110.94277350608388, 3.4263498874367455]
            },
        "skel_rot":{
            "root":[0.0, 0.0, 0.0],
            "centre": [0.0, 0.0, 0.0],
            "COG":[0.0, 0.0, 0.0]
            }
        },
    "fk_dict":{
        "fk_pos":{
            "ctrl_fk_root_root_0_M":[0.0, 0.0, 0.0],
            "ctrl_fk_root_centre_0_M": [0.0, 0.0, 0.0],
            "ctrl_fk_root_COG_0_M":[0.0, 110.94277350608388, 3.4263498874367455]
            },
        "fk_rot":{
            "ctrl_fk_root_root_0_M":[0.0, 0.0, 0.0],
            "ctrl_fk_root_centre_0_M": [0.0, 0.0, 0.0],
            "ctrl_fk_root_COG_0_M":[0.0, 0.0, 0.0]
            }
        },
    "ik_dict":{
        "ik_pos":{
            "ctrl_fk_root_root_0_M": False,
            "ctrl_fk_root_centre_0_M": False,
            "ctrl_fk_root_COG_0_M": False
            },
        "ik_rot":{
            "ctrl_fk_root_root_0_M": False,
            "ctrl_fk_root_centre_0_M": False,
            "ctrl_fk_root_COG_0_M": False
            }
        },
    "axis_dict":{
        "prim":"X", "scnd":"Y", "wld":"Z"
        }
}

spine_data = {
    "module_name":"spine",
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

# Isolated module-specific data flow
''' 
1 time data processing. 
'''
# root_data_manager = module_data_manager.ModuleDataManager(root_data)
# root_build = build_root.BuildRoot(root_data_manager)

# # Manual build order
# '''
# `.build()` is a class function from the Build[ModuleName] class. 
# # Root first
# # Spine Second
# '''
# root_build.build()

# spine mdl
spine_data_manager = module_data_manager.ModuleDataManager(spine_data)
spine_build = build_spine.BuildSpine(spine_data_manager)
spine_build.build()



