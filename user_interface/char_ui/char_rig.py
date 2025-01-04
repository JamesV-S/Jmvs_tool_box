
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
import os.path
import json

from databases.char_databases import database_schema_002

importlib.reload(database_schema_002)

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
        
        # button functions
        # ----------------------------------        
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # gather the existing files in 'config' and create a list of the files
        # Placeholder: 
        self.JSON_list = ['biped_arm.json', 'biped_leg.json']# , 'biped_leg.json'] # 
        self.json_dict = {} # json is a dictionary,so just go gather it. 
        for json_file in self.JSON_list:
            # configer the JSON file
            json_path = os.path.join(current_dir, "..", "..", "config", json_file)
            with open(json_path, 'r') as file:
                # load the json data
                self.json_data = json.load(file)
                self.json_dict[json_file] = self.json_data
        
        self.UI()
        # ui connections:
        # TAB 1 - Module editor
        self.add_blueprint_btn.clicked.connect(self.add_blueprint)

    def UI(self):
        # build the button's for this ui here
        # parts of the ui:
        
        self.orientation = "xyz"

        main_Vlayout = QtWidgets.QVBoxLayout(self)

        # tab 1 modules
        top_Hlayout = QtWidgets.QHBoxLayout()
        bottom_Vlayout = QtWidgets.QVBoxLayout()

        db_editor_Vlayout = QtWidgets.QVBoxLayout()
        module_editor_Vlayout = QtWidgets.QVBoxLayout()

        top_Hlayout.addLayout(db_editor_Vlayout)
        top_Hlayout.addLayout(module_editor_Vlayout)
        main_Vlayout.addLayout(top_Hlayout)
        main_Vlayout.addLayout(bottom_Vlayout)

        # database editor
        db_h_layout = QtWidgets.QHBoxLayout()
        
        db_Qlabel = QtWidgets.QLabel("database_BipedArm")
        db_h_layout.addWidget(db_Qlabel)
        db_editor_Vlayout.addLayout(db_h_layout)
    
        # ---------------------------------------------------------------------
        # module editor
        def module_editor_ui(mdl_name, side_items):
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
            
            module_editor_Vlayout.addLayout(mdl_h_layout)

            return mdl_checkBox, mdl_iterations, mdl_side
        
        ''' method of unpacking nested dict struture 'self.json_dict' 
        containing each JSON files's content under its filename as a key.
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
        self.mdl_editor_ui_dict = {}
        for mdl, sides in zip(mdl_list, side_list):
            mdl_editor_buttons = module_editor_ui(mdl, sides)
            self.mdl_editor_ui_dict[mdl] = mdl_editor_buttons

        print(f"self.mdl_editor_ui_dict = {self.mdl_editor_ui_dict}")

        
        # ---------------------------------------------------------------------
        # Updating modules and database
        update_Qlabel = QtWidgets.QLabel("update")
        # bottom_Vlayout.addWidget(update_Qlabel)

        self.add_blueprint_btn = QtWidgets.QPushButton("Add module")
        bottom_Vlayout.addWidget(self.add_blueprint_btn)

       
    def gather_JSON_data(self, json_data):
        print(f"CharRigging click button auto rig, {self.JSON_list}, data = {json_data}")
        # data for the guide's poisition (pos & rot) / constant data (spaceswap)
        # user_settings > to pass to the database!
        try:
            placement_dict = self.json_data['placement']
            constant_dict = self.json_data['constant']
            user_settings_dict = self.json_data['user_settings']
        except KeyError as e:
            print(f"{e} is not a key in {self.JSON_list[0]}")
        return placement_dict, constant_dict, user_settings_dict
    

    def cr_JSON_database(self):
            # print(f"database data to add: {self.gather_JSON_data(self.json_data)[2]}")
            self.u_s_dict = self.gather_JSON_data(self.json_data)[2]
            # print(f"mdl_name = {side}")
            database_schema = database_schema_002.CreateDatabase(self.json_data['mdl_name'], side, u_s_dict) 
            
            # unique_id = database_schema.get_unique_id()
            # print(f"unique_id == {unique_id} for {self.json_data['mdl_name']}_{side}")
            # import and call the database maker 'database_schema'


    def cr_JSON_guides(self):
        # Should read the database
        pass

    
    def add_blueprint(self):
        # connect signals for module editor buttons
        for mdl, (checkBox, iterations, side) in self.mdl_editor_ui_dict.items():
            if checkBox.isChecked(): # checkbox is the master 
                # access the input from iterations and side
                iterations_value = iterations.value()
                side_value = side.currentText() if side else None
                print(f"Adding blueprint for {mdl}: Iterations={iterations_value}, Side={side_value}")
        
        #self.cr_JSON_database()

        # Should read the database
        #self.cr_JSON_guides()

def char_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    ui = CharRigging()
    ui.show()
    app.exec()
    return ui
            