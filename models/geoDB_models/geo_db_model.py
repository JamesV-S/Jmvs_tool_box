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

class GeometryDatabaseModel:
    def __init__(self):
        self.custom_uuid_attr = "custom_UUID"
        # return_geo_uuid_from_db()
        self.db_row_id = ""

        # gather_active_database_combined_dict()
        self.active_db = ""
        self.active_db_dir = ""
        
        # visualise_active_db()
        self.joint_model = None #""
        self.geo_model = None #""

        # signal_to_geo_tree_highlight()
        self.geo_tree_view = ""
        self.joint_tree_view = ""


    def return_geo_uuid_from_db(self, db_row_id):
        uuids =  database_schema_001.ReturnRelationshipUUIDFromDatabase(
                obj_type="geo", database_name=self.active_db, 
                directory=self.active_db_dir, db_row_id=db_row_id
                )
        return uuids
    

    def update_database_ComboBox(self, database_comboBox):
        print(f"UPDATING DB COMBO BOX WITH NEW database!")
        self.db_files_update = []
        for directory in self.directory_list:
            if os.path.exists(directory):
                for db_file_name in os.listdir(directory):
                    if db_file_name.endswith('.db'):
                        self.db_files_update.append(db_file_name)
        database_comboBox.clear()
        database_comboBox.addItems(self.db_files_update)
        database_comboBox.setPlaceholderText("Updated Databases Added")
    

    # Tree view functions -----------------------------------------------------
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
        
    
    # Skinning functions ------------------------------------------------------
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
            


    
    
        
    