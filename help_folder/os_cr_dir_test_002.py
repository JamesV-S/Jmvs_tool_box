
import os

def hello_world_content():
    statement = "Hello world"
    return statement


def go_up_path_levels(path, levels):
    for _ in range(levels):
        path = os.path.dirname(path) # removes the last component of the path
    return path


def create_directory(*args):
    current_dir = os.path.dirname(os.path.abspath(__file__))
      
    # move up levels
    target_dir = go_up_path_levels(current_dir, 2)

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
    

def create_file(dir_path, file_name, content=''):
    # construct file path 
    file_path = os.path.join(dir_path, file_name)
    # cr & writ ethe file
    with open(file_path, 'w') as file:
        file.write(content)
    print(f"File '{file_path}' created.")
        

if __name__ == "__main__":
    dir_path = create_directory("new_folder_002", "sub_folder_002")
    file_content = hello_world_content()
    create_file(dir_path, "example_file.txt", file_content)