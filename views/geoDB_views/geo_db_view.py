# ----------------------------------------- VIEW ----------------------------------------

import importlib
from maya import OpenMayaUI
import os

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

from systems import (
    os_custom_directory_utils
)

from views import utils_view

importlib.reload(os_custom_directory_utils)
importlib.reload(utils_view)

maya_main_wndwPtr = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndwPtr), QWidget)

class GeometryDatabaseView(QtWidgets.QWidget):
    # define a signal to indicate completion of db creation
    # databaseCreated = Signal()
    def __init__(self, parent=None):
        super(GeometryDatabaseView, self).__init__(parent)
        version = "MVC"
        ui_object_name = f"JmvsGeoDatabase_{version}"
        ui_window_name = f"Jmvs_geo_database_{version}"
        utils_view.delete_existing_ui(ui_object_name)
        self.setObjectName(ui_object_name)

        # Set flags & dimensions
        self.setParent(main_window)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(ui_window_name)
        self.resize(400, 550)
        
        stylesheet_path = os.path.join(
            os_custom_directory_utils.create_directory("Jmvs_tool_box", "assets", "styles"), 
            "geoDB_style_sheet_001.css"
            )
        print(stylesheet_path)
        with open(stylesheet_path, "r") as file:
            stylesheet = file.read()
        self.setStyleSheet(stylesheet)
        
        self.directory_list = [os_custom_directory_utils.create_directory("Jmvs_tool_box", "databases", "geo_databases")]
        self.db_files = []
        for directory in self.directory_list:
             if os.path.exists(directory):
                 for db_file_name in os.listdir(directory):
                     if db_file_name.endswith('.db'):
                         self.db_files.append(db_file_name)
        self.init_ui()


    def init_ui(self):
        main_VLayout = QtWidgets.QVBoxLayout(self)
        main_VLayout.setObjectName("main_Layout")
        # 3 horizontal Layouts
        top_parent_HLayout = QtWidgets.QHBoxLayout() # 1
        mid_parent_HLayout = QtWidgets.QHBoxLayout() # 2
        bott_parent_HLayout = QtWidgets.QHBoxLayout() # 3

        main_VLayout.addLayout(top_parent_HLayout)
        main_VLayout.addLayout(mid_parent_HLayout)
        main_VLayout.addLayout(bott_parent_HLayout)
    
        #----------------------------------------------------------------------
        # 1
        #----------------------------------------------------------------------
        # ---- TREEVIEW data from database to visualise. ----
        
        # -- initialise models for each treeview --
        self.joint_model = QtGui.QStandardItemModel()
        self.joint_model.setColumnCount(1)
        self.geo_model = QtGui.QStandardItemModel()
        self.geo_model.setHeaderData(0, QtCore.Qt.Horizontal, "Geometry UUID")

        self.joint_tree_view = QtWidgets.QTreeView(self)
        self.joint_tree_view.setModel(self.joint_model)

        self.geo_tree_view = QtWidgets.QTreeView(self)
        self.geo_tree_view.setModel(self.geo_model)
        
        self.joint_tree_view.setObjectName("joint_tree_view")
        self.geo_tree_view.setObjectName("geo_tree_view")

        # -- treeView settings --
        header = self.geo_tree_view.header()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        # set the size of the two treesizess
        for tree_view in [self.joint_tree_view, self.geo_tree_view]:
            tree_view.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Maximum)
            tree_view.setMinimumSize(150, 400)
            tree_view.setHeaderHidden(True)
            tree_view.setAnimated(True)
            tree_view.setUniformRowHeights(True)
            tree_view.setEditTriggers(QtWidgets.QAbstractItemView.SelectedClicked)
        
        '''
        # expanding & collapsing
        self.joint_tree_view.setItemsExpandable(True)
        self.joint_tree_view.expandAll()
        self.joint_tree_view.setAllColumnsShowFocus(True)
        '''
    
        # -- Label tree views --
        joint_treeV_label_tree_layout = QtWidgets.QVBoxLayout()
        geo_treeV_label_tree_layout = QtWidgets.QVBoxLayout()
        
        jointTree_lbl = QtWidgets.QLabel("Joint UUIDs")
        geoTree_lbl = QtWidgets.QLabel("Geometry UUIDs")
        jointTree_lbl.setObjectName("jointTree_lbl")
        geoTree_lbl.setObjectName("geoTree_lbl")

        joint_treeV_label_tree_layout.addWidget(jointTree_lbl)
        geo_treeV_label_tree_layout.addWidget(geoTree_lbl)

        # -- add the 2 tree views to the tree Layout --
        tree_H_Layout = QtWidgets.QHBoxLayout()
        
        joint_treeV_label_tree_layout.addWidget(self.joint_tree_view)
        geo_treeV_label_tree_layout.addWidget(self.geo_tree_view)

        tree_H_Layout.addLayout(joint_treeV_label_tree_layout)
        tree_H_Layout.addLayout(geo_treeV_label_tree_layout)
        
        top_parent_HLayout.addLayout(tree_H_Layout)
        
        #----------------------------------------------------------------------
        # The Setting to the right of the Tree
        layV_TOP_R = QtWidgets.QVBoxLayout()
        #layV_TOP_R.setContentsMargins(0, 30, 0, 0)
        #layV_TOP_R.setSpacing(40)
        
        # -- Horizontal Spacer --
        layH_Spacer_0 = QtWidgets.QHBoxLayout()
        # Add the spacer QWidget
        spacerH_0 = QtWidgets.QWidget()
        spacerH_0.setFixedSize(350,10)
        spacerH_0.setObjectName("Spacer")
        layH_Spacer_0.addWidget(spacerH_0)
        layV_TOP_R.addLayout(layH_Spacer_0)
        layH_Spacer_0.setContentsMargins(0, 15, 0, 0)

        #---------------------
        # Add new Button & Export options
        layV_Add_DB = QtWidgets.QVBoxLayout()
        
        # -- Add New Database --
        layH_Add_New_DB = QtWidgets.QHBoxLayout()
        self.Add_new_DB_radioBtn = QtWidgets.QRadioButton("Add New Database | Options:")
        layH_Add_New_DB.addWidget(self.Add_new_DB_radioBtn)
        # -- Export Options button to call ui --
        self.exportOptions_btn = QtWidgets.QPushButton("+")
        self.exportOptions_btn.setEnabled(False)
        layH_Add_New_DB.addWidget(self.exportOptions_btn)
        
        # -- Horizontal Spacer --
        layH_Spacer_01 = QtWidgets.QHBoxLayout()
        # Add the spacer QWidget
        spacerH_01 = QtWidgets.QWidget()
        spacerH_01.setFixedSize(350,10)
        spacerH_01.setObjectName("Spacer")
        #spacerH_01 = QtWidgets.QSpacerItem(60, 15, QtWidgets.QSizePolicy.Maximum, 
        #                                   QtWidgets.QSizePolicy.Minimum)
        layH_Spacer_01.addWidget(spacerH_01)
        layH_Spacer_01.setContentsMargins(0, 15, 0, 0)

        layV_Add_DB.addLayout(layH_Add_New_DB)
        layV_Add_DB.addLayout(layH_Spacer_01)

        layV_TOP_R.addLayout(layV_Add_DB)

        #---------------------
        # Database dropDownBox Layout
        layV_dropDown_DB = QtWidgets.QVBoxLayout()

        # -- Databases path (add path's to location's the tool searches) -- 
        layH_Available_DB_path = QtWidgets.QHBoxLayout()
        #self.presetPath_checkBox = QtWidgets.QCheckBox("PRESET | Jmvs_ToolBox | DB | Folder")
        #self.presetPath_checkBox.setChecked(True)
        self.db_folder_path_btn = QtWidgets.QPushButton("Add DB Folder Path")
        self.db_folder_path_btn.setObjectName("folderPath_text")

        layH_Available_DB_path.addWidget(self.db_folder_path_btn)
        #layH_Available_DB_path.addWidget(self.presetPath_checkBox)
        
        layH_comboBox = QtWidgets.QHBoxLayout()
        self.database_comboBox = QtWidgets.QComboBox()
        self.database_comboBox.addItems(self.db_files)
        self.database_comboBox.setPlaceholderText("^Add Databases^")
        self.database_comboBox.model().sort(-1)
        # editing features of a QComboBox
        # self.database_comboBox.setMaxVisibleItems(1) # if 2, only 2 items at a time are shown, & adds a scrollbar
        ''' Lesson:
        #self.database_comboBox.setEditable(True) # user can type their own details
        self.database_comboBox.setCurrentIndex(0)# Set defualt selected item by index
        self.database_comboBox.insertItem(3, "George") # insert an item at a specific locaion
        #self.database_comboBox.removeItem(4) # Remove an item from by index (deleting db)
        #self.database_comboBox.clear()# clear all items from the ComboBox
        self.index_1 = self.database_comboBox.findText("Lis")# return the idex of a spceific item by text
        '''

        layH_comboBox.addWidget(self.database_comboBox)

        # -- Horizontal Spacer --
        layH_Spacer_02 = QtWidgets.QHBoxLayout()
        # Add the spacer QWidget
        spacerH_02 = QtWidgets.QWidget()
        spacerH_02.setFixedSize(350,10)
        spacerH_02.setObjectName("Spacer")
        layH_Spacer_02.addWidget(spacerH_02)
        layH_Spacer_02.setContentsMargins(0, 15, 0, 0)

        # layV_dropDown_DB.addLayout(layH_comboBox_Lbl)
        layV_dropDown_DB.addLayout(layH_Available_DB_path)
        layV_dropDown_DB.addLayout(layH_comboBox)
        layV_dropDown_DB.addLayout(layH_Spacer_02)

        layV_TOP_R.addLayout(layV_dropDown_DB)

        #---------------------
        # Skinning Buttons Layout
        skinning_grid_Layout = QtWidgets.QGridLayout()
        skinning_grid_Layout.setHorizontalSpacing(-1000)

        # -- Buttons --
        self.bind_skn_btn = QtWidgets.QPushButton("Bind Skin")
        self.unbind_skn_btn = QtWidgets.QPushButton("Unbind Skin")
        self.bind_all_btn = QtWidgets.QPushButton("Bind ALL")
        self.unbind_all_btn = QtWidgets.QPushButton("Unbind ALL")
        skinning_grid_Layout.addWidget(self.bind_skn_btn, 0,0)
        skinning_grid_Layout.addWidget(self.unbind_skn_btn, 0, 1)
        skinning_grid_Layout.addWidget(self.bind_all_btn, 1,0)
        skinning_grid_Layout.addWidget(self.unbind_all_btn, 1, 1)
    
        # add drop down db selector & skinning grid to `layV_TOP_R`
        layV_TOP_R.addLayout(skinning_grid_Layout)

        # -- Horizontal Spacer --
        layH_Spacer_03 = QtWidgets.QHBoxLayout()
        # Add the spacer QWidget
        spacerH_03 = QtWidgets.QWidget()
        spacerH_03.setFixedSize(350,10)
        spacerH_03.setObjectName("Spacer")
        layH_Spacer_03.addWidget(spacerH_03)
        layV_TOP_R.addLayout(layH_Spacer_03)
        layH_Spacer_03.setContentsMargins(0, 15, 0, 0)
        
        #---------------------
        # Delete Database Layout
        layH_delete_DB = QtWidgets.QHBoxLayout()
        
        # -- Delete Button --
        self.deleteDB_Btn = QtWidgets.QPushButton("(/)")
        self.deleteDB_Btn.setEnabled(False)

        # -- Delete Label --
        self.deleteDB_checkBox = QtWidgets.QCheckBox("Delete Databases:")
        self.deleteDB_checkBox.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.deleteDB_checkBox.setFixedSize(125, 30)
        
        layH_delete_DB.addWidget(self.deleteDB_checkBox)
        layH_delete_DB.addWidget(self.deleteDB_Btn)
        layV_TOP_R.addLayout(layH_delete_DB)

        # -------- Add All Widgets to Main Layout through its child --------
        top_parent_HLayout.addLayout(layV_TOP_R)

        # ---- STYLE SETTINGS ----
        bind_style = [self.bind_skn_btn, self.bind_all_btn, ]
        unbind_style = [self.unbind_skn_btn, self.unbind_all_btn]
        
        for bind_item, unbind_item in zip(bind_style, unbind_style):
            bind_item.setProperty("bind_style", True)
            unbind_item.setProperty("unbind_style", True)
        
        #----------------------------------------------------------------------
        # 2: update GEO & JOINT
        #----------------------------------------------------------------------
        self.new_relationship_checkBox = QtWidgets.QCheckBox("New Relationship +")
        self.new_relationship_checkBox.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.new_relationship_checkBox.setFixedSize(125, 30)
        self.new_jnt_btn = QtWidgets.QPushButton("New JOINT")
        self.new_jnt_btn.setEnabled(False)
        self.add_geo_btn = QtWidgets.QPushButton("Add GEO")
        self.add_geo_btn.setEnabled(True)

        self.add_jnt_btn = QtWidgets.QPushButton("Add JOINT")
        self.add_jnt_btn.setEnabled(True)

        mid_parent_HLayout.addWidget(self.new_relationship_checkBox)
        mid_parent_HLayout.addWidget(self.new_jnt_btn)
        mid_parent_HLayout.addWidget(self.add_geo_btn)
        mid_parent_HLayout.addWidget(self.add_jnt_btn)

        #----------------------------------------------------------------------
        # 3 replacing JOINT & GEO of selection!
        #----------------------------------------------------------------------
        self.rmv_rShip_checkBox = QtWidgets.QCheckBox("RMV RelationShip -")
        self.rmv_rShip_checkBox.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.rmv_rShip_checkBox.setFixedSize(125, 30)
        
        self.remove_relationship_btn = QtWidgets.QPushButton("Remove Relationship")
        self.rmv_geo_btn = QtWidgets.QPushButton("Remove GEOMETRY")
        self.rmv_jnt_btn = QtWidgets.QPushButton("Remove JOINT")
        
        special_true = [self.add_geo_btn, self.rmv_geo_btn]  
        for item in special_true:
            item.setProperty("geoButtons", True)
        self.remove_relationship_btn.setEnabled(False)
        
        bott_parent_HLayout.addWidget(self.rmv_rShip_checkBox)
        bott_parent_HLayout.addWidget(self.remove_relationship_btn)
        bott_parent_HLayout.addWidget(self.rmv_geo_btn)
        bott_parent_HLayout.addWidget(self.rmv_jnt_btn)
        
        #----------------------------------------------------------------------
        # ---- TOOL TIPS ----
        self.bind_skn_btn.setToolTip("Bind Geo to Joint SELECTION")
        self.unbind_skn_btn.setToolTip("Unind Geo to Joint SELECTION")
        self.bind_all_btn.setToolTip("Bind ALL Geo to Joint")
        self.unbind_all_btn.setToolTip("Unbind ALL Geo to Joint")
        self.add_jnt_btn.setToolTip("Select Existing Joint in TreeView FIRST")
        #----------------------------------------------------------------------
        
        self.setLayout(main_VLayout)