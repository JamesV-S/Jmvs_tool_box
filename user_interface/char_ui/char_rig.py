
import maya.cmds as cmds
from maya import OpenMayaUI

try:
    from PySide6 import QtCore, QtWidgets, QtGui
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import (QWidget)
    from shiboken6 import wrapInstance
except ModuleNotFoundError:
    from PySide2 import QtCore, QtWidgets, QtGui
    from PySide2.QtCore import Qt
    from PySide2.QtGui import QIcon
    from PySide2.QtWidgets import (QWidget)
    from shiboken2 import wrapInstance

import sys
import random
import importlib
import os
import json

from databases.char_databases import database_schema_002
from systems import (
    os_custom_directory_utils,
    utils
)
from systems.sys_char_rig import (
    cr_guides, 
    cr_ctrl
)

importlib.reload(database_schema_002)
importlib.reload(os_custom_directory_utils)
importlib.reload(utils)
importlib.reload(cr_guides)
importlib.reload(cr_ctrl)
# For the time being, use this file to simply call the 'modular_char_ui.py'
maya_main_wndwPtr = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndwPtr), QWidget)


class CharRigging(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CharRigging, self).__init__(parent)
        version = "001"
        ui_object_name = f"JmvsCharRig_{version}"
        ui_window_name = f"Jmvs_character_tool_{version}"
        utils.delete_existing_ui(ui_object_name)
        self.setObjectName(ui_object_name)

        # set flags & dimensions
        # ---------------------------------- 
        self.setParent(main_window) 
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(ui_window_name)
        self.resize(400, 550)
        
        # style
        stylesheet_path = os.path.join(
            os_custom_directory_utils.create_directory("Jmvs_tool_box", "assets", "styles"), 
            "char_style_sheet_001.css"
            )
        print(stylesheet_path)
        with open(stylesheet_path, "r") as file:
            stylesheet = file.read()
        self.setStyleSheet(stylesheet)
        
        # button functions
        # ----------------------------------        
        self.current_dir = os.path.dirname(os.path.abspath(__file__))

        # gather the existing files in 'config' and create a list of the files
        # Placeholder: 
        
        # TAB 1 = Modules
        self.orientation = "xyz"
        
        # derive the `self.json_all_mdl_list` from the config folder!
        #self.json_all_mdl_list = ['biped_arm.json', 'biped_leg.json']
        self.json_dict = self.get_modules_json_dict()
        
        self.user_module_data = {} # to store user inputs from 'choose module ui'! 
        
        self.UI_modules()
        self.UI_tab1_connect_signals()        
        
        # -- paramaters --
        # What's the syntax for rig database folders?
        self.db_rig_location = "db_rig_storage"
        self.name_of_DB_mdl_file = None # `DB_mdl_bipedArm.db`
        name_of_rig_fld = self.get_available_DB_rig_folders(self.db_rig_location)
        self.populate_available_rig(name_of_rig_fld)
        
        self.visualise_active_db()
        # self.load_rig_group()

    def UI_modules(self):
        main_Vlayout = QtWidgets.QVBoxLayout(self)
        main_Vlayout.setObjectName("main_Layout")
        
        

        top_Hlayout = QtWidgets.QHBoxLayout() # db_vis & mdl_choose
        bottom_Vlayout = QtWidgets.QVBoxLayout() # add_blueprint & updating db

        main_Vlayout.addLayout(top_Hlayout)
        main_Vlayout.addLayout(bottom_Vlayout)
        
        # style the labels
        style_treeview_ui = [] 
        # style_module_ui_labels = []
        style_update_mdl_ui = []
        style_addRemove_ui = []
        style_template_ui = []
        style_lockUnlock_ui = []
        
        #----------------------------------------------------------------------
        # ---- database editor ----
        layV_module_Tree = QtWidgets.QVBoxLayout()
        
        self.tree_view_name_lbl = QtWidgets.QLabel("Database: `Rig Name`")
        self.tree_view_name_lbl.setObjectName("tree_DB_NAME_lbl")
        style_treeview_ui.append(self.tree_view_name_lbl)

        self.mdl_tree_model = QtGui.QStandardItemModel()
        self.mdl_tree_model.setColumnCount(1)

        self.mdl_tree_view = QtWidgets.QTreeView(self)
        self.mdl_tree_view.setModel(self.mdl_tree_model)
        self.mdl_tree_view.setObjectName("mdl_treeview")
        style_treeview_ui.append(self.mdl_tree_view)

        # set selection mode to multiSelection
        self.mdl_tree_view.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        layV_module_Tree.addWidget(self.tree_view_name_lbl)
        layV_module_Tree.addWidget(self.mdl_tree_view)
        
        # -- treeView settings --
        header = self.mdl_tree_view.header()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.mdl_tree_view.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Maximum)
        self.mdl_tree_view.setMinimumSize(150, 200)
        self.mdl_tree_view.setHeaderHidden(True)
        self.mdl_tree_view.setAnimated(True)
        self.mdl_tree_view.setUniformRowHeights(True)
        self.mdl_tree_view.setEditTriggers(QtWidgets.QAbstractItemView.SelectedClicked)
        layV_module_Tree.setSpacing(5)
        # from selection in treeView, just uses name to select the
        top_Hlayout.addLayout(layV_module_Tree)

        #----------------------------------------------------------------------
        # ---- choose modules ----        
        layV_choose_mdl_ancestor = QtWidgets.QVBoxLayout()
        #layV_choose_mdl_ancestor.setContentsMargins(40, 0, 0, 40)
        #layV_choose_mdl_ancestor.setSpacing()
        
        # -- Available RIG --
        layV_available_rig = QtWidgets.QVBoxLayout()
        # layV_available_rig.setContentsMargins(0, 0, 0, 0)

        available_rig_lbl = QtWidgets.QLabel("Available RIG:")
        style_treeview_ui.append(available_rig_lbl)

        available_rig_lbl.setFixedSize(200,20)
        self.available_rig_comboBox = QtWidgets.QComboBox()
        self.available_rig_comboBox.setFixedSize(225,30)
        self.val_availableRigComboBox = self.available_rig_comboBox.currentText()
        style_treeview_ui.append(self.available_rig_comboBox)

        #layV_available_rig.addWidget(available_rig_lbl)
        layV_available_rig.addWidget(self.available_rig_comboBox)
        layV_choose_mdl_ancestor.addLayout(layV_available_rig)

        # -- Add module editor --
        layV_add_mdl_layout = QtWidgets.QVBoxLayout()

        def module_choose_ui(mdl_name, side_items):
            mdl_h_layout = QtWidgets.QHBoxLayout()
            
            mdl_checkBox = QtWidgets.QCheckBox()
            mdl_name_label = QtWidgets.QLabel(mdl_name)
            mdl_name_label.setFixedSize(70, 30)
            style_treeview_ui.append(mdl_name_label)
            style_treeview_ui.append(mdl_checkBox)
            
            mdl_iterations = QtWidgets.QSpinBox()
            mdl_iterations.setMinimum(1)
            mdl_iterations.setEnabled(False)
            mdl_iterations.setFixedSize(50, 30)
            style_treeview_ui.append(mdl_iterations)
            
            
            mdl_h_layout.addWidget(mdl_checkBox)
            mdl_h_layout.addWidget(mdl_name_label)
            mdl_h_layout.addWidget(mdl_iterations)
            
            mdl_side = None
            if side_items != "None":
                mdl_side = QtWidgets.QComboBox()
                mdl_side.addItems(side_items)
                mdl_side.setEnabled(False)
                mdl_h_layout.addWidget(mdl_side)
                mdl_side.setFixedSize(55, 30)
                style_treeview_ui.append(mdl_side)
                
            layV_add_mdl_layout.addLayout(mdl_h_layout)

            return mdl_checkBox, mdl_iterations, mdl_side

        # get mdl_name and side data for each module
        try:
            mdl_list = []
            side_list = []
            for filename, data in self.json_dict.items():
                # `.get()` used to access dict values, without keyerror if not 
                # like we get with `[]`
                mdl_name = data.get('mdl_name', 'no module name, there should be')
                # .get a nested value within a dict; empty '{}' means no error if 'user_settings' is missing.
                mdl_side = data.get('user_settings', {}).get('side', ['No side in mdl'])
                if mdl_name:
                    mdl_list.append(mdl_name)
                    if mdl_side == ['None']:
                        side_list.append([""])
                        print(f"HAHAHAHHAHAH {side_list}")
                    else:
                        side_list.append(mdl_side)
                        print(f">>> NONOONONONOON {side_list}")
            
            print(mdl_list) #['bipedArm', 'bipedLeg']
            print(side_list) #[['L', 'R'], ['L', 'R']]
        except KeyError as e:
            print(f"{e} is not a key in {filename}")
        
        # Create the ui components & store it in a dict
        ''' Signal Functions are handled here! '''
        self.mdl_choose_ui_dict = {}
        for mdl, sides in zip(mdl_list, side_list):
            mdl_choose_buttons = module_choose_ui(mdl, sides)
            self.mdl_choose_ui_dict[mdl] = mdl_choose_buttons
        print(f"self.mdl_choose_ui_dict = {self.mdl_choose_ui_dict}")
        
        layV_choose_mdl_ancestor.addLayout(layV_add_mdl_layout)

        top_Hlayout.addLayout(layV_choose_mdl_ancestor)

        #----------------------------------------------------------------------
        # -- Selected mdl operations --
        # self.layGRP_mdl_operations = QtWidgets.QGroupBox("GroupBoxTitle_001", self)
        #font = QtGui.QFont("Times New Roman",  12)
        #font.setBold(True)
        #self.layGRP_mdl_operations.setFont(font)
        layV_mdl_operations_ancestor = QtWidgets.QVBoxLayout()
        # -- Pusblish module additions --
        layH_publish_mdl_additons = QtWidgets.QHBoxLayout()
        # update mdl with new positions!
        self.rpl_live_component = QtWidgets.QPushButton("Replace live Component")
        self.publish_btn = QtWidgets.QPushButton("+ Publish Module Additions")
        layH_publish_mdl_additons.addWidget(self.rpl_live_component)
        layH_publish_mdl_additons.addWidget(self.publish_btn)
        style_treeview_ui.append(self.publish_btn)
        style_treeview_ui.append(self.rpl_live_component)

        layV_mdl_operations_ancestor.addLayout(layH_publish_mdl_additons)

        mdl_data_lbl = QtWidgets.QLabel("Module Data:")
        mdl_data_lbl.setObjectName("mdl_data_lbl")
        style_update_mdl_ui.append(mdl_data_lbl)

        # -- current_mdl_operations --
        #layV_current_MO_parent = QtWidgets.QVBoxLayout()
        layGrid_update = QtWidgets.QGridLayout()

        cmo_lbl = QtWidgets.QLabel("Current >")
        cmo_lbl.setObjectName("update_left_lbl")
        self.cmo_rigType_lbl = QtWidgets.QLabel("Rig Type: _ _")
        self.cmo_mirrorMdl_lbl = QtWidgets.QLabel("Mirror: _ _")
        self.cmo_stretch_lbl = QtWidgets.QLabel("Stretch: _ _")
        self.cmo_twist_lbl = QtWidgets.QLabel("Twist: _ _")
        
        
        umo_lbl = QtWidgets.QLabel("Update >")
        umo_lbl.setObjectName("update_left_lbl")
        umo_rigType_lbl = QtWidgets.QLabel("Rig Type:")
        style_update_mdl_ui.append(umo_rigType_lbl)
        self.umo_rigType_comboBox = QtWidgets.QComboBox()
        self.umo_rigType_comboBox.addItems(["FK", "IK", "IKFK"])
        self.umo_mirrorMdl_checkBox = QtWidgets.QCheckBox("Mirror")
        self.umo_stretch_checkBox = QtWidgets.QCheckBox("Stretch")
        self.umo_twist_checkBox = QtWidgets.QCheckBox("Twist")
        
        cmo_ls = [cmo_lbl, self.cmo_rigType_lbl, self.cmo_mirrorMdl_lbl, self.cmo_stretch_lbl, self.cmo_twist_lbl]
        umd_ls = [umo_lbl, self.umo_rigType_comboBox, self.umo_mirrorMdl_checkBox, self.umo_stretch_checkBox, self.umo_twist_checkBox]
        cmo_pos_ls = [[0,0], [0,1], [0,2], [0,3], [0,4]]
        umd_pos_ls = [[1,0], [1,1], [1,2], [1,3], [1,4]]
        for x in range(len(cmo_ls)):
            layGrid_update.addWidget(cmo_ls[x], cmo_pos_ls[x][0], cmo_pos_ls[x][1])
            layGrid_update.addWidget(umd_ls[x], umd_pos_ls[x][0], umd_pos_ls[x][1])
            style_update_mdl_ui.append(cmo_ls[x])
            style_update_mdl_ui.append(umd_ls[x])
        
        def layH_SPACER_func():
            # -- Horizontal Spacer --
            layH_Spacer = QtWidgets.QHBoxLayout()
            # Add the spacer QWidget
            spacerH = QtWidgets.QLabel()# QtWidgets.QWidget()
            #spacerH.setFixedSize(40,40)
            spacerH.setObjectName("Spacer")
            style_update_mdl_ui.append(spacerH)
            layH_Spacer.addWidget(spacerH)
            layH_Spacer.setContentsMargins(0, 0, 0, 0)
            return layH_Spacer

        layH_upd_mdl_btn = QtWidgets.QHBoxLayout()
        SpacerGraphic_0_layH = layH_SPACER_func()
        self.update_btn = QtWidgets.QPushButton("Update Module Data")
        style_update_mdl_ui.append(self.update_btn)

        SpacerGraphic_1_layH = layH_SPACER_func()
        layH_upd_mdl_btn.addLayout(SpacerGraphic_0_layH)
        layH_upd_mdl_btn.addWidget(self.update_btn)
        layH_upd_mdl_btn.addLayout(SpacerGraphic_1_layH)
        
        layV_mdl_operations_ancestor.addWidget(mdl_data_lbl)
        layV_mdl_operations_ancestor.addLayout(layGrid_update)
        layV_mdl_operations_ancestor.addLayout(layH_upd_mdl_btn)
        
        bottom_Vlayout.addLayout(layV_mdl_operations_ancestor)

        # ---------------------------------------------------------------------
        # Updating modules and database
        layV_deleteAdd_mdl_ancestor = QtWidgets.QVBoxLayout()
        
        # -- delete mdl btns --
        layH_mdl_delete = QtWidgets.QHBoxLayout()
        self.delete_mdl_btn = QtWidgets.QPushButton("Remove module") # selected mdl
        self.delete_blueprint_btn = QtWidgets.QPushButton("Delete Blueprint") # entire blueprint
        layH_mdl_delete.addWidget(self.delete_mdl_btn)
        layH_mdl_delete.addWidget(self.delete_blueprint_btn)
        
        # -- add mdl btns --
        layH_mdl_add = QtWidgets.QHBoxLayout()
        self.add_mdl_btn = QtWidgets.QPushButton("Add module") # selected mdl
        self.add_blueprint_btn = QtWidgets.QPushButton("Create Blueprint") # add entire blueprint(deletes old and remakes it)
        layH_mdl_add.addWidget(self.add_mdl_btn)
        layH_mdl_add.addWidget(self.add_blueprint_btn)

        layV_deleteAdd_mdl_ancestor.addLayout(layH_mdl_delete)
        layV_deleteAdd_mdl_ancestor.addLayout(layH_mdl_add)

        self.add_mdl_btn.setObjectName("add_mdl_btn")
        self.add_blueprint_btn.setObjectName("add_blueprint_btn")
        self.delete_mdl_btn.setObjectName("remove_mdl_btn")
        self.delete_blueprint_btn.setObjectName("delete_blueprint_btn")

        bottom_Vlayout.addLayout(layV_deleteAdd_mdl_ancestor)

        # ---------------------------------------------------------------------
        # ---- component editing ----
        layH_componentEditing_ancestor = QtWidgets.QHBoxLayout()
        
        # -- Template Display -- 
        self.grp_boxTempDisp = QtWidgets.QGroupBox("Template Display", self)
        self.grp_boxTempDisp.setObjectName("grp_boxTempDisp")
        self.grp_boxTempDisp.setObjectName("grp_boxTempDisp")

        layV_tempDisp = QtWidgets.QVBoxLayout()
        
        self.guide_template_checkBox = QtWidgets.QCheckBox("Guides")
        self.controls_template_checkBox = QtWidgets.QCheckBox("Controls")
        self.ddj_template_checkBox = QtWidgets.QCheckBox("Deform Diagnostics")
        layV_tempDisp.addWidget(self.guide_template_checkBox)
        layV_tempDisp.addWidget(self.controls_template_checkBox)
        layV_tempDisp.addWidget(self.ddj_template_checkBox)

        # set checkBox by default
        self.controls_template_checkBox.setChecked(True)
        self.ddj_template_checkBox.setChecked(True)

        # - template gid buttons - 
        layGrid_tempDisp = QtWidgets.QGridLayout()
        self.temp_Toggle_btn = QtWidgets.QPushButton("Toggle")
        self.temp_Isolate_btn = QtWidgets.QPushButton("Isolate")
        self.temp_All_btn = QtWidgets.QPushButton("Template All")
        self.temp_AllVis_btn = QtWidgets.QPushButton("All Visible")

        layGrid_tempDisp.addWidget(self.temp_Toggle_btn, 0, 0)
        layGrid_tempDisp.addWidget(self.temp_Isolate_btn, 0, 1)
        layGrid_tempDisp.addWidget(self.temp_All_btn, 1, 0)
        layGrid_tempDisp.addWidget(self.temp_AllVis_btn, 1, 1)

        layV_tempDisp.addLayout(layGrid_tempDisp)

        # layV_tempDisp.addLayout(layGrid_tempDisp)
        
        # -- Lock/Unlock --
        self.grp_boxUL = QtWidgets.QGroupBox("Lock/Unlock", self)
        self.grp_boxUL.setObjectName("grp_boxUL")

        layV_LU = QtWidgets.QVBoxLayout()
        
        self.compnent_checkBox = QtWidgets.QCheckBox("Component")
        self.val_compnent_checkBox = 0
        self.inputComp_checkBox = QtWidgets.QCheckBox("Input Components")
        self.OutputComp = QtWidgets.QCheckBox("Output Components")
        layV_LU.addWidget(self.compnent_checkBox)
        layV_LU.addWidget(self.inputComp_checkBox)
        layV_LU.addWidget(self.OutputComp)

        # - lock gid buttons - 
        layGrid_LU = QtWidgets.QGridLayout()
        self.lock_btn = QtWidgets.QPushButton("Lock")
        self.unlock_btn = QtWidgets.QPushButton("Unlock")

        layGrid_LU.addWidget(self.lock_btn, 0, 0)
        layGrid_LU.addWidget(self.unlock_btn, 0, 1)

        layV_LU.addLayout(layGrid_LU)
        
        self.grp_boxTempDisp.setLayout(layV_tempDisp)
        layH_componentEditing_ancestor.addWidget(self.grp_boxTempDisp)
        
        self.grp_boxUL.setLayout(layV_LU)
        layH_componentEditing_ancestor.addWidget(self.grp_boxUL)

        bottom_Vlayout.addLayout(layH_componentEditing_ancestor)
        
        # ---------------------------------------------------------------------
        self.setLayout(main_Vlayout)

        # add module label style property here
        for tree_widget in style_treeview_ui:
            tree_widget.setProperty("treeComponents_UI_01", True)

        for widget in style_update_mdl_ui:
            widget.setProperty("update_UI", True)

        for wid in [cmo_lbl, self.cmo_rigType_lbl, self.cmo_mirrorMdl_lbl, self.cmo_stretch_lbl, self.cmo_twist_lbl]:
            wid.setEnabled(False)
            wid.setProperty("Current_disabled", True)


    def UI_tab1_connect_signals(self):
        # -- visualise database --
        self.rpl_live_component.clicked.connect(self.sigFunc_rpl_live_component)

        # ------------ choose modules ------------
        self.available_rig_comboBox.currentIndexChanged.connect(self.sigFunc_availableRigComboBox)

        for mdl in self.mdl_choose_ui_dict:
            # unpack the elements of the dict containing the widgets dynamically built.  
            mdl_checkBox, mdl_iteration, mdl_side = self.mdl_choose_ui_dict[mdl]
            # create lambda functions to connect signals to slots with additional `mdl` argument
            mdl_checkBox.stateChanged.connect(lambda _, name=mdl: self.sigFunc_mdl_checkBox(name))
            mdl_iteration.valueChanged.connect(lambda _, name=mdl: self.sigFunc_mdl_IterationSpinBox(name))
            mdl_side.currentIndexChanged.connect(lambda _, name=mdl: self.sigFunc_mdl_SideCombobox(name))
        
        self.publish_btn.clicked.connect(self.sigfunc_publish_btn)
        # -- add blueprints --
        self.add_mdl_btn.clicked.connect(self.sigfunc_add_module)
        self.add_blueprint_btn.clicked.connect(self.sigfunc_add_blueprint)

        # ------------ component editing ------------
        # ---- Template Display ----
        self.guide_template_checkBox.stateChanged.connect(self.sigFunc_guide_template_checkBox)
        self.controls_template_checkBox.stateChanged.connect(self.sigFunc_controls_template_checkBox)
        self.ddj_template_checkBox.stateChanged.connect(self.sigFunc_ddj_template_checkBox)
        # ---- Lock/Unlock ----
        self.compnent_checkBox.stateChanged.connect(self.sigFunc_compnent_checkBox)
        self.lock_btn.clicked.connect(self.sigFunc_lock_btn)
        self.unlock_btn.clicked.connect(self.sigFunc_unlock_btn)
        
    ########## UI SIGNAL FUNCTOINS ##########
    # ------------ siFunc TREEVIEW functions ------------
    def sigFunc_rpl_live_component(self):
        # print selection in ui:
        component_selection = self.get_component_name_TreeSel()
        for component in component_selection:
            self.record_component_change(component)

    
    # ------------ siFunc Choose modules functions ------------
    def sigFunc_availableRigComboBox(self):
        self.val_availableRigComboBox = self.available_rig_comboBox.currentText()
        tree_name = self.val_availableRigComboBox.replace("DB_", "")
        self.tree_view_name_lbl.setText(f"Database: `{tree_name}`")
        self.visualise_active_db()
        print(f"available rig chosen: `{self.val_availableRigComboBox}`")


    # define the 3 widget functions appropriatly, taking the `mdl_name` arg from lambda!
    def sigFunc_mdl_checkBox(self, mdl_name):
        mdl_checkBox = self.mdl_choose_ui_dict[mdl_name][0]
        self.val_mdl_checkBox = mdl_checkBox.isChecked()

        # store the data! 
        # - set `mdl_name` as the keyy
        # - add checkbox & add temp value & string for remaining signals
        if mdl_name == 'spine':
            letter = "M"
        else:
            letter = "L"
        self.user_module_data[mdl_name] = {
            "mdl_checkBox": self.val_mdl_checkBox,
            "mdl_iteration": self.user_module_data.get(mdl_name, {}).get('iteration', 1),
            "mdl_side": self.user_module_data.get(mdl_name, {}).get('side', letter)
        }

        if self.val_mdl_checkBox: # Enable other widgets where neccesary
            self.mdl_choose_ui_dict[mdl_name][1].setEnabled(True)
            if mdl_name == "spine" or mdl_name == "root":
                pass
            else:
                self.mdl_choose_ui_dict[mdl_name][2].setEnabled(True)
        else:
            self.mdl_choose_ui_dict[mdl_name][1].setEnabled(False)             
            self.mdl_choose_ui_dict[mdl_name][2].setEnabled(False)
        print(f"MDL::{mdl_name} &  self.val_mdl_checkBox::{self.val_mdl_checkBox}")
    
    def sigFunc_mdl_IterationSpinBox(self, mdl_name):
        mdl_iteration = self.mdl_choose_ui_dict[mdl_name][1]
        if mdl_name == "root":
            mdl_iteration.setMinimum(1)
            mdl_iteration.setMaximum(1)
        self.val_mdl_iteration = mdl_iteration.value()
        
        # add the remaining iteration widget signal
        self.user_module_data[mdl_name]["mdl_iteration"] = self.val_mdl_iteration

        print(f"MDL::{mdl_name} &  self.val_mdl_checkBox::{self.val_mdl_iteration}")

    def sigFunc_mdl_SideCombobox(self, mdl_name):
        mdl_side = self.mdl_choose_ui_dict[mdl_name][2]
        self.val_mdl_side = mdl_side.currentText()
        self.val_mdl_name = mdl_name

        # add the remaining iteration widget signal
        #if self.val_mdl_side == "None":
        #    self.user_module_data[mdl_name]["mdl_side"] = ""
        #else:
        self.user_module_data[mdl_name]["mdl_side"] = self.val_mdl_side

        print(f"MDL::{self.val_mdl_name} &  self.val_mdl_checkBox::{self.val_mdl_side}")
    
    # -- Publish --
    def sigfunc_publish_btn(self): # cr a new dictionary to store the state of each module!
        print(f"sigfunc_publish_btn clicked")
        for mdl, signals in self.user_module_data.items():
            #print(f"MDL::{mdl} & signals::{signals}")
            print(f"MDL::{mdl} & checkbox::{signals['mdl_checkBox']}, iteration::{signals['mdl_iteration']}, side::{signals['mdl_side']}")
            self.cr_mdl_json_database(mdl, signals['mdl_checkBox'], signals['mdl_iteration'], signals['mdl_side'])
            self.visualise_active_db()
        
    
    # ---- add blueprint ----
    def func_createXfmGuides(self, component_selection):
            for selection in component_selection:
                parts = selection.split('_')
                if "root" in selection:
                    obj_name = f"*_{parts[1]}"
                else:
                    obj_name = f"*_{parts[1]}_*_{parts[2]}_{parts[3]}"
                if cmds.objExists(obj_name):
                    exists = 1
                else:
                    exists = 0
                    mdl_component_dict = self.retrieve_component_dict_from_nameSel(selection)
                    print(f"RETURNED DICT = {mdl_component_dict}")
                    cr_guides.CreateXfmGuides(mdl_component_dict)
            
            if not exists:
                # parent the blueprints to hierarchy rig group properly
                try:
                    cmds.parent("grp_component_misc", "grp_components")
                    cmds.parent("grp_ctrl_components", "grp_controls")
                except Exception as e:
                    print(f"parenting error: `grp_component_misc`, `grp_ctrl_components` to `grp_components` = {e}")
            else:
                print(f"component already exists in the scene: {selection}")
            self.controls_template_checkBox.setChecked(False)
            self.ddj_template_checkBox.setChecked(False)
            self.controls_template_checkBox.setChecked(True)
            self.ddj_template_checkBox.setChecked(True)


    def sigfunc_add_module(self):
        self.load_rig_group()
        print(f"What is mdl_choose_ui_dict? == {self.mdl_choose_ui_dict}") # output = {}
        # select the component(red) in the 
        # this dict comes from gathering data from active databases in active rig folder!
        example_component_dict = {
            "module_name":"bipedArm", 
            "unique_id":0,
            "side":"L", 
            "component_pos":{
                'clavicle': [3.9705319404602006, 230.650634765625, 2.762230157852166], 
                'shoulder': [28.9705319404602, 230.650634765625, 2.762230157852166], 
                'elbow': [53.69795846939088, 197.98831176757807, 6.61050152778626], 
                'wrist': [76.10134363174441, 169.30845642089832, 30.106774568557817]
                },
            "controls":{
                        'FK_ctrls': 
                                {'fk_clavicle': 'circle', 'fk_shoulder': 'circle', 'fk_elbow': 'circle', 'fk_wrist': 'circle'}, 
                        'IK_ctrls': 
                                {'ik_clavicle': 'cube', 'ik_shoulder': 'cube', 'ik_elbow': 'pv', 'ik_wrist': 'cube'}
                        }
            }
        component_selection = self.get_component_name_TreeSel()
        print(f"YAAAAAH component_selection = {component_selection[0]}")
        self.func_createXfmGuides(component_selection)

        self.func_unlocked_all()
        
        
    def sigfunc_add_blueprint(self):
        self.load_rig_group()
        # connect signals for module editor buttons
        for mdl, (checkBox, iterations, side) in self.mdl_choose_ui_dict.items():
            if checkBox.isChecked(): # checkbox is the master 
                # access the input from iterations and side
                iterations_value = iterations.value()
                side_value = side.currentText() if side else None
                print(f"Adding blueprint for {mdl}: Iterations={iterations_value}, Side={side_value}")
        
        component_selection = self.get_all_component_name_in_TreeView()
        self.func_createXfmGuides(component_selection)

        self.func_unlocked_all()


    # ---- Template Components! ----
    def sigFunc_guide_template_checkBox(self):
        self.val_guide_template_checkBox = self.guide_template_checkBox.isChecked()
        utils.select_set_displayType("xfm_guide_*", self.val_guide_template_checkBox, False)


    def sigFunc_controls_template_checkBox(self):
        self.val_controls_template_checkBox = self.controls_template_checkBox.isChecked()
        utils.select_set_displayType("ctrl_*", self.val_controls_template_checkBox, False)


    def sigFunc_ddj_template_checkBox(self):
        self.val_ddj_template_checkBox = self.ddj_template_checkBox.isChecked()
        utils.select_set_displayType("ddj_*", self.val_ddj_template_checkBox, False)
    
    # --- Unlocked component configuration ---
    def sigFunc_compnent_checkBox(self):
        self.val_compnent_checkBox = self.compnent_checkBox.isChecked()

    def sigFunc_lock_btn(self):
        if self.val_compnent_checkBox: #true
            component_selection = self.get_component_name_TreeSel()
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

    def sigFunc_unlock_btn(self):
        if self.val_compnent_checkBox: #true
            component_selection = self.get_component_name_TreeSel()
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
                self.constrain_guides_from_comp(unlock_rdy_component) 
        else: print(f"component checkbox is not checked")


    def func_unlocked_all(self):
        # establish components present in the scene!
        possible_comp_groups = "xfm_grp_*_component_*"
        cmds.select(possible_comp_groups)
        xfm_ancestorGrp = cmds.ls(sl=1, type="transform")
        # xfm_ancestorGrp = ['xfm_grp_bipedArm_component_0_L', 'xfm_grp_bipedLeg_component_0_L', 'xfm_grp_root_component_0_M', 'xfm_grp_spine_component_0_M'] 
        print(f"xfm_ancestorGrp = {xfm_ancestorGrp}")
        for component in xfm_ancestorGrp:
            self.constrain_guides_from_comp(component)
    
    
    def constrain_guides_from_comp(self, component):
        # guide > parentOperation > guideGROUP(constrained)
        print(f"NNNNNNNNNORMAL UNLOCK component = {component}")
        spine_output_mdl = "spine"
        parts = component.split('_')[2:]
        print(f"PARTS == {parts}")
        working_comp_unique_id = parts[2]
        working_comp_side =  parts[3]
        grpXfm = "offset_xfm_guide"
        xfm = "xfm_guide"
        if "bipedLeg" in component:
            print("bipedLeg unlocked configuration")
            if cmds.objExists("xfm_grp_spine_component_*_M"):
                cmds.select("xfm_grp_spine_component_*_M")
                leg_output_comp = cmds.ls(sl=1, type="transform")[0] # handles only 1 spine for time being
                print(f"output_comp = {leg_output_comp}") # xfm_grp_spine_component_0_M
                leg_spine_input_name = f"offset_xfm_guide_bipedLeg_hip_{working_comp_unique_id}_{working_comp_side}"
                leg_output_mdl = "spine"
                leg_output_uID = leg_output_comp.split('_')[4:][0]
                leg_output_side = leg_output_comp.split('_')[4:][-1]
                leg_spine_output_name =f"xfm_guide_{spine_output_mdl}_0_{leg_output_uID}_{leg_output_side}"
                # spine1 >PointConAll> hip 
                utils.constrain_2_items(leg_spine_output_name, leg_spine_input_name, "point", "all")
            else: print("spine component not in scene")
            # Hip >PointConAll> knee
            utils.constrain_2_items(
                f"{xfm}_bipedLeg_hip_{working_comp_unique_id}_{working_comp_side}", 
                f"{grpXfm}_bipedLeg_knee_{working_comp_unique_id}_{working_comp_side}", 
                "point", "all")
            # knee > Nothing
            # foot >PointConX_Z> ankle
            utils.constrain_2_items(
                f"{xfm}_bipedLeg_foot_{working_comp_unique_id}_{working_comp_side}", 
                f"{grpXfm}_bipedLeg_ankle_{working_comp_unique_id}_{working_comp_side}", 
                "point", ["X", "Z"])
            # foot >ParentConAll> ball
            utils.constrain_2_items(
                f"{xfm}_bipedLeg_foot_{working_comp_unique_id}_{working_comp_side}", 
                f"{grpXfm}_bipedLeg_ball_{working_comp_unique_id}_{working_comp_side}", 
                "parent", "all")
            # foot >ParentConAll> toe
            utils.constrain_2_items(
                f"{xfm}_bipedLeg_foot_{working_comp_unique_id}_{working_comp_side}", 
                f"{grpXfm}_bipedLeg_toe_{working_comp_unique_id}_{working_comp_side}", 
                "parent", "all")
            if cmds.objExists("xfm_grp_root_component_*_M"):
                # root >ParentCon_Y_> ankle
                # offset_xfm_guide_root
                utils.constrain_2_items(
                f"{xfm}_root",
                f"{grpXfm}_bipedLeg_ankle_{working_comp_unique_id}_{working_comp_side}", 
                "parent", ["Y"])
                # root >PointtConAll> foot
                utils.constrain_2_items(
                f"{xfm}_root",
                f"{grpXfm}_bipedLeg_foot_{working_comp_unique_id}_{working_comp_side}", 
                "point", "all")
        elif "bipedArm" in component:
            print("bipedArm unlocked configuration")
            if cmds.objExists("xfm_grp_spine_component_*_M"):
                print("Arm, spine IS component in scene")
                cmds.select("xfm_grp_spine_component_*_M")
                arm_output_comp = cmds.ls(sl=1, type="transform")[0] # handles only 1 spine for time being
                print(f"output_comp = {arm_output_comp}") # xfm_grp_spine_component_0_M
                arm_output_uID = arm_output_comp.split('_')[4:][0]
                arm_output_side = arm_output_comp.split('_')[4:][-1]
                arm_spine_output_name =f"xfm_guide_{spine_output_mdl}_3_{arm_output_uID}_{arm_output_side}"
                # spine4 >ParentConAll> clavicle
                clavicle_input_name = f"offset_xfm_guide_bipedArm_clavicle_{working_comp_unique_id}_{working_comp_side}"
                utils.constrain_2_items(arm_spine_output_name, clavicle_input_name, 
                                        "parent", "all")
                # spine4 >ParentConAll> shoulder
                shoulder_input_name = f"offset_xfm_guide_bipedArm_shoulder_{working_comp_unique_id}_{working_comp_side}"
                utils.constrain_2_items(arm_spine_output_name, shoulder_input_name, 
                                        "parent", "all")
                if cmds.objExists("xfm_grp_root_component_*_M"):
                    # root >ParentCon_Y_> ankle
                    utils.constrain_2_items(
                    f"{xfm}_root",
                    f"{grpXfm}_bipedArm_elbow_{working_comp_unique_id}_{working_comp_side}", 
                    "point", "all")
                    # root >PointtConAll> foot
                    utils.constrain_2_items(
                    f"{xfm}_root",
                    f"{grpXfm}_bipedArm_wrist_{working_comp_unique_id}_{working_comp_side}", 
                    "point", "all")
        elif "root" in component:
            print("root unlocked configuration")
            # root >PointtConAll> COG
            utils.constrain_2_items(
                f"{xfm}_root",
                f"{grpXfm}_COG", 
                "parent", "all")
        elif "spine" in component:
            print("spine unlocked configuration")
            if cmds.objExists("xfm_grp_root_component_*_M"):
                # cog >ParentConAll> spine1
                utils.constrain_2_items(
                f"{xfm}_COG",
                f"{grpXfm}_{spine_output_mdl}_0_{working_comp_unique_id}_{working_comp_side}", 
                "parent", "all")
            # spine0 > ParentConAll> spine1/2/3/4
            utils.constrain_2_items(
                f"{xfm}_{spine_output_mdl}_0_{working_comp_unique_id}_{working_comp_side}",
                f"{grpXfm}_{spine_output_mdl}_1_{working_comp_unique_id}_{working_comp_side}", 
                "parent", "all")
            utils.constrain_2_items(
                f"{xfm}_{spine_output_mdl}_0_{working_comp_unique_id}_{working_comp_side}",
                f"{grpXfm}_{spine_output_mdl}_2_{working_comp_unique_id}_{working_comp_side}", 
                "parent", "all")
            utils.constrain_2_items(
                f"{xfm}_{spine_output_mdl}_0_{working_comp_unique_id}_{working_comp_side}",
                f"{grpXfm}_{spine_output_mdl}_3_{working_comp_unique_id}_{working_comp_side}", 
                "parent", "all")
            utils.constrain_2_items(
                f"{xfm}_{spine_output_mdl}_0_{working_comp_unique_id}_{working_comp_side}",
                f"{grpXfm}_{spine_output_mdl}_4_{working_comp_unique_id}_{working_comp_side}", 
                "parent", "all")
            

    # -------------------------------------------------------------------------
    def load_rig_group(self):
        # rig_syntax "jmvs_char*_rig" - DB_jmvs_cyborg_rig
        rig_name = self.val_availableRigComboBox.replace("DB_", "")
        if not cmds.objExists(rig_name):
            try:
                utils.create_rig_group(rig_name)
            except Exception as e:
                print(e)
        else:
            print(f"rig_group `{rig_name}` already exists in the scene")
        

    # ---- TreeView functions ----
    def record_component_change(self, component_selection):
        split_names = component_selection.split('_')[1:] #ignore 'mdl' prefix
        module = split_names[0]
        unique_id = split_names[1]
        try: # handle if it has no side
            side = split_names[2]
        except Exception:
            side = "" #use M to represent middle (but doesn't show up in scene)
            # Or whatever it needs to be in the database! 
        print(f"split_names: module = {module}, unique_id = {unique_id}, side = {side}")

        print(f"xfm_guide_{module}_*_{unique_id}_{side}")
        #xfm_guide_bipedArm_*       _0_L
        #xfm_guide_bipedArm_clavicle_0_L
        try:
            cmds.select(f"xfm_guide_{module}_*_{unique_id}_{side}")
            guides = cmds.ls(sl=1, type="transform")
            # gather the positions of the selected
            new_component_pos_dict = utils.get_selection_trans_dict(guides, side)
            print("new_component_pos: ", new_component_pos_dict)
            ''' got this dict `B` from selection in treeView '''
            ''' if ^ = {} cancel the operation below. '''
            ''' get this dict `A` from the correct row in the right db '''
            ''' compare `B` to `A`, find the same name 'clavicle', ect, and put the new values in it.
            '''
            rig_folder_name = self.val_availableRigComboBox
            print(f"rig_folder_name = {rig_folder_name}")
            rig_db_directory = os_custom_directory_utils.create_directory(
                "Jmvs_tool_box", "databases", "char_databases", 
                self.db_rig_location, rig_folder_name
                )
            retrieved_exisiting_dict = database_schema_002.retrieveSpecificPlacementPOSData(
                rig_db_directory, module, unique_id, side
                )
            existing_pos_dict = retrieved_exisiting_dict.return_existing_pos_dict()
            print(f"existing_pos_dict = {existing_pos_dict}")

            updated_existing_pos_dict = {}
            for key in existing_pos_dict.keys():
                for new_key, new_value in new_component_pos_dict.items():
                    if key in new_key:
                        updated_existing_pos_dict[key] = new_value
                        break
            print(f"Updated `existing_dict` : {updated_existing_pos_dict}")
            ''' with new dict, update the database! '''
            database_schema_002.updateSpecificPlacementPOSData(
                rig_db_directory, module, unique_id, side, updated_existing_pos_dict
                )

        except Exception as e:
            print(f"No component exists in the scene of '{component_selection}'")
            print(f"error: {e}")
        

    def visualise_active_db(self):
        # get directory of current chosen rig folder!
        rig_folder_name = self.val_availableRigComboBox
        rig_db_directory = os_custom_directory_utils.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", 
            self.db_rig_location, rig_folder_name
            )
        # gather a list of database found in the folder: 
        db_names = []
        db_data = {}
        if os.path.exists(rig_db_directory):
            for db in os.listdir(rig_db_directory):
                if db.startswith("DB_") and db.endswith(".db"):
                    db_names.append(db)
                    
                    # get the table data `modules` from each database
                    # query the unique_id & side from each row
                    # store into a dictionary to pass to pop `populate_tree_views()`
                    data_retriever = database_schema_002.retrieveModulesData(
                        rig_db_directory, db)
                    db_data[db] = data_retriever.mdl_populate_tree_dict.get(db, [])
                else:
                    print(f"NO database file found in:{rig_db_directory}")
        else:
            print(f"directory does NOT exist: {rig_db_directory}")
        print(f"rig_folder_name: {rig_folder_name} & in that, {db_names}")
        
        # clear the modules everytime the active db is switched
        self.mdl_tree_model.clear()
        
        # add all databases to the treeView
        self.populate_tree_views(rig_folder_name, db_data)


    def populate_tree_views(self, rig_folder_name, db_data_dict):
        print(f"Populating Tree with `{rig_folder_name}'s` databases: {list(db_data_dict.keys())}")
        tree_parent_item = self.mdl_tree_model.invisibleRootItem()

        if not db_data_dict:
            print(f"NO databases in the folder `{rig_folder_name}`")
        else:
            print(f"found databases '{list(db_data_dict.keys())}' in the folder `{rig_folder_name}`")
            try:
                for db_name, rows in db_data_dict.items():
                    db_base_name = db_name.replace("DB_", "").replace(".db", "")
                    db_item = QtGui.QStandardItem(f"{db_base_name}") # Orange
                    db_item.setData(True, QtCore.Qt.UserRole)

                    for unique_id, side in rows:
                        if "root" in db_base_name:
                            item_name = f"mdl_{db_base_name}_{unique_id}"
                        else:
                            item_name = f"mdl_{db_base_name}_{unique_id}_{side}"
                        mdl_item = QtGui.QStandardItem(item_name)
                        mdl_item.setData(False, QtCore.Qt.UserRole)
                        db_item.appendRow(mdl_item)
                        
                    tree_parent_item.appendRow(db_item)
            except Exception as e:
                    print(f"If you just created a new db, ignore this error, if not: {e}")
    
    # ---- Choose modules functions ----

    # -- DB Rig folder functions --
    def get_available_DB_rig_folders(self, location):
            name_of_rig_fld = []
            self.rig_db_storage_dir = os_custom_directory_utils.create_directory("Jmvs_tool_box", "databases", "char_databases", location)
            if os.path.exists(self.rig_db_storage_dir):
                print(f"Dir does exist: {self.rig_db_storage_dir}")
                for db_rig_folder in os.listdir(self.rig_db_storage_dir):
                    if db_rig_folder.startswith("DB_jmvs_"):
                        name_of_rig_fld.append(db_rig_folder)
                        print(f"RIG Folder(s): {db_rig_folder}")
                    elif not db_rig_folder.startswith("DB_jmvs_"):
                        print(f"NOT a rig folder: {db_rig_folder}")
            else:
                print(f"Dir doesn't exist: {self.rig_db_storage_dir}")
            return name_of_rig_fld


    def populate_available_rig(self, name_of_rig_fld):
        # `name_of_rig_fld` will populate the ComboBox
        # IF no(None) ^folder^ in `self.db_rig_location`, print(f"No rig name folder found in {self.db_rig_location}, please create one.")
        print(f"`self.name_of_rig_fld` :: {name_of_rig_fld}")
        if name_of_rig_fld:
            print(f"Rig folder name found in {self.db_rig_location}, populating available rig option.")
            self.available_rig_comboBox.addItems(name_of_rig_fld)
        elif name_of_rig_fld == None:
            self.available_rig_comboBox.setPlaceholderText("No rig database folders")
            print(f"No rig folder name 'DB_jmvs_char*_rig' found in {self.db_rig_location}, please create one.")

    # -- mdl JSON functions --
    def get_modules_json_dict(self):
        # derive the `self.json_all_mdl_list` from the config folder!
        # self.json_all_mdl_list = ['biped_arm.json', 'biped_leg.json']
        json_mdl_list = []
        json_config_dir = os_custom_directory_utils.create_directory("Jmvs_tool_box", "config", "char_config")
        if os.path.exists(json_config_dir):
            for mdl_config_file in os.listdir(json_config_dir):
                if mdl_config_file.endswith('.json'):
                    json_mdl_list.append(mdl_config_file)
        
        # This dictionary contains nested dict of all possible json modules in `char_config` folder
        json_dict = {}
        for json_file in json_mdl_list:
            # configer the json file
            json_path = os.path.join(json_config_dir, json_file)
            with open(json_path, 'r') as file:
                # load the json data
                json_data = json.load(file)
                json_dict[json_file] = json_data
        return json_dict        

    
    # ---- json data functions ----  
    def cr_mdl_json_database(self, mdl_name, checkBox, iterations, side): # handles a single module at a time
            print(f"OIIIIIIIIIIIIIII self.json_data  == {self.json_dict}, `mdl_name` = {mdl_name}")
                        
            placement_dict = {}
            user_settings_dict = {}
            controls_dict = {}
            for key, values in self.json_dict.items():
                if key == f"{mdl_name}.json":
                    placement_dict =  values['placement']
                    user_settings_dict =  values['user_settings']
                    controls_dict =  values['controls']
            '''
            {'bipedArm.json': 
                {
                'mdl_name': 'bipedArm', 
                'names': ['clavicle', 'shoulder', 'elbow', 'wrist'], 
                'placement': {
                            'component_pos': {'clavicle': [3.9705319404602006, 230.650634765625, 2.762230157852166], 
                                            'shoulder': [25.234529495239258, 225.57975769042972, -12.279715538024915], 
                                            'elbow': [49.96195602416994, 192.91743469238278, -8.43144416809082], 
                                            'wrist': [72.36534118652347, 164.23757934570304, 15.064828872680739]}, 
                            'system_rot_xyz': {'clavicle': [-7.698626118758961, 34.531672095102785, -13.412947865931349], 
                                            'shoulder': [7.042431639335459, -5.366417614476926, -52.87199475566795], 
                                            'elbow': [3.4123575630188263, -32.847391136978814, -52.004681579832734], 
                                            'wrist': [3.4123575630188263, -32.847391136978814, -52.004681579832734]}, 
                            'system_rot_yzx': {'clavicle': [-101.01687892466634, -54.72478122395497, 0.0], 
                                            'shoulder': [38.44191942754821, -81.34821938773749, 179.00497225409262], 
                                            'elbow': [84.72265733457102, -56.99499092973047, 134.2807120402011], 
                                            'wrist': [84.72265733457102, -56.99499092973047, 134.2807120402011]}
                            }, 
                'constant': {
                            'space_swap': 
                                        [['world', 'COG', 'shoulder', 'custom'], ['world', 'wrist'], ['world', 'clavicle'], ['world', 'spine']], 
                            'ik_settings': 
                                        {'start_joint': 'shoulder', 'end_joint': 'wrist', 'pv_joint': 'elbow', 'top_joint': 'clavicle'}
                            }, 
                'user_settings': {
                                'mirror_rig': False, 'stretch': False, 
                                'rig_type': {'options': ['FK', 'IK', 'IKFK'], 'default': 'FK'}, 
                                'size': 1, 'side': ['L', 'R']
                                }, 
                'controls': {
                            'FK_ctrls': 
                                    {'fk_clavicle': 'circle', 'fk_shoulder': 'circle', 'fk_elbow': 'circle', 'fk_wrist': 'circle'}, 
                            'IK_ctrls': 
                                    {'ik_clavicle': 'cube', 'ik_shoulder': 'cube', 'ik_elbow': 'pv', 'ik_wrist': 'cube'}
                            }
                },
            'bipedLeg.json': {'mdl_name': 'bipedLeg', 'names': ['hip', 'knee', 'ankle', 'ball', 'toe'], 'placement': {'component_pos': {'hip': [16.036325454711914, 147.7965545654297, 0.051486290991306305], 'knee': [20.133201599121104, 82.05242919921866, -0.4505884051322898], 'ankle': [24.197132110595703, 12.625909805297809, -3.493209123611452], 'ball': [24.084232330322262, -1.2434497875801753e-14, 17.988098144531257], 'toe': [24.084232330322276, -1.1379786002407858e-14, 29.18881988525391]}, 'system_rot_xyz': {'hip': [-0.206856730062026, 0.4367008200374581, -86.43419733389054], 'knee': [-0.20685673006202596, 0.43670082003745814, -86.43419733389054], 'ankle': [0.5942622188475634, -59.55357811140123, -90.0], 'ball': [-89.85408725528224, -89.99999999999997, 0.0], 'toe': [-89.85408725528225, -89.99999999999997, 0.0]}, 'system_rot_yzx': {'hip': [-0.43670082003745525, 0.0, -176.43419733389047], 'knee': [-2.5051019515754724, 0.0035324430433216728, -176.434], 'ankle': [59.55357811140115, 0.0, 180.0], 'ball': [89.99999999999993, 1.8636062586700292e-16, -180.0], 'toe': [89.99999999999996, -1.2424041724466862e-17, -180.0]}}, 'constant': {'space_swap': [['world', 'COG', 'hip', 'custom'], ['world', 'ankle'], ['world', 'spine_0']], 'ik_settings': {'start_joint': 'hip', 'end_joint': 'ankle', 'pv_joint': 'knee'}}, 'user_settings': {'mirror_rig': False, 'stretch': False, 'rig_type': {'options': ['FK', 'IK', 'IKFK'], 'default': 'FK'}, 'size': 1, 'side': ['L', 'R']}, 'controls': {'FK_ctrls': {'fk_hip': 'circle', 'fk_knee': 'circle', 'fk_ankle': 'circle', 'fk_ball': 'circle', 'fk_toe': 'circle'}, 'IK_ctrls': {'ik_hip': 'cube', 'ik_knee': 'pv', 'ik_ankle': 'cube', 'ik_ball': 'None', 'ik_toe': 'None'}}}, 
            }
            'finger.json': {'mdl_name': 'Finger', 'names': ['bipedPhalProximal', 'bipedPhalMiddle', 'bipedPhalDistal', 'bipedPhalDEnd'], 'placement': {'component_pos': {'bipedPhalProximal': [80.61004637463462, 151.7215423583185, 24.099996037467385], 'bipedPhalMiddle': [84.45979996338392, 145.8773481500665, 28.318845156262494], 'bipedPhalDistal': [87.13240797932576, 141.82014294780598, 31.24768974670393], 'bipedPhalDEnd': [89.18559525612636, 138.70326159035977, 33.49772656951928]}, 'system_rot_xyz': {'bipedPhalProximal': [5.910977623767589, -31.083474503917564, -56.62585344811804], 'bipedPhalMiddle': [5.910977623767589, -31.083474503917564, -56.62585344811804], 'bipedPhalDistal': [5.910977623767589, -31.08347450391755, -56.62585344811804], 'bipedPhalDEnd': [5.910977623767589, -31.08347450391755, -56.62585344811804]}, 'system_rot_yzx': {'bipedPhalProximal': [50.95891725101831, -56.98582204849474, 153.9365525662274], 'bipedPhalMiddle': [50.95891725101831, -56.98582204849474, 153.9365525662274], 'bipedPhalDistal': [50.95891725101831, -56.98582204849474, 153.9365525662274], 'bipedPhalDEnd': [50.95891725101831, -56.98582204849474, 153.9365525662274]}}, 'constant': {'space_swap': [['world', 'COG', 'wrist', 'custom'], ['world', 'bipedPhalDEnd'], ['world', 'bipedPhalProximal'], ['world', 'wirst']], 'ik_settings': {'start_joint': 'bipedPhalProximal', 'end_joint': 'bipedPhalDistal', 'pv_joint': 'bipedPhalMiddle', 'world_orientation': False, 'last_joint': 'bipedPhalDEnd'}}, 'user_settings': {'mirror_rig': False, 'stretch': True, 'rig_type': {'options': ['FK', 'IK', 'IKFK'], 'default': 'FK'}, 'size': 0.15, 'side': ['L', 'R']}, 'controls': {'FK_ctrls': {'fk_bipedPhalProximal': 'circle', 'fk_bipedPhalMiddle': 'circle', 'fk_bipedPhalDistal': 'circle', 'fk_bipedPhalDEnd': 'circle'}, 'IK_ctrls': {'ik_bipedPhalProximal': 'cube', 'ik_bipedPhalMiddle': 'pv', 'ik_bipedPhalDistal': 'cube', 'ik_bipedPhalDEnd': 'cube'}}}, 
            
            'root.json': {'mdl_name': 'root', 'names': ['root', 'COG'], 'placement': {'component_pos': {'root': [0, 0, 0], 'COG': [0, 150, 0]}, 'system_rot_xyz': {'root': [0, 0, 0], 'COG': [0, 0, 0]}, 'system_rot_yzx': {'root': [0, 0, 0], 'COG': [0, 0, 0]}}, 'constant': {'space_swap': [], 'ik_settings': {}}, 'user_settings': {'mirror_rig': False, 'stretch': False, 'rig_type': {'options': ['FK'], 'default': 'FK'}, 'size': 1, 'side': ['None']}, 'controls': {'FK_ctrls': {'fk_root': 'circle', 'fk_COG': 'circle'}, 'IK_ctrls': {}}}, 
            
            'spine.json': {'mdl_name': 'spine', 'names': ['spine_1', 'spine_2', 'spine_3', 'spine_4', 'spine_5'], 'placement': {'component_pos': {'spine_1': [0.0, 150.0, 0.0], 'spine_2': [-1.0302985026792348e-14, 165.3182830810547, 2.138536453247061], 'spine_3': [-2.3043808310802754e-14, 185.50926208496094, 2.8292100429534632], 'spine_4': [-3.3364796818449844e-14, 204.27308654785156, -0.3802546262741595], 'spine_5': [-5.1020985278054485e-14, 237.46397399902344, -8.25034904479989]}, 'system_rot_xyz': {'spine_1': [0.0, -7.947513469078512, 90.00000000000001], 'spine_2': [-1.9890093469260345e-16, -1.959155005957633, 90.00000000000001], 'spine_3': [0.0, 9.706246313394262, 90.00000000000001], 'spine_4': [-8.171859705486283e-16, 13.339396285991443, 90.0], 'spine_5': [-7.814945266275812e-14, -9.271752801444176, 89.99999999999991]}, 'system_rot_yzx': {'spine_1': [7.667038985618099, 0.0, 0.0], 'spine_2': [1.880673240761548, 0.0, 0.0], 'spine_3': [-9.496334372767544, 0.0, 0.0], 'spine_4': [-13.212290179161894, 0.0, 0.0], 'spine_5': [9.331941466846782, 0.0, 0.0]}}, 'constant': {'space_swap': [], 'ik_settings': {'start_joint': 'spine_1', 'end_joint': 'spine_5', 'pv_joint': None, 'world_orientation': True}}, 'user_settings': {'mirror_rig': False, 'stretch': False, 'rig_type': {'options': ['FK', 'IK', 'IKFK'], 'default': 'FK'}, 'size': 1, 'side': ['None']}, 'controls': {'FK_ctrls': {'fk_spine_1': 'circle', 'fk_spine_2': 'circle', 'fk_spine_3': 'circle', 'fk_spine_4': 'circle', 'fk_spine_5': 'circle'}, 'IK_ctrls': {'ik_spine_1': 'cube', 'ik_spine_2': None, 'ik_spine_3': 'cube', 'ik_spine_4': None, 'ik_spine_5': 'cube'}}}}
            '''
            
            print(f"placement_dict >> {placement_dict}")
            print(f"user_settings_dict >> {user_settings_dict}")
            print(f"controls_dict >> {controls_dict}")
            mdl_directory = os.path.join(self.rig_db_storage_dir, self.val_availableRigComboBox)
            # update to need a directory!
            if checkBox:
                for db in range(iterations):
                    database_schema = database_schema_002.CreateDatabase(
                        mdl_directory, mdl_name, side, 
                        placement_dict, user_settings_dict, controls_dict)
                
                # unique_id = database_schema.get_unique_id()
                # print(f"unique_id == {unique_id} for {mdl_name}_{side}")
                # import and call the database maker 'database_schema'
            else:
                print(f"Not required module database creation for {mdl_name}")
            
    # -- gather data from treeView --
    def get_component_name_TreeSel(self):
        # get selection model of all items in the treeView
        selection_model = self.mdl_tree_view.selectionModel()
        selected_indexes = selection_model.selectedIndexes()

        # is there an item to be selected?
        if selected_indexes:
            multi_selection = selected_indexes
            module_item = []
            module_selection_list = []
            for index in multi_selection:
                item = self.mdl_tree_model.itemFromIndex(index)
                name = item.text()
                print(f"Name in for loop = {name}")
                module_item.append(item)
                module_selection_list.append(name)
            print(f"treeview selection list: {module_selection_list}")
            return module_selection_list
        

    def get_all_component_name_in_TreeView(self):
        # get selection model of all items in the treeView
        module_item_list = []
        def go_thru_items(parent_item):
            # collect items by goiun thru the tree 
            for row in range(parent_item.rowCount()):
                child_item = parent_item.child(row)
                # check it's the right item
                if child_item.text().startswith("mdl_"):
                    module_item_list.append(child_item.text())
                go_thru_items(child_item)
        root_item = self.mdl_tree_model.invisibleRootItem()
        go_thru_items(root_item)
        print(f"All items with 'mdl' in treeView = {module_item_list}")
        return module_item_list
        

    def retrieve_component_dict_from_nameSel(self, module_selection_name):
        # mdl_spine_0 : mdl_MODULE*_uniqueID*_side*
        # split the name 
        split_names = module_selection_name.split('_')[1:] #ignore 'mdl' prefix
        module = split_names[0]
        unique_id = split_names[1]
        try: # handle if it has no side
            side = split_names[2]
        except Exception:
            side = "L" #use M to represent middle (but doesn't show up in scene)
            # Or whatever it needs to be in the database! 
        print(f"split_names: module = {module}, unique_id = {unique_id}, side = {side}")
        
        # gather dict from database!
        rig_folder_name = self.val_availableRigComboBox
        print(f"rig_folder_name = {rig_folder_name}")
        rig_db_directory = os_custom_directory_utils.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", 
            self.db_rig_location, rig_folder_name
            )
        print(f"rig_db_directory = {rig_db_directory}")
        retrieve_mdl_component_dict = database_schema_002.retrieveSpecificComponentdata(rig_db_directory, module, unique_id, side)
        mdl_component_dict = retrieve_mdl_component_dict.return_mdl_component_dict()
        print(f"mdl_component_dict = {mdl_component_dict}")
        return mdl_component_dict


def char_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    ui = CharRigging()
    ui.show()
    app.exec()
    return ui
            