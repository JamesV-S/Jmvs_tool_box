
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


def unbindSkin_by_uuid_dict(geo_uuid_dict):
    print(f"RUNNING ``unbindSkin_by_uuid_dict``")
    all_geo = search_geometry_in_scene()
    for name, uuid in geo_uuid_dict.items():
        for geo in all_geo:
            if cmds.attributeQuery(custom_UUID, node=geo, exists=True):
                attr_value = cmds.getAttr(f"{geo}.{custom_UUID}", asString=1)
                print(f"attr_value = {attr_value}")
                if attr_value == uuid:
                    if geo:
                        skn_clus = cmds.ls(cmds.listHistory(geo), type='skinCluster')
                        if skn_clus:
                            for skin in skn_clus:
                                cmds.skinCluster(skin, edit=True, unbind=True)
                                print(f"Unbinded skin from geometry {geo}, with UUID: {uuid}")
                        else:
                            print(f"transform geo `{geo}` has no skincluster to unbind")
                    else:
                        print(f"Geo with UUID `{uuid}` does NOT exist")
                else:
                    print("NOT A MATCH")
            else:
                print("no object has custom attr")

    '''
    for name, uuid in geo_uuid_dict.items():
       
        geo = cmds.ls(uuid, type="transform")
        if geo:
            skn_clus = cmds.ls(cmds.listHistory(geo), type='skinCluster')
            if skn_clus:
                for skin in skn_clus:
                    cmds.skinCluster(skin, edit=True, unbind=True)
                    print(f"Unbinded skin from geometry {geo}, with UUID: {uuid}")
            else:
                print(f"transform geo `{geo}` has no skincluster to unbind")
        else:
            print(f"Geo with UUID `{uuid}` does NOT exist")
    '''

'''
geo_uuid_dict = {'geo_upperarm': 'A77BA8E3-4DBC-2121-CFEA-88AD3F446242', 
            'geo_lowerarm': '0AF4964F-40AC-FAB7-A329-C28F43B224EA', 
            'geo_hand': 'EB05CC29-40CB-1503-0C9C-629BE45E5CF8'}
unbindSkin_by_uuid_dict(geo_uuid_dict)
'''

def unbindSkin_by_uuid_list(geo_ls):
    for geo in geo_ls:
        skn_clus = cmds.ls(cmds.listHistory(geo), type='skinCluster')
        if skn_clus:
            cmds.skinCluster(skn_clus[0], edit=True, unbind=True)
        else:
            print(f"transform geo `{geo}` has no skincluster to unbind")
