# ----------------------------------- CONTROLLER ----------------------------------------
# controllers/Export_database_controller.py
import importlib

try:
    from PySide6 import QtCore, QtWidgets, QtGui
except ModuleNotFoundError:
    from PySide2 import QtCore, QtWidgets, QtGui

from models.geoDB_models import export_database_model
from views.geoDB_views import export_database_view
from utils import (
    utils_os
    )

importlib.reload(export_database_model)
importlib.reload(export_database_view)

importlib.reload(utils_os)

class ExportDatabaseController:
    def __init__(self): # class
        self.model = export_database_model.exportDatabaseModel()
        self.view = export_database_view.exportDatabaseView()
        
        print(f"Export DB CONTROLLER")

        # Connect signals and slots
        self.view.fileName_text.textChanged.connect(self.sigFunc_fileName)
        self.view.presetPath_radioBtn.clicked.connect(self.sigFunc_presetPath_radioBtn)
        self.view.folderPath_text.clicked.connect(self.sigFunc_selectFolder)
        self.view.export_btn.clicked.connect(self.sigFunc_export_database)
        
        print(f"Export DB CONTROLLER after")

    def sigFunc_fileName(self, text):
        # print("fileName text triggured")
        ''''''
        # Model has the file name now. 
        self.model.file_name = str(self.view.fileName_text.text())
        print(f"FileName = `{self.model.file_name}`")
        ''''''

    def sigFunc_presetPath_radioBtn(self):
        # print("radioBtn triggured")
        ''''''
        if self.view.presetPath_radioBtn.isChecked():
            print("radio button clicked ON")
            self.view.folderPath_text.setText("...\\Jmvs_ToolBox\\databases\\geo_databases")
            self.view.folderPath_text.setEnabled(False)
            # gather the directory rather than just writing it. 
            self.directory = utils_os.create_directory("Jmvs_tool_box", "databases", "geo_databases")
            print(f"database directory PRESET: {self.directory}")
            # self.directory = "C:\Docs\maya\scripts\Jmvs_tool_box\databases\geo_databases"
        else:
            print("radio button clicked OFF")
            self.view.folderPath_text.setText("Select Path")
            self.view.folderPath_text.setEnabled(True)
        ''''''

    def sigFunc_selectFolder(self):
        # print("selectFolder triggured")
        ''''''
        if not self.view.presetPath_radioBtn.isChecked():
            directory = QtWidgets.QFileDialog.getExistingDirectory(self.view, "Select Directory")
            if directory:
                self.view.folderPath_text.setText(directory)
                self.model.directory = directory
        ''''''

    def sigFunc_export_database(self):
        # print("export_databas triggured")
        ''''''
        self.model.create_database()
        # Emit the signal to update the ComboBox function on the main geo ui (VIEW)
        self.view.databaseCreated.emit()
        ''''''