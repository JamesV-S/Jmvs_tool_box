
import maya.cmds as cmds

def create_setup(locator_ls):
    if not locator_ls or len(locator_ls) < 2:
        print("Error: At least two locators are required.")
        return

    print(f"locator_ls = {locator_ls}")

    # Nurbs spehere to work as the parent to the whole setup
    first_position = cmds.xform(locator_ls[0], q=True, t=True, worldSpace=True)
    nurbs_cube = cmds.sphere(name=f"myNurbsSphere_{locator_ls[0]}", p=first_position, ssw=0, esw=360, r=1, d=3, ut=0, tol=0.01, s=8, nsp=4, ch=1)
    cmds.xform(nurbs_cube, centerPivots=True)
    cmds.scale(0.5, 0.5, 0.5, nurbs_cube, r=True)
    cmds.makeIdentity(nurbs_cube, a=True, t=False, r=False, s=True, n=False, pn=True)

    # controls
    ctrl = cmds.createNode('transform', n=f'ctl_{locator_ls[0]}')
    for axis in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]:
        cir = cmds.circle(nr=axis)
        cir_shp = cmds.listRelatives(cir, c=True, s=True)[0]
        cmds.parent(cir_shp, ctrl, s=True, r=True)
        cmds.delete(cir)
    
    cmds.matchTransform(ctrl, locator_ls[0], pos=True, scl=False, rot=True)
    cmds.move(0, 5, 0, ctrl, r=True, os=True)
    cmds.setAttr(ctrl + ".overrideEnabled", True)
    cmds.setAttr(ctrl + ".overrideColor", 18)

    # Create offset groups
    offset_grp = []
    for locator in locator_ls:
        offset = cmds.group(n=f"offset_{locator}", em=True)
        cmds.matchTransform(offset, locator)
        cmds.parent(locator, offset)
        offset_grp.append(offset)
    
    # axis params
    aimX = [1,0,0] # x
    aimY = [0,1,0] # y
    aimZ = [0,0,1] # z

    # Minus if 
    minus = 0
    if minus: 
        aimX = [-1 if i == 1 else i for i in aimX]
        aimY = [-1 if i == 1 else i for i in aimY]
        aimZ = [-1 if i == 1 else i for i in aimZ]
    print( f"aimX = {aimX}, aimY = {aimY}, aimZ = {aimZ}" )

    # Setup aim constraints
    for i in range(1, len(locator_ls)):
        previous_locator = offset_grp[i - 1]
        current_locator = offset_grp[i]
        print(f"Previous Locator: {previous_locator} & Current Locator: {current_locator}")
        
        

        cmds.aimConstraint(current_locator, previous_locator, weight=1, aim=aimX, upVector=aimY, worldUpType="vector", worldUpVector=aimY)
        cmds.parent(ctrl, offset_grp[i], nurbs_cube)

    cmds.parent(offset_grp[-1], nurbs_cube)
    
    # delete the annoying constraint left onn the last locator
    if cmds.listRelatives(locator_ls[-1], type="constraint"):
        null_constraint = cmds.listRelatives(locator_ls[-1], type="constraint")[0]
        cmds.delete(null_constraint)
    # match last locator to the one before it to match orientation
    cmds.matchTransform(offset_grp[-1], offset_grp[-2], pos=False, scl=False, rot=True)

    first_locator = locator_ls[0]
    for i in range(len(locator_ls)):
        cmds.setAttr(f"{offset_grp[i]}.rotateX", 0)
        cmds.setAttr(f"{locator_ls[i]}.rotateX", 0)
        cmds.aimConstraint(
            ctrl, locator_ls[0], weight=1, aim=[0, -1, 0], 
            upVector=[-1, 0, 0], worldUpType="objectrotation", worldUpObject=ctrl, 
            worldUpVector=[0, 1, 0], skip=('z', 'y'), mo=False
            )
        cmds.setAttr(locator_ls[i] + ".overrideEnabled", True)
        cmds.setAttr(locator_ls[i] + ".overrideColor", 18)
    
    # connect the first locator's rotate to all others so match aim orientation
    for i in range(1, len(locator_ls)):
        cmds.connectAttr(f'{first_locator}.rotate', f'{locator_ls[i]}.rotate')

    cmds.select(cl=True)

# Call the function with your locator list
#locator_ls = ['loc_edgePos_A', 'loc_edgePos_B', 'loc_edgePos_C', 'loc_edgePos_D']
create_setup(cmds.ls(sl=1, type="transform"))
    
    
    



    
    


