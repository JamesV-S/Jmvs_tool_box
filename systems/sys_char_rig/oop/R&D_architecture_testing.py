
#------------------------------------------------------------------------------
# Current architecturea approach:
    # Class ModuleBluePrint 
class ModuleBluePrint:
    """Consistent operations for all rig modules"""
    def create_controls(self):
        print("Creating standard controls")
    
    def setup_deformers(self):
        print("Setting up deformers")
    
    def connect_attributes(self):
        print("Connecting attributes")

    # Class System#
class SystemSpine:
    """Spine-specific operations"""
    def setup_spline_ik(self):
        print("Setting up spine spline IK")
    
    def create_spine_curves(self):
        print("Creating spine curves")

    # Class System#
class SystemBipedArm:
    """Arm-specific operations"""  
    def setup_fk_ik_switch(self):
        print("Setting up FK/IK switch")
    
    def create_elbow_pole_vector(self):
        print("Creating elbow pole vector")

    # Class Build#
class BuildSpine(ModuleBluePrint, SystemSpine):
    def build(self):
        self.create_controls()      # From BluePrint
        self.setup_spline_ik()      # From SystemSpine
        self.setup_deformers()      # From BluePrint

    # Class Build#
class BuildBipedArm(ModuleBluePrint, SystemBipedArm):
    def build(self):
        self.create_controls()      # From BluePrint  
        self.setup_fk_ik_switch()   # From SystemBipedArm
        self.create_elbow_pole_vector()  # From SystemBipedArm
#-------------------------------

'''
    in rigging script where I wire build module to ui element:
    import and call BuildSpine(), BuildBipedArm()
    
    HOW WILL I pass ("bipedArm", ex_external_plg_dict, ex_skeleton_dict, 
                        ex_fk_dict, ex_ik_dict, "X") 
    data to the member funtions of '' & 'SystemBipedArm' when they both use 
    the data across all their member functions in their own way?

    SOLUTION: 
        Carful data flow design!

        > Begin with 'SOlUTION 1' as it's the most straightforward approach and gives 
        me the clean data flow I need. 
        > As I test this, Evolve to approach 2 for better data validation. 
        > Continue to evolve this data flow as i grow my modules and 'jmvs_workflow'
    
        *IMPORTANT: 
            All parent classes ('Class ModuleBluePrint', 'Class System#') recieve 
            the same data container, but each uses the parts relevant to their 
            member_functions responsibilties. 
            Keeping my data coinsitent across the entire build process while 
            allowing each class to focus on its specific duty.
     ----------------------  SOLUTION 1 ------------------------------------- 
                Centralised data store (recommended)
'''

class ModuleBluePrint:
    """Consistent operations for all rig modules"""
    def __init__(self, module_data):
        self.data = module_data  # Central data store
    
    def create_controls(self):
        # Access shared data
        module_name = self.data['module_name']
        joints = self.data['joints']
        print(f"Creating controls for {module_name}: {joints}")
    
    def setup_deformers(self):
        # Same data, different usage
        deform_joints = self.data.get('deform_joints', self.data['joints'])
        print(f"Setting up deformers on: {deform_joints}")

class SystemBipedArm:
    """Arm-specific operations"""
    def __init__(self, module_data):
        self.data = module_data  # Same data store
    
    def setup_fk_ik_switch(self):
        # Arm-specific data usage
        switch_attr = self.data['control_attributes']['fk_ik_switch']
        print(f"Setting up FK/IK switch: {switch_attr}")
    
    def create_elbow_pole_vector(self):
        # Access arm-specific data
        elbow_joint = self.data['joints'][1]  # Second joint is elbow
        pole_distance = self.data.get('pole_vector_distance', 5.0)
        print(f"Creating pole vector for {elbow_joint} at distance {pole_distance}")

class BuildBipedArm(ModuleBluePrint, SystemBipedArm):
    def __init__(self, module_data):
        # Initialize both parents with same data
        ModuleBluePrint.__init__(self, module_data)
        SystemBipedArm.__init__(self, module_data)
        self.data = module_data  # Also store locally if needed
    
    def build(self):
        print(f"Building {self.data['module_name']}...")
        self.create_controls()          # Uses data via ModuleBluePrint
        self.setup_fk_ik_switch()       # Uses data via SystemBipedArm  
        self.create_elbow_pole_vector() # Uses data via SystemBipedArm
        self.setup_deformers()          # Uses data via ModuleBluePrint

# Usage with module-specific data
arm_data = {
    'module_name': 'biped_arm_L',
    'joints': ['shoulder_L', 'elbow_L', 'wrist_L'],
    'control_attributes': {
        'fk_ik_switch': 'arm_FKIK_L',
        'stretch': 'arm_stretch_L'
    },
    'pole_vector_distance': 7.5,
    'deform_joints': ['shoulder_deform_L', 'elbow_deform_L', 'wrist_deform_L']
}

arm_rig = BuildBipedArm(arm_data)
arm_rig.build()


'''
     ----------------------  SOLUTION 2 ------------------------------------- 
                Centralised data store (More Structered)
'''
class ModuleData:
    """Manages module-specific data with validation"""
    def __init__(self, **kwargs):
        self._data = kwargs
        self._validate_data()
    
    def _validate_data(self):
        """Ensure required data exists"""
        required = ['module_name', 'joints']
        for field in required:
            if field not in self._data:
                raise ValueError(f"Missing required field: {field}")
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value

class ModuleBluePrint:
    def __init__(self, module_data):
        self.data = module_data
    
    def create_controls(self):
        # Use data manager
        prefix = self.data['module_name']
        joints = self.data['joints']
        color = self.data.get('control_color', 'yellow')
        print(f"Creating {color} controls for {prefix}: {joints}")

class BuildBipedArm(ModuleBluePrint, SystemBipedArm):
    def __init__(self, **kwargs):
        data = ModuleData(**kwargs)  # Create validated data
        ModuleBluePrint.__init__(self, data)
        SystemBipedArm.__init__(self, data)
    
    def build(self):
        # All methods now use the same validated data
        self.create_controls()
        self.setup_fk_ik_switch()
        # ...

# Clean usage
arm_rig = BuildBipedArm(
    module_name='biped_arm_L',
    joints=['shoulder_L', 'elbow_L', 'wrist_L'],
    control_color='blue',
    pole_vector_distance=6.0
)
#------------------------------------------------------------------------------

# ^ Handling data duplication & repetitive processing that's presemt above ^
'''
     ----------------------  SOLUTION ------------------------------------- 
                        Data Manager class 
    - Every & each instance is completely isolated (no data leaks).
    - Proccess the data once for each module (no repetitive parsing).
    - clean access (use propertirs instead of idctionary lookups)
    - Maintainable (all data logic in one place)
    - performance (no repeated operations across the 3 custom classes)
    - Debuggable (easy to see what data is available)
    - DRY (Don't Repeat Yourself)

                Managing Architectual concern of data
                leaks when managing multiple modules.  

'''