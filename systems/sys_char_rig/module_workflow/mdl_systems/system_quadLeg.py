


import importlib
import maya.cmds as cmds

''' in 'main.py' set the directory of the four folders for this workflow '''
from systems.sys_char_rig.module_workflow.data_managers import module_data_manager

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
    def wire_hook_limbRoot_setup(self, inputs_grp, ik_ctrl_list, ik_pos_dict, ik_rot_dict):
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
        # ctrl_clav = ik_ctrl_list[0]
        ctrl_limbRoot = ik_ctrl_list[0]
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


    def cr_ik_aim_logic_joints(self, ik_pos_dict, ik_rot_dict, ik_ctrl_list, ik_jnt_list):
        ''' 
        # Description:
            Joint chain comprised of 2 joints. 
            'jnt_ik_quadLeg_aimBase_#_#' & 'jnt_ik_quadLeg_aimTip_#_#'
            Aim joints need to be orientd parallel to the hip.
        '''
        # cr the joints
        jnt_aim_base = f"jnt_ik_{self.dm.mdl_nm}_aimBase_{self.dm.unique_id}_{self.dm.side}"
        jnt_aim_tip = f"jnt_ik_{self.dm.mdl_nm}_aimTip_{self.dm.unique_id}_{self.dm.side}"
        for jnt_nm in [jnt_aim_base, jnt_aim_tip]:
            cmds.joint(n=jnt_nm)
            cmds.select(cl=1)

        # position jnts
        cmds.xform(jnt_aim_base, translation=ik_pos_dict[ik_ctrl_list[-1]], worldSpace=True)
        cmds.xform(jnt_aim_tip, translation=ik_pos_dict[ik_ctrl_list[0]], worldSpace=True)

        # Update the orientation of the two joints to be parallel with the hip.
            # cr temp locator and match to ankle jnt, and move on the Z axis a bit
        temp_loc = f"tmp_loc_{self.dm.mdl_nm}_aimBase_{self.dm.unique_id}_{self.dm.side}"
        cmds.spaceLocator(n=temp_loc)
        cmds.matchTransform(temp_loc, ik_jnt_list[3], pos=1, rot=1, scl=0)
        if self.dm.side == "L":
            cmds.move(0, 0, 10, temp_loc, r=1, os=1, wd=1)
        elif self.dm.side == "R":
            cmds.move(0, 0, -10, temp_loc, r=1, os=1, wd=1)

            # aim constrain the base. 
        cmds.aimConstraint(ik_jnt_list[0], 
                           jnt_aim_base, 
                           aimVector=(1, 0, 0), 
                           upVector=(0, 0, 1), 
                           worldUpType="object", 
                           worldUpObject=temp_loc,
                           n=f"temp_con_aimBase_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
                           )

        # delete constraint & locator
        cmds.delete(temp_loc, f"temp_con_aimBase_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}")

        # parent tip to base
        cmds.parent(jnt_aim_tip, jnt_aim_base)

        # orient tip joint to match its parent
        cmds.joint(jnt_aim_tip, e=1, oj="none", ch=1, zso=1 )

        # makeIdentity on the roations
        cmds.makeIdentity(jnt_aim_base, a=1, t=0, r=1, s=0, n=0, pn=1)
        cmds.select(cl=1)

        return [jnt_aim_base, jnt_aim_tip]

    # ik rp hdl on hip to calf. 
    def wire_logic_ik_handles(self, input_grp, ik_logic_jnt_list, ik_ctrl_list, ik_pos_dict, ik_rot_dict):
        '''
        # Description:
            Create Ik_handle on the logic joints(Ik RPSolver on logic joints w/ pole vector.), 
            wire the pin arm setup, wire the ikfkStretch setup from pin setup, 
            wire into ik handle from ikfkstretch. skn_wrist drives Ik_handle.opm.

            cr all other ik handles (SC & aim RP) -> grp individually 

            in 'wire_logic_foot_roll()' setup the foot roll hierarchy & ctrl_ik_ankle drives the ori_grp.opm
        # Attributes:
            inputs_grp (string): Group for input data for this module.
            ik_logic_jnt_list (list): list of arm logic joints. 
            ik_ctrl_list (list): Contains 4 ik control names.
        # Returns:
            bc_ikfk_stretch (utility): blendColors node returned so IKFK_Switch drives it.
            logic_hdl (string): logic Ik_handle name.
        '''
        # temp 
        cmds.hide("jnt_fk_quadLeg_hip_0_L")

        # cr Ik_handle on the logic joints
            # hip > calf
        logic_hdl = f"hdl_RP_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}" # hdl_bipedArm_0_L
        cmds.ikHandle( n=logic_hdl, sol="ikRPsolver", sj=ik_logic_jnt_list[0], ee=ik_logic_jnt_list[2], ccv=False, pcv=False)
            # group @ ik ankle pos
        grp_logic_hdl = f"grp_{logic_hdl}"
        utils.cr_empty_grp(grp_logic_hdl)
        cmds.xform(grp_logic_hdl, translation=list(ik_pos_dict.values())[-1], worldSpace=True)
        cmds.xform(grp_logic_hdl, rotation=list(ik_rot_dict.values())[-1], worldSpace=True)
        cmds.parent(logic_hdl, grp_logic_hdl)

            # calf > ankle
        calf_logic_hdl = f"hdl_SC_{self.dm.mdl_nm}_calf_{self.dm.unique_id}_{self.dm.side}" # hdl_bipedArm_0_L
        cmds.ikHandle( n=calf_logic_hdl, sol="ikSCsolver", sj=ik_logic_jnt_list[2], ee=ik_logic_jnt_list[3], ccv=False, pcv=False)
            # group @ ik calf pos
        grp_calf_logic_hdl = f"grp_{calf_logic_hdl}"
        utils.cr_empty_grp(grp_calf_logic_hdl)
        cmds.xform(grp_calf_logic_hdl, translation=list(ik_pos_dict.values())[2], worldSpace=True)
        cmds.xform(grp_calf_logic_hdl, rotation=list(ik_rot_dict.values())[2], worldSpace=True)
        cmds.parent(calf_logic_hdl, grp_calf_logic_hdl)

            # ankle > ball
            # martch translate to corresponding joint to
            # set orientation to ik ankle rot dict
        ball_logic_hdl = f"hdl_SC_{self.dm.mdl_nm}_ball_{self.dm.unique_id}_{self.dm.side}" # hdl_bipedArm_0_L
        cmds.ikHandle( n=ball_logic_hdl, sol="ikSCsolver", sj=ik_logic_jnt_list[3], ee=ik_logic_jnt_list[4], ccv=False, pcv=False)
            # group @ ik calf pos
        grp_ball_logic_hdl = f"grp_{ball_logic_hdl}"
        utils.cr_empty_grp(grp_ball_logic_hdl)
        cmds.matchTransform(grp_ball_logic_hdl, ik_logic_jnt_list[4], pos=1, rot=0, scl=0)
        cmds.xform(grp_ball_logic_hdl, rotation=list(ik_rot_dict.values())[-1], worldSpace=True)
        cmds.parent(ball_logic_hdl, grp_ball_logic_hdl)
            # ball > end
        end_logic_hdl = f"hdl_SC_{self.dm.mdl_nm}_toe_{self.dm.unique_id}_{self.dm.side}" # hdl_bipedArm_0_L
        cmds.ikHandle( n=end_logic_hdl, sol="ikSCsolver", sj=ik_logic_jnt_list[4], ee=ik_logic_jnt_list[5], ccv=False, pcv=False)
            # group @ ik calf pos
        grp_end_logic_hdl = f"grp_{end_logic_hdl}"
        utils.cr_empty_grp(grp_end_logic_hdl)
        cmds.matchTransform(grp_end_logic_hdl, ik_logic_jnt_list[4], pos=1, rot=0, scl=0)
        cmds.xform(grp_end_logic_hdl, rotation=list(ik_rot_dict.values())[-2], worldSpace=True)
        cmds.parent(end_logic_hdl, grp_end_logic_hdl)


    def wire_limbRt_ik_chain_root(self, ik_ctrl_list, ik_jnt_list, ik_pos_dict, ik_rot_dict):
        '''
        Have the limbRt control drive the root ik joint(see file 009)
        '''
        jnt_target = ik_jnt_list[0]
        print(f"jnt_target = {jnt_target}")

        mm_ik = f"MM_{self.dm.mdl_nm}_{jnt_target}"
        utils.cr_node_if_not_exists(1, 'multMatrix', mm_ik)

        utils.set_transformation_matrix([0.0, 0.0, 0.0], list(ik_rot_dict.values())[-1], f"{mm_ik}{utils.Plg.mtx_ins[0]}")         
        utils.connect_attr(f"{ik_ctrl_list[0]}{utils.Plg.wld_mtx_plg}", f"{mm_ik}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{mm_ik}{utils.Plg.mtx_sum_plg}", f"{jnt_target}{utils.Plg.opm_plg}")


    def wire_ik_logic_hierarchy(self, foot_piv_dict, ankle_trans_data):
        '''
        # Description:
            Setup the foot roll & group hierarchy for the ik handles. Foot pivot 
            data is used to create the groups. 
            
            foot_piv_dict = {
                "piv_out": [[],[]],
                "piv_in": [[],[]],
                "piv_toe": [[],[]],
                "piv_heel": [[],[]],
                }
            
            (ctrl_ik_ankle drives the ori_grp.opm (see file 008))
        # Arguments:
            foot_piv_dict (dict): {Keys= pivot name: values= [[pos], [rot]]}
            ankle_trans_data (nested list): [[pos], [rot]]
        # Return:
        '''
        #----------------------        
        # cr list from keys
        # piv_names = [n for n in foot_piv_dict.keys()]
        key_names = [n for n in foot_piv_dict.keys()]
        print(f"key_names = `{key_names}`")
        
        # itarate through keys to create groups.
        piv_names = []
        for name in key_names:
            pv_name = f"{name}_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
            utils.cr_node_if_not_exists(0, "transform", pv_name)
            piv_names.append(pv_name)
        print(f"piv_names = `{piv_names}`")

        # positon the groups using the dict!
        for key, piv in zip(key_names, piv_names):
            data = foot_piv_dict[key]
            # data[0] = pos, data[1] = rot.
            cmds.xform(piv, t=data[0], ro=data[1], ws=1)

        # cr origin grp
        grp_ori = f"grp_ik_{self.dm.mdl_nm}_ori_{self.dm.unique_id}_{self.dm.side}"
        utils.cr_node_if_not_exists(0, "transform", grp_ori)
        cmds.xform(grp_ori, t=ankle_trans_data[0], ro=ankle_trans_data[1], ws=1)

        # add the ori grp to the piv list.
        piv_names.insert(0, grp_ori)
        # parent the foot pivot grps in the right order to the ori group. 
        utils.parent_object_list(piv_names)
        # remove the ori grp from the piv list.
        piv_names.pop(0)

        #----------------------
        # ankle ball ik handle grp hierarchy 
        # (exists)
        grp_hdl_ball = f"grp_hdl_SC_{self.dm.mdl_nm}_ball_{self.dm.unique_id}_{self.dm.side}"
        # (new)
        grp_hdl_rollAim = f"grp_hdl_RP_{self.dm.mdl_nm}_rollAim_{self.dm.unique_id}_{self.dm.side}"
        utils.cr_node_if_not_exists(0, "transform", grp_hdl_rollAim)
        cmds.xform(grp_hdl_rollAim, t=ankle_trans_data[0], ro=ankle_trans_data[1], ws=1)
        # (exists)
        grp_hdl_rp_leg = f"grp_hdl_RP_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}" # grp_hdl_RP_quadLeg_0_L
        # (exists)
        grp_hdl_calf = f"grp_hdl_SC_{self.dm.mdl_nm}_calf_{self.dm.unique_id}_{self.dm.side}" # grp_hdl_SC_quadLeg_calf_0_L
        
        grp_hdl_list = [grp_hdl_ball, grp_hdl_rollAim, grp_hdl_rp_leg, grp_hdl_calf]
        utils.parent_object_list(grp_hdl_list)

        #----------------------
        # ankle toe ik handle grp hierarchy
        # (new)
        grp_hdl_toeBend = f"grp_hdl_SC_{self.dm.mdl_nm}_toeBend_{self.dm.unique_id}_{self.dm.side}" #grp_hdl_SC_quadLeg_toe_0_L
        utils.cr_node_if_not_exists(0, "transform", grp_hdl_toeBend)
        # (exists)
        grp_hdl_toe = f"grp_hdl_SC_{self.dm.mdl_nm}_toe_{self.dm.unique_id}_{self.dm.side}" #grp_hdl_SC_quadLeg_toe_0_L
        
        cmds.matchTransform(grp_hdl_toeBend, grp_hdl_toe, pos=1, rot=1, scl=0)

        grp_hdl_toe_list = [grp_hdl_toeBend, grp_hdl_toe]
        utils.parent_object_list(grp_hdl_toe_list)

        #----------------------
        # parent the two ik handle hiraerchy's to the end of the pivot's.
        cmds.parent(grp_hdl_list[0], grp_hdl_toe_list[0], piv_names[-1])

        cmds.select(cl=1)


    def pv_ik_hdl_leg_setup(self, ik_pv_ctrl): # ik_pv_ctrl, ik_handle
        ''' add the polevector constraint to the leg RP ik handle. '''
        # knee ctrl | leg ik handle
        cmds.poleVectorConstraint(
            ik_pv_ctrl, 
            f"hdl_RP_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        )


    def position_ik_ctrl_calf(self, ik_calf_ctrl, ik_pos_list, ik_rot_list):
        '''
        position the calf control. (same as the ankle control)
        '''
        cmds.xform(ik_calf_ctrl, t=ik_pos_list[-1], ro=ik_rot_list[-1], ws=1)

    
    def wire_calf_aim_setup(self, jnt_aim_ls, ik_ctrl_list, ik_jnt_list):
        # offset grp the ik calf ctrl. (ctrl must be zero)
        calf_ctrl = ik_ctrl_list[2]
        ofs_grp_calf = f"ofs_grp_{calf_ctrl}"
        utils.cr_node_if_not_exists(0, "transform", ofs_grp_calf)
        cmds.matchTransform(ofs_grp_calf, calf_ctrl, pos=1, rot=1, scl=0)
        cmds.parent(ofs_grp_calf, f"grp_ctrl_ik_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}")
        cmds.parent(calf_ctrl, ofs_grp_calf)
        cmds.select(cl=1)

        # calf drives ik handle (grp_hdl_RP_quadLeg_0_L) orientation w/ direct connection.
        grp_hdl_rp_leg = f"grp_hdl_RP_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        utils.connect_attr(f"{calf_ctrl}.rotate", f"{grp_hdl_rp_leg}.rotate")

        # cr ik handle on aim joints. (RP) + (group it)
        hdl_aim = f"hdl_SC_{self.dm.mdl_nm}_aim_{self.dm.unique_id}_{self.dm.side}" # hdl_bipedArm_0_L
        cmds.ikHandle( n=hdl_aim, sol="ikRPsolver", sj=jnt_aim_ls[0], ee=jnt_aim_ls[-1], ccv=False, pcv=False)
        grp_logic_hdl = f"grp_{hdl_aim}"
        utils.cr_empty_grp(grp_logic_hdl)
        cmds.matchTransform(grp_logic_hdl, hdl_aim, pos=1, rot=1, scl=0)
        cmds.parent(hdl_aim, grp_logic_hdl)
        cmds.select(cl=1)

        # point constrain (ik ankle ctrl > jnt_ik_quadLeg_aimBase_0_L)
        ankle_ctrl = ik_ctrl_list[-1]
        cmds.pointConstraint(ankle_ctrl, jnt_aim_ls[0], mo=1)

        # point constrain (ik hip ctrl > hdl_RP_quadLeg_aim_0_L)
        hip_ctrl = ik_ctrl_list[0]
        cmds.pointConstraint(hip_ctrl, hdl_aim, mo=1)

        # polevector contrain (ctrl_ik_quadLeg_knee_0_L > hdl_RP_quadLeg_aim_0_L)
        ik_pv_ctrl = ik_ctrl_list[1]
        cmds.poleVectorConstraint(ik_pv_ctrl, hdl_aim)

        #----------------------------------------------------------------------
        # # parent constrain (jnt_ik_quadLeg_aimBase_0_L > ofs_grp_ctrl_ik_calf)
        # cmds.parentConstraint(jnt_aim_ls[0], ofs_grp_calf, mo=1)

        # orient constrain (jnt_ik_quadLeg_aimBase_0_L > grp_hdl_aimRoll)
        # cmds.orientConstraint(
        #     jnt_aim_ls[0], 
        #     f"grp_hdl_RP_{self.dm.mdl_nm}_rollAim_{self.dm.unique_id}_{self.dm.side}", 
        #     mo=1
        # )

        # add attrib to ctrl_ik_calf & wire to rev node
        orient_switch_attr = "aim_active"
        utils.add_locked_attrib(calf_ctrl, ["Attributes"])
        utils.add_float_attrib(calf_ctrl, [f"{orient_switch_attr}"], [0.0, 1.0], True)
        rev_rollAim = f"REV_rollAim_{calf_ctrl}"
        utils.cr_node_if_not_exists(1, 'reverse', rev_rollAim)
        utils.connect_attr(
                f"{calf_ctrl}.{orient_switch_attr}",
                f"{rev_rollAim}{utils.Plg.inp_axis[0]}")

        grp_rollAim = f"grp_hdl_RP_{self.dm.mdl_nm}_rollAim_{self.dm.unique_id}_{self.dm.side}"
        # jnt_aim > ctrl_ik_ankle > grp_rollAim (parent no translate)
        pcon_rollAim_name = f"Pcon_jntAim_ctrlIkAnkle_grp_hdl_{self.dm.mdl_nm}_rollAim_{self.dm.unique_id}_{self.dm.side}"
        cmds.parentConstraint(jnt_aim_ls[0], ankle_ctrl, grp_rollAim, n=pcon_rollAim_name, st=["x","z","y"], mo=1)
        print(f" - Pcon: {jnt_aim_ls[0]} + {ankle_ctrl} > {grp_rollAim}")
        
        parts_ls = [jnt.split('_')[-3] for jnt in ik_jnt_list]

        # blend between these
        utils.connect_attr(
            f"{calf_ctrl}.{orient_switch_attr}", # jnt_ik_quadLeg_aimBase_0_LW0
            f"Pcon_jntAim_ctrlIkAnkle_grp_hdl_{self.dm.mdl_nm}_rollAim_{self.dm.unique_id}_{self.dm.side}.jnt_ik_{self.dm.mdl_nm}_aimBase_{self.dm.unique_id}_{self.dm.side}W0")
        utils.connect_attr(
            f"{rev_rollAim}{utils.Plg.out_axis[0]}", # ctrl_ik_quadLeg_ankle_0_LW1
            f"Pcon_jntAim_ctrlIkAnkle_grp_hdl_{self.dm.mdl_nm}_rollAim_{self.dm.unique_id}_{self.dm.side}.ctrl_ik_{self.dm.mdl_nm}_{parts_ls[-3]}_{self.dm.unique_id}_{self.dm.side}W1")
            

        # jnt_ik_calf > ofs_grp_ctrl_ik_calf (parent all)
        calf_ik_jnt = ik_jnt_list[2]
        cmds.parentConstraint(calf_ik_jnt, ofs_grp_calf, n=f"Pcon_{calf_ik_jnt}", mo=1)


        # parent constrain (ankle_ctrl > grp_ori)
        cmds.parentConstraint(
            ankle_ctrl, 
            f"grp_ik_{self.dm.mdl_nm}_ori_{self.dm.unique_id}_{self.dm.side}", 
            mo=1, n=f"Pcon_{ankle_ctrl}"
        )
        

    def wire_mdl_setting_ctrl(self, skn_jnt_wrist):
        '''
        # Description:
            Settings Control alr exists in scene so wire its positon & ADD all it's attributes!
        # Arguments: 
            skn_jnt_wrist (string): Name of the wrist skin joint.
            ik_ctrl_list (list): Contains 4 ik control names.
        # Returns:
            mdl_settings_ctrl (string): Name of the settings control.
            ikfk_plug (plug): 'ikfk_switch' control attribute plug for consitancy.
            stretch_volume_plug (plug): 'stretch_volume' control attribute plug for consitancy.
            shaper_plug (plug): 'shaper_visibility' control attribute plug for consitancy.
        '''
        ''' TEMPORARY -> ADD settings control to this module's database data! '''
        # duplicate the ik_shoudler ctrl when it is made, before it's posisioned
        mdl_settings_ctrl = f"ctrl_{self.dm.mdl_nm}_settings_{self.dm.unique_id}_{self.dm.side}"
        # Colour the settings ctrl a pale version of the current colour. 
        # if self.dm.side == "L":
        #     utils.colour_object(mdl_settings_ctrl, 4)
        # elif self.dm.side == "R":
        #     utils.colour_object(mdl_settings_ctrl, 18)
        # cmds.parent(mdl_settings_ctrl, f"grp_ctrls_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}")
        
        ikfk_switch_attr = "IK_FK_Switch"
        # stretch_state_attr = "Stretch_State"
        # stretch_vol_attr = "Stretch_Volume"
        # shaper_attr = "Vis_Shapers"
        utils.add_locked_attrib(mdl_settings_ctrl, ["Attributes"])
        utils.add_float_attrib(mdl_settings_ctrl, [f"{ikfk_switch_attr}"], [0.0, 1.0], True)
        # utils.add_float_attrib(root_ctrl, [f"Auto_Stretch"], [0.0, 1.0], True)

        # utils.add_locked_attrib(mdl_settings_ctrl, ["Visibility"])
        # utils.add_float_attrib(mdl_settings_ctrl, [f"{shaper_attr}"], [0.0, 1.0], True)

        # wire 'skn_jnt_wrist' to  'mdl_settings_ctrl.OPM'
        mm_settings = f"MM_{mdl_settings_ctrl}"
        utils.cr_node_if_not_exists(1, 'multMatrix', mm_settings)
        utils.connect_attr(f"{skn_jnt_wrist}{utils.Plg.wld_mtx_plg}", f"{mm_settings}{utils.Plg.mtx_ins[1]}")
        utils.connect_attr(f"{mm_settings}{utils.Plg.mtx_sum_plg}", f"{mdl_settings_ctrl}{utils.Plg.opm_plg}")
        
        ikfk_plug = f"{mdl_settings_ctrl}.{ikfk_switch_attr}"
        # stretch_state_plug = f"{mdl_settings_ctrl}.{stretch_state_attr}"
        # stretch_volume_plug = f"{mdl_settings_ctrl}.{stretch_vol_attr}"
        # shaper_plug = f"{mdl_settings_ctrl}.{shaper_attr}"

        return mdl_settings_ctrl, ikfk_plug #, stretch_state_plug, stretch_volume_plug, shaper_plug


    def blend_ik_fk_states_to_skin_chain(self, ik_chain, fk_chain, skn_chain, 
                                         mdl_settings_ctrl, ikfk_plug):
        '''
        # Description:            
            This function blends the ik & fk joint chains to drive 
            the skin joint chain with constraints.
        # Arguments:
            ik_chain (list): ik jnt stretch chain.
            fk_chain (list): fk jnt stretch chain.
            skn_chain (list): skin jnt chain.
        # Returns: N/A
        '''
        # Pcon skn_chain by ik_chain & fk_chain
        for x in range(len(skn_chain)):
            pcon_ikfk_name = f"Pcon_ikfk_jnts_{skn_chain[x]}"
            print(f"{ik_chain[x]}, {fk_chain[x]}, {skn_chain[x]}, n={pcon_ikfk_name}")
            cmds.parentConstraint(ik_chain[x], fk_chain[x], skn_chain[x], n=pcon_ikfk_name)
            # cmds.setAttr(f"{pcon_ikfk_name}.interpType", 2)

        # cr rev node
        rev_ikfk = f"REV_{mdl_settings_ctrl}"
        utils.cr_node_if_not_exists(1, 'reverse', rev_ikfk)
        utils.connect_attr(
                ikfk_plug,
                f"{rev_ikfk}{utils.Plg.inp_axis[0]}")

        # get the key name of the joints
        parts_ls = [jnt.split('_')[-3] for jnt in skn_chain]
        print(f"parts_ls = {parts_ls}")

        # wire the weights on the constraint
        for x in range(len(skn_chain)):
            utils.connect_attr(
                ikfk_plug, # jnt_ik_quadLeg_hip_0_LW0
                f"Pcon_ikfk_jnts_{skn_chain[x]}.jnt_ik_{self.dm.mdl_nm}_{parts_ls[x]}_{self.dm.unique_id}_{self.dm.side}W0")
            utils.connect_attr(
                f"{rev_ikfk}{utils.Plg.out_axis[0]}", # jnt_ik_quadLeg_hip_0_LW0
                f"Pcon_ikfk_jnts_{skn_chain[x]}.jnt_fk_{self.dm.mdl_nm}_{parts_ls[x]}_{self.dm.unique_id}_{self.dm.side}W1")
            

    def cr_foot_atr(self, ik_ctrl_list):
        '''
        # Description:            
            Add the foot attributes to the ankle control.
        # Arguments:
            ik_ctrl_list (list): ik control list.
        # Returns: foot_piv_atr_list (list). Pivot attribute names. 
        '''
        ankle_ctrl = ik_ctrl_list[-1]

        atr_ball_roll = "Ball_Roll"
        atr_toe_roll = "Toe_Roll"
        atr_heel_roll = "Heel_Roll"
        atr_ankle_roll = "Ankle_Roll"
        atr_heel_twist = "Heel_Twist"
        atr_toe_twist = "Toe_Twist"
        atr_toe_bend = "Toe_Bend"
        atr_foot_rock = "Foot_Rock"

        foot_piv_atr_list = [atr_ball_roll, atr_toe_roll, atr_heel_roll,
             atr_ankle_roll, atr_heel_twist, atr_toe_twist,
             atr_toe_bend, atr_foot_rock
            ]
        print(f"- foot_piv_atr_list = {foot_piv_atr_list}")
        utils.add_locked_attrib(ankle_ctrl, ["Foot"])
        utils.add_float_attrib(
            ankle_ctrl, 
            [f"{atr_ball_roll}", f"{atr_toe_roll}", f"{atr_heel_roll}",
             f"{atr_ankle_roll}", f"{atr_heel_twist}", f"{atr_toe_twist}",
             f"{atr_toe_bend}", f"{atr_foot_rock}"
            ], 
            [0.0, 1.0], False)
        
        return foot_piv_atr_list
      

    def wire_foot_atr(self, foot_piv_atr_list, ik_ctrl_list):
        '''
        # Description:            
            Wire the attributes as the drivers.
        # Arguments:
            ik_ctrl_list (list): ik control list.
            foot_piv_atr_list (list). Pivot attribute names.
        # Returns: N/A
        '''
        ankle_ctrl = ik_ctrl_list[-1]

        for atr in foot_piv_atr_list:
            print(f"atr = {atr}")
            if "Ball_Roll" in atr:
                # Ball_Roll > grp_hdl_SC_quadLeg_ball_0_L.rx
                utils.connect_attr(
                    f"{ankle_ctrl}.{atr}",
                    f"grp_hdl_SC_{self.dm.mdl_nm}_ball_{self.dm.unique_id}_{self.dm.side}.rx"
                )
            elif "Toe_Roll" in atr:
                # Toe_Roll > piv_toe_quadLeg_0_L.rx
                utils.connect_attr(
                    f"{ankle_ctrl}.{atr}",
                    f"piv_toe_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}.rx"
                )
            elif "Heel_Roll" in atr:
                # Heel_Roll > piv_heel_quadLeg_0_L.rx
                utils.connect_attr(
                    f"{ankle_ctrl}.{atr}",
                    f"piv_heel_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}.rx"
                )
            elif "Ankle_Roll" in atr:
                # Ankle_Roll > grp_hdl_SC_quadLeg_calf_0_L.rx 
                # Ankle_Roll > grp_hdl_SC_quadLeg_toe_0_L.rx
                utils.connect_attr(
                    f"{ankle_ctrl}.{atr}",
                    f"grp_hdl_SC_{self.dm.mdl_nm}_calf_{self.dm.unique_id}_{self.dm.side}.rx"
                )
                utils.connect_attr(
                    f"{ankle_ctrl}.{atr}",
                    f"grp_hdl_SC_{self.dm.mdl_nm}_toe_{self.dm.unique_id}_{self.dm.side}.rx"
                )
            elif "Heel_Twist" in atr:
                # Heel_Twist > piv_heel_quadLeg_0_L.ry
                utils.connect_attr(
                    f"{ankle_ctrl}.{atr}",
                    f" piv_heel_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}.ry"
                )
            elif "Toe_Twist" in atr:
                # Toe_Twist > piv_toe_quadLeg_0_L.ry
                utils.connect_attr(
                    f"{ankle_ctrl}.{atr}",
                    f" piv_toe_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}.ry"
                )
            elif "Toe_Bend" in atr:
                # Toe_Bend > grp_hdl_SC_quadLeg_toeBend_0_L.ry
                utils.connect_attr(
                    f"{ankle_ctrl}.{atr}",
                    f" grp_hdl_SC_{self.dm.mdl_nm}_toeBend_{self.dm.unique_id}_{self.dm.side}.rx"
                )
            elif "Foot_Rock" in atr:
                pass
                # Foot_Rock > piv_in_quadLeg_0_L.rz
                # Foot_Rock > piv_out_quadLeg_0_L.rz
                utils.connect_attr(
                    f"{ankle_ctrl}.{atr}",
                    f"piv_in_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}.rz"
                )
                utils.connect_attr(
                    f"{ankle_ctrl}.{atr}",
                    f"piv_out_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}.rz"
                )
                # set limit on the grps
                cmds.transformLimits(
                    f"piv_out_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}", 
                    rz=(0, 0), erz=(0, 1))
                cmds.transformLimits(
                    f"piv_in_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}", 
                    rz=(0, 0), erz=(1, 0))
            else:
                break


    def wire_ik_logic_elements(self, input_grp, ik_logic_jnt_list, ik_ctrl_list):
        '''
        arm pinn
        '''
        pass
        # # add opm from ik wrist ctrl to the mm_pv_ik_hdl
        # mm_pv_ik_hdl = f"MM_hdlPv_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # pm_pv_ik_hdl = f"PM_hdlPv_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # utils.cr_node_if_not_exists(1, 'multMatrix', mm_pv_ik_hdl)
        # utils.cr_node_if_not_exists(1, 'pickMatrix', pm_pv_ik_hdl, {"useRotate":0, "useScale":0, "useShear":0})

        # utils.connect_attr(f"{ik_ctrl_list[-1]}{utils.Plg.wld_mtx_plg}", f"{mm_pv_ik_hdl}{utils.Plg.mtx_ins[1]}")
        # utils.connect_attr(f"{mm_pv_ik_hdl}{utils.Plg.mtx_sum_plg}", f"{pm_pv_ik_hdl}{utils.Plg.inp_mtx_plg}")
        # utils.connect_attr(f"{pm_pv_ik_hdl}{utils.Plg.out_mtx_plg}", f"{logic_hdl}{utils.Plg.opm_plg}")
        #     # zero out the hdl attr
        # for axis in ["X", "Y", "Z"]:
        #     cmds.setAttr(f"{logic_hdl}.translate{axis}", 0, lock=1)
        #     cmds.setAttr(f"{logic_hdl}.rotate{axis}", 0, lock=1)

        # # Pin arm >drives> ik logic joints stretch. 
        # # ik logic joints stretch >drives> Ik_handle.poleVector plug
        # utils.add_locked_attrib(ik_ctrl_list[2], ["Attributes"])
        # utils.add_float_attrib(ik_ctrl_list[2], ["Pin_Arm"], [0.0, 1.0], True)

        # db_shld_wrist = f"DB_ik_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # db_shld_elb = f"DB_ikUpper_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # db_elb_wrist = f"DB_ikLower_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # fm_global = f"FM_byGlobal_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # fm_max = f"FM_max_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # fm_upPercent_div = f"FM_upPercentageDiv_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # fm_upPercentTotal_mult = f"FM_upPercentageTotalMult_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # fm_lowPercent_div = f"FM_lowPercentageDiv_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # fm_lowPercentTotal_mult = f"FM_lowPercentageTotalMult_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # bc_pin_limb = f"BC_pin_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # for db_name in [db_shld_wrist, db_shld_elb, db_elb_wrist]:
        #     utils.cr_node_if_not_exists(1, "distanceBetween", db_name)
        # utils.cr_node_if_not_exists(1, "floatMath", fm_max, {"operation":5})
        # for fm_div_name in [fm_upPercent_div, fm_lowPercent_div]:
        #     utils.cr_node_if_not_exists(1, "floatMath", fm_div_name, {"operation":3})
        # for fm_mult_name in [fm_global, fm_upPercentTotal_mult, fm_lowPercentTotal_mult]:
        #     utils.cr_node_if_not_exists(1, "floatMath", fm_mult_name, {"operation":2})
        # utils.cr_node_if_not_exists(1, "blendColors", bc_pin_limb)

        #     # db_shld_wrist > max
        # utils.connect_attr(f"{ik_ctrl_list[1]}{utils.Plg.wld_mtx_plg}", f"{db_shld_wrist}{utils.Plg.inMatrixs[1]}")
        # utils.connect_attr(f"{ik_ctrl_list[-1]}{utils.Plg.wld_mtx_plg}", f"{db_shld_wrist}{utils.Plg.inMatrixs[2]}")
        # utils.connect_attr(f"{db_shld_wrist}{utils.Plg.distance_plg}", f"{fm_max}{utils.Plg.flt_A}")
        
        #     # db_shld_elb > bc.color1R
        # utils.connect_attr(f"{ik_ctrl_list[1]}{utils.Plg.wld_mtx_plg}", f"{db_shld_elb}{utils.Plg.inMatrixs[1]}")
        # utils.connect_attr(f"{ik_ctrl_list[2]}{utils.Plg.wld_mtx_plg}", f"{db_shld_elb}{utils.Plg.inMatrixs[2]}")
        # utils.connect_attr(f"{db_shld_elb}{utils.Plg.distance_plg}", f"{bc_pin_limb}{utils.Plg.color1_plg[0]}")
        #     # db_elb_wrist > bc.color1G
        # utils.connect_attr(f"{ik_ctrl_list[2]}{utils.Plg.wld_mtx_plg}", f"{db_elb_wrist}{utils.Plg.inMatrixs[1]}")
        # utils.connect_attr(f"{ik_ctrl_list[-1]}{utils.Plg.wld_mtx_plg}", f"{db_elb_wrist}{utils.Plg.inMatrixs[2]}")
        # utils.connect_attr(f"{db_elb_wrist}{utils.Plg.distance_plg}", f"{bc_pin_limb}{utils.Plg.color1_plg[1]}")

        #     # > fm_global > fm_max.flt_B
        # cmds.setAttr(f"{fm_global}{utils.Plg.flt_A}", self.dm.d_shld_wrist)
        # utils.connect_attr(f"{input_grp}.{self.dm.global_scale_attr}", f"{fm_global}{utils.Plg.flt_B}")
        # utils.connect_attr(f"{fm_global}{utils.Plg.out_flt}", f"{fm_max}{utils.Plg.flt_B}")

        #     # fm_upPercent_div > fm_upPercentTotal_mult.flt_A
        # cmds.setAttr(f"{fm_upPercent_div}{utils.Plg.flt_A}", self.dm.d_shld_elb)
        # cmds.setAttr(f"{fm_upPercent_div}{utils.Plg.flt_B}", self.dm.d_shld_wrist)
        # utils.connect_attr(f"{fm_upPercent_div}{utils.Plg.out_flt}", f"{fm_upPercentTotal_mult}{utils.Plg.flt_A}")
        #     # fm_lowPercent_div > fm_lowPercentTotal_mult.flt_A
        # cmds.setAttr(f"{fm_lowPercent_div}{utils.Plg.flt_A}", self.dm.d_elb_wrist)
        # cmds.setAttr(f"{fm_lowPercent_div}{utils.Plg.flt_B}", self.dm.d_shld_wrist)
        # utils.connect_attr(f"{fm_lowPercent_div}{utils.Plg.out_flt}", f"{fm_lowPercentTotal_mult}{utils.Plg.flt_A}")
        
        #     # fm_upPercentTotal_mult > bc.color2R
        # utils.connect_attr(f"{fm_max}{utils.Plg.out_flt}", f"{fm_upPercentTotal_mult}{utils.Plg.flt_B}")
        # utils.connect_attr(f"{fm_upPercentTotal_mult}{utils.Plg.out_flt}", f"{bc_pin_limb}{utils.Plg.color2_plg[0]}")
        #     # fm_lowPercentTotal_mult > bc.color2G
        # utils.connect_attr(f"{fm_max}{utils.Plg.out_flt}", f"{fm_lowPercentTotal_mult}{utils.Plg.flt_B}")
        # utils.connect_attr(f"{fm_lowPercentTotal_mult}{utils.Plg.out_flt}", f"{bc_pin_limb}{utils.Plg.color2_plg[1]}")
        
        #     # pv.Pin_Arm > bc.blender
        # utils.connect_attr(f"{ik_ctrl_list[2]}.Pin_Arm", f"{bc_pin_limb}{utils.Plg.blndr_plg}")

        # # Initalise ik stretch logic
        # fm_up_fkStretch = f"FM_upFkStretchMult_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # fm_low_fkStretch = f"FM_lowFkStretchMult_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # fm_up_fkStretchGlobal = f"FM_upFkStretchGlobalMult_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # fm_low_fkStretchGlobal = f"FM_lowFkStretchGlobalMult_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # bc_ikfk_stretch = f"BC_ikfkStretch_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # for fm_mult_nm in [fm_up_fkStretchGlobal, fm_low_fkStretchGlobal]:
        #     utils.cr_node_if_not_exists(1, "floatMath", fm_mult_nm, {"operation":2})
        # utils.cr_node_if_not_exists(1, "blendColors", bc_ikfk_stretch, {"blender":1})
        
        #     # fm_up/low_fkStretch.out_flt > fm_up/low_global.flt_A
        # utils.connect_attr(f"{fm_up_fkStretch}{utils.Plg.out_flt}", f"{fm_up_fkStretchGlobal}{utils.Plg.flt_A}")
        # utils.connect_attr(f"{fm_low_fkStretch}{utils.Plg.out_flt}", f"{fm_low_fkStretchGlobal}{utils.Plg.flt_A}")
        
        #     # input_grp.globalScale > fm_up/low_global.flt_B
        # utils.connect_attr(f"{input_grp}.{self.dm.global_scale_attr}", f"{fm_up_fkStretchGlobal}{utils.Plg.flt_B}")
        # utils.connect_attr(f"{input_grp}.{self.dm.global_scale_attr}", f"{fm_low_fkStretchGlobal}{utils.Plg.flt_B}")
        
        #     # bc_pin_arm > bc_ikfk_stretch.color2
        # utils.connect_attr(f"{bc_pin_limb}{utils.Plg.out_letter[0]}", f"{bc_ikfk_stretch}{utils.Plg.color1_plg[0]}")
        # utils.connect_attr(f"{bc_pin_limb}{utils.Plg.out_letter[1]}", f"{bc_ikfk_stretch}{utils.Plg.color1_plg[1]}")
        
        #     # fm_up/low_global > bc_ikfk_stretch.color1#
        # utils.connect_attr(f"{fm_up_fkStretchGlobal}{utils.Plg.out_flt}", f"{bc_ikfk_stretch}{utils.Plg.color2_plg[0]}")
        # utils.connect_attr(f"{fm_low_fkStretchGlobal}{utils.Plg.out_flt}", f"{bc_ikfk_stretch}{utils.Plg.color2_plg[1]}")
        
        # # Plug into the logic joints!
        # md_ikfk_stretch = f"MD_ikfkStretch_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # utils.cr_node_if_not_exists(1, "multiplyDivide", md_ikfk_stretch, {"operation":2})
        #     # bc_ikfk_stretch.outColor# > md_ikfk_stretch.input1#
        # utils.connect_attr(f"{bc_ikfk_stretch}{utils.Plg.out_letter[0]}", f"{md_ikfk_stretch}{utils.Plg.input1_val[0]}")
        # utils.connect_attr(f"{bc_ikfk_stretch}{utils.Plg.out_letter[1]}", f"{md_ikfk_stretch}{utils.Plg.input1_val[1]}")
        #     # input_grp.globalScale > md_ikfk_stretch.input2#
        # utils.connect_attr(f"{input_grp}.{self.dm.global_scale_attr}", f"{md_ikfk_stretch}{utils.Plg.input2_val[0]}")
        # utils.connect_attr(f"{input_grp}.{self.dm.global_scale_attr}", f"{md_ikfk_stretch}{utils.Plg.input2_val[1]}")
        #     # md_ikfk_stretch.out# > logic_jnt.translate prim axis
        # utils.connect_attr(f"{md_ikfk_stretch}{utils.Plg.out_axis[0]}", f"{ik_logic_jnt_list[1]}.translate{self.dm.prim_axis}")
        # utils.connect_attr(f"{md_ikfk_stretch}{utils.Plg.out_axis[1]}", f"{ik_logic_jnt_list[2]}.translate{self.dm.prim_axis}")

        # # wire to the ikHandle.poleVector plug
        # pMM_shld = f"PMM_shld_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # cM_shld = f"CM_shld_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # iM_shld = f"IM_shld_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # mm_pv = f"MM_poleVector_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # dm_pv = f"DM_poleVector_{self.dm.mdl_nm}_{self.dm.unique_id}_{self.dm.side}"
        # utils.cr_node_if_not_exists(1, "pointMatrixMult", pMM_shld)
        # utils.cr_node_if_not_exists(0, "composeMatrix", cM_shld)
        # utils.cr_node_if_not_exists(1, "inverseMatrix", iM_shld)
        # utils.cr_node_if_not_exists(1, "multMatrix", mm_pv)
        # utils.cr_node_if_not_exists(0, "decomposeMatrix", dm_pv)
        #     # > pMM_shld
        # utils.connect_attr(f"{ik_logic_jnt_list[0]}{utils.Plg.prt_plg}", f"{pMM_shld}.inMatrix")
        # utils.connect_attr(f"{ik_logic_jnt_list[0]}.translate", f"{pMM_shld}.inPoint")
        #     # > compM_shld
        # utils.connect_attr(f"{pMM_shld}{utils.Plg.output_plg}", f"{cM_shld}{utils.Plg.inputT_plug}")
        #     # > iM_shld
        # utils.connect_attr(f"{cM_shld}{utils.Plg.out_mtx_plg}", f"{iM_shld}{utils.Plg.inp_mtx_plg}")
        #     # > mm_pv
        # utils.connect_attr(f"{ik_ctrl_list[2]}{utils.Plg.wld_mtx_plg}", f"{mm_pv}{utils.Plg.mtx_ins[0]}")
        # utils.connect_attr(f"{iM_shld}{utils.Plg.out_mtx_plg}", f"{mm_pv}{utils.Plg.mtx_ins[1]}")
        #     # > mm_pv
        # utils.connect_attr(f"{mm_pv}{utils.Plg.mtx_sum_plg}", f"{dm_pv}{utils.Plg.inp_mtx_plg}")
        #     # > hdl.poleVector
        # utils.connect_attr(f"{dm_pv}{utils.Plg.outT_plug}", f"{logic_hdl}.poleVector")
        
        # return bc_ikfk_stretch, logic_hdl


    '''
    setup the shaper controls & twist joints same as biped arm. 
    '''


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
        