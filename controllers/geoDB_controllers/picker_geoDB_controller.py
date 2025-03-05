# ----------------------------------- CONTROLLER ----------------------------------------
# controllers/Export_database_controller.py
import maya.cmds as cmds
import importlib
import os

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

from models.geoDB_models import picker_geoDB_model
from views.geoDB_views import picker_geoDB_view
from user_interface.geoDB_ui import geo_db

from main_entry_points.geoDB_mep import (
    import_geo_usd_main,
    export_geo_usd_main, 
    geo_db_main
)

importlib.reload(picker_geoDB_model)
importlib.reload(picker_geoDB_view)

importlib.reload(import_geo_usd_main)
importlib.reload(export_geo_usd_main)
importlib.reload(geo_db_main)
importlib.reload(geo_db)


class PickerGeometryDatabaseController:
    def __init__(self): # class
        print(f"Picker geoDB MVC controller")
        self.model = picker_geoDB_model.PickerGeometryDatabaseModel()
        self.view = picker_geoDB_view.PickerGeometryDatabaseView()
        
        self.view.export_usd_button.clicked.connect(self.sigFunc_export_usd_func)
        self.view.import_usd_button.clicked.connect(self.sigFunc_import_usd_func)
        self.view.geoDB_button.clicked.connect(self.sigFunc_geo_func)

        self.import_geo_usd_controller = None
        self.export_geo_usd_controller = None
        self.geo_db_controller = None


    def sigFunc_export_usd_func(self):
        print("loading export ui")
        self.export_geo_usd_controller = export_geo_usd_main.export_geo_usd_main()
        #delete_existing_ui(self.ui_object_name)

    
    def sigFunc_import_usd_func(self):
        print("loading import ui")
        self.import_geo_usd_controller = import_geo_usd_main.import_geo_usd_main()
        #delete_existing_ui(self.ui_object_name)


    def sigFunc_geo_func(self):
        print("loading geo uii")
        #self.geo_db_controller = geo_db_main.geo_db_main()
        geo_db.geoDB_main()
        # delete_existing_ui(self.ui_object_name)
    