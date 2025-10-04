
import maya.cmds as cmds
from maya import cmds, OpenMaya
import math
import os

def create_pole_vector(top_joint, pv_joint, end_joint):
        '''
        PV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                "..", "imports","pv_ctrl_import.abc")
        print(f"pv_control import path: {PV_FILE}")
        '''

        start = cmds.xform(top_joint, q=1,ws=1,t=1)
        mid = cmds.xform(pv_joint, q=1,ws=1,t=1)
        end = cmds.xform(end_joint, q=1,ws=1,t=1)

        startV = OpenMaya.MVector(start[0], start[1], start[2])
        midV = OpenMaya.MVector(mid[0], mid[1], mid[2])
        endV = OpenMaya.MVector(end[0], end[1], end[2])

        startEnd = endV - startV
        startMid = midV - startV

        dotP = startMid * startEnd

        proj = float(dotP) / float(startEnd.length())

        startEndN = startEnd.normal()

        projV = startEndN * proj
        arrowV = startMid - projV
        finalV = arrowV + midV

        cross1= startEnd ^ startMid
        cross1.normalize()

        cross2 = cross1 ^ arrowV
        cross2.normalize()
        arrowV.normalize()

        matrixV = [arrowV.x, arrowV.y, arrowV.z, 0,
                cross1.x, cross1.y, cross1.z, 0,
                cross2.x, cross2.y, cross2.z, 0,
                0,0,0,1]
                
        matrixM = OpenMaya.MMatrix()
        OpenMaya.MScriptUtil.createMatrixFromList(matrixV, matrixM)

        matrixFn = OpenMaya.MTransformationMatrix(matrixM)

        rot = matrixFn.eulerRotation()

        # imported = cmds.file(PV_FILE, i=1, namespace="imp_pv", rnn=1)
        imported = cmds.spaceLocator()
        cmds.scale(4, 4, 4, imported)
        pv_ctrl = cmds.rename(imported[0], f"ctrl_pv_import")
        # loc = cmds.spaceLocator() # pv

        cmds.xform(pv_ctrl, ws=1,t=(finalV.x, finalV.y, finalV.z))
        cmds.xform(pv_ctrl, ws=1, rotation = ((rot.x/math.pi*180.0),
                                        (rot.y/math.pi*180.0),
                                        (rot.z/math.pi*180.0)))

        return pv_ctrl 

create_pole_vector("ori_bipedArm_shoulder_0_L", "ori_bipedArm_elbow_0_L", "ori_bipedArm_wrist_0_L")