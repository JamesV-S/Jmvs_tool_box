
# This is for the database operations like (create, read, update, delete)
import sqlite3

def query_all_rows(conn, table, *args):
    cursor = conn.cursor()
    try:
        # check if the args r strings, integers will fuck up the statement. 
        if not all(isinstance(arg, str) for arg in args):
            ValueError("All column names need to be string!!")

        # to cr a comma-seperated string for the sql query 
        collumns = ', '.join(args) if args else '*'
        sql = f'SELECT {collumns} FROM {table}'
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            print(f"querying all rows, returning a tuple: {row}")
            # use row[2] to print all row's `arg3` & no longer in a tuple!
        return rows
    except sqlite3.Error as e:
        print(e)


def query_row_from_item(conn, table, item):
    cursor = conn.cursor()
    try:
        # to cr a comma-seperated string for the sql query 
        sql = f'SELECT * FROM {table}'
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            print(f"querying all rows, returning a tuple: {row}")
            # use row[2] to print all row's `arg3` & no longer in a tuple!
        return rows
    except sqlite3.Error as e:
        print(e)


def query_number_of_rows(conn, table, *args):
    cursor = conn.cursor()
    try:
        # check if the args r strings, integers will fuck up the statement. 
        if not all(isinstance(arg, str) for arg in args):
            ValueError("All column names need to be string!!")

        # to cr a comma-seperated string for the sql query 
        collumns = ', '.join(args) if args else '*'
        sql = f'SELECT {collumns} FROM {table}'
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            print(f"querying all rows, returning a tuple: {row}")
            # use row[2] to print all row's `arg3` & no longer in a tuple!
        return rows
    except sqlite3.Error as e:
        print(e)

def modify_schema(db_name):
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            
            # Step 1: Create the new table with modified schema
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS uuid_data_new (
                    db_row_id INTEGER PRIMARY KEY,
                    joint_name TEXT,
                    joint_uuid TEXT,
                    geo_name TEXT,
                    geo_uuid TEXT
                )
            """)

            # Step 2: Copy data from old table to new table
            cursor.execute("""
                INSERT INTO uuid_data_new (db_row_id, joint_name, joint_uuid, geo_name, geo_uuid)
                SELECT db_row_id, joint_name, joint_uuid, geo_name, geo_uuid FROM uuid_data
            """)

            # Step 3: Drop the old table
            cursor.execute("DROP TABLE uuid_data")

            # Step 4: Rename the new table to the original name
            cursor.execute("ALTER TABLE uuid_data_new RENAME TO uuid_data")

            print("Schema modified successfully: jnt/geo_name and jnt/geo_uuid now allow NULL values.")
    except sqlite3.Error as e:
        print(f"Error modifying schema: {e}")

# Example usage

#  C:\Docs\maya\scripts\Jmvs_tool_box\databases\char_databases\db_rig_storage\DB_jmvs_cartoonMale_rig\DB_bipedArm
#modify_schema(db_name)

def delete_row_by_id(db_name, row_id):
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            
            # Step 1: Delete the row with the specified db_row_id
            cursor.execute("DELETE FROM uuid_data WHERE db_id = ?", (row_id,))
            
            # Step 2: Commit the changes
            conn.commit()

            if cursor.rowcount > 0:
                print(f"Row with db_id {row_id} deleted successfully.")
            else:
                print(f"No row found with db_row_id {row_id}.")
    except sqlite3.Error as e:
        print(f"Error deleting row: {e}")

# Example usage
#db_name = r'C:\Docs\maya\scripts\Jmvs_tool_box\databases\geo_databases\DB_DB_geo_arm.db'
row_id_to_delete = 3  # Replace with the actual db_row_id you want to delete
#for x in range(1):
#    delete_row_by_id(db_name, x)
# delete_row_by_id(db_name, 3)
'''
# from database, where 'db_row_id' == 4, update it to '2'
table = 'uuid_data'
update_statement = f'UPDATE {table} SET db_row_id = ?, WHERE db_row_id = ?'
db_name = 'C:\Docs\maya\scripts\Jmvs_tool_box\databases\geo_databases\grp_MECH_db\DB_Mech_Torso.db'
# C:\Docs\maya\scripts\Jmvs_tool_box\databases\geo_databases\grp_MECH_db
def update_specififc_same_data(conn, sql, collumn_name, arg1, ID):
    cursor = conn.cursor()
    try:
        # execute the UPDATE statement with the priority and id.
        cursor.execute(f"SELECT * FROM {table} WHERE {collumn_name} = ?", (ID,))
        if cursor.fetchone() is None:
            print(f"No task found with id: `{ID}`.")
            return
        
        # Execute the UPDATE statement
        cursor.execute(sql, (arg1, ID))
        conn.commit()
        if cursor.rowcount == 0:
            print(f"No '{table}' table found with id `{ID}`.")
        else:
            print(f"'{table}' table found with id `{ID}`.")

        # verify the update on a specific row: 
        cursor.execute(f'SELECT {collumn_name}, FROM tasks WHERE {collumn_name} = ?', (ID,))
        row = cursor.fetchone() # Gets all rows from the result of the query
        if row: 
            print("Verifying the update:")
            print(row)
        else:
            print(f"No '{table}' table found with id `{ID}`.")

    except sqlite3.Error as e:
        print(f"An error occured in the UPDATE statement: {e}")

def same_name_main():
    try:
        with sqlite3.connect(db_name) as conn:
            update_specififc_same_data(conn, update_statement, collumn_name, arg1, ID)

    except sqlite3.Error as e:
        print(e)
'''

