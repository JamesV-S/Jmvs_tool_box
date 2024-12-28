
import importlib
import sys
import os
print("Is it UPDATING???")

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


def updating_paths():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    add_path = os.path.join(current_dir)
    add_to_sys_path(add_path)
    os.environ['MAYA_SCRIPT_PATH'] = current_dir + os.pathsep + os.environ.get('MAYA_SCRIPT_PATH', '')
    custom_dir_list = []
    
    # ----------------------------------------
    # custom directory's I need adding to path
    db_dir = os.path.join(os.path.dirname(os.path.normpath(__file__)), 
                               'databases')
    custom_dir_list.append(db_dir)
    
    # these dir share same path, so it's quicker to do this
    ui_list = ['char_ui', 'vehicle_ui', 'geoDB_ui', 'other_ui']
    for folder in ui_list:
        ui_dir = os.path.join(os.path.dirname(os.path.normpath(__file__)), 
                                'user_interface', folder)
        custom_dir_list.append(ui_dir)
    
    # check if the custom dir exist:
    for directory in custom_dir_list:
        if does_directory_exist(directory):
            add_to_sys_path(directory)


def run_tool_box():
    updating_paths()
    
    import toolBox
    importlib.reload(toolBox)
    toolBox.tool_box_main()

    
    

