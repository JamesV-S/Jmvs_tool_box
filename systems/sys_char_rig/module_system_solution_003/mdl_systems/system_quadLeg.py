


import importlib
import maya.cmds as cmds

''' in 'main.py' set the directory of the four folders for this workflow '''
from systems.sys_char_rig.module_system_solution_003.data_managers import module_data_manager

from utils import (
    utils
)
from systems.sys_char_rig import (
    cr_ctrl
)

importlib.reload(module_data_manager)
importlib.reload(utils)
importlib.reload(cr_ctrl)

class SystemQuadLeg:
    def __init__(self, data_manager):
        '''
        Use type hint checking `variable:type = data` to be able to let VsCode 
        know about autocomplete for `ModuleDataManager` class so i can access 
        the correct variable names with `self.dm.#`

        Pass the data_manager instance to 'self.#' so it can be shared throughout 
        the class functions
        '''
        
        self.dm:module_data_manager.ModuleDataManager = data_manager 
        print("<- - ->")
        print(f"SystemQuadLeg -> dataa_manager = {data_manager}")
    

    # Phase 2 - Module-specific class functions in 'System[ModuleName]'
    def wire_hook_limbRoot_setup(self, inputs_grp, ctrl_list, ik_pos_dict, ik_rot_dict):
        '''
        # Description:
            The 'input_grp.hook_matrix' drives the 'limb root control' which will 
            then be the root of the rest of the module: Both FK & IK follow it.  
        # Attributes:
            input_grp (string): Group for input data for this module.
            ctrl_list (list): Contains limbRt control names.
            ik_pos_dict (dict): key=Name of ik controls, value=Positional data.
            ik_rot_dict (dict): key=Name of ik controls, value=Rotational data.
        # Returns: N/A
        '''
        # ctrl_clav = ctrl_list[0]
        ctrl_limbRoot = ctrl_list[0]
        # Lock the limbRt rotate attr
        for axis in (['x', 'y', 'z']):
                cmds.setAttr(f"{ctrl_limbRoot}.r{axis}", lock=1, keyable=0, cb=1)

        # ctrl_clavicle setup
        # module_hook_mtx into ctrl_limb_root (ctrl_ik_quadLeg_hip_#_#)     
        mm_ctrl_limbRt = f"MM_{ctrl_limbRoot}"
        utils.cr_node_if_not_exists(1, 'multMatrix', mm_ctrl_limbRt)
            # set matrix offset value to MM[0]
        limbRt_pos = list(ik_pos_dict.values())[0]
        limbRt_rot = list(ik_rot_dict.values())[0]
        utils.set_transformation_matrix(limbRt_pos, limbRt_rot, f"{mm_ctrl_limbRt}{utils.Plg.mtx_ins[0]}")
            # plug incoming plug (the one to follow) to MM[1]
        utils.connect_attr(f"{inputs_grp}.hook_mtx", f"{mm_ctrl_limbRt}{utils.Plg.mtx_ins[1]}")
            # plug MM sum to obj to follow!
        utils.connect_attr(f"{mm_ctrl_limbRt}{utils.Plg.mtx_sum_plg}", f"{ctrl_limbRoot}{utils.Plg.opm_plg}")


    def logic_jnt_distances(self, skel_num, skel_pos_dict):
        '''
        # Description:
            Need to store the distances of the the limb, (to be used for PINNING! & More).
            Stored in a dictionary with each item being the distance going through the list of skel positions.
            Last item in dict is 'start to end' distance
        # Attributes:
            skel_num (int): number of joints in the module's skeleton.
            skel_pos_dict (dict): key=Name skel pos component, value=Positional data.
        # Returns:
            d_skel_dict (dict): key=Name '*component_*component', value= Int length.
        '''
        # print(f"skel_num = {skel_num}")
        d_skel_dict = {}
        for x in range(skel_num):
            # get distances through the skel pos dict and add to the dictionary. 
            try:
                # print(f"{list(skel_pos_dict.keys())[x]}, {list(skel_pos_dict.keys())[x+1]}")
                d = utils.get_distance(f"skel_jnt_sequence_{x}", list(skel_pos_dict.values())[x], list(skel_pos_dict.values())[x+1])
                d_skel_dict[f"{list(skel_pos_dict.keys())[x]}_{list(skel_pos_dict.keys())[x+1]}"] = d
            except IndexError:
                pass
        # Add start end distance to dictionary -> hip_ankle
        d_start_end = utils.get_distance("start_end", list(skel_pos_dict.values())[0], list(skel_pos_dict.values())[3])
        d_skel_dict[f"{list(skel_pos_dict.keys())[0]}_{list(skel_pos_dict.keys())[3]}"] = d_start_end
        print(d_skel_dict)

        '''{
        'hip_knee': 29.73453085918653, 
        'knee_calf': 29.79762073881076, 
        'calf_ankle': 14.904801745021047, 
        'ankle_ball': 5.432754706587857, 
        'ball_end': 6.2893240637222405, 
        'hip_ankle': 67.50895722456278
        }'''

        return d_skel_dict


    def wire_fk_logic_joints(self, fk_ctrl_list, fk_jnt_chain, bm_limbRt):
        '''
        # Description:
            bm_limbRt output drives fk_ctrl_list[0] translate
            Drive fk_jnt_chain.rotations with fk_ctrl_list.rotations.
        # Attributes:
            fk_ctrl_list (list): fk control names.
            fk_jnt_chain (list): fk joint names.
            bm_limbRt (utility) BlendMatrix node drives the positional transform for fk joints
        # Returns:
        '''
        #  bm_limbRt.outMatrix > fk_jnt_chain[0].opm
        utils.connect_attr(f"{bm_limbRt}{utils.Plg.out_mtx_plg}", f"{fk_jnt_chain[0]}{utils.Plg.opm_plg}")

        # direct connection of ctrl to joint
        for x, i in ((x, i) for x in range(len(fk_ctrl_list)) for i in range(len(self.dm.XYZ))):
            utils.connect_attr(f"{fk_ctrl_list[x]}.rotate{self.dm.XYZ[i]}", f"{fk_jnt_chain[x]}.rotate{self.dm.XYZ[i]}")



    # Do this after all other functions are complete.
    def wire_fk_ctrl_stretch_setup(self, fk_ctrl_list, fk_pos_dict):
        '''
        # Description:
            - stretches the fk ctrl's by translating the control in front. So to 
            "stretch" fk_0, the fk_1 is translated away.
            - This also acts as the default translation position of the fk ctrls. 
        # Attributes:
            fk_ctrl_list (list): Contains 3 fk control names.
            fk_pos_dict (dict): key=Name of fk controls, value=Positional data.
        # Returns: N/A
        '''
        for ctrl in fk_ctrl_list[:-1]:
            utils.add_locked_attrib(ctrl, ["Attributes"])
            utils.add_float_attrib(ctrl, ["Stretch"], [0.01, 999.0], True)
            cmds.setAttr(f"{ctrl}.Stretch", 1)
            
        # fk_shld_stretch_distance = self.d_shld_elb
        # fk_elbow_stretch_distance = self.d_elb_wrist
        # print(f"--------")
        # print(f"fk_shld_elb_stretch_distance = `{fk_shld_stretch_distance}`")
        # print(f"--------")
        # print(f"fk_elb_wrist_stretch_distance = `{fk_elbow_stretch_distance}`")
        # print(f"--------")

        # # shoulder stretch
        # fm_shld_stretch_mult = f"FM_upFkStretchMult_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # fm_shld_stretch_sub = f"FM_upFkStretchSub_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # utils.cr_node_if_not_exists(1, "floatMath", fm_shld_stretch_mult, {"operation":2, "floatA":fk_shld_stretch_distance})
        # utils.cr_node_if_not_exists(1, "floatMath", fm_shld_stretch_sub, {"operation":1, "floatB":fk_shld_stretch_distance})
        
        # utils.connect_attr(f"{fk_ctrl_list[0]}.Stretch", f"{fm_shld_stretch_mult}{utils.Plg.flt_B}")
        # utils.connect_attr(f"{fm_shld_stretch_mult}{utils.Plg.out_flt}", f"{fm_shld_stretch_sub}{utils.Plg.flt_A}")
        # utils.connect_attr(f"{fm_shld_stretch_sub}{utils.Plg.out_flt}", f"{fk_ctrl_list[1]}.translate{self.dm.prim_axis}")
        
        # # elbow stretch
        # fm_elb_stretch_mult = f"FM_lowFkStretchMult_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # fm_elb_stretch_sub = f"FM_lowFkStretchSub_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # utils.cr_node_if_not_exists(1, "floatMath", fm_elb_stretch_mult, {"operation":2, "floatA":fk_elbow_stretch_distance})
        # utils.cr_node_if_not_exists(1, "floatMath", fm_elb_stretch_sub, {"operation":1, "floatB":fk_elbow_stretch_distance})
        
        # utils.connect_attr(f"{fk_ctrl_list[1]}.Stretch", f"{fm_elb_stretch_mult}{utils.Plg.flt_B}")
        # utils.connect_attr(f"{fm_elb_stretch_mult}{utils.Plg.out_flt}", f"{fm_elb_stretch_sub}{utils.Plg.flt_A}")
        # utils.connect_attr(f"{fm_elb_stretch_sub}{utils.Plg.out_flt}", f"{fk_ctrl_list[2]}.translate{self.dm.prim_axis}")
        