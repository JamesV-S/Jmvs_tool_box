
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

import sys
import importlib
import os.path

from systems import (
    os_custom_directory_utils,
    utils
)

from usd_exports.systems import func_import_geometry_UUID_usd

importlib.reload(os_custom_directory_utils)
importlib.reload(utils)
importlib.reload(func_import_geometry_UUID_usd)

# For the time being, use this file to simply call the 'modular_char_ui.py'
maya_main_wndwPtr = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndwPtr), QWidget)

class imnportDatabaseOptions(QtWidgets.QWidget):
    # define a signal to indicate completion of db creation
    databaseCreated = Signal()
    def __init__(self, parent=None):
        super(imnportDatabaseOptions, self).__init__(parent)
        version = "001"
        ui_object_name = f"USD_uuid_Import{version}"
        ui_window_name = f"USD uuid Import {version}"
        utils.delete_existing_ui(ui_object_name)
        self.setObjectName(ui_object_name)

        # Set flags & dimensions
        self.setParent(main_window)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(ui_window_name)
        self.resize(200, 100)
        
        stylesheet_path = os.path.join(
            os_custom_directory_utils.create_directory("Jmvs_tool_box", "assets", "styles"), 
            "geoDB_style_sheet_001.css"
            )
        with open(stylesheet_path, "r") as file:
            stylesheet = file.read()
        self.setStyleSheet(stylesheet)

        self.val_presetPath_radioBtn = False

        self.UI()
        self.UI_connect_signals()


    def UI(self):
        
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
        self.layV_01_spacer = self.layV_SPACER_func()  # Vertical spacer 
        self.presetPath_lbl = QtWidgets.QLabel("| USD & JSON |")
        self.presetPath_radioBtn = QtWidgets.QRadioButton("Jmvs_ToolBox | USD | Folder") # Jmvs_tool_box\databases\geo_databases
        self.layV_02_spacer = self.layV_SPACER_func()
        
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
    
    
    def UI_connect_signals(self):
        # -- FileName --
        self.fileName_text.textChanged.connect(self.sigFunc_fileName)
        # -- Preset Path --
        self.presetPath_radioBtn.clicked.connect(self.sigFunc_presetPath_radioBtn)
        # -- Search Folder Path --
        self.folderPath_text.clicked.connect(self.sigFunc_selectFolder)
        # -- EXPORT Button --
        self.export_btn.clicked.connect(self.sigFunc_export)
    

    def sigFunc_fileName(self):
        self.val_fileName_text = str(self.fileName_text.text())
        print(f"FileName = `{self.val_fileName_text}`")
        return self.val_fileName_text


    def sigFunc_presetPath_radioBtn(self):
        self.val_presetPath_radioBtn = self.presetPath_radioBtn.isChecked()
        if self.val_presetPath_radioBtn:
            print("radio button clicked ON")
            self.folderPath_text.setText("...\\Jmvs_ToolBox\\usd_exports\\geo_db_usd")
            self.folderPath_text.setEnabled(False)
            # gather the directory rather than just writing it. 
            self.directory = os_custom_directory_utils.create_directory("Jmvs_tool_box", "usd_exports", "geo_db_usd")
            print(f"database directory PRESET: {self.directory}")
            # self.directory = "C:\Docs\maya\scripts\Jmvs_tool_box\databases\geo_databases"
        else:
            print("radio button clicked OFF")
            self.folderPath_text.setText("Select Path")
            self.folderPath_text.setEnabled(True)


    def sigFunc_selectFolder(self):
        # Open a directory picker dialog
        self.directory = QtWidgets.QFileDialog.getExistingDirectory(
        self, "Select Directory", os_custom_directory_utils.create_directory("Jmvs_tool_box", "usd_exports", "geo_db_usd"))
        # C:\Docs\maya\scripts\Jmvs_tool_box\usd_exports\geo_db_usd
        if self.directory:
            self.folderPath_text.setText(self.directory)
            print(f"Selected Directory: {self.directory}")
        print(f"directory :: `{self.directory}`")


    def layV_SPACER_func(self):
        layH_spacer = QtWidgets.QHBoxLayout()
        spacer = QtWidgets.QWidget()
        spacer.setFixedSize(100,10)
        spacer.setObjectName("Spacer")
        layH_spacer.addWidget(spacer)

        return layH_spacer
    

    def sigFunc_export(self):
        prefix = "exp_uuid_"
        
        #try:
        print(f"self.directory = {self.directory}")

        grp_name = self.directory.split('/')[-1]
        print(f"GRP_NAME = {grp_name}")

        if prefix in grp_name:
            usd_name = f"{grp_name}.usd"
            json_name = f"{grp_name}.json"

            # create a folder to go into this                                                                   exp_uuid_geo_shapes_001
            # grp_dir = os_custom_directory_utils.create_directory("Jmvs_tool_box", "usd_exports", "geo_db_usd", f"{prefix}{self.val_fileName_text}{suffix}")
            usd_save_dir = os.path.join(self.directory, usd_name)
            json_dir = os.path.join(self.directory, json_name)
            print(f"usd_name ={usd_name}, usd_save_dir = {usd_save_dir}, json_dir = {json_dir}")

            # run export function!
            func_import_geometry_UUID_usd.ImporttGeometryUUID(usd_file=usd_save_dir, json_file=json_dir)
        else:
            cmds.error("CHOOSE A VALID GROUP PATH!")

def import_UUID_usd_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    ui = imnportDatabaseOptions()
    ui.show()
    app.exec()
    return ui