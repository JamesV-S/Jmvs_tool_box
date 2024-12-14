
# This creates the tables & inital data I want in the database
# how to delete the database when creating, if the module exists in the scene, 
# by looking for master_guide, then if a database with the corelating name exists. prob make folders to save presets!
import sqlite3
import importlib
import sys
import os


''''''
# for running in VSCODE!

def determine_levels_to_target(current_dir, target_folder_name):
    #parts = current_dir.split(os.sep) 
    try:
        target_index = current_dir.split(os.sep).index(target_folder_name)
        levels = len(current_dir.split(os.sep) ) -target_index -1
        print(f"Number of levels to go up: {levels}")
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
''''''

from databases import database_manager
importlib.reload(database_manager)


def add_table(conn): 
    sql_cr_table_state = [
       """CREATE TABLE IF NOT EXISTS modules (
           db_id INTEGER PRIMARY KEY,
           unique_id INT,
           module_name text NOT NULL,
           side text NOT NULL
       );""",
       """CREATE TABLE IF NOT EXISTS user_settings (
           db_id INTEGER PRIMARY KEY,
           unique_id INT,
           mirror_rig FLOAT,
           stretch FLOAT,
           rig_options TEXT,
           rig_default TEXT, 
           size INT
       );"""
    ]
    cursor = conn.cursor()
    for state in sql_cr_table_state:
        cursor.execute(state)
    conn.commit()


def update_db(conn, table, values):
    cursor = conn.cursor()
    if table == 'modules':
        sql = f""" INSERT INTO {table} (unique_id, module_name, side) VALUES (?, ?, ?)"""
        cursor.execute(sql, values)
    elif table == 'user_settings':
        sql = f""" INSERT INTO {table} (unique_id, mirror_rig, stretch, 
               rig_options, rig_default, size) VALUES (?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql, values)
    conn.commit()


def get_unique_id(conn, table):
    cursor = conn.cursor()
    cursor.execute(f"SELECT MAX(unique_id) FROM {table}")
    max_id = cursor.fetchone()[0]
    return (max_id + 1) if max_id is not None else 1


def cr_database(mdl_name, side, user_setting_dict): # , 
    # DB_bipedArm
    # within that I want a table modules & user_settings
    db_name = f'DB_{mdl_name}.db'
    try:
        with sqlite3.connect(db_name) as conn:
            # interasct with datsabase
            add_table(conn)
            print(f"module {mdl_name}{side} has connected to database {db_name}")
            
            global unique_id
            unique_id = get_unique_id(conn, 'modules')
            rig_options = ', '.join(user_setting_dict['rig_type']['options'])
            #-----
            # check whether the module's columns already exists, if so dont create the row!
            rows = database_manager.query_all_rows(conn, 'modules', 'unique_id', 'module_name', 'side')
            # checking whethr the values from the module exist: 
            exists = any(row == (unique_id, mdl_name, side) for row in rows)
            if not exists: 
                print("no dullicates")
                update_db(conn, "modules", (unique_id, mdl_name, side))
                update_db(conn, "user_settings", (unique_id, u_s_dict['mirror_rig'], u_s_dict['stretch'], rig_options, u_s_dict['rig_type']['default'], u_s_dict['size']))
            else:    
                print(f'Duplicate exists: {unique_id, mdl_name, side}, not adding it!')
            #-----          
    except sqlite3.Error as e:
        print(e)


def return_unique_id():
    return unique_id


u_s_dict = {'mirror_rig': False, 'stretch': False, 'rig_type': {'options': ['FK', 'IK', 'IKFK'], 'default': 'FK'}, 'size': 1} 
cr_database("bipedArm", "_R", u_s_dict) # NEED unique_id == 1
cr_database("bipedArm", "_L", u_s_dict) # NEED unique_id == 1
cr_database("bipedArm", "_R", u_s_dict) # NEED unique_id == 2
cr_database("bipedArm", "_L", u_s_dict) # NEED unique_id == 2
print(u_s_dict['mirror_rig'], u_s_dict['stretch'], u_s_dict['rig_type']['options'], u_s_dict['rig_type']['default'], u_s_dict['size'])
            