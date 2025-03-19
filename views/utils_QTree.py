

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
        

