import os
import json
from pathlib import Path

import maya.cmds as cmds
from maya import OpenMayaUI as omui

class ImporttGeometryUUID():
    def __init__(self, usd_file, json_file):
        self.custom_UUID = "custom_UUID"
        self.usd_file = usd_file
        self.json_file = json_file
        self.import_data = self.load_json()
        self.load_plugin()
        self.import_geo_uuid()


    def load_plugin(self):
        if not cmds.pluginInfo("mayaUsdPlugin", q=1, loaded=1):
            cmds.loadPlugin("mayaUsdPlugin")


    def load_json(self):
        with open(self.json_file, 'r') as f:
            return json.load(f)


    def import_geo_uuid(self):
        cmds.file(self.usd_file, i=1, type='USD Import', ignoreVersion=True, 
                  ra=True, mergeNamespacesOnClash=False, namespace=":", options=";")
        
        for obj, uuid in self.import_data.items():
            if cmds.objExists(obj):
                self.store_uuid_as_attribute(obj, uuid)
        print("Import completed and custom attributes reassigned.")

    
    def store_uuid_as_attribute(self, obj, uuid):
        if not cmds.attributeQuery(self.custom_UUID, node=obj, exists=True):
            print(f"adding custom atribute '{uuid}' to geo: '{obj}'")
            cmds.addAttr(obj, longName=self.custom_UUID, dataType='string')
            cmds.setAttr(f"{obj}.{self.custom_UUID}", str(uuid), type='string')
        else:
            # is existing uuid the same as collected one?
            existing_cstm_uuid = cmds.getAttr(f"{obj}.{self.custom_UUID}")
            same_uuid = uuid == existing_cstm_uuid
            if not same_uuid:
                cmds.setAttr(f"{obj}.{self.custom_UUID}", str(uuid), type='string')
                updated_cstm_uuid = cmds.getAttr(f"{obj}.{self.custom_UUID}")
                print(f"updated_cstm_uuid = {updated_cstm_uuid}")
            else:
                print(f"Skip the {obj} custom attribute")
        try:
            cmds.setAttr(f"{obj}.{self.custom_UUID}", l=1)
        except:
            pass

def main():
    usd_file = "E:/My_RIGGING/YR_3/12FOLDSTUDIO_James_SSD/geo_db/exporting_scenes/exported_objects_001.usd"
    json_file_path = "E:/My_RIGGING/YR_3/12FOLDSTUDIO_James_SSD/geo_db/exporting_scenes/geo_data.json"
    ImporttGeometryUUID(usd_file, json_file_path)

# main()
