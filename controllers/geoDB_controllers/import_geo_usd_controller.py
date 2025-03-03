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

from models.geoDB_models import import_geo_usd_model
from views.geoDB_views import import_geo_usd_view

importlib.reload(os_custom_directory_utils)
importlib.reload(utils)
importlib.reload(import_geo_usd_model)
importlib.reload(import_geo_usd_view)

class ImportGeoUsdController:
    def __init__(self): # class
        self.model = import_geo_usd_model.ImportGeoUsdModel()
        self.view = import_geo_usd_view.ImportGeoUsdView()
        
        print(f"Export DB CONTROLLER")

        # Connect signals and slots
        # -- FileName --
        self.view.fileName_text.textChanged.connect(self.sigFunc_fileName)
        # -- Preset Path --
        self.view.presetPath_radioBtn.clicked.connect(self.sigFunc_presetPath_radioBtn)
        # -- Search Folder Path --
        self.view.folderPath_text.clicked.connect(self.sigFunc_selectFolder)
        # -- EXPORT Button --
        self.view.export_btn.clicked.connect(self.sigFunc_export)
        
        print(f"Export DB CONTROLLER after")


    def sigFunc_fileName(self):
        self.val_fileName_text = str(self.view.fileName_text.text())
        print(f"FileName = `{self.val_fileName_text}`")
        return self.val_fileName_text


    def sigFunc_presetPath_radioBtn(self):
        self.val_presetPath_radioBtn = self.view.presetPath_radioBtn.isChecked()
        if self.val_presetPath_radioBtn:
            print("radio button clicked ON")
            self.view.folderPath_text.setText("...\\Jmvs_ToolBox\\usd_exports\\geo_db_usd")
            self.view.folderPath_text.setEnabled(False)
            # gather the directory rather than just writing it. 
            self.directory = os_custom_directory_utils.create_directory("Jmvs_tool_box", "usd_exports", "geo_db_usd")
            print(f"database directory PRESET: {self.directory}")
            # self.directory = "C:\Docs\maya\scripts\Jmvs_tool_box\databases\geo_databases"
        else:
            print("radio button clicked OFF")
            self.view.folderPath_text.setText("Select Path")
            self.view.folderPath_text.setEnabled(True)


    def sigFunc_selectFolder(self):
        # Open a directory picker dialog
        self.directory = QtWidgets.QFileDialog.getExistingDirectory(
        self, "Select Directory", os_custom_directory_utils.create_directory("Jmvs_tool_box", "usd_exports", "geo_db_usd"))
        # C:\Docs\maya\scripts\Jmvs_tool_box\usd_exports\geo_db_usd
        if self.directory:
            self.view.folderPath_text.setText(self.directory)
            print(f"Selected Directory: {self.directory}")
        print(f"directory :: `{self.directory}`")
    

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
            self.model.usd_file = os.path.join(self.directory, usd_name)
            self.model.json_directory = os.path.join(self.directory, json_name)
            print(f"usd_name ={usd_name}, usd_save_dir = {self.model.usd_file}, json_dir = {self.model.json_directory}")

            # run export function!
            self.model.import_geo_uuid()#usd_file=self.model.usd_file, json_file=self.model.json_directory)
        else:
            cmds.error("CHOOSE A VALID GROUP PATH!")