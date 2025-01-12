
import maya.cmds as cmds
from maya import OpenMayaUI

try:
    from PySide6 import QtCore, QtWidgets, QtGui
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon, QStandardItemModel, QStandardItem
    from PySide6.QtWidgets import (QWidget)
    from shiboken6 import wrapInstance
except ModuleNotFoundError:
    from PySide2 import QtCore, QtWidgets, QtGui
    from PySide2.QtCore import Qt
    from PySide2.QtGui import QIcon
    from PySide2.QtWidgets import (QWidget)
    from shiboken2 import wrapInstance

import sys
import importlib
import os.path

from databases.geo_databases import database_schema_001
importlib.reload(database_schema_001)

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

        self.UI()
        geo_arm_db_select = 1
        if geo_arm_db_select:
            self.databse_selection_change()

        
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
        # data from database to visualise.
        
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
        layH_Add_DB_btn = QtWidgets.QHBoxLayout()
        layH_Add_DB_btn.setContentsMargins(100, 0, 0, 0)

        radioBtn_Add_new_DB = QtWidgets.QRadioButton("Add New Database")
        layH_Add_DB_btn.addWidget(radioBtn_Add_new_DB)
        
        # -- Export Options --
        layH_exportOptions_DB_btn = QtWidgets.QHBoxLayout()
        Btn_exportOptions = QtWidgets.QPushButton("+")
        Lbl_exportOptions = QtWidgets.QLabel("Export Options")
        layH_exportOptions_DB_btn.addWidget(Btn_exportOptions)
        layH_exportOptions_DB_btn.addWidget(Lbl_exportOptions)
        Lbl_exportOptions.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        Lbl_exportOptions.setFixedSize(150, 30)
        
        ''''''
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
        ''''''

        # add this sections H_Layout to parent V_Layout
        layV_Add_DB.addLayout(layH_Add_DB_btn)
        layV_Add_DB.addLayout(layH_exportOptions_DB_btn)
        layV_Add_DB.addLayout(layH_Spacer_01)

        layV_TOP_R.addLayout(layV_Add_DB)

        #---------------------
        # Database dropDownBox Layout
        layV_dropDown_DB = QtWidgets.QVBoxLayout()

        # -- Database Dropdown TITLE --
        layH_ddBox_Lbl = QtWidgets.QHBoxLayout()
        ddBox_Lbl = QtWidgets.QLabel("Available Databases'")
        layH_ddBox_Lbl.addWidget(ddBox_Lbl)
        ddBox_Lbl.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        ddBox_Lbl.setFixedSize(150, 30)

        # -- Database Dropdown -- 
        layH_ddBox = QtWidgets.QHBoxLayout()
        database_ddBox = QtWidgets.QComboBox()
        #                        (BElOW) TEMPORARY LIST (BElOW)
        database_ddBox.addItems(["DB_geo_arm.db", "DB_geo_mech.db", "DB_geo_cyborgMax.db"])
        layH_ddBox.addWidget(database_ddBox)

        # -- Horizontal Spacer --
        layH_Spacer_02 = QtWidgets.QHBoxLayout()
        # Add the spacer QWidget
        spacerH_02 = QtWidgets.QWidget()
        spacerH_02.setFixedSize(350,10)
        spacerH_02.setObjectName("Spacer")
        layH_Spacer_02.addWidget(spacerH_02)
        layH_Spacer_02.setContentsMargins(0, 15, 0, 0)

        layV_dropDown_DB.addLayout(layH_ddBox_Lbl)
        layV_dropDown_DB.addLayout(layH_ddBox)
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

        # -- Delete Label --
        deleteDB_Lbl = QtWidgets.QLabel("Delete Databases'")
        layH_delete_DB.addWidget(deleteDB_Lbl)

        # -- Delete Button --
        layH_deleteDB_Btn = QtWidgets.QPushButton("(/)")
        layH_delete_DB.addWidget(layH_deleteDB_Btn)

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
        upd_rletionship_btn = QtWidgets.QPushButton("Update Relationship")
        add_jnt_btn = QtWidgets.QPushButton("Add JOINT")
        add_geo_btn = QtWidgets.QPushButton("Add GEO")
        
        add_geo_btn.setProperty("specialButton_add", True)
        add_jnt_btn.setProperty("specialButton_add", True)

        mid_parent_HLayout.addWidget(upd_rletionship_btn)
        mid_parent_HLayout.addWidget(add_jnt_btn)
        mid_parent_HLayout.addWidget(add_geo_btn)

        #----------------------------------------------------------------------
        # 3 replacing JOINT & GEO of selection!
        #----------------------------------------------------------------------

        rpl_jnt_btn = QtWidgets.QPushButton("Replace JOINT")
        rpl_geo_btn = QtWidgets.QPushButton("Replace GEOMETRY")
        
        rpl_jnt_btn.setProperty("specialButton_rpl", True)
        rpl_geo_btn.setProperty("specialButton_rpl", True)

        bott_parent_HLayout.addWidget(rpl_jnt_btn)
        bott_parent_HLayout.addWidget(rpl_geo_btn)
        
        #----------------------------------------------------------------------
        self.setLayout(main_VLayout)
    

    def UI_exporting_database(self):
        # create the ui for the database exporter
        pass
    

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

    def databse_selection_change(self):
        current_db = "DB_geo_arm.db"# self.dropDown_db.currentText()
        if current_db == "DB_geo_arm.db":
            self.populate_tree_views(self.oneJNT_for_oneGEO_uuid_combined_dict)
            self.populate_tree_views(self.oneJNT_for_multiGEO_combined_dict)
            self.populate_tree_views(self.multiJNT_for_oneGEO_uuid_combined_dict)
            pass
        elif current_db == "DB_geo_mech.db":
            self.populate_tree_views(self.multiJNT_for_oneGEO_uuid_combined_dict)
        elif current_db == "DB_geo_cyborgMax.db":
            self.populate_tree_views(self.oneJNT_for_multiGEO_combined_dict)

    def create_database(self):
        database_schema_001.CreateDatabase(mdl_name="geo_mech")




def geoDB_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    ui = GeoDatabase()
    ui.show()
    app.exec()
    return ui