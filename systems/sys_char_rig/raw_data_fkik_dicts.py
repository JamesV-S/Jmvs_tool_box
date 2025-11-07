
import importlib
import maya.cmds as cmds
from utils import (
    utils
)

importlib.reload(utils)

'''
import importlib
from Jmvs_tool_box.systems.sys_char_rig import raw_data_fkik_dicts

importlib.reload(raw_data_fkik_dicts)
'''

class RawDataFkIKDicts():
    def __init__(self, fk_control_dict, ik_control_dict, 
                 component_pos, component_rot,
                 constant_name_dict):
        '''
        # Description:

        # Arguments:
            fk_control_dict (dict): key = fk_*module_*bone : value = ctrl type
            ik_control_dict (dict): key = ik_*module_*bone : value = ctrl type
            component_pos (dict): key = *bone name : value = pos data
            component_rot (dict): key = *bone name : value = rot data
            constant_name_dict (dict): key = attr name : value = 'bone name'/ or / 'false'
        # Return:
        '''
        self.fk_control_dict = fk_control_dict
        self.ik_control_dict = ik_control_dict
        self.component_pos = component_pos
        self.component_rot = component_rot
        self.limbRoot_name = constant_name_dict['limbRoot_name']
        self.hock_name = constant_name_dict['hock_name']
        self.ik_wld_name = constant_name_dict['ik_wld_name']

        self.get_fk_pos()
        self.get_fk_rot()
        self.get_ik_pos()
        self.get_ik_rot()
        

    def get_fk_pos(self):
        '''
        # method: 
            for a , b:
                try:
                    if b in a:
                        run
        args needed:
            FK_Ctrls keys
            skel_pos values
        '''
        fk_pos = {}      
        for (fk_name), (comp_name, comp_pos) in zip(self.fk_control_dict.keys(), 
                                                    self.component_pos.items()):
            try:
                if comp_name in fk_name:
                    fk_pos[fk_name] = comp_pos
            except:
                pass
        
        return fk_pos


    def get_fk_rot(self):
        '''
        args needed:
            FK_Ctrls keys
            skel_ values
        '''
        fk_rot = {}      
        for (fk_name), (comp_name, comp_rot) in zip(self.fk_control_dict.keys(), 
                                                    self.component_rot.items()):
            try:
                if comp_name in fk_name:
                    fk_rot[fk_name] = comp_rot
            except:
                pass
        
        return fk_rot


    def get_ik_pos(self):
        '''
        args needed:
            IK_Ctrls keys
            if IK_Ctrls value has 'pv' -> store that key as pv
                pv ctrl pos = utils.return_pv_transforms.
            all other pos = skel_pos values

        '''
        pv_pos, pv_rot = self.return_pv_pos_rot()
        ik_pos = {}      
        for (ik_name, ik_type), (comp_name, comp_pos) in zip(self.ik_control_dict.items(), 
                                                    self.component_pos.items()):
            try:
                if comp_name in ik_name:
                    if ik_type == "pv":
                        ik_pos[ik_name] = pv_pos
                    else:
                        ik_pos[ik_name] = comp_pos
            except:
                pass

        return ik_pos


    def get_ik_rot(self):
        '''
        args needed:
            rot keys:
                IK_Ctrls keys
                if IK_Ctrls value has 'pv' -> store that key as pv
                    pv ctrl rot = utils.return_pv_transforms.
            rot values:
                if 'limbRoot':
                    iterate through to find name & give:
                        value = [0.0, 0.0, 0.0]
                elif 'ik_wld_ori:'
                    iterate through to find name & give:
                        value = [0.0, y.y, 0.0]
                        # How can I get the orientation data for the world ori?
                        = the orientation of the corresponding guide.
                elif 'hock_name:'
                    iterate through to find name & give:
                        same as 
                        value = [0.0, y.y, 0.0]

            all other rot = skel_pos values

        '''
        pv_pos, pv_rot = self.return_pv_pos_rot()
        ik_rot = {}      
        for (ik_name, ik_type), (comp_name, comp_rot) in zip(self.ik_control_dict.items(), 
                                                    self.component_rot.items()):
            try:
                if comp_name in ik_name:
                    if ik_type == "pv":
                        ik_rot[ik_name] = pv_rot
                    # Need elif for the constant attributes! (each one if true, should differ from the component rot!)
                        # limbRoot_name
                        # hock_name
                        # ik_wld_name
                    else:
                        ik_rot[ik_name] = comp_rot
            except:
                pass

        print(ik_rot)

        return ik_rot
    

    def return_pv_pos_rot(self):
        # get component.key name for pv .value()
        pv_comp_name = []

        # get pv before & after component key names.
            # get corresponding component key names to the ik_pos names.
        comp_key_list = []
        for (ik_name, ik_type ), (comp_name, comp_pos) in zip(self.ik_control_dict.items(), 
                                                    self.component_pos.items()):
            try:
                if comp_name in ik_name:
                    comp_key_list.append(comp_name)
                    if ik_type == "pv":
                        pv_comp_name.append(comp_name)
            except: pass

            # get the before & after component names for pv.
        pv_before_after_comp_names = []
        for i, (key, value) in enumerate(self.ik_control_dict.items()):
            if value == 'pv':
                before_pv = comp_key_list[i-1] if i > 0 else None
                after_pv = comp_key_list[i+1] if i < len(comp_key_list)-1 else None
                pv_before_after_comp_names.append(before_pv)
                pv_before_after_comp_names.append(after_pv)

        # get the pv rot & pos
        pv_pos, pv_rot = utils.get_pv_pos_rot(self.component_pos[pv_before_after_comp_names[0]], 
                                              self.component_pos[pv_comp_name[0]],
                                              self.component_pos[pv_before_after_comp_names[1]])
        return pv_pos, pv_rot


# bipedArm Example:
fk_control_dict = {
    "fk_bipedArm_clavicle": "circle", 
    "fk_bipedArm_shoulder": "circle", 
    "fk_bipedArm_elbow": "circle", 
    "fk_bipedArm_wrist": "circle"}
ik_control_dict = {"ik_bipedArm_clavicle": "cube", "ik_bipedArm_shoulder": "cube", "ik_bipedArm_elbow": "pv", "ik_bipedArm_wrist": "cube"}
component_pos = {
    "clavicle": [3.9705319404602006, 230.650634765625, 2.762230157852166], 
    "shoulder": [28.9705319404602, 230.650634765625, 2.762230157852166], 
    "elbow": [53.69795846939088, 197.98831176757807, 6.61050152778626], 
    "wrist": [76.10134363174441, 169.30845642089832, 30.106774568557817]
    }
component_rot = {
    "clavicle": [0.0, 0.0, 0.0], 
    "shoulder": [7.042431639335366, -5.366417614476933, -52.87199475566796], 
    "elbow": [7.04243163933536, -32.847391136978864, -52.004681579832805], 
    "wrist": [7.04243163933536, -32.847391136978864, -52.004681579832805]
    }
constant_name_dict = {
    "limbRoot_name": "shoulder",
    "hock_name": False,
    "ik_wld_name": False}
RawDataFkIKDicts(fk_control_dict, ik_control_dict, component_pos, component_rot, constant_name_dict)

print(f"_____________________________________________________________________")

# quadLeg Example:
q_fk_control_dict = {
    "fk_quadLeg_hip": "circle", 
    "fk_quadLeg_knee": "circle", 
    "fk_quadLeg_calf": "circle", 
    "fk_quadLeg_ankle": "circle", 
    "fk_quadLeg_ball": "circle"
    }
q_ik_control_dict = {
    "ik_quadLeg_hip": "prism", 
    "ik_quadLeg_knee": "pv", 
    "ik_quadLeg_calf": "cube", 
    "ik_quadLeg_ankle": "cube"
    }
q_component_pos = {
    "hip": [8.600740644769745, 73.17778605595966, -43.86647675361294], 
    "knee": [8.60074064476974, 44.674795207918336, -32.37837552488726], 
    "calf": [8.60074064476974, 20.335971998048286, -47.07023669736204], 
    "ankle": [8.60074064476974, 5.737959787060513, -44.06889043484146], 
    "ball": [8.60074064476974, 5.737959787060513, -36.88480178040549], 
    "end": [8.60074064476974, 0.0982447548243588, -31.29348682927134]
    }
q_component_rot = {
    "hip": [90.36876231144643, -22.272743030153656, -90.00000000000001], 
    "knee": [-269.21385274254095, 31.115786848297205, -90.51623725561545], 
    "calf": [86.65319955869097, -11.616952223402183, -90.81454127018628], 
    "ankle": [2.1503500636142685, -90.0, 0.0], 
    "ball": [91.43634844111682, -44.75308558410996, -90.00000000000009], 
    "end": [91.43634844111682, -44.75308558410996, -90.00000000000009]
    }
q_constant_name_dict = {
    "limbRoot_name": "hip",
    "hock_name": "calf",
    "ik_wld_name": "ankle"}
RawDataFkIKDicts(q_fk_control_dict, q_ik_control_dict, q_component_pos, q_component_rot, q_constant_name_dict)
