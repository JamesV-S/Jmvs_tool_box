# ------------------------------ CONTROLLER -----------------------------------

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

import importlib
import os.path
from utils import (
    utils
)
from models.geoDB_models import export_geo_usd_model
from views.geoDB_views import export_geo_usd_view

importlib.reload(utils_os)
importlib.reload(utils)
importlib.reload(export_geo_usd_model)
importlib.reload(export_geo_usd_view)

class ExportGeoUsdController:
    def __init__(self): # class
        self.model = export_geo_usd_model.ExportGeoUsdModel()
        self.view = export_geo_usd_view.ExportGeoUsdView()

        # Connect signals and slots
        # -- FileName --
        self.view.fileName_text.textChanged.connect(self.sigFunc_fileName)
        # -- Preset Path --
        self.view.presetPath_radioBtn.clicked.connect(self.sigFunc_presetPath_radioBtn)
        # -- Search Folder Path --
        self.view.folderPath_text.clicked.connect(self.sigFunc_selectFolder)
        # -- EXPORT Button --
        self.view.export_btn.clicked.connect(self.sigFunc_export)
        
        self.val_presetPath_radioBtn = None


    def sigFunc_fileName(self):
        self.val_fileName_text = str(self.view.fileName_text.text())
        return self.val_fileName_text


    def sigFunc_presetPath_radioBtn(self):
        self.val_presetPath_radioBtn = self.view.presetPath_radioBtn.isChecked()
        if self.val_presetPath_radioBtn:
            self.view.folderPath_text.setText("...\\Jmvs_ToolBox\\usd_exports\\geo_db_usd")
            self.view.folderPath_text.setEnabled(False)
            # gather the directory rather than just writing it. 
            self.directory = utils_os.create_directory("Jmvs_tool_box", "usd_exports", "geo_db_usd")
            print(f"database directory PRESET: {self.directory}")
            # self.directory = "C:\Docs\maya\scripts\Jmvs_tool_box\databases\geo_databases"
        else:
            self.view.folderPath_text.setText("Select Path")
            self.view.folderPath_text.setEnabled(True)


    def sigFunc_selectFolder(self):
        # Open a directory picker dialog
        if not self.val_presetPath_radioBtn:
            self.directory = QtWidgets.QFileDialog.getExistingDirectory(
            parent=self.view,  # Assuming self.view is a QWidget
            caption="Select Directory",
            dir=utils_os.create_directory("Jmvs_tool_box", "usd_exports", "geo_db_usd")
        )
        if self.directory:
            self.view.folderPath_text.setText(self.directory)


    def sigFunc_export(self):
        # check if there is a valid selection
        shape_nodes = cmds.ls(sl=1, dag=1, type='mesh')
        if shape_nodes:
            print(shape_nodes)
            self.model.selected_objects = []
            for shape in shape_nodes:
                transform = cmds.listRelatives(shape, parent=1, type='transform')[0]
                self.model.selected_objects.append(transform)
            print(self.model.selected_objects)

            prefix = "exp_uuid_"
            suffix = ""

            self.model.usd_name = f"{prefix}{self.val_fileName_text}{suffix}"
            json_name = f"{prefix}{self.val_fileName_text}{suffix}.json"
            
            # create a folder to go into this
            grp_dir = utils_os.create_directory(
                "Jmvs_tool_box", "usd_exports", "geo_db_usd", 
                f"{prefix}{self.val_fileName_text}{suffix}"
                )
            self.model.usd_save_dir = grp_dir
            self.model.json_dir = os.path.join(grp_dir, json_name)
            print(f"self.model.usd_name ={self.model.usd_name}, self.model.usd_save_dir = {self.model.usd_save_dir}, self.model.json_dir = {self.model.json_dir}")

            # run export function!
            self.model.export_geo_uuid()
        else:
            cmds.error(f"Select valid geometry!")