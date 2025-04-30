# main.py -> in a different file!
import importlib
from controllers.geoDB_controllers import geo_db_controller 

# try:
#     from PySide6 import QtCore, QtWidgets, QtGui
#     from PySide6.QtCore import Qt
#     from PySide6.QtGui import QIcon
#     from PySide6.QtWidgets import (QWidget)
#     from shiboken6 import wrapInstance
# except ModuleNotFoundError:
#     from PySide2 import QtCore, QtWidgets, QtGui
#     from PySide2.QtCore import Qt
#     from PySide2.QtGui import QIcon
#     from PySide2.QtWidgets import (QWidget)
#     from shiboken2 import wrapInstance

importlib.reload(geo_db_controller)

def geo_db_main():
    # No ApplicationInstance becuase it is being handled through 'geo_db.py' already! 
    controller = geo_db_controller.GeometryDatabaseController()
    controller.view.show()

    return controller