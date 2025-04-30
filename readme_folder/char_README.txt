# Jmvs_tool_box\\char_rig

>> Can now succesfully pass data to database and guides in my scene.
Achieved:
        create db & visualise in the treeview
Next:
        write funvtions & classes to create guides & controls!

''' 
method of unpacking nested dict struture 'self.json_dict' 
containing each json files's content under its filename as a key.
Step 1 - dictionary & items
`.items()` method that returns a view object that displays a list
of the dict's key-value tuple pairs(step 2)

Step 2 - unpacking, using 'filename' + 'data' is tuple unpacking
for each itemreturned by step 1, is a tuple containing a key(filename) 
and its corresponding value(data).

Step 3 - Loop execution
thru each iteratipon, filename(key), and data(value) which is the 
associated dictionary.
'''
ACHIEVED: 
> made progress on new spine guides

NEXT:
> add ddj joints to new spine guides!
> add controls to new spine guides, based off of the ddg joints!
> add orientation aim control for each component!