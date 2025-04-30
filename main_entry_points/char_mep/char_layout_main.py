# main.py -> in a different file!
import importlib
from controllers.char_controllers import char_layout_controller 

importlib.reload(char_layout_controller)

class CharLayoutMain():
    def __init__(self, *args, **kwargs):
        self.controller = char_layout_controller.CharLayoutController()
    

    def show_ui(self):
        self.controller = char_layout_controller.CharLayoutController()
        self.controller.view.show()
        return self.controller