# -------------------------------------- MODEL ------------------------------------------
# models/database_model.py
from databases.geo_databases import database_schema_001

class exportDatabaseModel:
    def __init__(self):
        self.file_name = ""
        self.directory = ""

    def create_database(self):
        database_schema_001.CreateDatabase(name=self.file_name, directory=self.directory)


# ----------------------------------------- VIEW ----------------------------------------
# views/export_database_view.py
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Signal, Qt
import os

class ExportDatabaseView(QtWidgets.QWidget):
    databaseCreated = Signal()

    def __init__(self, parent=None):
        super(ExportDatabaseView, self).__init__(parent)
        self.setObjectName("DB_EXPORT001")
        self.setWindowTitle("DB Export Options 001")
        self.resize(400, 100)
        
        # Load stylesheet
        stylesheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "CSS", "geoDB_style_sheet_001.css")
        with open(stylesheet_path, "r") as file:
            stylesheet = file.read()
        self.setStyleSheet(stylesheet)

        self.init_ui()
    
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

# ----------------------------------- CONTROLLER ----------------------------------------
# controllers/export_database_controller.py
from models.database_model import exportDatabaseModel
from views.export_database_view import ExportDatabaseView
from systems import os_custom_directory_utils

class ExportDatabaseController:
    def __init__(self): # class
        self.model = exportDatabaseModel()
        self.view = ExportDatabaseView()
        
        # Connect signals and slots
        self.view.file_name_text.textChanged.connect(self.sigFunc_update_file_name)
        self.view.preset_path_radio.clicked.connect(self.sigFunc_toggle_preset_path)
        self.view.folder_path_button.clicked.connect(self.sigFunc_select_folder)
        self.view.export_button.clicked.connect(self.sigFunc_export_database)

    def sigFunc_update_file_name(self, text):
        self.model.file_name = text
    
    def sigFunc_toggle_preset_path(self):
        if self.view.preset_path_radio.isChecked():
            directory = os_custom_directory_utils.create_directory("Jmvs_tool_box", "databases", "geo_databases")
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
        self.view.databaseCreated.emit()
# - - - - - - - - - - - - - - - - - - - - - 
def export_db_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    controller = ExportDatabaseController()
    controller.view.show()
    app.exec()
# - - - - - - -  - OR - - - - - - - - - - -
# main.py -> in a different file!
from controllers.export_database_controller import ExportDatabaseController
from PySide6 import QtWidgets

def export_db_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    controller = ExportDatabaseController()
    controller.view.show()
    app.exec()
# - - - - - - - - - - - - - - - - - - - - - 




