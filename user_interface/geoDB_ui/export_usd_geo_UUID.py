
import maya.cmds as cmds
from maya import OpenMayaUI
from utils import utils_os

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

from utils import (
    utils
)

from usd_exports.systems import func_export_geometry_UUID_usd

importlib.reload(utils_os)
importlib.reload(utils)
importlib.reload(func_export_geometry_UUID_usd)

# For the time being, use this file to simply call the 'modular_char_ui.py'
maya_main_wndwPtr = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndwPtr), QWidget)

class exportUUIDusd(QtWidgets.QWidget):
    # define a signal to indicate completion of db creation
    def __init__(self, parent=None):
        super(exportUUIDusd, self).__init__(parent)
        version = "001"
        ui_object_name = f"EXPORT_UUID_usd{version}"
        ui_window_name = f"EXPORT UUID usd {version}"
        utils.delete_existing_ui(ui_object_name)
        self.setObjectName(ui_object_name)

        # Set flags & dimensions
        self.setParent(main_window)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(ui_window_name)
        self.resize(400, 100)
        
        stylesheet_path = os.path.join(
            utils_os.create_directory("Jmvs_tool_box", "assets", "styles"), 
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
        main_Vlayout.addLayout(layH_file_name)
        
        # -- Preset Path --
        layH_presetPath = QtWidgets.QHBoxLayout()

        # label & rafio button
        self.layV_01_spacer = self.layV_SPACER_func()  # Vertical spacer 
        self.presetPath_lbl = QtWidgets.QLabel("Path:")
        self.presetPath_radioBtn = QtWidgets.QRadioButton("Jmvs_ToolBox | USD_EXPORT | Folder") # Jmvs_tool_box\databases\geo_databases
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
        self.folderPath_text = QtWidgets.QPushButton("Select USD Path")
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
        self.export_btn = QtWidgets.QPushButton("EXPORT USD")
        
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
            self.directory = utils_os.create_directory("Jmvs_tool_box", "usd_exports", "geo_db_usd")
            print(f"database directory PRESET: {self.directory}")
            # self.directory = "C:\Docs\maya\scripts\Jmvs_tool_box\databases\geo_databases"
        else:
            print("radio button clicked OFF")
            self.folderPath_text.setText("Select Path")
            self.folderPath_text.setEnabled(True)


    def sigFunc_selectFolder(self):
        # Open a directory picker dialog
        if not self.val_presetPath_radioBtn:
            self.directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory", utils_os.create_directory("Jmvs_tool_box", "usd_exports"))
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
        # check if there is a valid selection
        shape_nodes = cmds.ls(sl=1, dag=1, type='mesh')
        if shape_nodes:
            print(shape_nodes)
            self.selected_objects = []
            for shape in shape_nodes:
                transform = cmds.listRelatives(shape, parent=1, type='transform')[0]
                self.selected_objects.append(transform)
            print(self.selected_objects)

            print(f"clicked to EXPORT selection for USD")
            prefix = "exp_uuid_"
            suffix = ""

            usd_name = f"{prefix}{self.val_fileName_text}{suffix}"
            json_name = f"{prefix}{self.val_fileName_text}{suffix}.json"
            
            # create a folder to go into this
            grp_dir = utils_os.create_directory(
                "Jmvs_tool_box", "usd_exports", "geo_db_usd", 
                f"{prefix}{self.val_fileName_text}{suffix}"
                )
            usd_save_dir = grp_dir
            json_dir = os.path.join(grp_dir, json_name)
            print(f"usd_name ={usd_name}, usd_save_dir = {usd_save_dir}, json_dir = {json_dir}")

            # run export function!
            func_export_geometry_UUID_usd.ExportGeometryUUID(
                selected_objects=self.selected_objects, 
                usd_name=usd_name, output_dir=usd_save_dir, 
                json_file_dir=json_dir
                )
        else:
            cmds.error(f"Select valid geometry!")

        
def export_UUID_usd_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    ui = exportUUIDusd()
    ui.show()
    app.exec()
    return ui