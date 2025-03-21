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
    from PySide2.QtGui import QIcon
    from PySide2.QtWidgets import (QWidget)
    from shiboken2 import wrapInstance

import importlib
import os.path

from systems import (
    os_custom_directory_utils,
    utils
)

from systems.sys_char_rig import (
    cr_guides, 
    cr_ctrl
)

from controllers import utils_QTree

from models.char_models import char_master_model
from views.char_views import char_master_view

from main_entry_points.char_mep import (
    char_layout_main,
    char_skeleton_main
)

importlib.reload(os_custom_directory_utils)
importlib.reload(utils)
importlib.reload(utils_QTree)
importlib.reload(cr_guides)
importlib.reload(cr_ctrl)
importlib.reload(char_master_model)
importlib.reload(char_master_view)
importlib.reload(char_layout_main)
importlib.reload(char_skeleton_main)

class CharMasterController:
    def __init__(self):
        self.model = char_master_model.CharMasterModel()
        self.view = char_master_view.CharMasterView()

        self.view.char_layout_button.clicked.connect(self.sigfunc_char_layout_button)
        self.view.char_skeleton_button.clicked.connect(self.sigfunc_char_skeleton_button)
        # self.char_layout_controller = None
        
    
    def sigfunc_char_layout_button(self):
        print(f"running 'char_layout_controller'")
        # self.char_layout_controller = char_layout_main.char_layout_main()

    
    def sigfunc_char_skeleton_button(self):
        print(f"running 'char_skeleotn_controller'")

    