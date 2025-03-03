# ------------------------------ MODEL ----------------------------------------
import importlib
import os.path

from systems import (
    os_custom_directory_utils,
    utils
)

from usd_exports.systems import func_import_geometry_UUID_usd

class ImportGeoUsdModel:
    def __init__(self):
        self.usd_file = ""
        self.json_directory = ""

    def import_geo_uuid(self):
        print(f"usd_file = {self.usd_file}, json_directory = {self.json_directory}" )
        func_import_geometry_UUID_usd.ImporttGeometryUUID(
            usd_file=self.usd_file, json_file=self.json_directory
            )