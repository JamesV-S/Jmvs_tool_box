
''' Without the Registry (single module build at a time)'''
'''
import importlib
from Jmvs_tool_box.systems.sys_char_rig.module_workflow import temp_mian_lion_builder

importlib.reload(temp_mian_lion_builder)
'''

# import the right classes
import importlib

# from data_managers import (module_data_manager)
from systems.sys_char_rig.module_workflow.data_managers import (module_data_manager)
from systems.sys_char_rig.module_workflow.builders import (
    build_root,
    build_spine, 
    build_quadLeg
    )

importlib.reload(module_data_manager)
importlib.reload(build_root)
importlib.reload(build_spine)
importlib.reload(build_quadLeg)

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
            "rt": [0.0, 0.0, 0.0],
            "centre": [0.0, 0.0, 0.0],
            "COG": [0.0, 65.0, 0.0]
            },
        "skel_rot":{
            "rt": [0.0, 0.0, 0.0],
            "centre": [0.0, 0.0, 0.0],
            "COG": [0.0, 0.0, 0.0]
            }
        },
    "fk_dict":{
        "fk_pos":{
            "ctrl_fk_root_rt_0_M": [0.0, 0.0, 0.0],
            "ctrl_fk_root_centre_0_M": [0.0, 0.0, 0.0],
            "ctrl_fk_root_COG_0_M": [0.0, 65.0, 0.0]
            },
        "fk_rot":{
            "ctrl_fk_root_rt_0_M": [0.0, 0.0, 0.0],
            "ctrl_fk_root_centre_0_M": [0.0, 0.0, 0.0],
            "ctrl_fk_root_COG_0_M": [0.0, 0.0, 0.0]
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
            'spine0': [0.0, 80.93791961669922, -33.59365463256836], 
            'spine1': [0.0, 81.17710889685091, -22.065891164099135], 
            'spine2': [0.0, 80.93536173489014, -10.538301453894608], 
            'spine3': [0.0, 80.15486508447295, 0.9651388224358417], 
            'spine4': [0.0, 78.7653854024847, 12.41069218727593], 
            'spine5': [0.0, 76.86710737169409, 23.78384710808872], 
            'spine6': [0.0, 74.7497459420233, 35.11885092993744], 
            'spine7': [0.0, 72.63502366683598, 46.45413490035679]
            },
        "skel_rot":{
            'spine0': [0.0, -91.18865815650966, -90.0], 
            'spine1': [0.0, -88.79861597717976, -90.0], 
            'spine2': [0.0, -86.11848885858963, -90.0], 
            'spine3': [0.0, -83.0782161077253, -90.0], 
            'spine4': [0.0, -80.52418794336602, -90.0], 
            'spine5': [0.0, -79.41919280636799, -90.0], 
            'spine6': [0.0, -79.42944934192094, -90.0], 
            'spine7': [0.0, -79.42944934192093, -90.0]}
        },
    "fk_dict":{
        "fk_pos":{
            'ctrl_fk_spine_spine0_0_M': [0.0, 80.93791961669922, -33.59365463256836], 
            'ctrl_fk_spine_spine1_0_M': [0.0, 80.93536173489014, -10.538301453894608], 
            'ctrl_fk_spine_spine2_0_M': [0.0, 76.86710737169409, 23.78384710808872]
            },
        "fk_rot":{
            'ctrl_fk_spine_spine0_0_M': [0.0, -91.18865815650966, -90.0], 
            'ctrl_fk_spine_spine1_0_M': [0.0, -86.11848885858963, -90.0], 
            'ctrl_fk_spine_spine2_0_M': [0.0, -79.41919280636799, -90.0]
            }
        },
    "ik_dict":{
        "ik_pos":{
            'ctrl_ik_spine_bottom_0_M': [0.0, 80.93791961669922, -33.59365463256836], 
            'ctrl_ik_spine_middle_0_M': [4.867957440048162e-15, 79.35285659322577, 4.382755211832176],
            'ctrl_ik_spine_top_0_M': [0.0, 72.63502366683598, 46.45413490035679]
            },
        "ik_rot":{
            'ctrl_ik_spine_bottom_0_M': [0.0, -91.18865815650966, -90.0], 
            'ctrl_ik_spine_middle_0_M': [4.17290486988409, -83.45439685986587, -90.0], 
            'ctrl_ik_spine_top_0_M': [0.0, -79.42944934192093, -90.0] # [-83.05738785592176, -79.75815644450279, -90.01607472073135]
            }
        },
    "axis_dict":{
        "prim":"X", "scnd":"Z", "wld":"Y"
        }
}

quadLeg_data = {
    "module_name":"quadLeg",
    "external_plg_dict": {
        "global_scale_grp":"grp_Outputs_root_0_M",
        "global_scale_atr":"globalScale",
        "base_plg_grp":"grp_Outputs_root_0_M",
        "base_plg_atr":"mtx_root_ctrl_fk_centre",
        "hook_plg_grp":"grp_Outputs_spine_0_M", 
        "hook_plg_atr":"mtx_spine_jnt_skn_bottom"
        },
    "output_hook_mtx_list": ["jnt_skn_ankle"],
    "skeleton_dict":{
        "skel_pos":{
            'rump': [5.353, 73.17778605595966, -41.283461318628305],
            'hip': [9.427100479531633, 73.17778605595966, -41.283461318628305], 
            'knee': [10.34594475222716, 45.31456132216192, -30.942341550811438], 
            'calf': [8.381440943844233, 20.335971998048286, -47.07023669736204], 
            'ankle': [8.17389538574193, 5.737959787060513, -44.06889043484146], 
            'ball': [9.241848087805904, 4.592991784562416, -38.86664582300684], 
            'end': [10.15430720015248, -0.06079745326662156, -34.735633685929784]
            },
        "skel_rot":{
            'rump': [0.0, 0.0, 0.0],
            'hip': [84.952120068356, -20.35168168884181, -88.11124419294283], 
            'knee': [83.51738586220513, 32.768618974963445, -94.49691374978813], 
            'calf': [81.68986907996045, -11.616952223402174, -90.81454127018631], 
            'ankle': [46.74101795216688, -73.24979121317386, -46.99323518291281], 
            'ball': [74.81562730475041, -41.05850090352503, -78.90685296138632], 
            'end': [74.81562730475041, -41.05850090352503, -78.90685296138632]
            }
        },
    "fk_dict":{
        "fk_pos":{
            'ctrl_fk_quadLeg_hip_0_L': [9.427100479531633, 73.17778605595966, -41.283461318628305], 
            'ctrl_fk_quadLeg_knee_0_L': [10.34594475222716, 45.31456132216192, -30.942341550811438], 
            'ctrl_fk_quadLeg_calf_0_L': [8.381440943844233, 20.335971998048286, -47.07023669736204], 
            'ctrl_fk_quadLeg_ankle_0_L': [8.17389538574193, 5.737959787060513, -44.06889043484146], 
            'ctrl_fk_quadLeg_ball_0_L': [9.241848087805904, 4.592991784562416, -38.86664582300684], 
            },
        "fk_rot":{
            'ctrl_fk_quadLeg_hip_0_L': [84.952120068356, -20.35168168884181, -88.11124419294283], 
            'ctrl_fk_quadLeg_knee_0_L': [83.51738586220513, 32.768618974963445, -94.49691374978813], 
            'ctrl_fk_quadLeg_calf_0_L': [81.68986907996045, -11.616952223402174, -90.81454127018631], 
            'ctrl_fk_quadLeg_ankle_0_L': [46.74101795216688, -73.24979121317386, -46.99323518291281], 
            'ctrl_fk_quadLeg_ball_0_L': [74.81562730475041, -41.05850090352503, -78.90685296138632]
            }
        },
    "ik_dict":{
        "ik_pos":{
            'ctrl_ik_quadLeg_rump_0_L': [5.353, 73.17778605595966, -41.283461318628305], 
            'ctrl_ik_quadLeg_hip_0_L': [9.427100479531633, 73.17778605595966, -41.283461318628305],
            'ctrl_ik_quadLeg_knee_0_L': [12.659764496445849, 42.94222489523101, -9.697506258361376],
            'ctrl_ik_quadLeg_calf_0_L': [8.381440943844233, 20.335971998048286, -47.07023669736204],
            'ctrl_ik_quadLeg_ankle_0_L': [8.17389538574193, 5.737959787060513, -44.06889043484146]
            },
        "ik_rot":{
            'ctrl_ik_quadLeg_rump_0_L': [0.0, 0.0, 0.0], 
            'ctrl_ik_quadLeg_hip_0_L':[0.0, 0.0, 0.0],
            'ctrl_ik_quadLeg_knee_0_L': [134.9261066953834, -81.13417480632245, -45.715423170008286],
            'ctrl_ik_quadLeg_calf_0_L': [0.0, 11.136004369497108, 0.0],
            'ctrl_ik_quadLeg_ankle_0_L': [0.0, 11.136004369497108, 0.0]
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

# build root
root_data_manager = module_data_manager.ModuleDataManager(root_data)
root_build = build_root.BuildRoot(root_data_manager)
root_build.build()

# spine mdl
spine_data_manager = module_data_manager.ModuleDataManager(spine_data)
spine_build = build_spine.BuildSpine(spine_data_manager)
spine_build.build()

# quadLeg mdl
quadLeg_data_manager = module_data_manager.ModuleDataManager(quadLeg_data)
quadLeg_build = build_quadLeg.BuildQuadLeg(quadLeg_data_manager)
quadLeg_build.build()