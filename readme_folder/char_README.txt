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

'''BELOW is not a utility, it's the order of constraint relationship of components'''
def unlocked_component():
    # guide > parentOperation > guideGROUP
    if "bipedLeg":
        print("bipedLeg unlocked configuration")
        if cmds.objExists("spine_module"):
            pass
            # spine1 >PointConAll> hip
        # Hip >PointConAll> knee
        # knee > Nothing
        if cmds.objExists("root_module"):
            pass
            # root >ParentCon_Y_> ankle
            # root >PointtConAll> foot
        # foot >PointConX_Z> ankle
        # foot >ParentConAll> ball
        # foot >ParentConAll> toe
    elif "bipedArm":
        print("bipedArm unlocked configuration")
        if cmds.objExists("spine_module"):
            pass
            # spine4 >ParentConAll> clavicle
            # spine4 >ParentConAll> shoulder
    elif "root":
        print("root unlocked configuration")
        # root >PointtConAll> cog
    elif "spine":
        print("spine unlocked configuration")
        # cog >ParentConAll> spine1
        # spine1 >ParentConAll> spine2
        # spine2 >ParentConAll> spine3
        # spine3 >ParentConAll> spine4
        # spine4 >ParentConAll> spine5