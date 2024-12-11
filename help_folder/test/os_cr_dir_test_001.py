
import os
import sys



def create_directory(*args):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir) # jumps up a level like '..' by removing the last component of the path!
    
    
    dir_path = os.path.join(parent_dir, *args)
        
    # cr directory if it doesn't exist
    os.makedirs(dir_path, exist_ok=True)

    # check if the dir exists now
    if os.path.exists(dir_path):
        print(f"The directory '{dir_path}' exists")
    else:
        print(f"The directory '{dir_path}' does not exist")
    

def create_file(dir_path, file_name, content=''):
    # construct file path 
    file_path = os.path.join(dir_path, file_name)
    # cr & writ ethe file
    with open(file_path, 'w') as file:
        file.write(content)
    print(f"File '{file_path}' created.")
        

if __name__ == "__main__":
    create_directory("new_folder", "sub_folder")
    # create_file("new_folder", "sub_folder")