import maya.cmds as cmds
# import pymel.core as pm

class MirrorFacsSetup():
    def __init__(self, ctrl_selection, grp_name):
        self.side = ctrl_selection[0].split('_')[-1]
        self.new_side = "R" if self.side == "L" else "L"

        # cr controls and group appropriatly 
        new_ctrls = self.duplicate_controls(ctrl_selection)
        offset_grp_ls = self.ofst_grp_to_zero(new_ctrls)
        self.parent_ofs_to_grp(grp_name, offset_grp_ls)
        cmds.select(new_ctrls)

        # wrte a function to read each controls outputs, 
        # so that i can duplicate the outputed utility nodes and connect to the corresponding blendshape, 
        # changing the suffix side, and creating the new connections.
        # the blendshape will be called the same except different side suffix. 

        # I think the best method would be to store the data effectively and learn how to gather the neccesary data
        # write utils functions to:
            # store dictionary of nodes > return name | type | setting | input | output
            # example: {name: 'MD_eyebrowouter_L', type: 'multiplydivide', settings:{"input1X": -1}, input:'' , output'' }


    def duplicate_controls(self, ctrl_selection):
        for sel in ctrl_selection:
            if not cmds.objExists(sel):
                raise ValueError(f"Control '{sel}' does not exist.")
        
        # Duplicate the entire group
        new_ctrls = []
        for node in ctrl_selection:
            dup = cmds.duplicate(node, n=node.replace(self.side, self.new_side))[0]
            new_ctrls.append(dup)
        return new_ctrls


    def ofst_grp_to_zero(self, new_ctrls):
        offset_grp_ls = []
        for i in range(len(new_ctrls)):
            offset_grp = cmds.group(n=f"offset_{new_ctrls[i]}", em=1)
            cmds.matchTransform(offset_grp, new_ctrls[i])
            cmds.parent(new_ctrls[i], offset_grp)
            offset_grp_ls.append(offset_grp)
        cmds.select(cl=1)
        return offset_grp_ls
        

    def parent_ofs_to_grp(self, grp_name, offset_grp_ls):
        temp_name = f"grp_setup_{grp_name}_{self.new_side}"
        grp = cmds.group(n=temp_name, em=1)
        for g in offset_grp_ls:
            cmds.parent(g, grp)
        cmds.setAttr(f"{grp}.scaleX", -1)


MirrorFacsSetup(cmds.ls(sl=1, typ="transform"), "eyebrow")