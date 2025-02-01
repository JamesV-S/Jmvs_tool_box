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
> Adding jnts & geo to active db
->-> `Add Geo button` needs to work in tandem with `new relationship`, and: 
    # A - when can the geo be added? 
            # A = once the joint had been selected in the treeview Ui 
                # OR
                # new relationship has been created, the joint from this is it's partner
- skiining buttons working
>>> Skinning 'ALL' from treeView/database buttons, (doesn't interact with treeView visually), 
    gathers combined dictionary's from them for skinning functions
>>> Skinning 'spcific' from treeView/database buttons, (interacts with treeView selection!), 
    gathers combined dictionary's from them for skinning functions
- change how treeview row's work
>> Change the way the treeviews are displayed. 
    - joint_A(in jnt treeview) > corresponding geo parented under 
    joint_A(in geo treeview) even if it's one to one relationship. 
    - Will help user readablity. 
> Add geo selected in scene to the row of the Joint selected in the treeview.
>> adjust treeView selection relationship!
> abloe to remove joint from relationship 
> Can now add joint
> Able to add joint properly (without overwriting) to 
selected relationship parent & also remove (delete) 
relationship row from database!

NEXT:
> delete database, stop it being locked by Maya - (Don't need for submission!)
> Replace jnt/geo on selected row in treeview - (Don't need for submission!)
