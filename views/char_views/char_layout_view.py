# ----------------------------------------- VIEW ----------------------------------------
import maya.cmds as cmds
import importlib
import json
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
        self.resize(510, 200)
    
        # Load the stylesheet
        stylesheet_path = os.path.join(
            utils_os.create_directory("Jmvs_tool_box", "assets", "styles"), 
            "char_style_sheet_002.css"
            )
        print(stylesheet_path)
        with open(stylesheet_path, "r") as file:
            self.stylesheet = file.read()
        self.setStyleSheet(self.stylesheet)
        
        # Initialise the config file json dict!
        self.json_dict = utils_json.get_modules_json_dict('char_config')
        
        # Create the main layout
        self.main_Vlay = QtWidgets.QVBoxLayout(self)
        self.main_Vlay.setObjectName("main_Layout")

        top_Hlay = QtWidgets.QHBoxLayout() # db_vis & mdl_choose
        # db_actions_Hlay = QtWidgets.QHBoxLayout() # publish_mdl + replace_comp
        management_options_Vlay = QtWidgets.QVBoxLayout() # management_options tabs
        mdl_actions_Vlay = QtWidgets.QVBoxLayout() # module scene action buttons!
        debugging_Vlay = QtWidgets.QVBoxLayout()

        self.main_Vlay.addLayout(top_Hlay)
        # self.main_Vlay.addLayout(db_actions_Hlay)
        self.main_Vlay.addLayout(management_options_Vlay)
        self.main_Vlay.addLayout(mdl_actions_Vlay)
        self.main_Vlay.addLayout(debugging_Vlay)
        
        # style groups
        self.style_treeview_ui = [] 
        self.style_module_ui_labels = []
        self.style_update_mdl_ui = []
        self.style_container = []
        self.style_child_container = []
        self.style_tab_1_ui = []
        self.style_template_ui = []
        self.style_lockUnlock_ui = []

        # Call the ui functions, passing the neccesary layout to each
        self.module_visualisation_ui(top_Hlay)
        self.module_additions_ui(top_Hlay)
        self.management_options_ui(management_options_Vlay)
        self.module_scene_actions_ui(mdl_actions_Vlay)
        self.debugging_ui(debugging_Vlay)

        self.set_style_property_funcUI()
        
        # ---------------------------------------------------------------------
        self.setLayout(self.main_Vlay)
        # ---------------------------------------------------------------------


    def module_visualisation_ui(self, widgets_layout):
        layV_module_visualisation = QtWidgets.QVBoxLayout()
        
        # ---- comboBox ----        
        self.available_rig_comboBox = QtWidgets.QComboBox()
        self.available_rig_comboBox.setMinimumSize(215, 30) # setFixedSize(215,30)
        self.val_availableRigComboBox = self.available_rig_comboBox.currentText()

        # ---- treeView ----
        self.mdl_tree_model = QtGui.QStandardItemModel()
        self.mdl_tree_model.setColumnCount(1)

        self.mdl_tree_view = QtWidgets.QTreeView(self)
        self.mdl_tree_view.setModel(self.mdl_tree_model)
        self.mdl_tree_view.setObjectName("mdl_treeview")    
            # -- treeView settings --
        # set selection mode to multiSelection
        self.mdl_tree_view.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        header = self.mdl_tree_view.header()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.mdl_tree_view.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.mdl_tree_view.setMinimumSize(100, 150)
        self.mdl_tree_view.setHeaderHidden(True)
        self.mdl_tree_view.setAnimated(True)
        self.mdl_tree_view.setUniformRowHeights(True)
        self.mdl_tree_view.setEditTriggers(QtWidgets.QAbstractItemView.SelectedClicked)
        layV_module_visualisation.setSpacing(5)

        self.rpl_live_component = QtWidgets.QPushButton("Replace live Component")
        
        # Assign layouts
        container_layout = QtWidgets.QVBoxLayout()
        container_layout.addWidget(self.available_rig_comboBox)
        container_layout.addWidget(self.mdl_tree_view)
        container_layout.addWidget(self.rpl_live_component)
        module_visualisation_container, chk_none = self.cr_container_funcUI("Character Database", container_layout, True)

        # layV_module_visualisation.addWidget(module_visualisation_container)
        # widgets_layout.addWidget(lbl)
        widgets_layout.addLayout(module_visualisation_container)

        # Assign custom style:
        utils_view.assign_style_ls(self.style_treeview_ui, [self.available_rig_comboBox, self.mdl_tree_view, self.rpl_live_component])

    
    def module_additions_ui(self, widgets_layout):
        layV_module_additions = QtWidgets.QVBoxLayout()
        #layV_module_additions.setContentsMargins(40, 0, 0, 40)
        #layV_module_additions.setSpacing()
            # -- Scroll area --
        scroll_area = QtWidgets.QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        
            # -- Container --
        self.module_container_widget = QtWidgets.QWidget()
        layV_add_mdl_layout = QtWidgets.QVBoxLayout(self.module_container_widget)
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
        
        # Create the ui components for each json file (config module) & store it in a dict.
        self.mdl_choose_ui_dict = {}
        for mdl, sides in zip(mdl_list, side_list):
            mdl_choose_buttons = self.module_choose_funcUI(layV_add_mdl_layout, mdl, sides)
            self.mdl_choose_ui_dict[mdl] = mdl_choose_buttons
        
        # -- Publish module additions --
        # layH_publish_btn = QtWidgets.QHBoxLayout()
        self.publish_btn = QtWidgets.QPushButton("Publish Module +")

        # Assign Widgets & Layouts
        scroll_area.setWidget(self.module_container_widget)
        
        # layV_module_additions.addWidget(self.component_list_lbl)
        layV_module_additions.addWidget(scroll_area)
        layV_module_additions.addWidget(self.publish_btn)
        module_additions_container, chk_none = self.cr_container_funcUI("Module List", layV_module_additions, True)

        widgets_layout.addLayout(module_additions_container)

        # Assign custom style:
        utils_view.assign_style_ls(self.style_treeview_ui, [self.publish_btn])
    
    
    def management_options_ui(self, widgets_layout):
        mop_tabs = QtWidgets.QTabWidget(self)
        mop_tabs.setStyleSheet(self.stylesheet)
        
        self.curve_tab_ui(mop_tabs)        
        self.module_editing_ui(mop_tabs)

        mop_container, chk_none = self.cr_container_funcUI("Management Options", mop_tabs)
        widgets_layout.addLayout(mop_container)


    def curve_tab_ui(self, tab):
        parent_widget = QtWidgets.QWidget()
        
        # Initialise Layouts
        layH_tab_curve_ancestor = QtWidgets.QHBoxLayout(parent_widget)
        layV_tab_curve_001 = QtWidgets.QVBoxLayout()
        layV_tab_curve_002 = QtWidgets.QVBoxLayout()
        layV_curve_editing = QtWidgets.QVBoxLayout()
        layH_crv_edit_001 = QtWidgets.QHBoxLayout()
        layH_crv_edit_002 = QtWidgets.QHBoxLayout()
        layH_crv_edit_003 = QtWidgets.QHBoxLayout()
        
        # ---- curve selection ----
        self.all_crv_edit_checkBox = QtWidgets.QCheckBox("All")
        self.ik_crv_edit_checkBox = QtWidgets.QCheckBox("IK")
        self.fk_crv_edit_checkBox = QtWidgets.QCheckBox("FK")
        # layH_crv_edit_001.addWidget(self.controls_crv_edit_checkBox)
        # layH_crv_edit_001.addWidget(self.guide_crv_edit_checkBox)

        self.select_data_in_comp_btn = QtWidgets.QPushButton("Select data in component")        
        self.expand_curve_btn = QtWidgets.QPushButton("Expand")
        self.collapse_curve_btn = QtWidgets.QPushButton("Collapse")
       
        self.controls_crv_edit_checkBox = QtWidgets.QCheckBox("Controls")
        self.guide_crv_edit_checkBox = QtWidgets.QCheckBox("Guides")
        self.mirror_comp_btn = QtWidgets.QPushButton("Mirror Component") # Mirror control and/or guide positional data!
        
        layH_crv_edit_001.addWidget(self.all_crv_edit_checkBox)
        layH_crv_edit_001.addWidget(self.ik_crv_edit_checkBox)
        layH_crv_edit_001.addWidget(self.fk_crv_edit_checkBox)
        layH_crv_edit_002.addWidget(self.expand_curve_btn)
        layH_crv_edit_002.addWidget(self.collapse_curve_btn)
        layV_curve_editing.addLayout(layH_crv_edit_001)
        layV_curve_editing.addWidget(self.select_data_in_comp_btn)
        layV_curve_editing.addLayout(self.lay_spacer_funcUI("H"))
        layV_curve_editing.addLayout(layH_crv_edit_002)
        layV_curve_editing.addLayout(self.lay_spacer_funcUI("H"))
        
        layH_crv_edit_003.addWidget(self.controls_crv_edit_checkBox)
        layH_crv_edit_003.addWidget(self.guide_crv_edit_checkBox)
        layV_curve_editing.addLayout(layH_crv_edit_003)
        layV_curve_editing.addWidget(self.mirror_comp_btn)
        crv_edit_container, chk_none = self.cr_container_funcUI("Curve Editing", layV_curve_editing, True, True)
        # ---- curve colour management ----
        ''' ADD COLOUR OPTIONS WITH PICKER ETC '''
        # ---- curve data management ----
        self.store_curve_comp_btn = QtWidgets.QPushButton("Store Curve Component")
        
        layV_tab_curve_001.addLayout(crv_edit_container)
        layV_tab_curve_001.addLayout(self.lay_spacer_funcUI("H"))
        layV_tab_curve_001.addWidget(self.store_curve_comp_btn)

        temp_dis_container = self.template_display_ui()
        l_u_container = self.lock_unlock_ui()
        
        layV_tab_curve_002.addLayout(temp_dis_container)
        layV_tab_curve_002.addLayout(l_u_container)
        layH_tab_curve_ancestor.addLayout(layV_tab_curve_001)
        layH_tab_curve_ancestor.addLayout(layV_tab_curve_002)

        tab.addTab(parent_widget, "curves")

        utils_view.assign_style_ls(self.style_tab_1_ui, 
             [self.expand_curve_btn, self.collapse_curve_btn, 
              self.mirror_comp_btn, self.store_curve_comp_btn, 
              self.select_data_in_comp_btn])


    def template_display_ui(self):
        layV_tempDisp = QtWidgets.QVBoxLayout()
        
        self.guide_template_checkBox = QtWidgets.QCheckBox("Guides")
        self.controls_template_checkBox = QtWidgets.QCheckBox("Controls")
        self.ddj_template_checkBox = QtWidgets.QCheckBox("Deform Diagnostics")
        layV_tempDisp.addWidget(self.guide_template_checkBox)
        layV_tempDisp.addWidget(self.controls_template_checkBox)
        layV_tempDisp.addWidget(self.ddj_template_checkBox)

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
        
        template_display_container, chk_none = self.cr_container_funcUI("Template Display", layV_tempDisp, True, True)

        utils_view.assign_style_ls(self.style_template_ui, 
             [self.guide_template_checkBox, self.controls_template_checkBox, self.ddj_template_checkBox, 
              self.temp_Toggle_btn, self.temp_Isolate_btn, self.temp_All_btn, self.temp_AllVis_btn])
        
        return template_display_container


    def lock_unlock_ui(self):
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
        
        lock_unlock_container, chk_none = self.cr_container_funcUI("Lock/Unlock", layV_LU, True, True)
        
        utils_view.assign_style_ls(self.style_lockUnlock_ui, 
             [self.compnent_checkBox, self.inputComp_checkBox, self.OutputComp, self.lock_btn, self.unlock_btn])

        return lock_unlock_container


    def module_editing_ui(self, tab):
        parent_widget = QtWidgets.QWidget()

        layV_module_editing = QtWidgets.QVBoxLayout(parent_widget)
        layH_sel_options = QtWidgets.QHBoxLayout()

        self.entire_comp_radioBtn = QtWidgets.QRadioButton("Work on components within moduls")
        self.sel_comp_radioBtn =  QtWidgets.QRadioButton("Work on individual components")
        self.selected_module_label = QtWidgets.QLabel("-> Module")
        layH_sel_options.addWidget(self.entire_comp_radioBtn)
        layH_sel_options.addWidget(self.sel_comp_radioBtn)
        
        # ----------------------------------------------------------
        # update component options
        # self.update_comp_data_checkBox = QtWidgets.QCheckBox()
        layGrid_upd_comp = self.update_component_data()
        upd_comp_container, self.update_comp_data_checkBox = self.cr_container_funcUI(
            label_name="Update comp data", widget_to_add=layGrid_upd_comp, 
            layout=True, child=True, checkbox=True)

        # Joint & control options!!
        layH_jnt_ctrl_editing = QtWidgets.QHBoxLayout()
        layV_joint_editing = QtWidgets.QVBoxLayout()
        layV_control_editing = QtWidgets.QVBoxLayout()
            # jnt editing
        layH_jnt_num = QtWidgets.QHBoxLayout()
        jnt_lbl = QtWidgets.QLabel("Joint nom : ")
        self.jnt_num_spinBox = QtWidgets.QSpinBox()
        layH_jnt_num.addWidget(jnt_lbl)
        layH_jnt_num.addWidget(self.jnt_num_spinBox)
        
        layH_ik_op = QtWidgets.QHBoxLayout()
        ik_operation_lbl = QtWidgets.QLabel("IK operations")
        self.ik_operation_comboBox = QtWidgets.QComboBox() # Add items using config data!
        layH_ik_op.addWidget(ik_operation_lbl)
        layH_ik_op.addWidget(self.ik_operation_comboBox)

        layH_constraint_type = QtWidgets.QHBoxLayout()
        constraint_type_lbl = QtWidgets.QLabel("constraint type : ")
        self.constraint_type_comboBox = QtWidgets.QComboBox() # Add items using config data!
        layH_constraint_type.addWidget(constraint_type_lbl)
        layH_constraint_type.addWidget(self.constraint_type_comboBox)
            
        layV_joint_editing.addLayout(layH_jnt_num)
        layV_joint_editing.addLayout(layH_ik_op)
        layV_joint_editing.addLayout(layH_constraint_type)
        
        joint_editing_container, self.joint_editing_checkBox = self.cr_container_funcUI(
            label_name="Edit joint data", widget_to_add=layV_joint_editing, 
            layout=True, child=True, checkbox=True)
        
        layH_jnt_ctrl_editing.addLayout(joint_editing_container)

        # ----------------------------------------------------------
            # control editing
        layH_ctrl_num = QtWidgets.QHBoxLayout()
        ctrl_num_lbl = QtWidgets.QLabel("Control nom :")
        self.ctrl_num_spinBox = QtWidgets.QSpinBox()
        layH_ctrl_num.addWidget(ctrl_num_lbl)
        layH_ctrl_num.addWidget(self.ctrl_num_spinBox)

        layH_ctrl_type = QtWidgets.QHBoxLayout()
        ctrl_type_lbl = QtWidgets.QLabel("Control type : ")
        self.ctrl_type_comboBox = QtWidgets.QComboBox() # Add items using config data!
        # layH_ctrl_type.addWidget(ctrl_type_lbl)
        layH_ctrl_type.addWidget(self.ctrl_type_comboBox)
        
        layV_control_editing.addLayout(layH_ctrl_num)
        layV_control_editing.addWidget(ctrl_type_lbl)
        layV_control_editing.addLayout(layH_ctrl_type)

        control_editing_container, self.ctrl_editing_checkBox = self.cr_container_funcUI(
            label_name="Edit control data", widget_to_add=layV_control_editing, 
            layout=True, child=True, checkbox=True)
        layH_jnt_ctrl_editing.addLayout(self.lay_spacer_funcUI("V"))
        layH_jnt_ctrl_editing.addLayout(control_editing_container)
        # Commit changes button!
        self.commit_module_edits_btn = QtWidgets.QPushButton("Commit Changes")
        
        # ----------------------------------------------------------
        # add these interfaces to the tab!
        layV_module_editing.addLayout(layH_sel_options)
        layV_module_editing.addLayout(upd_comp_container)
        layV_module_editing.addLayout(self.lay_spacer_funcUI("H"))
        layV_module_editing.addLayout(layH_jnt_ctrl_editing)
        layV_module_editing.addLayout(self.lay_spacer_funcUI("H"))
        layV_module_editing.addWidget(self.commit_module_edits_btn)

        tab.addTab(parent_widget, "Edit Module")

        for spinBox in [self.jnt_num_spinBox, self.ctrl_num_spinBox]:
            spinBox.setMinimum(0)

        # Temporary:
        self.ctrl_type_comboBox.addItem("all")
        self.constraint_type_comboBox.addItem("matrix")
        self.constraint_type_comboBox.addItem("rotate_solver")

        utils_view.assign_style_ls(self.style_tab_1_ui, 
             [self.entire_comp_radioBtn, self.sel_comp_radioBtn, self.selected_module_label,
               self.jnt_num_spinBox, self.ik_operation_comboBox, self.constraint_type_comboBox, 
               self.ctrl_type_comboBox, self.ctrl_num_spinBox, self.commit_module_edits_btn])

    def module_scene_actions_ui(self, widgets_layout):
        layV_module_scene_actions = QtWidgets.QVBoxLayout()

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

        layV_module_scene_actions.addLayout(layH_mdl_delete)
        layV_module_scene_actions.addLayout(layH_mdl_add)

        self.add_mdl_btn.setObjectName("add_mdl_btn")
        self.add_blueprint_btn.setObjectName("add_blueprint_btn")
        self.delete_mdl_btn.setObjectName("remove_mdl_btn")
        self.delete_blueprint_btn.setObjectName("delete_blueprint_btn")
        
        module_scene_actions_container, chk_none = self.cr_container_funcUI("Module Actions", layV_module_scene_actions, True)
    
        widgets_layout.addLayout(module_scene_actions_container)
        
        utils_view.assign_style_ls(self.style_treeview_ui, 
             [self.add_mdl_btn, self.add_blueprint_btn, self.delete_mdl_btn, self.delete_blueprint_btn])
             

    def debugging_ui(self, widgets_layout):
        layH_debugging = QtWidgets.QHBoxLayout()

        # Progress Bar
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Operation Progress")
        layH_debugging.addWidget(self.progress_bar)

        widgets_layout.addLayout(layH_debugging)


    def module_choose_funcUI(self, widgets_layout, mdl_name, side_items):
            mdl_h_layout = QtWidgets.QHBoxLayout()
            
            mdl_checkBox = QtWidgets.QCheckBox()

            mdl_name_label = QtWidgets.QLabel(mdl_name)
            mdl_name_label.setFixedSize(70, 30)
            
            mdl_iterations = QtWidgets.QSpinBox()
            mdl_iterations.setMinimum(1)
            mdl_iterations.setEnabled(False)
            mdl_iterations.setFixedSize(50, 30)
            
            mdl_h_layout.addWidget(mdl_checkBox)
            mdl_h_layout.addWidget(mdl_name_label)
            mdl_h_layout.addWidget(mdl_iterations)
            
            mdl_side = None 
            if side_items != "None":
                mdl_side = QtWidgets.QComboBox()
                mdl_side.addItems(side_items)
                mdl_side.setEnabled(False)
                mdl_h_layout.addWidget(mdl_side)
                mdl_side.setFixedSize(45, 30)
                
            widgets_layout.addLayout(mdl_h_layout)
            
            for widgets in [mdl_name_label, mdl_checkBox, mdl_iterations, mdl_side]:
                widgets.setProperty("treeComponents_UI_01", True)
                
            return mdl_checkBox, mdl_iterations, mdl_side
    

    def set_style_property_funcUI(self):            
        for container in self.style_container:
            container.setProperty("style_container", True)
            container.style().unpolish(container)
            container.style().polish(container)
            container.update()
        for child_container in self.style_child_container:
            child_container.setProperty("style_child_container", True)
            child_container.style().unpolish(child_container)
            child_container.style().polish(child_container)
            child_container.update()
        # add module label style property here
        for widget in self.style_treeview_ui:
            widget.setProperty("treeComponents_UI_01", True)
            
        for mdl_widget in self.style_module_ui_labels:
            mdl_widget.setProperty("treeComponents_UI_01", True)

        for widget in self.style_update_mdl_ui:
            pass
            # widget.setProperty("update_UI", True)

        for widget in self.style_template_ui:
            widget.setProperty("style_template_ui", True)
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()

            #style_lockUnlock_ui
        for widget in self.style_lockUnlock_ui:
            widget.setProperty("style_lockUnlock_ui", True)
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()

        for widget in self.style_tab_1_ui:
            widget.setProperty("style_tab_1_ui", True)
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()


    def cr_container_funcUI(self, label_name, widget_to_add, layout=None, child=None, checkbox=None):
        container = QtWidgets.QWidget()
        container_layV = QtWidgets.QVBoxLayout(container)
        if layout == True:
            container_layV.addLayout(widget_to_add)
        else:
            container_layV.addWidget(widget_to_add)

        # cr label & add to Vlayout to sit above the container 
        container_lbl = QtWidgets.QLabel(label_name)
        parent_container_layV = QtWidgets.QVBoxLayout()

        if checkbox:
            layH_checkboc_lbl = QtWidgets.QHBoxLayout()
            container_chckbox = QtWidgets.QCheckBox()
            container_chckbox.setFixedSize(15, 15)
            # container_chckbox.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

            layH_checkboc_lbl.addWidget(container_chckbox)
            layH_checkboc_lbl.addWidget(container_lbl)
            parent_container_layV.addLayout(layH_checkboc_lbl)
            if child == True:
                self.style_child_container.append(container_chckbox)
            else:
                self.style_container.append(container_chckbox)
        else:
            container_chckbox = None
            parent_container_layV.addWidget(container_lbl)
        parent_container_layV.addWidget(container)
        
        # Set the style to the container
        for widget in [container, container_lbl]:
            if child == True:
                self.style_child_container.append(widget)
            else:
                self.style_container.append(widget)
            widget.setStyleSheet(self.stylesheet)

        return parent_container_layV, container_chckbox
    

    def lay_spacer_funcUI(self, orientation):
        # -- Horizontal Spacer --
        layH_spacer = QtWidgets.QHBoxLayout()
        spacerH = QtWidgets.QWidget()
        if orientation == "H":
            spacerH.setMaximumHeight(1)
            layH_spacer.setContentsMargins(0, 5, 0, 5)  # Left, Top, Right, Bottom
        elif orientation == "V":
            spacerH.setMaximumWidth(1)
            layH_spacer.setContentsMargins(5, 0, 5, 0)
        spacerH.setObjectName("Spacer")
        
        self.style_update_mdl_ui.append(spacerH)
        layH_spacer.addWidget(spacerH)
        
        return layH_spacer
    
    
    def update_component_data(self):
        # -- current_mdl_operations --
        #layV_current_MO_parent = QtWidgets.QVBoxLayout()
        layGrid_update = QtWidgets.QGridLayout()

        self.cmo_lbl = QtWidgets.QLabel("Current >")
        self.cmo_lbl.setObjectName("update_left_lbl")
        self.cmo_rigType_lbl = QtWidgets.QLabel("Rig Type: _ _")
        self.cmo_mirrorMdl_lbl = QtWidgets.QLabel("Mirror: _ _")
        self.cmo_stretch_lbl = QtWidgets.QLabel("Stretch: _ _")
        self.cmo_twist_lbl = QtWidgets.QLabel("Twist: _ _")
                
        umo_lbl = QtWidgets.QLabel("Update >")
        umo_lbl.setObjectName("update_left_lbl")
        umo_rigType_lbl = QtWidgets.QLabel("Rig Type:")
        self.style_update_mdl_ui.append(umo_rigType_lbl)
        self.umo_rigType_comboBox = QtWidgets.QComboBox()
        self.umo_rigType_comboBox.addItems(["FK", "IK", "IKFK"])
        self.umo_mirror_checkBox = QtWidgets.QCheckBox("Mirror")
        self.umo_stretch_checkBox = QtWidgets.QCheckBox("Stretch")
        self.umo_twist_checkBox = QtWidgets.QCheckBox("Twist")
        
        cmo_ls = [self.cmo_lbl, self.cmo_rigType_lbl, self.cmo_mirrorMdl_lbl, self.cmo_stretch_lbl, self.cmo_twist_lbl]
        umd_ls = [umo_lbl, self.umo_rigType_comboBox, self.umo_mirror_checkBox, self.umo_stretch_checkBox, self.umo_twist_checkBox]
        cmo_pos_ls = [[0,0], [0,1], [0,2], [0,3], [0,4]]
        umd_pos_ls = [[1,0], [1,1], [1,2], [1,3], [1,4]]
        for x in range(len(cmo_ls)):
            layGrid_update.addWidget(cmo_ls[x], cmo_pos_ls[x][0], cmo_pos_ls[x][1])
            layGrid_update.addWidget(umd_ls[x], umd_pos_ls[x][0], umd_pos_ls[x][1])
            self.style_update_mdl_ui.append(cmo_ls[x])
            self.style_update_mdl_ui.append(umd_ls[x])

        # layH_upd_mdl_btn = QtWidgets.QHBoxLayout()
        # SpacerGraphic_0_layH = self.lay_spacer_funcUI("H")
        # self.update_btn = QtWidgets.QPushButton("Update Module Data")
        # self.style_update_mdl_ui.append(self.update_btn)

        # SpacerGraphic_1_layH = self.lay_spacer_funcUI("H")
        # layH_upd_mdl_btn.addLayout(SpacerGraphic_0_layH)
        # layH_upd_mdl_btn.addWidget(self.update_btn)
        # layH_upd_mdl_btn.addLayout(SpacerGraphic_1_layH)

        return layGrid_update   

