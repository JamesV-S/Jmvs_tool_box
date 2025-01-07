
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
        
        print("GeoDatabase class defined")

        self.UI()

    def UI(self):
        
        main_Vlayout = QtWidgets.QVBoxLayout(self)
        # 3 horizontal layouts
        top_parent_Hlayout = QtWidgets.QHBoxLayout() # 1
        mid_parent_Hlayout = QtWidgets.QHBoxLayout() # 2
        bott_parent_Hlayout = QtWidgets.QHBoxLayout() # 3

        main_Vlayout.addLayout(top_parent_Hlayout)
        main_Vlayout.addLayout(mid_parent_Hlayout)
        main_Vlayout.addLayout(bott_parent_Hlayout)
        
        # 4 layouts within the main_Vlayout

        #----------------------------------------------------------------------
        # 1
        #--------
        # data from database to visualise.
        oneJNT_for_multiGEO_combined_dict = {
            'joint_UUID_dict': {'jnt_skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134'}, 
            'geometry_UUID_dict': {'geo_1': '946C0344-4B43-4E3E-E610-33AEFC6A76D2', 
                'geo_2': 'BC1BBC88-49E0-705C-3B5E-89B24C670722', 
                'geo_3': '2AD65DAA-4F33-E185-634E-B7A81D073E31'}
            }

        multiJNT_for_oneGEO_uuid_combined_dict = {
            'joint_UUID_dict': {
                'skn_0_shoulder_L': '0ADBD31D-4A68-348A-FB5C-A5806EA2ED1F', 
                'skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134', 
                'skn_0_wrist_L': 'F0E55702-46CF-4131-30FB-BDBC0E16AAC9'
            }, 
            'geometry_UUID_dict': {'geo_4': 'BB3DD158-422F-3966-C861-7C8E8FA7F144'}
            }

        oneJNT_for_oneGEO_uuid_combined_dict = {
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
        
        self.model = QtGui.QStandardItemModel()

        jnt_tree_parent_item = self.model.invisibleRootItem()
        jnt_geo_parent_item = self.model.invisibleRootItem()
    
        self.joint_tree_view = QtWidgets.QTreeView(self)
        self.joint_tree_view.setObjectName("joint_treeview")
        self.joint_tree_view.setModel(self.model)

        self.geo_tree_view = QtWidgets.QTreeView(self)
        self.geo_tree_view.setObjectName("geo_treeview")
        self.geo_tree_view.setModel(self.model)

        # set the size of the two treesizess
        for tree_view in [self.joint_tree_view, self.geo_tree_view]:
            tree_view.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Maximum)
            tree_view.setMinimumSize(150, 400)
        
        # Put the data from the database into the tree!!
        jnt_uuid_dict = multiJNT_for_oneGEO_uuid_combined_dict['joint_UUID_dict']
        jnt_name_list = list(jnt_uuid_dict.keys())
        item = QtGui.QStandardItem(jnt_name_list[0])
        # jnt_tree_parent_item.appendRow(item)

        # add the 2 tree views to the tree layout. 
        tree_H_layout = QtWidgets.QHBoxLayout()
        tree_H_layout.addWidget(self.joint_tree_view)
        tree_H_layout.addWidget(self.geo_tree_view)
        top_parent_Hlayout.addLayout(tree_H_layout)
        
        #---------------------
        dropDown_db = QtWidgets.QComboBox()
        dropDown_db.addItems(["DB_geo_arm.db", "DB_geo_mech.db", "DB_geo_cyborgMax.db"])
        
        # skinning_grid_layout for skinning buttons
        bind_skn_btn = QtWidgets.QPushButton("Bind Skin")
        unbind_skn_btn = QtWidgets.QPushButton("Unbind Skin")
        skinning_grid_layout = QtWidgets.QGridLayout()
        skinning_grid_layout.setHorizontalSpacing(-1000)
        skinning_grid_layout.addWidget(bind_skn_btn, 0,0)
        skinning_grid_layout.addWidget(unbind_skn_btn, 0, 1)
        

        # set layout options too
        db_selector_skinnging_V_layout = QtWidgets.QVBoxLayout()
        db_selector_skinnging_V_layout.setContentsMargins(0, 30, 0, 0)
        db_selector_skinnging_V_layout.setSpacing(40)
        # add drop down db selector & skinning grid to `db_selector_skinnging_V_layout`
        db_selector_skinnging_V_layout.addWidget(dropDown_db)
        db_selector_skinnging_V_layout.addLayout(skinning_grid_layout)
        top_parent_Hlayout.addLayout(db_selector_skinnging_V_layout)

        #----------------------------------------------------------------------
        # 2: update GEO & JOINT
        upd_rletionship_btn = QtWidgets.QPushButton("Update Relationship")
        add_jnt_btn = QtWidgets.QPushButton("Add JOINT")
        add_geo_btn = QtWidgets.QPushButton("Add GEO")
        
        mid_parent_Hlayout.addWidget(upd_rletionship_btn)
        mid_parent_Hlayout.addWidget(add_jnt_btn)
        mid_parent_Hlayout.addWidget(add_geo_btn)
        #----------------------------------------------------------------------
        # 3 replacing JOINT & GEO of selection!
        rpl_jnt_btn = QtWidgets.QPushButton("Replace JOINT")
        rpl_geo_btn = QtWidgets.QPushButton("Replace GEOMETRY")
        
        bott_parent_Hlayout.addWidget(rpl_jnt_btn)
        bott_parent_Hlayout.addWidget(rpl_geo_btn)
        
        #----------------------------------------------------------------------
        self.setLayout(main_Vlayout)
    
    def populate_tree_views(self, data_dict):
        self.model.clear()
        
        jnt_tree_parent_item = self.model.invisibleRootItem()
        geo_tree_parent_item = self.model.invisibleRootItem()

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