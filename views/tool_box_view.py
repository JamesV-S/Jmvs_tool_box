
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
import os

from utils import (
    utils_os
)
from views import utils_view

importlib.reload(utils_os)
importlib.reload(utils_view)

maya_main_wndwPtr = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndwPtr), QWidget)

class ToolBoxView(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(ToolBoxView, self).__init__(*args, **kwargs)
        version = "MVC"
        self.ui_object_name = f"JmvsToolBoxView_{version}"
        ui_window_name = f"Jmvs_tool_box_{version}"
        utils_view.delete_existing_ui(self.ui_object_name)
        self.setObjectName(self.ui_object_name)
        
        stylesheet_path = os.path.join(
            utils_os.create_directory("Jmvs_tool_box", "assets", "styles"), 
            "toolBox_style_sheet.css"
            )
        print(stylesheet_path)
        with open(stylesheet_path, "r") as file:
            stylesheet = file.read()
        self.setStyleSheet(stylesheet)

        # set flags & dimensions
        # ---------------------------------- 
        self.setParent(main_window) 
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(ui_window_name)
        self.resize(300, 300)

        self.init_ui()


    def init_ui(self):
        self.char_button = QtWidgets.QPushButton()
        self.vehicle_button = QtWidgets.QPushButton()
        self.geoDB_button = QtWidgets.QPushButton()
        self.other_button = QtWidgets.QPushButton("other tools")
        
        btn_list = [self.char_button, self.vehicle_button, self.geoDB_button, self.other_button]
        
        # add images
        char_image_path = os.path.join(utils_os.create_directory(
            "Jmvs_tool_box", "assets", "images"), "img_char_db_001.png"
            )
        # Set the image as the button icon
        char_icon = QIcon(char_image_path)

        geo_image_path = os.path.join(utils_os.create_directory(
            "Jmvs_tool_box", "assets", "images"), "img_geo_db_001.png"
            )
        # Set the image as the button icon
        geo_icon = QIcon(geo_image_path)

        vehicle_image_path = os.path.join(utils_os.create_directory(
            "Jmvs_tool_box", "assets", "images"), "img_vehicle_db_001.png"
            )
        # Set the image as the button icon
        vehicle_icon = QIcon(vehicle_image_path)

        self.char_button.setIcon(char_icon)
        self.geoDB_button.setIcon(geo_icon)
        self.vehicle_button.setIcon(vehicle_icon)


        for buttons in btn_list:
            buttons.setFixedSize(135, 135)
            buttons.setMinimumSize(135, 135)
            buttons.setIconSize(QtCore.QSize(135, 135))  # Explicitly set icon size to button size
            buttons.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            

        # grid layout
        self.grid_layout = QtWidgets.QGridLayout(self)
        
        # add the widget!
        self.grid_layout.addWidget(self.char_button, 0, 0)
        self.grid_layout.addWidget(self.vehicle_button, 0, 1)
        self.grid_layout.addWidget(self.geoDB_button, 1, 0)
        self.grid_layout.addWidget(self.other_button, 1, 1)