# ----------------------------------------- VIEW ----------------------------------------
# views/export_database_view.py
import importlib
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
import os

from systems import (
    utils,
    os_custom_directory_utils
)

importlib.reload(utils)
importlib.reload(os_custom_directory_utils)

maya_main_wndwPtr = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndwPtr), QWidget)

class exportDatabaseView(QtWidgets.QWidget):
    databaseCreated = Signal()

    def __init__(self, parent=None):
        super(exportDatabaseView, self).__init__(parent)
        version = "MVC"
        ui_object_name = f"DB_EXPORT{version}"
        ui_window_name = f"DB Export Options {version}"
        utils.delete_existing_ui(ui_object_name)
        self.setObjectName(ui_object_name)
        self.setWindowTitle(ui_window_name)
        
        self.setParent(main_window)
        self.setWindowFlags(Qt.Window)
        self.resize(400, 100)
        
        # Load stylesheet
        stylesheet_path = os.path.join(
            os_custom_directory_utils.create_directory("Jmvs_tool_box", "assets", "styles"), 
            "geoDB_style_sheet_001.css"
            )
        with open(stylesheet_path, "r") as file:
            stylesheet = file.read()
        self.setStyleSheet(stylesheet)

        self.init_ui()
    '''
    def init_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        
        # FileName
        file_name_layout = QtWidgets.QHBoxLayout()
        self.file_name_label = QtWidgets.QLabel("FileName:")
        self.file_name_text = QtWidgets.QLineEdit()
        file_name_layout.addWidget(self.file_name_label)
        file_name_layout.addWidget(self.file_name_text)
        self.main_layout.addLayout(file_name_layout)
        
        # Preset Path
        preset_path_layout = QtWidgets.QHBoxLayout()
        self.preset_path_radio = QtWidgets.QRadioButton("PRESET | Jmvs_ToolBox | DB | Folder")
        preset_path_layout.addWidget(self.preset_path_radio)
        self.main_layout.addLayout(preset_path_layout)

        # Folder Path
        folder_path_layout = QtWidgets.QHBoxLayout()
        self.folder_path_button = QtWidgets.QPushButton("Select Path")
        folder_path_layout.addWidget(self.folder_path_button)
        self.main_layout.addLayout(folder_path_layout)

        # Export Button
        export_layout = QtWidgets.QHBoxLayout()
        self.export_button = QtWidgets.QPushButton("Add/Connect DB")
        export_layout.addWidget(self.export_button)
        self.main_layout.addLayout(export_layout)
    '''
    
    def init_ui(self):
        main_Vlayout = QtWidgets.QVBoxLayout(self)
        #----------------------------------------------------------------------
        # -- FileName --
        layH_file_name = QtWidgets.QHBoxLayout()
        # layH_file_name.setContentsMargins(100, 0, 0, 0)

        self.fileName_lbl = QtWidgets.QLabel("FileName:")
        self.pefix_DB_lbl = QtWidgets.QLabel("'DB_")
        self.fileName_text = QtWidgets.QLineEdit()
        self.suffix_DB_lbl = QtWidgets.QLabel(".db'")

        # ADD HORIZONTAL WIDGETS
        layH_file_name.addWidget(self.fileName_lbl)
        layH_file_name.addWidget(self.pefix_DB_lbl)
        layH_file_name.addWidget(self.fileName_text)
        layH_file_name.addWidget(self.suffix_DB_lbl)
        main_Vlayout.addLayout(layH_file_name)
        
        # -- Preset Path --
        layH_presetPath = QtWidgets.QHBoxLayout()

        # label & rafio button
        self.layV_01_spacer = self.layV_SPACER_func()  # Vertical spacer 
        self.presetPath_lbl = QtWidgets.QLabel("Path:")
        self.presetPath_radioBtn = QtWidgets.QRadioButton("PRESET | Jmvs_ToolBox | DB | Folder") # Jmvs_tool_box\databases\geo_databases
        self.layV_02_spacer = self.layV_SPACER_func() 
        
        # ADD HORIZONTAL WIDGETS
        layH_presetPath.addLayout(self.layV_01_spacer)
        # layH_presetPath.addWidget(self.presetPath_lbl)
        layH_presetPath.addWidget(self.presetPath_radioBtn)
        layH_presetPath.addLayout(self.layV_02_spacer)
        main_Vlayout.addLayout(layH_presetPath)

        # -- Search Folder Path --
        layH_folderPath = QtWidgets.QHBoxLayout()

        # text &  button
        self.folderPath_text = QtWidgets.QPushButton("Select Path")
        self.folderPath_btn = QtWidgets.QPushButton("FLDR")
        self.folderPath_text.setObjectName("folderPath_text")
        self.folderPath_btn.setObjectName("folderPath_btn")
        
        # ADD HORIZONTAL WIDGETS
        layH_folderPath.addWidget(self.folderPath_text)
        layH_folderPath.addWidget(self.folderPath_btn)
        main_Vlayout.addLayout(layH_folderPath)

        # -- Spacer --
        layH_spacer = QtWidgets.QHBoxLayout()
        spacerH = QtWidgets.QWidget()
        spacerH.setFixedSize(420,10)
        spacerH.setObjectName("Spacer")
        layH_spacer.addWidget(spacerH)
        main_Vlayout.addLayout(layH_spacer)

        # -- EXPORT Button --
        layH_export = QtWidgets.QHBoxLayout()

        # label & rafio button
        self.export_btn = QtWidgets.QPushButton("Add/Connect DB")
        
        # ADD HORIZONTAL WIDGETS
        layH_export.addWidget(self.export_btn)
        main_Vlayout.addLayout(layH_export)

        #-------- STYLE SETTINGS --------
        for widget in [self.fileName_text, self.fileName_lbl, self.folderPath_text, self.presetPath_lbl]:
            widget.setProperty("DB_export_UI_01", True)

        for label_02 in [self.suffix_DB_lbl, self.pefix_DB_lbl]:
            label_02.setProperty("DB_export_UI_02", True)
        
        self.setLayout(main_Vlayout)