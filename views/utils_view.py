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


def delete_existing_ui(ui_name):
    # print(f"Deleting ui window = {ui_name}")
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


def layV_SPACER_func():
        layH_spacer = QtWidgets.QHBoxLayout()
        spacer = QtWidgets.QWidget()
        spacer.setFixedSize(100,10)
        spacer.setObjectName("Spacer")
        layH_spacer.addWidget(spacer)

        return layH_spacer


def assign_style_ls(style, ls):
    for widgets in ls:
            style.append(widgets)


def add_to_main_lay(main_lay, layout_list):
    for layout in layout_list:
        main_lay.addLayout(layout)


def set_container_style_ls(style_ls, style_child_ls):
    '''
    # Description:
        Set the property of the `normal container style sheet` & 
        `child container style sheet`.
    # Attributes:
        style_ls (list): style_list to be set so a consistent style 
                        for the normal container option is applied.
        style_child_ls (list): style_list to be set so a consistent style 
                                for the child container's is applied.
    # Returns: N/A 
    '''   
    for container in style_ls:
        container.setProperty("style_container", True)
        container.style().unpolish(container)
        container.style().polish(container)
        container.update()
    for child_container in style_child_ls:
        child_container.setProperty("style_child_container", True)
        child_container.style().unpolish(child_container)
        child_container.style().polish(child_container)
        child_container.update()


# def cr_container_ui(label_name, widget_to_add, style_sheet, style_ls, style_child_ls,
#                      layout=None, child=None, checkbox=None):
#         '''
#         # Description:
#             Builds a consistent Container layout design. 
#         # Attributes:
#             label_name (string): Visible name of this contianer.
#             widget_to_add (Widget): Layout or Widget that contains all the ui widgets 
#                                         I want going i this container.
#             style_sheet (CSS): Style_sheet file.
#             style_ls (list): style_list to be set so a consistent style 
#                               for the normal container option is applied.
#             style_child_ls (list): style_list to be set so a consistent style 
#                                     for the child container's is set.
#             layout (bool): 'True' if `widget_to_add` is a Layout.
#             child (bool): 'True' if container should have a child stylesheet applied. 
#             checkbox (bool): 'True' if container should have a checkbox attached to it. 
#         # Returns: 
#             widget_container_layV (QVBoxLayout()): Top level Layout inside the 
#                                                     container to house 
#                                                     `widget_to_add`.
#             container_chckbox (QCheckBox/None): QCheckBox if `checkbox` == True, 
#                                                 ootherwie return None. 
#         '''   
#         container = QtWidgets.QWidget()
#         container_layV = QtWidgets.QVBoxLayout(container)
#         if layout == True:
#             container_layV.addLayout(widget_to_add)
#         else:
#             container_layV.addWidget(widget_to_add)

#         # cr label & add to Vlayout to sit above the container 
#         container_lbl = QtWidgets.QLabel(label_name)
#         widget_container_layV = QtWidgets.QVBoxLayout()

#         if checkbox:
#             layH_checkboc_lbl = QtWidgets.QHBoxLayout()
#             container_chckbox = QtWidgets.QCheckBox()
#             container_chckbox.setFixedSize(15, 15)
#             # container_chckbox.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

#             layH_checkboc_lbl.addWidget(container_chckbox)
#             layH_checkboc_lbl.addWidget(container_lbl)
#             widget_container_layV.addLayout(layH_checkboc_lbl)
#             if child == True:
#                 style_child_ls.append(container_chckbox)
#             else:
#                 style_ls.append(container_chckbox)
#         else:
#             container_chckbox = None
#             widget_container_layV.addWidget(container_lbl)
#         widget_container_layV.addWidget(container)
        
#         # Set the style to the container
#         for widget in [container, container_lbl]:
#             if child == True:
#                 style_child_ls.append(widget)
#             else:
#                 style_ls.append(widget)
#             widget.setStyleSheet(style_sheet)

#         return widget_container_layV, container_chckbox


# def new_cr_container_ui(label_name, widget_to_add, style_sheet, style_ls, style_child_ls,
#                      min_width=None, min_height=None, 
#                      max_width=None, max_height=None,
#                      fixed_width=None, fixed_height=None,
#                      layout=None, child=None, checkbox=None):
#         '''
#         # Description:
#             Builds a consistent Container layout design w/ size constraints. 
#         # Attributes:
#             label_name (string): Visible name of this contianer.
#             widget_to_add (Widget): Layout or Widget that contains all the ui widgets 
#                                         I want going i this container.
#             style_sheet (CSS): Style_sheet file.
#             style_ls (list): style_list to be set so a consistent style 
#                               for the normal container option is applied.
#             style_child_ls (list): style_list to be set so a consistent style 
#                                     for the child container's is set.
#             min_width, min_height (int): Minimum size constraints
#             max_width, max_height (int): Maximum size constraints
#             fixed_width, fixed_height (int): Fixed size constraints              
#             layout (bool): 'True' if `widget_to_add` is a Layout.
#             child (bool): 'True' if container should have a child stylesheet applied. 
#             checkbox (bool): 'True' if container should have a checkbox attached to it. 
#         # Returns: 
#             widget_container_layV (QVBoxLayout()): Top level Layout inside the 
#                                                     container to house 
#                                                     `widget_to_add`.
#             container_chckbox (QCheckBox/None): QCheckBox if `checkbox` == True, 
#                                                 ootherwie return None. 
#         '''   


#         # cr label & add to Vlayout to sit above the container 
#         widget_container_layV = QtWidgets.QVBoxLayout()

#         container_lbl = QtWidgets.QLabel(label_name)
#         container_widget = QtWidgets.QWidget()
#         container_layV = QtWidgets.QVBoxLayout(container_widget)
#         # Set the size constraint of the constinaer's layout
#         container_layV.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        
#         print(f"*VIEW: `layout` = {layout} ")
#         if layout == True:
#             container_layV.addLayout(widget_to_add)
#         else:
#             container_layV.addWidget(widget_to_add)

#         if checkbox:
#             layH_checkboc_lbl = QtWidgets.QHBoxLayout()
#             container_chckbox = QtWidgets.QCheckBox()
#             container_chckbox.setFixedSize(15, 15)
#             layH_checkboc_lbl.addWidget(container_chckbox)
#             layH_checkboc_lbl.addWidget(container_lbl)
#             widget_container_layV.addLayout(layH_checkboc_lbl)
#             if child == True:
#                 style_child_ls.append(container_chckbox)
#             else:
#                 style_ls.append(container_chckbox)
#         else:
#             container_chckbox = None
#             widget_container_layV.addWidget(container_lbl)
#         widget_container_layV.addWidget(container_widget)
        
#         # Set the style to the container
#         for widget in [container_widget, container_lbl]:
#             if child == True:
#                 style_child_ls.append(widget)
#             else:
#                 style_ls.append(widget)
#             widget.setStyleSheet(style_sheet)

#         # size constraints: 
#         if min_width is not None or min_height is not None:
#             container_widget.setMinimumSize(min_width or 0, min_height or 0)

#         if max_width is not None or max_height is not None: # Qt default max = 16777215
#             container_widget.setMaximumSize(max_width or 16777215, max_height or 16777215)

#         if fixed_width is not None and fixed_height is not None:
#             container_widget.setFixedSize(fixed_width, fixed_height)
#         elif fixed_width is not None:
#             container_widget.setFixedWidth(fixed_width)
#         elif fixed_height is not None:
#             container_widget.setFixedHeight(fixed_height)


#         return widget_container_layV, container_chckbox



def test_cr_container_ui(label_name, widget_to_add, style_sheet, style_ls, style_child_ls,
                     min_width=None, min_height=None, 
                     max_width=None, max_height=None,
                     layout=None, child=None, checkbox=None):
    '''
    # Description:
        Builds a consistent Container layout design w/ size constraints. 
    '''   
    # Create a main wrapper widget that will hold everything
    main_layV = QtWidgets.QVBoxLayout()
    # Create a main wrapper widget that will hold everything
    main_label = QtWidgets.QLabel(label_name)
    main_wrapper_widget = QtWidgets.QWidget()
    
    # Create your layout structure inside this wrapper widget
    widget_container_layV = QtWidgets.QVBoxLayout(main_wrapper_widget)
    
    print(f"*VIEW: `layout` = {layout} ")
    if layout == True:
        widget_container_layV.addLayout(widget_to_add)
    else:
        widget_container_layV.addWidget(widget_to_add)

    if checkbox:
        layH_checkbox_lbl = QtWidgets.QHBoxLayout()
        container_chckbox = QtWidgets.QCheckBox()
        container_chckbox.setFixedSize(15, 15)
        layH_checkbox_lbl.addWidget(container_chckbox)
        # layH_checkbox_lbl.addWidget(container_lbl)
        widget_container_layV.addLayout(layH_checkbox_lbl)
        if child == True:
            style_child_ls.append(container_chckbox)
        else:
            style_ls.append(container_chckbox)
    else:
        container_chckbox = None
        main_layV.addWidget(main_label)
    
    main_layV.addWidget(main_wrapper_widget)
    
    # Set the style to the container
    for widget in [main_label, main_wrapper_widget]:# [container_widget, container_lbl, main_wrapper_widget]:
        if child == True:
            style_child_ls.append(widget)
        else:
            style_ls.append(widget)
        widget.setStyleSheet(style_sheet)

    # Apply size constraints to the CONTAINER WIDGET (red background)
    if min_width is not None or min_height is not None:
        # container_widget.setMinimumSize(min_width or 0, min_height or 0)
        main_wrapper_widget.setMinimumSize(min_width or 0, min_height or 0)

    if max_width is not None or max_height is not None:
        # container_widget.setMaximumSize(max_width or 16777215, max_height or 16777215)
        main_wrapper_widget.setMaximumSize(max_width or 16777215, max_height or 16777215)

    main_wrapper_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)


    # Return the wrapper widget instead of the layout
    return main_layV, container_chckbox