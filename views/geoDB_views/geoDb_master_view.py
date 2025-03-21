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

from systems import (
    os_custom_directory_utils
)

from views import utils_view

importlib.reload(os_custom_directory_utils)
importlib.reload(utils_view)

maya_main_wndwPtr = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndwPtr), QWidget)

class GeoDbMasterView(QtWidgets.QWidget):
    # define a signal to indicate completion of db creation
    # databaseCreated = Signal()
    def __init__(self, parent=None):
        super(GeoDbMasterView, self).__init__(parent)
        version = "MVC"
        self.ui_object_name = f"Jmvs_geoDB_master_{version}"
        ui_window_name = f"Jmvs geoDB master {version}"
        utils_view.delete_existing_ui(self.ui_object_name)
        self.setObjectName(self.ui_object_name)
        
        # set flags & dimensions
        # ---------------------------------- 
        self.setParent(main_window) 
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(ui_window_name)
        self.resize(300, 150)

        # ---------------------------------
        # style
        stylesheet_path = os.path.join(
            os_custom_directory_utils.create_directory("Jmvs_tool_box", "assets", "styles"), 
            "toolBox_style_sheet.css"
            )
        print(stylesheet_path)
        with open(stylesheet_path, "r") as file:
            stylesheet = file.read()
        self.setStyleSheet(stylesheet)

        self.init_ui()


    def init_ui(self):
        self.export_usd_button = QtWidgets.QPushButton("EXPORT")
        self.import_usd_button = QtWidgets.QPushButton("IMPORT")
        self.geoDB_button = QtWidgets.QPushButton("DATABASE")
        
        btn_list = [self.export_usd_button, self.import_usd_button, self.geoDB_button]
        
        # add images
        '''
        export_image_path = os.path.join(os_custom_directory_utils.create_directory(
            "Jmvs_tool_box", "user_interface", "CSS", "images"), "img_char_db_001.png"
            )
        # Set the image as the button icon
        export_icon = QIcon(export_image_path)

        import_image_path = os.path.join(os_custom_directory_utils.create_directory(
            "Jmvs_tool_box", "user_interface", "CSS", "images"), "img_vehicle_db_001.png"
            )
        # Set the image as the button icon
        import_icon = QIcon(import_image_path)
        
        geo_image_path = os.path.join(os_custom_directory_utils.create_directory(
            "Jmvs_tool_box", "user_interface", "CSS", "images"), "img_geo_db_001.png"
            )
        # Set the image as the button icon
        geo_icon = QIcon(geo_image_path)

        self.export_usd_button.setIcon(export_icon)
        self.import_usd_button.setIcon(import_icon)
        self.geoDB_button.setIcon(geo_icon)
        '''

        for buttons in btn_list:
            buttons.setFixedSize(135, 135)
            buttons.setMinimumSize(135, 135)
            buttons.setIconSize(QtCore.QSize(135, 135))  # Explicitly set icon size to button size
            buttons.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            
        # grid layout
        self.grid_layout = QtWidgets.QGridLayout(self)
        
        # add the widget!
        self.grid_layout.addWidget(self.export_usd_button, 0, 0)
        self.grid_layout.addWidget(self.import_usd_button, 0, 1)
        self.grid_layout.addWidget(self.geoDB_button, 0, 2)