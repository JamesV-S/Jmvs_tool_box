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

from databases.char_databases import database_schema_002

importlib.reload(database_schema_002)
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
    def record_component_change(self, component_selection, val_availableRigComboBox):
        split_names = component_selection.split('_')[1:] #ignore 'mdl' prefix
        module = split_names[0]
        unique_id = split_names[1]
        side = split_names[2]
        if "root" in module:
            find_guide = f"xfm_guide_{module}_*"
        else:
            find_guide = f"xfm_guide_{module}_*_{unique_id}_{side}"

        try:
            cmds.select(find_guide)
            guides = cmds.ls(sl=1, type="transform")
            # gather the positions of the selected
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
            retrieved_exisiting_dict = database_schema_002.retrieveSpecificPlacementPOSData(
                rig_db_directory, module, unique_id, side
                )
            existing_pos_dict = retrieved_exisiting_dict.return_existing_pos_dict()
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
        if os.path.exists(rig_db_directory):
            for db in os.listdir(rig_db_directory):
                if db.startswith("DB_") and db.endswith(".db"):
                    db_names.append(db)
                    
                    # get the table data `modules` from each database
                    # query the unique_id & side from each row
                    # store into a dictionary to pass to pop `populate_tree_views()`
                    data_retriever = database_schema_002.retrieveModulesData(
                        rig_db_directory, db)
                    db_data[db] = data_retriever.mdl_populate_tree_dict.get(db, [])
                else:
                    print(f"NO database file found in:{rig_db_directory}")
        else:
            print(f"directory does NOT exist: {rig_db_directory}")
        print(f"rig_folder_name: {rig_folder_name} & in that, {db_names}")
        
        # clear the modules everytime the active db is switched
        mdl_tree_model.clear()
        
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
                    placement_dict =  values['placement']
                    user_settings_dict =  values['user_settings']
                    controls_dict =  values['controls']
                  
            print(f"placement_dict >> {placement_dict}")
            print(f"user_settings_dict >> {user_settings_dict}")
            print(f"controls_dict >> {controls_dict}")
            mdl_directory = os.path.join(self.rig_db_storage_dir, val_availableRigComboBox)
            # update to need a directory!
            if checkBox:
                for db in range(iterations):
                    database_schema = database_schema_002.CreateDatabase(
                        mdl_directory, mdl_name, side, 
                        placement_dict, user_settings_dict, controls_dict)
                
                # unique_id = database_schema.get_unique_id()
                # print(f"unique_id == {unique_id} for {mdl_name}_{side}")
                # import and call the database maker 'database_schema'
            else:
                print(f"Not required module database creation for {mdl_name}")

    
    def func_unlocked_all(self):
        # establish components present in the scene!
        possible_comp_groups = "xfm_grp_*_component_*"
        cmds.select(possible_comp_groups)
        xfm_ancestorGrp = cmds.ls(sl=1, type="transform")
        # xfm_ancestorGrp = ['xfm_grp_bipedArm_component_0_L', 'xfm_grp_bipedLeg_component_0_L', 'xfm_grp_root_component_0_M', 'xfm_grp_spine_component_0_M'] 
        print(f"xfm_ancestorGrp = {xfm_ancestorGrp}")
        for component in xfm_ancestorGrp:
            self.constrain_guides_from_comp(component)
        cmds.select(cl=1)
    
    # ---- Component constraints ----
    def constrain_guides_from_comp(self, component):
        # guide > parentOperation > guideGROUP(constrained)
        print(f"NNNNNNNNNORMAL UNLOCK component = {component}")
        spine_output_mdl = "spine"
        parts = component.split('_')[2:]
        print(f"PARTS == {parts}")
        working_comp_unique_id = parts[2]
        working_comp_side =  parts[3]
        grpXfm = "offset_xfm_guide"
        xfm = "xfm_guide"

        xfm_root = f"{xfm}_root_ROOT_{working_comp_unique_id}_M"
        xfm_cog = f"{xfm}_root_COG_{working_comp_unique_id}_M"

        if "bipedLeg" in component:
            print("bipedLeg unlocked configuration")
            if cmds.objExists("xfm_grp_spine_component_*_M"):
                cmds.select("xfm_grp_spine_component_*_M")
                leg_output_comp = cmds.ls(sl=1, type="transform")[0] # handles only 1 spine for time being
                print(f"output_comp = {leg_output_comp}") # xfm_grp_spine_component_0_M
                leg_spine_input_name = f"offset_xfm_guide_bipedLeg_hip_{working_comp_unique_id}_{working_comp_side}"
                leg_output_mdl = "spine"
                leg_output_uID = leg_output_comp.split('_')[4:][0]
                leg_output_side = leg_output_comp.split('_')[4:][-1]
                leg_spine_output_name =f"xfm_guide_{spine_output_mdl}_{spine_output_mdl}0_{leg_output_uID}_{leg_output_side}"
                # spine1 >PointConAll> hip 
                utils.constrain_2_items(leg_spine_output_name, leg_spine_input_name, "point", "all")
            else: print("spine component not in scene")
            # Hip >PointConAll> knee
            utils.constrain_2_items(
                f"{xfm}_bipedLeg_hip_{working_comp_unique_id}_{working_comp_side}", 
                f"{grpXfm}_bipedLeg_knee_{working_comp_unique_id}_{working_comp_side}", 
                "point", "all")
            # knee > Nothing
            # foot >PointConX_Z> ankle
            utils.constrain_2_items(
                f"{xfm}_bipedLeg_foot_{working_comp_unique_id}_{working_comp_side}", 
                f"{grpXfm}_bipedLeg_ankle_{working_comp_unique_id}_{working_comp_side}", 
                "point", ["X", "Z"])
            # foot >ParentConAll> ball
            utils.constrain_2_items(
                f"{xfm}_bipedLeg_foot_{working_comp_unique_id}_{working_comp_side}", 
                f"{grpXfm}_bipedLeg_ball_{working_comp_unique_id}_{working_comp_side}", 
                "parent", "all")
            # foot >ParentConAll> toe
            utils.constrain_2_items(
                f"{xfm}_bipedLeg_foot_{working_comp_unique_id}_{working_comp_side}", 
                f"{grpXfm}_bipedLeg_toe_{working_comp_unique_id}_{working_comp_side}", 
                "parent", "all")
            if cmds.objExists("xfm_grp_root_component_*_M"):
                # root >ParentCon_Y_> ankle
                # offset_xfm_guide_root
                utils.constrain_2_items(
                xfm_root,
                f"{grpXfm}_bipedLeg_ankle_{working_comp_unique_id}_{working_comp_side}", 
                "parent", ["Y"])
                # root >PointtConAll> foot
                utils.constrain_2_items(
                xfm_root,
                f"{grpXfm}_bipedLeg_foot_{working_comp_unique_id}_{working_comp_side}", 
                "point", "all")
        elif "bipedArm" in component:
            print("bipedArm unlocked configuration")
            if cmds.objExists("xfm_grp_spine_component_*_M"):
                print("Arm, spine IS component in scene")
                cmds.select("xfm_grp_spine_component_*_M")
                arm_output_comp = cmds.ls(sl=1, type="transform")[0] # handles only 1 spine for time being
                print(f"output_comp = {arm_output_comp}") # xfm_grp_spine_component_0_M
                arm_output_uID = arm_output_comp.split('_')[4:][0]
                arm_output_side = arm_output_comp.split('_')[4:][-1]
                arm_spine_output_name =f"xfm_guide_{spine_output_mdl}_{spine_output_mdl}3_{arm_output_uID}_{arm_output_side}"
                # spine4 >ParentConAll> clavicle
                clavicle_input_name = f"offset_xfm_guide_bipedArm_clavicle_{working_comp_unique_id}_{working_comp_side}"
                utils.constrain_2_items(arm_spine_output_name, clavicle_input_name, 
                                        "parent", "all")
                # spine4 >ParentConAll> shoulder
                shoulder_input_name = f"offset_xfm_guide_bipedArm_shoulder_{working_comp_unique_id}_{working_comp_side}"
                utils.constrain_2_items(arm_spine_output_name, shoulder_input_name, 
                                        "parent", "all")
                if cmds.objExists("xfm_grp_root_component_*_M"):
                    # root >ParentCon_Y_> ankle
                    utils.constrain_2_items(
                    xfm_root,
                    f"{grpXfm}_bipedArm_elbow_{working_comp_unique_id}_{working_comp_side}", 
                    "point", "all")
                    # root >PointtConAll> foot
                    utils.constrain_2_items(
                    xfm_root,
                    f"{grpXfm}_bipedArm_wrist_{working_comp_unique_id}_{working_comp_side}", 
                    "point", "all")
        elif "root" in component:
            print("root unlocked configuration")
            # root >PointtConAll> COG
            utils.constrain_2_items(
                f"{xfm}_root_ROOT_{working_comp_unique_id}_{working_comp_side}",
                f"{grpXfm}_root_COG_{working_comp_unique_id}_{working_comp_side}", 
                "parent", "all")
        elif "spine" in component:
            print("spine unlocked configuration")
            if cmds.objExists("xfm_grp_root_component_*_M"):
                # cog >ParentConAll> spine1
                utils.constrain_2_items(
                xfm_cog,
                f"{grpXfm}_{spine_output_mdl}_{spine_output_mdl}0_{working_comp_unique_id}_{working_comp_side}", 
                "parent", "all")
            # spine0 > ParentConAll> spine1/2/3/4
            utils.constrain_2_items(
                f"{xfm}_{spine_output_mdl}_{spine_output_mdl}0_{working_comp_unique_id}_{working_comp_side}",
                f"{grpXfm}_{spine_output_mdl}_{spine_output_mdl}1_{working_comp_unique_id}_{working_comp_side}", 
                "parent", "all")
            utils.constrain_2_items(
                f"{xfm}_{spine_output_mdl}_{spine_output_mdl}0_{working_comp_unique_id}_{working_comp_side}",
                f"{grpXfm}_{spine_output_mdl}_{spine_output_mdl}2_{working_comp_unique_id}_{working_comp_side}", 
                "parent", "all")
            utils.constrain_2_items(
                f"{xfm}_{spine_output_mdl}_{spine_output_mdl}0_{working_comp_unique_id}_{working_comp_side}",
                f"{grpXfm}_{spine_output_mdl}_{spine_output_mdl}3_{working_comp_unique_id}_{working_comp_side}", 
                "parent", "all")
            utils.constrain_2_items(
                f"{xfm}_{spine_output_mdl}_{spine_output_mdl}0_{working_comp_unique_id}_{working_comp_side}",
                f"{grpXfm}_{spine_output_mdl}_{spine_output_mdl}4_{working_comp_unique_id}_{working_comp_side}", 
                "parent", "all")

    
    # ---- Control data recording ----
    def store_component_control_data(self, component_selection, val_availableRigComboBox):
        split_names = component_selection.split('_')[1:]
        module = split_names[0]
        unique_id = split_names[1]
        side = split_names[2]

        ''' Might not need to do this here!
        # need the controls linked to the component selection
            #  func to return list of controls. Arg = component_selection
                # Method: get dict from the database from 'curve_info' column (check if its empty or nah)
                # focus on the keys only, and create the ctrl names and return a list '''
        
        # need to store the data of the correct controls (selct them from the keys in the curv_info dict gotten from db column)
        # SO get curve data for each control
        # then put this data that's returned back into the curve_info culimn, looking like this: 
            # { }"fk_clavicle": {"degree": #, "Periodic": #, "cvs": #, "knot_vector": #, "int_B": #},
            # "fk_shoulder": {"degree": #, "Periodic": #, "cvs": #, "knot_vector": #, "int_B": #},
            # ... }
        # Curve_info is checked on control creation!
        # "cr_guides.py" needs to read curve_info column from database, and apply the data if there are values in the keys to each control!


    def record_ctrl_data(self, control):
        degree = cmds.getAttr(f"{control}.degree")# control.degree()
        if isinstance(degree, list):
            degree = degree[0]
        form = cmds.getAttr(f"{control}.form")
        if isinstance(form, list):
            form = form[0]
        periodic = True if form == 3 else False
        cvs = cmds.getAttr(f"{control}.controlPoints[*]")
        cvs = [(cv[0], cv[1], cv[2]) for cv in cvs]
        print(f"degree: {degree}, form:{form}, periodic:{periodic}, cvs:{cvs}")
        knot_vector = utils.knot_vector(periodic, cvs, degree)
        scale = cmds.xform(control, q=1, s=1, worldSpace=1) 
        
        data = {"crv_name":control, "degree": degree, "periodic": periodic, 
            "points": cvs, "knot": knot_vector, "scale": scale
            }
        
        print(f"data = {data}")

        return data


    def rebuild_ctrl(self, control, data):
        print(f"Name = {control}, data = {data}")
        if data["crv_name"] == control:
            cmds.setAttr(f"{control}.degree", data["degree"])
            if data["periodic"]:
                cmds.closeCurve(control, preserveShape=True)
            for i, cv in enumerate(data["points"]):
                cmds.setAttr(f"{control}.controlPoints[{i}]", cv[0], cv[1], cv[2])
            cmds.rebuildCurve(control, degree=data["degree"], keepRange=0, keepControlPoints=True)
            cmds.xform(control, s=data["scale"], worldSpace=1) 
        else:
            print("the provided curve doesn't match the crv_name in the given data")