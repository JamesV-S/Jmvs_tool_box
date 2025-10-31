


class ModuleDataManager:
    def __init__(self, module_data):
        self.raw_data = module_data
        print(f"---------------------------------------------------------------")
        print(f"Running ModuleDataManager (M.D.M).")

        print(f"DEBUG: Type of module_data = {type(module_data)}")
        print(f"DEBUG: Is it a ModuleDataManager instance? {isinstance(module_data, ModuleDataManager)}")

        print(f"M.D.M: module_data = `{module_data}`")
        print(f"M.D.M: self.raw_data = `{self.raw_data}`")
        self._validate_data()
        self._process_data()

        # _function_name(): function is meant for internal use within the class
    

    def _validate_data(self):
        '''
        # Description:
            Ensures the required data is exists
        # Attributes:
        # Returns:
        '''
        required = ['module_name', 'external_plg_dict', 'skeleton_dict', 
                            'fk_dict', 'ik_dict', 'axis_dict']
        for field in required:
            if field not in self.raw_data.keys():
                raise ValueError(f"ModuleBP Missing field: {field}")

    
    def _process_data(self):
        skeleton_dict = self.raw_data['skeleton_dict']
        fk_dict = self.raw_data['fk_dict']
        ik_dict = self.raw_data['ik_dict']

        # data to be shared to 'ModuleBlueprint', 'System[ModuleName]', 'Build[ModuleName]'
        self._external_plg_dict = self.raw_data['external_plg_dict']
        self._skel_pos_dict = skeleton_dict["skel_pos"]
        self._skel_rot_dict = skeleton_dict["skel_rot"]
        self._fk_pos_dict = fk_dict["fk_pos"]
        self._ik_pos_dict = ik_dict["ik_pos"]
        self._fk_rot_dict = fk_dict["fk_rot"]
        self._ik_rot_dict = ik_dict["ik_rot"]
        self._axis_dict = self.raw_data['axis_dict']
        self._fk_ctrl_list = [key for key in self._fk_pos_dict.keys()]
        self._ik_ctrl_list = [key for key in self._ik_pos_dict.keys()]
        self._mdl_nm = self.raw_data['module_name'] 
        self._unique_id = self._fk_ctrl_list[0].split('_')[-2]
        self._side = self._fk_ctrl_list[0].split('_')[-1]

        # gather the number of values in the dict
        self._skel_pos_num = len(self._skel_pos_dict.keys())

        # Plg data from 'external_plg_dict'.
        self._GLOBAL_SCALE_PLG = f"{self._external_plg_dict['global_scale_grp']}.{self._external_plg_dict['global_scale_atr']}" # grp_Outputs_root_0_M.globalScale
        self._BASE_MTX_PLG = f"{self._external_plg_dict['base_plg_grp']}.{self._external_plg_dict['base_plg_atr']}" # grp_Outputs_root_0_M.ctrl_centre_mtx
        self._HOOK_MTX_PLG = f"{self._external_plg_dict['hook_plg_grp']}.{self._external_plg_dict['hook_plg_atr']}" # grp_Outputs_spine_0_M.ctrl_spine_top_mtx
        
        self._global_scale_attr = self._external_plg_dict['global_scale_atr']


    @property
    def external_plg_dict(self):
        return self._external_plg_dict 
    @property
    def skel_pos_dict(self):
        return self._skel_pos_dict 
    @property
    def skel_rot_dict(self):
        return self._skel_rot_dict
    @property
    def fk_pos_dict(self):
        return self._fk_pos_dict
    @property
    def ik_pos_dict(self):
        return self._ik_pos_dict
    @property
    def fk_rot_dict(self):
        return self._fk_rot_dict
    @property
    def ik_rot_dict(self):
        return self._ik_rot_dict
    @property
    def prim_axis(self):
        return self._axis_dict["prim"]
    @property
    def axis_dict(self):
        return self._axis_dict
    @property
    def fk_ctrl_list(self):
        return self._fk_ctrl_list
    @property
    def ik_ctrl_list(self):
        return self._ik_ctrl_list
    @property
    def mdl_nm(self):
        return self._mdl_nm
    @property
    def unique_id(self):
        return self._unique_id
    @property
    def side(self):
        return self._side
    @property
    def skel_pos_num(self):
        return self._skel_pos_num
    @property
    def GLOBAL_SCALE_PLG(self):
        return self._GLOBAL_SCALE_PLG
    @property
    def BASE_MTX_PLG(self):
        return self._BASE_MTX_PLG
    @property
    def HOOK_MTX_PLG(self):
        return self._HOOK_MTX_PLG
    @property
    def global_scale_attr(self):
        return self._global_scale_attr
    @property
    def XYZ(self):
        return ["X", "Y", "Z"]
    




        




