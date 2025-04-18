
import maya.cmds as cmds
from maya import OpenMayaUI
import sys
import importlib
import os

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


from models import tool_box_model
from views import tool_box_view

from views import utils_view

importlib.reload(tool_box_model)
importlib.reload(tool_box_view)
importlib.reload(utils_view)

# Using sevice pattern method to manage dependecies!!!
import service_locator_pattern # DO NOT RELOAD!!

maya_main_wndwPtr = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndwPtr), QWidget)


class ToolBoxController(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(ToolBoxController, self).__init__(*args, **kwargs)
        self.view = tool_box_view.ToolBoxView()
        self.model = tool_box_model.ToolBoxModel()

        self.view.char_button.clicked.connect(self.sigFunc_character)
        self.view.geoDB_button.clicked.connect(self.sigFunc_geoDB_picekr)
        self.view.other_button.clicked.connect(self.sigFunc_other)


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
        utils_view.delete_existing_ui(self.view.ui_object_name)


    def sigFunc_other(self):
        print(f"OTHER FUNCCCCCCCCCC")
        char_master_controller = service_locator_pattern.ServiceLocator.get_service('char_master_main')
        if char_master_controller:
            char_master_controller.show_ui()


    def sigFunc_geoDB_picekr(self):
        geoDB_master_controller = service_locator_pattern.ServiceLocator.get_service('geoDB_master_main')
        if geoDB_master_controller:
            geoDB_master_controller.show_ui()
            utils_view.delete_existing_ui(self.view.ui_object_name)
       

# def MVC_calling_main():
#     app = QtWidgets.QApplication.instance()
#     if not app:
#         app = QtWidgets.QApplication([])
    
#     ui = ToolBoxController()
#     ui.show()
#     app.exec()
#     return ui
            