# ----------------------------------------- VIEW ----------------------------------------
import maya.cmds as cmds
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
    utils_os,
    utils_json
)

from views import (
    utils_view
    )

importlib.reload(utils_os)
importlib.reload(utils_json)
importlib.reload(utils_view)

maya_main_wndwPtr = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndwPtr), QWidget)

class CharLayoutView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CharLayoutView, self).__init__(parent)
        version = "MVC"
        ui_object_name = f"JmvsCharLayout_{version}"
        ui_window_name = f"Jmvs_Char_Layout_{version}"
        utils_view.delete_existing_ui(ui_object_name)
        self.setObjectName(ui_object_name)

        self.setParent(main_window) 
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(ui_window_name)
        self.resize(400, 550)

        stylesheet_path = os.path.join(
            utils_os.create_directory("Jmvs_tool_box", "assets", "styles"), 
            "char_style_sheet_001.css"
            )
        print(stylesheet_path)
        with open(stylesheet_path, "r") as file:
            stylesheet = file.read()
        self.setStyleSheet(stylesheet)

        self.json_dict = utils_json.get_modules_json_dict('char_config')

        self.init_ui()

  
    def init_ui(self):
        main_Vlayout = QtWidgets.QVBoxLayout(self)
        main_Vlayout.setObjectName("main_Layout")

        top_Hlayout = QtWidgets.QHBoxLayout() # db_vis & mdl_choose
        bottom_Vlayout = QtWidgets.QVBoxLayout() # add_blueprint & updating db

        main_Vlayout.addLayout(top_Hlayout)
        main_Vlayout.addLayout(bottom_Vlayout)
        
        # style the labels
        style_treeview_ui = [] 
        # style_module_ui_labels = []
        style_update_mdl_ui = []
        style_addRemove_ui = []
        style_template_ui = []
        style_lockUnlock_ui = []
        
        #----------------------------------------------------------------------
        # ---- database editor ----
        layV_module_Tree = QtWidgets.QVBoxLayout()
        
        self.tree_view_name_lbl = QtWidgets.QLabel("Database: `Rig Name`")
        self.tree_view_name_lbl.setObjectName("tree_DB_NAME_lbl")
        style_treeview_ui.append(self.tree_view_name_lbl)

        self.mdl_tree_model = QtGui.QStandardItemModel()
        self.mdl_tree_model.setColumnCount(1)

        self.mdl_tree_view = QtWidgets.QTreeView(self)
        self.mdl_tree_view.setModel(self.mdl_tree_model)
        self.mdl_tree_view.setObjectName("mdl_treeview")
        style_treeview_ui.append(self.mdl_tree_view)

        # set selection mode to multiSelection
        self.mdl_tree_view.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        layV_module_Tree.addWidget(self.tree_view_name_lbl)
        layV_module_Tree.addWidget(self.mdl_tree_view)
        
        # -- treeView settings --
        header = self.mdl_tree_view.header()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.mdl_tree_view.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Maximum)
        self.mdl_tree_view.setMinimumSize(150, 200)
        self.mdl_tree_view.setHeaderHidden(True)
        self.mdl_tree_view.setAnimated(True)
        self.mdl_tree_view.setUniformRowHeights(True)
        self.mdl_tree_view.setEditTriggers(QtWidgets.QAbstractItemView.SelectedClicked)
        layV_module_Tree.setSpacing(5)
        # from selection in treeView, just uses name to select the
        top_Hlayout.addLayout(layV_module_Tree)

        #----------------------------------------------------------------------
        # ---- choose modules ----        
        layV_choose_mdl_ancestor = QtWidgets.QVBoxLayout()
        #layV_choose_mdl_ancestor.setContentsMargins(40, 0, 0, 40)
        #layV_choose_mdl_ancestor.setSpacing()
        
        # -- Available RIG --
        layV_available_rig = QtWidgets.QVBoxLayout()
        # layV_available_rig.setContentsMargins(0, 0, 0, 0)

        available_rig_lbl = QtWidgets.QLabel("Available RIG:")
        style_treeview_ui.append(available_rig_lbl)

        available_rig_lbl.setFixedSize(200,20)
        self.available_rig_comboBox = QtWidgets.QComboBox()
        self.available_rig_comboBox.setFixedSize(225,30)
        self.val_availableRigComboBox = self.available_rig_comboBox.currentText()
        style_treeview_ui.append(self.available_rig_comboBox)

        #layV_available_rig.addWidget(available_rig_lbl)
        layV_available_rig.addWidget(self.available_rig_comboBox)
        layV_choose_mdl_ancestor.addLayout(layV_available_rig)

        # -- Add module editor --
        layV_add_mdl_layout = QtWidgets.QVBoxLayout()

        def module_choose_ui(mdl_name, side_items):
            mdl_h_layout = QtWidgets.QHBoxLayout()
            
            mdl_checkBox = QtWidgets.QCheckBox()
            mdl_name_label = QtWidgets.QLabel(mdl_name)
            mdl_name_label.setFixedSize(70, 30)
            style_treeview_ui.append(mdl_name_label)
            style_treeview_ui.append(mdl_checkBox)
            
            mdl_iterations = QtWidgets.QSpinBox()
            mdl_iterations.setMinimum(1)
            mdl_iterations.setEnabled(False)
            mdl_iterations.setFixedSize(50, 30)
            style_treeview_ui.append(mdl_iterations)
            
            
            mdl_h_layout.addWidget(mdl_checkBox)
            mdl_h_layout.addWidget(mdl_name_label)
            mdl_h_layout.addWidget(mdl_iterations)
            
            mdl_side = None
            if side_items != "None":
                mdl_side = QtWidgets.QComboBox()
                mdl_side.addItems(side_items)
                mdl_side.setEnabled(False)
                mdl_h_layout.addWidget(mdl_side)
                mdl_side.setFixedSize(55, 30)
                style_treeview_ui.append(mdl_side)
                
            layV_add_mdl_layout.addLayout(mdl_h_layout)

            return mdl_checkBox, mdl_iterations, mdl_side

        # get mdl_name and side data for each module
        try:
            mdl_list = []
            side_list = []
            for filename, data in self.json_dict.items():
                # `.get()` used to access dict values, without keyerror if not 
                # like we get with `[]`
                mdl_name = data.get('mdl_name', 'no module name, there should be')
                # .get a nested value within a dict; empty '{}' means no error if 'user_settings' is missing.
                mdl_side = data.get('user_settings', {}).get('side', ['No side in mdl'])
                if mdl_name:
                    mdl_list.append(mdl_name)
                    if mdl_side == ['None']:
                        side_list.append([""])
                        print(f"HAHAHAHHAHAH {side_list}")
                    else:
                        side_list.append(mdl_side)
                        print(f">>> NONOONONONOON {side_list}")
            
            print(mdl_list) #['bipedArm', 'bipedLeg']
            print(side_list) #[['L', 'R'], ['L', 'R']]
        except KeyError as e:
            print(f"{e} is not a key in {filename}")
        
        # Create the ui components & store it in a dict
        ''' Signal Functions are handled here! '''
        self.mdl_choose_ui_dict = {}
        for mdl, sides in zip(mdl_list, side_list):
            mdl_choose_buttons = module_choose_ui(mdl, sides)
            self.mdl_choose_ui_dict[mdl] = mdl_choose_buttons
        print(f"self.mdl_choose_ui_dict = {self.mdl_choose_ui_dict}")
        
        layV_choose_mdl_ancestor.addLayout(layV_add_mdl_layout)

        top_Hlayout.addLayout(layV_choose_mdl_ancestor)

        #----------------------------------------------------------------------
        # -- Selected mdl operations --
        # self.layGRP_mdl_operations = QtWidgets.QGroupBox("GroupBoxTitle_001", self)
        #font = QtGui.QFont("Times New Roman",  12)
        #font.setBold(True)
        #self.layGRP_mdl_operations.setFont(font)
        layV_mdl_operations_ancestor = QtWidgets.QVBoxLayout()
        # -- Pusblish module additions --
        layH_publish_mdl_additons = QtWidgets.QHBoxLayout()
        # update mdl with new positions!
        self.rpl_live_component = QtWidgets.QPushButton("Replace live Component")
        self.publish_btn = QtWidgets.QPushButton("+ Publish Module Additions")
        layH_publish_mdl_additons.addWidget(self.rpl_live_component)
        layH_publish_mdl_additons.addWidget(self.publish_btn)
        style_treeview_ui.append(self.publish_btn)
        style_treeview_ui.append(self.rpl_live_component)

        layV_mdl_operations_ancestor.addLayout(layH_publish_mdl_additons)

        mdl_data_lbl = QtWidgets.QLabel("Module Data:")
        mdl_data_lbl.setObjectName("mdl_data_lbl")
        style_update_mdl_ui.append(mdl_data_lbl)

        # -- current_mdl_operations --
        #layV_current_MO_parent = QtWidgets.QVBoxLayout()
        layGrid_update = QtWidgets.QGridLayout()

        cmo_lbl = QtWidgets.QLabel("Current >")
        cmo_lbl.setObjectName("update_left_lbl")
        self.cmo_rigType_lbl = QtWidgets.QLabel("Rig Type: _ _")
        self.cmo_mirrorMdl_lbl = QtWidgets.QLabel("Mirror: _ _")
        self.cmo_stretch_lbl = QtWidgets.QLabel("Stretch: _ _")
        self.cmo_twist_lbl = QtWidgets.QLabel("Twist: _ _")
        
        
        umo_lbl = QtWidgets.QLabel("Update >")
        umo_lbl.setObjectName("update_left_lbl")
        umo_rigType_lbl = QtWidgets.QLabel("Rig Type:")
        style_update_mdl_ui.append(umo_rigType_lbl)
        self.umo_rigType_comboBox = QtWidgets.QComboBox()
        self.umo_rigType_comboBox.addItems(["FK", "IK", "IKFK"])
        self.umo_mirrorMdl_checkBox = QtWidgets.QCheckBox("Mirror")
        self.umo_stretch_checkBox = QtWidgets.QCheckBox("Stretch")
        self.umo_twist_checkBox = QtWidgets.QCheckBox("Twist")
        
        cmo_ls = [cmo_lbl, self.cmo_rigType_lbl, self.cmo_mirrorMdl_lbl, self.cmo_stretch_lbl, self.cmo_twist_lbl]
        umd_ls = [umo_lbl, self.umo_rigType_comboBox, self.umo_mirrorMdl_checkBox, self.umo_stretch_checkBox, self.umo_twist_checkBox]
        cmo_pos_ls = [[0,0], [0,1], [0,2], [0,3], [0,4]]
        umd_pos_ls = [[1,0], [1,1], [1,2], [1,3], [1,4]]
        for x in range(len(cmo_ls)):
            layGrid_update.addWidget(cmo_ls[x], cmo_pos_ls[x][0], cmo_pos_ls[x][1])
            layGrid_update.addWidget(umd_ls[x], umd_pos_ls[x][0], umd_pos_ls[x][1])
            style_update_mdl_ui.append(cmo_ls[x])
            style_update_mdl_ui.append(umd_ls[x])
        
        def layH_SPACER_func():
            # -- Horizontal Spacer --
            layH_Spacer = QtWidgets.QHBoxLayout()
            # Add the spacer QWidget
            spacerH = QtWidgets.QLabel()# QtWidgets.QWidget()
            #spacerH.setFixedSize(40,40)
            spacerH.setObjectName("Spacer")
            style_update_mdl_ui.append(spacerH)
            layH_Spacer.addWidget(spacerH)
            layH_Spacer.setContentsMargins(0, 0, 0, 0)
            return layH_Spacer

        layH_upd_mdl_btn = QtWidgets.QHBoxLayout()
        SpacerGraphic_0_layH = layH_SPACER_func()
        self.update_btn = QtWidgets.QPushButton("Update Module Data")
        style_update_mdl_ui.append(self.update_btn)

        SpacerGraphic_1_layH = layH_SPACER_func()
        layH_upd_mdl_btn.addLayout(SpacerGraphic_0_layH)
        layH_upd_mdl_btn.addWidget(self.update_btn)
        layH_upd_mdl_btn.addLayout(SpacerGraphic_1_layH)
        
        layV_mdl_operations_ancestor.addWidget(mdl_data_lbl)
        layV_mdl_operations_ancestor.addLayout(layGrid_update)
        layV_mdl_operations_ancestor.addLayout(layH_upd_mdl_btn)
        
        bottom_Vlayout.addLayout(layV_mdl_operations_ancestor)

        # ---------------------------------------------------------------------
        # Updating modules and database
        layV_deleteAdd_mdl_ancestor = QtWidgets.QVBoxLayout()
        
        # -- delete mdl btns --
        layH_mdl_delete = QtWidgets.QHBoxLayout()
        self.delete_mdl_btn = QtWidgets.QPushButton("Remove module") # selected mdl
        self.delete_blueprint_btn = QtWidgets.QPushButton("Delete Blueprint") # entire blueprint
        layH_mdl_delete.addWidget(self.delete_mdl_btn)
        layH_mdl_delete.addWidget(self.delete_blueprint_btn)
        
        # -- add mdl btns --
        layH_mdl_add = QtWidgets.QHBoxLayout()
        self.add_mdl_btn = QtWidgets.QPushButton("Add module") # selected mdl
        self.add_blueprint_btn = QtWidgets.QPushButton("Create Blueprint") # add entire blueprint(deletes old and remakes it)
        layH_mdl_add.addWidget(self.add_mdl_btn)
        layH_mdl_add.addWidget(self.add_blueprint_btn)

        layV_deleteAdd_mdl_ancestor.addLayout(layH_mdl_delete)
        layV_deleteAdd_mdl_ancestor.addLayout(layH_mdl_add)

        self.add_mdl_btn.setObjectName("add_mdl_btn")
        self.add_blueprint_btn.setObjectName("add_blueprint_btn")
        self.delete_mdl_btn.setObjectName("remove_mdl_btn")
        self.delete_blueprint_btn.setObjectName("delete_blueprint_btn")

        bottom_Vlayout.addLayout(layV_deleteAdd_mdl_ancestor)

        # ---------------------------------------------------------------------
        # ---- component editing ----
        layH_componentEditing_ancestor = QtWidgets.QHBoxLayout()
        
        # -- Template Display -- 
        self.grp_boxTempDisp = QtWidgets.QGroupBox("Template Display", self)
        self.grp_boxTempDisp.setObjectName("grp_boxTempDisp")
        self.grp_boxTempDisp.setObjectName("grp_boxTempDisp")

        layV_tempDisp = QtWidgets.QVBoxLayout()
        
        self.guide_template_checkBox = QtWidgets.QCheckBox("Guides")
        self.controls_template_checkBox = QtWidgets.QCheckBox("Controls")
        self.ddj_template_checkBox = QtWidgets.QCheckBox("Deform Diagnostics")
        layV_tempDisp.addWidget(self.guide_template_checkBox)
        layV_tempDisp.addWidget(self.controls_template_checkBox)
        layV_tempDisp.addWidget(self.ddj_template_checkBox)

        # set checkBox by default
        self.controls_template_checkBox.setChecked(True)
        self.ddj_template_checkBox.setChecked(True)

        # - template gid buttons - 
        layGrid_tempDisp = QtWidgets.QGridLayout()
        self.temp_Toggle_btn = QtWidgets.QPushButton("Toggle")
        self.temp_Isolate_btn = QtWidgets.QPushButton("Isolate")
        self.temp_All_btn = QtWidgets.QPushButton("Template All")
        self.temp_AllVis_btn = QtWidgets.QPushButton("All Visible")

        layGrid_tempDisp.addWidget(self.temp_Toggle_btn, 0, 0)
        layGrid_tempDisp.addWidget(self.temp_Isolate_btn, 0, 1)
        layGrid_tempDisp.addWidget(self.temp_All_btn, 1, 0)
        layGrid_tempDisp.addWidget(self.temp_AllVis_btn, 1, 1)

        layV_tempDisp.addLayout(layGrid_tempDisp)

        # layV_tempDisp.addLayout(layGrid_tempDisp)
        
        # -- Lock/Unlock --
        self.grp_boxUL = QtWidgets.QGroupBox("Lock/Unlock", self)
        self.grp_boxUL.setObjectName("grp_boxUL")

        layV_LU = QtWidgets.QVBoxLayout()
        
        self.compnent_checkBox = QtWidgets.QCheckBox("Component")
        self.val_compnent_checkBox = 0
        self.inputComp_checkBox = QtWidgets.QCheckBox("Input Components")
        self.OutputComp = QtWidgets.QCheckBox("Output Components")
        layV_LU.addWidget(self.compnent_checkBox)
        layV_LU.addWidget(self.inputComp_checkBox)
        layV_LU.addWidget(self.OutputComp)

        # - lock gid buttons - 
        layGrid_LU = QtWidgets.QGridLayout()
        self.lock_btn = QtWidgets.QPushButton("Lock")
        self.unlock_btn = QtWidgets.QPushButton("Unlock")

        layGrid_LU.addWidget(self.lock_btn, 0, 0)
        layGrid_LU.addWidget(self.unlock_btn, 0, 1)

        layV_LU.addLayout(layGrid_LU)
        
        self.grp_boxTempDisp.setLayout(layV_tempDisp)
        layH_componentEditing_ancestor.addWidget(self.grp_boxTempDisp)
        
        self.grp_boxUL.setLayout(layV_LU)
        layH_componentEditing_ancestor.addWidget(self.grp_boxUL)

        bottom_Vlayout.addLayout(layH_componentEditing_ancestor)
        
        # ---------------------------------------------------------------------
        self.setLayout(main_Vlayout)

        # add module label style property here
        for tree_widget in style_treeview_ui:
            tree_widget.setProperty("treeComponents_UI_01", True)

        for widget in style_update_mdl_ui:
            widget.setProperty("update_UI", True)

        for wid in [cmo_lbl, self.cmo_rigType_lbl, self.cmo_mirrorMdl_lbl, self.cmo_stretch_lbl, self.cmo_twist_lbl]:
            wid.setEnabled(False)
            wid.setProperty("Current_disabled", True)
