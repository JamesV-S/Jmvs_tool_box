
import maya.cmds as cmds
from maya import OpenMayaUI

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QWidget)
from shiboken6 import wrapInstance

import sys
import random
import importlib
import os


from user_interface.char_ui import char_rig
importlib.reload(char_rig)


# For the time being, use this file to simply call the 'modular_char_ui.py'
maya_main_wndw = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndw), QWidget)

def delete_existing_ui(ui_name):
    if cmds.window(ui_name, exists=True):
        cmds.deleteUI(ui_name, window=True)

class ToolBox(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(ToolBox, self).__init__(*args, **kwargs)

        # ui for toolbox dimensions
        
        # placeholder for ui button
        auto_rig_button = 1
        if auto_rig_button:
            self.auto_rig_btn_func()
        
    def UI(self):
        # build the tool button's in here
        pass

    def auto_rig_btn_func(self):
        # when the button is clicked, load the char_ui!
        char_rig.char_main()
        print("toolBox click button auto rig")

def tl_bx_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    
    ui = ToolBox()
    ui.show()
    app.exec()
    return ui
            