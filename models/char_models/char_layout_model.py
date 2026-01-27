# ------------------------------ MODEL ----------------------------------------
import importlib
import os.path
import maya.cmds as cmds
# import pymel.core as pm
import json

try:
    from PySide6 import QtCore, QtWidgets, QtGui
except ModuleNotFoundError:
    from PySide2 import QtCore, QtWidgets, QtGui

from utils import (
    utils,
    utils_os,
    utils_json,
    utils_QTree
)

from databases.char_databases import (
    database_schema_002
    )

from databases import (
    db_connection_tracker
)

from systems.sys_char_rig import (
    raw_data_fkik_dicts
)

importlib.reload(utils)
importlib.reload(utils_os)
importlib.reload(utils_json)
importlib.reload(utils_QTree)
importlib.reload(database_schema_002)
importlib.reload(db_connection_tracker)
importlib.reload(raw_data_fkik_dicts)


class CharLayoutModel:
    def __init__(self):        
        self.db_rig_location = "db_rig_storage"
        self.rig_db_storage_dir = utils_os.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", "db_rig_storage"
            )
        self.json_dict = utils_json.get_modules_json_dict('char_config')

    # ---- TreeView functions ----
    def load_rig_group(self, val_availableRigComboBox):
        # rig_syntax "jmvs_char*_rig" - DB_jmvs_cyborg_rig
        print(f"GEORGE | val_availableRigComboBox == {val_availableRigComboBox}")
        rig_name = val_availableRigComboBox.replace("DB_", "")
        if not cmds.objExists(rig_name):
            try:
                utils.create_rig_group(rig_name)
            except Exception as e:
                print(e)
        else:
            print(f"rig_group `{rig_name}` already exists in the scene")


    def get_available_DB_rig_folders(self, location):
            name_of_rig_fld = []
            self.rig_db_storage_dir = utils_os.create_directory("Jmvs_tool_box", "databases", "char_databases", location)
            if os.path.exists(self.rig_db_storage_dir):
                print(f"Dir does exist: {self.rig_db_storage_dir}")
                for db_rig_folder in os.listdir(self.rig_db_storage_dir):
                    if db_rig_folder.startswith("DB_jmvs_"):
                        name_of_rig_fld.append(db_rig_folder)
                        print(f"RIG Folder(s): {db_rig_folder}")
                    elif not db_rig_folder.startswith("DB_jmvs_"):
                        print(f"NOT a rig folder: {db_rig_folder}")
            else:
                print(f"Dir doesn't exist: {self.rig_db_storage_dir}")
            return name_of_rig_fld
    

    def retrieve_component_dict_from_nameSel(self, val_availableRigComboBox,  module_selection_name):
        # mdl_spine_0 : mdl_MODULE*_uniqueID*_side*
        # split the name 
        split_names = module_selection_name.split('_')[1:] #ignore 'mdl' prefix
        module = split_names[0]
        unique_id = split_names[1]
        try: # handle if it has no side
            side = split_names[2]
        except Exception:
            side = "M" #use M to represent middle (but doesn't show up in scene)
            # Or whatever it needs to be in the database! 
        print(f"split_names: module = {module}, unique_id = {unique_id}, side = {side}")
        
        # gather dict from database!
        print(f"MODEL | val_availableRigComboBox = {val_availableRigComboBox}")
        rig_folder_name = val_availableRigComboBox
        print(f"rig_folder_name = {rig_folder_name}")
        rig_db_directory = utils_os.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", 
            self.db_rig_location, rig_folder_name
            )
        print(f"rig_db_directory = {rig_db_directory}")
        retrieve_mdl_component_dict = database_schema_002.RetrievePlacementData(rig_db_directory, module, unique_id, side)
        mdl_component_dict = retrieve_mdl_component_dict.return_mdl_component_dict()
        print(f"mdl_component_dict = {mdl_component_dict}")
        return mdl_component_dict


    # ---- TreeView 'Record Live Component' functions ----
    def record_component_position(self, component_selection, val_availableRigComboBox):
        module, unique_id, side = utils.get_name_id_data_from_component(component_selection)
        find_guide = f"xfm_guide_{module}_*_{unique_id}_{side}"

        try:
            cmds.select(find_guide)
            guides = cmds.ls(sl=1, type="transform")
            # gather the positions of the live compnent!
            new_component_pos_dict = utils.get_selection_trans_dict(guides, side)
            print("new_component_pos: ", new_component_pos_dict)
            ''' got this dict `B` from selection in treeView '''
            ''' if ^ = {} cancel the operation below. '''
            ''' get this dict `A` from the correct row in the right db '''
            ''' compare `B` to `A`, find the same name 'clavicle', ect, and put the new values in it.
            '''
            print(f"MODEL | val_availableRigComboBox = {val_availableRigComboBox}")
            rig_folder_name = val_availableRigComboBox
            print(f"rig_folder_name = {rig_folder_name}")
            rig_db_directory = utils_os.create_directory(
                "Jmvs_tool_box", "databases", "char_databases", 
                self.db_rig_location, rig_folder_name
                )
            retrieved_existing_dict = database_schema_002.RetrievePlacementData(
                rig_db_directory, module, unique_id, side
                )
            existing_pos_dict = retrieved_existing_dict.return_existing_pos_dict()
            print(f"existing_pos_dict = {existing_pos_dict}")

            updated_existing_pos_dict = {}
            for key in existing_pos_dict.keys():
                for new_key, new_value in new_component_pos_dict.items():
                    if key in new_key:
                        updated_existing_pos_dict[key] = new_value
                        updated_dict = True
                        break
                    else:
                        updated_dict = False
            if updated_dict:
                print(f"Updated `existing_dict` : {updated_existing_pos_dict}")
                ''' with new dict, update the database! '''
                database_schema_002.UpdateSpecificPlacementPOSData(
                    rig_db_directory, module, unique_id, side, updated_existing_pos_dict
                    )
            
        except Exception as e:
            print(f"No component exists in the scene of '{component_selection}'")
            print(f"error: {e}")
        cmds.select(cl=1)


    def record_compnonent_orientation(self, component_selection, val_availableRigComboBox):
        module, unique_id, side = utils.get_name_id_data_from_component(component_selection)
        try:            
            # need to get the list of available ori guides in correct order
            rig_db_directory = utils_os.create_directory(
                "Jmvs_tool_box", "databases", "char_databases", 
                self.db_rig_location, val_availableRigComboBox
                )
            retrieve_rot_data = database_schema_002.RetrievePlacementData(
            rig_db_directory, module, unique_id, side)
            
            # Establish the ori guides for the component
            comp_rot_dict = retrieve_rot_data.return_existing_rot_dict()
            ori_guides_keys = [key for key, rot in list(comp_rot_dict.items())]
            ori_guides = [f"ori_{module}_{ori_guides_keys[x]}_{unique_id}_{side}" for x in range(len(ori_guides_keys))]
            print(f"ORI record: ori_guides = `{ori_guides}`")
            
            # Get rot  
            new_component_rot_dict = utils.get_selection_rot_dict(ori_guides[:-1])
            print(f"ORI recording: new_component_rot_dict = `{new_component_rot_dict}`")
 
            # Copy the data of 'second to last' ori guide and paste it to the last ori guide in the stored dict!
            new_component_rot_dict[ori_guides[-1]] = new_component_rot_dict[ori_guides[-2]]
            print(f"NEW ORI recording: new_component_rot_dict = `{new_component_rot_dict}`")

            # -- Orientation data --
            # Update the database with just the keys as the keys and not the name of ori!
            updated_rot_dict = {}
            for key in comp_rot_dict.keys():
                for new_key, new_value in new_component_rot_dict.items():
                    if key in new_key:
                        updated_rot_dict[key] = new_value
            print(f"ORI UPDATE - updated_rot_dict = `{updated_rot_dict}`")
            
            # -- Planes data --
            # update the geo planes dict too!
            plane_object_list = ori_guides[:-1]
            new_geo_plane_dict = utils.get_sel_ori_plane_dict(plane_object_list, "Planes_Scale")
            updated_plane_dict = {}
            for key in comp_rot_dict.keys():
                for new_key, new_value in new_geo_plane_dict.items():
                    if key in new_key:
                        updated_plane_dict[key] = new_value

            # update the database with these two updated dictionary's!
            database_schema_002.UpdatePlacementROTData(
                rig_db_directory, module, unique_id, side, 
                updated_rot_dict, updated_plane_dict
                )
            
        except Exception as e:
            print(f"No component exists in the scene of '{component_selection}'")
            print(f"error: {e}")
        cmds.select(cl=1)
    

    def update_component_fkik_control_dicts(self, component_selection, val_availableRigComboBox):
        '''
        # Description:
            Update the component's database with by cl;acualting NEW fk/ik_pos/rot 
            raw data! 
        # Arguments:
            component_selection (string): Name of the selected component on GUI.
            val_availableRigComboBox (string): Name of the folder the .db file 
            of this component resides in.
        # Returns: N/A 
        '''
        module, unique_id, side = utils.get_name_id_data_from_component(component_selection)
        rig_db_directory = utils_os.create_directory(
                        "Jmvs_tool_box", "databases", "char_databases", 
                        self.db_rig_location, val_availableRigComboBox
                        )
        # retrun constant_dict
        retrieve_constant_data = database_schema_002.RetrieveConstantData(rig_db_directory, module, unique_id, side)
        limbRoot_name_attr = retrieve_constant_data.return_limbRoot_name()
        hock_name_attr = retrieve_constant_data.return_hock_name()
        ik_wld_name_attr = retrieve_constant_data.return_ik_wld_name()
        print(f"MODEL fkik: limbRoot_name_attr = {limbRoot_name_attr}")
        print(f"MODEL fkik: hock_name_attr = {hock_name_attr}")
        print(f"MODEL fkik: ik_wld_name_attr = {ik_wld_name_attr}")
        const_attr_dict = {
            "limbRoot_name":retrieve_constant_data.return_limbRoot_name(),
            "hock_name":retrieve_constant_data.return_hock_name(),
            "ik_wld_name":retrieve_constant_data.return_ik_wld_name()
        }
        print(f"MODEL fkik: const_attr_dict = {const_attr_dict}")

        # return placement_dict
        retrieve_placement_data = database_schema_002.RetrievePlacementData(rig_db_directory, module, unique_id, side)
        component_pos_dict = retrieve_placement_data.return_existing_pos_dict()
        component_rot_dict = retrieve_placement_data.return_existing_rot_dict()
        controls_typ_dict = retrieve_placement_data.return_controls_typ_dict()
        print(f"MODEL fkik: component_pos_dict = {dict(component_pos_dict)}")

        # Get constant attr dict
        constant_attr_dict = utils.get_constant_attr_from_constant_dict(const_attr_dict)
        # Get fkik contrrol raw dicts 
        raw_fkik_data = raw_data_fkik_dicts.RawDataFkIKDicts(
                        controls_typ_dict['FK_ctrls'], controls_typ_dict['IK_ctrls'],
                        component_pos_dict, component_rot_dict,
                        constant_attr_dict, unique_id, side)
        fk_pos, fk_rot, ik_pos, ik_rot = raw_fkik_data.return_RawDataFkIKDicts()

        print(f"MODEL fkik: ik_rot = {ik_rot}")

        # update database with the dicts
        database_schema_002.UpdateControlsRawData(rig_db_directory, module, unique_id, side, 
                                                  fk_pos, fk_rot, ik_pos, ik_rot)


    def visualise_active_db(self, val_availableRigComboBox, mdl_tree_model):
        '''
        # Description:
        Update the gui with module information that is present in the database.
        The ui container that are updated are:
            -> 'Character Database' (QTreeView)
            -> 'External Input Hook' (QListView)
            -> 'Output Hook' (QListView)
        # Arguments:
            val_availableRigComboBox (string): Name of the rig grp that stores 
                                                all .db files for each module 
                                                of the rig.
            mdl_tree_model (QTreeModel): Model of the tree view.
        # Data structures (The data created in this function):
             db_data (dict): keys = 'DB_*{module_name}.db' : 
                             vals = [(unique_id, side, for each component), etc, ]
                example: 
                    {
                    'DB_bipedArm.db': [(0, 'L'), (0, 'R')], 
                    'DB_quadArm.db': [(0, 'L')]
                    }

        '''
        # get directory of current chosen rig folder!
        rig_db_directory = utils_os.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", 
            self.db_rig_location, val_availableRigComboBox
            )
        # gather a list of database found in the folder: 
        db_names = []
        db_data = {}
        if os.path.exists(rig_db_directory):
            for db in os.listdir(rig_db_directory):
                if db.startswith("DB_") and db.endswith(".db"):
                    db_names.append(db)
                    
                    # get the table data `modules` from each database
                    # query the unique_id & side from each row
                    # store into a dictionary to pass to pop `populate_char_db_QTreeView_model()`
                    data_retriever = database_schema_002.RetrieveModulesData(
                        rig_db_directory, db)
                    db_data[db] = data_retriever.db_data_iteraion.get(db, [])    
                else:
                    print(f"NO database file found in:{rig_db_directory}")
        else:
            print(f"directory does NOT exist: {rig_db_directory}")
        
        print(f" * 'visualise_active_db(): 'db_data = {db_data}")
        '''
        
        '''

        
        
        # add all databases to the treeView
        self.populate_char_db_QTreeView_model(mdl_tree_model, val_availableRigComboBox, db_data)
        

    def populate_char_db_QTreeView_model(self, mdl_tree_model, rig_folder_name, db_data):
        '''
        # Description:
            Add items to the QTreeView model. Items being the module name & 
            components within it.
        # Arguments:
            mdl_tree_model (QTreeModel): Model of the tree view.
            rig_folder_name (string): Name of the rig folder for debugging & 
            printing purposes only.
            db_data (dict): keys = 'DB_*{module_name}.db' : 
                            vals = [
                                (unique_id, side, for each component), etc,
                                ]
        # Reuturn: N/A 
        '''
        # clear the treeView's model (ie, the items in it) everytime the active 
        # db is switched.
        mdl_tree_model.clear()
        
        tree_parent_item = mdl_tree_model.invisibleRootItem()
        
        if not db_data:
            # NO module data in the dictionary 'db_data'
            print(f"NO databases in the folder `{rig_folder_name}`")
        else:
            print(f"found databases '{list(db_data.keys())}' in the folder `{rig_folder_name}`")
            try:
                for db_name, rows in db_data.items():
                    db_base_name = db_name.replace("DB_", "").replace(".db", "")
                    db_item = QtGui.QStandardItem(f"{db_base_name}")
                    db_item.setData(True, QtCore.Qt.UserRole)

                    for unique_id, side in rows:
                        item_name = f"mdl_{db_base_name}_{unique_id}_{side}"
                        mdl_item = QtGui.QStandardItem(item_name)
                        mdl_item.setData(False, QtCore.Qt.UserRole)
                        db_item.appendRow(mdl_item)
                        
                    tree_parent_item.appendRow(db_item)
            except Exception as e:
                    print(f"If you just created a new db, ignore this error, if not: {e}")
    

    def populate_ext_input_hook_QListView_model(self):
        '''
        # Description:
            Add items to the QTreeView model. Items being the module name & 
            components within it.
        # Arguments:
        # Reuturn: N/A 
        '''


    # ---- json data functions ----  
    def cr_mdl_json_database(self, val_availableRigComboBox, mdl_name, checkBox, iterations, side): # handles a single module at a time
            print(f"OIIIIIIIIIIIIIII self.json_data  == {self.json_dict}, `mdl_name` = {mdl_name}")     
            placement_dict = {}
            user_settings_dict = {}
            controls_dict = {}
            for key, values in self.json_dict.items():
                if key == f"{mdl_name}.json":
                    mdl_object_list = values['names']
                    placement_dict =  values['placement']
                    constant_dict = values['constant']
                    user_settings_dict =  values['user_settings']
                    controls_dict =  values['controls']
            print(f"constant_dict >> {constant_dict}")
            print(f"mdl_object_list >> {mdl_object_list}")
            print(f"placement_dict >> {placement_dict}")
            print(f"user_settings_dict >> {user_settings_dict}")
            print(f"controls_dict >> {controls_dict}")
            mdl_directory = os.path.join(self.rig_db_storage_dir, val_availableRigComboBox)
            # create the database!
            if checkBox:
                for db in range(iterations):
                    database_schema = database_schema_002.CreateDatabase(
                        mdl_directory, mdl_name, side, mdl_object_list,
                        placement_dict, constant_dict, user_settings_dict, controls_dict)
            
            
                # unique_id = database_schema.get_unique_id()
                # print(f"unique_id == {unique_id} for {mdl_name}_{side}")
                # import and call the database maker 'database_schema'
            else:
                print(f"Not required module database creation for {mdl_name}")

            '''
            placement_dict >> 
            {'component_pos': 
                {'clavicle': [3.9705319404602006, 230.650634765625, 2.762230157852166], 
                'shoulder': [28.9705319404602, 230.650634765625, 2.762230157852166], 
                'elbow': [53.69795846939088, 197.98831176757807, 6.61050152778626], 
                'wrist': [76.10134363174441, 169.30845642089832, 30.106774568557817]
                }, 
            'component_rot': {'clavicle': [0.0, 0.0, 0.0], 'shoulder': [0.0, 0.0, 0.0], 'elbow': [0.0, 0.0, 0.0], 'wrist': [0.0, 0.0, 0.0]}, 'component_rot_yzx': {'clavicle': [0.0, 0.0, 0.0], 'shoulder': [0.0, 0.0, 0.0], 'elbow': [0.0, 0.0, 0.0], 'wrist': [0.0, 0.0, 0.0]}}

            '''


    def func_unlocked_all(self, component_selection, val_availableRigComboBox):
        for component in component_selection:
            self.guide_connections_setup(component, val_availableRigComboBox)
    

    # ---- Component constraints ----   
    def guide_connections_setup(self, component, val_availableRigComboBox):
        module, unique_id, side = utils.get_name_id_data_from_component(component)
        print(f"guide_connections :component: {component} ")
        rig_db_directory = utils_os.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", 
            self.db_rig_location, val_availableRigComboBox
            )
        get_guides_connection = database_schema_002.RetrieveSpecificData(rig_db_directory, module, unique_id, side)
        guides_connection_ls = get_guides_connection.return_guides_connection()
        guides_follow_ls = get_guides_connection.return_guides_follow()
        print(f"J > module = {module}")
        print(f"J > guides_connection_ls = {guides_connection_ls}")
        print(f"J > guides_follow_ls = {guides_follow_ls}")
        
        if guides_connection_ls:
            for item in guides_connection_ls:
                key = item["key"]
                typ = item["typ"]
                constrained = item["constrained"]
                values = self.get_values(item["attr"])
                
                part = key.split('_')[0]
                if cmds.objExists(f"xfm_grp_{part}_component_*_*"):
                    print(f"J connections working")
                    other_comp_grp = cmds.ls(f"xfm_grp_{part}_component_*_*")[0] # xfm_grp_root_component_0_M
                    print(f"other_comp_grp = {other_comp_grp}")
                    parts = other_comp_grp.split("_")
                    other_comp = f"mdl_{part}_{parts[4]}_{parts[5]}" # mdl_root_0_M
                    other_mdl, other_unique_id, mirror_side = utils.get_name_id_data_from_component(other_comp)
            
                    print(f"xfm_guide_{other_mdl}_{other_unique_id}_{mirror_side}")
                    print(f"constraining `offset_xfm_guide_{module}_{constrained}_{unique_id}_{side}`")
                    print(f"with type = `{typ}`")
                    print(f"with values = `{values}`")
                    utils.constrain_2_items(
                        f"xfm_guide_{key}_{other_unique_id}_{mirror_side}",
                        f"offset_xfm_guide_{module}_{constrained}_{unique_id}_{side}", 
                        f"{typ}", f"{values}")
                else:
                    print(f"J connections NOT working")

        '''{"key": "spine0", "typ":"parent", "constrained":"spine1", "attr":{"all": true}}'''
        if guides_follow_ls:
            for item in guides_follow_ls:
                key = item["key"]
                typ = item["typ"]
                constrained = item["constrained"]
                values = self.get_values(item["attr"])
                
                print(f"HERE > with values = `{values}`")

                utils.constrain_2_items(
                    f"xfm_guide_{module}_{key}_{unique_id}_{side}",
                    f"offset_xfm_guide_{module}_{constrained}_{unique_id}_{side}", 
                    f"{typ}", f"{values}")


    def get_values(self, attr):
        if attr.get('all', False):
            return "all"
        else:
            # Extract the axes that are false and return the remaining axes
            axes = ["X", "Y", "Z"]
            skip_axes = [axis for axis in axes if not attr.get(axis, True)]
            return skip_axes
        

    # ---- Control data recording ----

    def store_component_control_data(self, component_selection, val_availableRigComboBox):
        module, unique_id, side = utils.get_name_id_data_from_component(component_selection)
        #  func to return list of controls. Arg = component_selection is handled in tge database operation
        # SO get curve data for each control
        # then put this data that's returned back into the 'curve_info' column, looking like this:  
        rig_db_directory = utils_os.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", 
            self.db_rig_location, val_availableRigComboBox
            )
        get_control_names = database_schema_002.CurveInfoData(rig_db_directory, module, unique_id, side)
        control_names_ls = get_control_names.return_comp_ctrl_ls()
        control_data_dict = {}
        # check if the object exist in the scene
        if cmds.objExists(control_names_ls[0]):
            for each_control in control_names_ls:
                data = utils.record_ctrl_data(each_control)
                control_data_dict[each_control] = data            
            # Now update the database with the newly stored control data!
            database_schema_002.UpdateCurveInfo(rig_db_directory, module, unique_id, side, control_data_dict)
        else:
            cmds.warning(f"Make sure the component `{component_selection}` exists in the scene with the controls, cus CANNOT find any")


    def select_component_data(self, comp, val_availableRigComboBox, all_checkbox, ik_checkbox, fk_checkbox, ori_guide_checkbox, xfm_guide_checkbox):
        module, unique_id, side = utils.get_name_id_data_from_component(comp)
        rig_db_directory = utils_os.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", 
            self.db_rig_location, val_availableRigComboBox
            )
        get_control_names = database_schema_002.CurveInfoData(rig_db_directory, module, unique_id, side)
        control_names_ls = get_control_names.return_comp_ctrl_ls()
        print(control_names_ls)
        access_data = database_schema_002.RetrievePlacementData(
            rig_db_directory, module, unique_id, side)
        comp_dict = access_data.return_mdl_component_dict()
        get_names_dict = comp_dict["component_pos"]
        
        ctrl_name_ls = [ctrl for ctrl in control_names_ls]
        if all_checkbox:
            cmds.select(ctrl_name_ls, add=1)
        elif not all_checkbox:
            cmds.select(ctrl_name_ls, d=1)
        else:
            # select ik or fk or both. 
            for mode in [ik_checkbox, fk_checkbox]:
                if mode == 'ik': # need to return this or 'None'
                    for ctrl in control_names_ls:
                        if ctrl.startswith("ctrl_ik"):
                            cmds.select(ctrl, tgl=1)
                elif mode == 'fk':
                    for ctrl in control_names_ls:
                        if ctrl.startswith("ctrl_fk"):
                            cmds.select(ctrl, tgl=1)
        
        ori_name_ls = [f"ori_{module}_{ori}_{unique_id}_{side}" for ori in get_names_dict.keys()]
        xfm_name_ls = [f"xfm_guide_{module}_{xfm}_{unique_id}_{side}" for xfm in get_names_dict.keys()]
        # for ori in get_names_dict.keys():
        #         ori_name = f"ori_{module}_{ori}_{unique_id}_{side}"

        if ori_guide_checkbox:
            cmds.select(ori_name_ls[:-1], add=1)
        if not ori_guide_checkbox:
            cmds.select(ori_name_ls, d=1)
        if xfm_guide_checkbox:
            cmds.select(xfm_name_ls, add=1)
        if not xfm_guide_checkbox:
            cmds.select(xfm_name_ls, d=1)

    
    def mirror_component_data(self, component_selection, val_availableRigComboBox, mdl_tree_model, val_ctrl_crv_edit_checkbox, val_guide_crv_edit_checkBox):
        module, unique_id, side = utils.get_name_id_data_from_component(component_selection)
        rig_db_directory = utils_os.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", 
            self.db_rig_location, val_availableRigComboBox
            )
        
        if side == 'M':
            middle_comp = True
        elif side == 'L':
            middle_comp = False
            mirror_side = "R"
        elif side == 'R':
            middle_comp = False
            mirror_side = "L"

        if not middle_comp:
            # check if the databse exists:
            # Check if the database component exists or not
            get_db_data = database_schema_002.CheckMirrorData(rig_db_directory, module, unique_id, mirror_side)
            mirror_comp_exists = get_db_data.return_mirror_database_exists()

            print(f"Model > mirror database exists:  `{mirror_comp_exists}`")

            if not mirror_comp_exists:
                # placement_dict = {}
                # user_settings_dict = {}
                # controls_dict = {}
                for key, values in self.json_dict.items():
                    if key == f"{module}.json":
                        mdl_object_list = values['names']
                        mirror_placement_dict =  values['placement']
                        mirror_constant_dict = values['constant']
                        mirror_user_settings_dict =  values['user_settings']
                        mirror_controls_dict =  values['controls']
                        print(f"mirror_placement_dict = {mirror_placement_dict}")
                        database_schema_002.CreateDatabase(
                            rig_db_directory, module, mirror_side, mdl_object_list, mirror_placement_dict, 
                            mirror_constant_dict, mirror_user_settings_dict, mirror_controls_dict)
                    
            # update the databse with the gathered data!
            if val_ctrl_crv_edit_checkbox:
                # retirvs the colour too. i don't want the colour!
                get_control_names = database_schema_002.CurveInfoData(rig_db_directory, module, unique_id, side)
                curve_info_dict = get_control_names.return_curve_info_dict()
                mirror_control_data_dict = {}
                for key, value in curve_info_dict.items():
                    new_key = key.replace(f"{unique_id}_{side}", f"{unique_id}_{mirror_side}")
                    if 'colour' in value:
                        value['colour'] = 6
                    mirror_control_data_dict[new_key] = value
                print(f"mirrored curve_info_dict = {mirror_control_data_dict}")
                database_schema_002.UpdateCurveInfo(rig_db_directory, module, unique_id, mirror_side, mirror_control_data_dict)

            if val_guide_crv_edit_checkBox:
                # need the positional data of the current component!
                retrieved_existing_dict = database_schema_002.RetrievePlacementData(
                    rig_db_directory, module, unique_id, side)
                existing_pos_dict = retrieved_existing_dict.return_existing_pos_dict()
                existing_rot_dict = retrieved_existing_dict.return_existing_rot_dict()
                existing_plane_dict = retrieved_existing_dict.return_existing_plane_dict()
                # Must invert the x value!!
                '''
                {'clavicle': [0.0, 0.0, 0.0], 
                'shoulder': [2.9407037031303735, -5.366417614476933, -52.87199475566796], 
                'elbow': [1.4116820605103142, -32.847391136978864, -52.004681579832805], 
                'wrist': [1.4116820605103142, -32.847391136978864, -52.004681579832805]}
                '''

                
                print(f"MIRROR: ORI: existing_rot_dict = {existing_rot_dict}")
                # mirror
                # apply these to the mirrored component
                database_schema_002.UpdateSpecificPlacementPOSData(
                    rig_db_directory, module, unique_id, mirror_side, existing_pos_dict
                    )
                database_schema_002.UpdatePlacementROTData(
                    rig_db_directory, module, unique_id, mirror_side, existing_rot_dict, existing_plane_dict)


    def commit_module_edit_changes(self, component, val_availableRigComboBox, val_joint_editing_checkBox, val_ctrl_editing_checkBox, jnt_num):
        module, unique_id, side = utils.get_name_id_data_from_component(component)
        rig_db_directory = utils_os.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", 
            self.db_rig_location, val_availableRigComboBox
            )
        
        print(f"Module = `{module}`, unique_id = `{unique_id}`, side = `{side}`")
 
        # update the user_settings DB
        ''' if val_update_comp_data_checkBox:
            print(f"update modu;e l editing model functions running")
            database_schema_002.UpdateUserSettings(rig_db_directory, module, unique_id, side, umo_dict)'''
        # get the value in the db!
        if val_joint_editing_checkBox:
            print(f"joint editing model functions running")
            user_settings_data = database_schema_002.RetrieveSpecificData(rig_db_directory, module, unique_id, side)
            DB_joint_num = user_settings_data.return_get_jnt_num()
            # True if we want to proceed!
            if not DB_joint_num == "NULL": # Don't manipulate the number of joints!
                database_schema_002.UpdateJointNum(rig_db_directory, module, unique_id, side, jnt_num)
        if val_ctrl_editing_checkBox:
            print(f"ctrl editing model functions running")
        

    # ---- Orientation guides functions ----
    def align_orientation_to_last(self, guide_selection):
        '''
        # Description:
        Call util functions to set the X (first item of a rotation list) of 
        selected ori_guides to the same as the last orig_guide in the list
        # Arguments:
            guide_selection (list): Selected ori_guides in the scene. 
        # Returns: N/A 
        '''
        ori_rot_dict = utils.get_selection_rot_dict(guide_selection)
        utils.align_source_rotX_to_target(ori_rot_dict)


    # ---- External Input Hook Matrix functions ----
    '''
    There is a hierarchy for the UI widget's change:
    - inp_hk_mtx_QList (clicked)
        |- inp_hk_mtx_CB_obj (Current Index Change)
            |- inp_hk_mtx_CB_prim (Current Index Change & Items Change)
            |- inp_hk_mtx_CB_scnd (Current Index Change & Items Change)
    '''

    def get_db_inp_hook_mtx_from_Qlist(self, component_name, val_availableRigComboBox):
        '''
        # Description: 
            Get the `external input_hook_mtx_plg list` from selected component db: `[*object.*attr]`
        # Arguments:
            component_name (string): Name of the component in .db file to retirve data from. 
            val_availableRigComboBox (string): Name of the current rig database folder.
        # Return: 
            db_inp_hook_mtx_ls (list): [*object.*attr]
        '''
        module, unique_id, side = utils.get_name_id_data_from_component(component_name)
        rig_db_directory = utils_os.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", 
            self.db_rig_location, val_availableRigComboBox
            )
        get_user_settings_data = database_schema_002.RetrieveSpecificData(rig_db_directory, module, unique_id, side)
        db_inp_hook_mtx_ls = get_user_settings_data.return_inp_hk_mtx()

        return db_inp_hook_mtx_ls


    def get_db_out_hook_mtx_from_comboBox(self, ext_obj_component_name, val_availableRigComboBox):
        '''
        # Description: 
            Get the `output_hook_mtx_list` from .db file using `object QComboBox` 
            as the component name.
        # Arguments:
            ext_obj_component_name (string): Name of the component in .db file to retirve data from. 
            val_availableRigComboBox (string): Name of the current rig database folder.
        # Return: 
            db_out_hook_mtx_ls (list): [*attr, *attr]
        '''
        module, unique_id, side = utils.get_name_id_data_from_component(ext_obj_component_name)
        rig_db_directory = utils_os.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", 
            self.db_rig_location, val_availableRigComboBox
            )
        get_user_settings_data = database_schema_002.RetrieveSpecificData(
            rig_db_directory, module, unique_id, side
            )
        db_out_hook_mtx_ls = get_user_settings_data.return_out_hk_mtx()

        return db_out_hook_mtx_ls


    def get_inp_hook_mtx_obj_data(self, db_inp_hook_mtx_ls):
        '''
        # Description: 
            Seperate the object & attr from the `external input_hook_mtx_plg list`.
        # Arguments:
            db_inp_hook_mtx_ls (list): [*object.*attr] is `external input_hook_mtx_plg list`.
        # Return: 
            ext_obj_ls (list): Object of the `external input_hook_mtx_plg list`
            ext_atr_ls (list): Attr's of the `external input_hook_mtx_plg list`
        '''
        ext_obj_ls = []
        ext_atr_ls = []
        for inp_plg in db_inp_hook_mtx_ls:
            parts = inp_plg.split('.')
            obj = parts[0]
            atr = parts[-1]
            ext_obj_ls.append(obj)
            ext_atr_ls.append(atr)
        
        # ext_obj_ls should only ever hold 1 module name (cus more than 1 means a duplicate)
        if len(ext_obj_ls) > 1:
            ext_obj_ls = ext_obj_ls[:1]

        return ext_obj_ls, ext_atr_ls


    def cr_out_hook_mtx_atr_dict(self, db_out_hook_mtx_ls):
        ext_atr_dict = {
            'ext_prim':"", 
            'ext_scnd':"", 
        }
        if len(db_out_hook_mtx_ls) > 1: # two items in the list
            prim_val = db_out_hook_mtx_ls[0]
            scnd_val = db_out_hook_mtx_ls[1]
        else:
            prim_val = db_out_hook_mtx_ls[0]
            scnd_val = 'None'
        ext_atr_dict['ext_prim'] = prim_val
        ext_atr_dict["ext_scnd"] = scnd_val
        print(f"ext_atr_dict = {ext_atr_dict}")
        return ext_atr_dict

    
    def set_inp_hook_obj_comboBox(self, Qlist_compnent_names, ext_obj_ls, view_cb_obj):
        print(f"*set_inp_hook_obj_comboBox: ext_obj_ls = {ext_obj_ls}")

        obj_match = None
        ext_inp_hk_comp_ls = []
        for obj in ext_obj_ls:
            if not ext_obj_ls == ['None']:
                for comp in Qlist_compnent_names:
                    if obj in comp: # if spine is an existing database
                        if obj == comp:
                            print(f"EXACT MATCH")
                            obj_match = True

                            ext_inp_hk_comp_ls.append(comp)
                        else:
                            print(f"NO EXACT MATCH")
                            obj_match = False
                            ext_inp_hk_comp_ls.append(comp)

                    # print(f"comp found in inp_hk_mtx obj {comp}")

        print(f"*set_inp_hook_obj_comboBox = ext_inp_hk_comp_ls = {ext_inp_hk_comp_ls}")

        # # if ext_inp_hk_comp_ls is more than one this means it did not find an exact match. 
        if obj_match == True:
            update_obj = ext_obj_ls[0]
        if obj_match == False:
            update_obj = ext_inp_hk_comp_ls[0]
        if obj_match == None:
            update_obj = 'None'

            # update obj comboBox
        print(f"Update obj = {update_obj}")
        # Set the cb to 'None' before setting again. 
        view_cb_obj.setCurrentText('None')
        view_cb_obj.setCurrentText(update_obj)


    def set_inp_hook_atrs_comboBox_items(self, external_atr_dict, view_cb_prim, view_cb_scnd):
        '''
        # Description:
            Add the possible external input hook attribute as items to the `prim` 
            & `scnd` QComboBox's using the dict `external_atr_dict`.
        # Arguments:
            external_atr_dict (dict): {keys: 'prim'/'scnd', values:*atr}
            view_cb_prim (QComboBox): primary external hook comboBox
            view_cb_prim (QComboBox): secondary external hook comboBox
        # Return: N/A
        '''
        view_cb_prim.clear()
        view_cb_scnd.clear()
        # view_cb_prim.addItem('None')
        view_cb_scnd.addItem('None')
        if external_atr_dict:
            view_cb_prim.addItem(external_atr_dict['ext_prim'])
            view_cb_prim.addItem(external_atr_dict['ext_scnd'])
            view_cb_scnd.addItem(external_atr_dict['ext_prim'])
            view_cb_scnd.addItem(external_atr_dict['ext_scnd'])


    def set_inp_hook_atrs_comboBox_placeholder(self, external_atr_dict, current_inp_atr_ls, view_cb_prim, view_cb_scnd):
        '''
        # Description:
            Set the current text of the prim & scnd QComboBox's using the dict 
            `current_inp_atr_ls` compared to the `external_atr_dict`.
        # Arguments:
            external_atr_dict (dict): {keys: 'prim'/'scnd', values:*atr}
            current_inp_atr_ls (list): Current component input hook attribute list.  
            view_cb_prim (QComboBox): primary external hook comboBox
            view_cb_prim (QComboBox): secondary external hook comboBox
        # Return: N/A
        '''
        # If the number of attributes in `current_inp_atr_ls` is greater than 1,
        # `prim` & `scnd` QComboBox's must both be filled.
        if len(current_inp_atr_ls) > 1:
            print(f" - {current_inp_atr_ls} > 1, so(prim & scnd must both be filled) ")
            view_cb_prim.setCurrentText(external_atr_dict['ext_prim'])
            view_cb_scnd.setCurrentText(external_atr_dict['ext_scnd'])
        else:
            # Otherwise, Need to add the `current_inp_atr_ls` if it ecists in 
            # `external_atr_list` (a list of the values from `external_atr_dict`).
            external_atr_list = [val for val in external_atr_dict.values()]
            print(f" - external_atr_list = {external_atr_list}")
            
            # check if the `current_inp_atr_ls` item exusts in `external_atr_list`
            current_prim_atr_check = False
            for ext_atr in external_atr_list:
                if current_inp_atr_ls[0] == ext_atr:
                    current_prim_atr_check = True
            
            # if `current_prim_atr_check` is True, set as follows...
            if current_prim_atr_check:
                view_cb_prim.setCurrentText(current_inp_atr_ls[0])
                view_cb_scnd.setCurrentText('None')
    

    def update_db_inp_hook_mtx_empty(self, component_name, val_availableRigComboBox):
        module, unique_id, side = utils.get_name_id_data_from_component(component_name)
        rig_db_directory = utils_os.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", 
            self.db_rig_location, val_availableRigComboBox
            )
        
        print(f" *- running update_db_inp_hook_mtx_empty()")
        print(f" *- Update component_name: {component_name}, inp_hk_mtx_ls: {['_None_']}")

        # # Problem > the prim atr resets to 1st item in it's list. WHEN THIS class IS RUN!
        # database_schema_002.UpdateMtxModuleDataEMPTY(
        #             directory=rig_db_directory,
        #             module_name=module,
        #             unique_id=unique_id,
        #             side=side,
        #             inp_hk_mtx_ls=['_None_'],
        #             )

        # when this class is run, there is no problem. 
        database_schema_002.TEST_(
            directory=rig_db_directory,
            module_name=module,
            unique_id=unique_id,
            side=side
        )


    def update_db_inp_hook_mtx(self, component_name, ext_obj_name, prim_atr, scnd_atr, val_availableRigComboBox):
        print(f" -- component_name = `{component_name}`")
        if not component_name == 'None':

            module, unique_id, side = utils.get_name_id_data_from_component(component_name)
            rig_db_directory = utils_os.create_directory(
                "Jmvs_tool_box", "databases", "char_databases", 
                self.db_rig_location, val_availableRigComboBox
                )
            
            upd_inp_hk_plg_ls = []

            if not prim_atr == None:
                scnd_plg = f"{ext_obj_name}.{prim_atr}"
                upd_inp_hk_plg_ls.append(scnd_plg)

            # if scnd_atr == 'None' -> don't add. 
            if not scnd_atr == None:
                # add this to the list. 
                scnd_plg = f"{ext_obj_name}.{scnd_atr}"
                upd_inp_hk_plg_ls.append(scnd_plg)

            print(f" -- Update component_name: {component_name}, ext_obj_name: {ext_obj_name}, prim: {upd_inp_hk_plg_ls}")

            # update the database!
            if not prim_atr == None:
                database_schema_002.UpdateMtxModuleData(
                    directory=rig_db_directory,
                    module_name=module,
                    unique_id=unique_id,
                    side=side,
                    inp_hk_mtx_ls=upd_inp_hk_plg_ls,
                    out_hk_mtx_ls=[],
                    prim=True,
                    scnd=False)


    # ---- Delete database functions ----
    def delete_database_module(self, module_name, val_availableRigComboBox, mdl_tree_model):
        '''
        # Description:
            Delete the .db file of the given module. 
        # Arguments:
            db_folder_path (string): Path of the folder the .db modules are in
            module_name (string): Name of the module to delete.
            val_availableRigComboBox (string): Name of the db rig grp. 
            mdl_tree_model (QTreeModel): model of the tree view.
        # Returns: N/A 
        '''
        # cr .db name
        db_folder_path = utils_os.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", 
            self.db_rig_location, val_availableRigComboBox
            )
        db_name = f"DB_{module_name}.db"
        db_path = f"{db_folder_path}/{db_name}"

        # Force all connections closed first
        db_connection_tracker.DBConnectionTracker.force_close_all()

        # Now safely delete the file
        try:
            os.unlink(db_path)
            print(f"{db_name} successfully deleted from {db_folder_path}")
        except Exception as e:
            print(f"{db_name} delete failed: {e}")


    def delete_database_component(self, component_selection, val_availableRigComboBox, mdl_tree_model):
        '''
        # Description:
            Delete the specific component from the .db file of the given module. 
        # Arguments:
            component_selection (string): Name of the selected component (1 only, not multiple). 
            val_availableRigComboBox (string): Name of the db rig grp. 
            mdl_tree_model (QTreeModel): model of the tree view.
        # Returns: N/A 
        '''
        module, unique_id, side = utils.get_name_id_data_from_component(component_selection)
        rig_db_directory = utils_os.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", 
            self.db_rig_location, val_availableRigComboBox
            )
        
        database_schema_002.DeleteComponentRows(rig_db_directory, module, unique_id, side)


    def delete_scene_component(self, component_selection):
        '''
        # Description:
            Delete all traces of the given component in the module from the 
            current maya scene if they exist. 
        # Arguments:
            module_name (string): Name of the module to delete.
        # Returns: N/A 
        '''
        module, unique_id, side = utils.get_name_id_data_from_component(component_selection)

        # check if the module has been added to the scene by checking for grp:
        # grp_ctrl_*module_component_*uniqueID_*side
        # grp_misc_*module_component_*uniqueID_*side
        # xfm_grp_*module_component_*uniqueID_*side
        # grp_ori_*module_component_*uniqueID_*side
            # then delete them
        
        for name in ["ctrl", "misc", "xfm", "ori"]:
            grp_name = f"grp_{name}_{module}_component_{unique_id}_{side}"
            if cmds.objExists(grp_name):
                cmds.delete(grp_name)
                print(f"Deleted grp_name from component `{component_selection}`")
            else:
                print(f"del_comp Not exist: {grp_name}")


    def delete_scene_module(self, module_name, tree_model):
        '''
        # Description:
            Delete all traces of the given module from the current maya scene if they exist. 
        # Arguments:
            component_list (list): Name components in the module.
        # Returns: N/A 
        '''
        # check if the module has been added to the scene by checking for grp:
        component_list = utils_QTree.get_components_of_selected_module(tree_model, module_name)

        for component in component_list:
            print(f"del module, component = {component}")
            self.delete_scene_component(component)
