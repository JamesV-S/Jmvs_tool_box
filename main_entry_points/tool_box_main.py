
import importlib
from controllers import tool_box_controller 

importlib.reload(tool_box_controller)

class ToolBoxMain:
    def __init__(self, *args, **kwargs):
        self.controller = tool_box_controller.ToolBoxController()
        self.controller.view.show()
        # return self.controller


def tool_box_main():
    controller = tool_box_controller.ToolBoxController()
    controller.view.show()
    return controller
        

    