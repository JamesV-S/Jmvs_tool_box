
import os
''' os MODULE functions'''
# Instead of using `path.dirname` to extraxt the directory of a given path
# >> Use `os.path.normpath` to ensure a consistent path format, 
# making paths cleaner and more predictable.
os.path.normpath('C:/path/to/file.txt') 
    # Returns `C:\\path\\to\\file.txt`
'''
`os.path.normpath` is used to normalize a path, collapsing redundant separators 
and up-level references, but it doesn't change the directory level of a path. 
It only cleans up the path syntax.

Example: os.path.normpath('a/b/../c') results in 'a/c', but it doesn't navigate directories like `os.path.dirname`.

** USE `os.path.dirname` TO NAVIGATE DIRECTORIES!!!! ** 
'''

# U know what `os.path.joint()` does: 
os.path.join('folder', 'another_folder', 'file.txt') 
    # returns 'folder\\another_folder\\file.txt'

# `os.path.exists()` checks if a given path exists (file or directory)
if os.path.exists('path/to//check'):
    print('path exists')
else:
    print('Path does not exist')

# `os.makedirs()` CREATES a directory recursively! If the intermediate 
# directories don't exist, it creates them. 
os.makedirs('new_folder/subfolder', exist_ok=True)
    # Creates 'new_folder' & 'new_folder/subfolder' if they don't exist

    # `exist_ok` option prevents an error if the directory already exists. 
    # Without `exist_ok=True` and the directory already exists, an error (FileExistsError) is raised.
    # With `exist_ok=True` the function will not raise an error if the directory exists, it'll do nothing

    # Example use: 
os.makedirs('Parent_folder/subfolder', exist_ok=True)
    # cr the directories, won't raise an error if they exist.
if os.path.exists('Parent_folder/subfolder'):
    print('The directory exists')
else:
    print('The directory does not exist')
    # Checks if the directory exists, a good way to handle any unforseen issues. 
''' ^ A possible way to save out files from a tool! ^ '''

# `os.sep` > splits directory path into a list of its `sep`erated components
dir_path = "this\\is\\a\\path"
parts = dir_path.split(os.sep)
    # parts = ["this", "is", "a", "path"]
# -----------------------------------------------------------------------------
import sys
''' sys MODULE functions'''

# U already know `sys.path`, a list of strings that specifies the search for modules. 
# Append paths
sys.path.append('/path/to/additional/modules')

# `sys.argv` is a list containing command-line arguments passed to a script. 
    #  `sys.argv[0]` is the script name & the rest are arguments.
print(sys.argv)
    # if running `python script.py arg1 arg2`, it prints: ['script.py', 'arg1', 'arg2']
''' 
`sys.argv[0]` = 'script.py'
`sys.argv[1]` = 'arg1'
`sys.argv[2]` = 'arg2'
'''
    # `sys.argv` usage:
def greet():
    if len(sys.argv) < 2:
        print("Usage: python greet.py [name]")
        sys.exit(1)

    name = sys.argv[1]
    print(f"Hello, {name}!")

if __name__ == "__main__":
    greet()


# `sys.exit` exits/terminates a python script & returns with a specific status code. A non-zero status code indicates an error!
# Complete example: 
def read_file(file_path):
    # Check if the file exists before reading it!. If not it prints an error message and exits with a status of 1
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist." )
        sys.exit(1) # Exits the program with a status code of 1

    # Read & print file, if the file exists, it reads and prints the content. 
    with open(file_path, 'r') as file:
        content = file.read()
        print(content)
    '''
    Anatomy of readign a file: 
    `with` statement ensures the file is properly closed after its suite finishes, even if an exception is raised. 
    `open(file_pathm, 'r')` opens the file @ 'file_path' in read mode ('r')
    '''

def main():
    # Check for command-Line Argument: script expects file path as a 
    # command-line argumen, if not provided, it displays a usage message and exits.
    if len(sys.argv) < 2:
        ''' `if len(sys.argv) < 2:` checks if fewer than two arguments are provided 
        ( like just the `script` name & NO additional arguments )'''

        print("Usage: python script.py [file_path], please provide a suitable file path")
        sys.exit(1) # Exits the program with a status code of 1
    
    file_path = sys.argv[1]
    read_file(file_path)
if __name__ == "__main__":
    main()

    






