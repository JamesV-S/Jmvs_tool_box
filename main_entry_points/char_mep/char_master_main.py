# main.py -> in a different file!
import importlib
from controllers.char_controllers import char_master_controller 

importlib.reload(char_master_controller)

def char_master_main():
    # No ApplicationInstance becuase it is being handled through 'geo_db.py' already! 
    controller = char_master_controller.CharMasterController()
    controller.view.show()

    return controller