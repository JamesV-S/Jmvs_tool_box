
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
        
        # set flags & dimensions
        # ---------------------------------- 
        self.setParent(main_window) 
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(ui_window_name)
        self.resize(400, 550)
        
        self.UI()
        # button functions
        # ----------------------------------        
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # placeholder for the dropdown
        self.JSON_list = ['biped_arm.json'] # 'biped_leg.json'
        json_dict = {} # json is a dictionary,so just go gather it. 
        for json_file in self.JSON_list:
            # configer the JSON file
            json_path = os.path.join(current_dir, "..", "..", "config", json_file)
            with open(json_path, 'r') as file:
                # load the json data
                self.json_data = json.load(file)
                json_dict[json_file] = self.json_data
        
        # placeholder for ui button
        cr_JSON_db_btn = 0
        if cr_JSON_db_btn:
            pass
            # self.cr_JSON_database()
            

    def UI(self):
        # build the button's for this ui here
        # parts of the ui:
        global side
        side = "_L"
        self.orientation = "xyz"

        main_layout = QtWidgets.QVBoxLayout(self)

        self.char_rig_label = QtWidgets.QLabel("CHAR_RIG_WIP")
        main_layout.addWidget(self.char_rig_label)


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
        u_s_dict = self.gather_JSON_data(self.json_data)[2]
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
            