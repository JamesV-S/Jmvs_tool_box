
import importlib
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)
os.environ['MAYA_SCRIPT_PATH'] = script_dir + os.pathsep + os.environ.get('MAYA_SCRIPT_PATH', '')

# import the ui & run it
import ui_toolBox
importlib.reload(ui_toolBox)

def run_ui():
    ui_toolBox.main()
    print("main is run")
#run_ui()
