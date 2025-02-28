# main.py -> in a different file!
import importlib
from controllers.geoDB_controllers import export_database_controller 
from PySide6 import QtWidgets
importlib.reload(export_database_controller)

def export_db_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    controller = export_database_controller.ExportDatabaseController()
    controller.view.show()
    app.exec()
    # returning `controller.view` specifically becuase need to use 
    # 'databaseCreated' signal that's in the view
    return controller.view