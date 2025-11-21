# ----------------------------------------- VIEW ----------------------------------------
import importlib
from maya import OpenMayaUI
import os

try:
    from PySide6 import QtCore, QtWidgets, QtGui
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtGui import QIcon, QStandardItemModel, QStandardItem
    from PySide6.QtWidgets import (QWidget)
    from shiboken6 import wrapInstance
except ModuleNotFoundError:
    from PySide2 import QtCore, QtWidgets, QtGui
    from PySide2.QtCore import Qt, Signal
    from PySide2.QtGui import QIcon
    from PySide2.QtWidgets import (QWidget)
    from shiboken2 import wrapInstance

from utils import (
    utils_os
)

from views import utils_view

importlib.reload(utils_os)
importlib.reload(utils_view)

maya_main_wndwPtr = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndwPtr), QWidget)

class JmvsNetworkView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(JmvsNetworkView, self).__init__(parent)
        version = "MVC"
        ui_object_name = f"JmvsNetwork_{version}"
        ui_window_name = f"Jmvs_Network_{version}"
        utils_view.delete_existing_ui(ui_object_name)
        self.setObjectName(ui_object_name)

        # set flags & dimensions
        # ---------------------------------- 
        self.setParent(main_window) 
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(ui_window_name)
        self.resize(200, 200)
        
        # Load the stylesheet
        stylesheet_path = os.path.join(
            utils_os.create_directory("Jmvs_tool_box", "assets", "styles"), 
            "jmvs_network_style_sheet.css"
            ) #  jmvs_network_style_sheet
        print(stylesheet_path)
        with open(stylesheet_path, "r") as file:
            stylesheet = file.read()
        self.style_sheet = stylesheet
        self.setStyleSheet(stylesheet)
        
        self.user_module_data = {} # to store user inputs from 'choose module ui'! 
        
        # Create the main layout
        self.main_Vlay = QtWidgets.QVBoxLayout(self)
        self.main_Vlay.setObjectName("main_Layout")

        # Core ui layouts
            # jmvs_network ui workspace 
        layV_network = QtWidgets.QVBoxLayout()
            # Buttons for Tools
        layH_tools = QtWidgets.QHBoxLayout()
        utils_view.add_to_main_lay(self.main_Vlay, [layV_network, layH_tools])

        # Container style lists
        self.container_style_ls = []
        self.container_child_style_ls = []

        # style groups
        self.style_network_ui = []
        self.style_tools_buttons = []
        # Call ui bbuild functions
        self.network_ui(layV_network)
        self.tools_button_ui(layH_tools)

        for container in self.container_style_ls:
            container.setProperty("style_container", True)
            container.style().unpolish(container)
            container.style().polish(container)
            container.update()
        for child_container in self.container_child_style_ls:
            child_container.setProperty("style_child_container", True)
            child_container.style().unpolish(child_container)
            child_container.style().polish(child_container)
            child_container.update()

        # style list property
        for widget in self.style_network_ui:
            widget.setProperty("network_UI", True)
        for widget in self.style_tools_buttons:
            widget.setProperty("tool_UI", True)

        # Set main layout
        self.setLayout(self.main_Vlay)


    def network_ui(self, widgets_layout):
        '''
        # Description:
            Top level ui creation. 
            For: Network ui.
            FEATURES:
                - Make new rig project. 
                - Rig File Mangement.
        # Attributes:
            widgets_layout (Q*BoxLayout): QWidget that is the invisible top level 
                                        container for this ui. 
        # Returns: N/A 
        '''
        

        lft_temp_layV = QtWidgets.QVBoxLayout()
        rt_temp_layV = QtWidgets.QVBoxLayout()
        # temp_layV.addWidget(temp_button)
        lft_btn_ls = []
        rt_btn_ls = []
        lft_btn_name_ls = ["Apple", "Beta", "Charlie", "Denvor", "Elephant"]
        rt_btn_name_ls = ["Apple", "Beta", "Charlie", "Denvor", "Elephant"]
        rt_btn_name_ls.reverse()
        for l_btn, r_btn in zip(lft_btn_name_ls, rt_btn_name_ls):
            lb = QtWidgets.QPushButton(l_btn)
            rb = QtWidgets.QPushButton(r_btn)
            lft_btn_ls.append(lb)
            rt_btn_ls.append(rb)

        for l_btn, r_btn in zip(lft_btn_ls, rt_btn_ls):
            lft_temp_layV.addWidget(l_btn)
            rt_temp_layV.addWidget(r_btn)

        lft_network_container_lay, chk_none = utils_view.test_cr_container_ui(
            label_name="Left Network", 
            widget_to_add=lft_temp_layV, 
            style_sheet=self.style_sheet, 
            style_ls=self.container_style_ls, style_child_ls=self.container_child_style_ls,
            # min_width=150, min_height=300,
            layout=True,
            child=True
            )
        
        rt_network_container_lay, chk_none = utils_view.test_cr_container_ui(
            label_name="Right Network", 
            widget_to_add=rt_temp_layV, 
            style_sheet=self.style_sheet, 
            style_ls=self.container_style_ls, style_child_ls=self.container_child_style_ls,
            min_width=600, min_height=500,
            layout=True,
            child=True
            )

        # lft_rt_layH = QtWidgets.QHBoxLayout()

        parent_container_layH = QtWidgets.QHBoxLayout()
        parent_network_container_lay, chk_none = utils_view.test_cr_container_ui(
            label_name="Rig Management & Versioning",
            widget_to_add=parent_container_layH, 
            style_sheet=self.style_sheet, 
            style_ls=self.container_style_ls, style_child_ls=self.container_child_style_ls,
            # min_width=700, min_height=500,
            layout=True,
            )
        
        parent_container_layH.addLayout(lft_network_container_lay)
        parent_container_layH.addLayout(rt_network_container_lay)

        widgets_layout.addLayout(parent_network_container_lay)


    def tools_button_ui(self, widgets_layout):
        '''
        # Description:
            Top level ui creation. 
            For: Buttons 'char_layout', 'char_systems', 'char_skeleton' ui's.
            FEATURES:
                - Button for each tool.
        # Attributes:
            widgets_layout (Q*BoxLayout): QWidget that is the invisible top level 
                                        container for this ui. 
        # Returns: N/A 
        '''
        tools_layH = QtWidgets.QHBoxLayout()

        self.char_layout_btn = QtWidgets.QPushButton("Layout")
        self.char_systems_btn = QtWidgets.QPushButton("Systems")
        self.char_skeleton_btn = QtWidgets.QPushButton("Skeleton")
        btn_list = [self.char_layout_btn, self.char_systems_btn, self.char_skeleton_btn]

        # utils_view.assign_style_ls(self.style_tools_buttons, btn_list)
        
        for btn in btn_list:
            tools_layH.addWidget(btn)
        
        tools_container, chk_none = utils_view.test_cr_container_ui(
            label_name="Tools", 
            widget_to_add=tools_layH, 
            style_sheet=self.style_sheet, 
            style_ls=self.container_style_ls, style_child_ls=self.container_child_style_ls,
            # min_width=None, min_height=None, 
            # max_width=None, max_height=None,
            layout=True,
            )

        widgets_layout.addLayout(tools_container)

