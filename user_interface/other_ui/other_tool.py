
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

class OtherTool(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(OtherTool, self).__init__(parent)
        version = "001"
        ui_object_name = f"JmvsOtherTool_{version}"
        ui_window_name = f"Jmvs_other_tool_{version}"
        delete_existing_ui(ui_object_name)
        self.setObjectName(ui_object_name)

        # set flags & dimensions
        # ---------------------------------- 
        self.setParent(main_window) 
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(ui_window_name)
        self.resize(300, 150)

        self.UI()

    def UI(self):
        # Build the ui buttons and layout here
        main_layout = QtWidgets.QVBoxLayout(self)

        self.other_label = QtWidgets.QLabel("Other_Tool_WIP")
        main_layout.addWidget(self.other_label)

def other_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    ui = OtherTool()
    ui.show()
    app.exec()
    return ui