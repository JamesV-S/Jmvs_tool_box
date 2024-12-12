
import importlib
import sys
import os

import toolBox
importlib.reload(toolBox)


def does_directory_exist(directory):
    if os.path.exists(directory):
        print(f"Directory '{directory}' exists")
        return True
    else:
        print(f"Directory '{directory}' does NOT exist")
        return False


def add_to_sys_path(directory):
    if directory not in sys.path:
        sys.path.append(directory)
        print(f"Added '{directory} to sys.path")
    else:
        print(f"'{directory}' is already in sys.path")


def updating_paths():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    add_path = os.path.join(current_dir)
    add_to_sys_path(add_path)
    os.environ['MAYA_SCRIPT_PATH'] = current_dir + os.pathsep + os.environ.get('MAYA_SCRIPT_PATH', '')

    # custom directory's I need adding to path
    char_db_dir = os.path.join(os.path.dirname(os.path.normpath(__file__)), 
                               'databases')
    char_ui_dir = os.path.join(os.path.dirname(os.path.normpath(__file__)), 
                               'user_interface', 'char_ui')

    # check if the custom dir exist: 
    if does_directory_exist(char_db_dir):
        add_to_sys_path(char_db_dir)
    
    if does_directory_exist(char_ui_dir):
        add_to_sys_path(char_ui_dir)


def run_tool_box():
    updating_paths()
    toolBox.tl_bx_main()
    print("run toolBox")
    

