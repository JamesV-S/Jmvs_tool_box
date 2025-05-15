# ------------------------------ Controller -----------------------------------
import maya.cmds as cmds
from maya import OpenMayaUI

try:
    from PySide6 import QtCore, QtWidgets, QtGui
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtGui import QIcon, QStandardItemModel, QStandardItem
    from PySide6.QtWidgets import (QWidget)
    from shiboken6 import wrapInstance
except ModuleNotFoundError:
    from PySide2 import QtCore, QtWidgets, QtGui
    from PySide2.QtCore import Qt, Signal
    from PySide2.QtGui import QIcon
    from PySide2.QtWidgets import (QWidget)
    from shiboken2 import wrapInstance

import importlib
import os.path

from utils import (
    utils,
    utils_json
)

from systems.sys_char_rig import (
    cr_guides, 
    cr_ctrl
)

from controllers import utils_QTree

from models.char_models import char_layout_model
from views.char_views import char_layout_view

# importlib.reload(utils_os)
importlib.reload(utils)
importlib.reload(utils_json)
importlib.reload(utils_QTree)
importlib.reload(cr_guides)
importlib.reload(cr_ctrl)
importlib.reload(char_layout_model)
importlib.reload(char_layout_view)

class CharLayoutController:
    def __init__(self): # class
        self.model = char_layout_model.CharLayoutModel()
        self.view = char_layout_view.CharLayoutView()
        
        self.json_dict = utils_json.get_modules_json_dict('char_config')
        self.user_module_data = {}

        self.db_rig_location = "db_rig_storage"
        name_of_rig_fld = self.model.get_available_DB_rig_folders(self.db_rig_location)
        self.populate_available_rig_comboBox(name_of_rig_fld)
        self.val_availableRigComboBox = self.view.available_rig_comboBox.currentText()
        
        self.set_prerequisite_signals()
        # Connect signals and slots
        self.setup_connections()
        
        print(f"self.view.mdl_tree_model == {self.view.mdl_tree_model}")
        self.model.visualise_active_db(self.val_availableRigComboBox, self.view.mdl_tree_model)
        
        # tree_name = self.val_availableRigComboBox.replace("DB_", "")
        # self.view.tree_view_name_lbl.setText(f"Database: `{tree_name}`")


    def set_prerequisite_signals(self):
        self.view.all_crv_edit_checkBox.setChecked(True)
        self.view.controls_crv_edit_checkBox.setChecked(True)
        self.view.guide_crv_edit_checkBox.setChecked(False)
        
        self.sig_all_crv_edit_checkBox()
        self.sig_ik_crv_edit_checkBox()
        self.sig_fk_crv_edit_checkBox()
        self.sig_ctrl_crv_edit_checkBox()
        self.sig_guide_crv_edit_checkBox()
        self.sig_entire_comp_radioBtn()
        self.sig_sel_comp_radioBtn()
        
        # ----
        self.view.controls_template_checkBox.setChecked(True)
        self.view.ddj_template_checkBox.setChecked(True)
        # ----
        self.view.entire_comp_radioBtn.setChecked(True)
        self.val_entire_comp_radioBtn = True
        # ----
        self.view.update_comp_data_checkBox.setChecked(False)
        self.view.joint_editing_checkBox.setChecked(False)
        self.view.ctrl_editing_checkBox.setChecked(False)
    
        self.sig_update_comp_data_checkBox()
        self.sig_joint_editing_checkBox()
        self.sig_ctrl_editing_checkBox()

        self.sig_umo_rigType_comboBox()
        self.sig_umo_mirror_checkBox()
        self.sig_umo_stretch_checkBox()
        self.sig_umo_twist_checkBox()

    def setup_connections(self):
        # selection_model = self.view.mdl_tree_view.selectionModel()
        # selection_model.selectionChanged.connect(self.set_selected_module_label)

        # -- visualise database --
        self.view.available_rig_comboBox.currentIndexChanged.connect(self.sig_availableRigComboBox)
        self.view.rpl_live_component.clicked.connect(self.sig_rpl_live_component)
        # ------------ choose modules ------------
        for mdl in self.view.mdl_choose_ui_dict:
            # unpack the elements of the dict containing the widgets dynamically built.  
            mdl_checkBox, mdl_iteration, mdl_side = self.view.mdl_choose_ui_dict[mdl]
            # create lambda functions to connect signals to slots with additional `mdl` argument
            mdl_checkBox.stateChanged.connect(lambda _, name=mdl: self.sig_mdl_checkBox(name))
            mdl_iteration.valueChanged.connect(lambda _, name=mdl: self.sig_mdl_IterationSpinBox(name))
            mdl_side.currentIndexChanged.connect(lambda _, name=mdl: self.sig_mdl_SideCombobox(name))
        
        self.view.publish_btn.clicked.connect(self.sig_publish_btn)
        
        # -- add blueprints --
        self.view.add_mdl_btn.clicked.connect(self.sig_add_module)
        self.view.add_blueprint_btn.clicked.connect(self.sig_add_blueprint)

        # ------------ Management options ------------
            # ---- Tab1 - Curves ----
                # ---- Curve Editing ----
        self.view.all_crv_edit_checkBox.stateChanged.connect(self.sig_all_crv_edit_checkBox)
        self.view.ik_crv_edit_checkBox.stateChanged.connect(self.sig_ik_crv_edit_checkBox)
        self.view.fk_crv_edit_checkBox.stateChanged.connect(self.sig_fk_crv_edit_checkBox)
        
        self.view.controls_crv_edit_checkBox.stateChanged.connect(self.sig_ctrl_crv_edit_checkBox)
        self.view.guide_crv_edit_checkBox.stateChanged.connect(self.sig_guide_crv_edit_checkBox)
        self.view.select_data_in_comp_btn.clicked.connect(self.sig_sl_data_in_comp_btn)
                # ---- Template Display ----
        self.view.guide_template_checkBox.stateChanged.connect(self.sig_guide_template_checkBox)
        self.view.controls_template_checkBox.stateChanged.connect(self.sig_controls_template_checkBox)
        self.view.ddj_template_checkBox.stateChanged.connect(self.sig_ddj_template_checkBox)
                # ---- Lock/Unlock ----
        self.view.compnent_checkBox.stateChanged.connect(self.sig_compnent_checkBox)
        self.view.lock_btn.clicked.connect(self.sig_lock_btn)
        self.view.unlock_btn.clicked.connect(self.sig_unlock_btn)

        # self.view.mirror_comp_btn.clicked.connect()
        self.view.store_curve_comp_btn.clicked.connect(self.sig_store_curve_comp_btn)
        
            # ---- Tab2 - Edit module ----
        self.view.entire_comp_radioBtn.clicked.connect(self.sig_entire_comp_radioBtn)
        self.view.sel_comp_radioBtn.clicked.connect(self.sig_sel_comp_radioBtn)
        self.view.update_comp_data_checkBox.stateChanged.connect(self.sig_update_comp_data_checkBox)
        self.view.umo_rigType_comboBox.currentIndexChanged.connect(self.sig_umo_rigType_comboBox)
        self.view.umo_mirror_checkBox.stateChanged.connect(self.sig_umo_mirror_checkBox)
        self.view.umo_stretch_checkBox.stateChanged.connect(self.sig_umo_stretch_checkBox)
        self.view.umo_twist_checkBox.stateChanged.connect(self.sig_umo_twist_checkBox)
        self.view.joint_editing_checkBox.stateChanged.connect(self.sig_joint_editing_checkBox)
        self.view.ctrl_editing_checkBox.stateChanged.connect(self.sig_ctrl_editing_checkBox)
        self.view.jnt_num_spinBox.valueChanged.connect(self.sig_jnt_num_spinBox)
        self.view.commit_module_edits_btn.clicked.connect(self.sig_commit_module_edits_btn)


    def update_progress(self, value, operation_name=""):
        # Update the progress bar with the given value and operation name
        self.view.progress_bar.setValue(value)
        if 'DONE:' in operation_name:
            self.view.progress_bar.setFormat(f"{operation_name}")
        else:    
            self.view.progress_bar.setFormat(f"{operation_name} : {value}%")


    # ------------ module visulisation siFunc ------------
    def sig_availableRigComboBox(self):
        print("run available rig drop down")
        self.val_availableRigComboBox = self.view.available_rig_comboBox.currentText()
        # tree_name = self.val_availableRigComboBox.replace("DB_", "")
        # self.view.tree_view_name_lbl.setText(f"Database: `{tree_name}`")
        self.model.visualise_active_db(self.val_availableRigComboBox, self.view.mdl_tree_model)
        print(f"available rig chosen: `{self.val_availableRigComboBox}`")


    def sig_rpl_live_component(self):
        # print selection in ui:
        component_selection = utils_QTree.get_component_name_TreeSel(self.view.mdl_tree_view , self.view.mdl_tree_model)
        # for component in component_selection:
        total_index = len(component_selection)
        for stp, component in enumerate(component_selection):
            self.model.record_component_change(component, self.val_availableRigComboBox)
            
            progress_value = utils.progress_value(stp, total_index)
            self.update_progress(progress_value, f"Replacing {component} positional data")
        
        self.update_progress(0, f"DONE: Replaced {component_selection} pos data")

    # ------------ module additions siFunc ------------
    def sig_mdl_checkBox(self, mdl_name):
        # define the 3 widget functions appropriatly, taking the `mdl_name` arg from lambda!
        mdl_checkBox = self.view.mdl_choose_ui_dict[mdl_name][0]
        self.val_mdl_checkBox = mdl_checkBox.isChecked()

        # Change how the component 'side' is chosen!
            # Read the config `user_settings` `side` attribute!
        print(f"j :self.json_dict: `{self.json_dict}`")
        config_dict = self.json_dict[f'{mdl_name}.json']
        config_user_settings = config_dict["user_settings"]
        config_side = config_user_settings["side"][0]
 
        self.user_module_data[mdl_name] = {
            "mdl_checkBox": self.val_mdl_checkBox,
            "mdl_iteration": self.user_module_data.get(mdl_name, {}).get('iteration', 1),
            "mdl_side": self.user_module_data.get(mdl_name, {}).get('side', config_side)
        }

        if self.val_mdl_checkBox: # Enable other widgets where neccesary
            self.view.mdl_choose_ui_dict[mdl_name][1].setEnabled(True)
            # if mdl_name == "spine" or mdl_name == "root":
            #     pass
            if config_side == "M":
                pass
            else:
                self.view.mdl_choose_ui_dict[mdl_name][2].setEnabled(True)
        else:
            self.view.mdl_choose_ui_dict[mdl_name][1].setEnabled(False)             
            self.view.mdl_choose_ui_dict[mdl_name][2].setEnabled(False)
        print(f"MDL::{mdl_name} &  self.val_mdl_checkBox::{self.val_mdl_checkBox}")
    

    def sig_mdl_IterationSpinBox(self, mdl_name):
        mdl_iteration = self.view.mdl_choose_ui_dict[mdl_name][1]
        if mdl_name == "root":
            mdl_iteration.setMinimum(1)
            mdl_iteration.setMaximum(1)
        self.val_mdl_iteration = mdl_iteration.value()
        
        # add the remaining iteration widget signal
        self.user_module_data[mdl_name]["mdl_iteration"] = self.val_mdl_iteration

        print(f"MDL::{mdl_name} &  self.val_mdl_checkBox::{self.val_mdl_iteration}")


    def sig_mdl_SideCombobox(self, mdl_name):
        mdl_side = self.view.mdl_choose_ui_dict[mdl_name][2]
        self.val_mdl_side = mdl_side.currentText()
        self.val_mdl_name = mdl_name

        # add the remaining iteration widget signal
        #if self.val_mdl_side == "None":
        #    self.user_module_data[mdl_name]["mdl_side"] = ""
        #else:
        self.user_module_data[mdl_name]["mdl_side"] = self.val_mdl_side

        print(f"MDL::{self.val_mdl_name} &  self.val_mdl_checkBox::{self.val_mdl_side}")
    
    # -- Publish --
    def sig_publish_btn(self): # cr a new dictionary to store the state of each module!
        total_stp = len(self.user_module_data)
        for stp, (mdl, signals) in enumerate(self.user_module_data.items()):
            #print(f"MDL::{mdl} & signals::{signals}")
            print(f"MDL::{mdl} & checkbox::{signals['mdl_checkBox']}, iteration::{signals['mdl_iteration']}, side::{signals['mdl_side']}")
            self.model.cr_mdl_json_database(self.val_availableRigComboBox, mdl, signals['mdl_checkBox'], signals['mdl_iteration'], signals['mdl_side'])
            self.model.visualise_active_db(self.val_availableRigComboBox, self.view.mdl_tree_model)
            
            # progress_value = utils.progress_value()
    
    # ---- add blueprint ----
    def func_createXfmGuides(self, component_selection):
            total_stp = len(component_selection) 
            for stp, selection in enumerate(component_selection):
                parts = selection.split('_')
                # if "root" in selection:
                #     obj_name = f"*_{parts[1]}"
                # else:
                obj_name = f"*_{parts[1]}_*_{parts[2]}_{parts[3]}"
                if cmds.objExists(obj_name):
                    exists = 1
                else:
                    exists = 0
                    mdl_component_dict = self.model.retrieve_component_dict_from_nameSel(self.val_availableRigComboBox, selection)
                    print(f"RETURNED DICT = {mdl_component_dict}")
                    cr_guides.CreateXfmGuides(mdl_component_dict, self.val_availableRigComboBox)

                progress_value = utils.progress_value(stp, total_stp)
                self.update_progress(progress_value, f"create module {selection}")
            
            if not exists:
                # parent the blueprints to hierarchy rig group properly
                try:
                    cmds.parent("grp_component_misc", "grp_components")
                    cmds.parent("grp_xfm_components", "grp_components")
                    cmds.parent("grp_ctrl_components", "grp_controls")
                except Exception as e:
                    print(f"parenting error: `grp_component_misc`, `grp_xfm_components` to `grp_components` = {e}")
            else:
                print(f"component already exists in the scene: {selection}")
            self.view.controls_template_checkBox.setChecked(False)
            self.view.ddj_template_checkBox.setChecked(False)
            self.view.controls_template_checkBox.setChecked(True)
            self.view.ddj_template_checkBox.setChecked(True)


    def sig_add_module(self):
        self.model.load_rig_group(self.val_availableRigComboBox)
        # this dict comes from gathering data from active databases in active rig folder!
        component_selection = utils_QTree.get_component_name_TreeSel(self.view.mdl_tree_view, self.view.mdl_tree_model)
        # print(f"YAAAAAH component_selection = {component_selection[0]}")
        self.func_createXfmGuides(component_selection)
        self.model.func_unlocked_all()
        self.update_progress(0, f"DONE: Added {component_selection} to scene")

        
    def sig_add_blueprint(self):
        self.model.load_rig_group(self.val_availableRigComboBox)
        # connect signals for module editor buttons
        for mdl, (checkBox, iterations, side) in self.view.mdl_choose_ui_dict.items():
            if checkBox.isChecked(): # checkbox is the master 
                # access the input from iterations and side
                iterations_value = iterations.value()
                side_value = side.currentText() if side else None
                print(f"Adding blueprint for {mdl}: Iterations={iterations_value}, Side={side_value}")
        
        component_selection = utils_QTree.get_all_component_name_in_TreeView(self.view.mdl_tree_model)
        self.func_createXfmGuides(component_selection)
        self.model.func_unlocked_all()
        self.update_progress(0, f"DONE: '{self.val_availableRigComboBox}' Blueprint")

    # ------------ management options siFunc ------------
    # ---- Tab 1 - curves ----
    def sig_all_crv_edit_checkBox(self):
        self.val_all_crv_edit_checkBox = self.view.all_crv_edit_checkBox.isChecked()
        if self.val_all_crv_edit_checkBox:
            self.view.ik_crv_edit_checkBox.setEnabled(False)
            self.view.fk_crv_edit_checkBox.setEnabled(False)
        else:
            self.view.ik_crv_edit_checkBox.setEnabled(True)
            self.view.fk_crv_edit_checkBox.setEnabled(True)
    def sig_ik_crv_edit_checkBox(self):
        self.val_ik_crv_edit_checkBox = self.view.ik_crv_edit_checkBox.isChecked()
        if self.val_ik_crv_edit_checkBox:
            self.val_ik_crv_edit_checkBox = "ik"
    def sig_fk_crv_edit_checkBox(self):
        self.val_fk_crv_edit_checkBox = self.view.fk_crv_edit_checkBox.isChecked()
        if self.val_fk_crv_edit_checkBox:
            self.val_fk_crv_edit_checkBox = "fk"
        

    def sig_sl_data_in_comp_btn(self):
        print(f"> Select data in chosen components!")
        comp_sel = utils_QTree.get_component_name_TreeSel(self.view.mdl_tree_view , self.view.mdl_tree_model)
        try:
            for comp in comp_sel:
                self.model.select_component_data(comp, self.val_availableRigComboBox, self.val_all_crv_edit_checkBox, self.val_ik_crv_edit_checkBox, self.val_fk_crv_edit_checkBox)
        except TypeError as e:
            cmds.error(f"Select a component first!: |{e}|")


    def sig_ctrl_crv_edit_checkBox(self):
        self.val_ctrl_crv_edit_checkbox = self.view.controls_crv_edit_checkBox.isChecked()


    def sig_guide_crv_edit_checkBox(self):
        self.val_guide_crv_edit_checkBox = self.view.guide_crv_edit_checkBox.isChecked()
    

    def sig_store_curve_comp_btn(self):
        """ 
        # for the selected component, record and replace the data for each curve. 
        # NEED:
        # add to database schema to include data that makes up a nurbs curve.
        # in ctrl creation, once ctrl is imported, record its data & add to database with a dictionary [A].
            # in ctrl creation, the ctrl is imported based on config data, 
                # if database has no data on it, means the ctrl in dictionary hasen't got any data
                    # it needs its current data stored.
                # else database has got data on it,
                    # must update the ctrl with that data.
        # with this function, any changes to scale knots, ect will replace the [A] with new data. 
        # So when the module is reloaded/created again the changes to the controls remain!
        # """
        component_selection = utils_QTree.get_component_name_TreeSel(self.view.mdl_tree_view , self.view.mdl_tree_model)
        print(f"component_selection = {component_selection}")
        total_index = len(component_selection)
        # try: 
        for stp, component in enumerate(component_selection):
            self.model.store_component_control_data(component, self.val_availableRigComboBox)

            progress_value = utils.progress_value(stp, total_index)
            self.update_progress(progress_value, f"Storing curve data: [{component}]")
        self.update_progress(0, f"DONE: Stored Curve Data")
        # except TypeError as e:
        #     cmds.error(f" Select a component in 'Character Database!' {e}")

    # -- Template Components! --
    def sig_guide_template_checkBox(self):
        try:
            self.val_guide_template_checkBox = self.view.guide_template_checkBox.isChecked()
            utils.select_set_displayType("xfm_guide_*", self.val_guide_template_checkBox, False)
        except ValueError:
                    pass


    def sig_controls_template_checkBox(self):
        try:
            self.val_controls_template_checkBox = self.view.controls_template_checkBox.isChecked()
            utils.select_set_displayType("ctrl_*", self.val_controls_template_checkBox, False)
        except ValueError:
            pass


    def sig_ddj_template_checkBox(self):
        try:
            self.val_ddj_template_checkBox = self.view.ddj_template_checkBox.isChecked()
            utils.select_set_displayType("ddj_*", self.val_ddj_template_checkBox, False)
        except ValueError:
            pass
    
    # -- Unlocked component configuration --
    def sig_compnent_checkBox(self):
        self.val_compnent_checkBox = self.view.compnent_checkBox.isChecked()


    def sig_lock_btn(self):
        if self.val_compnent_checkBox: #true
            component_selection = utils_QTree.get_component_name_TreeSel(self.view.mdl_tree_view , self.view.mdl_tree_model)
            # treeSel = ["mdl_bipedArm_0_L"]
            for component in component_selection:
                # delete any constraints on the component's guides
                # offset_xfm_guide_bipedArm_clavicle_0_L
                # bipedArm_*_0_L
                if "mdl_root_0" in component:
                    component = "mdl_root_0_M"
                parts = component.split('_')[1:] # bipedArm, 0, L
                mdl = parts[0] # bipedArm
                uID = parts[1] # 0
                side = parts[2] # L
                
                # create the box:
                if not cmds.objExists(f"cg_{mdl}_{uID}_{side}"):
                    if 'bipedArm' in component:
                        if side == "L": ctrl_type = "imp_cg_arm_L"
                        else: ctrl_type = "imp_cg_arm_R"
                    elif 'bipedLeg' in component:
                        if side == "L": ctrl_type = "imp_cg_leg_L"
                        else: ctrl_type = "imp_cg_leg_R"
                    elif 'spine' in component:
                        ctrl_type = "imp_cg_spine"
                    elif 'root' in component:
                        ctrl_type = "imp_cg_root"
                    cube_imp_ctrl = cr_ctrl.CreateControl(type=ctrl_type, name=f"cg_{mdl}_{uID}_{side}")
                    cube_locked_comp = cube_imp_ctrl.retrun_ctrl()
                else: cube_locked_comp = f"cg_{mdl}_{uID}_{side}"
                cmds.select(cl=1)
                cmds.showHidden("cg_*")
                
                try:
                    cmds.setAttr(f"{cube_locked_comp}.overrideEnabled", 1)
                    cmds.setAttr(f"{cube_locked_comp}.hiddenInOutliner", 1)
                except Exception as e:
                    print(f"Hiding CAGEE error: {e}")

                if "mdl_root_0_M" in component:
                    sel = f"offset_xfm_guide_root", f"offset_xfm_guide_COG"
                else:
                    sel = f"offset_xfm_guide_{mdl}_*_{uID}_{side}"
                cmds.select(sel) #"pointCon_xfm_guide_bipedArm_0_L")
                comp_grpXfm_ls = cmds.ls(sl=1, type="transform")
                print(f"comp_grpXfm_ls = {comp_grpXfm_ls}")
                # get constraint & delete it!
                for grpXfm in comp_grpXfm_ls:
                    if cmds.objExists(grpXfm):
                        print(f"grpXfm = {grpXfm}")
                        constraints = cmds.listRelatives(grpXfm, type='constraint', ad=0)
                        if constraints:
                            for con in constraints:
                                print(f"constraint : : {con}")
                                cmds.delete(con)
                        # constrain grps to cage!
                        utils.constrain_2_items(cube_locked_comp, grpXfm, "parent", "all")  
        else: print(f"component checkbox is not checked")


    def sig_unlock_btn(self):
        if self.val_compnent_checkBox: #true
            component_selection = utils_QTree.get_component_name_TreeSel(self.view.mdl_tree_view , self.view.mdl_tree_model)
            # treeSel = ["mdl_bipedArm_0_L"]
            for component in component_selection:
                # delete any constraints on the component's guides
                # offset_xfm_guide_bipedArm_clavicle_0_L
                # bipedArm_*_0_L
                if "mdl_root_0" in component:
                    component = "mdl_root_0_M"
                parts = component.split('_')[1:] # bipedArm, 0, L
                mdl = parts[0] # bipedArm
                uID = parts[1] # 0
                side = parts[2] # L
                
                if "mdl_root_0_M" in component:
                    sel = f"offset_xfm_guide_root", f"offset_xfm_guide_COG"
                else:
                    sel = f"offset_xfm_guide_{mdl}_*_{uID}_{side}"
                cmds.select(sel) #"pointCon_xfm_guide_bipedArm_0_L")
                comp_grpXfm_ls = cmds.ls(sl=1, type="transform")
                print(f"comp_grpXfm_ls = {comp_grpXfm_ls}")
                # get constraint & delete it!
                for grpXfm in comp_grpXfm_ls:
                    if cmds.objExists(grpXfm):
                        print(f"grpXfm = {grpXfm}")
                        constraints = cmds.listRelatives(grpXfm, type='constraint', ad=0)
                        if constraints:
                            for con in constraints:
                                print(f"constraint : : {con}")
                                cmds.delete(con)
                # hide the cages (make it specific in the future) 
                cmds.hide("cg_*")

                # add the normal following constraints!
                print(f"Comp_for selectionUNLOCK = {component}")
                # NORM = xfm_grp_bipedLeg_component_0_L
                # new = mdl_bipedLeg_0_L
                if "mdl_root_0" in component:
                    unlock_rdy_component = f"xfm_grp_{mdl}_component_{uID}_M"
                else: unlock_rdy_component = f"xfm_grp_{mdl}_component_{uID}_{side}" 
                self.model.constrain_guides_from_comp(unlock_rdy_component) 
        else: print(f"component checkbox is not checked")

    # ---- Tab 2 - edit module ----
    def sig_entire_comp_radioBtn(self):
        self.val_entire_comp_radioBtn = self.view.entire_comp_radioBtn.isChecked()


    def sig_sel_comp_radioBtn(self):
        self.val_sel_comp_radioBtn = self.view.sel_comp_radioBtn.isChecked()
        self.val_entire_comp_radioBtn = False

    # current module data! -> this data will be passed to the database!
    def sig_update_comp_data_checkBox(self):
        self.val_update_comp_data_checkBox = self.view.update_comp_data_checkBox.isChecked()
        print(f"update_comp_data_checkBox")
        if self.val_update_comp_data_checkBox:
            self.view.umo_rigType_comboBox.setEnabled(True)
            self.view.umo_mirror_checkBox.setEnabled(True)
            self.view.umo_stretch_checkBox.setEnabled(True)
            self.view.umo_twist_checkBox.setEnabled(True)
        else:
            self.view.umo_rigType_comboBox.setEnabled(False)
            self.view.umo_mirror_checkBox.setEnabled(False)
            self.view.umo_stretch_checkBox.setEnabled(False)
            self.view.umo_twist_checkBox.setEnabled(False)


    def sig_umo_rigType_comboBox(self):
        self.val_umo_rigType_comboBox = self.view.umo_rigType_comboBox.currentText()
    def sig_umo_mirror_checkBox(self):
        self.val_umo_mirror_checkBox = self.view.umo_mirror_checkBox.isChecked()
    def sig_umo_stretch_checkBox(self):
        self.val_umo_stretch_checkBox = self.view.umo_stretch_checkBox.isChecked()
    def sig_umo_twist_checkBox(self):
        self.val_umo_twist_checkBox = self.view.umo_twist_checkBox.isChecked()

    
    def sig_commit_module_edits_btn(self):
        # update the database with data for each module
        component_selection = utils_QTree.get_component_name_TreeSel(self.view.mdl_tree_view, self.view.mdl_tree_model)
        if self.val_entire_comp_radioBtn:
            # gives mdl name, need to extract all components within that!
            temp_list = []
            for mdl_list in component_selection:
                output = utils_QTree.get_components_of_selected_module(self.view.mdl_tree_model, mdl_list)
                temp_list.append(output)
            comp_list = [item for sublist in temp_list for item in sublist]
            print(f"comp_list = `{comp_list}`")
        else:
            comp_list = component_selection
            print(f"Entire radioButton is not being read {self.val_entire_comp_radioBtn}")
        if self.val_joint_editing_checkBox:
            umo_dict = {
            "mirror_rig": self.val_umo_mirror_checkBox,
            "stretch": self.val_umo_stretch_checkBox,
            "twist": self.val_umo_twist_checkBox,
            "rig_sys": self.val_umo_rigType_comboBox
            }
        else:
            umo_dict = {}
        
        # update the DB | pass joint number!
        total_index = len(comp_list)
        for stp, comp in enumerate(comp_list):
            self.model.commit_module_edit_changes(comp, self.val_availableRigComboBox, self.val_update_comp_data_checkBox, self.val_joint_editing_checkBox, self.val_ctrl_editing_checkBox, umo_dict, self.val_jnt_num_spinBox)
            
            progress_value = utils.progress_value(stp, total_index)
            self.update_progress(progress_value, f"Commiting data: [{comp}]")
        self.update_progress(0, f"DONE: Updated module options: {comp_list}")

        # update the ui (current options + update options presets)
        if self.val_joint_editing_checkBox:
            self.update_umo_label("Rig sys", self.view.cmo_rigType_lbl, umo_dict["rig_sys"])
            self.update_umo_label("Mirror", self.view.cmo_mirrorMdl_lbl, umo_dict["mirror_rig"])
            self.update_umo_label("Stretch", self.view.cmo_stretch_lbl, umo_dict["stretch"])
            self.update_umo_label("Twist", self.view.cmo_twist_lbl, umo_dict["twist"])


    def sig_joint_editing_checkBox(self):
        self.val_joint_editing_checkBox = self.view.joint_editing_checkBox.isChecked()
        if self.val_joint_editing_checkBox:
            self.view.constraint_type_comboBox.setEnabled(True)
            self.view.ik_operation_comboBox.setEnabled(True)
            self.view.jnt_num_spinBox.setEnabled(True)
        else:
            self.view.constraint_type_comboBox.setEnabled(False)
            self.view.ik_operation_comboBox.setEnabled(False)
            self.view.jnt_num_spinBox.setEnabled(False)


    def sig_ctrl_editing_checkBox(self):
        self.val_ctrl_editing_checkBox = self.view.ctrl_editing_checkBox.isChecked()
        if self.val_joint_editing_checkBox:
            self.view.ctrl_num_spinBox.setEnabled(True)
            self.view.ctrl_type_comboBox.setEnabled(True)
        else:
            self.view.ctrl_num_spinBox.setEnabled(False)
            self.view.ctrl_type_comboBox.setEnabled(False)


    def sig_jnt_num_spinBox(self):
        try:
            self.val_jnt_num_spinBox = float(self.view.jnt_num_spinBox.value())
        except ValueError as e:
            cmds.error(f"error in 'sig_jnt_numm_spinBox': {e}")


    def update_umo_label(self, name, qlabel, value):
        ''' Args: QLabel, name, value'''
        if value == "True":
            value = "Yes"
        elif value == "False":
            value = "No"
        qlabel.setText(f"{name}: {value}")


    def set_selected_module_label(self):
        pass
        # from selection set the name of the module working on
        # component_selection = utils_QTree.get_component_name_TreeSel(self.view.mdl_tree_view , self.view.mdl_tree_model)
        # mdl_name_display = ""
        # if self.val_sel_comp_radioBtn:
        #     print(f"val_sel_comp_radioBtn")
        #     parts = component_selection.split("_")
        #     mdl_name_display = parts[1]
        # print(f"J : comp_selection = {component_selection}")
        # print(f"J : Module diplay name = {mdl_name_display}")
        # self.view.selected_module_label.setText(f"Module: {mdl_name_display}")

    # ------------ Neccessary functions ------------
    def populate_available_rig_comboBox(self, name_of_rig_fld):
        # `name_of_rig_fld` will populate the ComboBox
        # IF no(None) ^folder^ in `self.db_rig_location`, print(f"No rig name folder found in {self.db_rig_location}, please create one.")
        print(f"`self.name_of_rig_fld` :: {name_of_rig_fld}")
        if name_of_rig_fld:
            print(f"Rig folder name found in {self.db_rig_location}, populating available rig option.")
            self.view.available_rig_comboBox.addItems(name_of_rig_fld)
        elif name_of_rig_fld == None:
            self.view.available_rig_comboBox.setPlaceholderText("No rig database folders")
            print(f"No rig folder name 'DB_jmvs_char*_rig' found in {self.db_rig_location}, please create one.")

    