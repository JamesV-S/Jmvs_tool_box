# ------------------------------ MODEL ----------------------------------------
import importlib
import os.path

from utils import (
    utils
)

from usd_exports.systems import func_import_geometry_UUID_usd
from utils import utils_os

class ImportGeoUsdModel:
    def __init__(self):
        self.usd_file = ""
        self.json_directory = ""

    def import_geo_uuid(self):
        print(f"usd_file = {self.usd_file}, json_directory = {self.json_directory}" )
        func_import_geometry_UUID_usd.ImporttGeometryUUID(
            usd_file=self.usd_file, json_file=self.json_directory
            )