
''' Without the Registry (single module build at a time)'''
'''
import importlib
from Jmvs_tool_box.systems.sys_char_rig.module_workflow import temp_mian_tyrannosaurusss_builder

importlib.reload(temp_mian_tyrannosaurusss_builder)
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
            "COG": [0.0, 360.0, 0.0]
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
            "ctrl_fk_root_COG_0_M": [0.0, 360.0, 0.0]
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
    'module_name': 'quadLeg', 
    'external_plg_dict': {
        'global_scale_grp': 'grp_Outputs_root_0_M', 
        'global_scale_atr': 'globalScale', 
        'base_plg_grp': 'grp_Outputs_root_0_M', 
        'base_plg_atr': 'mtx_root_ctrl_fk_centre', 
        'hook_plg_grp': 'grp_Outputs_root_0_M', 
        'hook_plg_atr': 'mtx_root_ctrl_fk_COG'
        }, 
    'output_hook_mtx_list': ['jnt_skn_ankle'], 
    'skeleton_dict': {
        'skel_pos': {
            'rump': [32.986259492592744, 399.71815364196743, -80.06218600181712], 
            'hip': [60.347192939725524, 399.71815364196794, -80.06611904469996], 
            'knee': [72.53250111287363, 230.19152642009465, 10.719691949462131], 
            'calf': [57.30248846343446, 109.95786388537925, -72.58729766070104], 
            'ankle': [60.37411697460796, 39.79577535000606, -47.19654951468622], 
            'ball': [64.43855478356869, 16.853438876020352, -13.599024167118056], 
            'end': [72.36121868152429, 0.006284018101766264, 51.89143568072978]
            }, 
        'skel_rot': {
            'rump': [0.0, 0.008236077048466302, 0.0], 
            'hip': [78.8224002228247, -28.425997294326205, -85.83370929440753], 
            'knee': [-283.15665926655504, 34.40641164066855, -97.74198564012104], 
            'calf': [79.4390375825061, -19.97689737919437, -88.33523363501281], 
            'ankle': [77.83377335803591, -55.259040978669496, -79.95378152067585], 
            'ball': [63.94602438148762, -74.13106225371192, -64.81393854025784], 
            'end': [63.94602438148762, -74.13106225371192, -64.81393854025784]
            }
        }, 
    'fk_dict': {
        'fk_pos': {
            'ctrl_fk_quadLeg_hip_0_L': [60.347192939725524, 399.71815364196794, -80.06611904469996], 
            'ctrl_fk_quadLeg_knee_0_L': [72.53250111287363, 230.19152642009465, 10.719691949462131], 
            'ctrl_fk_quadLeg_calf_0_L': [57.30248846343446, 109.95786388537925, -72.58729766070104], 
            'ctrl_fk_quadLeg_ankle_0_L': [60.37411697460796, 39.79577535000606, -47.19654951468622], 
            'ctrl_fk_quadLeg_ball_0_L': [64.43855478356869, 16.853438876020352, -13.599024167118056]
            }, 
        'fk_rot': {
            'ctrl_fk_quadLeg_hip_0_L': [78.8224002228247, -28.425997294326205, -85.83370929440753], 
            'ctrl_fk_quadLeg_knee_0_L': [-283.15665926655504, 34.40641164066855, -97.74198564012104], 
            'ctrl_fk_quadLeg_calf_0_L': [79.4390375825061, -19.97689737919437, -88.33523363501281], 
            'ctrl_fk_quadLeg_ankle_0_L': [77.83377335803591, -55.259040978669496, -79.95378152067585], 
            'ctrl_fk_quadLeg_ball_0_L': [63.94602438148762, -74.13106225371192, -64.81393854025784]
            }
        }, 
        'ik_dict': {
            'ik_pos': {
                'ctrl_ik_quadLeg_rump_0_L': [32.986259492592744, 399.71815364196743, -80.06218600181712], 
                'ctrl_ik_quadLeg_hip_0_L': [60.347192939725524, 399.71815364196794, -80.06611904469996], 
                'ctrl_ik_quadLeg_knee_0_L': [92.179, 233.115, 132.004],
                'ctrl_ik_quadLeg_calf_0_L': [57.30248846343446, 109.95786388537925, -72.58729766070104], 
                'ctrl_ik_quadLeg_ankle_0_L': [60.37411697460796, 39.79577535000606, -47.19654951468622]
                }, 
            'ik_rot': {
                'ctrl_ik_quadLeg_rump_0_L': [0.0, 0.0, 0.0], 
                'ctrl_ik_quadLeg_hip_0_L': [0.0, 0.0, 0.0], 
                'ctrl_ik_quadLeg_knee_0_L': [80.81405482844525, -80.69924690793599, 8.465179288412154], 
                'ctrl_ik_quadLeg_calf_0_L': [0.0, 6.897799061450713, 0.0], 
                'ctrl_ik_quadLeg_ankle_0_L': [0.0, 6.897799061450715, 0.0]
                }
            }, 
            'axis_dict': {'prim': 'X', 'scnd': 'Y', 'wld': 'Z'}
    }

# Isolated module-specific data flow
''' 
1 time data processing. 
'''

# build root
root_data_manager = module_data_manager.ModuleDataManager(root_data)
root_build = build_root.BuildRoot(root_data_manager)
root_build.build()

# # spine mdl
# spine_data_manager = module_data_manager.ModuleDataManager(spine_data)
# spine_build = build_spine.BuildSpine(spine_data_manager)
# spine_build.build()

# quadLeg mdl
quadLeg_data_manager = module_data_manager.ModuleDataManager(quadLeg_data)
quadLeg_build = build_quadLeg.BuildQuadLeg(quadLeg_data_manager)
quadLeg_build.build()


