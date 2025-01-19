
import maya.cmds as cmds
import importlib
import sys
import os

from systems import (
    os_custom_directory_utils,
    utils
)
importlib.reload(os_custom_directory_utils)
importlib.reload(utils)

class CreateXfmGuides():
    def __init__(self, database_componment_dict):
        # 1) write an example dictionary to pass to this to make it work, then 
        # 2) write funtions in `char_ui` to gather necessary data from database, 
        # based off the selection in the ui!
        '''
        database_componment_dict = {
            "module_name":"bipedArm", 
            "unique_id":0,
            "side":"L", 
            "component_pos":{'clavicle': [3.9705319404602006, 230.650634765625, 2.762230157852166], 
                            'shoulder': [28.9705319404602, 230.650634765625, 2.762230157852166], 
                            'elbow': [49.96195602416994, 192.91743469238278, -8.43144416809082], 
                            'wrist': [72.36534118652347, 164.23757934570304, 15.064828872680739]}                
            }
        '''
        print(f"crerating guide component for {database_componment_dict}")
        # self.component_pos_dict = {} 
        #for value in database_componment_dict.values():
        self.module_name = database_componment_dict['module_name']
        self.unique_id = database_componment_dict['unique_id']
        self.side = database_componment_dict['side']
        self.component_pos_dict = database_componment_dict['component_pos']

        print(f"Working on `self.module_name`: {self.module_name}, `self.unique_id`: {self.unique_id}, `self.side`: {self.side}, `self.component_pos_dict`:{self.component_pos_dict}")
        '''
        Working on `self.module_name`: bipedArm, `self.unique_id`: 0, `self.side`: L, `self.component_pos_dict`:{'clavicle': [3.9705319404602006, 230.650634765625, 2.762230157852166], 'shoulder': [25.234529495239258, 225.57975769042972, -12.279715538024915], 'elbow': [49.96195602416994, 192.91743469238278, -8.43144416809082], 'wrist': [72.36534118652347, 164.23757934570304, 15.064828872680739]}
        '''
        self.build_components(self.module_name, self.unique_id, self.side, self.component_pos_dict)
       
    def build_components(self, module_name, unique_id, side, component_pos):
        guide_import_dir =  os.path.join(os_custom_directory_utils.create_directory("Jmvs_tool_box", "imports" ), "imp_component_guide.abc")# 
        
        # import the guide & distribbute it to all necessary guides!    
        guides = []
        for key, pos in component_pos.items():
            imported_guide = cmds.file(guide_import_dir, i=1, ns="component_guide", rnn=1)
            guide_name = f"xfm_guide_{unique_id}_{module_name}_{key}_{side}"
            guides.append(cmds.rename(imported_guide[0], guide_name))
            cmds.xform(guide_name, translation=pos, worldSpace=1)        

        for x in range(len(guides)):
            try:
                cmds.setAttr(f"{guides[x]}.overrideEnabled", 1)
                cmds.setAttr(f"{guides[x]}.overrideColor", 25)
                # PARENTING THE GUIDES IS TEMPORARY!
                cmds.parent(guides[x+1], guides[x])
                utils.connect_guide(guides[x], guides[x+1])
            except:
                pass
        
        # NOT PERMANANT reference the joints! > make UI control this!
        cmds.select("ddj_*")
        clusters = cmds.ls(selection=True)
        print(clusters)
        for x in clusters:
            cmds.setAttr(f"{x}.overrideEnabled", 1)
            cmds.setAttr(f"{x}.overrideDisplayType", 1)
        cmds.select(cl=1)

        print(f"imported_guide = {imported_guide[0]}")
        



        
        # establish the things I need 
        # Arg: I would like a dictionary with:
            # module, uniqueID, side & part of the mdl/component it's matching to.
        # guide name = "xfm_guide_uniqueID*_mdl*_part*_side*"

        # do I want this function to work on a single dict for mdl/component at a time 
        # or pass a dictionary that contains all.
        # if its a single component then i just need to call it through a loop 
        # allowing for "add_module button". ANS = single dict component at a time 

        # I want the selection of the tree view to dictate the compnents to add.
        # if a component already exists then pass and move on, don't error!

        