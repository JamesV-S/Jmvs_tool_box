
import importlib
from controllers.char_controllers import char_master_controller 

importlib.reload(char_master_controller)

class CharMasterMain:
    def __init__(self, *args, **kwargs):
        self.controller = char_master_controller.CharMasterController()
        
        
    def show_ui(self):
        self.controller.view.show()
        return self.controller

    