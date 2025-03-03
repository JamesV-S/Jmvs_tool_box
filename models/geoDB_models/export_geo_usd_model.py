# ------------------------------ MODEL ----------------------------------------
import importlib

from usd_exports.systems import func_export_geometry_UUID_usd
importlib.reload(func_export_geometry_UUID_usd)

class ExportGeoUsdModel:
    def __init__(self):
        self.selected_objects = ""
        self.usd_name = ""
        self.usd_save_dir = ""
        self.json_dir = ""


    def export_geo_uuid(self):
        func_export_geometry_UUID_usd.ExportGeometryUUID(
                selected_objects=self.selected_objects, 
                usd_name=self.usd_name, output_dir=self.usd_save_dir, 
                json_file_dir=self.json_dir
                )