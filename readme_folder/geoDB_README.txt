# Jmvs_tool_box\\char_rig

>> Can now succesfully:
-> How to make sure I can delete the database while Maya is open, and not make 
maya lock the file, as it should automatically have a closed connection with 
`with sqlite3.connect(db_name) as conn`
-> Then get -- Available Databases -- dynamicalkly adding all the geo databses 
working & the treeview show the chosen one!
>> Visualising Tree View due to drop down selection (active)!
Achieved: 
->  new relationship checkbox works well
-> Add Joint button works in tandem with new relationship. 

NEXT:
> Adding jnts & geo to active
    Next: 
    -> `Add Geo button` needs to work in tandem with `new relationship`, and: 
    # A - when can the geo be added? 
            # A = once the joint had been selected in the treeview Ui 
                # OR
                # new relationship has been created, the joint from this is it's partner
            # B - The Joint either selected in treeview OR partner relationship(dictated by `self.val_new_relationship_checkBox`), 
                # needs its row queried so geo can be added to the right one! 

> Replace jnt/geo on selected row in treeview
> Remove Row from treeview & database button!
>> Skinning from treeView/database
> delete database, stop it being locked by Maya - (Don't need for submission!)

