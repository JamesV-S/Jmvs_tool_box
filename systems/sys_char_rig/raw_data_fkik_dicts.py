
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
                 constant_attr_dict,
                 unique_id, side):
        '''
        # Description:
            Create 4 dicts, 2 for each fk & ik. Each of those 2 being Pos & Rot data.
                Must ONLY be used when getting default data when creating database.
                Must ONLY be used when updating datbase data when using char_layout.
                Must NOT use when retrieving the data from the database for raw_data.
        # Arguments:
            fk_control_dict (dict): key = fk_*module_*bone : value = ctrl type
            ik_control_dict (dict): key = ik_*module_*bone : value = ctrl type
            component_pos (dict): key = *bone name : value = pos data
            component_rot (dict): key = *bone name : value = rot data
            constant_attr_dict (dict): key = attr name : value = 'bone name'/ or / 'false'
        # Return:
            fk_pos, fk_rot, ik_pos, ik_rot
        '''
        self.fk_control_dict = fk_control_dict
        self.ik_control_dict = ik_control_dict
        self.component_pos = component_pos
        self.component_rot = component_rot
        self.limbRoot_name = constant_attr_dict['limbRoot_name']
        self.hock_name = constant_attr_dict['hock_name']
        self.ik_wld_name = constant_attr_dict['ik_wld_name']
        self.unique_id, self.side = unique_id, side

        self.fk_pos = self.get_fk_pos()
        self.fk_rot = self.get_fk_rot()
        self.ik_pos = self.get_ik_pos()
        self.ik_rot = self.get_ik_rot()
        

    def get_fk_pos(self):
        '''
        # Description:
            Create the 'fk_pos' dictionary from 'self.fk_control_dict' & 
            'self.component_pos'. Assigning keys with the former & its values with 
            the latter.
        # Arguments: N/A
        # Return:
            fk_pos(dict): keys = fk_*module_*bone : values = pos data. 
        '''
        fk_pos = {}      
        for (fk_name), (comp_name, comp_pos) in zip(self.fk_control_dict.keys(), 
                                                    self.component_pos.items()):
            try:
                if comp_name in fk_name:
                    fk_pos[fk_name] = comp_pos
            except:
                pass

        print(f"fk_pos = {fk_pos}")
        
        return fk_pos


    def get_fk_rot(self):
        '''
        # Description:
            Create the 'fk_rot' dictionary from 'self.fk_control_dict' & 
            'self.component_rot'. Assigning keys with the former & its values with 
            the latter.
        # Arguments: N/A
        # Return:
            fk_rot(dict): keys = fk_*module_*bone : values = rot data. 
        '''
        fk_rot = {}      
        for (fk_name), (comp_name, comp_rot) in zip(self.fk_control_dict.keys(), 
                                                    self.component_rot.items()):
            try:
                if comp_name in fk_name:
                    fk_rot[fk_name] = comp_rot
            except:
                pass
        
        print(f"fk_rot = {fk_rot}")


        return fk_rot


    def get_ik_pos(self):
        '''
        # Description:
            Create the 'ik_pos' dictionary from 'self.ik_control_dict' & 
            'self.component_pos'. Assigning keys with the former & its values with 
            the latter. 
            IF pv type in 'self.ik_control_dict': set unique pos value,
            else set remaining items pos value.
        # Arguments: N/A
        # Return:
            ik_pos(dict): keys = ik_*module_*bone : values = rot data. 
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

        print(f"ik_pos = {ik_pos}")

        return ik_pos


    def get_ik_rot(self):
        '''
        # Description:
            Create the 'ik_rot' dictionary from 'self.ik_control_dict' & 
            'self.component_rot'. Assigning keys with the former & its values with 
            the latter. 
            First iteration checks for 'constant attrib's' that set unique rot value. 
            Second iteration deals with IF pv type in 'self.ik_control_dict': 
            set unique rot value, else set remaining items pos value.
        # Arguments: N/A
        # Return:
            ik_rot(dict): keys = ik_*module_*bone : values = rot data. 
        '''
        ik_rot = {}

        # Iterate through comp_name keys in the ik_name keys.
        # IF 'self.*_name' attr and IF the attr in ik_name then give unique rot 
        self.temp_ik_name_ls = []
        hock_rot_y = self.get_ik_wld_y_rot(self.hock_name)
        ik_wld_rot_y = self.get_ik_wld_y_rot(self.ik_wld_name)
        for (ik_name, ik_type), (comp_name, comp_rot) in zip(self.ik_control_dict.items(), 
                                                    self.component_rot.items()):
            try:
                if comp_name in ik_name:
                    # limbRoot name
                    self.if_constant_attr(self.limbRoot_name, ik_rot, ik_name, [0.0, 0.0, 0.0])
                    
                    # hock name
                    self.if_constant_attr(self.hock_name, ik_rot, ik_name, [0.0, hock_rot_y, 0.0])

                    # ik wld name
                    self.if_constant_attr(self.ik_wld_name, ik_rot, ik_name, [0.0, ik_wld_rot_y, 0.0])         
            except:
                pass
            
            # Iterate through the two dicts again to IF an ik_name hasen't been 
            # assigned to the 'ik_rot = {}' dict yet. And IF 'pv' type exists,
            # assign the 'ik_rot = {}' with the pv unique rotation.
            pv_pos, pv_rot = self.return_pv_pos_rot()
            for (ik_name, ik_type), (comp_name, comp_rot) in zip(self.ik_control_dict.items(), 
                                                                self.component_rot.items()):
                if ik_name not in self.temp_ik_name_ls:
                    # Check for 'pv' type
                    if comp_name in ik_name:
                        if ik_type == "pv":
                            ik_rot[ik_name] = pv_pos
                        else:
                            # Uses component rotation value if no change required.
                            ik_rot[ik_name] = comp_rot

        print(f"ik_rot = {ik_rot}")

        return ik_rot
    

    def return_pv_pos_rot(self):
        '''
        # Description:
            Retrieve the pos & rot data for the location of a pv control based 
            off the bones positon before & after the pv bone itself. This is 
            calculated with a utils function.
        # Arguments: N/A
        # Return: N/A
        '''
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


    def if_constant_attr(self, const_attr, new_dict, control_name, value_data):
        '''
        # Description:
            IF checks for 'constant attrib's' to set a unique rot value in 'new_dict'.
            IF 'constant attrib' is in control_name
                pass the control name to key &  value_data to value for the 'new_dict'
        # Arguments:
            const_attr(string/bool): Attribute name being a *bone in the module (hip)
            new_dict(dict): empty dict to add data to.
            control_name(string): Name of control 'fk/ik_*module_*bone'.
            value_data(list): pos or rot data = [#.#, #.#, #.#].
        # Return: N/A
        '''
        if const_attr:
            if const_attr in control_name:
                new_dict[control_name] = value_data
                self.temp_ik_name_ls.append(control_name)


    def get_ik_wld_y_rot(self, attr_name):
        '''
        # Description:
            Get the [#.#, y.y, #.#] Y rotaiion axis of the module's xfm guide 
            using 'const_attr' to identify it. and return it
        # Arguments: N/A
        # Return: N/A
        '''  
        if attr_name:
            target_ik_control_ls = []
            ik_controls_ls = list(self.ik_control_dict.keys())
            for ik_name in ik_controls_ls:
                # check if it's string or False
                    if attr_name in ik_name:
                        target_ik_control_ls.append(ik_name)
            tgt_module = target_ik_control_ls[0].split('_')[-2]
            tgt_control = target_ik_control_ls[0].split('_')[-1]
            # print(f"tgt_module = {tgt_module}")
            # print(f"tgt_control = {tgt_control}")
            tgt_xfm_guide = f"xfm_guide_{tgt_module}_{tgt_control}_{self.unique_id}_{self.side}"
            if cmds.objExists(tgt_xfm_guide):
                rot_y = cmds.xform(tgt_xfm_guide, q=True, ro=True, ws=True)[1]
                # print(f"rotation = {rot_y}")
                return rot_y

            else:
                print(f"{tgt_xfm_guide} Not Exists")
                return 0.0

            # xfm_guide_quadLeg_ankle_0_L
        else:
            print(f"ik_wld_name = False ")
            return 0.0
            

    def return_RawDataFkIKDicts(self):
        return self.fk_pos, self.fk_rot, self.ik_pos, self.ik_rot
    

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
    "clavicle": [10.0, 10.0, 10.0], 
    "shoulder": [7.042431639335366, -5.366417614476933, -52.87199475566796], 
    "elbow": [7.04243163933536, -32.847391136978864, -52.004681579832805], 
    "wrist": [7.04243163933536, -32.847391136978864, -52.004681579832805]
    }
constant_attr_dict = {
    "limbRoot_name": "shoulder",
    "hock_name": 0,
    "ik_wld_name": "wrist"}

RawDataFkIKDicts(fk_control_dict, ik_control_dict, component_pos, component_rot, constant_attr_dict, "0", "L")

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
q_constant_attr_dict = {
    "limbRoot_name": "hip",
    "hock_name": "calf",
    "ik_wld_name": "ankle"}
RawDataFkIKDicts(q_fk_control_dict, q_ik_control_dict, q_component_pos, q_component_rot, q_constant_attr_dict, "0", "L")
