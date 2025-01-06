
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

from user_interface.char_ui import char_rig 
from user_interface.vehicle_ui import vehicle_rig 
from user_interface.geoDB_ui import geo_db
from user_interface.other_ui import other_tool

importlib.reload(char_rig)
importlib.reload(vehicle_rig)
importlib.reload(geo_db)
importlib.reload(other_tool)

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
        ui_object_name = f"JmvsToolBox_{version}"
        ui_window_name = f"Jmvs_ToolBox_{version}"
        delete_existing_ui(ui_object_name)
        self.setObjectName(ui_object_name)
        ''' Doesn't work
        # ---------------------------------
        # Create a frameless window
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Custom title bar
        self.title_bar = QtWidgets.QWidget(self)
        self.title_bar.setStyleSheet("background-color: #444; color: white;")
        self.title_bar.setFixedHeight(30)

        self.title_label = QtWidgets.QLabel(ui_window_name, self.title_bar)
        self.title_label.setStyleSheet("margin-left: 10px;")

        # Custom close button
        self.close_button = QtWidgets.QPushButton("X", self.title_bar)
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("background-color: #f00; border: none;")
        self.close_button.clicked.connect(self.close)

        # Layout for title bar
        title_layout = QtWidgets.QHBoxLayout(self.title_bar)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.close_button)

        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.title_bar)
        '''
        # ---------------------------------

        self.setStyleSheet("""
            QWidget {
                background-color:rgb(245, 245, 245);
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
            QWidget {
                background-color: #444;
                color: white;
            }
            QWidget::title {
                background-color: #444;
                color: rgb(220, 127, 20);
            }
        """)

        # set flags & dimensions
        # ---------------------------------- 
        self.setParent(main_window) 
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(ui_window_name)
        self.resize(300, 500)

        # button functions
        # ----------------------------------  
        self.current_ui = None
        self.ui_stack = []

        self.UI()
        
        self.char_button.clicked.connect(self.char_func)
        self.vehicle_button.clicked.connect(self.vehicle_func)
        self.geoDB_button.clicked.connect(self.geo_func)
        self.other_button.clicked.connect(self.other_func)

        
    def UI(self):
        self.char_button = QtWidgets.QPushButton("Char_tool")
        self.vehicle_button = QtWidgets.QPushButton("Vehicle_tool")
        self.geoDB_button = QtWidgets.QPushButton("geometryDB_tool")
        self.other_button = QtWidgets.QPushButton("other_tool")
        
        btn_list = [self.char_button, self.vehicle_button, self.geoDB_button, self.other_button]
        
        for buttons in btn_list:
            buttons.setFixedSize(125, 125)
            buttons.setMinimumSize(125, 125)
            buttons.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        '''
        # Instead of calling the main function directly in the lambda, 
        # pass the class to load_ui which will make an instance of it when needed
        Call the main function of the class when I want to initialisee the 
        ui outside of ToolBox Menu (right clcik function!)
        # self.char_button.clicked.connect(lambda: self.load_ui(CharRigging))
        self.vehicle_button.clicked.connect(lambda: self.load_ui(VehicleRigging))
        self.geoDB_button.clicked.connect(lambda: self.load_ui(GeoDatabase))
        self.other_button.clicked.connect(lambda: self.load_ui(OtherTool))
        '''

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
    
    
    def char_func(self):
        print("loading character ui")
        char_rig.char_main()

    
    def vehicle_func(self):
        print("loading vehicle ui")
        vehicle_rig.vehicle_main()


    def geo_func(self):
        print("loading geo ui")
        geo_db.geoDB_main()
    

    def other_func(self):
        print("loading other ui")
        other_tool.other_main()

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
            