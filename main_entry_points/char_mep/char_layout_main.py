# main.py -> in a different file!
import importlib
from controllers.char_controllers import char_layout_controller 

importlib.reload(char_layout_controller)

def char_layout_main():
    # No ApplicationInstance becuase it is being handled through 'geo_db.py' already! 
    controller = char_layout_controller.CharLayoutController()
    controller.view.show()

    return controller