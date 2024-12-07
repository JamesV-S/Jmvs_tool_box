
# This creates the tables & inital data I want in the database
# how to delete the database when creating, if the module exists in the scene, 
# by looking for master_guide, then if a databse with the corelating name exists, 
import sqlite3

'''maybe make an empty database and if there is a duplicate of the  '''
def add_table(conn, unique_id): 
    sql_cr_table_state = [
       """CREATE TABLE IF NOT EXISTS details (
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
    if table == 'details':
        sql = f""" INSERT INTO {table} (unique_id, module_name, side) VALUES (?, ?, ?)"""
        cursor.execute(sql, values)
    elif table == 'user_settings':
        sql = f""" INSERT INTO {table} (unique_id, mirror_rig, stretch, 
        rig_options, rig_default, size) 
        VALUES (?, ?, ?, ?, ?, ?)"""
        cursor.execute(sql, values)
    
    
    conn.commit()


def cr_database(mdl_name, unique_id, side, user_setting_dict): # , 
    # DB_bipedArm
    # within that I want a table details & user_settings
    db_name = f'DB_{mdl_name}.db'
    try:
        with sqlite3.connect(db_name) as conn:
            # interasct with datsabase
            add_table(conn, unique_id)
            print(f"module {mdl_name}_{unique_id}{side} has connected to database {db_name}")
            print(f"{(unique_id, mdl_name)}")
            update_db(conn, "details", (unique_id, mdl_name, side)) # 'user_settings'
            # update_db(conn, "user_settings", (user_setting_dict['mirror_rig'], user_setting_dict['stretch'], user_setting_dict['rig_options'], user_setting_dict['rig_default'], user_setting_dict['size']))
    except sqlite3.Error as e:
        print(e)

u_s_dict = {'mirror_rig': False, 'stretch': False, 'rig_type': {'options': ['FK', 'IK', 'IKFK'], 'default': 'FK', 'size': 1}}, 
cr_database("bipedArm", 1, "_R", u_s_dict)
cr_database("bipedArm", 0, "_R", u_s_dict)
cr_database("bipedArm", 1, "_L", u_s_dict)
cr_database("bipedArm", 0, "_L", u_s_dict)
