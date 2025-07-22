# Jmvs_tool_box\\char_rig

Backing up orientation config data incase I want to use in the future:
bipedArm : {"system_rot_xyz":{
            "clavicle": [-7.698626118758961, 34.531672095102785, -13.412947865931349], 
            "shoulder": [7.042431639335459, -5.366417614476926, -52.87199475566795], 
            "elbow": [3.4123575630188263, -32.847391136978814, -52.004681579832734], 
            "wrist": [3.4123575630188263, -32.847391136978814, -52.004681579832734]
        }}

bipedLeg : {"system_rot_xyz": {
            "hip": [-0.206856730062026, 0.4367008200374581, -86.43419733389054],
            "knee": [-0.20685673006202596, 0.43670082003745814, -86.43419733389054],
            "ankle": [0.5942622188475634, -59.55357811140123, -90.0],
            "ball": [-89.85408725528224, -89.99999999999997, 0.0],
            "toe": [-89.85408725528225, -89.99999999999997, 0.0]
        }}

head : {"system_rot_xyz": {
            "neck0": [0.0, 240, 90.0], 
            "neck1": [0.0, 250, 90.0], 
            "neck2": [0.0, 260, 90.0],
            "neck3": [0.0, 260, 90.0]
        }}

neck : {"system_rot_xyz": {
            "neck0": [0.0, 240, 90.0], 
            "neck1": [0.0, 250, 90.0], 
            "neck2": [0.0, 260, 90.0],
            "neck3": [0.0, 270, 90.0],
            "neck4": [0.0, 280, 90.0]
        }}

bipedLeg : {"system_rot_xyz": {
            "hip": [0.0, -1.6180766381813425, -90.03391613228942],
            "knee": [0.0, 51.1435387994787, -90.03391613228945],
            "calf": [0.0, -3.717444687739824, -90.03391613228942],
            "ankle": [0.0, -3.717444687739824, -90.03391613228942]
        }}

spine : {"system_rot_xyz": {
            "spine0": [0.0, -7.947513469078512, 90.00000000000001],
            "spine1": [-1.9890093469260345e-16, -1.959155005957633, 90.00000000000001],
            "spine2": [0.0, 9.706246313394262, 90.00000000000001],
            "spine3": [-8.171859705486283e-16, 13.339396285991443, 90.0],
            "spine4": [-7.814945266275812e-14, -9.271752801444176, 89.99999999999991]
        }}

tail : {"system_rot_xyz": {
            "tail0": [0.0, 240, 90.0],
            "tail1": [0.0, 250, 90.0],
            "tail2": [0.0, 260, 90.0],
            "tail3": [0.0, 270, 90.0],
            "tail4": [0.0, 280, 90.0]
        }}
 

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