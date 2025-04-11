# ------------------------------ MODEL ----------------------------------------
import importlib
import os.path
import maya.cmds as cmds
import json

try:
    from PySide6 import QtCore, QtWidgets, QtGui
except ModuleNotFoundError:
    from PySide2 import QtCore, QtWidgets, QtGui

from systems import (
    os_custom_directory_utils,
    utils
)

from databases.char_databases import database_schema_002

importlib.reload(database_schema_002)

class CharLayoutModel:
    def __init__(self):
        self.db_rig_location = "db_rig_storage"
        self.rig_db_storage_dir = os_custom_directory_utils.create_directory(
            "Jmvs_tool_box", "databases", "char_databases", "db_rig_storage"
            )
        self.json_dict = self.get_modules_json_dict()

    # ---- TreeView functions ----
    def load_rig_group(self, val_availableRigComboBox):
        # rig_syntax "jmvs_char*_rig" - DB_jmvs_cyborg_rig
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
            self.rig_db_storage_dir = os_custom_directory_utils.create_directory("Jmvs_tool_box", "databases", "char_databases", location)
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
        rig_folder_name = val_availableRigComboBox
        print(f"rig_folder_name = {rig_folder_name}")
        rig_db_directory = os_custom_directory_utils.create_directory(
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
        try: # handle if it has no side
            side = split_names[2]
        except Exception:
            side = "" #use M to represent middle (but doesn't show up in scene)
            # Or whatever it needs to be in the database! 
        print(f"split_names: module = {module}, unique_id = {unique_id}, side = {side}")

        print(f"xfm_guide_{module}_*_{unique_id}_{side}")
        #xfm_guide_bipedArm_*       _0_L
        #xfm_guide_bipedArm_clavicle_0_L
        try:
            cmds.select(f"xfm_guide_{module}_*_{unique_id}_{side}")
            guides = cmds.ls(sl=1, type="transform")
            # gather the positions of the selected
            new_component_pos_dict = utils.get_selection_trans_dict(guides, side)
            print("new_component_pos: ", new_component_pos_dict)
            ''' got this dict `B` from selection in treeView '''
            ''' if ^ = {} cancel the operation below. '''
            ''' get this dict `A` from the correct row in the right db '''
            ''' compare `B` to `A`, find the same name 'clavicle', ect, and put the new values in it.'''
            rig_folder_name = val_availableRigComboBox
            print(f"rig_folder_name = {rig_folder_name}")
            rig_db_directory = os_custom_directory_utils.create_directory(
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
                    if key in new_key:
                        updated_existing_pos_dict[key] = new_value
                        break
            print(f"Updated `existing_dict` : {updated_existing_pos_dict}")
            ''' with new dict, update the database! '''
            database_schema_002.updateSpecificPlacementPOSData(
                rig_db_directory, module, unique_id, side, updated_existing_pos_dict
                )

        except Exception as e:
            print(f"No component exists in the scene of '{component_selection}'")
            print(f"error: {e}")


    def visualise_active_db(self, val_availableRigComboBox, mdl_tree_model):
        # get directory of current chosen rig folder!
        rig_folder_name = val_availableRigComboBox
        rig_db_directory = os_custom_directory_utils.create_directory(
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
                    db_item = QtGui.QStandardItem(f"{db_base_name}") # Orange
                    db_item.setData(True, QtCore.Qt.UserRole)

                    for unique_id, side in rows:
                        if "root" in db_base_name:
                            item_name = f"mdl_{db_base_name}_{unique_id}"
                        else:
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
            '''
            {'bipedArm.json': 
                {
                'mdl_name': 'bipedArm', 
                'names': ['clavicle', 'shoulder', 'elbow', 'wrist'], 
                'placement': {
                            'component_pos': {'clavicle': [3.9705319404602006, 230.650634765625, 2.762230157852166], 
                                            'shoulder': [25.234529495239258, 225.57975769042972, -12.279715538024915], 
                                            'elbow': [49.96195602416994, 192.91743469238278, -8.43144416809082], 
                                            'wrist': [72.36534118652347, 164.23757934570304, 15.064828872680739]}, 
                            'system_rot_xyz': {'clavicle': [-7.698626118758961, 34.531672095102785, -13.412947865931349], 
                                            'shoulder': [7.042431639335459, -5.366417614476926, -52.87199475566795], 
                                            'elbow': [3.4123575630188263, -32.847391136978814, -52.004681579832734], 
                                            'wrist': [3.4123575630188263, -32.847391136978814, -52.004681579832734]}, 
                            'system_rot_yzx': {'clavicle': [-101.01687892466634, -54.72478122395497, 0.0], 
                                            'shoulder': [38.44191942754821, -81.34821938773749, 179.00497225409262], 
                                            'elbow': [84.72265733457102, -56.99499092973047, 134.2807120402011], 
                                            'wrist': [84.72265733457102, -56.99499092973047, 134.2807120402011]}
                            }, 
                'constant': {
                            'space_swap': 
                                        [['world', 'COG', 'shoulder', 'custom'], ['world', 'wrist'], ['world', 'clavicle'], ['world', 'spine']], 
                            'ik_settings': 
                                        {'start_joint': 'shoulder', 'end_joint': 'wrist', 'pv_joint': 'elbow', 'top_joint': 'clavicle'}
                            }, 
                'user_settings': {
                                'mirror_rig': False, 'stretch': False, 
                                'rig_type': {'options': ['FK', 'IK', 'IKFK'], 'default': 'FK'}, 
                                'size': 1, 'side': ['L', 'R']
                                }, 
                'controls': {
                            'FK_ctrls': 
                                    {'fk_clavicle': 'circle', 'fk_shoulder': 'circle', 'fk_elbow': 'circle', 'fk_wrist': 'circle'}, 
                            'IK_ctrls': 
                                    {'ik_clavicle': 'cube', 'ik_shoulder': 'cube', 'ik_elbow': 'pv', 'ik_wrist': 'cube'}
                            }
                },
            'bipedLeg.json': {'mdl_name': 'bipedLeg', 'names': ['hip', 'knee', 'ankle', 'ball', 'toe'], 'placement': {'component_pos': {'hip': [16.036325454711914, 147.7965545654297, 0.051486290991306305], 'knee': [20.133201599121104, 82.05242919921866, -0.4505884051322898], 'ankle': [24.197132110595703, 12.625909805297809, -3.493209123611452], 'ball': [24.084232330322262, -1.2434497875801753e-14, 17.988098144531257], 'toe': [24.084232330322276, -1.1379786002407858e-14, 29.18881988525391]}, 'system_rot_xyz': {'hip': [-0.206856730062026, 0.4367008200374581, -86.43419733389054], 'knee': [-0.20685673006202596, 0.43670082003745814, -86.43419733389054], 'ankle': [0.5942622188475634, -59.55357811140123, -90.0], 'ball': [-89.85408725528224, -89.99999999999997, 0.0], 'toe': [-89.85408725528225, -89.99999999999997, 0.0]}, 'system_rot_yzx': {'hip': [-0.43670082003745525, 0.0, -176.43419733389047], 'knee': [-2.5051019515754724, 0.0035324430433216728, -176.434], 'ankle': [59.55357811140115, 0.0, 180.0], 'ball': [89.99999999999993, 1.8636062586700292e-16, -180.0], 'toe': [89.99999999999996, -1.2424041724466862e-17, -180.0]}}, 'constant': {'space_swap': [['world', 'COG', 'hip', 'custom'], ['world', 'ankle'], ['world', 'spine_0']], 'ik_settings': {'start_joint': 'hip', 'end_joint': 'ankle', 'pv_joint': 'knee'}}, 'user_settings': {'mirror_rig': False, 'stretch': False, 'rig_type': {'options': ['FK', 'IK', 'IKFK'], 'default': 'FK'}, 'size': 1, 'side': ['L', 'R']}, 'controls': {'FK_ctrls': {'fk_hip': 'circle', 'fk_knee': 'circle', 'fk_ankle': 'circle', 'fk_ball': 'circle', 'fk_toe': 'circle'}, 'IK_ctrls': {'ik_hip': 'cube', 'ik_knee': 'pv', 'ik_ankle': 'cube', 'ik_ball': 'None', 'ik_toe': 'None'}}}, 
            }
            'finger.json': {'mdl_name': 'Finger', 'names': ['bipedPhalProximal', 'bipedPhalMiddle', 'bipedPhalDistal', 'bipedPhalDEnd'], 'placement': {'component_pos': {'bipedPhalProximal': [80.61004637463462, 151.7215423583185, 24.099996037467385], 'bipedPhalMiddle': [84.45979996338392, 145.8773481500665, 28.318845156262494], 'bipedPhalDistal': [87.13240797932576, 141.82014294780598, 31.24768974670393], 'bipedPhalDEnd': [89.18559525612636, 138.70326159035977, 33.49772656951928]}, 'system_rot_xyz': {'bipedPhalProximal': [5.910977623767589, -31.083474503917564, -56.62585344811804], 'bipedPhalMiddle': [5.910977623767589, -31.083474503917564, -56.62585344811804], 'bipedPhalDistal': [5.910977623767589, -31.08347450391755, -56.62585344811804], 'bipedPhalDEnd': [5.910977623767589, -31.08347450391755, -56.62585344811804]}, 'system_rot_yzx': {'bipedPhalProximal': [50.95891725101831, -56.98582204849474, 153.9365525662274], 'bipedPhalMiddle': [50.95891725101831, -56.98582204849474, 153.9365525662274], 'bipedPhalDistal': [50.95891725101831, -56.98582204849474, 153.9365525662274], 'bipedPhalDEnd': [50.95891725101831, -56.98582204849474, 153.9365525662274]}}, 'constant': {'space_swap': [['world', 'COG', 'wrist', 'custom'], ['world', 'bipedPhalDEnd'], ['world', 'bipedPhalProximal'], ['world', 'wirst']], 'ik_settings': {'start_joint': 'bipedPhalProximal', 'end_joint': 'bipedPhalDistal', 'pv_joint': 'bipedPhalMiddle', 'world_orientation': False, 'last_joint': 'bipedPhalDEnd'}}, 'user_settings': {'mirror_rig': False, 'stretch': True, 'rig_type': {'options': ['FK', 'IK', 'IKFK'], 'default': 'FK'}, 'size': 0.15, 'side': ['L', 'R']}, 'controls': {'FK_ctrls': {'fk_bipedPhalProximal': 'circle', 'fk_bipedPhalMiddle': 'circle', 'fk_bipedPhalDistal': 'circle', 'fk_bipedPhalDEnd': 'circle'}, 'IK_ctrls': {'ik_bipedPhalProximal': 'cube', 'ik_bipedPhalMiddle': 'pv', 'ik_bipedPhalDistal': 'cube', 'ik_bipedPhalDEnd': 'cube'}}}, 
            
            'root.json': {'mdl_name': 'root', 'names': ['root', 'COG'], 'placement': {'component_pos': {'root': [0, 0, 0], 'COG': [0, 150, 0]}, 'system_rot_xyz': {'root': [0, 0, 0], 'COG': [0, 0, 0]}, 'system_rot_yzx': {'root': [0, 0, 0], 'COG': [0, 0, 0]}}, 'constant': {'space_swap': [], 'ik_settings': {}}, 'user_settings': {'mirror_rig': False, 'stretch': False, 'rig_type': {'options': ['FK'], 'default': 'FK'}, 'size': 1, 'side': ['None']}, 'controls': {'FK_ctrls': {'fk_root': 'circle', 'fk_COG': 'circle'}, 'IK_ctrls': {}}}, 
            
            'spine.json': {'mdl_name': 'spine', 'names': ['spine_1', 'spine_2', 'spine_3', 'spine_4', 'spine_5'], 'placement': {'component_pos': {'spine_1': [0.0, 150.0, 0.0], 'spine_2': [-1.0302985026792348e-14, 165.3182830810547, 2.138536453247061], 'spine_3': [-2.3043808310802754e-14, 185.50926208496094, 2.8292100429534632], 'spine_4': [-3.3364796818449844e-14, 204.27308654785156, -0.3802546262741595], 'spine_5': [-5.1020985278054485e-14, 237.46397399902344, -8.25034904479989]}, 'system_rot_xyz': {'spine_1': [0.0, -7.947513469078512, 90.00000000000001], 'spine_2': [-1.9890093469260345e-16, -1.959155005957633, 90.00000000000001], 'spine_3': [0.0, 9.706246313394262, 90.00000000000001], 'spine_4': [-8.171859705486283e-16, 13.339396285991443, 90.0], 'spine_5': [-7.814945266275812e-14, -9.271752801444176, 89.99999999999991]}, 'system_rot_yzx': {'spine_1': [7.667038985618099, 0.0, 0.0], 'spine_2': [1.880673240761548, 0.0, 0.0], 'spine_3': [-9.496334372767544, 0.0, 0.0], 'spine_4': [-13.212290179161894, 0.0, 0.0], 'spine_5': [9.331941466846782, 0.0, 0.0]}}, 'constant': {'space_swap': [], 'ik_settings': {'start_joint': 'spine_1', 'end_joint': 'spine_5', 'pv_joint': None, 'world_orientation': True}}, 'user_settings': {'mirror_rig': False, 'stretch': False, 'rig_type': {'options': ['FK', 'IK', 'IKFK'], 'default': 'FK'}, 'size': 1, 'side': ['None']}, 'controls': {'FK_ctrls': {'fk_spine_1': 'circle', 'fk_spine_2': 'circle', 'fk_spine_3': 'circle', 'fk_spine_4': 'circle', 'fk_spine_5': 'circle'}, 'IK_ctrls': {'ik_spine_1': 'cube', 'ik_spine_2': None, 'ik_spine_3': 'cube', 'ik_spine_4': None, 'ik_spine_5': 'cube'}}}}
            '''
            
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


    def get_modules_json_dict(self):
        # derive the `self.json_all_mdl_list` from the config folder!
        # self.json_all_mdl_list = ['biped_arm.json', 'biped_leg.json']
        json_mdl_list = []
        json_config_dir = os_custom_directory_utils.create_directory("Jmvs_tool_box", "config", "char_config")
        if os.path.exists(json_config_dir):
            for mdl_config_file in os.listdir(json_config_dir):
                if mdl_config_file.endswith('.json'):
                    json_mdl_list.append(mdl_config_file)
        
        # This dictionary contains nested dict of all possible json modules in `char_config` folder
        json_dict = {}
        for json_file in json_mdl_list:
            # configer the json file
            json_path = os.path.join(json_config_dir, json_file)
            with open(json_path, 'r') as file:
                # load the json data
                json_data = json.load(file)
                json_dict[json_file] = json_data
        return json_dict 
    

    # ---- Component constraints ----
    def func_unlocked_all(self):
        # establish components present in the scene!
        possible_comp_groups = "xfm_grp_*_component_*"
        cmds.select(possible_comp_groups)
        xfm_ancestorGrp = cmds.ls(sl=1, type="transform")
        # xfm_ancestorGrp = ['xfm_grp_bipedArm_component_0_L', 'xfm_grp_bipedLeg_component_0_L', 'xfm_grp_root_component_0_M', 'xfm_grp_spine_component_0_M'] 
        print(f"xfm_ancestorGrp = {xfm_ancestorGrp}")
        for component in xfm_ancestorGrp:
            self.constrain_guides_from_comp(component)
    
    
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
                leg_spine_output_name =f"xfm_guide_{spine_output_mdl}_0_{leg_output_uID}_{leg_output_side}"
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
                f"{xfm}_root",
                f"{grpXfm}_bipedLeg_ankle_{working_comp_unique_id}_{working_comp_side}", 
                "parent", ["Y"])
                # root >PointtConAll> foot
                utils.constrain_2_items(
                f"{xfm}_root",
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
                arm_spine_output_name =f"xfm_guide_{spine_output_mdl}_3_{arm_output_uID}_{arm_output_side}"
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
                    f"{xfm}_root",
                    f"{grpXfm}_bipedArm_elbow_{working_comp_unique_id}_{working_comp_side}", 
                    "point", "all")
                    # root >PointtConAll> foot
                    utils.constrain_2_items(
                    f"{xfm}_root",
                    f"{grpXfm}_bipedArm_wrist_{working_comp_unique_id}_{working_comp_side}", 
                    "point", "all")
        elif "root" in component:
            print("root unlocked configuration")
            # root >PointtConAll> COG
            utils.constrain_2_items(
                f"{xfm}_root",
                f"{grpXfm}_COG", 
                "parent", "all")
        elif "spine" in component:
            print("spine unlocked configuration")
            if cmds.objExists("xfm_grp_root_component_*_M"):
                # cog >ParentConAll> spine1
                utils.constrain_2_items(
                f"{xfm}_COG",
                f"{grpXfm}_{spine_output_mdl}_0_{working_comp_unique_id}_{working_comp_side}", 
                "parent", "all")
            # spine0 > ParentConAll> spine1/2/3/4
            utils.constrain_2_items(
                f"{xfm}_{spine_output_mdl}_0_{working_comp_unique_id}_{working_comp_side}",
                f"{grpXfm}_{spine_output_mdl}_1_{working_comp_unique_id}_{working_comp_side}", 
                "parent", "all")
            utils.constrain_2_items(
                f"{xfm}_{spine_output_mdl}_0_{working_comp_unique_id}_{working_comp_side}",
                f"{grpXfm}_{spine_output_mdl}_2_{working_comp_unique_id}_{working_comp_side}", 
                "parent", "all")
            utils.constrain_2_items(
                f"{xfm}_{spine_output_mdl}_0_{working_comp_unique_id}_{working_comp_side}",
                f"{grpXfm}_{spine_output_mdl}_3_{working_comp_unique_id}_{working_comp_side}", 
                "parent", "all")
            utils.constrain_2_items(
                f"{xfm}_{spine_output_mdl}_0_{working_comp_unique_id}_{working_comp_side}",
                f"{grpXfm}_{spine_output_mdl}_4_{working_comp_unique_id}_{working_comp_side}", 
                "parent", "all")