
import maya.cmds as cmds

# bind from 2 nested dictionary's
combined_dict = {
    'joint_UUID_dict': {
        'skn_0_shoulder_L': '0ADBD31D-4A68-348A-FB5C-A5806EA2ED1F', 
        'skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134', 
        'skn_0_wrist_L': 'F0E55702-46CF-4131-30FB-BDBC0E16AAC9'
        }, 
    'geometry_UUID_dict': {
        'skn_geo_upperarm': 'A77BA8E3-4DBC-2121-CFEA-88AD3F446242', 
        'skn_geo_lowerarm': '0AF4964F-40AC-FAB7-A329-C28F43B224EA', 
        'skn_geo_hand': 'EB05CC29-40CB-1503-0C9C-629BE45E5CF8'
        }
    }
''' 
def old_bind_skin_from_combined_dict(combined_dict):
    # unpack the nested dict
    jnt_uuid_dict = combined_dict["joint_UUID_dict"]
    geo_uuid_dict = combined_dict["geometry_UUID_dict"]

    all_bound = True
    jnt_list = []
    geo_list = []
    for jnt_name, jnt_uuid in jnt_uuid_dict.items():
        jnt = cmds.ls(jnt_uuid, type="joint")
        jnt_list.append(jnt[0])
    for geo_name, geo_uuid in geo_uuid_dict.items():
        geo = cmds.ls(geo_uuid, type="transform")
        geo_list.append(geo[0])

    print(f"jnt = {jnt_list} & geo = {geo_list}")
    
    for jnt, geo in zip(jnt_list, geo_list):   
        if not jnt or not geo:
            print(f"joint or geometry UUID doesn't exist: `{jnt_uuid}` & `{geo_uuid}`")
            continue
        skn_clus = cmds.ls(cmds.listHistory(geo), type='skinCluster')
        try:
            if skn_clus:
                existing_jnt_influence = cmds.skinCluster( skn_clus[0], q=1, inf=1 )
                if jnt[0] not in existing_jnt_influence:
                    cmds.skinCluster(skn_clus[0], edit=True, unbind=True)
                    cmds.skinCluster(jnt, geo, tsb=True, wd=1)
                    print(f"binded skin: geo `{geo}`, to jnt `{jnt}`")
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
#old_bind_skin_from_combined_dict(combined_dict)
#------------------------------------------------------------------------------

# bind from 2 seperate dicts
jnt_uuid_dict = {
        'skn_0_shoulder_L': '0ADBD31D-4A68-348A-FB5C-A5806EA2ED1F', 
        'skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134', 
        'skn_0_wrist_L': 'F0E55702-46CF-4131-30FB-BDBC0E16AAC9'
        }

geo_uuid_dict = {'skn_geo_upperarm': 'A77BA8E3-4DBC-2121-CFEA-88AD3F446242', 
            'skn_geo_lowerarm': '0AF4964F-40AC-FAB7-A329-C28F43B224EA', 
            'skn_geo_hand': 'EB05CC29-40CB-1503-0C9C-629BE45E5CF8'}

#------------------------------------------------------------------------------
# this function is the meat of skin binding, handling errors and pre existing skinclusters!
def bind_joints_to_geos(jnt_list, geo_list):
    all_bound = True
    for geo in geo_list:   
        skn_clus = cmds.ls(cmds.listHistory(geo), type='skinCluster')
        try: # # handle attempting to bind a jnts that's alr influencing the geo
            if skn_clus:
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
    jnt_list = []
    geo_list = []
    for jnt_name, jnt_uuid in jnt_uuid_dict.items():
        jnt = cmds.ls(jnt_uuid, type="joint")
        if jnt:
            jnt_list.append(jnt[0])
    for geo_name, geo_uuid in geo_uuid_dict.items():
        geo = cmds.ls(geo_uuid, type="transform")
        if geo:
            geo_list.append(geo[0])

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
# bind_skin_from_2_dicts(jnt_uuid_dict, geo_uuid_dict)

#------------------------------------------------------------------------------
# Testing diff number of geos with diff number of joints.

oneJNT_for_multiGEO_combined_dict = {
    'joint_UUID_dict': {'jnt_skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134'}, 
    'geometry_UUID_dict': {'geo_1': '946C0344-4B43-4E3E-E610-33AEFC6A76D2', 
          'geo_2': 'BC1BBC88-49E0-705C-3B5E-89B24C670722', 
          'geo_3': '2AD65DAA-4F33-E185-634E-B7A81D073E31'}
    }

multiJNT_for_oneGEO_combined_dict = {
    'joint_UUID_dict': {
        'skn_0_shoulder_L': '0ADBD31D-4A68-348A-FB5C-A5806EA2ED1F', 
        'skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134', 
        'skn_0_wrist_L': 'F0E55702-46CF-4131-30FB-BDBC0E16AAC9'
    }, 
    'geometry_UUID_dict': {'geo_4': 'BB3DD158-422F-3966-C861-7C8E8FA7F144'}
    }

oneJNT_for_oneGEO_combined_dict = {
    'joint_UUID_dict': {
        'skn_0_shoulder_L': '0ADBD31D-4A68-348A-FB5C-A5806EA2ED1F', 
        'skn_0_elbow_L': '02E77D75-4DB2-4ECF-EF09-93B6F13E1134', 
        'skn_0_wrist_L': 'F0E55702-46CF-4131-30FB-BDBC0E16AAC9'
        }, 
    'geometry_UUID_dict': {
        'skn_geo_upperarm': 'A77BA8E3-4DBC-2121-CFEA-88AD3F446242', 
        'skn_geo_lowerarm': '0AF4964F-40AC-FAB7-A329-C28F43B224EA', 
        'skn_geo_hand': 'EB05CC29-40CB-1503-0C9C-629BE45E5CF8'
        }
    }

def bind_skin_from_combined_dict(combined_dict):
    # unpack the nested dict
    jnt_uuid_dict = combined_dict["joint_UUID_dict"]
    geo_uuid_dict = combined_dict["geometry_UUID_dict"]

    jnt_list = []
    geo_list = []
    for jnt_name, jnt_uuid in jnt_uuid_dict.items():
        jnt = cmds.ls(jnt_uuid, type="joint")
        if jnt:
            jnt_list.append(jnt[0])
    for geo_name, geo_uuid in geo_uuid_dict.items():
        geo = cmds.ls(geo_uuid, type="transform")
        if geo:
            geo_list.append(geo[0])

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


bind_skin_from_combined_dict(oneJNT_for_multiGEO_combined_dict)
bind_skin_from_combined_dict(multiJNT_for_oneGEO_combined_dict)
bind_skin_from_combined_dict(oneJNT_for_oneGEO_combined_dict)


''' READ THE DATABASE TO SKIN! So gather the combined dixtinary
 from each row and and create skin with button(5) '''
#------------------------------------------------------------------------------



