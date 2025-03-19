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

from systems import (
    os_custom_directory_utils,
    utils
)

from views import (
    utils_view, 
    utils_Qtree
    )

importlib.reload(os_custom_directory_utils)
importlib.reload(utils_view)
importlib.reload(utils_TreeView)

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
            os_custom_directory_utils.create_directory("Jmvs_tool_box", "assets", "styles"), 
            "char_style_sheet_001.css"
            )
        print(stylesheet_path)
        with open(stylesheet_path, "r") as file:
            stylesheet = file.read()
        self.setStyleSheet(stylesheet)
    

    def UI_modules(self):
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


    def sigFunc_rpl_live_component(self):
        # print selection in ui:
        component_selection = self.get_component_name_TreeSel()
        for component in component_selection:
            self.record_component_change(component)

    
    # ------------ siFunc Choose modules functions ------------
    def sigFunc_availableRigComboBox(self):
        self.val_availableRigComboBox = self.available_rig_comboBox.currentText()
        tree_name = self.val_availableRigComboBox.replace("DB_", "")
        self.tree_view_name_lbl.setText(f"Database: `{tree_name}`")
        self.visualise_active_db()
        print(f"available rig chosen: `{self.val_availableRigComboBox}`")


    # define the 3 widget functions appropriatly, taking the `mdl_name` arg from lambda!
    def sigFunc_mdl_checkBox(self, mdl_name):
        mdl_checkBox = self.mdl_choose_ui_dict[mdl_name][0]
        self.val_mdl_checkBox = mdl_checkBox.isChecked()

        # store the data! 
        # - set `mdl_name` as the keyy
        # - add checkbox & add temp value & string for remaining signals
        if mdl_name == 'spine':
            letter = "M"
        else:
            letter = "L"
        self.user_module_data[mdl_name] = {
            "mdl_checkBox": self.val_mdl_checkBox,
            "mdl_iteration": self.user_module_data.get(mdl_name, {}).get('iteration', 1),
            "mdl_side": self.user_module_data.get(mdl_name, {}).get('side', letter)
        }

        if self.val_mdl_checkBox: # Enable other widgets where neccesary
            self.mdl_choose_ui_dict[mdl_name][1].setEnabled(True)
            if mdl_name == "spine" or mdl_name == "root":
                pass
            else:
                self.mdl_choose_ui_dict[mdl_name][2].setEnabled(True)
        else:
            self.mdl_choose_ui_dict[mdl_name][1].setEnabled(False)             
            self.mdl_choose_ui_dict[mdl_name][2].setEnabled(False)
        print(f"MDL::{mdl_name} &  self.val_mdl_checkBox::{self.val_mdl_checkBox}")
    
    def sigFunc_mdl_IterationSpinBox(self, mdl_name):
        mdl_iteration = self.mdl_choose_ui_dict[mdl_name][1]
        if mdl_name == "root":
            mdl_iteration.setMinimum(1)
            mdl_iteration.setMaximum(1)
        self.val_mdl_iteration = mdl_iteration.value()
        
        # add the remaining iteration widget signal
        self.user_module_data[mdl_name]["mdl_iteration"] = self.val_mdl_iteration

        print(f"MDL::{mdl_name} &  self.val_mdl_checkBox::{self.val_mdl_iteration}")

    def sigFunc_mdl_SideCombobox(self, mdl_name):
        mdl_side = self.mdl_choose_ui_dict[mdl_name][2]
        self.val_mdl_side = mdl_side.currentText()
        self.val_mdl_name = mdl_name

        # add the remaining iteration widget signal
        #if self.val_mdl_side == "None":
        #    self.user_module_data[mdl_name]["mdl_side"] = ""
        #else:
        self.user_module_data[mdl_name]["mdl_side"] = self.val_mdl_side

        print(f"MDL::{self.val_mdl_name} &  self.val_mdl_checkBox::{self.val_mdl_side}")
    
    # -- Publish --
    def sigfunc_publish_btn(self): # cr a new dictionary to store the state of each module!
        print(f"sigfunc_publish_btn clicked")
        for mdl, signals in self.user_module_data.items():
            #print(f"MDL::{mdl} & signals::{signals}")
            print(f"MDL::{mdl} & checkbox::{signals['mdl_checkBox']}, iteration::{signals['mdl_iteration']}, side::{signals['mdl_side']}")
            self.cr_mdl_json_database(mdl, signals['mdl_checkBox'], signals['mdl_iteration'], signals['mdl_side'])
            self.visualise_active_db()
        
    
    # ---- add blueprint ----
    def func_createXfmGuides(self, component_selection):
            for selection in component_selection:
                parts = selection.split('_')
                if "root" in selection:
                    obj_name = f"*_{parts[1]}"
                else:
                    obj_name = f"*_{parts[1]}_*_{parts[2]}_{parts[3]}"
                if cmds.objExists(obj_name):
                    exists = 1
                else:
                    exists = 0
                    mdl_component_dict = self.retrieve_component_dict_from_nameSel(selection)
                    print(f"RETURNED DICT = {mdl_component_dict}")
                    cr_guides.CreateXfmGuides(mdl_component_dict)
            
            if not exists:
                # parent the blueprints to hierarchy rig group properly
                try:
                    cmds.parent("grp_component_misc", "grp_components")
                    cmds.parent("grp_ctrl_components", "grp_controls")
                except Exception as e:
                    print(f"parenting error: `grp_component_misc`, `grp_ctrl_components` to `grp_components` = {e}")
            else:
                print(f"component already exists in the scene: {selection}")
            self.controls_template_checkBox.setChecked(False)
            self.ddj_template_checkBox.setChecked(False)
            self.controls_template_checkBox.setChecked(True)
            self.ddj_template_checkBox.setChecked(True)


    def sigfunc_add_module(self):
        self.load_rig_group()
        print(f"What is mdl_choose_ui_dict? == {self.mdl_choose_ui_dict}") # output = {}
        # select the component(red) in the 
        # this dict comes from gathering data from active databases in active rig folder!
        example_component_dict = {
            "module_name":"bipedArm", 
            "unique_id":0,
            "side":"L", 
            "component_pos":{
                'clavicle': [3.9705319404602006, 230.650634765625, 2.762230157852166], 
                'shoulder': [28.9705319404602, 230.650634765625, 2.762230157852166], 
                'elbow': [53.69795846939088, 197.98831176757807, 6.61050152778626], 
                'wrist': [76.10134363174441, 169.30845642089832, 30.106774568557817]
                },
            "controls":{
                        'FK_ctrls': 
                                {'fk_clavicle': 'circle', 'fk_shoulder': 'circle', 'fk_elbow': 'circle', 'fk_wrist': 'circle'}, 
                        'IK_ctrls': 
                                {'ik_clavicle': 'cube', 'ik_shoulder': 'cube', 'ik_elbow': 'pv', 'ik_wrist': 'cube'}
                        }
            }
        component_selection = self.get_component_name_TreeSel()
        print(f"YAAAAAH component_selection = {component_selection[0]}")
        self.func_createXfmGuides(component_selection)

        self.func_unlocked_all()
        
        
    def sigfunc_add_blueprint(self):
        self.load_rig_group()
        # connect signals for module editor buttons
        for mdl, (checkBox, iterations, side) in self.mdl_choose_ui_dict.items():
            if checkBox.isChecked(): # checkbox is the master 
                # access the input from iterations and side
                iterations_value = iterations.value()
                side_value = side.currentText() if side else None
                print(f"Adding blueprint for {mdl}: Iterations={iterations_value}, Side={side_value}")
        
        component_selection = self.get_all_component_name_in_TreeView()
        self.func_createXfmGuides(component_selection)

        self.func_unlocked_all()


    # ---- Template Components! ----
    def sigFunc_guide_template_checkBox(self):
        self.val_guide_template_checkBox = self.guide_template_checkBox.isChecked()
        utils.select_set_displayType("xfm_guide_*", self.val_guide_template_checkBox, False)


    def sigFunc_controls_template_checkBox(self):
        self.val_controls_template_checkBox = self.controls_template_checkBox.isChecked()
        utils.select_set_displayType("ctrl_*", self.val_controls_template_checkBox, False)


    def sigFunc_ddj_template_checkBox(self):
        self.val_ddj_template_checkBox = self.ddj_template_checkBox.isChecked()
        utils.select_set_displayType("ddj_*", self.val_ddj_template_checkBox, False)
    
    # --- Unlocked component configuration ---
    def sigFunc_compnent_checkBox(self):
        self.val_compnent_checkBox = self.compnent_checkBox.isChecked()

    def sigFunc_lock_btn(self):
        if self.val_compnent_checkBox: #true
            component_selection = self.get_component_name_TreeSel()
            # treeSel = ["mdl_bipedArm_0_L"]
            for component in component_selection:
                # delete any constraints on the component's guides
                # offset_xfm_guide_bipedArm_clavicle_0_L
                # bipedArm_*_0_L
                if "mdl_root_0" in component:
                    component = "mdl_root_0_M"
                parts = component.split('_')[1:] # bipedArm, 0, L
                mdl = parts[0] # bipedArm
                uID = parts[1] # 0
                side = parts[2] # L
                
                # create the box:
                if not cmds.objExists(f"cg_{mdl}_{uID}_{side}"):
                    if 'bipedArm' in component:
                        if side == "L": ctrl_type = "imp_cg_arm_L"
                        else: ctrl_type = "imp_cg_arm_R"
                    elif 'bipedLeg' in component:
                        if side == "L": ctrl_type = "imp_cg_leg_L"
                        else: ctrl_type = "imp_cg_leg_R"
                    elif 'spine' in component:
                        ctrl_type = "imp_cg_spine"
                    elif 'root' in component:
                        ctrl_type = "imp_cg_root"
                    cube_imp_ctrl = cr_ctrl.CreateControl(type=ctrl_type, name=f"cg_{mdl}_{uID}_{side}")
                    cube_locked_comp = cube_imp_ctrl.retrun_ctrl()
                else: cube_locked_comp = f"cg_{mdl}_{uID}_{side}"
                cmds.select(cl=1)
                cmds.showHidden("cg_*")
                
                try:
                    cmds.setAttr(f"{cube_locked_comp}.overrideEnabled", 1)
                    cmds.setAttr(f"{cube_locked_comp}.hiddenInOutliner", 1)
                except Exception as e:
                    print(f"Hiding CAGEE error: {e}")

                if "mdl_root_0_M" in component:
                    sel = f"offset_xfm_guide_root", f"offset_xfm_guide_COG"
                else:
                    sel = f"offset_xfm_guide_{mdl}_*_{uID}_{side}"
                cmds.select(sel) #"pointCon_xfm_guide_bipedArm_0_L")
                comp_grpXfm_ls = cmds.ls(sl=1, type="transform")
                print(f"comp_grpXfm_ls = {comp_grpXfm_ls}")
                # get constraint & delete it!
                for grpXfm in comp_grpXfm_ls:
                    if cmds.objExists(grpXfm):
                        print(f"grpXfm = {grpXfm}")
                        constraints = cmds.listRelatives(grpXfm, type='constraint', ad=0)
                        if constraints:
                            for con in constraints:
                                print(f"constraint : : {con}")
                                cmds.delete(con)
                        # constrain grps to cage!
                        utils.constrain_2_items(cube_locked_comp, grpXfm, "parent", "all")  
        else: print(f"component checkbox is not checked")

    def sigFunc_unlock_btn(self):
        if self.val_compnent_checkBox: #true
            component_selection = self.get_component_name_TreeSel()
            # treeSel = ["mdl_bipedArm_0_L"]
            for component in component_selection:
                # delete any constraints on the component's guides
                # offset_xfm_guide_bipedArm_clavicle_0_L
                # bipedArm_*_0_L
                if "mdl_root_0" in component:
                    component = "mdl_root_0_M"
                parts = component.split('_')[1:] # bipedArm, 0, L
                mdl = parts[0] # bipedArm
                uID = parts[1] # 0
                side = parts[2] # L
                
                if "mdl_root_0_M" in component:
                    sel = f"offset_xfm_guide_root", f"offset_xfm_guide_COG"
                else:
                    sel = f"offset_xfm_guide_{mdl}_*_{uID}_{side}"
                cmds.select(sel) #"pointCon_xfm_guide_bipedArm_0_L")
                comp_grpXfm_ls = cmds.ls(sl=1, type="transform")
                print(f"comp_grpXfm_ls = {comp_grpXfm_ls}")
                # get constraint & delete it!
                for grpXfm in comp_grpXfm_ls:
                    if cmds.objExists(grpXfm):
                        print(f"grpXfm = {grpXfm}")
                        constraints = cmds.listRelatives(grpXfm, type='constraint', ad=0)
                        if constraints:
                            for con in constraints:
                                print(f"constraint : : {con}")
                                cmds.delete(con)
                # hide the cages (make it specific in the future) 
                cmds.hide("cg_*")

                # add the normal following constraints!
                print(f"Comp_for selectionUNLOCK = {component}")
                # NORM = xfm_grp_bipedLeg_component_0_L
                # new = mdl_bipedLeg_0_L
                if "mdl_root_0" in component:
                    unlock_rdy_component = f"xfm_grp_{mdl}_component_{uID}_M"
                else: unlock_rdy_component = f"xfm_grp_{mdl}_component_{uID}_{side}" 
                self.constrain_guides_from_comp(unlock_rdy_component) 
        else: print(f"component checkbox is not checked")


