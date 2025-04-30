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

class ImportGeoUsdView(QtWidgets.QWidget):
    # define a signal to indicate completion of db creation
    # databaseCreated = Signal()
    def __init__(self, parent=None):
        super(ImportGeoUsdView, self).__init__(parent)
        version = "MVC"
        ui_object_name = f"USD_uuid_Import{version}"
        ui_window_name = f"USD uuid Import {version}"
        utils_view.delete_existing_ui(ui_object_name)
        self.setObjectName(ui_object_name)

        # Set flags & dimensions
        self.setParent(main_window)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(ui_window_name)
        self.resize(200, 100)
        
        stylesheet_path = os.path.join(
            utils_os.create_directory("Jmvs_tool_box", "assets", "styles"), 
            "geoDB_style_sheet_001.css"
            )
        with open(stylesheet_path, "r") as file:
            stylesheet = file.read()
        self.setStyleSheet(stylesheet)

        self.val_presetPath_radioBtn = False

        self.init_ui()


    def init_ui(self):
        main_Vlayout = QtWidgets.QVBoxLayout(self)
        #----------------------------------------------------------------------
        # -- FileName --
        layH_file_name = QtWidgets.QHBoxLayout()
        # layH_file_name.setContentsMargins(100, 0, 0, 0)

        self.fileName_lbl = QtWidgets.QLabel("USD Folder:")
        self.pefix_DB_lbl = QtWidgets.QLabel("'exp_uuid_")
        self.fileName_text = QtWidgets.QLineEdit()
        self.suffix_DB_lbl = QtWidgets.QLabel("_###.usd'")
        # UUID_name_Export_001.usd

        # ADD HORIZONTAL WIDGETS
        layH_file_name.addWidget(self.fileName_lbl)
        layH_file_name.addWidget(self.pefix_DB_lbl)
        layH_file_name.addWidget(self.fileName_text)
        layH_file_name.addWidget(self.suffix_DB_lbl)
        # main_Vlayout.addLayout(layH_file_name)
        
        # -- Preset Path --
        layH_presetPath = QtWidgets.QHBoxLayout()

        # label & rafio button
        self.layV_01_spacer = utils_view.layV_SPACER_func()  # Vertical spacer 
        self.presetPath_lbl = QtWidgets.QLabel("| USD & JSON |")
        self.presetPath_radioBtn = QtWidgets.QRadioButton("Jmvs_ToolBox | USD | Folder") # Jmvs_tool_box\databases\geo_databases
        self.layV_02_spacer = utils_view.layV_SPACER_func()
        
        # ADD HORIZONTAL WIDGETS
        layH_presetPath.addLayout(self.layV_01_spacer)
        layH_presetPath.addWidget(self.presetPath_lbl)
        #layH_presetPath.addWidget(self.presetPath_radioBtn)
        layH_presetPath.addLayout(self.layV_02_spacer)
        main_Vlayout.addLayout(layH_presetPath)

        # -- Search Folder Path --
        layH_folderPath = QtWidgets.QHBoxLayout()

        # text &  button
        self.folderPath_text = QtWidgets.QPushButton("Select USD Path")
        self.folderPath_btn = QtWidgets.QPushButton("FLDR")
        self.folderPath_text.setObjectName("folderPath_text")
        self.folderPath_btn.setObjectName("folderPath_btn")
        
        # ADD HORIZONTAL WIDGETS
        layH_folderPath.addWidget(self.folderPath_text)
        # layH_folderPath.addWidget(self.folderPath_btn)
        main_Vlayout.addLayout(layH_folderPath)

        # -- Spacer --
        layH_spacer = QtWidgets.QHBoxLayout()
        spacerH = QtWidgets.QWidget()
        spacerH.setFixedSize(300,10)
        spacerH.setObjectName("Spacer")
        layH_spacer.addWidget(spacerH)
        main_Vlayout.addLayout(layH_spacer)

        # -- EXPORT Button --
        layH_export = QtWidgets.QHBoxLayout()

        # label & rafio button
        self.export_btn = QtWidgets.QPushButton("IMPORT GEO USD")
        
        # ADD HORIZONTAL WIDGETS
        layH_export.addWidget(self.export_btn)
        main_Vlayout.addLayout(layH_export)

        #-------- STYLE SETTINGS --------
        for widget in [self.fileName_text, self.fileName_lbl, self.folderPath_text, self.presetPath_lbl]:
            widget.setProperty("DB_export_UI_01", True)

        for label_02 in [self.suffix_DB_lbl, self.pefix_DB_lbl]:
            label_02.setProperty("DB_export_UI_02", True)
        
        self.setLayout(main_Vlayout)