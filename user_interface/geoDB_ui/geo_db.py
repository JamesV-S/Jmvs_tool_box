
import maya.cmds as cmds
from maya import OpenMayaUI

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

import sys
import importlib
import os

from databases import database_manager
from databases.geo_databases import database_schema_001
from controllers.geoDB_controllers import export_database_controller 

from user_interface.geoDB_ui import export_db


from systems import (
    os_custom_directory_utils,
    utils
)
from systems.sys_geoDB import (
    uuid_handler, 
    bind_skin,
    unbind_skin
)

importlib.reload(export_database_controller)
importlib.reload(database_manager)
importlib.reload(database_schema_001)
importlib.reload(export_db)
importlib.reload(os_custom_directory_utils)
importlib.reload(utils)
importlib.reload(uuid_handler)
importlib.reload(bind_skin)
importlib.reload(unbind_skin)


# For the time being, use this file to simply call the 'modular_char_ui.py'
maya_main_wndwPtr = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndwPtr), QWidget)

class GeoDatabase(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(GeoDatabase, self).__init__(parent)
        version = "001"
        ui_object_name = f"JmvsGeoDatabase_{version}"
        ui_window_name = f"Jmvs_geo_database_{version}"
        utils.delete_existing_ui(ui_object_name)
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

        # gather available database file names & pass to the ComboBox
        self.directory_list = [os_custom_directory_utils.create_directory("Jmvs_tool_box", "databases", "geo_databases")]
        self.db_files = []
        for directory in self.directory_list:
            if os.path.exists(directory):
                for db_file_name in os.listdir(directory):
                    if db_file_name.endswith('.db'):
                        self.db_files.append(db_file_name)
        
        self.custom_uuid_attr = "custom_UUID"
        self.UI()
        self.UI_connect_signals()
        self.val_new_relationship_checkBox = 0
        self.active_db = self.database_comboBox.currentText()
        self.visualise_active_db()

        self.export_db_controller = None


    def update_database_ComboBox(self):
        print(f"UPDATING DB COMBO BOX WITH NEW database!")
        self.db_files_update = []
        for directory in self.directory_list:
            if os.path.exists(directory):
                for db_file_name in os.listdir(directory):
                    if db_file_name.endswith('.db'):
                        self.db_files_update.append(db_file_name)
        self.database_comboBox.clear()
        self.database_comboBox.addItems(self.db_files_update)
        self.database_comboBox.setPlaceholderText("Updated Databases Added")

    
    def create_item(text, checkable=False):
        item = QStandardItem(text)
        if checkable:
            item.setCheckable(True)
        return item


    def UI(self):
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
    
        # Connect the selection change on joint tree to effect geo tree. 
        self.joint_tree_view.selectionModel().selectionChanged.connect(self.signal_to_geo_tree_highlight)
        self.joint_tree_view.selectionModel().selectionChanged.connect(self.ui_joint_selects_scene_joint)
        self.geo_tree_view.selectionModel().selectionChanged.connect(self.ui_geo_selects_scene_geo)
        
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
    
    
    def UI_connect_signals(self):
        ########## UI CONNECTIONS : 1 : ##########
        # -------- Tree views --------
        self.geo_model.itemChanged.connect(self.sigfunc_on_geoTree_item_change)

        # -------- Options to the right of treer --------
        # -- Add Database options --
        self.Add_new_DB_radioBtn.clicked.connect(self.sigFunc_addNewDB_radioBtn)
        self.exportOptions_btn.clicked.connect(self.sigFunc_exportOptions_btn)

        # -- Available database options --
        self.db_folder_path_btn.clicked.connect(self.sigFunc_dbFolderPath_btn)
        self.database_comboBox.currentIndexChanged.connect(self.sigFunc_database_comboBox)

        # -- Skinning options --
        self.bind_skn_btn.clicked.connect(self.sigFunc_bind_skn_btn)
        self.unbind_skn_btn.clicked.connect(self.sigFunc_unbind_skn_btn)
        self.bind_all_btn.clicked.connect(self.sigFunc_bind_all_btn)
        self.unbind_all_btn.clicked.connect(self.sigFunc_unbind_all_btn)

        # -- Delete database options --
        self.deleteDB_checkBox.stateChanged.connect(self.sigFunc_deleteDB_checkBox)
        ########## UI CONNECTIONS : 2 : ##########
        # -- add JOINT/GEO & update relationship btns --
        self.new_relationship_checkBox.stateChanged.connect(self.sigFunc_new_relationship_checkBox)
        self.new_jnt_btn.clicked.connect(self.sigFunc_add_joint_to_db_btn)
        self.add_geo_btn.clicked.connect(self.sigFunc_add_geo_to_db_btn)
        self.add_jnt_btn.clicked.connect(self.sigFunc_add_jnt_to_db_btn)

        # -- Remove JOINT/GEO --
        self.rmv_rShip_checkBox.stateChanged.connect(self.sigFunc_rmv_rShip_checkBox)
        self.rmv_jnt_btn.clicked.connect(self.sigFunc_rmv_jnt_btn)
        self.rmv_geo_btn.clicked.connect(self.sigFunc_rmv_geo_btn)
        self.remove_relationship_btn.clicked.connect(self.sigFunc_remove_relationship_btn)

    ########## UI SIGNAL FUNCTOINS ##########
    # -------- Tree views --------
    def sigfunc_on_geoTree_item_change(self, item):
        if item.isCheckable():
            name = item.text()
            state = "checked" if item.checkState() == Qt.Checked else "unchecked"
            print(f"item  '{item.text()}' was {state}")
            
            # select geometry in relationship
            print(f"select geometry in relationship")

            # gather the custom uuid's from the database!
            db_row_id = name.split('_')[-1]
            print(db_row_id)
            # geo_uuids = ["AA179516-491A-F48B-34B3-F284368B43CE"]
            uuids =  database_schema_001.ReturnRelationshipUUIDFromDatabase(
                obj_type="geo", database_name=self.active_db, 
                directory=self.active_db_dir, db_row_id=db_row_id
                )
            geo_uuids = uuids.get_uuids_list()
            print(f"GEO_UUID: {geo_uuids}")
            # from the list, select the objects by custom uuid

            # gather's all abjects in the scene with the given custom attr
            all_geo = utils.search_geometry_in_scene(self.custom_uuid_attr)

            # search through all geo with custom attr. 
            geo_uuid_map = {}
            for geo in all_geo:
                if cmds.attributeQuery(self.custom_uuid_attr, node=geo, exists=True):
                    attr_value = cmds.getAttr(f"{geo}.{self.custom_uuid_attr}", asString=1)
                    geo_uuid_map[attr_value] = geo
                    
            # Compare the 'geo_uuids' & if they're found in the 'geo_uuid_map' select those objects!
            print(f"geo_uuid_map = {geo_uuid_map}")
            for uuid in geo_uuids:
                if uuid in geo_uuid_map:
                    selected_geo = geo_uuid_map[uuid]
                    if state == "checked":
                        print(f"selecting objects: {selected_geo}")
                        cmds.select(selected_geo, add=1)
                    else:
                        print(f"Not selecting objects: {selected_geo}")
                        cmds.select(selected_geo, deselect=True)

                # gather all objects in the scene with the given custom attr. search through all geo with custom attr. Compare the 'geo_uuids' & if they're found in the 'geo_uuid_map' select those objects!

    # -- Add Database options --
    def sigFunc_addNewDB_radioBtn(self):
        self.val_addDB_radioBtn = self.Add_new_DB_radioBtn.isChecked()
        if self.val_addDB_radioBtn:
            print("radio button clicked ON")
            self.exportOptions_btn.setEnabled(True)
        else:
            print("radio button clicked OFF")
            self.exportOptions_btn.setEnabled(False)
    

    def sigFunc_exportOptions_btn(self):
        try:
            self.export_db_controller = export_database_controller.exportDatabaseController()
            self.export_db_controller.view.show()
            self.export_db_controller.databaseCreated.connect(self.update_database_ComboBox)
        except Exception as e:
            print(f"Export button encounted an error: {e}")

    # -- available databases --
    def sigFunc_dbFolderPath_btn(self):
        # below is the chosen path by the user
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory", os_custom_directory_utils.create_directory("Jmvs_tool_box", "databases", "geo_databases"))
        self.directory_list.append(directory)
        self.update_database_ComboBox()


    def sigFunc_database_comboBox(self, index):
        self.val_database_comboBox = self.database_comboBox.itemText(index)
        self.active_db = self.database_comboBox.currentText()
        #print(f"db_comboBox current text = `{self.active_db}`")
        self.visualise_active_db()
        return self.val_database_comboBox
    
    # -- skinning --
    def sigFunc_bind_skn_btn(self):
        print(f"bind_skn_btn clicked!")
        result = self.get_sel_jnt_index_and_uuid()
        if result:
            row_index, joint_uuid = result
            print(f"the row index in treeView is :: {row_index} & joint_uuid of selected item in treeView = {joint_uuid}")
            # get a dictionary from a specific row (`row_index`) from the active_database `self.active_db`
            retrieved_row = database_schema_001.Retrieve_UUID_Database_from_row(
                database_name=self.active_db, row_id=row_index+1, directory=self.active_db_dir
                )
            combined_dict_from_row = retrieved_row.get_retrtieved_combined_dict()
            print(f"combined_dict_from_row == {combined_dict_from_row}")
            bind_skin.bind_skin_from_combined_dict(combined_dict_from_row)
        else:
            print(f"No item in joint treeview selected")
        
        
    def sigFunc_unbind_skn_btn(self):
        print(f"unbind_skn_btn clicked!")
        result = self.get_sel_jnt_index_and_uuid()
        if result:
            row_index, joint_uuid = result
            print(f"the row index in treeView is :: {row_index} & joint_uuid of selected item in treeView = {joint_uuid}")
            # get a dictionary from a specific row (`row_index`) from the active_database `self.active_db`
            retrieved_row = database_schema_001.Retrieve_UUID_Database_from_row(
                database_name=self.active_db, row_id=row_index+1, directory=self.active_db_dir
                )
            combined_dict_from_row = retrieved_row.get_retrtieved_combined_dict()
            print(f"combined_dict_from_row == {combined_dict_from_row}")
            
            # Concerned only with the geometry dict!
            unbind_skin.unbindSkin_by_uuid_dict(combined_dict_from_row['geometry_UUID_dict'])
        else:
            print(f"No item in joint treeview selected")


    def sigFunc_bind_all_btn(self):
        print(f"bind_all_btn clicked!")
        all_combined_dicts = self.gather_active_database_combined_dict()
        print(f"all_combined_dicts = {all_combined_dicts}")
        for key, values in all_combined_dicts.items():
            bind_skin.bind_skin_from_combined_dict(combined_dict=values)


    def sigFunc_unbind_all_btn(self):
        print(f"unbind_all_btn clicked!")
        all_combined_dicts = self.gather_active_database_combined_dict()
        # Get all geo UUID dicts and put in a list to iterate over afrer
        geometry_dicts = []
        for dict_entry in all_combined_dicts.values():
            geometry_dicts.append(dict_entry["geometry_UUID_dict"])
        # Iterate over the geo dict list
        for geo_uuid_dict in geometry_dicts:
            unbind_skin.unbindSkin_by_uuid_dict(geo_uuid_dict)

    # -- Delete DB --
    def sigFunc_deleteDB_checkBox(self):
        self.val_deleteDB_checkBox = self.deleteDB_checkBox.isChecked()
        if self.val_deleteDB_checkBox:
            self.deleteDB_Btn.setEnabled(True)
        else:
            self.deleteDB_Btn.setEnabled(False)

    # -- Add JOINT/GEO buttons --
    def sigFunc_add_joint_to_db_btn(self):
        self.add_geo_btn.setEnabled(True)
        print(f"add_joint_to_db_btn cicked")

        # get's joint uuid & stores in a dictionary
        selection = cmds.ls(sl=1, type="joint")
        if selection:
            jnt_uuid_dict = uuid_handler.return_uuid_dict_from_joint(selection)
            print(f"jnt_uuid_dict  == {jnt_uuid_dict}")
        else:
            print("No JOINT selected!")

        # add the chosen joint to new relationship!    
        try:
            if self.val_new_relationship_checkBox:# create new row on database
                # must gather the jnt_name & uuid from the ui selection!
                update_jnt_db = database_schema_001.UpdateJointDatabase(
                    self.active_db, jnt_uuid_dict, self.active_db_dir
                    )
                self.jnt_rShip_row = update_jnt_db.get_new_row()
                print(f"update_jnt_row!: {self.jnt_rShip_row}")
                self.visualise_active_db()
            else: # would not add joint to existing row, becuase would just make a new relationship if it doesn't already exist, 
                # instead work on geo being added!
                pass
        except Exception as e:
            print(f"add_joint_to_db_btn ERROR: {e}")
        
    
    def sigFunc_add_geo_to_db_btn(self):
        print(f"add_geo_to_db_btn cicked")
        # cancel the operation if joints are selected!
        joint_selection = cmds.ls(sl=1, type="joint")
        if joint_selection:
            print("Operation canceled: Joints are selected!")
            return  
        geo_selection = cmds.ls(sl=1, type="transform")
        if geo_selection:
            geo_uuid_dict = uuid_handler.return_uuid_dict_from_geo(geo_selection)
        try:
            print(f"geo_uuid_dict  == {geo_uuid_dict}")
        except Exception as e:
            print(f"add_geo_to_db_btn ERROR, selected tree jont parent! : {e}")
    
        try:
            if self.val_new_relationship_checkBox: # Add geo to db, new relationship has been created, the joint is it's partner
                print(f"self.jnt_rShip_row  when 'add_geo' CLICKED = {self.jnt_rShip_row}")
                database_schema_001.UpdateGeoDatabase(
                    self.jnt_rShip_row, self.active_db, 
                    geo_uuid_dict, self.active_db_dir
                    )
                self.visualise_active_db()
            else: # once the joint had been selected in the treeview Ui
                print(f"Adding GEO to existing row!")
                result = self.get_sel_jnt_index_and_uuid()
                if result:
                    row_index, joint_uuid = result
                    print(f"joint selected in treeView = {joint_uuid}")
                    print(f"joint row_index in treeView = {row_index}")
                    # from uuid, return row
                    '''
                    retrieved_row = database_schema_001.Retrieve_UUID_Database_from_row(
                    database_name=self.active_db, row_id=row_index+1, directory=self.active_db_dir
                    )
                    '''
                    # add geo 
                    database_schema_001.UpdateGeoDatabase(
                        row_index+1, self.active_db, geo_uuid_dict, self.active_db_dir
                        )
                    self.visualise_active_db()
                else:
                    print(f"add geo to existing: error selecting existing joint")
        except Exception as e:
            print(f"add_geo_to_db_btn ERROR: {e}")
        self.new_relationship_checkBox.setChecked(False)
    
    
    def sigFunc_add_jnt_to_db_btn(self):
        print(f"sigFunc_add_jnt_to_db_btn CLICKED!!")
        jnt_parent_name = utils.get_selected_parent_name(self.joint_tree_view, self.joint_model)
        print(f"relationship_name = {jnt_parent_name}")
        jnt_parent_num = jnt_parent_name.split('_')[-1]

        joint_selection = cmds.ls(sl=1, type="joint")
        if not joint_selection:
            print("Operation canceled: Joints NOT selected!")
            return
        elif joint_selection:
            joint_uuid_dict = uuid_handler.return_uuid_dict_from_joint(joint_selection)
        try:
            print(f"joint_uuid_dict  == {joint_uuid_dict}")
        except Exception as e:
            print(f"add_jnt_to_db_btn ERROR, selected tree joint parent! : {e}")
        
        try:
            if not self.val_new_relationship_checkBox:
                # need to select joint in scene, DONE, need to select row in treeView to establish row!
                result = self.get_sel_jnt_index_and_uuid()
                if result:
                    row_index, joint_uuid = result
                    print(f"joint selected in treeView = {joint_uuid}")
                    print(f"joint row_index in treeView = {row_index}")
                    database_schema_001.UpdateJointDatabase(
                    self.active_db, joint_uuid_dict, self.active_db_dir, 
                    jnt_parent_num
                    )
                    self.visualise_active_db()
                else:
                    print(f"add joint to existing row: error selecting existing joint")
        except Exception as e:
            print(f"add_jnt_to_db_btn ERRO: {e}")
        

    def sigFunc_new_relationship_checkBox(self):
        print(f"new_relationship_checkBox is checked cicked")
        self.val_new_relationship_checkBox = self.new_relationship_checkBox.isChecked()
        if self.val_new_relationship_checkBox:
            self.new_jnt_btn.setEnabled(True)
            self.add_geo_btn.setEnabled(False)
            self.add_jnt_btn.setEnabled(False)
        else:
            self.new_jnt_btn.setEnabled(False)
            self.add_geo_btn.setEnabled(True)
            self.add_jnt_btn.setEnabled(True)


    # -- Remove JOINT/GEO buttons --
    def sigFunc_rmv_rShip_checkBox(self):
        
        self.val_rmv_rShip_checkBox = self.rmv_rShip_checkBox.isChecked()
        if self.val_rmv_rShip_checkBox:
            print(f"rmv_rShip_checkBox YES")
            self.remove_relationship_btn.setEnabled(True)
            self.rmv_geo_btn.setEnabled(False)
            self.rmv_jnt_btn.setEnabled(False)
        else:
            print(f"rmv_rShip_checkBox NO")
            self.remove_relationship_btn.setEnabled(False)
            self.rmv_geo_btn.setEnabled(True)
            self.rmv_jnt_btn.setEnabled(True)


    def sigFunc_remove_relationship_btn(self):
        print("clicked remove_relationship_btn")
        try:
            jnt_parent_name = utils.get_selected_parent_name(self.joint_tree_view, self.joint_model)
            print(f"relationship_name = {jnt_parent_name}")
            db_row_id = jnt_parent_name.split('_')[-1]

            database_schema_001.DeleteRelationshipFromDatabase(self.active_db, self.active_db_dir, db_row_id)
        except:
            print(f"Error: Need to SELECT relationship parent in JOINT TreeView!")
        self.visualise_active_db()
        
    
    def sigFunc_rmv_geo_btn(self):
        # cancel the operation if joints are selected!
        result = self.get_geo_name_and_uuid_TreeSel()
        if result:
            geo_name, geo_uuid = result
            print(f"geo_name = {geo_name} & geo_uuid = {geo_uuid}")
            database_schema_001.RemoveSpecificDATAfromDB(
                self.active_db, self.active_db_dir, "geo", geo_name, geo_uuid
                )
            self.visualise_active_db()
        else:
            print(f"in trying to REMOVE GEO, getting name & uuid failed.")


    def sigFunc_rmv_jnt_btn(self):
        print(f"Remove joint button selected")
        # cancel operation if selection isn't a specific joint!
        result = self.get_sel_jnt_name_and_uuid()
        if result:
            joint_name, joint_uuid = result
            print(f"joint_row = {joint_name} & joint_uuid = {joint_uuid}")
            database_schema_001.RemoveSpecificDATAfromDB(
                self.active_db, self.active_db_dir, "joint", joint_name, joint_uuid
                )
            self.visualise_active_db()
    
    
    #--------------------------------------------------------------------------
    ########## TREE VIEW FUNCTOINS ##########
    def gather_active_database_combined_dict(self):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            levels = os_custom_directory_utils.determine_levels_to_target(
                current_dir, "Jmvs_tool_box"
                )
            root_dir = os_custom_directory_utils.go_up_path_levels(current_dir, levels)
            try:
                self.active_db_dir = utils.find_directory(self.active_db, root_dir)
                #print(f"Directory of `{self.active_db}` is:  `{self.active_db_dir}`")
            except FileNotFoundError as e:
                print(f"active db file '{self.active_db}' not found cus of this error: {e}")

            # Get dictionary of all the data from db
            uuid_retrieval = database_schema_001.RetrieveAllUUIDs(
                self.active_db, self.active_db_dir
                )
            try:
                combined_dict = uuid_retrieval.get_combined_dict()
                return combined_dict
            except Exception as e:
                print(f"If you just created a new db, ignore this error, if not: {e}")
    
    # by calling the 'populate tree view' i can update the treeview live as operations happen
    def visualise_active_db(self):
        combined_dict = self.gather_active_database_combined_dict()
        # clear the modules everytime the active db is switched
        self.joint_model.clear()
        self.geo_model.clear()
        #for key, values in combined_dict.items():
        self.populate_tree_views(combined_dict)


    def populate_tree_views(self, data_dict):
        # Store the UUID's from TreeView as Data
            # use 'setData' method to store the UUID in each item with a custom
            # role (QtCore.Qt.UserRole).
        jnt_tree_parent_item = self.joint_model.invisibleRootItem()
        geo_tree_parent_item = self.geo_model.invisibleRootItem()

        #joint_dict = data_dict['joint_UUID_dict']
        #geo_dict = data_dict['geometry_UUID_dict']
        try:
            for index, dict_entry in data_dict.items():
                joint_dict = dict_entry['joint_UUID_dict']
                geo_dict = dict_entry['geometry_UUID_dict']

                # create a parent item for the relationship
                joint_relationship_item = QtGui.QStandardItem(f"joint_relatonship_{index}")
                geo_relationship_item = QtGui.QStandardItem(f"geo_relatonship_{index}")

                # append the relationship item to both tree views
                jnt_tree_parent_item.appendRow(joint_relationship_item)
                geo_tree_parent_item.appendRow(geo_relationship_item)

                # populate the joint treeview
                for joint_name, joint_uuid in joint_dict.items():
                    joint_item = QtGui.QStandardItem(joint_name)
                    joint_relationship_item.appendRow(joint_item)
                    joint_item.setData(joint_uuid, QtCore.Qt.UserRole) # store jnt UUID

                for geo_name, geo_uuid in geo_dict.items():
                    geo_item = QtGui.QStandardItem(geo_name)
                    geo_relationship_item.appendRow(geo_item)
                    geo_relationship_item.setCheckable(True)
                    geo_item.setData(geo_uuid, QtCore.Qt.UserRole) # store jnt UUID
        except Exception as e:
                print(f"If you just created a new db, ignore this error, if not: {e}")
            

    def toggle_uuid_visibility(self, visible):
        # toggle visibility of UUID's, 'toggle_uuids_visibility' function
        print(f"TOGGLE_VISIBILITY")
        for x in range(self.joint_model.rowCount()):
            joint_item = self.joint_model.item(x)
            uuid_item = joint_item.data(QtCore.Qt.UserRole)
            print(f"TV: joint_item = {joint_item}")
            print(f"TV: uuid_item = {uuid_item}")
        if visible:
            joint_item.setText(f"{joint_item.text()} ({uuid_item})")
        else:
            joint_item.setText(joint_item.text().split(' ')[0])

    
    def signal_to_geo_tree_highlight(self):
        # this will change to highlight corresponding relationship parent
        selection_model = self.joint_tree_view.selectionModel()
        selected_indexes = selection_model.selectedIndexes()

        if selected_indexes:
            selected_index = selected_indexes[0]
            if 'joint_relatonship_' in selected_index.data():
                geo_relationship_name = f"geo_relatonship_{selected_index.row() + 1}"
                # find the relationship item in the geo tree view & highlight it
                geo_indexes = self.geo_model.findItems(geo_relationship_name, QtCore.Qt.MatchExactly)
                
                if geo_indexes:
                    geo_item = geo_indexes[0]
                    self.geo_tree_view.expand(geo_item.index())
                    self.geo_tree_view.setCurrentIndex(geo_item.index())

    
    def ui_geo_selects_scene_geo(self):
        geo_uuid = self.retrive_geo_uuid_of_selection()
        # print(f"From treeView selection geo_uuid = {geo_uuid}")
        # select the geo in the scene.
        objects_with_attr = cmds.ls(f"*.{self.custom_uuid_attr}", objectsOnly=1)

        # store the obj & its custom UUID
        uuid_to_obj = {}

        # if cmds.attributeQuery(self.custom_uuid_attr, node=geo, exists=True):
        
        # retrieve all custom UUIDs in one call
        if objects_with_attr:
            custom_uuids = cmds.getAttr(f"{objects_with_attr[0]}.{self.custom_uuid_attr}", asString=1)
            
            for obj in objects_with_attr:
                obj_uuid = cmds.getAttr(f"{obj}.{self.custom_uuid_attr}", asString=1)
                uuid_to_obj[obj_uuid] = obj
            found_obj = uuid_to_obj.get(geo_uuid)
        
            if found_obj:
                cmds.select(found_obj)
                print(f"selected object: {found_obj}")
            else:
                print("No object matches that given geo_uuid")
        else: 
            # this will tend to mean the object hasn't been exported
            # Checking the original file for match.
            print("No objects have custom UUID, meaning geo has not been imported USD")
            shape_nodes = cmds.ls(dag=1, type='mesh')
            all_geo = []
            if shape_nodes:
                transforms = cmds.listRelatives(shape_nodes, parent=True, type='transform', fullPath=True)
                all_geo = list(set(transforms))  # Remove duplicates if any
                for obj in all_geo: # loop thru the objs and check their uuid
                    obj_uuid = cmds.ls(obj, uuid=1)
                    # obj_uuid = cmds.getAttr(f"{obj}.{self.custom_uuid_attr}", asString=1)
                    if obj_uuid and obj_uuid[0] == geo_uuid:
                        found_obj = obj
                        break
            # if found, select it
            if found_obj:
                cmds.select(found_obj)
                print(f"selected object without cutom UUID: {found_obj}")


            

    
    def ui_joint_selects_scene_joint(self):
        joint_uuid = self.retrive_joint_uuid_of_selection()
        """
        all_joints = cmds.ls("jnt_skn_*", dag=1, long=1, type="joint", uuid=1)
        # Map the UUID's to the joint names
        uuid_to_joint = {uuid: joint for joint, uuid in zip(all_joints[::2], all_joints[1::2])}
        found_obj = uuid_to_joint.get(joint_uuid)
        if found_obj:
            cmds.select(found_obj)
            print(f"selected Joint: {found_obj}")
        """
        #print(f"From treeView selection joint_uuid = {joint_uuid}")
        # select the joint in the scene. 
        all_objects = cmds.ls(dag=1, long=1, type="transform")
        found_obj = None
        for obj in all_objects: # loop thru the objs and check their uuid
            obj_uuid = cmds.ls(obj, uuid=1)
            # obj_uuid = cmds.getAttr(f"{obj}.{self.custom_uuid_attr}", asString=1)
            if obj_uuid and obj_uuid[0] == joint_uuid:
                found_obj = obj
                break
        # if found, select it
        if found_obj:
            cmds.select(found_obj)
            print(f"selected object: {found_obj}")
        
        else:
            print("No object matches that given geo_uuid")
        


    def retrive_geo_uuid_of_selection(self):
        # get the selection of the geo tree view
        selection_model = self.geo_tree_view.selectionModel()
        selected_indexes = selection_model.selectedIndexes()

        # if a relationship was selected
        if selected_indexes:
            # could edit to select multiple within the relationship parent
            selected_index = selected_indexes[0]
            geo_item = self.geo_model.itemFromIndex(selected_index)
            geo_uuid = geo_item.data(QtCore.Qt.UserRole)
            return geo_uuid
    
    
    def retrive_joint_uuid_of_selection(self):
        # gets the uuid of the selected joint tree
        selection_model = self.joint_tree_view.selectionModel()
        selected_indexes = selection_model.selectedIndexes()

        # if a relationship was selected
        if selected_indexes:
            # could edit to select multiple within the relationship parent
            selected_index = selected_indexes[0]
            joint_item = self.joint_model.itemFromIndex(selected_index)
            joint_uuid = joint_item.data(QtCore.Qt.UserRole)

            return joint_uuid
            # use joint_uuid to query my data such as findiong it's row in database!

    #--------------------------------------------------------------------------
    ########## SKINNING FUNCTOINS ##########
    def get_sel_jnt_index_and_uuid(self):
        selected_index = utils.get_first_tree_index(self.joint_tree_view)
        row_index = selected_index.row()
        joint_item = self.joint_model.itemFromIndex(selected_index)
        joint_uuid = joint_item.data(QtCore.Qt.UserRole)

        return row_index, joint_uuid

    def get_sel_jnt_name_and_uuid(self):
        selected_index = utils.get_first_tree_index(self.joint_tree_view)
        joint_item = self.joint_model.itemFromIndex(selected_index)
        joint_name = joint_item.text()
        joint_uuid = joint_item.data(QtCore.Qt.UserRole)

        return joint_name, joint_uuid

    def get_geo_name_and_uuid_TreeSel(self):
        selected_index = utils.get_first_tree_index(self.geo_tree_view)
        geo_item = self.geo_model.itemFromIndex(selected_index)
        # is it possible to retrieve the uuid of the selected object?
        geom_name = geo_item.text()
        geo_uuid = geo_item.data(QtCore.Qt.UserRole)

        return geom_name, geo_uuid

def geoDB_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    ui = GeoDatabase()
    ui.show()
    app.exec()
    return ui
