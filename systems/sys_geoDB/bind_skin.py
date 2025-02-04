
import maya.cmds as cmds

custom_UUID = "custom_UUID"

def search_geometry_in_scene():
    shape_nodes = cmds.ls(dag=1, type='mesh')
    if shape_nodes:
        print(shape_nodes)
        all_geo = []
        for shape in shape_nodes:
            transform = cmds.listRelatives(shape, parent=1, type='transform')[0]
            all_geo.append(transform)
        return all_geo

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
def bind_skin_from_2_dicts(jnt_uuid_dict, geo_uuid_dict):
    print(f"RUNNING 'bind_skin_from_2_dicts'")
    jnt_list = []
    geo_list = []
    for jnt_name, jnt_uuid in jnt_uuid_dict.items():
        jnt = cmds.ls(jnt_uuid, type="joint")
        if jnt:
            jnt_list.append(jnt[0])
    
    all_geo = search_geometry_in_scene()
    for geo_name, geo_uuid in geo_uuid_dict.items():
        for geo in all_geo:
            if cmds.attributeQuery(custom_UUID, node=geo, exists=True):
                attr_value = cmds.getAttr(f"{geo}.{custom_UUID}", asString=1)
                print(f"attr_value = {attr_value}")
                if attr_value == geo_uuid:
                    print("OMG THEY MATCH!!!!")
                    geo_list.append(geo)
                else:
                    print("NOT A MATCH")
            else:
                print("no object has custom attr")
    
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
    '''
    for jnt, geo in zip(jnt_list, geo_list):   
        if not jnt or not geo:
            print(f"joint or geometry UUID doesn't exist: `{jnt_uuid}` & `{geo_uuid}`")
            continue

        # determine if the geo already has a skincluster and whether the joint is already an influence
        skn_clus = cmds.ls(cmds.listHistory(geo), type='skinCluster')
        
        # handle runtime eroors, attempting to bind a joints that's already influencing the geo
        try:
            if skn_clus:
                existing_jnt_influence = cmds.skinCluster( skn_clus[0], q=1, inf=1 )
                if jnt[0] not in existing_jnt_influence:
                    cmds.skinCluster(skn_clus[0], edit=True, unbind=True)
                    cmds.skinCluster(jnt, geo, tsb=True, wd=1)
                    print(f"binded skin: geo `{geo}`, to jnt `{jnt}`")
                    # set 'all_bound' to False cus not all joints r bound
                    all_bound = False
                else: 
                    print(f"existing influence `{jnt_name}` is already skinned to {geo_name} with existing skincluster")
            else:
                cmds.skinCluster(jnt, geo, tsb=True, wd=1)
                print(f"binded skin: geo `{geo}`, to jnt `{jnt}`")
                all_bound = False
        except RuntimeError as e:
            print(f"RuntimeError: in bind_skin {e}")
    
    if all_bound:
        print(f"All bind joints r already skinned to the geometry with skincluster")
    '''

#------------------------------------------------------------------------------
def bind_skin_from_combined_dict(combined_dict):
    print(f"******** RUNNING 'bind_skin_from_combined_dict'")
    # unpack the nested dict
    jnt_uuid_dict = combined_dict["joint_UUID_dict"]
    geo_uuid_dict = combined_dict["geometry_UUID_dict"]

    jnt_list = []
    geo_list = []
    for jnt_name, jnt_uuid in jnt_uuid_dict.items():
        jnt = cmds.ls(jnt_uuid, type="joint")
        if jnt:
            jnt_list.append(jnt[0])

    all_geo = search_geometry_in_scene()
    for geo_name, geo_uuid in geo_uuid_dict.items():
        for geo in all_geo:
            if cmds.attributeQuery(custom_UUID, node=geo, exists=True):
                attr_value = cmds.getAttr(f"{geo}.{custom_UUID}", asString=1)
                print(f"attr_value = {attr_value}")
                if attr_value == geo_uuid:
                    print("OMG THEY MATCH!!!!")
                    geo_list.append(geo)
                else:
                    print("NOT A MATCH")
            else:
                print("no object has custom attr")

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