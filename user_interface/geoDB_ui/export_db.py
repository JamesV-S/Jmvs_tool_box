
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

from databases.geo_databases import database_schema_001
importlib.reload(database_schema_001)

from systems import (
    os_custom_directory_utils
)
importlib.reload(os_custom_directory_utils)

# For the time being, use this file to simply call the 'modular_char_ui.py'
maya_main_wndwPtr = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndwPtr), QWidget)

def delete_existing_ui(ui_name):
    if cmds.window(ui_name, exists=True):
        cmds.deleteUI(ui_name, window=True)

class exportDatabaseOptions(QtWidgets.QWidget):
    # define a signal to indicate completion of db creation
    databaseCreated = Signal()
    def __init__(self, parent=None):
        super(exportDatabaseOptions, self).__init__(parent)
        version = "001"
        ui_object_name = f"DB_EXPORT{version}"
        ui_window_name = f"DB Export Options {version}"
        delete_existing_ui(ui_object_name)
        self.setObjectName(ui_object_name)

        # Set flags & dimensions
        self.setParent(main_window)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(ui_window_name)
        self.resize(400, 100)
        
        stylesheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                       "..", "CSS", "geoDB_style_sheet_001.css")
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
            self.folderPath_text.setText("...\\Jmvs_ToolBox\\databases\\geo_databases")
            self.folderPath_text.setEnabled(False)
            # gather the directory rather than just writing it. 
            self.directory = os_custom_directory_utils.create_directory("Jmvs_tool_box", "databases", "geo_databases")
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
            self, "Select Directory", os_custom_directory_utils.create_directory("Jmvs_tool_box", "databases", "geo_databases"))
        if self.directory:
            self.folderPath_text.setText(self.directory)
            print(f"Selected Directory: {self.directory}")
        print(f"directory :: `{self.directory}`") 


    def layV_SPACER_func(self):
        layV_spacer = QtWidgets.QHBoxLayout()
        spacer = QtWidgets.QWidget()
        spacer.setFixedSize(100,10)
        spacer.setObjectName("Spacer")
        layV_spacer.addWidget(spacer)

        return layV_spacer
    

    def sigFunc_export(self):
        print(f"Creating geometry database!")
        database_schema_001.CreateDatabase(name=self.val_fileName_text, directory=self.directory)
        # Emit the signal to update the ComboBox function on the main geo ui
        self.databaseCreated.emit()
        

def export_DB_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    ui = exportDatabaseOptions()
    ui.show()
    app.exec()
    return ui