# This  

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