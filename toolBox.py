
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

from main_entry_points.geoDB_mep import picker_geoDB_main

from user_interface.char_ui import char_rig 
from user_interface.vehicle_ui import vehicle_rig 
from user_interface.geoDB_ui import master_geo_db_picker
from user_interface.other_ui import other_tool

from systems import (
    os_custom_directory_utils
)

importlib.reload(picker_geoDB_main)

importlib.reload(char_rig)
importlib.reload(vehicle_rig)
importlib.reload(master_geo_db_picker)
importlib.reload(other_tool)
importlib.reload(os_custom_directory_utils)

# For the time being, use this file to simply call the 'modular_char_ui.py'
maya_main_wndwPtr = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndwPtr), QWidget)

def delete_existing_ui(ui_name):
    if cmds.window(ui_name, exists=True):
        cmds.deleteUI(ui_name, window=True)

class ToolBox(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(ToolBox, self).__init__(*args, **kwargs)
        version = "001"
        self.ui_object_name = f"JmvsToolBox_{version}"
        ui_window_name = f"Jmvs_ToolBox_{version}"
        delete_existing_ui(self.ui_object_name)
        self.setObjectName(self.ui_object_name)
        
        # ---------------------------------
        # style
        stylesheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "assets", "styles", "toolBox_style_sheet.css")
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

        # button functions
        # ----------------------------------  
        self.current_ui = None
        self.ui_stack = []

        self.UI()
        self.UI_connect_signals()

        self.picker_geoDB_controller = None

        
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

        
        # status bar label:
        #self.status_label = QtWidgets.QLabel("ToolBox menu open")
        #self.grid_layout.addWidget(self.status_label, 2, 0)
        
        '''
        # Navigation buttons
        back_button = QtWidgets.QPushButton("BACK")
        back_button.clicked.connect(self.go_back)
        self.grid_layout.addWidget(back_button)

        home_button = QtWidgets.QPushButton("Home")
        back_button.clicked.connect(self.go_home)
        self.grid_layout.addWidget(home_button)
        ''' 
    
    
    def UI_connect_signals(self):
        self.char_button.clicked.connect(self.sigFunc_character)
        self.vehicle_button.clicked.connect(self.sigFunc_vehicle)
        self.geoDB_button.clicked.connect(self.sigFunc_geometry)
        self.other_button.clicked.connect(self.sigFunc_other)


    def sigFunc_character(self):
        print("loading character ui")
        char_rig.char_main()
        delete_existing_ui(self.ui_object_name)

    
    def sigFunc_vehicle(self):
        print("loading vehicle ui")
        vehicle_rig.vehicle_main()
        delete_existing_ui(self.ui_object_name)


    def sigFunc_geometry(self):
        print("loading geo ui")
        # self.picker_geoDB_controller = picker_geoDB_main.picker_geoDB_main()
        master_geo_db_picker.master_geo_main()
        delete_existing_ui(self.ui_object_name)
    

    def sigFunc_other(self):
        print("loading other ui")
        other_tool.geoDB_main()
        delete_existing_ui(self.ui_object_name)

    # Not in use
    '''
    def load_ui(self, ui_class):
        if self.current_ui:
            # need to save current UI to stack
            self.ui_stack.append(self.current_ui)
            self.grid_layout.removeWidget(self.current_ui)
            self.current_ui.deleteLater()
        
        self.current_ui = ui_class()
        self.grid_layout.addWidget(self.current_ui)
        # use the update status
        self.update_status(f"{self.current_ui.__class__.__name__} Open")
    
    
    def go_back(self):
        if self.ui_stack:
            # Remove the current UI
            if self.current_ui:
                self.grid_layout.removeWidget(self.current_ui)
                self.current_ui.deleteLater()

            # get the last ui, pop it from there & show that ui
            self.current_ui = self.ui_stack.pop()
            self.grid_layout.addWidget(self.current_ui)
            self.update_status(f"{self.current_ui.__class__.__name__} Open")
        else:
            # If the stack is empty, go back to home. 
            self.go_home()


    def go_home(self):
        if self.current_ui:
            self.grid_layout.removeWidget(self.current_ui)
            self.current_ui.deleteLater()
            self.current_ui = None
        self.update_status("ToolBox menu Open")


    def update_status(self, status):
        self.status_label.setText(f"status: {status}")
    '''

def tool_box_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    
    ui = ToolBox()
    ui.show()
    app.exec()
    return ui
            