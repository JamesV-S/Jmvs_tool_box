# ----------------------------------- CONTROLLER ----------------------------------------
# controllers/export_database_controller.py
import importlib

try:
    from PySide6 import QtCore, QtWidgets, QtGui
except ModuleNotFoundError:
    from PySide2 import QtCore, QtWidgets, QtGui

from models.geoDB_models.export_database_model import exportDatabaseModel
from views.geoDB_views.export_database_view import exportDatabaseView
from systems import (
    os_custom_directory_utils
    )

importlib.reload(exportDatabaseModel)
importlib.reload(exportDatabaseView)

importlib.reload(os_custom_directory_utils)

class ExportDatabaseController:
    def __init__(self): # class
        self.model = exportDatabaseModel()
        self.view = exportDatabaseView()
        
        # Connect signals and slots
        self.view.file_name_text.textChanged.connect(self.sigFunc_update_file_name)
        self.view.preset_path_radio.clicked.connect(self.sigFunc_toggle_preset_path)
        self.view.folder_path_button.clicked.connect(self.sigFunc_select_folder)
        self.view.export_button.clicked.connect(self.sigFunc_export_database)


    def sigFunc_update_file_name(self, text):
        self.model.file_name = text
    

    def sigFunc_toggle_preset_path(self):
        if self.view.preset_path_radio.isChecked():
            directory = os_custom_directory_utils.create_directory(
                "Jmvs_tool_box", "databases", "geo_databases"
                )
            self.view.folder_path_button.setText(directory)
            self.view.folder_path_button.setEnabled(False)
            self.model.directory = directory
        else:
            self.view.folder_path_button.setText("Select Path")
            self.view.folder_path_button.setEnabled(True)


    def sigFunc_select_folder(self):
        if not self.view.preset_path_radio.isChecked():
            directory = QtWidgets.QFileDialog.getExistingDirectory(self.view, "Select Directory")
            if directory:
                self.view.folder_path_button.setText(directory)
                self.model.directory = directory


    def sigFunc_export_database(self):
        self.model.create_database()
        # Emit the signal to update the ComboBox function on the main geo ui (VIEW)
        self.view.databaseCreated.emit()

'''
def export_DB_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    ui = ExportDatabaseController()
    ui.show()
    app.exec()
    return ui
'''