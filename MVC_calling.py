
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

from systems import (
    os_custom_directory_utils
)
from views import utils_view

importlib.reload(os_custom_directory_utils)
importlib.reload(utils_view)

# Using sevice pattern method to manage dependecies!!!
import service_locator_pattern # DO NOT RELOAD!!

# from main_entry_points.char_mep import char_master_main # PY File
from main_entry_points.geoDB_mep import picker_geoDB_main

# importlib.reload(char_master_main)
importlib.reload(picker_geoDB_main)

maya_main_wndwPtr = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndwPtr), QWidget)

class MVCCALLING(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(MVCCALLING, self).__init__(*args, **kwargs)
        version = "001"
        self.ui_object_name = f"JmvsMVCCALLING_{version}"
        ui_window_name = f"Jmvs_MVCCALLING_{version}"
        utils_view.delete_existing_ui(self.ui_object_name)
        self.setObjectName(self.ui_object_name)
        
        # set flags & dimensions
        # ---------------------------------- 
        self.setParent(main_window) 
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(ui_window_name)
        self.resize(300, 300)

        # button functions
        # ----------------------------------  
        self.current_ui = None
        self.ui_stack = []

        self.UI()
        self.UI_connect_signals()

        '''INITIALISE ITS CONTROLLER'''
        '''CALL THE MEP AND RETURN CONTROLLER'''
        

    def UI(self):
        self.char_button = QtWidgets.QPushButton()
        self.vehicle_button = QtWidgets.QPushButton()
        self.geoDB_button = QtWidgets.QPushButton()
        self.other_button = QtWidgets.QPushButton("other tools")
        
        btn_list = [self.char_button, self.vehicle_button, self.geoDB_button, self.other_button]
        
        # add images
        char_image_path = os.path.join(os_custom_directory_utils.create_directory(
            "Jmvs_tool_box", "assets", "images"), "img_char_db_001.png"
            )
        # Set the image as the button icon
        char_icon = QIcon(char_image_path)

        geo_image_path = os.path.join(os_custom_directory_utils.create_directory(
            "Jmvs_tool_box", "assets", "images"), "img_geo_db_001.png"
            )
        # Set the image as the button icon
        geo_icon = QIcon(geo_image_path)

        vehicle_image_path = os.path.join(os_custom_directory_utils.create_directory(
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
    

    def UI_connect_signals(self):
        self.char_button.clicked.connect(self.sigFunc_character)
        self.geoDB_button.clicked.connect(self.sigFunc_geoDB_picekr)
        self.other_button.clicked.connect(self.sigFunc_other)
        

    def sigFunc_character(self):
        print("loading character MASTER Main")
        # Retrieve the initialised tool anywhere I want!
        char_master_controller = service_locator_pattern.ServiceLocator.get_service('char_master_main')
        if char_master_controller:
            char_master_controller.show_ui()
            print(f"RETRIAVAL WORKEDDDDDDD")
        else:
            print("char_master_controller NOT retrieved")
            print("Available services:", service_locator_pattern.ServiceLocator._services)
        utils_view.delete_existing_ui(self.ui_object_name)


    def sigFunc_other(self):
        print(f"OTHER FUNCCCCCCCCCC")
        char_master_controller = service_locator_pattern.ServiceLocator.get_service('char_master_main')
        if char_master_controller:
            char_master_controller.show_ui()


    def sigFunc_geoDB_picekr(self):
        pass
        # # REGESTERING THE INSTANCE! Acts like the Master initaliser. 
        # picker_geoDB_instance = picker_geoDB_main.picker_geoDB_main()
        # service_locator_pattern.ServiceLocator.add_service('picker_geoDB_main', picker_geoDB_instance)
        # self.pciker_geoDB_controller = service_locator_pattern.ServiceLocator.get_service('picker_geoDB_main')
        # utils_view.delete_existing_ui(self.ui_object_name)


def MVC_calling_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    
    ui = MVCCALLING()
    ui.show()
    app.exec()
    return ui
            