# main.py -> in a different file!
from controllers.geoDB_controllers.export_database_controller import ExportDatabaseController
from PySide6 import QtWidgets

def export_db_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    controller = ExportDatabaseController()
    controller.view.show()
    app.exec()
    # returning `controller.view` specifically becuase need to use 
    # 'databaseCreated' signal that's in the view
    return controller.view