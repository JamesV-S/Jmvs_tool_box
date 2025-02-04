import os
import json
from pathlib import Path

import maya.cmds as cmds
from maya import OpenMayaUI as omui

class ExportGeometryUUID():
    def __init__(
        self, selected_objects, usd_name, output_dir, json_file_dir):
        self.usd_name = usd_name
        self.output_dir = os.path.normpath(output_dir)
        self.json_file = json_file_dir
        self.selected_objects = selected_objects
        self.custom_uuid_attr = "custom_UUID"
        
        if self.selected_objects:
            self.load_plugin()
            self.export_geo_uuid()
        else:
            print(f"select obj pls")

    def load_plugin(self):
        if not cmds.pluginInfo("mayaUsdPlugin", q=1, loaded=1):
            cmds.loadPlugin("mayaUsdPlugin")

    def export_geo_uuid(self):
        if not os.path.exists(self.output_dir):
            os.makesirs(self.output_dir)

        export_data = {}

        for obj in self.selected_objects:
            # get the UUID for each geo object

            # custom_uuid = cmds.createNode('transform', name='tempNode')
            uuid = cmds.ls(obj, uuid=1)[0]
            #cmds.delete(custom_uuid)

            print(f"{obj} uuid == {uuid}")

            # add attribute to the obj
            # self.store_uuid_as_attribute(obj, uuid)

            # prepare the export data for USD
            export_data[obj] = uuid
        print(f"export_data = {export_data}")

        # export_file_path 
        export_file_path = os.path.join(self.output_dir, f"{self.usd_name}.usd")
        print(f"export_file_path, {export_file_path}")
        cmds.select(self.selected_objects)
        export_arguments = {
            "file": export_file_path,
            "selection": True,
            "defaultMeshScheme": "none",
            "exportVisibility": True,
            "exportUVs": True,
            "shadingMode": "none",
            "staticSingleSample": True,
            "stripNamespaces": True
        }
        cmds.mayaUSDExport(**export_arguments)

        # writing export data to JSON
        with open(self.json_file, 'w') as f:
            json.dump(export_data, f, indent=4)

        print(f"Export completed. Dat saved to {self.json_file}")


def main():
    usd_dir = "E:/My_RIGGING/YR_3/12FOLDSTUDIO_James_SSD/geo_db/exporting_scenes"
    json_file_path = "E:/My_RIGGING/YR_3/12FOLDSTUDIO_James_SSD/geo_db/exporting_scenes/geo_data.json"
    ExportGeometryUUID(usd_dir, json_file_path)

# main()
