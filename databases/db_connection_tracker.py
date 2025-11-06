
from contextlib import contextmanager 
import sqlite3
import os
import gc

class DBConnectionTracker():
    # class dict variable to share across all instances
    _active_connections = {}

    @classmethod
    @contextmanager
    def get_connection(cls, db_path):
        '''
        # Description:
            Tracks and properly closes connections
        # Attributes:
            cls (class method): Not an instance; is the class itself, like 'self' but for class
            methods to give access to class-level variables (_active_connections). 
            db_path (directory string): the path of the database.
        # Returns: N/A
        '''
        conn = None
        try:
            # crete new connetion
            conn = sqlite3.connect(db_path)

            # track the conn in the global variable
            cls._active_connections[db_path] = conn

            # yeild means returniong a list of items one at a time, 
            # so the caller can use it in a for loop.
            yield conn

            # if no exceptions, commit the changes.
            conn.commit

        except sqlite3.Error as e:
            # this makes all chnaged reversed, data remains consitant to what it was.
            if conn:
                conn.rollback()
            raise e
        
        finally:
            # ALWAYS close and claun up even if an error ocurs.
            if conn:
                # close the connection
                conn.close()

                if db_path in cls._active_connections:
                    del cls._active_connections[db_path]

            # force garbage collection
            gc.collect()


    @classmethod
    def force_close_all(cls):
        '''
        # Description:
            Force close all connections, call this before file operations in the 
            gui funciton not the db classes files!
        # Attributes:
            cls (class method): Not an instance; is the class itself, like 'self' but for class
            methods to give access to class-level variables (_active_connections). 
        # Returns: N/A
        '''
        # iterate through alll tracked connections
        for db_path, conn in list(cls._active_connections.items()):
            try:
                # close each connection
                conn.close()
            except:
                # even if closing fails, continue setup
                pass

            del cls._active_connections[db_path]

        # force gartbage collection.
        gc.collect()
        print("All databases connections forced closed.")


class DeleteDB:
    def __init__(self):
        self.delete_database_callback()
    
    def delete_database_callback(self):
        """This is called when user clicks 'Delete Database' button"""
        # 1. Force close all connections first
        # db_connection_tracker.DBConnectionTracker.force_close_all()
        DBConnectionTracker.force_close_all()
        
        # 2. Now safely delete the file
        db_path = "C:/Docs/maya/scripts/Jmvs_tool_box/databases/char_databases/db_rig_storage/DB_jmvs_modules_rig/DB_bipedArm.db"
        #"C:\Docs\maya\scripts\Jmvs_tool_box\databases\char_databases\db_rig_storage\DB_jmvs_modules_rig"
        try:
            os.unlink(db_path)
            print("Database deleted successfully")
        except Exception as e:
            print(f"Delete failed: {e}")

# DeleteDB()