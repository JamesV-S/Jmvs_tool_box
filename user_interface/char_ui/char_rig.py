
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
        self.JSON_list = ['biped_arm.json']# , 'biped_leg.json'] # 
        json_dict = {} # json is a dictionary,so just go gather it. 
        for json_file in self.JSON_list:
            # configer the JSON file
            json_path = os.path.join(current_dir, "..", "..", "config", json_file)
            with open(json_path, 'r') as file:
                # load the json data
                self.json_data = json.load(file)
                json_dict[json_file] = self.json_data
        
        '''
        # placeholder for ui button
        cr_JSON_db_btn = 0
        if cr_JSON_db_btn:
            pass
            # self.cr_JSON_database()
        '''
        
        self.UI()
        # ui connections:
        # TAB 1 - Module editor
        

    def UI(self):
        # build the button's for this ui here
        # parts of the ui:
        global side
        side = "_L"
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
    
        # module editor

        def module_editor_ui(mdl_name, side_items):
            mdl_h_layout = QtWidgets.QHBoxLayout()
            
            mdl_checkBox = QtWidgets.QCheckBox()
            mdl_name = QtWidgets.QLabel(mdl_name)
            mdl_iterations = QtWidgets.QSpinBox()
            mdl_iterations.setMinimum(1)

            mdl_side = QtWidgets.QComboBox()
            mdl_side.addItems(side_items)
            
            mdl_h_layout.addWidget(mdl_checkBox)
            mdl_h_layout.addWidget(mdl_name)
            mdl_h_layout.addWidget(mdl_iterations)
            mdl_h_layout.addWidget(mdl_side)

            module_editor_Vlayout.addLayout(mdl_h_layout)
        
        try:
            print(self.json_data['mdl_name'])
            mdl_list = []
            #for dict in self.json_data:
            #    mdl_name = dict['mdl_name']
            #    mdl_list.append(mdl_name)
            #print(mdl_list)
        except KeyError as e:
            print(f"{e} is not a key in {self.json_data}")
        module_editor_ui("bipedArm", ["L", "R"])
        
        # sets the buttons, need to gather the existing JSON's for the name
        # Need to return the buttons for connection: `self.button_02.clicked.connect(self.second_btn_func)`
            # the buttons create the settings for building the database & blueprint in the scene!
        # Need to 


        # Updating modules and database
        update_Qlabel = QtWidgets.QLabel("update")
        bottom_Vlayout.addWidget(update_Qlabel)
       

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
    

    def cr_JSON_guides(self):
        # Should read the database
        pass


    def cr_JSON_database(self):
        # print(f"database data to add: {self.gather_JSON_data(self.json_data)[2]}")
        side = '_L'
        self.u_s_dict = self.gather_JSON_data(self.json_data)[2]
        print(f"mdl_name = {side}")
        database_schema = database_schema_002.CreateDatabase(self.json_data['mdl_name'], side, u_s_dict) 
        # unique_id = database_schema.get_unique_id()
        # print(f"unique_id == {unique_id} for {self.json_data['mdl_name']}_{side}")
        # import and call the database maker 'database_schema'


def char_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    ui = CharRigging()
    ui.show()
    app.exec()
    return ui
            