# main.py -> in a different file!
import importlib
from controllers.char_controllers import char_skeleton_controller 

importlib.reload(char_skeleton_controller)

class CharSkeletonMain():
    def __init__(self, *args, **kwargs):
        # No ApplicationInstance becuase it is being handled through 'geo_db.py' already! 
        self.controller = char_skeleton_controller.CharSkeletonController()

    
    def show_ui(self):
        self.controller.view.show()
        return self.controller