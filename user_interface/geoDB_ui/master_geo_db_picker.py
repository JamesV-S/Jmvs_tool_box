
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

from main_entry_points.geoDB_mep import (
    import_geo_usd_main,
    export_geo_usd_main
)

from user_interface.geoDB_ui import (
    export_usd_geo_UUID,
    # import_usd_geo_UUID,
    geo_db
    )

from systems import (
    os_custom_directory_utils
)

importlib.reload(import_geo_usd_main)
importlib.reload(export_geo_usd_main)
importlib.reload(export_usd_geo_UUID)
# importlib.reload(import_usd_geo_UUID)
importlib.reload(geo_db)

# For the time being, use this file to simply call the 'modular_char_ui.py'
maya_main_wndwPtr = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndwPtr), QWidget)

def delete_existing_ui(ui_name):
    if cmds.window(ui_name, exists=True):
        cmds.deleteUI(ui_name, window=True)

class masterGeoPicker(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(masterGeoPicker, self).__init__(*args, **kwargs)
        version = "001"
        self.ui_object_name = f"Jmvs_masterGeoPicker_{version}"
        ui_window_name = f"Jmvs_masterGeoPicker_{version}"
        delete_existing_ui(self.ui_object_name)
        self.setObjectName(self.ui_object_name)
        
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
        

        # set flags & dimensions
        # ---------------------------------- 
        self.setParent(main_window) 
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(ui_window_name)
        self.resize(300, 150)

        # button functions
        # ----------------------------------  
        self.current_ui = None
        self.ui_stack = []

        self.UI()
        
        self.export_usd_button.clicked.connect(self.export_usd_func)
        self.import_usd_button.clicked.connect(self.import_usd_func)
        self.geoDB_button.clicked.connect(self.geo_func)

        self.import_geo_usd_controller = None
        self.export_geo_usd_controller = None

        
    def UI(self):
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
    
    
    def export_usd_func(self):
        print("loading export ui")
        self.export_geo_usd_controller = export_geo_usd_main.import_geo_usd_main()
        # export_usd_geo_UUID.export_UUID_usd_main()
        #delete_existing_ui(self.ui_object_name)

    
    def import_usd_func(self):
        print("loading import ui")
        self.import_geo_usd_controller = import_geo_usd_main.import_geo_usd_main()
        #delete_existing_ui(self.ui_object_name)


    def geo_func(self):
        print("loading geo ui")
        geo_db.geoDB_main()
        # delete_existing_ui(self.ui_object_name)


def master_geo_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    
    ui = masterGeoPicker()
    ui.show()
    app.exec()
    return ui
            