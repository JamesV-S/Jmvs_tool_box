# ------------------------------ Controller -----------------------------------

import maya.cmds as cmds
from maya import OpenMayaUI

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

import importlib
import os.path

from systems import (
    os_custom_directory_utils,
    utils
)

from systems.sys_char_rig import (
    cr_guides, 
    cr_ctrl
)

from controllers import utils_QTree

from models.char_models import char_layout_model
from views.char_views import char_layout_view

importlib.reload(os_custom_directory_utils)
importlib.reload(utils)
importlib.reload(utils_QTree)
importlib.reload(cr_guides)
importlib.reload(cr_ctrl)
importlib.reload(char_layout_model)
importlib.reload(char_layout_view)

class CharLayoutController:
    def __init__(self): # class
        self.model = char_layout_model.CharLayoutModel()
        self.view = char_layout_view.CharLayoutView()
        
        self.user_module_data = {}

        # Connect signals and slots
        # -- visualise database --
        self.view.rpl_live_component.clicked.connect(self.sigFunc_rpl_live_component)

        # ------------ choose modules ------------
        self.view.available_rig_comboBox.currentIndexChanged.connect(self.sigFunc_availableRigComboBox)

        for mdl in self.view.mdl_choose_ui_dict:
            # unpack the elements of the dict containing the widgets dynamically built.  
            mdl_checkBox, mdl_iteration, mdl_side = self.view.mdl_choose_ui_dict[mdl]
            # create lambda functions to connect signals to slots with additional `mdl` argument
            mdl_checkBox.stateChanged.connect(lambda _, name=mdl: self.sigFunc_mdl_checkBox(name))
            mdl_iteration.valueChanged.connect(lambda _, name=mdl: self.sigFunc_mdl_IterationSpinBox(name))
            mdl_side.currentIndexChanged.connect(lambda _, name=mdl: self.sigFunc_mdl_SideCombobox(name))
        
        self.view.publish_btn.clicked.connect(self.sigfunc_publish_btn)
        # -- add blueprints --
        self.view.add_mdl_btn.clicked.connect(self.sigfunc_add_module)
        self.view.add_blueprint_btn.clicked.connect(self.sigfunc_add_blueprint)

        # ------------ component editing ------------
        # ---- Template Display ----
        self.view.guide_template_checkBox.stateChanged.connect(self.sigFunc_guide_template_checkBox)
        self.view.controls_template_checkBox.stateChanged.connect(self.sigFunc_controls_template_checkBox)
        self.view.ddj_template_checkBox.stateChanged.connect(self.sigFunc_ddj_template_checkBox)
        # ---- Lock/Unlock ----
        self.view.compnent_checkBox.stateChanged.connect(self.sigFunc_compnent_checkBox)
        self.view.lock_btn.clicked.connect(self.sigFunc_lock_btn)
        self.view.unlock_btn.clicked.connect(self.sigFunc_unlock_btn)
    

    def sigFunc_rpl_live_component(self):
        # print selection in ui:
        component_selection = utils_QTree.get_component_name_TreeSel(self.view.mdl_tree_view , self.view.mdl_tree_model)
        for component in component_selection:
            self.model.record_component_change(component)

    
    # ------------ siFunc Choose modules functions ------------
    def sigFunc_availableRigComboBox(self):
        self.val_availableRigComboBox = self.view.available_rig_comboBox.currentText()
        tree_name = self.val_availableRigComboBox.replace("DB_", "")
        self.view.tree_view_name_lbl.setText(f"Database: `{tree_name}`")
        self.model.visualise_active_db(self.view.val_availableRigComboBox, self.view.mdl_tree_model)
        print(f"available rig chosen: `{self.val_availableRigComboBox}`")


    # define the 3 widget functions appropriatly, taking the `mdl_name` arg from lambda!
    def sigFunc_mdl_checkBox(self, mdl_name):
        mdl_checkBox = self.view.mdl_choose_ui_dict[mdl_name][0]
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
            self.view.mdl_choose_ui_dict[mdl_name][1].setEnabled(True)
            if mdl_name == "spine" or mdl_name == "root":
                pass
            else:
                self.view.mdl_choose_ui_dict[mdl_name][2].setEnabled(True)
        else:
            self.view.mdl_choose_ui_dict[mdl_name][1].setEnabled(False)             
            self.view.mdl_choose_ui_dict[mdl_name][2].setEnabled(False)
        print(f"MDL::{mdl_name} &  self.val_mdl_checkBox::{self.val_mdl_checkBox}")
    
    def sigFunc_mdl_IterationSpinBox(self, mdl_name):
        mdl_iteration = self.view.mdl_choose_ui_dict[mdl_name][1]
        if mdl_name == "root":
            mdl_iteration.setMinimum(1)
            mdl_iteration.setMaximum(1)
        self.val_mdl_iteration = mdl_iteration.value()
        
        # add the remaining iteration widget signal
        self.user_module_data[mdl_name]["mdl_iteration"] = self.val_mdl_iteration

        print(f"MDL::{mdl_name} &  self.val_mdl_checkBox::{self.val_mdl_iteration}")

    def sigFunc_mdl_SideCombobox(self, mdl_name):
        mdl_side = self.view.mdl_choose_ui_dict[mdl_name][2]
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
            self.model.cr_mdl_json_database(mdl, self.view.val_availableRigComboBox, signals['mdl_checkBox'], signals['mdl_iteration'], signals['mdl_side'])
            self.model.visualise_active_db(self.view.val_availableRigComboBox, self.view.mdl_tree_model)
        
    
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
                    mdl_component_dict = self.model.retrieve_component_dict_from_nameSel(self.view.val_availableRigComboBox, selection)
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
            self.view.controls_template_checkBox.setChecked(False)
            self.view.ddj_template_checkBox.setChecked(False)
            self.view.controls_template_checkBox.setChecked(True)
            self.view.ddj_template_checkBox.setChecked(True)


    def sigfunc_add_module(self):
        self.model.load_rig_group(self.view.val_availableRigComboBox)
        print(f"What is mdl_choose_ui_dict? == {self.view.mdl_choose_ui_dict}") # output = {}
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
        component_selection = utils_QTree.get_component_name_TreeSel(self.view.mdl_tree_view , self.view.mdl_tree_model)
        print(f"YAAAAAH component_selection = {component_selection[0]}")
        self.func_createXfmGuides(component_selection)

        self.model.func_unlocked_all()
        
        
    def sigfunc_add_blueprint(self):
        self.model.load_rig_group(self.view.val_availableRigComboBox)
        # connect signals for module editor buttons
        for mdl, (checkBox, iterations, side) in self.view.mdl_choose_ui_dict.items():
            if checkBox.isChecked(): # checkbox is the master 
                # access the input from iterations and side
                iterations_value = iterations.value()
                side_value = side.currentText() if side else None
                print(f"Adding blueprint for {mdl}: Iterations={iterations_value}, Side={side_value}")
        
        component_selection = utils_QTree.get_all_component_name_in_TreeView(self.view.mdl_tree_model)
        self.func_createXfmGuides(component_selection)

        self.model.func_unlocked_all()


    # ---- Template Components! ----
    def sigFunc_guide_template_checkBox(self):
        self.val_guide_template_checkBox = self.view.guide_template_checkBox.isChecked()
        utils.select_set_displayType("xfm_guide_*", self.val_guide_template_checkBox, False)


    def sigFunc_controls_template_checkBox(self):
        self.val_controls_template_checkBox = self.view.controls_template_checkBox.isChecked()
        utils.select_set_displayType("ctrl_*", self.val_controls_template_checkBox, False)


    def sigFunc_ddj_template_checkBox(self):
        self.val_ddj_template_checkBox = self.view.ddj_template_checkBox.isChecked()
        utils.select_set_displayType("ddj_*", self.val_ddj_template_checkBox, False)
    
    # --- Unlocked component configuration ---
    def sigFunc_compnent_checkBox(self):
        self.val_compnent_checkBox = self.view.compnent_checkBox.isChecked()

    def sigFunc_lock_btn(self):
        if self.val_compnent_checkBox: #true
            component_selection = utils_QTree.get_component_name_TreeSel(self.view.mdl_tree_view , self.view.mdl_tree_model)
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
            component_selection = utils_QTree.get_component_name_TreeSel(self.view.mdl_tree_view , self.view.mdl_tree_model)
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
                self.model.constrain_guides_from_comp(unlock_rdy_component) 
        else: print(f"component checkbox is not checked")



    