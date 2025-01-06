
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
import importlib
import os.path

from databases.geo_databases import database_schema_001
importlib.reload(database_schema_001)

# For the time being, use this file to simply call the 'modular_char_ui.py'
maya_main_wndwPtr = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndwPtr), QWidget)

def delete_existing_ui(ui_name):
    if cmds.window(ui_name, exists=True):
        cmds.deleteUI(ui_name, window=True)

class GeoDatabase(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(GeoDatabase, self).__init__(parent)
        version = "001"
        ui_object_name = f"JmvsGeoDatabase_{version}"
        ui_window_name = f"Jmvs_geo_database_{version}"
        delete_existing_ui(ui_object_name)
        self.setObjectName(ui_object_name)

        self.setStyleSheet("""
            QWidget {
                background-color:#4f7b7f;
                color: #333;
                font-size: 12px;
            }
            QPushButton {
                background-color: #ccc;
                border: 1px solid #888;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #ddd;
            }
            QLabel {
                font-weight: bold;
        """)


        # Set flags & dimensions
        self.setParent(main_window)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(ui_window_name)
        self.resize(400, 550)
        
        print("GeoDatabase class defined")

        self.UI()

    def UI(self):
        # Build the ui buttons and layout here
        
        #self.geoDB_label = QtWidgets.QLabel("GeoDB_WIP")
        #main_layout.addWidget(self.geoDB_label)
        main_Vlayout = QtWidgets.QVBoxLayout(self)

        # 4 layouts within the main_Vlayout

        # 2: Tab layout Database selector
        ''' I want this to work a lot like the "layer" tab in ngskinTools! with this tab on the left  '''
        example_database_list = ["DB_geo_mech", "DB_geo_arm", "DB_geo_other"]
        # create layer ui for this and put into this layout:
        db_selector_layout = QtWidgets.QVBoxLayout()
        # this button will create a new database. 
        cr_database_btn = QtWidgets.QPushButton("+")

        # 1: Tab layout Database visualisation
        ''' I want this to work a lot like the "influences" tab in ngskinTools! with this tab on the right next to the `db_selector_layout` '''
        db_list_layout = QtWidgets.QVBoxLayout()
        

        # 3: tab layout for buttons that add joints or geometry to the database




        self.setLayout(main_Vlayout)
    
    def create_database(self):
        pass

def geoDB_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    ui = GeoDatabase()
    ui.show()
    app.exec()
    return ui