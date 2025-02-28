
import importlib
import sys
import os

# construct the dir path for newfolders! 
#dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'systems')
#os.makedirs(dir_path, exist_ok=True)
#print(f"dir_path = {dir_path}")
#from systems import (
#    os_custom_directory_utils
#    )

# importlib.reload(os_custom_directory_utils)

current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"current_dir == {current_dir}")


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


def gather_folders_to_add_to_list(the_list, append_list, *args):
    from systems import os_custom_directory_utils
    importlib.reload(os_custom_directory_utils)
    folder_list = the_list
    for fld in folder_list:
        dr = os.path.join(os_custom_directory_utils.create_directory(*args, fld))
        append_list.append(dr)


def updating_paths():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    add_path = os.path.join(current_dir)
    add_to_sys_path(add_path)
    os.environ['MAYA_SCRIPT_PATH'] = current_dir + os.pathsep + os.environ.get('MAYA_SCRIPT_PATH', '')
    custom_dir_list = []
    

    # ------------------ Add Necessary paths ----------------------
    gather_folders_to_add_to_list(['char_ui', 'vehicle_ui', 'geoDB_ui', 'other_ui'], custom_dir_list, "Jmvs_tool_box", "user_interface")
    gather_folders_to_add_to_list(['databases', 'models', 'views', 'controllers'], custom_dir_list, "Jmvs_tool_box")
    gather_folders_to_add_to_list(['char_models', 'geoDB_models'], custom_dir_list, "Jmvs_tool_box", "models")

    # check if the custom dir exist:
    for directory in custom_dir_list:
        if does_directory_exist(directory):
            add_to_sys_path(directory)


def run_tool_box():
    updating_paths()
    
    import toolBox
    importlib.reload(toolBox)
    toolBox.tool_box_main()

    
    

