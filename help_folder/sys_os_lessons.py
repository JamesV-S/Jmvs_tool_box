
import os
import sys

# Instead of using `path.dirname` to extraxt the directory of a given path
# >> Use `os.path.normpath` to ensure a consistent path format, making paths cleaner and more predictable.
os.path.normpath('C:/path/to/file.txt') # Returns `C:\\path\\to\\file.txt`