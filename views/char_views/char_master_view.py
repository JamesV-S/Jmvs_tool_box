# ----------------------------------------- VIEW ----------------------------------------
import importlib
from maya import OpenMayaUI
import os

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

from utils import (
    utils_os
)

from views import utils_view

importlib.reload(utils_os)
importlib.reload(utils_view)

maya_main_wndwPtr = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndwPtr), QWidget)

class CharMasterView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CharMasterView, self).__init__(parent)
        version = "MVC"
        ui_object_name = f"JmvsCharMaster_{version}"
        ui_window_name = f"Jmvs_Character_Master_{version}"
        utils_view.delete_existing_ui(ui_object_name)
        self.setObjectName(ui_object_name)

        # set flags & dimensions
        # ---------------------------------- 
        self.setParent(main_window) 
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(ui_window_name)
        self.resize(300, 400)
        
        # style
        stylesheet_path = os.path.join(
            utils_os.create_directory("Jmvs_tool_box", "assets", "styles"), 
            "char_style_sheet_001.css"
            )
        print(stylesheet_path)
        with open(stylesheet_path, "r") as file:
            stylesheet = file.read()
        # self.setStyleSheet(stylesheet)
        
        self.user_module_data = {} # to store user inputs from 'choose module ui'! 
        
        self.init_ui()
        # -- CONTROL paramaters --

    def init_ui(self):
        layV_main = QtWidgets.QVBoxLayout(self)
        layH_row = QtWidgets.QHBoxLayout()
        layV_main.addLayout(layH_row)

        self.char_layout_button = QtWidgets.QPushButton("Layout")
        self.char_skeleton_button = QtWidgets.QPushButton("Skeleton")

        layH_row.addWidget(self.char_layout_button)
        layH_row.addWidget(self.char_skeleton_button)

        btn_list = [self.char_layout_button, self.char_skeleton_button]
        
        # add images
        # char_layout_image_path = os.path.join(os_custom_directory_utils.create_directory(
        #     "Jmvs_tool_box", "assets", "images"), "img_char_layout_db_001.png"
        #     )
        # # Set the image as the button icon
        # char_layout_icon = QIcon(char_layout_image_path)
        # self.char_layout_button.setIcon(char_layout_icon)
        
        utils_view.set_button_size(btn_list, 100, 100)
            