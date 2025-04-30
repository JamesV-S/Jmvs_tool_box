import pymel.core as pmc

# Rewriting code for composability
''' function to filter root joints ''' 
def is_root_joint(obj):
    return obj.type() == 'joint' and obj.getParent() is None
all_roots = [o for o in pmc.ls() if is_root_joint(o)]
# new_roots = [o for o in cmds.importFile("some_file_path") if is_root_joint(o)]

# getting the first item in a sequence
''' function to filter root joints '''

import maya.cmds as cmds

# cmds.ls(getP)