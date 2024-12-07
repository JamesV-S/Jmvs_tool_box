
import importlib
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
add_path = os.path.join(current_dir, "user_interface")
print(f"current_dir = {current_dir}, add_path = {add_path}")
sys.path.append(add_path)
os.environ['MAYA_SCRIPT_PATH'] = current_dir + os.pathsep + os.environ.get('MAYA_SCRIPT_PATH', '')

# import the ui & run it
import toolBox
importlib.reload(toolBox)

def run_tool_box():
    toolBox.tl_bx_main()
    print("main is run")

