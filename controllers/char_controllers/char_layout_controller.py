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
    utils_os,
    utils_json,
    utils_QTree
)

from systems.sys_char_rig import (
    cr_guides, 
    cr_ctrl,
    raw_data_fkik_dicts
)

from models.char_models import (
    layout_qt_models
)

from models.char_models import char_layout_model
from views.char_views import char_layout_view

# Temporarily
from databases.char_databases import (
    database_schema_002
    )

# importlib.reload(utils_os)
importlib.reload(utils)
importlib.reload(utils_os)
importlib.reload(utils_json)
importlib.reload(utils_QTree)
importlib.reload(cr_guides)
importlib.reload(cr_ctrl)
importlib.reload(raw_data_fkik_dicts)
importlib.reload(layout_qt_models)

importlib.reload(char_layout_model)
importlib.reload(char_layout_view)

# Temporarily
importlib.reload(database_schema_002)


class CharLayoutController:
    def __init__(self): # class
        self.model = char_layout_model.CharLayoutModel()
        self.view = char_layout_view.CharLayoutView()
        
        self.json_dict = utils_json.get_modules_json_dict('char_config')

        self.db_rig_location = "db_rig_storage"
        name_of_rig_fld = self.model.get_available_DB_rig_folders(self.db_rig_location)
        self.populate_available_rig_comboBox(name_of_rig_fld)
        self.val_availableRigComboBox = self.view.available_rig_comboBox.currentText()
        
        self.user_module_data = {}
        
        self.set_prerequisite_signals()
        # Connect signals and slots
        self.setup_connections()
        
        self.visualise_active_db()


    def set_prerequisite_signals(self):
        self.view.all_crv_sel_checkBox.setChecked(True)
        self.view.controls_crv_edit_checkBox.setChecked(True)
        self.view.guide_crv_edit_checkBox.setChecked(False)
        
        # Does this slow it down> -> Use the variable instead
        self.sig_all_crv_sel_checkBox()
        self.sig_ik_crv_sel_checkBox()
        self.sig_fk_crv_sel_checkBox()
        self.sig_ori_guide_sel_checkBoxx()
        self.sig_xfm_guide_sel_checkBox()
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
        '''self.view.update_comp_data_checkBox.setChecked(False)'''
        self.view.joint_editing_checkBox.setChecked(False)
        self.view.ctrl_editing_checkBox.setChecked(False)
    
        self.sig_joint_editing_checkBox()
        self.sig_ctrl_editing_checkBox()
        
        for cb in [self.view.attr_inp_hk_mtx_CB_obj, self.view.attr_inp_hk_mtx_CB_prim, self.view.attr_inp_hk_mtx_CB_scnd]:
            cb.setEnabled(False)


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
        
        # -- add modules --
        self.view.add_mdl_btn.clicked.connect(self.sig_add_module)
        self.view.add_blueprint_btn.clicked.connect(self.sig_add_blueprint)
        # -- delete modules --
        self.view.delete_comp_btn.clicked.connect(self.sig_del_comp)
        self.view.delete_mdl_btn.clicked.connect(self.sig_del_module)

        # ------------ Management options ------------
            # ---- Tab1 - Curves ----
                # ---- Curve Editing ----
        self.view.all_crv_sel_checkBox.stateChanged.connect(self.sig_all_crv_sel_checkBox)
        self.view.ik_crv_sel_checkBox.stateChanged.connect(self.sig_ik_crv_sel_checkBox)
        self.view.fk_crv_sel_checkBox.stateChanged.connect(self.sig_fk_crv_sel_checkBox)
        self.view.ori_guide_sel_checkBox.stateChanged.connect(self.sig_ori_guide_sel_checkBoxx)
        self.view.xfm_guide_sel_checkBox.stateChanged.connect(self.sig_xfm_guide_sel_checkBox)

        self.view.mirror_comp_btn.clicked.connect(self.sig_mirror_comp_btn)
        self.view.store_curve_comp_btn.clicked.connect(self.sig_store_curve_comp_btn)

        self.view.controls_crv_edit_checkBox.stateChanged.connect(self.sig_ctrl_crv_edit_checkBox)
        self.view.guide_crv_edit_checkBox.stateChanged.connect(self.sig_guide_crv_edit_checkBox)
        self.view.select_data_in_comp_btn.clicked.connect(self.sig_sl_data_in_comp_btn)
                # ---- Template Display ----
        self.view.guide_template_checkBox.stateChanged.connect(self.sig_guide_template_checkBox)
        self.view.controls_template_checkBox.stateChanged.connect(self.sig_controls_template_checkBox)
        self.view.ddj_template_checkBox.stateChanged.connect(self.sig_ddj_template_checkBox)
        self.view.show_orientation_checkBox.stateChanged.connect(self.sig_show_orientation_checkBox)
                # ---- Lock/Unlock ----
        self.view.compnent_checkBox.stateChanged.connect(self.sig_compnent_checkBox)
        self.view.lock_btn.clicked.connect(self.sig_lock_btn)
        self.view.unlock_btn.clicked.connect(self.sig_unlock_btn)
        
            # ---- Tab2 - Edit module ---- 
        self.view.entire_comp_radioBtn.clicked.connect(self.sig_entire_comp_radioBtn)
        self.view.sel_comp_radioBtn.clicked.connect(self.sig_sel_comp_radioBtn)

            # External Inout Hook Matrix
        self.view.comp_inp_hk_mtx_Qlist.clicked.connect(self.sig_comp_inp_hk_mtx_Qlist_clicked)
        self.view.attr_inp_hk_mtx_CB_obj.currentIndexChanged.connect(self.sig_attr_inp_hk_mtx_CB_obj)
        self.view.attr_inp_hk_mtx_CB_prim.currentIndexChanged.connect(self.sig_attr_inp_hk_mtx_CB_prim)

            # Output Hook Matrix

            # joint & control editing.
        self.view.joint_editing_checkBox.stateChanged.connect(self.sig_joint_editing_checkBox)
        self.view.ctrl_editing_checkBox.stateChanged.connect(self.sig_ctrl_editing_checkBox)
        self.view.jnt_num_spinBox.valueChanged.connect(self.sig_jnt_num_spinBox)
        self.view.commit_module_edits_btn.clicked.connect(self.sig_commit_module_edits_btn)


    def sig_comp_inp_hk_mtx_Qlist_clicked(self, idx):
        '''
        # Description: 
            When user selects the `component/object name in QList` it visualises 
            the `external hook matrix data` on the 3 QComboBox's with data 
            queried from the comp's database by updatying the 'Object QComboBox'.
            (Update to `Object` QComboBox causes `Prim` & `Scnd` QComboBox's to 
            update their visualisation.)
        # Arguments:
            idx (int): index of the current selected item in the QList. 
        # Return: N/A
        '''   
        print(f"----- new list sel -----")
        # setEnabled the 3 QComboBox widgets. 
        for cb in [self.view.attr_inp_hk_mtx_CB_obj, 
                   self.view.attr_inp_hk_mtx_CB_prim, 
                   self.view.attr_inp_hk_mtx_CB_scnd]:
            cb.setEnabled(True)

        # get current database name
        component_name = idx.data()        
        ''' 
        Not sure what I wanted to do with this function below 
            # self.update_ext_inp_hk_mtx_comboBoxs(component_name)
        '''
        
        # get a list of all component names present in the QList. 
        model = self.view.comp_inp_hk_mtx_Qlist_Model
        Qlist_compnent_names = []
        for row in range(model.rowCount()):
            index = model.index(row, 0)
            item = model.data(index)
            if item is not None:
                Qlist_compnent_names.append(item)
        
        # get the `external input_hook_mtx_plg list` from selected component db: `[*object.*attr]`
        db_inp_hook_mtx_ls = self.model.get_db_inp_hook_mtx_from_Qlist(component_name, self.val_availableRigComboBox)
        
        # get the object & attr seperated into lists from the `external input_hook_mtx_plg list`
        ext_obj_ls, ext_atr_ls = self.model.get_inp_hook_mtx_obj_data(db_inp_hook_mtx_ls)

        # sets the inp hook obj QComboBox
        self.model.set_inp_hook_obj_comboBox(Qlist_compnent_names, ext_obj_ls, self.view.attr_inp_hk_mtx_CB_obj)
        

    def sig_attr_inp_hk_mtx_CB_obj(self):
        '''
        # Description: 
            When user selects the `component/object name comboBox(top right)` 
            it updates the `prim & scnd comboBox's` with their hook attributes.  
        # Arguments: N/A
        # Return: N/A
        '''       
        ext_obj_component_name = self.view.attr_inp_hk_mtx_CB_obj.currentText()
        print(f">>>ext_obj_component_name = {ext_obj_component_name}")

        if ext_obj_component_name == 'None':
            print(f"ext_obj_component_name = 'NONE'")

            # Reset the  the CB atr (prim & scnd)
            utils_QTree.populate_ext_inp_hk_mtx_atrComboBox_model(
                self.view.attr_inp_hk_mtx_CB_prim, self.view.attr_inp_hk_mtx_CB_scnd
                )
        else:
            print(f"ext_obj_component_name EXISTS in the blueprint")
            
            # get current database name.
            component_name_Qlist = utils_QTree.get_current_selected_item_Qlist(self.view.comp_inp_hk_mtx_Qlist, self.view.comp_inp_hk_mtx_Qlist_Model)
            print(f"& component_name_Qlist = {component_name_Qlist}")

            # get the `current input_hook_mtx_plg list` from selected component db: `[*object.*attr]`
            db_inp_hook_mtx_ls = self.model.get_db_inp_hook_mtx_from_Qlist(component_name_Qlist, self.val_availableRigComboBox)
            print(f" sig_attr_inp_hk_mtx_CB_obj() - current db_inp_hook_mtx_ls = {db_inp_hook_mtx_ls}")

            # get the object & attr seperated into lists from the `external input_hook_mtx_plg list`
            inp_obj_ls, inp_atr_ls = self.model.get_inp_hook_mtx_obj_data(db_inp_hook_mtx_ls)
            print(f" sig_attr_inp_hk_mtx_CB_obj() - current inp_atr_ls = {inp_atr_ls}")

            # get the `output_hook_mtx_atr list` from .db using `external inp_hk_mtx component name`: `[*attr, *attr]`
            db_out_hook_mtx_ls = self.model.get_db_out_hook_mtx_from_comboBox(ext_obj_component_name, self.val_availableRigComboBox)
            print(f"*db_out_hook_mtx_ls = {db_out_hook_mtx_ls}")

            # Create an dictionary using the output_hook_atr data from the external 
            # component's data: external component output list = {'ext_prim': *atr, 'ext_scnd': *atr}
            ext_atr_dict = self.model.cr_out_hook_mtx_atr_dict(db_out_hook_mtx_ls)
            
            self.model.set_inp_hook_atrs_comboBox_items(
                ext_atr_dict, 
                self.view.attr_inp_hk_mtx_CB_prim, 
                self.view.attr_inp_hk_mtx_CB_scnd
                )
            self.model.set_inp_hook_atrs_comboBox_placeholder(
                ext_atr_dict,
                inp_atr_ls, 
                self.view.attr_inp_hk_mtx_CB_prim, 
                self.view.attr_inp_hk_mtx_CB_scnd
            )


    def sig_attr_inp_hk_mtx_CB_prim(self):
        '''
        # Description: 
            Changes to the `Prim` QComboBox to update the `external 
            input_hook_mtx_plg list` first index attribute in the .db file using 
            the currently selected component name in the Qlist.  
        # Arguments: N/A
        # Return: N/A
        '''
        # get current database name.
        component_name_Qlist = utils_QTree.get_current_selected_item_Qlist(
            self.view.comp_inp_hk_mtx_Qlist, self.view.comp_inp_hk_mtx_Qlist_Model)
        print(f" - CB_Prim component_name: {component_name_Qlist} ")
        
        obj_text = self.view.attr_inp_hk_mtx_CB_obj.currentText()
        prim_text = self.view.attr_inp_hk_mtx_CB_prim.currentText()

        if not prim_text == 'None':
            self.model.update_db_inp_hook_mtx(
                component_name_Qlist, obj_text, prim_text, 'None', self.val_availableRigComboBox)


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
        self.visualise_active_db()
        print(f"available rig chosen: `{self.val_availableRigComboBox}`")


    def sig_rpl_live_component(self):
        '''
        # Description:
            Retrieve the selected component(in GUI) and update its database with Pos, Rot & 
            fk/ik_pos/rot raw control data.
        # Attributes: N/A 
        # Returns: N/A 
        '''
        # print selection in ui:
        component_selection = utils_QTree.get_component_name_TreeSel(self.view.mdl_tree_view , self.view.mdl_tree_model)
        # for component in component_selection:
        total_index = len(component_selection)
        for stp, component in enumerate(component_selection):
            module, unique_id, side = utils.get_name_id_data_from_component(component)
            self.model.record_component_position(component, self.val_availableRigComboBox)
            self.model.record_compnonent_orientation(component, self.val_availableRigComboBox)

            # Update the fk/ik_pos/rot raw data!
            self.model.update_component_fkik_control_dicts(component, self.val_availableRigComboBox)

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
            self.visualise_active_db()
            
            # progress_value = utils.progress_value()
    
    # ---- add blueprint ----
    def func_create_guides(self, component_selection):
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
                    cmds.parent("grp_ori_components", "grp_components")
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
        self.func_create_guides(component_selection)
        self.model.func_unlocked_all(component_selection, self.val_availableRigComboBox)
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
        self.func_create_guides(component_selection)
        self.model.func_unlocked_all(component_selection, self.val_availableRigComboBox)
        self.update_progress(0, f"DONE: '{self.val_availableRigComboBox}' Blueprint")


    # -- delete modules --
    def sig_del_comp(self):
        print(f"delete comp button clicked")
        component_selection_ls = utils_QTree.get_component_name_TreeSel(self.view.mdl_tree_view, self.view.mdl_tree_model)
        
        print(f"Del_Comp > `component_selection_ls` = `{component_selection_ls}`")
        for comp_sel in component_selection_ls:
            self.model.delete_database_component(comp_sel, self.val_availableRigComboBox, self.view.mdl_tree_model)
            self.model.delete_scene_component(comp_sel)
            self.visualise_active_db()


    def sig_del_module(self):
        print(f"delete module button clicked")
        module_selection_ls = utils_QTree.get_module_name_TreeSel(self.view.mdl_tree_view, self.view.mdl_tree_model)
        print(f"module_selection_ls = {module_selection_ls}")
        for module in module_selection_ls:
            self.model.delete_scene_module(module, self.view.mdl_tree_model)
            self.model.delete_database_module(module, self.val_availableRigComboBox, self.view.mdl_tree_model)
            self.visualise_active_db()


    # ------------ management options siFunc ------------
    # ---- Tab 1 - select data ----
    def sig_all_crv_sel_checkBox(self):
        self.val_all_crv_sel_checkBox = self.view.all_crv_sel_checkBox.isChecked()
        if self.val_all_crv_sel_checkBox:
            self.view.ik_crv_sel_checkBox.setEnabled(False)
            self.view.fk_crv_sel_checkBox.setEnabled(False)
        else:
            self.view.ik_crv_sel_checkBox.setEnabled(True)
            self.view.fk_crv_sel_checkBox.setEnabled(True)
    def sig_ik_crv_sel_checkBox(self):
        self.val_ik_crv_sel_checkBox = self.view.ik_crv_sel_checkBox.isChecked()
        if self.val_ik_crv_sel_checkBox:
            self.val_ik_crv_sel_checkBox = "ik"
    def sig_fk_crv_sel_checkBox(self):
        self.val_fk_crv_sel_checkBox = self.view.fk_crv_sel_checkBox.isChecked()
        if self.val_fk_crv_sel_checkBox:
            self.val_fk_crv_sel_checkBox = "fk"
    def sig_ori_guide_sel_checkBoxx(self):
        self.val_ori_guide_sel_checkBoxx = self.view.ori_guide_sel_checkBox.isChecked()
        print(f"val_ori_guide_sel_checkBoxx = {self.val_ori_guide_sel_checkBoxx}")
    def sig_xfm_guide_sel_checkBox(self):
        self.val_xfm_guide_sel_checkBox = self.view.xfm_guide_sel_checkBox.isChecked()
        print(f"val_xfm_guide_sel_checkBox = {self.val_xfm_guide_sel_checkBox}")
        

    def sig_sl_data_in_comp_btn(self):
        print(f"> Select data in chosen components!")
        comp_sel = utils_QTree.get_component_name_TreeSel(self.view.mdl_tree_view , self.view.mdl_tree_model)
        try:
            for comp in comp_sel:
                self.model.select_component_data(
                    comp, self.val_availableRigComboBox,  self.val_all_crv_sel_checkBox, 
                    self.val_ik_crv_sel_checkBox, self.val_fk_crv_sel_checkBox, 
                    self.val_ori_guide_sel_checkBoxx, self.val_xfm_guide_sel_checkBox)
        except TypeError as e:
            cmds.error(f"Select a component first!: |{e}|")


    def sig_ctrl_crv_edit_checkBox(self):
        self.val_ctrl_crv_edit_checkbox = self.view.controls_crv_edit_checkBox.isChecked()


    def sig_guide_crv_edit_checkBox(self):
        self.val_guide_crv_edit_checkBox = self.view.guide_crv_edit_checkBox.isChecked()
    

    def sig_mirror_comp_btn(self, ):
        component_selection = utils_QTree.get_component_name_TreeSel(self.view.mdl_tree_view , self.view.mdl_tree_model)
        print(f"component_selection = {component_selection}")
        total_index = len(component_selection)
        # try: 
        for stp, component in enumerate(component_selection):
            self.model.mirror_component_data(component, self.val_availableRigComboBox, self.view.mdl_tree_model, self.val_ctrl_crv_edit_checkbox, self.val_guide_crv_edit_checkBox)
            self.visualise_active_db()

            progress_value = utils.progress_value(stp, total_index)
            self.update_progress(progress_value, f"Storing curve data: [{component}]")
        self.update_progress(0, f"DONE: Mirrored component Data")


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
    

    def sig_show_orientation_checkBox(self):
        try:
            self.val_show_orientation_checkBox = self.view.show_orientation_checkBox.isChecked()
            if self.val_show_orientation_checkBox:
                print("Hide Orientation")
                cmds.hide("grp_ori_components")
            if not self.val_show_orientation_checkBox:
                print("Show Orientation")
                cmds.showHidden("grp_ori_components")
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
                module, unique_id, side = utils.get_name_id_data_from_component(component)
    
                # create the arrow guide:
                lock_guide_name = f"lock_{module}_{unique_id}_{side}"
                if not cmds.objExists(lock_guide_name):
                    cube_imp_ctrl = cr_ctrl.CreateControl(type="arrow", name=lock_guide_name)
                    lock_guide_name = cube_imp_ctrl.retrun_ctrl()
                    
                    first_guide = utils.get_first_child(f"xfm_grp_{module}_component_{unique_id}_{side}") # xfm_grp_spine_component_0_M
                    utils.mtrans_and_pivot_to_origin(target_obj=lock_guide_name, source_obj=first_guide, 
                                                     translation_vector=(0, 15, 0), rotate={"X":180})
                    cmds.parent(lock_guide_name, f"grp_misc_{module}_component_{unique_id}_{side}")
                    utils.clean_opm(lock_guide_name)
                    
                cmds.select(cl=1)
                cmds.showHidden(lock_guide_name)
                
                try:
                    cmds.setAttr(f"{lock_guide_name}.overrideEnabled", 1)
                    cmds.setAttr(f"{lock_guide_name}.overrideColor", 14)
                    
                except Exception as e:
                    print(f"Hiding lock_guide error: {e}")

                # if "module_root_0_M" in component:
                #     sel = f"offset_xfm_guide_root", f"offset_xfm_guide_COG"
                # else:
                sel = f"offset_xfm_guide_{module}_*_{unique_id}_{side}"
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
                        utils.constrain_2_items(lock_guide_name, grpXfm, "parent", "all")  
                cmds.select(cl=1)
        else: print(f"component checkbox is not checked")


    def sig_unlock_btn(self):
        if self.val_compnent_checkBox: #true
            component_selection = utils_QTree.get_component_name_TreeSel(self.view.mdl_tree_view , self.view.mdl_tree_model)
            for component in component_selection:
                module, unique_id, side = utils.get_name_id_data_from_component(component)            
                sel = f"offset_xfm_guide_{module}_*_{unique_id}_{side}"
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
                cmds.hide(f"lock_{module}_{unique_id}_{side}")
                self.model.guide_connections_setup(component, self.val_availableRigComboBox) 
                cmds.select(cl=1)
        else: print(f"component checkbox is not checked")

    # ---- Tab 2 - edit module ----
    def sig_entire_comp_radioBtn(self):
        self.val_entire_comp_radioBtn = self.view.entire_comp_radioBtn.isChecked()


    def sig_sel_comp_radioBtn(self):
        self.val_sel_comp_radioBtn = self.view.sel_comp_radioBtn.isChecked()
        self.val_entire_comp_radioBtn = False

    
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
        # if self.val_joint_editing_checkBox:
        #     umo_dict = {
        #     "mirror_rig": self.val_umo_mirror_checkBox,
        #     "stretch": self.val_umo_stretch_checkBox,
        #     "twist": self.val_umo_twist_checkBox,
        #     "rig_sys": self.val_umo_rigType_comboBox
        #     }
        # else:
        #     umo_dict = {}
        
        # update the DB | pass joint number!
        total_index = len(comp_list)
        for stp, comp in enumerate(comp_list):
            self.model.commit_module_edit_changes(comp, self.val_availableRigComboBox, self.val_joint_editing_checkBox, self.val_ctrl_editing_checkBox, self.val_jnt_num_spinBox)
            
            progress_value = utils.progress_value(stp, total_index)
            self.update_progress(progress_value, f"Commiting data: [{comp}]")
        self.update_progress(0, f"DONE: Updated module options: {comp_list}")


    def sig_joint_editing_checkBox(self):
        self.val_joint_editing_checkBox = self.view.joint_editing_checkBox.isChecked()
        if self.val_joint_editing_checkBox:
            # self.view.constraint_type_comboBox.setEnabled(True)
            # self.view.ik_operation_comboBox.setEnabled(True)
            self.view.jnt_num_spinBox.setEnabled(True)
        else:
            # self.view.constraint_type_comboBox.setEnabled(False)
            # self.view.ik_operation_comboBox.setEnabled(False)
            self.view.jnt_num_spinBox.setEnabled(False)


    def sig_ctrl_editing_checkBox(self):
        self.val_ctrl_editing_checkBox = self.view.ctrl_editing_checkBox.isChecked()
        if self.val_joint_editing_checkBox:
            self.view.ctrl_num_spinBox.setEnabled(True)
            self.view.ctrl_type_btn.setEnabled(True)
        else:
            self.view.ctrl_num_spinBox.setEnabled(False)
            self.view.ctrl_type_btn.setEnabled(False)


    def sig_jnt_num_spinBox(self):
        try:
            self.val_jnt_num_spinBox = float(self.view.jnt_num_spinBox.value())
        except ValueError as e:
            cmds.error(f"error in 'sig_jnt_numm_spinBox': {e}")


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
        if name_of_rig_fld:
            print(f"Rig folder name found in {self.db_rig_location}, populating available rig option.")
            self.view.available_rig_comboBox.addItems(name_of_rig_fld)
        elif name_of_rig_fld == None:
            self.view.available_rig_comboBox.setPlaceholderText("No rig database folders")
            print(f"No rig folder name 'DB_jmvs_char*_rig' found in {self.db_rig_location}, please create one.")

    
    def visualise_active_db(self):
        '''
        # Description:
            call classes to update the gui with database iformation dynamically.
        '''

        self.db_rig_directory = utils_os.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", 
            self.db_rig_location, self.val_availableRigComboBox
            )

        print(f"** trying to run new visualise_active_db_")
        # QTreeView Update
        print(f" ~ visualise_active_db: ")
        layout_qt_models.UpdateQTreeModel(
            self.db_rig_directory, self.view)
        
        # Output Hook Matrix QListView Update
        layout_qt_models.UpdateOutputHookQListModel(
            self.db_rig_directory, self.view)
        
        # External Input Hook Matrix QListView Update
        layout_qt_models.UpdateExtInputHookQListModel(
            self.db_rig_directory, self.view)
        

    def update_ext_inp_hk_mtx_comboBoxs(self, component_name):
        # get all database item's names
        pass