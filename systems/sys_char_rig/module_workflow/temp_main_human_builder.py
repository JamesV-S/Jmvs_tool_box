
''' Without the Registry (single module build at a time)'''
'''
import importlib
from Jmvs_tool_box.systems.sys_char_rig.module_workflow import temp_main_human_builder

importlib.reload(temp_main_human_builder)
'''

# import the right classes
import importlib

# from data_managers import (module_data_manager)
from systems.sys_char_rig.module_workflow.data_managers import (module_data_manager)
from systems.sys_char_rig.module_workflow.builders import (
    build_root,
    build_spine,
    build_bipedArm
    )

importlib.reload(module_data_manager)
importlib.reload(build_root)
importlib.reload(build_spine)
importlib.reload(build_bipedArm)

# raw module-specific data
root_data = {
    "module_name":"root",
    "external_plg_dict": {
        "global_scale_grp":"grp_Outputs_root_0_M",
        "global_scale_atr":"globalScale",
        "base_plg_grp":None,
        "base_plg_atr":None,
        "hook_plg_grp":None,
        "hook_plg_atr":None
        },
    "output_hook_mtx_list": ["ctrl_fk_centre", "ctrl_fk_COG"],
    "skeleton_dict":{
        "skel_pos":{
            "rt":[0.0, 0.0, 0.0],
            "centre": [0.0, 0.0, 0.0],
            "COG":[0.0, 110.94277350608388, 3.4263498874367455]
            },
        "skel_rot":{
            "rt":[0.0, 0.0, 0.0],
            "centre": [0.0, 0.0, 0.0],
            "COG":[0.0, 0.0, 0.0]
            }
        },
    "fk_dict":{
        "fk_pos":{
            "ctrl_fk_root_rt_0_M":[0.0, 0.0, 0.0],
            "ctrl_fk_root_centre_0_M": [0.0, 0.0, 0.0],
            "ctrl_fk_root_COG_0_M":[0.0, 110.94277350608388, 3.4263498874367455]
            },
        "fk_rot":{
            "ctrl_fk_root_rt_0_M":[0.0, 0.0, 0.0],
            "ctrl_fk_root_centre_0_M": [0.0, 0.0, 0.0],
            "ctrl_fk_root_COG_0_M":[0.0, 0.0, 0.0]
            }
        },
    "ik_dict":{
        "ik_pos":{
            "ctrl_fk_root_rt_0_M": False,
            "ctrl_fk_root_centre_0_M": False,
            "ctrl_fk_root_COG_0_M": False
            },
        "ik_rot":{
            "ctrl_fk_root_rt_0_M": False,
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
        "global_scale_atr":"globalScale",
        "base_plg_grp":"grp_Outputs_root_0_M",
        "base_plg_atr":"mtx_root_ctrl_fk_centre",
        "hook_plg_grp":"grp_Outputs_root_0_M", 
        "hook_plg_atr":"mtx_root_ctrl_fk_COG"
        },
    "output_hook_mtx_list": ["jnt_skn_top", "jnt_skn_bottom"],
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
            'spine7' : [0.0, 0.0, 0.0]
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
            'ctrl_ik_spine_bottom_0_M': [0.0, 0.0, 0.0], 
            'ctrl_ik_spine_middle_0_M': [0.0, 0.0, 0.0], 
            'ctrl_ik_spine_top_0_M': [0.0, 0.0, 0.0]
            }
        },
    "axis_dict":{
        "prim":"Y", "scnd":"X", "wld":"Z"
        }
}

bipedArm_data = {
    "module_name":"bipedArm",
    "external_plg_dict": {
        "global_scale_grp":"grp_Outputs_root_0_M",
        "global_scale_atr":"globalScale",
        "base_plg_grp":"grp_Outputs_root_0_M",
        "base_plg_atr":"mtx_root_ctrl_fk_centre",
        "hook_plg_grp":"grp_Outputs_spine_0_M", 
        "hook_plg_atr":"mtx_spine_jnt_skn_top"
        },
    "output_hook_mtx_list": ["jnt_skn_wrist", "jnt_skn_lower5"],
    "skeleton_dict":{
        "skel_pos":{
            "clavicle":[2.44448507146776, 154.57145295222426, 4.459872829725054], 
            "shoulder":[19.021108627319336, 152.5847778320312, -3.6705198287963885],
            "elbow":[51.95222091674805, 151.27154541015625, -7.411651611328125],
            "wrist":[82.27891540527344, 151.65419006347656, -0.65576171875]
            },
        "skel_rot":{
            "clavicle":[-3.0037333819801293, 25.96554559489243, -6.834187725057292],
            "shoulder":[-0.2577070326177839, 6.4761835670879035, -2.2836406890784096], 
            "elbow":[-0.15718070963992195, -12.557766678467543, 0.7228865771539283],
            "wrist":[-0.04691076638914411, -12.440289615750016, -3.1178613803887054]
            }
        },
    "fk_dict":{
        "fk_pos":{
            'ctrl_fk_bipedArm_shoulder_0_L':[19.021108627319336, 152.5847778320312, -3.6705198287963885],
            'ctrl_fk_bipedArm_elbow_0_L':[51.95222091674805, 151.27154541015625, -7.411651611328125],
            'ctrl_fk_bipedArm_wrist_0_L':[82.27891540527344, 151.65419006347656, -0.65576171875]
            },
        "fk_rot":{
            'ctrl_fk_bipedArm_shoulder_0_L':[-0.2577070326177839, 6.4761835670879035, -2.2836406890784096], 
            'ctrl_fk_bipedArm_elbow_0_L':[-0.15718070963992195, -12.557766678467543, 0.7228865771539283],
            'ctrl_fk_bipedArm_wrist_0_L':[-0.04691076638914411, -12.440289615750016, -3.1178613803887054]
            }
        },
    "ik_dict":{
        "ik_pos":{
            'ctrl_ik_bipedArm_clavicle_0_L':[2.44448507146776, 154.57145295222426, 4.459872829725054],
            'ctrl_ik_bipedArm_shoulder_0_L':[19.021108627319336, 152.5847778320312, -3.6705198287963885],
            'ctrl_ik_bipedArm_elbow_0_L':[53.17503418460073, 147.03618221256727, -34.37697986989994],
            'ctrl_ik_bipedArm_wrist_0_L':[82.27891540527344, 151.65419006347656, -0.65576171875]
            },
        "ik_rot":{
            'ctrl_ik_bipedArm_clavicle_0_L':[0.0, 0.0, 0.0],
            'ctrl_ik_bipedArm_shoulder_0_L':[0.0, 0.0, 0.0],
            'ctrl_ik_bipedArm_elbow_0_L':[-72.84109068999213, 80.71528988472048, -73.89575036760148],
            'ctrl_ik_bipedArm_wrist_0_L':[-0.04691076638914411, -12.440289615750016, -3.1178613803887054]
            }
        },
    "axis_dict":{
        "prim":"X", "scnd":"Y", "wld":"Z"
        }
}

# Isolated module-specific data flow
''' 
1 time data processing. 
# '''
root_data_manager = module_data_manager.ModuleDataManager(root_data)
root_build = build_root.BuildRoot(root_data_manager)
# Manual build order
'''
`.build()` is a class function from the Build[ModuleName] class. 
# Root first
# Spine Second
'''
root_build.build()

# spine mdl
spine_data_manager = module_data_manager.ModuleDataManager(spine_data)
spine_build = build_spine.BuildSpine(spine_data_manager)
spine_build.build()

# # spine mdl
bipedArm_data_manager = module_data_manager.ModuleDataManager(bipedArm_data)
bipedArm_build = build_bipedArm.BuildBipedArm(bipedArm_data_manager)
bipedArm_build.build()




