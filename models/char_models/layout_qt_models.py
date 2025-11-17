
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
    def __init__(self, db_rig_project_directory, val_availableRigComboBox, char_layout_view:CharLayoutViewType):
        print(f"** Hello from DatabaseData()")
        self.view = char_layout_view
        self.db_rig_project_directory = db_rig_project_directory
        self.val_availableRigComboBox = val_availableRigComboBox

        print(f"** db_rig_project_directory = `{self.db_rig_project_directory}`")
        print(f"** val_availableRigComboBox = `{self.val_availableRigComboBox}`")

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
    def __init__(self, db_rig_project_directory, val_availableRigComboBox, char_layout_view):
        super().__init__(db_rig_project_directory, val_availableRigComboBox, char_layout_view)

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
    

class UpdateExtInputHookQListModel(DatabaseData):
    def __init__(self, db_rig_project_directory, val_availableRigComboBox, char_layout_view):
        super().__init__(db_rig_project_directory, val_availableRigComboBox, char_layout_view)

        print(f"*- HEllo from UpdateExtInputHookQListModel()")

        self.populate_ext_input_hook_QListView_model()
        self.populate_ext_input_hook__attr__comboBox_model()

    
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


    def populate_ext_input_hook__attr__comboBox_model(self):
        '''
        # Description: 
            From 'self.db_data' get all the module's components names & add to 
            QList
        '''
        # Return a dictionary of 'input_hook_mtx_plug' key=module: value=attr
        # inp_dict = {}
        # for db in os.listdir(self.db_rig_project_directory):
        #     if db.startswith("DB_") and db.endswith(".db"):
        #         # Iterates over each module.db file & query's the unique_id 
        #         # & side from each row.
        #         data_retriever = database_schema_002.RetrieveModulesData(
        #             self.db_rig_project_directory, db)
        #         inp_dict[db] = data_retriever.db_input_hook_mtx_dict.get(db, [])
        # print(f" # # inp_dict = {inp_dict}")

        # clear the comboBox's & add items to them again!
        self.view.attr_inp_hk_mtx_CB_1.clear()
        self.view.attr_inp_hk_mtx_CB_2.clear()

        # add placeholder text when 'visualising the active db'
        self.view.attr_inp_hk_mtx_CB_1.setPlaceholderText("Select Component in the List")
        self.view.attr_inp_hk_mtx_CB_2.setPlaceholderText("Select Component in the List")

        '''`
        Problem: Current structure
        /{'DB_bipedArm.db': ['jnt_skn_wrist', 'jnt_skn_lower5'], 'DB_bipedLeg.db': ['jnt_skn_ankle'], 'DB_spine.db': ['jnt_skn_top', 'jnt_skn_bottom']}`
        /{'DB_bipedArm.db': [(0, 'L'), (0, 'R')], 'DB_bipedLeg.db': [(0, 'L')], 'DB_spine.db': [(0, 'M')]}
        
        -------------------
        # Needed structure for : 'get_attr_out_hk_mtx_dict()'
         = {
        '*module_name' : [ 
                        ([*output_hook_mtx_list], *unique_id, *'side') 
                        ]
        }

        # Example: bipedArm_0_L, bipedArm_0_R & spine
        Solution_dict_structure = {
        'DB_bipedArm.db': [
                        (['jnt_skn_wrist', 'jnt_skn_lower5'], 0, 'L'), 
                        (['jnt_skn_wrist', 'jnt_skn_lower5'], 0, 'R')
                        ],
        'DB_spine.db': [
                        (["jnt_skn_top", "jnt_skn_bottom"], 0, 'M')
                        ]
        }

        This becomes useful because I can write the items to be added to 
        ComboBox's sinse I will compare db.input_hook_mtx_plug with possible attr 
        from 'Solution_dict_structure'.
        # To give me (for ComboBox's) :
            bipedArm_0_L -> spine.jnt_skn_top_0_M 
            bipedArm_0_R -> spine.jnt_skn_top_0_M
            spine_0_M -> None (cus 'root' module hasn't been published yet!)
        
        # It's Important to note that the addition of *unique_id, *'side' means I 
            need to process this even if I didn't commit changes to 'Edit Data' Tab.
        # + ModuleBlueprint() needs to adapt to this change! 
        '''

        for db_name, out_item in self.attr_out_hk_mtx_dict.items():
            # for out_i in out_item:
            print(f" # self.attr_out_hk_mtx_dict items = `{out_item}`")
            self.view.attr_inp_hk_mtx_CB_1.addItems(out_item)
            self.view.attr_inp_hk_mtx_CB_2.addItems(out_item)


        # Maybe temp here -> add 'None' when wiring the external_imp relationship 
        # between QList selection & QComboBox set, using a diictionary gathered 
        # from the .db's. 
        self.view.attr_inp_hk_mtx_CB_1.addItem("None")
        self.view.attr_inp_hk_mtx_CB_2.addItem("None")

        ''' Items to be added by output attrs!
        # add null item
        self.view.attr_inp_hk_mtx_CB_2.addItem("None")

        # add items to the 
        if inp_dict:
            for value_inp_attr in inp_dict.values():
                self.view.attr_inp_hk_mtx_CB_1.addItems(value_inp_attr)
                self.view.attr_inp_hk_mtx_CB_2.addItems(value_inp_attr)
        '''


class UpdateOutputHookQListModel(DatabaseData):
    def __init__(self, db_rig_project_directory, val_availableRigComboBox, char_layout_view):
        super().__init__(db_rig_project_directory, val_availableRigComboBox, char_layout_view)

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
        
