# -------------------------------------- MODEL ------------------------------------------
# models/database_model.py
import importlib
from databases.geo_databases import database_schema_001

importlib.reload(database_schema_001)

class exportDatabaseModel:
    def __init__(self):
        self.file_name = ""
        self.directory = ""

    def create_database(self):
        database_schema_001.CreateDatabase(name=self.file_name, directory=self.directory)
