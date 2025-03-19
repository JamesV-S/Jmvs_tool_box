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

from views import utils_QTree

from models.char_models import char_skeleton_model
from views.char_views import char_skeleton_view

importlib.reload(os_custom_directory_utils)
importlib.reload(utils)
importlib.reload(utils_QTree)
importlib.reload(cr_guides)
importlib.reload(cr_ctrl)
importlib.reload(char_skeleton_model)
importlib.reload(char_skeleton_view)

class CharSkeletonController:
    def __init__(self): # class
        self.model = char_skeleton_model.CharSkeletonModel()
        self.view = char_skeleton_view.CharSkeletonView()