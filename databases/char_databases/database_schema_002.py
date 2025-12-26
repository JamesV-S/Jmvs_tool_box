
import sqlite3
import json
import importlib
import sys
import os
import gc

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

from utils import (
    utils,
    utils_db
)

from databases import (
    database_manager,
    db_connection_tracker
    )

from systems.sys_char_rig import (
    raw_data_fkik_dicts
)

importlib.reload(utils)
importlib.reload(utils_db)
importlib.reload(database_manager)
importlib.reload(db_connection_tracker)
importlib.reload(raw_data_fkik_dicts)

# Temporary, this is already gathered automarically from the JSON
# u_s_dict = {'mirror_rig': False, 'stretch': False, 'rig_sys': {'options': ['FK', 'IK', 'IKFK'], 'default': 'FK'}, 'size': 1} 

class CreateDatabase():
    def __init__(self, directory, mdl_name, side, item_name_list, placement_dict, constant_dict, user_settings_dict, controls_dict):
        db_directory = os.path.expanduser(directory)
        os.makedirs(db_directory, exist_ok=1)
        db_name = os.path.join(db_directory, f'DB_{mdl_name}.db')
        
        self.unique_id_tracker = {}
        try:
            with db_connection_tracker.DBConnectionTracker.get_connection(db_name) as conn:
                # interasct with datsabase
                self.add_table(conn)
                print(f"module {mdl_name}_{side} has connected to database {db_name}")

                ''' query the database for the current max `unique_id` for each `mdl_name` & `side`'''
                self.query_uniqueID_tracker(conn) # BEFORE processing new data.
                self.unique_id = self.get_unique_id_sequence(mdl_name, side)
                
                # tables modules ----------------------------------------------
                self.update_db(conn, "modules", (
                    self.unique_id, 
                    mdl_name, 
                    side
                    ))
                
                # table placement ---------------------------------------------
                self.update_db(conn, "placement", (
                    self.unique_id, 
                    placement_dict['component_pos'], 
                    placement_dict['component_rot'],
                    side
                    ))
                
                # constant data -----------------------------------------------
                self.update_db(conn, "constant", (
                    self.unique_id,
                    constant_dict['guides_connection'], 
                    constant_dict['guides_follow'],
                    item_name_list,
                    constant_dict['limbRoot_name'],
                    constant_dict['hock_name'],
                    constant_dict['ik_wld_name'],
                    side
                    ))
                
                # table user_settings -----------------------------------------
                '''rig_options = ', '.join(user_settings_dict['rig_sys']['options'])'''
                # print(f"DB* user_settings_dict['twist']= `{user_settings_dict['twist']}`" )
                
                print(f"DB Schema: user_settings = {user_settings_dict}")
                print(f"DB Schema: input_hook_mtx_plug = {user_settings_dict['input_hook_mtx_plug']}")
                print(f"DB Schema: output_hook_mtx_list = {user_settings_dict['output_hook_mtx_list']}")

                self.update_db(conn, "user_settings", (
                    self.unique_id,
                    user_settings_dict['input_hook_mtx_plug'],
                    user_settings_dict['output_hook_mtx_list'],
                    user_settings_dict['joint_num'],
                    user_settings_dict['size'],
                    side
                    ))
                
                # controls data -----------------------------------------------
                    # Get constant attr dict
                constant_attr_dict = utils.get_constant_attr_from_constant_dict(constant_dict)
                    # Get fkik contrrol raw dicts
                raw_fkik_data = raw_data_fkik_dicts.RawDataFkIKDicts(
                    controls_dict['FK_ctrls'], controls_dict['IK_ctrls'],
                    placement_dict['component_pos'], placement_dict['component_rot'],
                    constant_attr_dict, self.unique_id, side)
                fk_pos, fk_rot, ik_pos, ik_rot = raw_fkik_data.return_RawDataFkIKDicts()
                     # cr curve_info dictionary!
                curve_info_dict = utils_db.cr_curve_info_dictionary(controls_dict['FK_ctrls'], controls_dict['IK_ctrls'], self.unique_id, side)
                    # cr ori plane dict
                ori_plane_dict = utils_db.cr_ori_plane_dict(item_name_list[:-1], 10)
                self.update_db(conn, "controls", (
                    self.unique_id, 
                    controls_dict['FK_ctrls'], 
                    controls_dict['IK_ctrls'],
                    fk_pos,
                    fk_rot,
                    ik_pos,
                    ik_rot, 
                    curve_info_dict,
                    ori_plane_dict,
                    side
                    ))

        except sqlite3.Error as e:
            print(e)


    def add_table(self, conn): 
        sql_cr_table_state = [
        """CREATE TABLE IF NOT EXISTS modules (
            db_id INTEGER PRIMARY KEY,
            unique_id INT,
            module_name text NOT NULL,
            side text
        );""",
        """CREATE TABLE IF NOT EXISTS placement (
            db_id INTEGER PRIMARY KEY,
            unique_id INT,
            component_pos TEXT,
            component_rot TEXT,
            side text
        );""",
        """CREATE TABLE IF NOT EXISTS constant (
            db_id INTEGER PRIMARY KEY,
            unique_id INT,
            guides_connection TEXT,
            guides_follow TEXT,
            items TEXT,
            limbRoot_name TEXT,
            hock_name TEXT,
            ik_wld_name TEXT,
            side text
        );""",
        """CREATE TABLE IF NOT EXISTS user_settings (
            db_id INTEGER PRIMARY KEY,
            unique_id INT,
            input_hook_mtx_plug TEXT,
            output_hook_mtx_list TEXT,
            joint_num INT,
            size INT,
            side text
        );""",
        """CREATE TABLE IF NOT EXISTS controls (
            db_id INTEGER PRIMARY KEY,
            unique_id INT,
            FK_ctrls TEXT,
            IK_ctrls TEXT,
            fk_pos TEXT,
            fk_rot TEXT,
            ik_pos TEXT,
            ik_rot TEXT,
            curve_info TEXT,
            ori_plane_info TEXT,
            side text
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
            try:
                cursor.execute(sql, values)
            except sqlite3.Error as e:
                print(f"*** *** cr_DB_schema `constant` Error: {e}")

        elif table == 'placement':
            values = (values[0], json.dumps(values[1]), json.dumps(values[2]), values[3])
            sql = f""" INSERT INTO {table} (unique_id, component_pos, component_rot, side) VALUES (?, ?, ?, ?)"""
            try:
                cursor.execute(sql, values)
            except sqlite3.Error as e:
                print(f"*** *** cr_DB_schema `constant` Error: {e}")

        elif table == 'constant':
            values = (values[0], 
                      json.dumps(values[1]), json.dumps(values[2]), json.dumps(values[3]), 
                      values[4], 
                      values[5], 
                      values[6], 
                      values[7])
            sql = f""" INSERT INTO {table} 
                        (unique_id, 
                        guides_connection, guides_follow, items, 
                        limbRoot_name,
                        hock_name, 
                        ik_wld_name, 
                        side) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
            try:
                cursor.execute(sql, values)
            except sqlite3.Error as e:
                print(f"*** *** cr_DB_schema `constant` Error: {e}")

        elif table == 'user_settings':
            values = (values[0], 
                      json.dumps(values[1]), json.dumps(values[2]),
                      values[3],
                      values[4],
                      values[5])
            sql = f""" INSERT INTO {table}
                        (unique_id,
                        input_hook_mtx_plug, output_hook_mtx_list,
                        joint_num,
                        size,
                        side) VALUES (?, ?, ?, ?, ?, ?)"""
            try:
                cursor.execute(sql, values)
            except sqlite3.Error as e:
                print(f"*** *** cr_DB_schema `user_settings` Error: {e}")

        elif table == 'controls':
            values = (values[0], 
                      json.dumps(values[1]), json.dumps(values[2]), 
                      json.dumps(values[3]), json.dumps(values[4]), json.dumps(values[5]), json.dumps(values[6]),
                      json.dumps(values[7]), 
                      json.dumps(values[8]), 
                      values[9])
            sql = f""" INSERT INTO {table} 
                        (unique_id, 
                        FK_ctrls, IK_ctrls, 
                        fk_pos, fk_rot, ik_pos, ik_rot,
                        curve_info, 
                        ori_plane_info, 
                        side) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            try:
                cursor.execute(sql, values)
            except sqlite3.Error as e:
                print(f"*** *** cr_DB_schema `controls` Error: {e}")

        conn.commit()

       
    def query_uniqueID_tracker(self, conn):
        cursor = conn.cursor()
        cursor.execute(f"SELECT module_name, side, MAX(unique_id) FROM modules GROUP BY module_name, side")
        rows = cursor.fetchall()
        for row in rows:
            mdl_name, side, max_id = row
            self.unique_id_tracker[(mdl_name, side)] = max_id

    # global so the dict can keep track over multiple calls, to generate new unique_ids as expected
    def get_unique_id_sequence(self, mdl_name, side):
        '''function updates the next unique_id for a given combination. '''
        key = (mdl_name, side)
        print(f"key = {key} / self.unique_id_tracker = {self.unique_id_tracker}" )
        if key not in self.unique_id_tracker:
            print(f">> `unique_id` existing database is empty:{self.unique_id_tracker}, so set to 0")
            self.unique_id_tracker[key] = 0
        else:
            print(f">> `unique_id` dict from existing database = {self.unique_id_tracker}, adding +1")
            self.unique_id_tracker[key] += 1
        return self.unique_id_tracker[key]

#------------------------------------------------------------------------------
class RetrieveModulesData():
    def __init__(self, directory, database_name):
        db_directory = os.path.expanduser(directory)
        os.makedirs(db_directory, exist_ok=1)
        # db_name must include the entire path too!
        db_name = os.path.join(db_directory, database_name)

        try:
            with db_connection_tracker.DBConnectionTracker.get_connection(db_name) as conn:
                self.db_data_iteraion = self.dict_from_table(
                    conn, 'modules', database_name
                    )
                self.db_output_hook_mtx_dict = self.out_hk_mtx_from_table(
                    conn, 'user_settings', database_name
                    )
                self.db_input_hook_mtx_dict = self.inp_hk_mtx_from_table(
                    conn, 'user_settings', database_name
                    )
        except sqlite3.Error as e:
            print(e)

        
    def dict_from_table(self, conn, table, database_name):
        # return a dict where each key is the database_name & each value is tuple of (unique_id & side)
        cursor = conn.cursor()
        query_param_state = f"SELECT unique_id, side FROM {table}"
        try:
            cursor.execute(query_param_state)
            rows = cursor.fetchall()
            db_data = {database_name: []}

            # rows == [int(unique_id), string(side)]
            if rows:
                for row in rows:
                    unique_id, side = row[0], row[1]
                    db_data[database_name].append((unique_id, side))
            return db_data

        except sqlite3.Error as e:
            print(f"** DB_DATA sqlite3.Error: {e}")
            return {}
        

    def out_hk_mtx_from_table(self, conn, table, database_name):
        # return a dict where each key is the database_name & each value is tuple of (unique_id & side)
        cursor = conn.cursor()
        query = f"SELECT output_hook_mtx_list FROM {table}"
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            out_data_dict = {}
            
            if rows:
                for row in rows:
                    out_data_json = row[0]
                    print(f">> db_schema_002: out_hk_mtx = {out_data_json}")
                    # if out_hk_mtx_json:
                    out_attr = json.loads(out_data_json)
                    out_data_dict[database_name] = out_attr
                    # else:
                    #     out_hk_mtx_list = []
                    #     # db_out_hk_mtx_data.append([])

            return out_data_dict

        except sqlite3.Error as e:
            print(f"** 'out_hk_mtx_from_table' sqlite3.Error: {e}")
            return {}
    

    def inp_hk_mtx_from_table(self, conn, table, database_name):
        cursor = conn.cursor()
        query = f"SELECT input_hook_mtx_plug FROM {table}"
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            inp_data_dict = {}

            if rows:
                for row in rows:
                    inp_attr_json = row[0]
                    inp_attr = json.loads(inp_attr_json)
                    inp_data_dict[database_name] = inp_attr
            return inp_data_dict

        except sqlite3.Error as e:
            print(f"** inp_hk_mtx_from_table sqlite3.Error: {e}")
            return {}
        

# ---- Inheritance ----
class DatabaseSchema():
    def __init__(self, directory, module_name, unique_id, side):
        self.db_path = utils_db.get_database_name_path(directory, module_name)

        self.module_name = module_name
        self.unique_id = unique_id
        self.side = side


class RetrievePlacementData(DatabaseSchema):
    def __init__(self, directory, module_name, unique_id, side):
        super().__init__(directory, module_name, unique_id, side)
        try:
            with db_connection_tracker.DBConnectionTracker.get_connection(self.db_path) as conn:
                self.existing_pos_dict = self.component_pos_dict_from_table(conn)
                self.existing_rot_dict = self.component_rot_dict_from_table(conn)
                self.existing_plane_dict = self.component_ori_plane_dict_from_table(conn)
                self.controls_dict = self.controls_dict_from_table(conn)

                self.mdl_component_dict = {
                    "module_name":self.module_name, 
                    "unique_id":int(self.unique_id),
                    "side":self.side,
                    "component_pos": self.existing_pos_dict,
                    "controls": self.controls_dict
                    }
                
        except sqlite3.Error as e:
            print(f"module component retrieval sqlite3.Error: {e}")
    

    def component_pos_dict_from_table(self, conn):
        cursor = conn.cursor()
        placement_sql = f"SELECT component_pos FROM placement WHERE unique_id = ? AND side = ? "
        try:
            cursor.execute(placement_sql, (self.unique_id, self.side,))
            row = cursor.fetchone()
            if row:
                component_pos_json = row[0]
                # use Python's 'json module' to load json dict into python dictionary's
                component_pos_dict = json.loads(component_pos_json)
            return component_pos_dict

        except sqlite3.Error as e:
            print(f"placement sqlite3.Error: {e}")
            return {}
    

    def component_rot_dict_from_table(self, conn):
        cursor = conn.cursor()
        placement_sql = f"SELECT component_rot FROM placement WHERE unique_id = ? AND side = ? "
        try:
            cursor.execute(placement_sql, (self.unique_id, self.side,))
            row = cursor.fetchone()
            if row:
                component_rot_json = row[0]
                # use Python's 'json module' to load json dict into python dictionary's
                component_rot_dict = json.loads(component_rot_json)
            return component_rot_dict

        except sqlite3.Error as e:
            print(f"placement sqlite3.Error: {e}")
            return {}
        

    def component_ori_plane_dict_from_table(self, conn):
        cursor = conn.cursor()
        sql = f"SELECT ori_plane_info FROM controls WHERE unique_id = ? AND side = ? "
        try:
            cursor.execute(sql, (self.unique_id, self.side,))
            row = cursor.fetchone()
            if row:
                comp_plane_json = row[0]
                comp_plane_dict = json.loads(comp_plane_json)
            return comp_plane_dict

        except sqlite3.Error as e:
            print(f"placement sqlite3.Error: {e}")
            return {}


    def controls_dict_from_table(self, conn):
        cursor = conn.cursor()
        controls_sql = f"SELECT FK_ctrls, IK_ctrls FROM controls WHERE unique_id = ? AND side = ? "
        try:
            cursor.execute(controls_sql, (self.unique_id, self.side,))
            rows = cursor.fetchall()
            controls_dict = {"FK_ctrls":{}, "IK_ctrls":{}}
            if rows:
                for row in rows:
                    fk_ctrls_sjon =row[0] 
                    ik_ctrl_json = row[1]
                    # use Python's 'json module' to load json dict into python dictionary's
                    controls_dict["FK_ctrls"] = json.loads(fk_ctrls_sjon)
                    controls_dict["IK_ctrls"] = json.loads(ik_ctrl_json)
            return controls_dict

        except sqlite3.Error as e:
            print(f"controls sqlite3.Error: {e}")
            return {}


    def return_existing_pos_dict(self):
        return self.existing_pos_dict
    

    def return_existing_rot_dict(self):
        return self.existing_rot_dict
    

    def return_existing_plane_dict(self):
        return self.existing_plane_dict


    def return_controls_typ_dict(self):
        return self.controls_dict


    def return_mdl_component_dict(self):
        return self.mdl_component_dict


class RetrieveConstantData(DatabaseSchema):
    def __init__(self, directory, module_name, unique_id, side):
        super().__init__(directory, module_name, unique_id, side)

        try:
            with db_connection_tracker.DBConnectionTracker.get_connection(self.db_path) as conn:
                self.limbRoot_name = self.get_constant_attr_from_table(conn, "limbRoot_name")
                self.hock_name = self.get_constant_attr_from_table(conn, "hock_name")
                self.ik_wld_name = self.get_constant_attr_from_table(conn, "ik_wld_name")
        except sqlite3.Error as e:
            print(f"Constant Data Retrieval sqlite3.Error: {e}")


    def get_constant_attr_from_table(self, conn, attr_name):
        cursor = conn.cursor()
        placement_sql = f"SELECT {attr_name} FROM constant WHERE unique_id = ? AND side = ? "
        try:
            cursor.execute(placement_sql, (self.unique_id, self.side,))
            row = cursor.fetchone()
            if row:
                const_attr = row[0]
            return const_attr

        except sqlite3.Error as e:
            print(f"Constant Data Retrieval sqlite3.Error: {e}")
            return None
        

    def return_limbRoot_name(self):
        return self.limbRoot_name
    

    def return_hock_name(self):
        return self.hock_name
    

    def return_ik_wld_name(self):
        return self.ik_wld_name
        

class RetrieveSpecificData(DatabaseSchema):
    def __init__(self, directory, module_name, unique_id, side):
        super().__init__(directory, module_name, unique_id, side)
        try:
            with db_connection_tracker.DBConnectionTracker.get_connection(self.db_path) as conn:
                self.jnt_num = self.get_jnt_num(conn, "user_settings")
                self.inp_hk_mtx = self.inp_hk_mtx_from_table(conn, "user_settings")
                self.out_hk_mtx = self.out_hk_mtx_from_table(conn, "user_settings")
                self.guides_connection, self.guides_follow = self.get_guide_data(conn, "constant")
                self.ori_plane_dict = self.get_ori_plane_data(conn, "controls")
        except sqlite3.Error as e:
            print(f"DB* module umo update Error: {e}")
    
    
    def inp_hk_mtx_from_table(self, conn, table):
        cursor = conn.cursor()
        query = f"SELECT input_hook_mtx_plug FROM {table} WHERE unique_id = ? AND side = ?"
        try:
            cursor.execute(query, (self.unique_id, self.side,))
            row = cursor.fetchone()
            print(f"**inp_hk_mtx row={row}")
            if row:
                inp_plg_json = row[0]
                inp_plg = json.loads(inp_plg_json)
                return inp_plg #inp_attr
            else:
                print(f"Not row: {self.module_name}")
            # return inp_data_list

        except sqlite3.Error as e:
            print(f"** inp_hk_mtx_from_table sqlite3.Error: {e}")
            return []
        
    
    def out_hk_mtx_from_table(self, conn, table):
        cursor = conn.cursor()
        query = f"SELECT output_hook_mtx_list FROM {table} WHERE unique_id = ? AND side = ?"
        try:
            cursor.execute(query, (self.unique_id, self.side,))
            row = cursor.fetchone()
            if row:
                out_hk_mtx_ls_json = row[0]
                out_hk_mtx_ls = json.loads(out_hk_mtx_ls_json)
                return out_hk_mtx_ls #inp_attr
            else:
                print(f"No out_hk_mtx row: {self.module_name}")
            # return inp_data_list

        except sqlite3.Error as e:
            print(f"** inp_hk_mtx_from_table sqlite3.Error: {e}")
            return []


    def get_jnt_num(self, conn, table):
        cursor = conn.cursor()
        sql = f"SELECT joint_num FROM {table} WHERE unique_id = ? AND side = ? "
        try:
            cursor.execute(sql, (self.unique_id, self.side,))
            row = cursor.fetchone()
            if row:
                jnt_num = row[0]
                if jnt_num is None:
                    return 'NULL'
                else:
                    return jnt_num
            else:
                return 'NULL'
        except sqlite3.Error as e:
            print(f"placement sqlite3.Error: {e}")
            return {}
        
    
    def get_guide_data(self, conn, table):
        cursor = conn.cursor()
        sql= f"SELECT guides_connection, guides_follow FROM {table} WHERE unique_id = ? AND side = ? "
        try:
            cursor.execute(sql, (self.unique_id, self.side,))
            rows = cursor.fetchall()
            # controls_dict = {"FK_ctrls":{}, "IK_ctrls":{}}
            if rows:
                for row in rows:
                    gd_con_json =row[0] 
                    gd_fol_json = row[1]
                    # use Python's 'json module' to load json list into python dictionary's
                    guides_connection = json.loads(gd_con_json)
                    guides_follow = json.loads(gd_fol_json)
                    print(f"DB > guides_connection = {guides_connection}")
                    print(f"DB > guides_follow = {guides_follow}")
            return guides_connection, guides_follow
        except sqlite3.Error as e:
            print(f"constant table sqlite3.Error: {e}")
            return None, None
        

    def get_ori_plane_data(self, conn, table):
        cursor = conn.cursor()
        sql= f"SELECT ori_plane_info FROM {table} WHERE unique_id = ? AND side = ? "
        try:
            cursor.execute(sql, (self.unique_id, self.side,))
            row = cursor.fetchone()
            if row:
                ori_pln_dict = json.loads(row[0])
                print(f"DB > ori_pln_dict = `{ori_pln_dict}`")
            return ori_pln_dict
        except sqlite3.Error as e:
            print(f"controls table sqlite3.Error: {e}")
            return None

    def return_inp_hk_mtx(self):
        return self.inp_hk_mtx
    
    def return_out_hk_mtx(self):
        return self.out_hk_mtx

    def return_get_jnt_num(self):
        return self.jnt_num
    
    def return_guides_connection(self):
        return self.guides_connection
    
    def return_guides_follow(self):
        return self.guides_follow
    
    def return_ori_plane_dict(self):
        return self.ori_plane_dict
    
# NEW 24/12/2025 -> less other operations being retrieved from db!
class RetrieveMtxModuleData(DatabaseSchema):
    def __init__(self, directory, module_name, unique_id, side):
        super().__init__(directory, module_name, unique_id, side)
        try:
            with db_connection_tracker.DBConnectionTracker.get_connection(self.db_path) as conn:
                self.inp_hk_mtx = self.inp_hk_mtx_from_table(conn, "user_settings")
                self.out_hk_mtx = self.out_hk_mtx_from_table(conn, "user_settings")
        except sqlite3.Error as e:
            print(f"DB* module umo update Error: {e}")
    
    
    def inp_hk_mtx_from_table(self, conn, table):
        cursor = conn.cursor()
        query = f"SELECT input_hook_mtx_plug FROM {table} WHERE unique_id = ? AND side = ?"
        try:
            cursor.execute(query, (self.unique_id, self.side,))
            row = cursor.fetchone()
            if row:
                inp_plg_json = row[0]
                inp_plg = json.loads(inp_plg_json)
                return inp_plg #inp_attr
            else:
                print(f"Not row: {self.module_name}")

        except sqlite3.Error as e:
            print(f"** inp_hk_mtx_from_table sqlite3.Error: {e}")
            return []
        
    
    def out_hk_mtx_from_table(self, conn, table):
        cursor = conn.cursor()
        query = f"SELECT output_hook_mtx_list FROM {table} WHERE unique_id = ? AND side = ?"
        try:
            cursor.execute(query, (self.unique_id, self.side,))
            row = cursor.fetchone()
            if row:
                out_hk_mtx_ls_json = row[0]
                out_hk_mtx_ls = json.loads(out_hk_mtx_ls_json)
                return out_hk_mtx_ls #inp_attr
            else:
                print(f"No out_hk_mtx row: {self.module_name}")

        except sqlite3.Error as e:
            print(f"** inp_hk_mtx_from_table sqlite3.Error: {e}")
            return []
        

    def return_inp_hk_mtx(self):
        return self.inp_hk_mtx
    
    def return_out_hk_mtx(self):
        return self.out_hk_mtx    


class RetrieveControlsData(DatabaseSchema):
    def __init__(self, directory, module_name, unique_id, side):
        super().__init__(directory, module_name, unique_id, side)
        try:
            with db_connection_tracker.DBConnectionTracker.get_connection(self.db_path) as conn:
                self.fk_pos_dict = self.fkik_posrot_from_table(conn, "fk", "pos")
                self.fk_rot_dict = self.fkik_posrot_from_table(conn, "fk", "rot")
                self.ik_pos_dict = self.fkik_posrot_from_table(conn, "ik", "pos")
                self.ik_rot_dict = self.fkik_posrot_from_table(conn, "ik", "rot")
        except sqlite3.Error as e:
            print(f"DB* module umo update Error: {e}")
    
    
    def fkik_posrot_from_table(self, conn, type, value):
        cursor = conn.cursor()
        query = f"SELECT {type}_{value} FROM controls WHERE unique_id = ? AND side = ?"
        try:
            cursor.execute(query, (self.unique_id, self.side,))
            row = cursor.fetchone()
            if row:
                ctrl_dict_json = row[0]
                ctrl_dict = json.loads(ctrl_dict_json)
                return ctrl_dict #inp_attr
            else:
                print(f"Not row: {self.module_name}")

        except sqlite3.Error as e:
            print(f"** fkik_pos_from_table() sqlite3.Error: {e}")
            return []


    def return_fk_pos_dict(self):
        return self.fk_pos_dict
    
    def return_fk_rot_dict(self):
        return self.fk_rot_dict    
    
    def return_ik_pos_dict(self):
        return self.ik_pos_dict
    
    def return_ik_rot_dict(self):
        return self.ik_rot_dict    


#------------------------------------------------------------------------------
class UpdateSpecificPlacementPOSData(DatabaseSchema):
    def __init__(self, directory, module_name, unique_id, side, updated_pos_dict):
        super().__init__(directory, module_name, unique_id, side)
        try:
            with db_connection_tracker.DBConnectionTracker.get_connection(self.db_path) as conn:
                self.update_db(conn, "placement", (updated_pos_dict, unique_id, side))
                print(f"Updated database `component_pos`: {self.db_path} with {updated_pos_dict}, where its unique_id = {unique_id} & side = {side}")
        except sqlite3.Error as e:
            print(f"module component retrieval sqlite3.Error: {e}")
    

    def update_db(self, conn, table, values):
        cursor = conn.cursor()
        if table == 'placement':
            print(f"H H placement VALUES: {values}")
            sql = f'UPDATE {table} SET component_pos = ? WHERE unique_id = ? AND side = ?'
            values = (json.dumps(values[0]), values[1], values[2])
            cursor.execute(sql, values)
        conn.commit()


class UpdatePlacementROTData(DatabaseSchema):
    def __init__(self, directory, module_name, unique_id, side, updated_rot_dict, updated_plane_dict):
        super().__init__(directory, module_name, unique_id, side)

        try:
            with db_connection_tracker.DBConnectionTracker.get_connection(self.db_path) as conn:
                self.update_rot_data(conn, "placement", (updated_rot_dict, unique_id, side))
                self.update_plane_data(conn, "controls", (updated_plane_dict, unique_id, side))
                print(f"Updated database `component_rot`: {self.db_path} with {updated_rot_dict}, where its unique_id = {unique_id} & side = {side}")
        except sqlite3.Error as e:
            print(f"module component retrieval sqlite3.Error: {e}")
    

    def update_rot_data(self, conn, table, values):
        cursor = conn.cursor()
        if table == 'placement':
            sql = f'UPDATE {table} SET component_rot = ? WHERE unique_id = ? AND side = ?'
            values = (json.dumps(values[0]), values[1], values[2])
            cursor.execute(sql, values)
        conn.commit()
    

    def update_plane_data(self, conn, table, values):
        cursor = conn.cursor()
        if table == 'controls':
            sql = f'UPDATE {table} SET ori_plane_info = ? WHERE unique_id = ? AND side = ?'
            values = (json.dumps(values[0]), values[1], values[2])
            cursor.execute(sql, values)
        conn.commit()


class UpdateControlsRawData(DatabaseSchema):
    def __init__(self, directory, module_name, unique_id, side, fk_pos, fk_rot, ik_pos, ik_rot):
        super().__init__(directory, module_name, unique_id, side)

        try:
            with db_connection_tracker.DBConnectionTracker.get_connection(self.db_path) as conn:
                self.update_controls_raw_dict(conn, "fk_pos", (fk_pos, unique_id, side))
                self.update_controls_raw_dict(conn, "fk_rot", (fk_rot, unique_id, side))
                self.update_controls_raw_dict(conn, "ik_pos", (ik_pos, unique_id, side))
                self.update_controls_raw_dict(conn, "ik_rot", (ik_rot, unique_id, side))
        except sqlite3.Error as e:
            print(f"Constant Data Retrieval sqlite3.Error: {e}")
    

    def update_controls_raw_dict(self, conn, dict_name, values):
        cursor = conn.cursor()
        sql = f'UPDATE controls SET {dict_name} = ? WHERE unique_id = ? AND side = ?'
        values = (json.dumps(values[0]), values[1], values[2])
        cursor.execute(sql, values)
        conn.commit()


class CurveInfoData(DatabaseSchema):
    def __init__(self, directory, module_name, unique_id, side):
        super().__init__(directory, module_name, unique_id, side)
        try:
            with db_connection_tracker.DBConnectionTracker.get_connection(self.db_path) as conn:
                self.comp_control_ls, self.curve_info_dict = self.curve_info_from_row(conn)
        except sqlite3.Error as e:
            print(f"module component retrieval sqlite3.Error: {e}")
    

    def curve_info_from_row(self, conn):
        cursor = conn.cursor()
        controls_sql = f"SELECT curve_info FROM controls WHERE unique_id = ? AND side = ? "
        try:
            cursor.execute(controls_sql, (self.unique_id, self.side,))
            rows = cursor.fetchall()
            controls_list = []
            if rows:
                for row in rows:
                    ctrls_sjon =row[0]
                    controls_list = list(json.loads(ctrls_sjon).keys())
                curv_info_dict = json.loads(ctrls_sjon)
            return controls_list, curv_info_dict

        except sqlite3.Error as e:
            print(f"controls sqlite3.Error: {e}")
            return {}
        
    
    def return_comp_ctrl_ls(self):
        return self.comp_control_ls
    

    def return_curve_info_dict(self):
        return self.curve_info_dict
    

class UpdateCurveInfo(DatabaseSchema):
    def __init__(self, directory, module_name, unique_id, side, comp_ctrl_data):
        super().__init__(directory, module_name, unique_id, side)
        try:
            with db_connection_tracker.DBConnectionTracker.get_connection(self.db_path) as conn:
                self.update_db(conn, (comp_ctrl_data, unique_id, side))
                print(f"Updated database `curve_info`: DB_{module_name}.db with {comp_ctrl_data}, where its unique_id = {unique_id} & side = {side}")
        except sqlite3.Error as e:
            print(f"DB* module component retrieval sqlite3.Error: {e}")

    
    def update_db(self, conn, values):
        cursor = conn.cursor()
        sql = f'UPDATE controls SET curve_info = ? WHERE unique_id = ? AND side = ?'
        values = (json.dumps(values[0]), values[1], values[2])
        cursor.execute(sql, values)
        conn.commit()


# class UpdateUserSettings(DatabaseSchema):
#     def __init__(self, directory, module_name, unique_id, side, umo_dict):
#         super().__init__(directory, module_name, unique_id, side)
#         try:
#             with db_connection_tracker.DBConnectionTracker.get_connection(self.db_path) as conn:
#                 self.update_user_setting(conn, "user_settings", umo_dict)
#         except sqlite3.Error as e:
#             print(f"DB* module umo update Error: {e}")


#     def update_user_setting(self, conn, table, umo_dict):
#         cursor = conn.cursor()
#         # get values!
#         if table == 'user_settings':
#             sql = f'UPDATE {table} SET mirror_rig = ?, stretch = ?, twist = ?, rig_default = ? WHERE unique_id = ? AND side = ?'
#             values = (umo_dict["mirror_rig"], umo_dict["stretch"], umo_dict["twist"], umo_dict["rig_sys"], self.unique_id, self.side)
#             cursor.execute(sql, values)


class UpdateJointNum(DatabaseSchema):
    def __init__(self, directory, module_name, unique_id, side, jnt_num):
        super().__init__(directory, module_name, unique_id, side)
        try:
            with db_connection_tracker.DBConnectionTracker.get_connection(self.db_path) as conn:
                self.update_joint_num(conn, "user_settings", jnt_num)
        except sqlite3.Error as e:
            print(f"DB* module umo update Error: {e}")


    def update_joint_num(self, conn, table, jnt_num):
        cursor = conn.cursor()
        if table == 'user_settings':
            sql = f'UPDATE {table} SET joint_num = ? WHERE unique_id = ? AND side = ?'
            values = (jnt_num, self.unique_id, self.side)
            cursor.execute(sql, values)

#------------------------------------------------------------------------------
class CheckMirrorData(DatabaseSchema):
    def __init__(self, directory, module_name, unique_id, side):
        super().__init__(directory, module_name, unique_id, side)
        try:
            with db_connection_tracker.DBConnectionTracker.get_connection(self.db_path) as conn:
                self.mirror_database_exists = self.get_database_side_exists(conn, "modules")
        except sqlite3.Error as e:
            print(f"DB* check mirror data Error: {e}")

        
    def get_database_side_exists(self, conn, table):
        cursor = conn.cursor()
        sql = f"SELECT module_name FROM {table} WHERE unique_id = ? AND side = ? "
        try:
            cursor.execute(sql, (self.unique_id, self.side,))
            row = cursor.fetchone()
            if row:
                print(f"DB mirror Database does exist")
                return True
            else:
                print(f"DB mirror Database does NOT exist")
                return False
        except sqlite3.Error as e:
            print(f"placement sqlite3.Error: {e}")
            return False


    def return_mirror_database_exists(self):
        return self.mirror_database_exists
    
#------------------------------------------------------------------------------
class DeleteComponentRows(DatabaseSchema):
    def __init__(self, directory, module_name, unique_id, side):
        '''
        # Description:
            Delete all traces of the specific component's rows to delete it from the db file. 
        # Attributes:
            directory (string path): Path to the folder the db is stored in.
            module_name (string): Name of the db module
            unique_id (string): unique_id of the db module
            side (string): side of the db module
        # Returns: N/A 
        '''
        super().__init__(directory, module_name, unique_id, side)

        print(f"Del_comp row: db_path = {self.db_path}")

        try:
            with sqlite3.connect(self.db_path) as conn:
                self.delete_row(conn, "constant")
                self.delete_row(conn, "controls")
                self.delete_row(conn, "modules")
                self.delete_row(conn, "placement")
                self.delete_row(conn, "user_settings")
                print(f"schema: Compoonent deletion successful")
        except sqlite3.Error as e:
            print(f"schema: Component deletion Error: {e}")
    

    def delete_row(self, conn, table):
        cursor = conn.cursor()
        del_sql = f'DELETE FROM {table} WHERE unique_id = ? AND side = ?'
        values = (self.unique_id, self.side)
        print(f"Delete table {table} row with VALUES: {values}")
        cursor.execute(del_sql, values)




        
