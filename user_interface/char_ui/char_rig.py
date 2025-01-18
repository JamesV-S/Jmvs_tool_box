
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

importlib.reload(database_schema_002)
importlib.reload(os_custom_directory_utils)
importlib.reload(utils)

# For the time being, use this file to simply call the 'modular_char_ui.py'
maya_main_wndwPtr = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndwPtr), QWidget)

def delete_existing_ui(ui_name):
    if cmds.window(ui_name, exists=True):
        cmds.deleteUI(ui_name, window=True)

class CharRigging(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CharRigging, self).__init__(parent)
        version = "001"
        ui_object_name = f"JmvsCharRig_{version}"
        ui_window_name = f"Jmvs_character_tool_{version}"
        delete_existing_ui(ui_object_name)
        self.setObjectName(ui_object_name)
        
        self.setStyleSheet("""
            QHBoxLayout {
                background-color:#4f7b7f;
                color: #333;
                font-size: 12px;
            }
            QVBoxLayout {
                background-color: #ccc;
                border: 1px solid #888;
                border-radius: 5px;
                padding: 10px;
            }
        """)

        # set flags & dimensions
        # ---------------------------------- 
        self.setParent(main_window) 
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(ui_window_name)
        self.resize(400, 550)
        
        # style
        stylesheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                       "..", "CSS", "char_style_sheet_001.css")
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
        
        self.UI_modules()
        self.UI_tab1_connect_signals()

        # -- paramaters --
        # What's the syntax for rig database folders?
        self.db_rig_location = "db_rig_storage"
        self.name_of_DB_mdl_file = None # `DB_mdl_bipedArm.db`
        name_of_rig_fld = self.get_available_DB_rig_folders(self.db_rig_location)
        self.populate_available_rig(name_of_rig_fld)
        # ui connections:
        

    def UI_modules(self):
        main_Vlayout = QtWidgets.QVBoxLayout(self)
        main_Vlayout.setObjectName("main_Layout")
        
        top_Hlayout = QtWidgets.QHBoxLayout() # db_vis & mdl_choose
        bottom_Vlayout = QtWidgets.QVBoxLayout() # add_blueprint & updating db

        main_Vlayout.addLayout(top_Hlayout)
        main_Vlayout.addLayout(bottom_Vlayout)

        #----------------------------------------------------------------------
        # ---- database editor ----
        layV_module_Tree = QtWidgets.QVBoxLayout()
        
        self.tree_view_name_lbl = QtWidgets.QLabel("Database: `Rig Name`")
        
        self.mdl_tree_model = QtGui.QStandardItemModel()
        self.mdl_tree_model.setColumnCount(1)

        self.mdl_tree_view = QtWidgets.QTreeView(self)
        self.mdl_tree_view.setModel(self.mdl_tree_model)
        self.mdl_tree_view.setObjectName("mdl_treeview")

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
        available_rig_lbl.setFixedSize(200,20)
        self.available_rig_comboBox = QtWidgets.QComboBox()
        self.available_rig_comboBox.setFixedSize(200,30)
        # searches the necessary folder that stores database!
        #self.available_rig_comboBox.addItems(["Male_rig", "Female_rig"])

        layV_available_rig.addWidget(available_rig_lbl)
        layV_available_rig.addWidget(self.available_rig_comboBox)
        layV_choose_mdl_ancestor.addLayout(layV_available_rig)

        # -- Add module editor --
        layV_add_mdl_layout = QtWidgets.QVBoxLayout()

        def module_choose_ui(mdl_name, side_items):
            mdl_h_layout = QtWidgets.QHBoxLayout()
            
            mdl_checkBox = QtWidgets.QCheckBox()
            mdl_name_label = QtWidgets.QLabel(mdl_name)
            mdl_iterations = QtWidgets.QSpinBox()
            mdl_iterations.setMinimum(1)
            mdl_iterations.setDisabled(False)
            
            mdl_h_layout.addWidget(mdl_checkBox)
            mdl_h_layout.addWidget(mdl_name_label)
            mdl_h_layout.addWidget(mdl_iterations)
            
            mdl_side = None
            if side_items != "None":
                mdl_side = QtWidgets.QComboBox()
                mdl_side.addItems(side_items)
                mdl_side.setDisabled(False) 
                mdl_h_layout.addWidget(mdl_side)
            
            layV_add_mdl_layout.addLayout(mdl_h_layout)

            return mdl_checkBox, mdl_iterations, mdl_side
        
        ''' method of unpacking nested dict struture 'self.json_dict' 
        containing each json files's content under its filename as a key.
        Step 1 - dictionary & items
            `.items()` method that returns a view object that displays a list
            of the dict's key-value tuple pairs(step 2)
            
        Step 2 - unpacking, using 'filename' + 'data' is tuple unpacking
        for each itemreturned by step 1, is a tuple containing a key(filename) 
        and its corresponding value(data).
        
        Step 3 - Loop execution
        thru each iteratipon, filename(key), and data(value) which is the 
        associated dictionary.  '''

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
                    side_list.append(mdl_side)
            print(mdl_list)
            print(side_list)
        except KeyError as e:
            print(f"{e} is not a key in {self.json_data}")
        
        # Create the ui components & store it in a dict
        ''' Signal Functions are handled here! '''
        self.mdl_choose_ui_dict = {}
        for mdl, sides in zip(mdl_list, side_list):
            mdl_choose_buttons = module_choose_ui(mdl, sides)
            self.mdl_choose_ui_dict[mdl] = mdl_choose_buttons
        print(f"self.mdl_choose_ui_dict = {self.mdl_choose_ui_dict}")
        
        layV_choose_mdl_ancestor.addLayout(layV_add_mdl_layout)

        # -- Pusblish module additions --
        layH_publish_mdl_additons = QtWidgets.QHBoxLayout()

        # self.publish_lbl = QtWidgets.QLabel("Publish:")
        self.publish_btn = QtWidgets.QPushButton("Publish Module Additions")
        layH_publish_mdl_additons.addWidget(self.publish_btn)

        layV_choose_mdl_ancestor.addLayout(layH_publish_mdl_additons)

        top_Hlayout.addLayout(layV_choose_mdl_ancestor)

        #----------------------------------------------------------------------
        # -- Selected mdl operations --
        # self.layGRP_mdl_operations = QtWidgets.QGroupBox("GroupBoxTitle_001", self)
        #font = QtGui.QFont("Times New Roman",  12)
        #font.setBold(True)
        #self.layGRP_mdl_operations.setFont(font)
        layV_mdl_operations_ancestor = QtWidgets.QVBoxLayout()
        mdl_data_lbl = QtWidgets.QLabel("Module Data")

        # -- current_mdl_operations --
        layV_current_MO_parent = QtWidgets.QVBoxLayout()
        cmo_lbl = QtWidgets.QLabel("Current")
        
        layH_current_mdl_operations = QtWidgets.QHBoxLayout()
        self.cmo_rigType_lbl = QtWidgets.QLabel("Rig Type: _ _ _")
        self.cmo_mirrorMdl_lbl = QtWidgets.QLabel("Mirror Mdl: _ _ _")
        self.cmo_stretch_lbl = QtWidgets.QLabel("Stretch: _ _ _")
        self.cmo_twist_lbl = QtWidgets.QLabel("Twist: _ _ _")
        for cmd_widget in [self.cmo_rigType_lbl, self.cmo_mirrorMdl_lbl, self.cmo_stretch_lbl, self.cmo_twist_lbl]:
            layH_current_mdl_operations.addWidget(cmd_widget)

        layV_current_MO_parent.addWidget(cmo_lbl)
        layV_current_MO_parent.addLayout(layH_current_mdl_operations)
        
        # -- update_mdl_operations --
        layV_update_MO_parent = QtWidgets.QVBoxLayout()
        umo_lbl = QtWidgets.QLabel("Update")

        layH_update_mdl_operations = QtWidgets.QHBoxLayout()
        umo_rigType_lbl = QtWidgets.QLabel("Rig Type:")
        self.umo_rigType_comboBox = QtWidgets.QComboBox()
        self.umo_rigType_comboBox.addItems(["FK", "IK", "IKFK"])
        self.umo_mirrorMdl_checkBox = QtWidgets.QCheckBox("Mirror Mdl")
        self.umo_stretch_checkBox = QtWidgets.QCheckBox("Stretch")
        self.umo_twist_checkBox = QtWidgets.QCheckBox("Twist")
        for umd_widget in [self.umo_rigType_comboBox, self.umo_mirrorMdl_checkBox, self.umo_stretch_checkBox, self.umo_twist_checkBox]:
            layH_update_mdl_operations.addWidget(umd_widget)
        
        layV_update_MO_parent.addWidget(umo_lbl)
        layV_update_MO_parent.addLayout(layH_update_mdl_operations)

        self.update_btn = QtWidgets.QPushButton("Update Module Data")
        
        layV_mdl_operations_ancestor.addWidget(mdl_data_lbl)
        layV_mdl_operations_ancestor.addLayout(layV_current_MO_parent)
        layV_mdl_operations_ancestor.addLayout(layV_update_MO_parent)
        layV_mdl_operations_ancestor.addWidget(self.update_btn)
        
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

        bottom_Vlayout.addLayout(layV_deleteAdd_mdl_ancestor)

        # ---------------------------------------------------------------------
        self.setLayout(main_Vlayout)


    def UI_tab1_connect_signals(self):
        # -- visualise database --
        self.publish_btn.clicked.connect(self.sigfunc_publish_btn)
        # -- choose blueprint --

        # -- add blueprints --
        self.add_blueprint_btn.clicked.connect(self.add_blueprint)
    
    ########## UI SIGNAL FUNCTOINS ##########
    # ---- siFunc Choose modules functions ----
    def sigfunc_publish_btn(self):
        print(f"sigfunc_publish_btn clicked")

    # -------------------------------------------------------------------------
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
                self.json_data = json.load(file)
                json_dict[json_file] = self.json_data
        return json_dict

    
    def publish_mdl_database_to_chosen_rig(self):
        self.cr_json_database()


    # ---- json data functions ----
    def gather_json_data(self, json_data):
        print(f"CharRigging click button auto rig, {self.json_all_mdl_list}, data = {json_data}")
        # data for the guide's poisition (pos & rot) / constant data (spaceswap)
        # user_settings > to pass to the database!
        try:
            placement_dict = self.json_data['placement']
            constant_dict = self.json_data['constant']
            user_settings_dict = self.json_data['user_settings']
        except KeyError as e:
            print(f"{e} is not a key in {self.json_all_mdl_list[0]}")
        return placement_dict, constant_dict, user_settings_dict
    

    def cr_json_database(self):
            # print(f"database data to add: {self.gather_json_data(self.json_data)[2]}")
            self.u_s_dict = self.gather_json_data(self.json_data)[2]
            # print(f"mdl_name = {side}")
            database_schema = database_schema_002.CreateDatabase(self.json_data['mdl_name'], side, self.u_s_dict) 
            
            # unique_id = database_schema.get_unique_id()
            # print(f"unique_id == {unique_id} for {self.json_data['mdl_name']}_{side}")
            # import and call the database maker 'database_schema'


    def cr_json_guides(self):
        # Should read the database
        pass

    
    # ---- add blueprint ----
    def add_blueprint(self):
        # connect signals for module editor buttons
        for mdl, (checkBox, iterations, side) in self.mdl_choose_ui_dict.items():
            if checkBox.isChecked(): # checkbox is the master 
                # access the input from iterations and side
                iterations_value = iterations.value()
                side_value = side.currentText() if side else None
                print(f"Adding blueprint for {mdl}: Iterations={iterations_value}, Side={side_value}")

        # Should read the database
        #self.cr_json_guides()

def char_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    ui = CharRigging()
    ui.show()
    app.exec()
    return ui
            