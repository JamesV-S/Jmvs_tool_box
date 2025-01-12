
import maya.cmds as cmds

# return a uuid dict
def return_uuid_dict_from_geo(obj_sel):
    # put the uuids into dict. Use `uuid=True` flag in `cmds.ls()`
    uuid_dict = {}
    for name in obj_sel:
        if cmds.objExists(name):
            uuid = cmds.ls(name, uuid=True)[0]
            uuid_dict[name] = uuid
        else:
            print(f"Geo `{name}` doesn't exist")
    print(f"geo: {uuid_dict}")
    return uuid_dict


def return_uuid_dict_from_joint(jnts_sel):
    uuid_dict = {}
    for name in jnts_sel:
        if cmds.objExists(name):
            uuid = cmds.ls(name, uuid=True)[0]
            uuid_dict[name] = uuid
        else:
            print(f"joint `{name}` doesn't exist")
    print(f"jnt: {uuid_dict}")
    return uuid_dict


# return a uuid list
def return_uuid_list_from_geo(obj_sel):
    # put the uuids into list. Use `uuid=True` flag in `cmds.ls()`
    uuid_list = []
    for name in obj_sel:
        if cmds.objExists(name):
            uuid = cmds.ls(name, uuid=True)[0]
            uuid_list.append(uuid)
        else:
            print(f"Geo `{name}` doesn't exist")
    print(f"list {uuid_list}")
    return uuid_list









#------------------------------------------------------------------------------
# UPDATES THE GEO & JOINT NAME of existing UUID dict.
''' Such updates will be passed to the chosen Database's correct row!!! '''
# from the dictionary, ignore the key and select find the uuid in the scene, 
# read the name and update the key of the name if there's a difference
def update_recorded_uuid_geo(uuid_geo_dict):
    updated_dict = {}
    for previous_name, uuid in uuid_geo_dict.items():
        # if the uuid exists in the scene
        geo = cmds.ls(uuid)
        if geo:
            current_name = geo[0]
            # update the dict with the current name as the key
            updated_dict[current_name] = uuid
            if current_name != previous_name:
                print(f"updated prev name `{previous_name}` to `{current_name}` for UUID `{uuid}`")
        else:
            print(f"NO geo found for UUID: `{uuid}`")
    print(f"updated_dict: `{updated_dict}`")
    
    return updated_dict

geo_dict = {'geo_upperarm': 'A77BA8E3-4DBC-2121-CFEA-88AD3F446242', 
            'geo_lowerarm': '0AF4964F-40AC-FAB7-A329-C28F43B224EA', 
            'geo_hand': 'EB05CC29-40CB-1503-0C9C-629BE45E5CF8'}
# updated_geo_dict = update_recorded_uuid_geo(geo_dict)


def update_recorded_uuid_joint(uuid_jnt_dict):
    updated_dict = {}
    for previous_name, uuid in uuid_jnt_dict.items():
        # if the uuid exists in the scene
        jnt = cmds.ls(uuid, type="joint")
        if jnt:
            current_name = jnt[0]
            updated_dict[current_name] = uuid
            if current_name != previous_name:
                print(f"updated prev name `{previous_name}` to `{current_name}` for UUID `{uuid}`")
        else:
            print(f"NO jnt found for UUID: `{uuid}`")
    print(f"updated_dict: `{updated_dict}`")
    
    return updated_dict

joint_dict = {'jnt_skn_0_shoulder_L': '0ADBD31D-4A68-348A-FB5C-A5806EA2ED1F', 
              'jnt_skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134', 
              'jnt_skn_0_wrist_L': 'F0E55702-46CF-4131-30FB-BDBC0E16AAC9'}
# updated_jnt_dict = update_recorded_uuid_joint(joint_dict)

#------------------------------------------------------------------------------
# from 2 dictionary's combine into a single one

def combine_2_dict_into_1(jnt_dict, geo_dict):
        combined_dict = {}
        combined_dict["joint_UUID_dict"] = jnt_dict
        combined_dict["geometry_UUID_dict"] = geo_dict
        print(f"combined_dict = {combined_dict}")
        return combined_dict

# combine_2_dict_into_1(updated_jnt_dict, updated_geo_dict)
''' BUILD THE DATABASE FROM THIS! '''
#------------------------------------------------------------------------------
# Update geo & joint UUID of existing UUID dict. (including the number of jnt or geo!)
# This will change the name & uuid!

# UPDATE W/ NEW SELECTED GEO
''' pretend this dict below is an old version '''
prev_geo_dict = {
    'geo_example_001': 'J77BA8E3-4DBC-2121-CFEA-88AD3F446242', 
    'geo_example_002': 'LW2ND64F-40XC-FAB7-A329-C28F2LS224EA', 
    'geo_example_003': 'H05CC29-40CB-2004-0C9C-6294JD435CF8'
    }

def replace_geo_uuid(current_geo_uuid_dict):
    print(f"before update: {current_geo_uuid_dict}")
    new_geo_sel = cmds.ls(sl=1, type="transform")
    
    # cr new dict w/ the UUIDS of the selected geos
    new_uuid_dict = return_uuid_dict_from_geo(new_geo_sel)

    # update the current dict with the new UUIDS
    current_geo_uuid_dict.clear()
    current_geo_uuid_dict.update(new_uuid_dict)

    print(f"after updated dict: `{current_geo_uuid_dict}`")
    return current_geo_uuid_dict
    
# replace_geo_uuid(prev_geo_dict)

# UPDATE W/ NEW SELECTED JOINTS!
prev_jnt_dict = {
    'jnt_example_001': 'J77BA8E3-74GF-2121-CFEA-88AD3F446242', 
    'jnt_example_002': 'LW2ND64F-40XC-FAB7-A329-C28F2LS224EA', 
    'jnt_example_003': 'H05CC29-40CB-2004-0C9C-6294JD435CF8'
    }
def replace_jnt_uuid(current_jnt_uuid_dict):
    print(f"before update: {current_jnt_uuid_dict}")
    new_jnt_sel = cmds.ls(sl=1, type="joint")
    
    # cr new dict w/ the UUIDS of the selected geos
    new_uuid_dict = return_uuid_dict_from_joint(new_jnt_sel)

    # update the current dict with the new UUIDS
    current_jnt_uuid_dict.clear()
    current_jnt_uuid_dict.update(new_uuid_dict)

    print(f"after updated dict: `{current_jnt_uuid_dict}`")
    return current_jnt_uuid_dict
    
# replace_jnt_uuid(prev_jnt_dict)

#------------------------------------------------------------------------------
