# ------------------------------ MODEL ----------------------------------------
import maya.cmds as cmds
import importlib
import os.path

try:
    from PySide6 import QtCore, QtWidgets, QtGui, QtUiTools
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon, QStandardItemModel, QStandardItem
    from PySide6.QtWidgets import (QWidget)
    from shiboken6 import wrapInstance
except ModuleNotFoundError:
    from PySide2 import QtCore, QtWidgets, QtGui, QtUiTools
    from PySide2.QtCore import Qt
    from PySide2.QtGui import QIcon
    from PySide2.QtWidgets import (QWidget)
    from shiboken2 import wrapInstance

from systems import (
    os_custom_directory_utils,
    utils
)

from databases.geo_databases import database_schema_001

importlib.reload(database_schema_001)

class GeoDbMasterModel:
    def __init__(self):
        pass


    
    


    
    
        
    