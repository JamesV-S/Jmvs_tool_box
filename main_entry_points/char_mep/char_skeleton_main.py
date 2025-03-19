# main.py -> in a different file!
import importlib
from controllers.char_controllers import char_skeleton_controller 

importlib.reload(char_skeleton_controller)

def geo_db_main():
    # No ApplicationInstance becuase it is being handled through 'geo_db.py' already! 
    controller = char_skeleton_controller.CharSkeletonController()
    controller.view.show()

    return controller