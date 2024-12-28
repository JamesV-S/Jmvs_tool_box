
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
        main_layout = QtWidgets.QVBoxLayout(self)

        h_layout = QtWidgets.QHBoxLayout()
        
        
        btn_1 = QtWidgets.QPushButton("Button 1")
        btn_2 = QtWidgets.QPushButton("Button 2")
        btn_list = [btn_1, btn_2]
        
        for buttons in btn_list:
            buttons.setFixedSize(50, 50)
            buttons.setMinimumSize(40, 40)
            buttons.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        h_layout.addWidget(btn_1)
        h_layout.addWidget(btn_2)

        grid_layout = QtWidgets.QGridLayout()
        grid_layout.addWidget(QtWidgets.QPushButton("Grid Button 1"), 0, 0)
        grid_layout.addWidget(QtWidgets.QPushButton("Grid Button 2"), 0, 1)

        main_layout.addLayout(h_layout)
        main_layout.addLayout(grid_layout)

        # Add more widgets to the main layout if necessary. 
        # main_layout.addWidget(QtWidgets.QLabel("Additional Widget"))
        
        self.setLayout(main_layout)

def geoDB_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    ui = GeoDatabase()
    ui.show()
    app.exec()
    return ui