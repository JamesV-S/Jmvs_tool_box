
import importlib
import sys
import os
from utils import utils_os

tool_box_controller = None
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
    # from utils import utils_os
    # importlib.reload(utils_os)
    folder_list = the_list
    for fld in folder_list:
        dr = os.path.join(utils_os.create_directory(*args, fld))
        append_list.append(dr)


def updating_paths():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    add_path = os.path.join(current_dir)
    add_to_sys_path(add_path)
    os.environ['MAYA_SCRIPT_PATH'] = current_dir + os.pathsep + os.environ.get('MAYA_SCRIPT_PATH', '')
    
    # ------------------ Add Necessary paths ----------------------
    custom_dir_list = []
    gather_folders_to_add_to_list(['char_ui', 'vehicle_ui', 'geoDB_ui', 'other_ui'], custom_dir_list, "Jmvs_tool_box", "user_interface")
    gather_folders_to_add_to_list(['databases', 'models', 'views', 'controllers'], custom_dir_list, "Jmvs_tool_box")
    gather_folders_to_add_to_list(['char_models', 'geoDB_models'], custom_dir_list, "Jmvs_tool_box", "models")
    
    # check if the custom dir exist:
    for directory in custom_dir_list:
        if does_directory_exist(directory):
            add_to_sys_path(directory)


def register_services():
    import service_locator_pattern 
    from main_entry_points.char_mep import char_master_main
    from main_entry_points.geoDB_mep import geoDB_master_main

    importlib.reload(service_locator_pattern)
    importlib.reload(char_master_main)

    from main_entry_points import tool_box_main
    importlib.reload(tool_box_main)

    tool_box_instance = tool_box_main.ToolBoxMain()
    service_locator_pattern.ServiceLocator.add_service('tool_box_main', tool_box_instance)

    char_master_instance = char_master_main.CharMasterMain() 
    service_locator_pattern.ServiceLocator.add_service('char_master_main', char_master_instance)

    geoDB_master_instance = geoDB_master_main.GeoDbMasterMain()
    service_locator_pattern.ServiceLocator.add_service('geoDB_master_main', geoDB_master_instance)
    print("Registered services:", service_locator_pattern.ServiceLocator._services)
    
    # show the tool_box ui!
    tool_box_controller = service_locator_pattern.ServiceLocator.get_service('tool_box_main')
    if tool_box_controller:
        print("Available services:", service_locator_pattern.ServiceLocator._services)
        tool_box_controller.show_ui()


def run_tool_box():
    updating_paths()
    register_services()
    
    
    
    

