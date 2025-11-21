
import importlib
from controllers.char_controllers import jmvs_network_controller 

importlib.reload(jmvs_network_controller)

class JmvsNetworkMain:
    def __init__(self, *args, **kwargs):
        self.controller = jmvs_network_controller.JmvsNetworkController()
        
        
    def show_ui(self):
        self.controller.view.show()
        return self.controller

    