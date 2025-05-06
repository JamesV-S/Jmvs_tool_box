import maya.cmds as cmds

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


def layV_SPACER_func():
        layH_spacer = QtWidgets.QHBoxLayout()
        spacer = QtWidgets.QWidget()
        spacer.setFixedSize(100,10)
        spacer.setObjectName("Spacer")
        layH_spacer.addWidget(spacer)

        return layH_spacer


def delete_existing_ui(ui_name):
    print(f"ui_name to delete = {ui_name}")
    if cmds.window(ui_name, exists=True):
        cmds.deleteUI(ui_name, window=True)


def get_component_name_TreeSel(tree_view, tree_model):
    # get selection model of all items in the treeView
    selection_model = tree_view.selectionModel()
    selected_indexes = selection_model.selectedIndexes()

    # is there an item to be selected?
    if selected_indexes:
        multi_selection = selected_indexes
        module_item = []
        module_selection_list = []
        for index in multi_selection:
            item = tree_model.itemFromIndex(index)
            name = item.text()
            print(f"Name in for loop = {name}")
            module_item.append(item)
            module_selection_list.append(name)
        print(f"treeview selection list: {module_selection_list}")
        return module_selection_list
    

def set_button_size(btn_list, fixed_val_01, fixed_val_02):
     for buttons in btn_list:
        buttons.setFixedSize(fixed_val_01, fixed_val_02)
        buttons.setMinimumSize(fixed_val_01, fixed_val_02)
        buttons.setIconSize(QtCore.QSize(fixed_val_01, fixed_val_02))  # Explicitly set icon size to button size
        buttons.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)


def assign_style_ls(style, ls):
    for widgets in ls:
            style.append(widgets)