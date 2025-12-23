
import importlib
import os.path
import maya.cmds as cmds
# import pymel.core as pm
import json
from typing import TYPE_CHECKING

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

from utils import (
    utils,
    utils_os,
    utils_json,
    utils_QTree
)

from databases.char_databases import (
    database_schema_002
    )

from views.char_views.char_layout_view import CharLayoutView
CharLayoutViewType = CharLayoutView

importlib.reload(utils)
importlib.reload(utils_os)
importlib.reload(utils_json)
importlib.reload(utils_QTree)
importlib.reload(database_schema_002)

class DatabaseData:
    def __init__(self, db_rig_project_directory, char_layout_view:CharLayoutViewType):
        print(f"** Hello from DatabaseData()")
        self.view = char_layout_view
        self.db_rig_project_directory = db_rig_project_directory

        print(f"** db_rig_project_directory = `{self.db_rig_project_directory}`")

        self.db_data = self.get_db_data()
        self.component_name_ls = self.get_component_name_ls()
        self.attr_out_hk_mtx_dict = self.get_attr_out_hk_mtx_dict()


    def get_db_data(self):
        print(f"** running 'get_db_data()' func")
        '''
        # Description
            Iterate through each module.db file in the 'db_rig_project_directory'
            & gather the neccesary data into 'db_data'. 
        # Return:
            db_data (dict): keys = 'DB_*{module_name}.db' : 
                            vals = [(unique_id, side, for each component), etc, ]
            example: 
                {
                'DB_bipedArm.db': [(0, 'L'), (0, 'R')], 
                'DB_quadArm.db': [(0, 'L')]
                }
        '''
        db_data = {}
        if os.path.exists(self.db_rig_project_directory):
            for db in os.listdir(self.db_rig_project_directory):
                if db.startswith("DB_") and db.endswith(".db"):
                    # Iterates over each module.db file & query's the unique_id 
                    # & side from each row.
                    data_retriever = database_schema_002.RetrieveModulesData(
                        self.db_rig_project_directory, db)
                    db_data[db] = data_retriever.db_data_iteraion.get(db)
            print(f"** 'DatabaseData' db_data = {db_data}")
            
            return db_data
        else:
            cmds.warning(f" {self.db_rig_project_directory}")
            return {}
        

    def get_component_name_ls(self):
        component_name_ls = []

        if self.db_data:
            # Create naming convention for of the items to add to QList. 
            for db_name, rows in self.db_data.items():
                db_base_name = db_name.replace("DB_", "").replace(".db", "")
                for unique_id, side in rows:
                    item_name = f"{db_base_name}_{unique_id}_{side}"
                    print(f"* mdl_name:`{db_name}`, item_name:`{item_name}`")
                    component_name_ls.append(item_name)

        return component_name_ls
    

    def get_attr_out_hk_mtx_dict(self):
        # return with database_schema_002
        attr_out_hk_mtx_dict = {}
        for db in os.listdir(self.db_rig_project_directory):
            if db.startswith("DB_") and db.endswith(".db"):
                # Iterates over each module.db file & query's the unique_id 
                # & side from each row.
                data_retriever = database_schema_002.RetrieveModulesData(
                    self.db_rig_project_directory, db)
                attr_out_hk_mtx_dict[db] = data_retriever.db_output_hook_mtx_dict.get(db)
        print(f"** attr_out_hk_mtx_dict = `{attr_out_hk_mtx_dict}`")
        return attr_out_hk_mtx_dict    


class UpdateQTreeModel(DatabaseData):
    def __init__(self, db_rig_project_directory, char_layout_view):
        super().__init__(db_rig_project_directory, char_layout_view)

        print(f"* HEllo from TestInheritance()")
        print(f"* self.db_data = {self.db_data}")

        self.populate_QTreeView_model()


    def populate_QTreeView_model(self):
        '''
        # Description:
            Add items to the QTreeView model. Items being the module name & 
            components within it.
        # Attributes: N/A 
        # Reuturn: N/A 
        '''
        # clear the treeView's model (ie, the items in it) everytime the active 
        # db is switched.
        self.view.mdl_tree_model.clear()
        
        tree_parent_item = self.view.mdl_tree_model.invisibleRootItem()
        
        if not self.db_data:
            # NO module data in the dictionary 'db_data'
            print(f"NO data in self.db_data: {self.db_data}` ")
        else:
            # try:
            for db_name, rows in self.db_data.items():
                db_base_name = db_name.replace("DB_", "").replace(".db", "")
                db_item = QtGui.QStandardItem(f"{db_base_name}")
                db_item.setData(True, QtCore.Qt.UserRole)

                for unique_id, side in rows:
                    item_name = f"mdl_{db_base_name}_{unique_id}_{side}"
                    mdl_item = QtGui.QStandardItem(item_name)
                    mdl_item.setData(False, QtCore.Qt.UserRole)
                    db_item.appendRow(mdl_item)
                    
                tree_parent_item.appendRow(db_item)
    

class UpdateOutputHookQListModel(DatabaseData):
    def __init__(self, db_rig_project_directory, char_layout_view):
        super().__init__(db_rig_project_directory, char_layout_view)

        print(f"*- HEllo from UpdateExtInputHookQListModel()")

        self.populate_output_hook__component__QListView_model()
        self.populate_output_hook__attr__QListView_model()

    
    def populate_output_hook__component__QListView_model(self):
        '''
        #Description: 
            From 'self.db_data' get all the module's components names & add to 
            QList
        '''
        model = self.view.comp_out_hk_mtx_Qlist_Model
        model.clear()

        print(f" >* component_name_ls = `{self.component_name_ls}`")
        # Add the list of component names to QListModel!
        for item in self.component_name_ls:
            mdl_item = QtGui.QStandardItem(item)
            model.appendRow(mdl_item)


    def populate_output_hook__attr__QListView_model(self):
        # From a list of component names, return a list or dict of the ascociated 
        # output matrix attr with database_schema_002 
        model = self.view.attr_out_hk_mtx_Qlist_Model
        model.clear()
        
        # bipedArm, quadLeg, root, spine
        example_out_component_name_ls = [
            ["jnt_skn_wrist", "jnt_skn_lower5"], 
            ["jnt_skn_ankle"], 
            ["ctrl_fk_centre", "ctrl_fk_COG"],
            ["jnt_skn_top", "jnt_skn_bottom"]
            ]
        
        for key, i in self.attr_out_hk_mtx_dict.items():
            if len(i) > 1:
                add_item = f"{i[0]} | {i[1]}"
            else:
                add_item = f"{i[0]}"
            mdl_item = QtGui.QStandardItem(add_item)
            model.appendRow(mdl_item)
        

class UpdateExtInputHookQListModel(DatabaseData):
    def __init__(self, db_rig_project_directory, char_layout_view):
        super().__init__(db_rig_project_directory, char_layout_view)

        print(f"*- HEllo from UpdateExtInputHookQListModel()")

        self.populate_ext_input_hook_QListView_model()
        self.populate_ext_inp_hk_mtx_objComboBox_model()
        utils_QTree.populate_ext_inp_hk_mtx_atrComboBox_model(
            self.view.attr_inp_hk_mtx_CB_prim, self.view.attr_inp_hk_mtx_CB_scnd
            )

        # self.view.comp_inp_hk_mtx_Qlist.clicked.connect(self.on_Qlist_item_clicked)

    
    def populate_ext_input_hook_QListView_model(self):
        '''
        #Description: 
            From 'self.db_data' get all the module's components names & add to 
            QList
        '''
        model = self.view.comp_inp_hk_mtx_Qlist_Model
        model.clear()

        print(f"* component_name_ls = `{self.component_name_ls}`")
        # Add the list of component names to QListModel!
        for item in self.component_name_ls:
            mdl_item = QtGui.QStandardItem(item)
            model.appendRow(mdl_item)

    
    def populate_ext_inp_hk_mtx_objComboBox_model(self):
        model = self.view.comp_inp_hk_mtx_Qlist_Model
        item_ls = []
        for row in range(model.rowCount()):
            index = model.index(row, 0)
            item = model.data(index)
            if item is not None:
                item_ls.append(item)
        print(f"*all items in list: {item_ls}")
        item_ls.append('None')
        self.view.attr_inp_hk_mtx_CB_obj.clear()
        self.view.attr_inp_hk_mtx_CB_obj.setPlaceholderText("Select a Component in the List")
        self.view.attr_inp_hk_mtx_CB_obj.addItems(item_ls)
            

    def on_Qlist_item_clicked(self, idx):
        # model = self.view.comp_inp_hk_mtx_Qlist_Model
        item_txt = idx.data()

        self.update_comboBoxs(item_txt)


    def update_comboBoxs(self, component_name):
        self.view.attr_inp_hk_mtx_CB_prim.clear()
        self.view.attr_inp_hk_mtx_CB_scnd.clear()

        attributes = self.get_attributes_for_component(component_name)

        if attributes:
            # self.view.attr_inp_hk_mtx_CB_prim.setPlaceholderText("Select Component in the List")
            self.view.attr_inp_hk_mtx_CB_prim.setPlaceholderText("Primary Atr")
            self.view.attr_inp_hk_mtx_CB_scnd.setPlaceholderText("Secondary Atr")
            self.view.attr_inp_hk_mtx_CB_prim.addItems(attributes)
            self.view.attr_inp_hk_mtx_CB_scnd.addItems(attributes)


    def get_attributes_for_component(self, component_name):
        module, unique_id, side = utils.get_name_id_data_from_component(component_name)

        val_availableRigComboBox = self.view.available_rig_comboBox.currentText()
        rig_db_directory = utils_os.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", 
            "db_rig_storage", val_availableRigComboBox
            )
        get_user_settings_data = database_schema_002.RetrieveSpecificData(rig_db_directory, module, unique_id, side)
        inp_hook_mtx_ls = get_user_settings_data.return_inp_hk_mtx()
        
        atr_ls = []
        # a list of the comp's that match the input_hook_mtx obj & exist as a database. 
        for inp_plg in inp_hook_mtx_ls:
            # print(f"plg = {inp_plg}")
            parts = inp_plg.split('.')
            # print(f"Parts = {parts}")
            atr = parts[-1]
            atr_ls.append(atr)
        atr_ls.append('None')

        return atr_ls


