
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
from user_interface.geoDB_ui import export_db
from systems import (
    os_custom_directory_utils,
    utils
)
from systems.sys_geoDB import (
    uuid_handler
)

importlib.reload(database_manager)
importlib.reload(database_schema_001)
importlib.reload(export_db)
importlib.reload(os_custom_directory_utils)
importlib.reload(utils)
importlib.reload(uuid_handler)

# For the time being, use this file to simply call the 'modular_char_ui.py'
maya_main_wndwPtr = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndwPtr), QWidget)

def delete_existing_ui(ui_name):
    if cmds.window(ui_name, exists=True):
        cmds.deleteUI(ui_name, window=True)


class GeoDatabase(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(GeoDatabase, self).__init__(parent)
        version = "001"
        ui_object_name = f"JmvsGeoDatabase_{version}"
        ui_window_name = f"Jmvs_geo_database_{version}"
        delete_existing_ui(ui_object_name)
        self.setObjectName(ui_object_name)

        # Set flags & dimensions
        self.setParent(main_window)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(ui_window_name)
        self.resize(400, 550)
        
        stylesheet_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                       "..", "CSS", "geoDB_style_sheet_001.css")
        print(stylesheet_path)
        with open(stylesheet_path, "r") as file:
            stylesheet = file.read()
        self.setStyleSheet(stylesheet)

        # gather available database file names & pass to the ComboBox
        self.directory_list = [os_custom_directory_utils.create_directory("Jmvs_tool_box", "databases", "geo_databases")]
        '''
        self.directory_list = [
            "C:\\Docs\\maya\\scripts\\Jmvs_tool_box\\databases\\geo_databases", 
            "C:\\Docs\\maya\\scripts\\Jmvs_tool_box\\databases"
            ]
        '''
        self.db_files = []
        for directory in self.directory_list:
            if os.path.exists(directory):
                for db_file_name in os.listdir(directory):
                    if db_file_name.endswith('.db'):
                        self.db_files.append(db_file_name)
        '''
        self.available_db_path = "C:\\Docs\\maya\\scripts\\Jmvs_tool_box\\databases\\geo_databases" # retrieve this dynamically with the ui
        other_available_path = "C:\\Docs\\maya\\scripts\\Jmvs_tool_box\\databases"
        self.db_files = []# ["James", "Lilirose", "Lis", "Claudia"]
        for db_file_name in os.listdir(self.available_db_path):
            if db_file_name.endswith('.db'):
                self.db_files.append(db_file_name)
        '''

        self.UI()
        self.UI_connect_signals()


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
        '''
        items_to_add_DBcomboBox_update = []
        for db_file_name in os.listdir(self.available_db_path):
            items_to_add_DBcomboBox_update.append(db_file_name)
        # filter out items in the folder except database files
        filtered_list = [item for item in items_to_add_DBcomboBox_update if item.endswith('.db')]
        self.database_comboBox.clear()
        self.database_comboBox.addItems(filtered_list)
        '''
        '''
        print(f"original_db_list = `{self.db_files}`")
        print(f"updated_db_list = `{self.db_files}`")
        # determine the difference between the list on the ui vs the updated list of databases in the directory
        updated_db_list = list(set(filtered_list) - set(self.db_files))
        self.database_comboBox.addItems(updated_db_list)
        '''

    
    def get_database_directory(self, user_dir):
        # from the user input, use the data, if radio button was called 
        pass


    def UI(self):
        self.oneJNT_for_multiGEO_combined_dict = {
            'joint_UUID_dict': {'jnt_skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134'}, 
            'geometry_UUID_dict': {'geo_1': '946C0344-4B43-4E3E-E610-33AEFC6A76D2', 
                'geo_2': 'BC1BBC88-49E0-705C-3B5E-89B24C670722', 
                'geo_3': '2AD65DAA-4F33-E185-634E-B7A81D073E31'}
            }

        self.multiJNT_for_oneGEO_uuid_combined_dict = {
            'joint_UUID_dict': {
                'skn_0_shoulder_L': '0ADBD31D-4A68-348A-FB5C-A5806EA2ED1F', 
                'skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134', 
                'skn_0_wrist_L': 'F0E55702-46CF-4131-30FB-BDBC0E16AAC9'
            }, 
            'geometry_UUID_dict': {'geo_4': 'BB3DD158-422F-3966-C861-7C8E8FA7F144'}
            }

        self.oneJNT_for_oneGEO_uuid_combined_dict = {
            'joint_UUID_dict': {
                'skn_0_shoulder_L': '0ADBD31D-4A68-348A-FB5C-A5806EA2ED1F', 
                'skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134', 
                'skn_0_wrist_L': 'F0E55702-46CF-4131-30FB-BDBC0E16AAC9'
                }, 
            'geometry_UUID_dict': {
                'skn_geo_upperarm': 'A77BA8E3-4DBC-2121-CFEA-88AD3F446242', 
                'skn_geo_lowerarm': '0AF4964F-40AC-FAB7-A329-C28F43B224EA', 
                'skn_geo_hand': 'EB05CC29-40CB-1503-0C9C-629BE45E5CF8'
                }
            }
        

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
        
        # initialise models for each treeview
        self.joint_model = QtGui.QStandardItemModel()
        self.joint_model.setHeaderData(0, QtCore.Qt.Horizontal, "Joint UUID")
        self.geo_model = QtGui.QStandardItemModel()
        self.geo_model.setHeaderData(0, QtCore.Qt.Horizontal, "Geometry UUID")
    
        self.joint_tree_view = QtWidgets.QTreeView(self)
        self.joint_tree_view.setObjectName("joint_treeview")
        self.joint_tree_view.setModel(self.joint_model)

        self.geo_tree_view = QtWidgets.QTreeView(self)
        self.geo_tree_view.setObjectName("geo_treeview")
        self.geo_tree_view.setModel(self.geo_model)
        
        self.joint_tree_view.setObjectName("joint_tree_view")
        self.geo_tree_view.setObjectName("geo_tree_view")

        header = self.geo_tree_view.header()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        # set the size of the two treesizess
        for tree_view in [self.joint_tree_view, self.geo_tree_view]:
            tree_view.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Maximum)
            tree_view.setMinimumSize(150, 400)
        
        # Connect the selection change on joint tree to effect geo tree. 
        self.joint_tree_view.selectionModel().selectionChanged.connect(self.highlight_corresponding_geo)

        # add the 2 tree views to the tree Layout. 
        tree_H_Layout = QtWidgets.QHBoxLayout()
        tree_H_Layout.addWidget(self.joint_tree_view)
        tree_H_Layout.addWidget(self.geo_tree_view)
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
        bind_skn_btn = QtWidgets.QPushButton("Bind Skin")
        unbind_skn_btn = QtWidgets.QPushButton("Unbind Skin")
        bind_all = QtWidgets.QPushButton("Bind ALL")
        unbind_all = QtWidgets.QPushButton("Unbind ALL")
        skinning_grid_Layout.addWidget(bind_skn_btn, 0,0)
        skinning_grid_Layout.addWidget(unbind_skn_btn, 0, 1)
        skinning_grid_Layout.addWidget(bind_all, 1,0)
        skinning_grid_Layout.addWidget(unbind_all, 1, 1)
    
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

        # ---- TOOL TIPS ----
        bind_skn_btn.setToolTip("Bind Geo to Joint SELECTION")
        unbind_skn_btn.setToolTip("Bind Geo to Joint SELECTION")
        bind_all.setToolTip("Bind ALL Geo to Joint")
        unbind_all.setToolTip("Unbind ALL Geo to Joint")

        # ---- STYLE SETTINGS ----
        special_true = [bind_skn_btn, unbind_skn_btn, bind_all, unbind_all]
        special_false = []
        
        for item in special_true:
            item.setProperty("specialButton_Skin", True)
        for item in special_false:
            item.setProperty("specialButton_Skin", False)

        #----------------------------------------------------------------------
        # 2: update GEO & JOINT
        #----------------------------------------------------------------------
        self.new_relationship_checkBox = QtWidgets.QCheckBox("New Relationship +")
        self.new_relationship_checkBox.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.new_relationship_checkBox.setFixedSize(125, 30)
        self.add_jnt_btn = QtWidgets.QPushButton("Add JOINT")
        self.add_jnt_btn.setEnabled(False)
        self.add_geo_btn = QtWidgets.QPushButton("Add GEO")
        self.add_geo_btn.setEnabled(True)
        
        self.add_geo_btn.setProperty("specialButton_add", True)
        self.add_jnt_btn.setProperty("specialButton_add", True)

        mid_parent_HLayout.addWidget(self.new_relationship_checkBox)
        mid_parent_HLayout.addWidget(self.add_jnt_btn)
        mid_parent_HLayout.addWidget(self.add_geo_btn)

        #----------------------------------------------------------------------
        # 3 replacing JOINT & GEO of selection!
        #----------------------------------------------------------------------

        rpl_jnt_btn = QtWidgets.QPushButton("Replace JOINT")
        rpl_geo_btn = QtWidgets.QPushButton("Replace GEOMETRY")
        remove_relationship = QtWidgets.QPushButton("REMOVE Row/Relationship")
        
        rpl_jnt_btn.setProperty("specialButton_rpl", True)
        rpl_geo_btn.setProperty("specialButton_rpl", True)

        bott_parent_HLayout.addWidget(rpl_jnt_btn)
        bott_parent_HLayout.addWidget(rpl_geo_btn)
        bott_parent_HLayout.addWidget(remove_relationship)
        
        #----------------------------------------------------------------------
        self.setLayout(main_VLayout)
    
    
    def UI_connect_signals(self):
        ########## UI CONNECTIONS : 1 : ##########
        # -------- Tree views --------

        # -------- Options to the right of treer --------
        # -- Add Database options --
        self.Add_new_DB_radioBtn.clicked.connect(self.sigFunc_addNewDB_radioBtn)
        self.exportOptions_btn.clicked.connect(self.sigFunc_exportOptions_btn)

        # -- Available database options --
        self.db_folder_path_btn.clicked.connect(self.sigFunc_dbFolderPath_btn)
        self.database_comboBox.currentIndexChanged.connect(self.sigFunc_database_comboBox)

        # -- Skinning options --

        # -- Delete database options --
        self.deleteDB_checkBox.stateChanged.connect(self.sigFunc_deleteDB_checkBox)
        ########## UI CONNECTIONS : 2 : ##########
        # -- add JOINT/GEO & update relationship btns --
        self.new_relationship_checkBox.stateChanged.connect(self.sigFunc_new_relationship_checkBox)
        self.add_jnt_btn.clicked.connect(self.sigFunc_add_joint_to_db_btn)
        self.add_geo_btn.clicked.connect(self.sigFunc_add_geo_to_db_btn)


    ########## UI SIGNAL FUNCTOINS ##########
    # -------- Tree views --------
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
            ui = export_db.export_DB_main()
            # connect the signal to the update db combobox function
            ui.databaseCreated.connect(self.update_database_ComboBox)
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
        self.visualise_active_databse()
        return self.val_database_comboBox

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
        selection = cmds.ls(sl=1, type="joint")
        if selection:
            jnt_uuid_dict = uuid_handler.return_uuid_dict_from_joint(selection)
            print(f"jnt_uuid_dict  == {jnt_uuid_dict}")
        else:
            print("No JOINT selected!")
        
        '''
        conditions: 
        A - create a neew row? OR add to existing row, what dictates this?
        A = add to NEW row IF self.val_new_relationship_checkBox == True
            
            add to existing row IF self.val_new_relationship_checkBox == False
            > how do I know which row to add to?
        
        B = call `visualise_active_databse()` function so the ui treeview is updated live
        ''' 
        # output: jnt_uuid_dict  == 
        # {'jnt_skn_0_shoulder_L': '0ADBD31D-4A68-348A-FB5C-A5806EA2ED1F'}
        try:
            if self.val_new_relationship_checkBox:# create new row on database
                # must gather the jnt_name & uuid from the ui selection!
                database_schema_001.UpdateJointDatabase(self.active_db, jnt_uuid_dict, self.active_db_dir)
            else: # add_to existing row
                pass
        except Exception as e:
            print(f"add_joint_to_db_btn ERROR: {e}")
        
    
    def sigFunc_add_geo_to_db_btn(self):
        print(f"add_geo_to_db_btn cicked")
        self.new_relationship_checkBox.setChecked(False)
        # cancel the operation if joints are selected!
        joint_selection = cmds.ls(sl=1, type="joint")
        if joint_selection:
            print("Operation canceled: Joints are selected!")
            return  
        selection = cmds.ls(sl=1, type="transform")
        if selection:
            geo_uuid_dict = uuid_handler.return_uuid_dict_from_geo(selection)
        try:
            print(f"geo_uuid_dict  == {geo_uuid_dict}")
        except Exception as e:
            print(f"add_joint_to_db_btn ERROR: {e}")
        # geo_uuid_dict  == {
        # 'geo_sphere_shldr_0': 'E1B664E3-4A0E-6AFA-F4AD-F2A5048CD5A6', 
        # 'geo_sphere_shldr_1': '45BCB083-4C20-827E-BF4E-11B42AAEDA90'
        # }

        # A - when can the geo be added? 
        # A = once the joint had been selected in the treeview Ui 
            # OR
            # new relationship has been created, the joint from this is it's partner
        # B - The Joint either selected in treeview OR partner relationship(dictated by `self.val_new_relationship_checkBox`), 
            # needs its row queried so geo can be added to the right one!
        '''
        if self.val_new_relationship_checkBox:# create new row on database
            # must gather the jnt_name & uuid from the ui selection!
            database_schema_001.UpdateGeoDatabase(self.active_db, geo_uuid_dict, self.active_db_dir)
        else: # add_to existing row
            pass
        '''


    def sigFunc_new_relationship_checkBox(self):
        print(f"new_relationship_checkBox is checked cicked")
        self.val_new_relationship_checkBox = self.new_relationship_checkBox.isChecked()
        if self.val_new_relationship_checkBox:
            self.add_jnt_btn.setEnabled(True)
            self.add_geo_btn.setEnabled(False)
        else:
            self.add_jnt_btn.setEnabled(False)
            self.add_geo_btn.setEnabled(True)

    #--------------------------------------------------------------------------
    ########## TREE VIEW FUNCTOINS ##########
    def visualise_active_databse(self):
        print(f"the active database is: {self.active_db}")

        # gather the active database's directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        levels = os_custom_directory_utils.determine_levels_to_target(current_dir, "Jmvs_tool_box")
        root_dir = os_custom_directory_utils.go_up_path_levels(current_dir, levels)
        try:
            self.active_db_dir = utils.find_directory(self.active_db, root_dir)
            print(f"Directory of `{self.active_db}` is:  `{self.active_db_dir}`")
        except FileNotFoundError as e:
            print(f"active db file '{self.active_db}' not found cus of this error: {e}")

        # Get dictionary of all the data from db
        uuid_retrieval = database_schema_001.RetrieveAllUUIDs(self.active_db, self.active_db_dir)
        combined_dict = uuid_retrieval.get_combined_dict()
        print(f"active db's combinded dict = `{combined_dict}` retrieved from `{self.active_db}")
        
        # clear the modules everytime the active db is switched
        self.joint_model.clear()
        self.geo_model.clear()
        for key, values in combined_dict.items():
            self.populate_tree_views(values)

        '''
        {
        1: {
        'joint_UUID_dict': 
            {'jnt_skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134'}, 
        'geometry_UUID_dict': 
            {'geo_1': '946C0344-4B43-4E3E-E610-33AEFC6A76D2', 
            'geo_2': 'BC1BBC88-49E0-705C-3B5E-89B24C670722', 
            'geo_3': '2AD65DAA-4F33-E185-634E-B7A81D073E31'
            }
        },
        2: {
        'joint_UUID_dict': 
            {'skn_0_shoulder_L': '0ADBD31D-4A68-348A-FB5C-A5806EA2ED1F', 
            'skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134', 
            'skn_0_wrist_L': 'F0E55702-46CF-4131-30FB-BDBC0E16AAC9'}, 
        'geometry_UUID_dict': 
            {'geo_4': 'BB3DD158-422F-3966-C861-7C8E8FA7F144'}
        }, 
        3: {
        'joint_UUID_dict': 
            {'skn_0_shoulder_L': '0ADBD31D-4A68-348A-FB5C-A5806EA2ED1F', 
            'skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134', 
            'skn_0_wrist_L': 'F0E55702-46CF-4131-30FB-BDBC0E16AAC9'}, 
        'geometry_UUID_dict': 
            {'skn_geo_upperarm': 'A77BA8E3-4DBC-2121-CFEA-88AD3F446242', 
            'skn_geo_lowerarm': '0AF4964F-40AC-FAB7-A329-C28F43B224EA', 
            'skn_geo_hand': 'EB05CC29-40CB-1503-0C9C-629BE45E5CF8'}
        }
        }`
        '''


    def populate_tree_views(self, data_dict):
        #self.joint_model.clear() # Don''t want to clear, needs to be adative!
        #self.geo_model.clear()
        
        jnt_tree_parent_item = self.joint_model.invisibleRootItem()
        geo_tree_parent_item = self.geo_model.invisibleRootItem()

        joint_dict = data_dict['joint_UUID_dict']
        geo_dict = data_dict['geometry_UUID_dict']

        # Determine the type of dictionary
        if len(joint_dict) == 1 and len(geo_dict) > 1:
            # One joint, multiple geometries
            for joint_name, joint_uuid in joint_dict.items():
                joint_item = QtGui.QStandardItem(joint_name)
                jnt_tree_parent_item.appendRow(joint_item)

                geo_parent_item = QtGui.QStandardItem(joint_name)
                geo_tree_parent_item.appendRow(geo_parent_item)
                for geo_name, geo_uuid in geo_dict.items():
                    geo_item = QtGui.QStandardItem(geo_name)
                    geo_parent_item.appendRow(geo_item)

        elif len(joint_dict) > 1 and len(geo_dict) == 1:
            # Multiple joints, one geometry
            geo_name = next(iter(geo_dict))
            geo_item = QtGui.QStandardItem(geo_name)
            geo_tree_parent_item.appendRow(geo_item)

            joint_parent_item = QtGui.QStandardItem(geo_name)
            jnt_tree_parent_item.appendRow(joint_parent_item)
            for joint_name, joint_uuid in joint_dict.items():
                joint_item = QtGui.QStandardItem(joint_name)
                joint_parent_item.appendRow(joint_item)

        elif len(joint_dict) == len(geo_dict):
            # One-to-one joint and geometry
            for joint_name, joint_uuid in joint_dict.items():
                joint_item = QtGui.QStandardItem(joint_name)
                jnt_tree_parent_item.appendRow(joint_item)

                geo_name = list(geo_dict.keys())[list(joint_dict.keys()).index(joint_name)]
                geo_item = QtGui.QStandardItem(geo_name)
                geo_tree_parent_item.appendRow(geo_item)

        
    def highlight_corresponding_geo(self, selected, deselected):
        # Clear previous selection
        self.geo_tree_view.selectionModel().clearSelection()

        # Get the selected joint item
        for index in selected.indexes():
            joint_name = index.data()
            
            # Logic to be changed!
            # Based on the current dictionary, find the corresponding geo item
            current_db = "DB_geo_arm.db" # self.dropDown_db.currentText()
            if current_db == "DB_geo_arm.db":
                active_dict = self.oneJNT_for_oneGEO_uuid_combined_dict
            elif current_db == "DB_geo_mech.db":
                active_dict = self.multiJNT_for_oneGEO_uuid_combined_dict
            elif current_db == "DB_geo_cyborgMax.db":
                active_dict = self.oneJNT_for_multiGEO_combined_dict
            else:
                return
            

            # Find the corresponding geo item for the selected joint
            geo_dict = active_dict['geometry_UUID_dict']
            joint_dict = active_dict['joint_UUID_dict']

            if joint_name in joint_dict:
                if len(joint_dict) == 1 and len(geo_dict) > 1:
                    # One joint, multiple geos
                    for geo_name in geo_dict.keys():
                        geo_item = self.geo_model.findItems(geo_name, QtCore.Qt.MatchExactly)
                        if geo_item:
                            geo_index = self.geo_model.indexFromItem(geo_item[0])
                            self.geo_tree_view.selectionModel().select(
                                geo_index, QtCore.QItemSelectionModel.Select
                            )

                elif len(joint_dict) > 1 and len(geo_dict) == 1:
                    # Multiple joints, one geo
                    geo_name = next(iter(geo_dict))
                    geo_item = self.geo_model.findItems(geo_name, QtCore.Qt.MatchExactly)
                    if geo_item:
                        geo_index = self.geo_model.indexFromItem(geo_item[0])
                        self.geo_tree_view.selectionModel().select(
                            geo_index, QtCore.QItemSelectionModel.Select
                        )

                elif len(joint_dict) == len(geo_dict):
                    # One-to-one joint and geometry
                    geo_name = list(geo_dict.keys())[list(joint_dict.keys()).index(joint_name)]
                    geo_item = self.geo_model.findItems(geo_name, QtCore.Qt.MatchExactly)
                    if geo_item:
                        geo_index = self.geo_model.indexFromItem(geo_item[0])
                        self.geo_tree_view.selectionModel().select(
                            geo_index, QtCore.QItemSelectionModel.Select
                        )    

    ########## ADD JOINT/GEO FUNCTOINS ##########
    def add_joint_to_db(self):
        pass
    
    
    def add_geo_to_db(self):
        pass



def geoDB_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    ui = GeoDatabase()
    ui.show()
    app.exec()
    return ui