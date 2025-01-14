
import sqlite3
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

# store the dict in a database!

class CreateDatabase():
    def __init__(self, name, directory):
        db_directory = os.path.expanduser(directory)
        os.makedirs(db_directory, exist_ok=1)
        # db_name must include the entire path too!
        db_name = os.path.join(db_directory, f'DB_{name}.db') # f'DB_{name}.db'
        print(f"db_name = `{db_name}`")
        
        try:
            with sqlite3.connect(db_name) as conn:
                # interasct with datsabase
                print(f"Connection to database {db_name} opened successfully")
                self.add_table(conn)
                print(f"name `{name}` has connected to database {db_name}")
        except sqlite3.Error as e:
            print(f"Create GEO Database error: {e}")
        finally:
            print(f"Connection to database {db_name} closed")
    ''' 
    """CREATE TABLE IF NOT EXISTS db_name (
        db_row_id INTEGER PRIMARY KEY,
        name text NOT NULL
    );""", 
    '''
    def add_table(self, conn): 
        sql_cr_table_state = [
        """CREATE TABLE IF NOT EXISTS uuid_data (
            db_row_id INTEGER PRIMARY KEY,
            joint_name TEXT,
            joint_uuid TEXT,
            geo_name TEXT,
            geo_uuid TEXT
        );"""
        ]
        cursor = conn.cursor()
        for state in sql_cr_table_state:
            cursor.execute(state)
        conn.commit()

#CreateDatabase("geo_TEST_002")

#------------------------------------------------------------------------------

oneJNT_for_multiGEO_uuid_combined_dict = {
    'joint_UUID_dict': {'jnt_skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134'}, 
    'geometry_UUID_dict': {'geo_1': '946C0344-4B43-4E3E-E610-33AEFC6A76D2', 
          'geo_2': 'BC1BBC88-49E0-705C-3B5E-89B24C670722', 
          'geo_3': '2AD65DAA-4F33-E185-634E-B7A81D073E31'}
    }

multiJNT_for_oneGEO_uuid_combined_dict = {
    'joint_UUID_dict': {
        'skn_0_shoulder_L': '0ADBD31D-4A68-348A-FB5C-A5806EA2ED1F', 
        'skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134', 
        'skn_0_wrist_L': 'F0E55702-46CF-4131-30FB-BDBC0E16AAC9'
    }, 
    'geometry_UUID_dict': {'geo_4': 'BB3DD158-422F-3966-C861-7C8E8FA7F144'}
    }

oneJNT_for_oneGEO_uuid_combined_dict = {
    'joint_UUID_dict': {
        'skn_0_shoulder_L': '0ADBD31D-4A68-348A-FB5C-A5806EA2ED1F', 
        'skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134', 
        'skn_0_wrist_L': 'F0E55702-46CF-4131-30FB-BDBC0E16AAC9'
        }, 
    'geometry_UUID_dict': {
        'skn_geo_upperarm': 'A77BA8E3-4DBC-2121-CFEA-88AD3F446242', 
        'skn_geo_lowerarm': '0AF4964F-40AC-FAB7-A329-C28F43B224EA', 
        'skn_geo_hand': 'EB05CC29-40CB-1503-0C9C-629BE45E5CF8'
        }
    }

class UpdateDatabase():
    def __init__(self, database_name, db_uuid_dict, directory):
        db_directory = os.path.expanduser(directory)
        os.makedirs(db_directory, exist_ok=1)
        # db_name must include the entire path too!
        db_name = os.path.join(db_directory, database_name) # f'DB_{name}.db'
        
        # get lists from the neseted dict
        jnt_uuid_dict = db_uuid_dict['joint_UUID_dict']
        geo_uuid_dict = db_uuid_dict['geometry_UUID_dict']

        # need to handle different types of nested dictionary's!
        # So cr lists of names and uuid's
        jnt_name_list = list(jnt_uuid_dict.keys())
        jnt_uuid_list = list(jnt_uuid_dict.values())

        geo_name_list = list(geo_uuid_dict.keys())
        geo_uuid_list = list(geo_uuid_dict.values())

        # prepare the values to put inot db
        jnt_names = ', '.join(jnt_name_list)
        jnt_uuids = ', '.join(jnt_uuid_list)
        geo_names = ', '.join(geo_name_list)
        geo_uuids = ', '.join(geo_uuid_list)

        try:
            with sqlite3.connect(db_name) as conn:
                #for (jnt_name, jnt_uuid), (geo_name, geo_uuid) in zip(jnt_uuid_list, geo_uuid_list):
                self.update_db(conn, 'uuid_data', (jnt_names, jnt_uuids, 
                                geo_names, geo_uuids))
    
                print(f"data has been scuccesfully inserted into `{db_name}`")
        except sqlite3.Error as e:
            print(e)
        

    def update_db(self, conn, table, values):
        cursor = conn.cursor()
        if table == 'uuid_data':
            sql = f""" INSERT INTO {table} (joint_name, joint_uuid, geo_name, geo_uuid) VALUES (?, ?, ?, ?)"""
            cursor.execute(sql, values)
        conn.commit()


class UpdateJointDatabase():
    def __init__(self, database_name, jnt_uuid_dict, directory):
        db_directory = os.path.expanduser(directory)
        os.makedirs(db_directory, exist_ok=1)
        # db_name must include the entire path too!
        db_name = os.path.join(db_directory, database_name) # f'DB_{name}.db'

        # need to handle different types of nested dictionary's!
        # So cr lists of names and uuid's
        jnt_name_list = list(jnt_uuid_dict.keys())
        jnt_uuid_list = list(jnt_uuid_dict.values())

        # prepare the values to put inot db
        jnt_names = ', '.join(jnt_name_list)
        jnt_uuids = ', '.join(jnt_uuid_list)

        print(f"jnt_names = {jnt_names} & jnt_uuids = {jnt_uuids}")

        try:
            with sqlite3.connect(db_name) as conn:
                for jnt_name, jnt_uuid in zip(jnt_name_list, jnt_uuid_list):
                    self.update_db(conn, 'uuid_data', (jnt_names, jnt_uuids))
    
                print(f"data has been scuccesfully inserted into `{db_name}`")
        except sqlite3.Error as e:
            print(f"Update Joint Database error is: {e}")
        

    def update_db(self, conn, table, values):
        cursor = conn.cursor()
        if table == 'uuid_data':
            sql = """INSERT INTO uuid_data (joint_name, joint_uuid, geo_name, geo_uuid) VALUES (?, ?, NULL, NULL)"""
            cursor.execute(sql, values)
        conn.commit()


class UpdateGeoDatabase():
    def __init__(self, database_name, geo_uuid_dict, directory):
        db_directory = os.path.expanduser(directory)
        os.makedirs(db_directory, exist_ok=1)
        # db_name must include the entire path too!
        db_name = os.path.join(db_directory, database_name) # f'DB_{name}.db'

        # need to handle different types of nested dictionary's!
        # So cr lists of names and uuid's
        geo_name_list = list(geo_uuid_dict.keys())
        geo_uuid_list = list(geo_uuid_dict.values())

        # prepare the values to put inot db
        geo_names = ', '.join(geo_name_list)
        geo_uuids = ', '.join(geo_uuid_list)

        try:
            with sqlite3.connect(db_name) as conn:
                #for (jnt_name, jnt_uuid), (geo_name, geo_uuid) in zip(jnt_uuid_list, geo_uuid_list):
                self.update_db(conn, 'uuid_data', (geo_names, geo_uuids))
                print(f"data has been scuccesfully inserted into `{db_name}`")
        except sqlite3.Error as e:
            print(f"Update Geometry Database error is: {e}")
        

    def update_db(self, conn, table, values):
        cursor = conn.cursor()
        if table == 'uuid_data':
            sql = """INSERT INTO uuid_data (joint_name, joint_uuid, geo_name, geo_uuid) VALUES (NULL, NULL, ?, ?)"""
            cursor.execute(sql, values)
        conn.commit()

#------------------------------------------------------------------------------
# from a specific relationship 
class Retrieve_UUID_Database_from_row():
    def __init__(self, database_name, row_id, directory ):
        db_directory = os.path.expanduser(directory)
        os.makedirs(db_directory, exist_ok=1)
        # db_name must include the entire path too!
        db_name = os.path.join(db_directory, database_name) # f'DB_{name}.db'

        db_name = database_name # database_name
        try:
            with sqlite3.connect(db_name) as conn:
                # interasct with datsabase
                combined_dict = self.get_dict_from_db_row(conn, 'uuid_data', row_id)
                print(f"retrieved `{combined_dict}` in row `{row_id}` from db: `{db_name}`")
                
        except sqlite3.Error as e:
            print(e)

    def get_dict_from_db_row(self, conn, table, row_id):
        cursor = conn.cursor()
        # dictated by a specified row! aka this is the row/skinn relationship
        query_param_state = f'SELECT joint_name, joint_uuid, geo_name, geo_uuid FROM {table} WHERE db_row_id=?'
        try:
            cursor.execute(query_param_state, (row_id,))
            row = cursor.fetchone()
            print(f"row = {row}")
            if row:
                print(f"querying (id row '{row}'): {row}")
                # in the db the values and keys r separated by ', '
                jnt_names, jnt_uuids = row[0].split(', '), row[1].split(', ')
                geo_names, geo_uuids = row[2].split(', '), row[3].split(', ')
                
                # then zip these values into 2 dictionary's
                jnt_uuid_dict = {name: uuid for name, uuid in zip(jnt_names, jnt_uuids)}
                geo_uuid_dict = {name: uuid for name, uuid in zip(geo_names, geo_uuids)}
                
                # add both dictionary's to a combined one!
                uuid_combined_dict = {
                    'joint_UUID_dict':jnt_uuid_dict,
                    'geometry_UUID_dict':geo_uuid_dict
                }
                print(f"uuid_combined_dict: {uuid_combined_dict}")
            return uuid_combined_dict
        except sqlite3.Error as e:
            print(f"sqlite3.Error: {e}")
        return None
    


class RetrieveAllUUIDs():
    def __init__(self, database_name, directory):
        db_directory = os.path.expanduser(directory)
        os.makedirs(db_directory, exist_ok=1)
        # db_name must include the entire path too!
        db_name = os.path.join(db_directory, database_name) # f'DB_{name}.db'
        print(f"Retrieving UUID dict from db// db_naem: {db_name}")
        try:
            with sqlite3.connect(db_name) as conn:
                # interasct with datsabase
                self.combined_dict = self.get_ALL_dict_from_db(conn, 'uuid_data')
                print(f"retrieved `{self.combined_dict}` in row ALL rows from: `{db_name}`")
                
        except sqlite3.Error as e:
            print(f"Retrieving UUID dict from db// ERROR: {e}")

    def get_ALL_dict_from_db(self, conn, table):
        cursor = conn.cursor()
        query_param_state = f'SELECT db_row_id, joint_name, joint_uuid, geo_name, geo_uuid FROM {table}'
        all_dicts = {}
        try:
            for row in cursor.execute(query_param_state):
                row_id, jnt_names, jnt_uuids, geo_names, geo_uuids = row
                jnt_uuid_dict = {name: uuid for name, uuid in zip(jnt_names.split(', '), jnt_uuids.split(', '))}
                geo_uuid_dict = {name: uuid for name, uuid in zip(geo_names.split(', '), geo_uuids.split(', '))}
                
                # make the row id the key for each nested dict!
                all_dicts[row_id] = {
                    'joint_UUID_dict':jnt_uuid_dict,
                    'geometry_UUID_dict':geo_uuid_dict
                }
        except sqlite3.Error as e:
            print(f"sqlite3.Error: {e}")
        return all_dicts
    
    def get_combined_dict(self):
        return self.combined_dict
    

# Output: 
# {1: {'joint_UUID_dict': {'jnt_skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134'}, 'geometry_UUID_dict': {'geo_1': '946C0344-4B43-4E3E-E610-33AEFC6A76D2', 'geo_2': 'BC1BBC88-49E0-705C-3B5E-89B24C670722', 'geo_3': '2AD65DAA-4F33-E185-634E-B7A81D073E31'}}, 2: {'joint_UUID_dict': {'skn_0_shoulder_L': '0ADBD31D-4A68-348A-FB5C-A5806EA2ED1F', 'skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134', 'skn_0_wrist_L': 'F0E55702-46CF-4131-30FB-BDBC0E16AAC9'}, 'geometry_UUID_dict': {'geo_4': 'BB3DD158-422F-3966-C861-7C8E8FA7F144'}}, 3: {'joint_UUID_dict': {'skn_0_shoulder_L': '0ADBD31D-4A68-348A-FB5C-A5806EA2ED1F', 'skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134', 'skn_0_wrist_L': 'F0E55702-46CF-4131-30FB-BDBC0E16AAC9'}, 'geometry_UUID_dict': {'skn_geo_upperarm': 'A77BA8E3-4DBC-2121-CFEA-88AD3F446242', 'skn_geo_lowerarm': '0AF4964F-40AC-FAB7-A329-C28F43B224EA', 'skn_geo_hand': 'EB05CC29-40CB-1503-0C9C-629BE45E5CF8'}}}

''' THIS IS WORKING VERY NICELY!
{
1: {
'joint_UUID_dict': 
    {'jnt_skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134'}, 
'geometry_UUID_dict': 
    {'geo_1': '946C0344-4B43-4E3E-E610-33AEFC6A76D2', 
    'geo_2': 'BC1BBC88-49E0-705C-3B5E-89B24C670722', 
    'geo_3': '2AD65DAA-4F33-E185-634E-B7A81D073E31'
    }
},
2: {
'joint_UUID_dict': 
    {'skn_0_shoulder_L': '0ADBD31D-4A68-348A-FB5C-A5806EA2ED1F', 
    'skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134', 
    'skn_0_wrist_L': 'F0E55702-46CF-4131-30FB-BDBC0E16AAC9'}, 
'geometry_UUID_dict': 
    {'geo_4': 'BB3DD158-422F-3966-C861-7C8E8FA7F144'}
}, 
3: {
'joint_UUID_dict': 
    {'skn_0_shoulder_L': '0ADBD31D-4A68-348A-FB5C-A5806EA2ED1F', 
    'skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134', 
    'skn_0_wrist_L': 'F0E55702-46CF-4131-30FB-BDBC0E16AAC9'}, 
'geometry_UUID_dict': 
    {'skn_geo_upperarm': 'A77BA8E3-4DBC-2121-CFEA-88AD3F446242', 
    'skn_geo_lowerarm': '0AF4964F-40AC-FAB7-A329-C28F43B224EA', 
    'skn_geo_hand': 'EB05CC29-40CB-1503-0C9C-629BE45E5CF8'}
}
}`

UpdateDatabase(f'DB_geo_arm.db', oneJNT_for_multiGEO_uuid_combined_dict)
UpdateDatabase(f'DB_geo_arm.db', multiJNT_for_oneGEO_uuid_combined_dict)
UpdateDatabase(f'DB_geo_arm.db', oneJNT_for_oneGEO_uuid_combined_dict)
'''