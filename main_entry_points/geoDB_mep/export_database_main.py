# main.py -> in a different file!
import importlib
from controllers.geoDB_controllers import export_database_controller 

try:
    from PySide6 import QtCore, QtWidgets, QtGui
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import (QWidget)
    from shiboken6 import wrapInstance
except ModuleNotFoundError:
    from PySide2 import QtCore, QtWidgets, QtGui
    from PySide2.QtCore import Qt
    from PySide2.QtGui import QIcon
    from PySide2.QtWidgets import (QWidget)
    from shiboken2 import wrapInstance

importlib.reload(export_database_controller)

def export_db_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    controller = export_database_controller.exportDatabaseController()
    controller.view.show()
    app.exec()
    # returning `controller.view` specifically becuase need to use 
    # 'databaseCreated' signal that's in the view
    return controller.view