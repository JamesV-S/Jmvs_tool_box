
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

from utils import (
    utils,
    utils_db
)

from databases import database_manager
importlib.reload(database_manager)
importlib.reload(utils)
importlib.reload(utils_db)


class retrieveModulesData():
    def __init__(self, directory, database_name):
        self.mdl_populate_tree_dict = {}
        # db_directory = os.path.expanduser(directory)
        # os.makedirs(db_directory, exist_ok=1)
        # # db_name must include the entire path too!
        # db_name = os.path.join(db_directory, database_name)
        db_path = utils_db.get_database_name_path(directory, database_name)


        try:
            with sqlite3.connect(db_path) as conn:
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
            # rows == [int(unique_id), string(side)]
            mdl_populate_tree_dict = {database_name: []}
            if rows:
                for row in rows:
                    unique_id, side = row[0], row[1]
                    mdl_populate_tree_dict[database_name].append((unique_id, side))
            return mdl_populate_tree_dict

        except sqlite3.Error as e:
            print(f"sqlite3.Error: {e}")
            return {}
        

class retrieveSpecificComponentdata():
    def __init__(self, directory, module_name, unique_id, side):
        print(f" Retrieve specific component data MODULE_NAME: {module_name} ")

        db_path = utils_db.get_database_name_path(directory, module_name)

        # constants:
        self.module_name = module_name
        self.unique_id = unique_id
        self.side = side

        try:
            with sqlite3.connect(db_path) as conn:
                pos_dict = self.position_dict_from_table(conn)
                self.rot_dict = self.rotation_dict_from_table(conn)
                self.controls_dict = self.controls_dict_from_table(conn)
                self.mdl_component_dict = {
                    "module_name":self.module_name, 
                    "unique_id":int(self.unique_id),
                    "side":self.side,
                    "component_pos": pos_dict,
                    "controls": self.controls_dict
                    }
                print(f"THE DICT :: self.mdl_component_dict = {self.mdl_component_dict}")
                
        except sqlite3.Error as e:
            print(f"module component retrieval sqlite3.Error: {e}")
    

    def position_dict_from_table(self, conn):
        cursor = conn.cursor()
        placement_sql = f"SELECT component_pos FROM placement WHERE unique_id = ? AND side = ? "
        try:
            cursor.execute(placement_sql, (self.unique_id, self.side,))
            row = cursor.fetchone()
            if row:
                component_pos_json = row[0]
                # use Python's 'json module' to load json dict into python dictionary's
                component_pos_dict = json.loads(component_pos_json)
                print(f"component_pos = {component_pos_dict}")
            return component_pos_dict              

        except sqlite3.Error as e:
            print(f"placement sqlite3.Error: {e}")
            return {}
        

    def rotation_dict_from_table(self, conn):
        cursor = conn.cursor()
        placement_sql = f"SELECT component_rot_xyz FROM placement WHERE unique_id = ? AND side = ? "
        try:
            cursor.execute(placement_sql, (self.unique_id, self.side,))
            row = cursor.fetchone()
            if row:
                comp_rot_json = row[0]
                # use Python's 'json module' to load json dict into python dictionary's
                comp_rot_dict = json.loads(comp_rot_json)
                print(f"component_pos = {comp_rot_dict}")
            return comp_rot_dict              

        except sqlite3.Error as e:
            print(f"table placement, ROT sqlite3.Error: {e}")
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
                    print(f"controls_dict = {controls_dict}")
            return controls_dict

        except sqlite3.Error as e:
            print(f"controls sqlite3.Error: {e}")
            return {}
        

    def return_mdl_component_dict(self):
        return self.mdl_component_dict

    
    def return_rot_component_dict(self):
        return self.rot_dict
    
    def return_pos_dict(self):
        return self.controls_dict
    

class retrieveSpecificPlacementPOSData():
    def __init__(self, directory, module_name, unique_id, side):
        db_directory = os.path.expanduser(directory)
        os.makedirs(db_directory, exist_ok=1)
        # db_name must include the entire path too!
        database_name = f"DB_{module_name}.db"
        db_name = os.path.join(db_directory, database_name)

        # constants:
        self.module_name = module_name
        self.unique_id = unique_id
        self.side = side

        try:
            with sqlite3.connect(db_name) as conn:
                self.existing_pos_dict = self.component_pos_dict_from_table(conn)
                self.existing_rot_dict = self.component_rot_dict_from_table(conn)
                self.existing_plane_dict = self.component_ori_plane_dict_from_table(conn)
                
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
        placement_sql = f"SELECT component_rot_xyz FROM placement WHERE unique_id = ? AND side = ? "
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


    def return_existing_pos_dict(self):
        return self.existing_pos_dict
    
    def return_existing_rot_dict(self):
        return self.existing_rot_dict
    
    def return_existing_plane_dict(self):
        return self.existing_plane_dict


class RetrieveSpecificData():
    def __init__(self, directory, module_name, unique_id, side):
        db_path = utils_db.get_database_name_path(directory, module_name)
        self.unique_id = unique_id
        self.side = side
        try:
            with sqlite3.connect(db_path) as conn:
                self.jnt_num = self.get_jnt_num(conn, "user_settings")
                self.guides_connection, self.guides_follow = self.get_guide_data(conn, "constant")
                self.ori_plane_dict = self.get_ori_plane_data(conn, "controls")
        except sqlite3.Error as e:
            print(f"DB* module umo update Error: {e}")


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


    def return_get_jnt_num(self):
        return self.jnt_num
    

    def return_guides_connection(self):
        return self.guides_connection
    

    def return_guides_follow(self):
        return self.guides_follow
    
    def return_ori_plane_dict(self):
        return self.ori_plane_dict
    

# -----------------------------------------------------------------------------

# Class Parent
class RetrieveDatabase():
    def __init__(self, directory, module_name=None, unique_id=None, side=None):
        '''
        # Description:
            Prent class for all operation's to do with 'Retrieval'.
            4 major functions that will be called in the child classes.
        # Attributes: 
            directory (string): Path where the databases are stored. (not the full path including the directory to work on) 
            module_name (string): Name of the .db module.
            unique_id (string): Name of the 'unique_id' row in .db file .
            side (string): Name of the 'side' row in .db file.
        # Returns: N/A
        '''
        self.directory = directory
        self.module_name = module_name
        self.unique_id = unique_id
        self.side = side
        self.connection = None


    def get_db_path(self):
        '''
        # Description:
            Get the database path.
        # Attributes: N/A
        # Returns: (string) ' / / / / '
        '''
        return utils_db.get_database_name_path(self.directory, self.module_name)
    
    def connect(self, db_path):
        '''
        # Description:
            Establish the database connection and handle any connection arrors with this function
        # Attributes: N/A
        # Returns: (Parent Class Variable) Stores sqlite3.connect(*)
        '''
        try:
            self.connection = sqlite3.connect(db_path)
            return self.connection
        except sqlite3.Error as e:
            print(f"Databse connection error: {e}")
            return None


    def close_connection(self):
        '''
        # Description:
            Close the databse connect. Having open connecions can cause the databses 
            to be locked. (I think this is why I am undable to delete module databses 
            without closing Maya)
        # Attributes: N/A
        # Returns: N/A
        '''
        if self.connection:
            self.connection.close()
            self.connection = None

    
    def execute_query(self, query, params = None):
        '''
        # Description:
            Execute a given query (sql) and return the cursor
        # Attributes: N/A
        # Returns: N/A
        '''
        if not self.connection:
            raise ConnectionError
        
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except sqlite3.Error as e:
            print(f"Query execution error: {e}")
            raise
            

# child class
class RetrieveModuleTable(RetrieveDatabase):
    '''
    # Description:
        Child class of 'RetrieveDatabase' parent. Retireving module-level component 
        data in spcific .db file.
    # Attributes: N/A
    # Returns: N/A
    '''
    def __init__(self, directory, database_name):
        super().__init__(directory)
        # print(f"self.directory = {self.directory}")
        self.db_name = database_name
        self.mdl_data_dict = {}
        
    
    def retrieve_data(self):
        # db_path = self.get_db_path()
        db_directory = os.path.expanduser(self.directory)
        os.makedirs(db_directory, exist_ok=True)
        db_path = os.path.join(db_directory, self.db_name)
        try:
            with self.connect(db_path) as conn:
                print(f"> db_path = {db_path}")
                
                # self.mdl_populate_tree_dict = self.dict_from_table(
                #     'modules', self.db_name
                #     )
        except sqlite3.Error as e:
            print(f"Module component data retireval error: {e}")

        print(f"class module data `self.mdl_data_dict` = {self.mdl_data_dict}")

        return self.mdl_data_dict
    

    def dict_from_table(self, table, database_name):
        '''
        # Description:
            Child class of 'RetrieveDatabase' parent. Retireving module-level component 
            data in spcific .db file.
        # Attributes: 
            conn (sqlite): open connection. 
            table (string): name of the table to retireve data from. 
            database_name (string) module name of the database [e.g: 'bipedArm']
        # Returns: 
            mdl_data_dict (dict): key = database name, value = (unique_id, side)
        '''
        print(f"> Running dict_from_table()")
        query = f"SELECT unique_id, side FROM {table}"
        try:
            cursor = self.execute_query(query)
            rows = cursor.fetchall()
            # rows == [int(unique_id), string(side)]
            mdl_data_dict = {database_name: []}
            if rows:
                for row in rows:
                    unique_id, side = row[0], row[1]
                    mdl_data_dict[database_name].append((unique_id, side))
        
            return mdl_data_dict

        except sqlite3.Error as e:
            print(f"sqlite3.Error: {e}")
            return {}
        


class RetrieveCompData(RetrieveDatabase):
    def __init__(self, directory, module_name, unique_id, side):
        super().__init__(directory, module_name, unique_id, side)
        self.rot_dict = {}
        self.controls_dict = {}
        self.mdl_component_dict = {}

    def retrieve_data(self):
        db_path = self.get_db_path()
        try:
            with self.connect(db_path) as conn:
                pos_dict = self.position_dict_from_table()
                self.rot_dict = self.rotation_dict_from_table()
                self.controls_dict = self.controls_dict_from_table()

                self.mdl_component_dict = {
                    "module_name":self.module_name, 
                    "unique_id":int(self.unique_id),
                    "side":self.side,
                    "component_pos": pos_dict,
                    "controls": self.controls_dict
                    }
                
                print(f"Component data retrieved = {self.mdl_component_dict}")
                
        except sqlite3.Error as e:
            print(f"Component data retrieval error: {e}")

        return self.mdl_component_dict
    

    def position_dict_from_table(self):
        query = f"SELECT component_pos FROM placement WHERE unique_id = ? AND side = ? "
        try:
            cursor = self.execute_query(query, (self.unique_id, self.side))
            row = cursor.fetchone()
            if row:
                component_pos_json = row[0]
                # use Python's 'json module' to load json dict into python dictionary's
                component_pos_dict = json.loads(component_pos_json)
                print(f"component_pos = {component_pos_dict}")
                return component_pos_dict              

        except sqlite3.Error as e:
            print(f"Position data retrieval error: {e}")
            return {}
        

    def rotation_dict_from_table(self):
        query = f"SELECT component_rot_xyz FROM placement WHERE unique_id = ? AND side = ? "
        try:
            # cursor.execute(placement_sql, (self.unique_id, self.side,))
            cursor = self.execute_query(query, (self.unique_id, self.side))
            row = cursor.fetchone()

            if row:
                comp_rot_json = row[0]
                # use Python's 'json module' to load json dict into python dictionary's
                comp_rot_dict = json.loads(comp_rot_json)
                print(f"component_rot = {comp_rot_dict}")
                return comp_rot_dict              

        except sqlite3.Error as e:
            print(f"Rotation data retrieval error: {e}")
            return {}
        

    def controls_dict_from_table(self):
        query = f"SELECT FK_ctrls, IK_ctrls FROM controls WHERE unique_id = ? AND side = ? "
        try:
            # cursor.execute(controls_sql, (self.unique_id, self.side,))
            cursor = self.execute_query(query, (self.unique_id, self.side))
            rows = cursor.fetchall()
            controls_dict = {"FK_ctrls":{}, "IK_ctrls":{}}
            if rows:
                for row in rows:
                    fk_ctrls_sjon =row[0] 
                    ik_ctrl_json = row[1]
                    # use Python's 'json module' to load json dict into python dictionary's
                    controls_dict["FK_ctrls"] = json.loads(fk_ctrls_sjon)
                    controls_dict["IK_ctrls"] = json.loads(ik_ctrl_json)
                    print(f"controls_dict = {controls_dict}")
            return controls_dict

        except sqlite3.Error as e:
            print(f"Control data retrieval error: {e}")
            return {}
        
    # Use @property methods for easy acces to the data
    @property
    def component_dict(self):
        return self.mdl_component_dict

    @property
    def position_dict(self):
        return self.controls_dict

    @property
    def rotation_dict(self):
        return self.rot_dict
    
    
    
# example testing:
# # Example 1: Retrieve module data
# module_retriever = RetrieveModuleTable("~/my_app/data", "my_database.db")
# module_data = module_retriever.retrieve_data()
# print(module_data)

# # Example 2: Retrieve specific component data
# component_retriever = RetrieveCompData(
#     "~/my_app/data", 
#     "bipedArm", 
#     0, 
#     "L"
# )
# component_data = component_retriever.retrieve_data()

# # Access data through properties
# print(component_retriever.component_dict)
# print(component_retriever.rotation_dict)
# print(component_retriever.position_dict)


# INHERITENCE with Object-Orientated Programming. 
class Person: # Parent class
    def __init__(self, fname, lname):
        self.first_name = fname
        self.last_name = lname

    def print_name(self):
        print(self.first_name, self.last_name)


class Student(Person): # Child class, inherits properties of 'Person' class
    def __init__(self, fname, lname, year): # __init__() overrides the inheritence of the parent's __init__() func. 
        super().__init__(fname, lname) # 'super().' function makes the child class inherite all the methods & properties from its parent. 
        self.graduation_year = year
    
    def welcome(self):
        print(f"Welcome {self.first_name} {self.last_name} to the class of {self.graduation_year}!")
