
''' I can store this file anywhere in my tool box & create folders & files anywhere I want '''
import os
import json


def string_dir_content():
    content = "Hello world"
    return content

'''
def json_dir_content():
    json_content = {
        "constant": {
            "space_swap": [
                ["world", "COG", "shoulder", "custom"],
                ["world", "wrist"],
                ["world", "clavicle"],
                ["world", "spine"]
            ]
        }
    }
    return json_content
'''

# Calculate how many directory levles to go up to reach the specific target 
# folder 'Jmvs_tool_box' (the git repo name in this example!)
def determine_levels_to_target(target_folder_name):
    current_dir = os.path.dirname(os.path.abspath(__file__)) # > removes file name
    parts = current_dir.split(os.sep) # > splits directory path into a list of its `sep`erated components
    try:
        # get index[#] of target folder name in the split parts list
        target_index = parts.index(target_folder_name)
        # work out the levels to go up
        levels = len(parts) -target_index -1
        '''
        len(parts) = total number of components in the current path, each 
        component represents a directory level.
        
        target_index = with the index, it tells me how many levels deep the 
        target folder is from the root!
        
        `len(parts) - target_index` = calculate how many levels are between the 
        target folder and the end of the current path
        
        `-1` = this is to exclude the levelof the target folder itself. 
        So that it's counting how many levels to move up from the current 
        directory to just above the target folder
        '''
        print(f"Number of levels to go up: {levels}")
    except ValueError:
        raise ValueError(f"Target folder '{target_folder_name}' not found in path.")
    return levels


def go_up_path_levels(path, levels):
    for _ in range(levels):
        path = os.path.dirname(path) # removes the last component of the path
    return path


def create_directory(dir_location, *args):
    current_dir = os.path.dirname(os.path.abspath(__file__))
      
    # move up levels
    levels = determine_levels_to_target(dir_location)
    target_dir = go_up_path_levels(current_dir, levels)

    # construct the dir path for newfolders! 
    dir_path = os.path.join(target_dir, *args)
        
    # cr directory if it doesn't exist
    os.makedirs(dir_path, exist_ok=True)

    # check if the dir exists now
    if os.path.exists(dir_path):
        print(f"The directory '{dir_path}' exists")
    else:
        print(f"The directory '{dir_path}' does not exist")

    return dir_path
    
''''''
def create_file(dir_path, file_name, content=''):
    # construct file path 
    file_path = os.path.join(dir_path, file_name)

    # If content is a dict it usually means it's a json so convert it to one!
    if isinstance(content, dict):
        content = json.dumps(content, indent=4)
     
    # cr & writ ethe file
    with open(file_path, 'w') as file:
        file.write(content)
    print(f"File '{file_path}' created.")
''''''     

def get_specific_path_from_dir(dir_path, target_folder_name): # 'c:\Docs\maya\scripts\Jmvs_tool_box\new_folder_004\sub_folder_004\json_file.json', target = "new_folder_004"
    # not removed the file name of the `dir_path`
    parts = dir_path.split(os.sep)
    try:
        # get index[#] of target folder name in the split parts list
        target_index = parts.index(target_folder_name) # = 5
        # reconstruct the path up to the target folder!
        target_path = os.sep.join(parts[:target_index + 1]) 
    except ValueError:
        raise ValueError(f"Target folder '{target_folder_name}' not found in path.")
    return target_path


if __name__ == "__main__":
    # to create a simple txt file
    dir_path = create_directory("Jmvs_tool_box", "top_folder_003", "subfolder_003") # (dir_location, *args)
    
    file_content = string_dir_content()
    create_file(dir_path, "Created_text_file.txt", file_content) # automatically places the new file in the last folder!
    '''
    # to create a simple .py file
    # >> need to figure out how to convert to a string and put it in a predefined variable 
    # create_file(dir_path, "python_file.py", file_content)
    
    # get specific folder from dir_path & get the json content
    specific_abstracted_dir_path = get_specific_path_from_dir(dir_path, "top_folder_003")
    json_file_content = json_dir_content()
    create_file(specific_abstracted_dir_path, "Created_json_file.json", json_file_content)
    '''