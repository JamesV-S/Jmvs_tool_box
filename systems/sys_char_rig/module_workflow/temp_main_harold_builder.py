
''' Without the Registry (single module build at a time)'''
'''
import importlib
from Jmvs_tool_box.systems.sys_char_rig.module_workflow import temp_main_harold_builder

importlib.reload(temp_main_harold_builder)
'''

# import the right classes
import importlib

# from data_managers import (module_data_manager)
from systems.sys_char_rig.module_workflow.data_managers import (module_data_manager)
from systems.sys_char_rig.module_workflow.builders import (
    build_root,
    build_spine,
    build_bipedArm,
    build_bipedLeg
    )

importlib.reload(module_data_manager)
importlib.reload(build_root)
importlib.reload(build_spine)
importlib.reload(build_bipedArm)
importlib.reload(build_bipedLeg)

# raw module-specific data
root_data = {'module_name': 'root', 'external_plg_dict': {'global_scale_grp': 'grp_Outputs_root_0_M', 'global_scale_atr': 'globalScale', 'base_plg_grp': None, 'base_plg_atr': None, 'hook_plg_grp': None, 'hook_plg_atr': None}, 'output_hook_mtx_list': ['ctrl_fk_centre', 'ctrl_fk_COG'], 'skeleton_dict': {'skel_pos': {'rt': [0.0, 0.0, 0.0], 'centre': [0.0, 0.0, 0.0], 'COG': [0.0, 93.30952750371226, 0.0]}, 'skel_rot': {'rt': [0.0, 0.0, 0.0], 'centre': [0.0, 0.0, 90.0], 'COG': [0.0, 0.0, 90.0]}}, 'fk_dict': {'fk_pos': {'ctrl_fk_root_rt_0_M': [0.0, 0.0, 0.0], 'ctrl_fk_root_centre_0_M': [0.0, 0.0, 0.0], 'ctrl_fk_root_COG_0_M': [0.0, 93.30952750371226, 0.0]}, 'fk_rot': {'ctrl_fk_root_rt_0_M': [0.0, 0.0, 0.0], 'ctrl_fk_root_centre_0_M': [0.0, 0.0, 90.0], 'ctrl_fk_root_COG_0_M': [0.0, 0.0, 90.0]}}, 'ik_dict': {'ik_pos': {}, 'ik_rot': {}}, 'axis_dict': {'prim': 'X', 'scnd': 'Y', 'wld': 'Z'}}

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
            'spine0': [0.0, 94.06878351483358, 1.5987211554602254], 
            'spine1': [0.0, 99.0687835148336, 1.5987211554602254], 
            'spine2': [0.0, 104.06878351483361, 1.5987211554602254], 
            'spine3': [0.0, 109.06878351483363, 1.5987211554602254], 
            'spine4': [0.0, 114.06878351483364, 1.5987211554602254], 
            'spine5': [0.0, 119.06878351483365, 1.5987211554602254], 
            'spine6': [0.0, 124.06878351483367, 1.5987211554602254]
            },
        "skel_rot":{
            'spine0' : [0.0, 0.0, 0.0], 
            'spine1' : [0.0, 0.0, 0.0], 
            'spine2' : [0.0, 0.0, 0.0], 
            'spine3' : [0.0, 0.0, 0.0], 
            'spine4' : [0.0, 0.0, 0.0], 
            'spine5' : [0.0, 0.0, 0.0], 
            'spine6' : [0.0, 0.0, 0.0]
            }
        },
    "fk_dict":{
        "fk_pos":{
            'ctrl_fk_spine_spine0_0_M': [0.0, 94.06878351483358, 1.5987211554602254], 
            'ctrl_fk_spine_spine1_0_M':  [0.0, 104.06878351483361, 1.5987211554602254], 
            'ctrl_fk_spine_spine2_0_M': [0.0, 114.06878351483364, 1.5987211554602254]
            },
        "fk_rot":{
            'ctrl_fk_spine_spine0_0_M': [0.0, 0.0, 0.0], 
            'ctrl_fk_spine_spine1_0_M': [0.0, 0.0, 0.0], 
            'ctrl_fk_spine_spine2_0_M': [0.0, 0.0, 0.0]
            }
        },
    "ik_dict":{
        "ik_pos":{
            'ctrl_ik_spine_spine_bottom_0_M':[0.0, 94.06878351483358, 1.5987211554602254], 
            'ctrl_ik_spine_spine_middle_0_M': [0.0, 109.06878351483363, 1.5987211554602254], 
            'ctrl_ik_spine_spine_top_0_M': [0.0, 124.06878351483367, 1.5987211554602254]
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

bipedArm_data = {'module_name': 'bipedArm', 'external_plg_dict': {
        'global_scale_grp': 'grp_Outputs_root_0_M', 
        'global_scale_atr': 'globalScale', 
        'base_plg_grp': 'grp_Outputs_root_0_M', 
        'base_plg_atr': 'mtx_root_ctrl_fk_centre', 
        'hook_plg_grp': 'grp_Outputs_spine_0_M', 
        'hook_plg_atr': 'mtx_spine_jnt_skn_top'}, 'output_hook_mtx_list': ['jnt_skn_wrist', 'jnt_skn_lower5'], 'skeleton_dict': {'skel_pos': {'clavicle': [1.545724952390838, 133.9715022556759, -1.3120755253334369], 'shoulder': [19.795685636425475, 130.41890975101134, -4.34643495910321], 'elbow': [33.00848388671875, 107.99212646484375, -7.820152282714844], 'wrist': [48.08352279663086, 85.04073333740234, -4.697444915771484]}, 'skel_rot': {'clavicle': [-0.6353993213185715, 9.269135383588923, -11.015607699509347], 'shoulder': [-4.24506345621818, 7.601364282360991, -59.49542289242958], 'elbow': [-4.262776952670774, -6.4878352223958276, -56.70210750190426], 'wrist': [-4.262776952670774, -6.4878352223958276, -56.70210750190426]}}, 'fk_dict': {'fk_pos': {'ctrl_fk_bipedArm_shoulder_0_L': [19.795685636425475, 130.41890975101134, -4.34643495910321], 'ctrl_fk_bipedArm_elbow_0_L': [33.00848388671875, 107.99212646484375, -7.820152282714844], 'ctrl_fk_bipedArm_wrist_0_L': [48.08352279663086, 85.04073333740234, -4.697444915771484]}, 'fk_rot': {'ctrl_fk_bipedArm_shoulder_0_L': [-4.24506345621818, 7.601364282360991, -59.49542289242958], 'ctrl_fk_bipedArm_elbow_0_L': [-4.262776952670774, -6.4878352223958276, -56.70210750190426], 'ctrl_fk_bipedArm_wrist_0_L': [-4.262776952670774, -6.4878352223958276, -56.70210750190426]}}, 'ik_dict': {'ik_pos': {'ctrl_ik_bipedArm_clavicle_0_L': [1.545724952390838, 133.9715022556759, -1.3120755253334369], 'ctrl_ik_bipedArm_shoulder_0_L': [19.795685636425475, 130.41890975101134, -4.34643495910321], 'ctrl_ik_bipedArm_elbow_0_L': [32.444225703456205, 107.66592632900718, -11.122916841207983], 'ctrl_ik_bipedArm_wrist_0_L': [48.08352279663086, 85.04073333740234, -4.697444915771484]},                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
        'ik_rot': {
            'ctrl_ik_bipedArm_clavicle_0_L': [0.0, 0.0, 0.0], 
            'ctrl_ik_bipedArm_shoulder_0_L': [0.0, 0.0, 0.0], 'ctrl_ik_bipedArm_elbow_0_L': [88.05708186101224, 101.16322156761208, 30.032395601042847], 'ctrl_ik_bipedArm_wrist_0_L': [-4.262776952670774, -6.4878352223958276, -56.70210750190426]}}, 'axis_dict': {'prim': 'X', 'scnd': 'Y', 'wld': 'Z'}}


bipedLeg_data = {
    'module_name': 'bipedLeg', 
    'external_plg_dict': {
        'global_scale_grp': 'grp_Outputs_root_0_M', 
        'global_scale_atr': 'globalScale', 
        'base_plg_grp': 'grp_Outputs_root_0_M', 
        'base_plg_atr': 'mtx_root_ctrl_fk_centre', 
        'hook_plg_grp': 'grp_Outputs_spine_0_M', 
        'hook_plg_atr': 'mtx_spine_jnt_skn_bottom'}, 'output_hook_mtx_list': ['jnt_skn_ankle'], 'skeleton_dict': {'skel_pos': {'hip': [10.656302250480918, 86.7630104099756, 0.0514862909913063], 'knee': [9.479150295257568, 38.91950988769531, 1.1611289978027344], 'ankle': [8.413028717041016, 9.177447319030762, -2.4644412994384766], 'ball': [11.325602435425008, -1.2434497875801749, 13.352066159053704], 'toe': [12.349699242463426, -1.1379786002407858, 18.70219353136403]}, 'skel_rot': {'hip': [87.09521693036125, -1.3282310436592994, -91.40943353315498], 'knee': [-273.2313872214912, 6.945673004306646, -92.0529216620297], 'ankle': [69.61778489601946, -58.66841954055061, -72.39253586718058], 'ball': [0.0, -79.1637820305985, 0.0], 'toe': [0.0, -79.1637820305985, 0.0]}}, 'fk_dict': {'fk_pos': {'ctrl_fk_bipedLeg_hip_0_L': [10.656302250480918, 86.7630104099756, 0.0514862909913063], 'ctrl_fk_bipedLeg_knee_0_L': [9.479150295257568, 38.91950988769531, 1.1611289978027344], 'ctrl_fk_bipedLeg_ankle_0_L': [8.413028717041016, 9.177447319030762, -2.4644412994384766], 'ctrl_fk_bipedLeg_ball_0_L': [11.325602435425008, -1.2434497875801749, 13.352066159053704]}, 'fk_rot': {'ctrl_fk_bipedLeg_hip_0_L': [87.09521693036125, -1.3282310436592994, -91.40943353315498], 'ctrl_fk_bipedLeg_knee_0_L': [-273.2313872214912, 6.945673004306646, -92.0529216620297], 'ctrl_fk_bipedLeg_ankle_0_L': [69.61778489601946, -58.66841954055061, -72.39253586718058], 'ctrl_fk_bipedLeg_ball_0_L': [0.0, -79.1637820305985, 0.0]}}, 'ik_dict': {
            'ik_pos': {'ctrl_ik_bipedLeg_hip_0_L': [10.656302250480918, 86.7630104099756, 0.0514862909913063], 'ctrl_ik_bipedLeg_knee_0_L': [9.682661127081245, 38.82743074803014, 3.8192443038003603], 'ctrl_ik_bipedLeg_ankle_0_L': [8.413028717041016, 9.177447319030762, -2.4644412994384766]}, 
            'ik_rot': {'ctrl_ik_bipedLeg_hip_0_L': [0.0, 0.0, 0.0], 'ctrl_ik_bipedLeg_knee_0_L': [112.76019911753282, -85.19648512314475, -24.3445290398897], 'ctrl_ik_bipedLeg_ankle_0_L': [0.0, 0.0, 0.0]}}, 'axis_dict': {'prim': 'X', 'scnd': 'Y', 'wld': 'Z'}}

# Isolated module-specific data flow
''' 
# 1 time data processing. 
# # '''
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

# bipedArm mdl
bipedArm_data_manager = module_data_manager.ModuleDataManager(bipedArm_data)
bipedArm_build = build_bipedArm.BuildBipedArm(bipedArm_data_manager)
bipedArm_build.build()

# bipedLeg mdl
bipedLeg_data_manager = module_data_manager.ModuleDataManager(bipedLeg_data)
bipedLeg_build = build_bipedLeg.BuildBipedLeg(bipedLeg_data_manager)
bipedLeg_build.build()




