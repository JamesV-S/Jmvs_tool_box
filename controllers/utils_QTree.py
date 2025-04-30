

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
        

def get_all_component_name_in_TreeView(tree_model):
        # get selection model of all items in the treeView
        module_item_list = []
        def go_thru_items(parent_item):
            # collect items by goiun thru the tree 
            for row in range(parent_item.rowCount()):
                child_item = parent_item.child(row)
                # check it's the right item
                if child_item.text().startswith("mdl_"):
                    module_item_list.append(child_item.text())
                go_thru_items(child_item)
        root_item = tree_model.invisibleRootItem()
        go_thru_items(root_item)
        print(f"All items with 'mdl' in treeView = {module_item_list}")
        return module_item_list
        
