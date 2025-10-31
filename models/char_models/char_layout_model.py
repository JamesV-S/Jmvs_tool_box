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
    utils_json
)

from databases.char_databases import (
    database_schema_002,
    database_schema_003
    )

importlib.reload(database_schema_002)
importlib.reload(database_schema_003)
importlib.reload(utils_os)
importlib.reload(utils_json)

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
        retrieve_mdl_component_dict = database_schema_002.retrieveSpecificComponentdata(rig_db_directory, module, unique_id, side)
        mdl_component_dict = retrieve_mdl_component_dict.return_mdl_component_dict()
        print(f"mdl_component_dict = {mdl_component_dict}")
        return mdl_component_dict


    # ---- TreeView functions ----
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
            retrieved_existing_dict = database_schema_002.retrieveSpecificPlacementPOSData(
                rig_db_directory, module, unique_id, side
                )
            existing_pos_dict = retrieved_existing_dict.return_existing_pos_dict()
            print(f"existing_pos_dict = {existing_pos_dict}")

            updated_existing_pos_dict = {}
            for key in existing_pos_dict.keys():
                for new_key, new_value in new_component_pos_dict.items():
                    print(f"if key:`{key}` in new_key:`{new_key}`")
                    if key in new_key:
                        updated_existing_pos_dict[key] = new_value
                        updated_dict = True
                        break
                    else:
                        updated_dict = False
            if updated_dict:
                print(f"Updated `existing_dict` : {updated_existing_pos_dict}")
                ''' with new dict, update the database! '''
                database_schema_002.updateSpecificPlacementPOSData(
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
            retrieve_rot_data = database_schema_002.retrieveSpecificComponentdata(
            rig_db_directory, module, unique_id, side)
            
            # Establish the ori guides for the component
            comp_rot_dict = retrieve_rot_data.return_rot_component_dict()
            ori_guides_keys = [key for key, rot in list(comp_rot_dict.items())]
            ori_guides = [f"ori_{module}_{ori_guides_keys[x]}_{unique_id}_{side}" for x in range(len(ori_guides_keys))]
            print(f"ORI record: ori_guides = `{ori_guides}`")
            
            # Get rot  
            new_component_rot_dict = utils.get_selection_rot_dict(ori_guides[:-1])
            print(f"ORI recording: new_component_rot_dict = `{new_component_rot_dict}`")
            """
            new_component_rot_dict = {
            'ori_bipedArm_clavicle_0_L': [0.0, 0.0, -25.14671680808026], 
            'ori_bipedArm_shoulder_0_L': [-32.63938984529915, 34.55844334711877, -48.47071953609031], 
            'ori_bipedArm_elbow_0_L': [121.21093795508934, -84.46437211672716, -121.09236735327723]
            }
            """
            # Copy the data of 'second to last' ori guide and paste it to the last ori guide in the stored dict!
            new_component_rot_dict[ori_guides[-1]] = new_component_rot_dict[ori_guides[-2]]
            print(f"NEW ORI recording: new_component_rot_dict = `{new_component_rot_dict}`")
            """
            {
            'ori_bipedArm_clavicle_0_L': [0.0, 0.0, -25.14671680808026], 
            'ori_bipedArm_shoulder_0_L': [-32.63938984529915, 34.55844334711877, -48.47071953609031], 
            'ori_bipedArm_elbow_0_L': [121.21093795508934, -84.46437211672716, -121.09236735327723], 
            'ori_bipedArm_wrist_0_L': [121.21093795508934, -84.46437211672716, -121.09236735327723]}
            """
            # -- Orientation data --
            # Update the database with just the keys as the keys and not the name of ori!
            updated_rot_dict = {}
            for key in comp_rot_dict.keys():
                for new_key, new_value in new_component_rot_dict.items():
                    print(f"if key:`{key}` in new_key:`{new_key}`")
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


    def visualise_active_db(self, val_availableRigComboBox, mdl_tree_model):
        # get directory of current chosen rig folder!
        rig_folder_name = val_availableRigComboBox
        rig_db_directory = utils_os.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", 
            self.db_rig_location, rig_folder_name
            )
        # gather a list of database found in the folder: 
        db_names = []
        db_data = {}
        db_test = {}
        if os.path.exists(rig_db_directory):
            for db_name in os.listdir(rig_db_directory):
                if db_name.startswith("DB_") and db_name.endswith(".db"):
                    db_names.append(db_name)
                    
                    # get the table data `modules` from each database
                    # query the unique_id & side from each row
                    # store into a dictionary to pass to pop `populate_tree_views()`
                    
                    data_retriever = database_schema_002.retrieveModulesData(rig_db_directory, db_name)
                    db_test[db_name] = data_retriever.mdl_populate_tree_dict.get(db_name, [])
                    
                    data_retriever = database_schema_003.RetrieveModuleTable(
                        rig_db_directory, db_name
                    )
                    db_data[db_name] = data_retriever.retrieve_data().get(db_name, [])
                
                else:
                    print(f"NO database file found in: {rig_db_directory}")
        else:
            print(f"directory does NOT exist: {rig_db_directory}")
        print(f"rig_folder_name: {rig_folder_name} & in that, {db_names}")
        
        # clear the modules everytime the active db is switched
        mdl_tree_model.clear()
            
        print(f"db_test = {db_test}")
        print(f"db_data = {db_data}")

        # add all databases to the treeView
        self.populate_tree_views(mdl_tree_model, rig_folder_name, db_data)
        

    def populate_tree_views(self, mdl_tree_model, rig_folder_name, db_data_dict):
        print(f"Populating Tree with `{rig_folder_name}'s` databases: {list(db_data_dict.keys())}")
        tree_parent_item = mdl_tree_model.invisibleRootItem()

        if not db_data_dict:
            print(f"NO databases in the folder `{rig_folder_name}`")
        else:
            print(f"found databases '{list(db_data_dict.keys())}' in the folder `{rig_folder_name}`")
            try:
                for db_name, rows in db_data_dict.items():
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
            'component_rot_xyz': {'clavicle': [0.0, 0.0, 0.0], 'shoulder': [0.0, 0.0, 0.0], 'elbow': [0.0, 0.0, 0.0], 'wrist': [0.0, 0.0, 0.0]}, 'component_rot_yzx': {'clavicle': [0.0, 0.0, 0.0], 'shoulder': [0.0, 0.0, 0.0], 'elbow': [0.0, 0.0, 0.0], 'wrist': [0.0, 0.0, 0.0]}}

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
        access_data = database_schema_002.retrieveSpecificComponentdata(
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
                        self.visualise_active_db(val_availableRigComboBox, mdl_tree_model)
                    
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
                retrieved_existing_dict = database_schema_002.retrieveSpecificPlacementPOSData(
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
                database_schema_002.updateSpecificPlacementPOSData(
                    rig_db_directory, module, unique_id, mirror_side, existing_pos_dict
                    )
                database_schema_002.UpdatePlacementROTData(
                    rig_db_directory, module, unique_id, mirror_side, existing_rot_dict, existing_plane_dict)


    def commit_module_edit_changes(self, component, val_availableRigComboBox, val_update_comp_data_checkBox, val_joint_editing_checkBox, val_ctrl_editing_checkBox, umo_dict, jnt_num):
        module, unique_id, side = utils.get_name_id_data_from_component(component)
        rig_db_directory = utils_os.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", 
            self.db_rig_location, val_availableRigComboBox
            )
        
        print(f"Module = `{module}`, unique_id = `{unique_id}`, side = `{side}`")
        print(f"model | umo_dict = {umo_dict}")
 
        # update the user_settings DB
        if val_update_comp_data_checkBox:
            print(f"update modu;e l editing model functions running")
            database_schema_002.UpdateUserSettings(rig_db_directory, module, unique_id, side, umo_dict)
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
        