
import maya.cmds as cmds

custom_UUID = "custom_UUID"

#------------------------------------------------------------------------------
# this function is the meat of skin binding, handling errors and pre existing skinclusters!
def bind_joints_to_geos(jnt_list, geo_list):
    all_bound = True
    for geo in geo_list:   
        skn_clus = cmds.ls(cmds.listHistory(geo), type='skinCluster')
        print(f"skin_cluster")
        try: # # handle attempting to bind a jnts that's alr influencing the geo
            if skn_clus:
                print(f"ZZ SkinCluster is True")
                existing_jnt_influence = cmds.skinCluster( skn_clus[0], q=1, inf=1 )
                for jnt in jnt_list:
                    if jnt not in existing_jnt_influence:
                        cmds.skinCluster(skn_clus[0], edit=1, addInfluence=jnt, wt=0)
                        print(f"Added influence `{jnt}` to geo `{geo}`")
                        all_bound = False
            else:
                cmds.skinCluster(jnt_list, geo, tsb=True, wd=1)
                print(f"binded skin: geo `{geo}`, to jnt `{jnt_list}`")
                all_bound = False
        except RuntimeError as e:
            print(f"RuntimeError: in bind_skin {e}")
    
    if all_bound:
        print(f"All bind joints r already skinned to the geometry with skincluster")


#------------------------------------------------------------------------------
def bind_search_geometry_in_scene():
    shape_nodes = cmds.ls(dag=1, type='mesh')
    all_geo = []

    if shape_nodes:
        transforms = cmds.listRelatives(shape_nodes, parent=True, type='transform', fullPath=True)
        all_geo = list(set(transforms))  # Remove duplicates if any

    return all_geo

#------------------------------------------------------------------------------
def bind_skin_from_2_dicts(jnt_uuid_dict, geo_uuid_dict):
    print(f"RUNNING 'bind_skin_from_2_dicts'")
    jnt_list = [cmds.ls(jnt_uuid, type="joint")[0] for jnt_name, jnt_uuid in 
                jnt_uuid_dict.items() if cmds.ls(jnt_uuid, type="joint")]
    
    all_geo = bind_search_geometry_in_scene()
    geo_uuid_map = {}
    for geo in all_geo:
        if cmds.attributeQuery(custom_UUID, node=geo, exists=True):
            attr_value = cmds.getAttr(f"{geo}.{custom_UUID}", asString=1)
            geo_uuid_map[attr_value] = geo 
    
    geo_list = [geo_uuid_map[geo_uuid] for geo_name, geo_uuid in geo_uuid_dict.items() if geo_uuid in geo_uuid_map]

    # determine the bining strategy!!!
    if len(jnt_list) == len(geo_list):
        # One-to-one corresponding between joints and geos
        for jnt, geo in zip(jnt_list, geo_list):
            bind_joints_to_geos([jnt], [geo])
    elif len(jnt_list) == 1 :
        # One joint to multiple geometries
        for geo in geo_list:
            bind_joints_to_geos(jnt_list, [geo])
    elif len(geo_list) == 1:
        # Multiple joints to one geometry
        bind_joints_to_geos(jnt_list, geo_list)
    else:
        print("Unsupported configuration.")

#------------------------------------------------------------------------------
def bind_skin_from_combined_dict(combined_dict):
    print(f"******** RUNNING 'bind_skin_from_combined_dict'")
    # unpack the nested dict
    jnt_uuid_dict = combined_dict["joint_UUID_dict"]
    geo_uuid_dict = combined_dict["geometry_UUID_dict"]

    jnt_list = [cmds.ls(jnt_uuid, type="joint")[0] for jnt_name, jnt_uuid in 
                jnt_uuid_dict.items() if cmds.ls(jnt_uuid, type="joint")]
    
    all_geo = bind_search_geometry_in_scene()
    geo_uuid_map = {}
    for geo in all_geo:
        if cmds.attributeQuery(custom_UUID, node=geo, exists=True):
            attr_value = cmds.getAttr(f"{geo}.{custom_UUID}", asString=1)
            geo_uuid_map[attr_value] = geo 
    
    geo_list = [geo_uuid_map[geo_uuid] for geo_name, geo_uuid in geo_uuid_dict.items() if geo_uuid in geo_uuid_map]

    # determine the binding strategy!!!
    if len(jnt_list) == len(geo_list):
        # One-to-one corresponding between joints and geos
        for jnt, geo in zip(jnt_list, geo_list):
            bind_joints_to_geos([jnt], [geo])
    elif len(jnt_list) == 1 :
        # One joint to multiple geometries
        for geo in geo_list:
            bind_joints_to_geos(jnt_list, [geo])
    elif len(geo_list) == 1:
        # Multiple joints to one geometry
        bind_joints_to_geos(jnt_list, geo_list)
    else:
        print("Unsupported relationship configuration.")