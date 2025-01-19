
import sqlite3
import json
import importlib
import sys
import os

'''
# for running in VSCODE!
def determine_levels_to_target(current_dir, target_folder_name):
    #parts = current_dir.split(os.sep) 
    try:
        target_index = current_dir.split(os.sep).index(target_folder_name)
        levels = len(current_dir.split(os.sep) ) -target_index -1
        print(f"THE Number of levels to go up: {levels}")
    except ValueError:
        raise ValueError(f"Target folder '{target_folder_name}' not found in path.")
    return levels
def go_up_path_levels(path, levels):
    for _ in range(levels):
        path = os.path.dirname(path)
    return path

# Add the project root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
levels = determine_levels_to_target(current_dir, 'Jmvs_tool_box')
target_dir = go_up_path_levels(current_dir, levels)

project_root = os.path.join(current_dir, '..', '..')  # Adjust path as necessary
print(f"target_dir : {target_dir}, project_root: {project_root}")
sys.path.append(os.path.abspath(target_dir))
'''

from databases import database_manager
importlib.reload(database_manager)

# Temporary, this is already gathered automarically from the JSON
# u_s_dict = {'mirror_rig': False, 'stretch': False, 'rig_type': {'options': ['FK', 'IK', 'IKFK'], 'default': 'FK'}, 'size': 1} 


class CreateDatabase():
    def __init__(self, directory, mdl_name, side, placement_dict, user_settings_dict, controls_dict):
        db_directory = os.path.expanduser(directory)
        os.makedirs(db_directory, exist_ok=1)
        db_name = os.path.join(db_directory, f'DB_{mdl_name}.db')

        self.unique_id_tracker = {}
        try:
            with sqlite3.connect(db_name) as conn:
                # interasct with datsabase
                self.add_table(conn)
                print(f"module {mdl_name}_{side} has connected to database {db_name}")

                ''' query the database for the current max `unique_id` for each `mdl_name` & `side`'''
                self.query_uniqueID_tracker(conn) # BEFORE processing new data.
                self.unique_id = self.get_unique_id_sequence(mdl_name, side)
                
                # update the tables!
                # table modules
                self.update_db(conn, "modules", (self.unique_id, mdl_name, side))
                # table user_settings
                rig_options = ', '.join(user_settings_dict['rig_type']['options'])
                self.update_db(conn, "user_settings", (self.unique_id, user_settings_dict['mirror_rig'], user_settings_dict['stretch'], 
                                                    rig_options, user_settings_dict['rig_type']['default'], user_settings_dict['size']))
                # table placement
                self.update_db(conn, "placement", (self.unique_id, placement_dict['component_pos'], placement_dict['system_rot_xyz'], placement_dict['system_rot_yzx']))
                # module controls
                self.update_db(conn, "controls", (self.unique_id, controls_dict['FK_ctrls'], controls_dict['IK_ctrls']))
                    
        except sqlite3.Error as e:
            print(e)
    

    def add_table(self, conn): 
        sql_cr_table_state = [
        """CREATE TABLE IF NOT EXISTS modules (
            db_id INTEGER PRIMARY KEY,
            unique_id INT,
            module_name text NOT NULL,
            side text NOT NULL
        );""",
        """CREATE TABLE IF NOT EXISTS placement (
            db_id INTEGER PRIMARY KEY,
            unique_id INT,
            component_pos TEXT,
            system_rot_xyz TEXT,
            system_rot_yzx TEXT
        );""",
        """CREATE TABLE IF NOT EXISTS user_settings (
            db_id INTEGER PRIMARY KEY,
            unique_id INT,
            mirror_rig FLOAT,
            stretch FLOAT,
            rig_options TEXT,
            rig_default TEXT, 
            size INT
        );""",
        """CREATE TABLE IF NOT EXISTS controls (
            db_id INTEGER PRIMARY KEY,
            unique_id INT,
            FK_ctrls TEXT,
            IK_ctrls TEXT 
        );"""
        ]
        cursor = conn.cursor()
        for state in sql_cr_table_state:
            cursor.execute(state)
        conn.commit()


    def update_db(self, conn, table, values):
        cursor = conn.cursor()
        if table == 'modules':
            sql = f""" INSERT INTO {table} (unique_id, module_name, side) VALUES (?, ?, ?)"""
            cursor.execute(sql, values)
        elif table == 'placement':
            values = (values[0], json.dumps(values[1]), json.dumps(values[2]), json.dumps(values[3]))
            sql = f""" INSERT INTO {table} (unique_id, component_pos, system_rot_xyz, 
                system_rot_yzx) VALUES (?, ?, ?, ?)"""
            cursor.execute(sql, values)
        elif table == 'user_settings':
            sql = f""" INSERT INTO {table} (unique_id, mirror_rig, stretch, 
                rig_options, rig_default, size) VALUES (?, ?, ?, ?, ?, ?)"""
            cursor.execute(sql, values)
        elif table == 'controls':
            values = (values[0], json.dumps(values[1]), json.dumps(values[2]))
            sql = f""" INSERT INTO {table} (unique_id, FK_ctrls, IK_ctrls) 
                VALUES (?, ?, ?)"""
            cursor.execute(sql, values)
        conn.commit()

    
    def query_uniqueID_tracker(self, conn):
        cursor = conn.cursor()
        cursor.execute(f"SELECT module_name, side, MAX(unique_id) FROM modules GROUP BY module_name, side")
        rows = cursor.fetchall()
        for row in rows:
            mdl_name, side, max_id = row
            self.unique_id_tracker[(mdl_name, side)] = max_id


    '''function updates the next unique_id for a given combination. '''
    # global so the dict can keep track over multiple calls, to generate new unique_ids as expected
    def get_unique_id_sequence(self, mdl_name, side):
        key = (mdl_name, side)
        if key not in self.unique_id_tracker:
            print(f">> `unique_id` existing database is empty:{self.unique_id_tracker}, so set to 0")
            self.unique_id_tracker[key] = 0
        else:
            print(f">> `unique_id` dict from existing database = {self.unique_id_tracker}, adding +1")
            self.unique_id_tracker[key] += 1
        return self.unique_id_tracker[key]
    
'''
clavicle_Xyz TEXT,
shoulder_Xyz TEXT,
elbow_Xyz TEXT,
wrist_Xyz TEXT,
'''

class retrieveModulesData():
    def __init__(self, directory, database_name):
        self.mdl_populate_tree_dict = {}
        db_directory = os.path.expanduser(directory)
        os.makedirs(db_directory, exist_ok=1)
        # db_name must include the entire path too!
        db_name = os.path.join(db_directory, database_name)

        try:
            with sqlite3.connect(db_name) as conn:
                self.mdl_populate_tree_dict = self.dict_from_table(
                    conn, 'modules', database_name
                    )
                #return self.mdl_populate_tree_dict
        except sqlite3.Error as e:
            print(e)

    def dict_from_table(self, conn, table, database_name):
        # return a dict where each key is the database_name & each value is tuple of (unique_id & side)
        cursor = conn.cursor()
        query_param_state = f"SELECT unique_id, side FROM {table}"
        try:
            cursor.execute(query_param_state)
            rows = cursor.fetchall()
            print(f"rows = {rows}")
            mdl_populate_tree_dict = {database_name: []}
            if rows:
                for row in rows:
                    unique_id, side = row[0], row[1]
                    mdl_populate_tree_dict[database_name].append((unique_id, side))
            return mdl_populate_tree_dict

        except sqlite3.Error as e:
            print(f"sqlite3.Error: {e}")
            return {}