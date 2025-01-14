import os

def find_directory(db_name, root_directory):
            for dirpath, dirnames, filenames in os.walk(root_directory):
                if db_name in filenames:
                    return dirpath
            raise FileNotFoundError(f"Database '{db_name}' not found starting from '{root_directory}'.")