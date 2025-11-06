try:
    from PySide6 import QtCore, QtWidgets, QtGui
except ModuleNotFoundError:
    from PySide2 import QtCore, QtWidgets, QtGui


def util_o_thru_items(parent_item):
    # collect items by going thru the tree 
    module_item_list = []
    for row in range(parent_item.rowCount()):
        child_item = parent_item.child(row)
        # check it's the right item
        if child_item.text().startswith("mdl_"):
            module_item_list.append(child_item.text())
        module_item_list.extend(util_o_thru_items(child_item))
    
    return module_item_list


def util_find_item_by_name(parent_item, name):
    # recursivly search for an item with the given name starting from "parent_item"
    for row in range(parent_item.rowCount()):
        child_item = parent_item.child(row)
        if child_item.text() == name:
            return child_item
        result = util_find_item_by_name(child_item,name)
        if result:
            return result


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
            module_item.append(item)
            module_selection_list.append(name)
        return module_selection_list


def get_all_component_name_in_TreeView(tree_model):
    # get selection model of all items in the treeView
    root_item = tree_model.invisibleRootItem()
    module_item_list = util_o_thru_items(root_item)
    return module_item_list


def get_components_of_selected_module(tree_model, module_name):
    root_item = tree_model.invisibleRootItem()
    # find the parent item with the given name
    parent_item = util_find_item_by_name(root_item, module_name)
    if parent_item:
        print(f"GOT IT")
        return util_o_thru_items(parent_item)
    else:
        print(f"NOTHING")
        return []


def get_module_name_TreeSel(tree_view, tree_model):
    # get selection model of all items in the treeView
    selection_model = tree_view.selectionModel()
    selected_indexes = selection_model.selectedIndexes()

    # is there an item to be selected?
    if selected_indexes:
        multi_selection = selected_indexes
        parent_selection_list = []
        for index in multi_selection:
            item = tree_model.itemFromIndex(index)
        
            # Check if this is a root/parent item (no parent)
            if item.parent() is None:
                name = item.text()
                parent_selection_list.append(name)
        
        return parent_selection_list
    
    return []  # Return empty list if no selection
