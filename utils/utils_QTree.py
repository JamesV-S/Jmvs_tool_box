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


def get_qListView_comp_sel(list_view, list_model):
    selection_model = list_view.selectionModel()
    selected_indexes = selection_model.selectedIndexes()

    # is there an item to be selected?
    if selected_indexes:
        multi_selection = selected_indexes
        parent_selection_list = []

        for index in multi_selection:
            item = list_model.itemFromIndex(index)
            parent_selection_list.addItem()
    
    print()

def get_items_in_Qlist(Qlist_model):
    '''
    Docstring for on_QlistView_clicked
    # Description: 
        Put all the names of items currently in the Qlist. 
    # Return: 
        item_ls (list): Names of all items in the Qlist.
    '''
    model = Qlist_model
    item_ls = []
    for row in range(model.rowCount()):
        index = model.index(row, 0)
        item = model.data(index)
        if item is not None:
            item_ls.append(item)
    return item_ls



def get_current_selected_item_Qlist(view_Qlist, view_Qlist_model):
    # Get the selection model from the QListView
    # selection_model = self.view.comp_inp_hk_mtx_Qlist.selectionModel()
    selection_model = view_Qlist.selectionModel()
    
    # Get the current selected indexes
    selected_indexes = selection_model.selectedIndexes()
    
    if selected_indexes:
        # Get the first selected item (assuming single selection mode)
        selected_index = selected_indexes[0]
        
        # Get the model and data
        # model = self.view.comp_inp_hk_mtx_Qlist_Model
        model = view_Qlist_model
        item_txt = model.data(selected_index)
        
        print(f"*Currently selected item: {item_txt}")
        return item_txt
    
    return None


def populate_ext_inp_hk_mtx_atrComboBox_model(view_prim, view_scnd):
        # This method should either:
        # 1. Set up state of the attribute combobox
        # For now, just clear it or set default state
        view_prim.clear()
        view_scnd.clear()
        view_prim.setPlaceholderText("Primary Atr")
        view_scnd.setPlaceholderText("Secondary Atr")
        view_prim.addItem('None')
        view_scnd.addItem('None')