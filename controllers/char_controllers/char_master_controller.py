# ------------------------------ Controller -----------------------------------
import maya.cmds as cmds
from maya import OpenMayaUI

try:
    from PySide6 import QtCore, QtWidgets, QtGui
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtGui import QIcon, QStandardItemModel, QStandardItem
    from PySide6.QtWidgets import (QWidget)
    from shiboken6 import wrapInstance
except ModuleNotFoundError:
    from PySide2 import QtCore, QtWidgets, QtGui
    from PySide2.QtCore import Qt, Signal
    from PySide2.QtGui import QIcon, QStandardItemModel, QStandardItem
    from PySide2.QtWidgets import (QWidget)
    from shiboken2 import wrapInstance

import service_locator_pattern
import importlib
import os.path

from utils import (
    utils,
)


from systems.sys_char_rig import (
    cr_guides, 
    cr_ctrl
)

from utils import utils_QTree

from models.char_models import char_master_model
from views.char_views import char_master_view

from main_entry_points.char_mep import (
    char_layout_main,
    char_skeleton_main
)

''''''
# Temp:

from user_interface.char_ui import char_rig

''''''

importlib.reload(utils)
importlib.reload(utils_QTree)
importlib.reload(cr_guides)
importlib.reload(cr_ctrl)
importlib.reload(char_master_model)
importlib.reload(char_master_view)
importlib.reload(char_layout_main)
importlib.reload(char_skeleton_main)
importlib.reload(char_rig)

import service_locator_pattern

class CharMasterController:
    def __init__(self):
        self.model = char_master_model.CharMasterModel()
        self.view = char_master_view.CharMasterView()

        self.view.char_layout_button.clicked.connect(self.sigfunc_char_layout_button)
        self.view.char_skeleton_button.clicked.connect(self.sigfunc_char_skeleton_button)
        
        # Add service here
        char_layout_instance = char_layout_main.CharLayoutMain()
        service_locator_pattern.ServiceLocator.add_service(
            'char_layout_main', char_layout_instance)
        char_skeleton_instance = char_skeleton_main.CharSkeletonMain()
        service_locator_pattern.ServiceLocator.add_service(
            'char_skeleton_main', char_skeleton_instance)
    

    def sigfunc_char_layout_button(self):
        print(f"running 'char_layout_controller'")
        char_layout_controller = service_locator_pattern.ServiceLocator.get_service('char_layout_main')
        if char_layout_controller:
            char_layout_controller.show_ui()
    

    def sigfunc_char_skeleton_button(self):
        print(f"running 'char_skeleotn_controller'")
        # char_rig.char_main()

    