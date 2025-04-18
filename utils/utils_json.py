
import os
import json
from utils import (
    utils_os
)

def get_modules_json_dict(config_folder):
    # derive the `self.json_all_mdl_list` from the config folder!
    # self.json_all_mdl_list = ['biped_arm.json', 'biped_leg.json']
    json_mdl_list = []
    json_config_dir = utils_os.create_directory("Jmvs_tool_box", "config", config_folder)# "char_config")
    if os.path.exists(json_config_dir):
        for mdl_config_file in os.listdir(json_config_dir):
            if mdl_config_file.endswith('.json'):
                json_mdl_list.append(mdl_config_file)
    
    # This dictionary contains nested dict of all possible json modules in `char_config` folder
    json_dict = {}
    for json_file in json_mdl_list:
        # configer the json file
        json_path = os.path.join(json_config_dir, json_file)
        with open(json_path, 'r') as file:
            # load the json data
            json_data = json.load(file)
            json_dict[json_file] = json_data
    return json_dict