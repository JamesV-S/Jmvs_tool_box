
import importlib
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
add_path = os.path.join(current_dir)
sys.path.append(add_path)
os.environ['MAYA_SCRIPT_PATH'] = current_dir + os.pathsep + os.environ.get('MAYA_SCRIPT_PATH', '')

char_db_path = os.path.join(os.path.dirname(__file__), 'databases', 'char_databases')
char_ui_path = os.path.join(os.path.dirname(__file__), 'user_interface', 'char_ui')

sys.path.append(os.path.join(os.path.dirname(__file__), 'databases', 'char_databases'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'user_interface', 'char_ui'))

print(f"custom paths: DB = {char_db_path} & UI = {char_ui_path}")

# import the ui & run it
import toolBox
importlib.reload(toolBox)

def run_tool_box():
    #toolBox.tl_bx_main()
    #print("run toolBox")
    pass

