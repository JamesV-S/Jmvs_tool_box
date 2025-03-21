# main.py -> in a different file!
import importlib
from controllers.geoDB_controllers import geoDB_master_controller 

importlib.reload(geoDB_master_controller)


class GeoDbMasterMain:
    def __init__(self, *args, **kwargs):
        self.controller = geoDB_master_controller.GeoDbMasterController()
        
        
    def show_ui(self):
        self.controller.view.show()
        return self.controller
