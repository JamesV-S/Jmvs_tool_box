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

from models.geoDB_models import geo_db_model
from views.geoDB_views import geo_db_view

from main_entry_points.geoDB_mep import export_database_main  

from databases import database_manager
from databases.geo_databases import database_schema_001
from systems import (
    os_custom_directory_utils,
    utils
    )
from systems.sys_geoDB import (
    uuid_handler, 
    bind_skin,
    unbind_skin
)

importlib.reload(geo_db_model)
importlib.reload(geo_db_view)

importlib.reload(database_manager)
importlib.reload(database_schema_001)
importlib.reload(export_database_main)
importlib.reload(os_custom_directory_utils)
importlib.reload(utils)
importlib.reload(uuid_handler)
importlib.reload(bind_skin)
importlib.reload(unbind_skin)

class GeometryDatabaseController:
    def __init__(self): # class
        self.model = geo_db_model.GeometryDatabaseModel()
        self.view = geo_db_view.GeometryDatabaseView()
        
        # gather available database file names & pass to the ComboBox
        self.directory_list = [os_custom_directory_utils.create_directory("Jmvs_tool_box", "databases", "geo_databases")]
        self.db_files = []
        for directory in self.directory_list:
            if os.path.exists(directory):
                for db_file_name in os.listdir(directory):
                    if db_file_name.endswith('.db'):
                        self.db_files.append(db_file_name)
        
        self.view.database_comboBox.addItems(self.db_files)

        self.custom_uuid_attr = "custom_UUID"
        self.export_db_controller = None
        self.val_new_relationship_checkBox = 0
        self.active_db = self.view.database_comboBox.currentText()
        self.model.visualise_active_db()
        
        # Connect the selection change on joint tree to effect geo tree. 
        self.view.joint_tree_view.selectionModel().selectionChanged.connect(self.model.signal_to_geo_tree_highlight)
        self.view.joint_tree_view.selectionModel().selectionChanged.connect(self.model.ui_joint_selects_scene_joint)
        self.view.geo_tree_view.selectionModel().selectionChanged.connect(self.model.ui_geo_selects_scene_geo)
        

        ########## UI CONNECTIONS : 1 : ##########
        # -------- Tree views --------
        self.view.geo_model.itemChanged.connect(self.sigfunc_on_geoTree_item_change)

        # -------- Options to the right of treer --------
        # -- Add Database options --
        self.view.Add_new_DB_radioBtn.clicked.connect(self.sigFunc_addNewDB_radioBtn)
        self.view.exportOptions_btn.clicked.connect(self.sigFunc_exportOptions_btn)

        # -- Available database options --
        self.view.db_folder_path_btn.clicked.connect(self.sigFunc_dbFolderPath_btn)
        self.view.database_comboBox.currentIndexChanged.connect(self.sigFunc_database_comboBox)

        # -- Skinning options --
        self.view.bind_skn_btn.clicked.connect(self.sigFunc_bind_skn_btn)
        self.view.unbind_skn_btn.clicked.connect(self.sigFunc_unbind_skn_btn)
        self.view.bind_all_btn.clicked.connect(self.sigFunc_bind_all_btn)
        self.view.unbind_all_btn.clicked.connect(self.sigFunc_unbind_all_btn)

        # -- Delete database options --
        self.view.deleteDB_checkBox.stateChanged.connect(self.sigFunc_deleteDB_checkBox)
        ########## UI CONNECTIONS : 2 : ##########
        # -- add JOINT/GEO & update relationship btns --
        self.view.new_relationship_checkBox.stateChanged.connect(self.sigFunc_new_relationship_checkBox)
        self.view.new_jnt_btn.clicked.connect(self.sigFunc_add_joint_to_db_btn)
        self.view.add_geo_btn.clicked.connect(self.sigFunc_add_geo_to_db_btn)
        self.view.add_jnt_btn.clicked.connect(self.sigFunc_add_jnt_to_db_btn)

        # -- Remove JOINT/GEO --
        self.view.rmv_rShip_checkBox.stateChanged.connect(self.sigFunc_rmv_rShip_checkBox)
        self.view.rmv_jnt_btn.clicked.connect(self.sigFunc_rmv_jnt_btn)
        self.view.rmv_geo_btn.clicked.connect(self.sigFunc_rmv_geo_btn)
        self.view.remove_relationship_btn.clicked.connect(self.sigFunc_remove_relationship_btn)


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
            uuids =  self.model.return_geo_uuid_from_db(db_row_id)
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
        self.val_addDB_radioBtn = self.view.Add_new_DB_radioBtn.isChecked()
        if self.val_addDB_radioBtn:
            print("radio button clicked ON")
            self.view.exportOptions_btn.setEnabled(True)
        else:
            print("radio button clicked OFF")
            self.view.exportOptions_btn.setEnabled(False)
    

    def sigFunc_exportOptions_btn(self):
        try:
            # Show the ui & get the returned the controller
            self.export_db_controller = export_database_main.export_db_main()
        
            # Access the view through the controller 
            ui = self.export_db_controller.view
            
            # connect the signal to the update db combobox function
            ui.databaseCreated.connect(self.model.update_database_ComboBox)
        except Exception as e:
            print(f"Export button encounted an errors: {e}")


    # -- available databases --
    def sigFunc_dbFolderPath_btn(self):
        # below is the chosen path by the user
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory", os_custom_directory_utils.create_directory("Jmvs_tool_box", "databases", "geo_databases"))
        self.directory_list.append(directory)
        self.model.update_database_ComboBox()


    def sigFunc_database_comboBox(self, index):
        self.val_database_comboBox = self.view.db_folder_path_btn.itemText(index)
        self.active_db = self.view.db_folder_path_btn.currentText()
        #print(f"db_comboBox current text = `{self.active_db}`")
        self.model.visualise_active_db()
        return self.val_database_comboBox
    
    # -- skinning --
    def sigFunc_bind_skn_btn(self):
        print(f"bind_skn_btn clicked!")
        result = self.model.get_sel_jnt_index_and_uuid()
        if result:
            row_index, joint_uuid = result
            print(f"the row index in treeView is :: {row_index} & joint_uuid of selected item in treeView = {joint_uuid}")
            # get a dictionary from a specific row (`row_index`) from the active_database `self.active_db`
            retrieved_row = database_schema_001.Retrieve_UUID_Database_from_row(
                database_name=self.active_db, row_id=row_index+1, directory=self.model.active_db_dir
                )
            combined_dict_from_row = retrieved_row.get_retrtieved_combined_dict()
            print(f"combined_dict_from_row == {combined_dict_from_row}")
            bind_skin.bind_skin_from_combined_dict(combined_dict_from_row)
        else:
            print(f"No item in joint treeview selected")
        
        
    def sigFunc_unbind_skn_btn(self):
        print(f"unbind_skn_btn clicked!")
        result = self.model.get_sel_jnt_index_and_uuid()
        if result:
            row_index, joint_uuid = result
            print(f"the row index in treeView is :: {row_index} & joint_uuid of selected item in treeView = {joint_uuid}")
            # get a dictionary from a specific row (`row_index`) from the active_database `self.active_db`
            retrieved_row = database_schema_001.Retrieve_UUID_Database_from_row(
                database_name=self.active_db, row_id=row_index+1, directory=self.model.active_db_dir
                )
            combined_dict_from_row = retrieved_row.get_retrtieved_combined_dict()
            print(f"combined_dict_from_row == {combined_dict_from_row}")
            
            # Concerned only with the geometry dict!
            unbind_skin.unbindSkin_by_uuid_dict(combined_dict_from_row['geometry_UUID_dict'])
        else:
            print(f"No item in joint treeview selected")


    def sigFunc_bind_all_btn(self):
        print(f"bind_all_btn clicked!")
        all_combined_dicts = self.model.gather_active_database_combined_dict()
        print(f"all_combined_dicts = {all_combined_dicts}")
        for key, values in all_combined_dicts.items():
            bind_skin.bind_skin_from_combined_dict(combined_dict=values)


    def sigFunc_unbind_all_btn(self):
        print(f"unbind_all_btn clicked!")
        all_combined_dicts = self.model.gather_active_database_combined_dict()
        # Get all geo UUID dicts and put in a list to iterate over afrer
        geometry_dicts = []
        for dict_entry in all_combined_dicts.values():
            geometry_dicts.append(dict_entry["geometry_UUID_dict"])
        # Iterate over the geo dict list
        for geo_uuid_dict in geometry_dicts:
            unbind_skin.unbindSkin_by_uuid_dict(geo_uuid_dict)

    # -- Delete DB --
    def sigFunc_deleteDB_checkBox(self):
        self.val_deleteDB_checkBox = self.view.deleteDB_checkBox.isChecked()
        if self.val_deleteDB_checkBox:
            self.view.deleteDB_Btn.setEnabled(True)
        else:
            self.view.deleteDB_Btn.setEnabled(False)

    # -- Add JOINT/GEO buttons --
    def sigFunc_add_joint_to_db_btn(self):
        self.view.add_geo_btn.setEnabled(True)
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
                    self.active_db, jnt_uuid_dict, self.model.active_db_dir
                    )
                self.jnt_rShip_row = update_jnt_db.get_new_row()
                print(f"update_jnt_row!: {self.jnt_rShip_row}")
                self.model.visualise_active_db()
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
                    geo_uuid_dict, self.model.active_db_dir
                    )
                self.model.visualise_active_db()
            else: # once the joint had been selected in the treeview Ui
                print(f"Adding GEO to existing row!")
                result = self.model.get_sel_jnt_index_and_uuid()
                if result:
                    row_index, joint_uuid = result
                    print(f"joint selected in treeView = {joint_uuid}")
                    print(f"joint row_index in treeView = {row_index}")
                    # from uuid, return row
                    '''
                    retrieved_row = database_schema_001.Retrieve_UUID_Database_from_row(
                    database_name=self.active_db, row_id=row_index+1, directory=self.model.active_db_dir
                    )
                    '''
                    # add geo 
                    database_schema_001.UpdateGeoDatabase(
                        row_index+1, self.active_db, geo_uuid_dict, self.model.active_db_dir
                        )
                    self.model.visualise_active_db()
                else:
                    print(f"add geo to existing: error selecting existing joint")
        except Exception as e:
            print(f"add_geo_to_db_btn ERROR: {e}")
        self.view.new_relationship_checkBox.setChecked(False)
    
    
    def sigFunc_add_jnt_to_db_btn(self):
        print(f"sigFunc_add_jnt_to_db_btn CLICKED!!")
        jnt_parent_name = utils.get_selected_parent_name(self.view.joint_tree_view, self.view.joint_model)
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
                result = self.model.get_sel_jnt_index_and_uuid()
                if result:
                    row_index, joint_uuid = result
                    print(f"joint selected in treeView = {joint_uuid}")
                    print(f"joint row_index in treeView = {row_index}")
                    database_schema_001.UpdateJointDatabase(
                    self.active_db, joint_uuid_dict, self.model.active_db_dir, 
                    jnt_parent_num
                    )
                    self.model.visualise_active_db()
                else:
                    print(f"add joint to existing row: error selecting existing joint")
        except Exception as e:
            print(f"add_jnt_to_db_btn ERRO: {e}")
        

    def sigFunc_new_relationship_checkBox(self):
        print(f"new_relationship_checkBox is checked cicked")
        self.val_new_relationship_checkBox = self.view.new_relationship_checkBox.isChecked()
        if self.val_new_relationship_checkBox:
            self.view.new_jnt_btn.setEnabled(True)
            self.view.add_geo_btn.setEnabled(False)
            self.view.add_jnt_btn.setEnabled(False)
        else:
            self.view.new_jnt_btn.setEnabled(False)
            self.view.add_geo_btn.setEnabled(True)
            self.view.add_jnt_btn.setEnabled(True)


    # -- Remove JOINT/GEO buttons --
    def sigFunc_rmv_rShip_checkBox(self):
        
        self.val_rmv_rShip_checkBox = self.view.rmv_rShip_checkBox.isChecked()
        if self.val_rmv_rShip_checkBox:
            print(f"rmv_rShip_checkBox YES")
            self.view.remove_relationship_btn.setEnabled(True)
            self.view.rmv_geo_btn.setEnabled(False)
            self.view.rmv_jnt_btn.setEnabled(False)
        else:
            print(f"rmv_rShip_checkBox NO")
            self.view.remove_relationship_btn.setEnabled(False)
            self.view.rmv_geo_btn.setEnabled(True)
            self.view.rmv_jnt_btn.setEnabled(True)


    def sigFunc_remove_relationship_btn(self):
        print("clicked remove_relationship_btn")
        try:
            jnt_parent_name = utils.get_selected_parent_name(self.view.joint_tree_view, self.view.joint_model)
            print(f"relationship_name = {jnt_parent_name}")
            db_row_id = jnt_parent_name.split('_')[-1]

            database_schema_001.DeleteRelationshipFromDatabase(self.active_db, self.model.active_db_dir, db_row_id)
        except:
            print(f"Error: Need to SELECT relationship parent in JOINT TreeView!")
        self.model.visualise_active_db()
        
    
    def sigFunc_rmv_geo_btn(self):
        # cancel the operation if joints are selected!
        result = self.model.get_geo_name_and_uuid_TreeSel()
        if result:
            geo_name, geo_uuid = result
            print(f"geo_name = {geo_name} & geo_uuid = {geo_uuid}")
            database_schema_001.RemoveSpecificDATAfromDB(
                self.active_db, self.model.active_db_dir, "geo", geo_name, geo_uuid
                )
            self.model.visualise_active_db()
        else:
            print(f"in trying to REMOVE GEO, getting name & uuid failed.")


    def sigFunc_rmv_jnt_btn(self):
        print(f"Remove joint button selected")
        # cancel operation if selection isn't a specific joint!
        result = self.model.get_sel_jnt_name_and_uuid()
        if result:
            joint_name, joint_uuid = result
            print(f"joint_row = {joint_name} & joint_uuid = {joint_uuid}")
            database_schema_001.RemoveSpecificDATAfromDB(
                self.active_db, self.model.active_db_dir, "joint", joint_name, joint_uuid
                )
            self.model.visualise_active_db()
    