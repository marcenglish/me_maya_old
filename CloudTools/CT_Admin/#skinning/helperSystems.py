####  HelperJoints v2 by Marc English
####  This script contains all the procedures called when building pieces of the modular bind rig setup
####  Section 1 contains sub-procedures that simplify basic tasks.  Joint creation, null creation etc.  
####  Section 2 contains the procedures that build joint systems - weighted joints, offset joints and cross pivots
####  Section 3 contains the procedures that build body components - hand, forearm, upperArm, etc..
####
####  Currently in development:
####  -Simplification/Code cleaning
####  -Twist implementation 
##############################################################################################################

import maya.cmds as cmds

####  Section 1 ##############################################################################################
##############################################################################################################

def meJoint(obj,name,naturalParent,postParent,matchRadius,offset,offsetType,jo,acv):
    #JOINT CREATION WRAPPER
    #parent - created joint will initially be parented under this joint.  it will also inherit its orientation and position. 
    #postParent - if not left blank, this variable passes the non-natural joint under which the helper will be parented.    
    #matchRadius - if '0', will match radius, otherwise, will accept a float value for radius.
    # offset - vector/tuple used for positioning.  can either be a bone length ratio or world space coordinates.  see offsetType    
    # offsetType - can be either 'ratio' or 'worldPosition', designating that the info in offset is either a ratio or a world space translate.
    #jo - joint orientation
    cmds.select(obj)
    cmds.joint(n=name)    
    cmds.parent(name,naturalParent)
    
    radius = matchRadius
    if matchRadius == 0:
        radius = cmds.getAttr(obj+".radius")            
    cmds.setAttr(name+'.radius',radius)
    
    if offsetType == "Ratio":        
        new_pos = [0.0,0.0,0.0]   
        objSpace_pos = cmds.getAttr(obj+".t")[0]     
        new_pos[0] = objSpace_pos[0] * offset[0]
        new_pos[1] = objSpace_pos[0] * offset[1]
        new_pos[2] = objSpace_pos[0] * offset[2]
        cmds.setAttr(name+".t",new_pos[0],new_pos[1],new_pos[2])
    if offsetType == "WorldPosition":
        cmds.xform(name,ws=True,t=(offset[0],offset[1],offset[2]))

    if jo != '':
        cmds.setAttr(name+".jointOrientX",jo[0])
        cmds.setAttr(name+".jointOrientY",jo[1])
        cmds.setAttr(name+".jointOrientZ",jo[2])
    
    if naturalParent != postParent:
        cmds.parent(name,postParent)

def meNull(null,snapTo,parent,adopt):
    #snapTo - snaps to object
    #parent - parent under object
    #adopt - array with objects to be parented under this null
    cmds.group(em=True,n=null)
    cmds.delete(cmds.parentConstraint(snapTo,null))
    cmds.parent(null,parent)    
    if adopt != '':
        for ea in adopt:
            cmds.parent(ea,null)

def meParentSpace(name):
    parent = cmds.listRelatives(name,p=True)[0]
    meNull(name+'_Space',name,parent,[name])

def meBBLOC():
    sel = cmds.ls(sl=True)
    bb =  cmds.exactWorldBoundingBox(sel)
    x = (bb[0] + bb[3]) / 2
    y = (bb[1] + bb[4]) / 2
    z = (bb[2] + bb[5]) / 2
    name = sel[0].split('.')
    cmds.spaceLocator(n=name[0]+"_LOC")
    cmds.setAttr(name[0]+"_LOC.t",x,y,z)

####  Section 2 ##############################################################################################
##############################################################################################################
   
def meHelper(obj,tgt,offset,offsetType,weight,label,aimVector,upVector,parent,acParent,jo,side,driverType):
    #CREATES HELPER JOINTS - OFFSET PIVOTS FOR GEOMETRY WEIGHTING, ROTATION READING DONE WITH AIM CONSTRAINTS TO PREVENT EULER FLIPPING 
    # obj - object that the weighted joint will follow
    # tgt - the target object for the aim constraint. If blank, aimconstraint will use the first child as the target.
    # offset - vector/tuple used for positioning.  can either be a bone length ratio or world space coordinates.  see offsetType    
    # offsetType - can be either 'ratio' or 'worldTrans', designatign that the info in offset is either a ratio or a world space translate. 
    # weight - proportion of rotate follow transferred to the helper joint. A Weight of one means no blending, just a direct connection.
    # label - extra descriptor on the joint name.
    # aimVector - described as (1,0,0) for x, (0,1,0) for y, etc.
    # upVector - see above.  This is the axis of rotation which will get the most frip-free rotation, the other will be limited to 90 degrees.
    # parent - if not left blank, this variable passes the non-natural joint under which the helper will be parented.
    # acParent - if not left blank, this variable passes the non-natural joint under which the aimConstraint parent space will be parented.
    # jo - joint orientation
    # side - adds the side defining indicator to the nodes' names.
    naturalParent = cmds.listRelatives(obj,c=False,p=True)[0]
    position = cmds.getAttr(obj+".t")[0]
    meJoint(obj,obj+"_helper"+label,naturalParent,parent,0,offset,offsetType,jo,aimVector)        
    if tgt == '':
        tgt = cmds.listRelatives(obj,p=False,c=True)            
    if parent == '':
        parent = cmds.listRelatives(obj)[0]
            
    if driverType == "ac_pb":        
        meNull(obj+"_helper"+label+"_AC",obj,parent,'')    
        meParentSpace(obj+"_helper"+label+"_AC")
        if parent != acParent:
            cmds.parent(obj+"_helper"+label+"_AC_Space",acParent)
        cmds.aimConstraint(tgt,obj+"_helper"+label+"_AC",aimVector=aimVector,upVector=upVector,worldUpType='objectrotation',worldUpVector=upVector,worldUpObject=obj+"_helper"+label+"_AC_Space",n=obj+"_helper"+label+"_ACON")
        cmds.createNode('pairBlend',n=obj+"_helper"+label+"_PB")
        cmds.setAttr(obj+"_helper"+label+"_PB.rotInterpolation",1) 
        cmds.setAttr(obj+"_helper"+label+"_PB.weight",0.5)
        cmds.connectAttr(obj+"_helper"+label+"_ACON.constraintRotateX",obj+"_helper"+label+"_PB.inRotateX2")
        cmds.connectAttr(obj+"_helper"+label+"_ACON.constraintRotateY",obj+"_helper"+label+"_PB.inRotateY2")
        cmds.connectAttr(obj+"_helper"+label+"_ACON.constraintRotateZ",obj+"_helper"+label+"_PB.inRotateZ2")
        cmds.connectAttr(obj+"_helper"+label+"_PB.outRotateX",obj+"_helper"+label+".rx")
        cmds.connectAttr(obj+"_helper"+label+"_PB.outRotateY",obj+"_helper"+label+".ry")
        cmds.connectAttr(obj+"_helper"+label+"_PB.outRotateZ",obj+"_helper"+label+".rz")
        cmds.addAttr(obj+"_helper"+label,ln="weight",at='double',dv=0.5)
        cmds.setAttr(obj+"_helper"+label+".weight",e=True, k=True, l=False)
        cmds.connectAttr(obj+"_helper"+label+".weight", obj+"_helper"+label+"_PB.weight")
       
        print "AimConstraint weighted joint setup complete."
        
    if driverType == "direct":
        cmds.connectAttr(obj+".rx",obj+"_helper"+label+".rx")
        cmds.connectAttr(obj+".ry",obj+"_helper"+label+".ry")
        cmds.connectAttr(obj+".rz",obj+"_helper"+label+".rz")
        print "Direct connection joint setup complete."    



def dpReader():
    #create rig
    sel = m.ls(sl=True)[0]
    child = m.listRelatives(sel,p=False,c=True)[0]
    prnt = m.listRelatives(sel,c=False,p=True)[0]
    vectors = ['ReaderAim_'+sel,'ReaderAdj_'+sel,'ReaderOpp_'+sel]

    m.group(n='ReaderBase_'+sel, em=True)
    m.delete(m.parentConstraint(sel,'ReaderBase_'+sel))
    m.parentConstraint(prnt,'ReaderBase_'+sel,mo=True)

    for vector in vectors:
        m.spaceLocator(n=vector)
        m.parent(vector,'ReaderBase_'+sel,r=True)    
        
    m.parentConstraint(child,'ReaderAim_'+sel,mo=False)
    m.setAttr('ReaderAdj_'+sel+'.tx',1)
    m.setAttr('ReaderOpp_'+sel+'.tz',1)

    #create node setup
    for vector in vectors:
        m.createNode('vectorProduct',n=vector+'_VCTR_VP')
        m.connectAttr(vector+'.translate',vector+'_VCTR_VP.input1')
        m.connectAttr('ReaderAim_'+sel+'.translate',vector+'_VCTR_VP.input2')
        m.setAttr(vector+'_VCTR_VP.operation',3)
        
        if 'Aim' not in vector:
            print 'check!'
            print sel
            m.createNode('vectorProduct',n=vector+'_DP_VP')
            m.connectAttr(vector+'_VCTR_VP.output',vector+'_DP_VP.input1')
            m.connectAttr('ReaderAim_'+sel+'_VCTR_VP.output',vector+'_DP_VP.input2')
            m.setAttr(vector+'_DP_VP.operation',1)
            
            m.addAttr('ReaderBase_'+sel,ln=vector,at='double',k=1)
            m.connectAttr(vector+'_DP_VP.outputX','ReaderBase_'+sel+'.'+vector)
            m.setAttr (vector+'_DP_VP.normalizeOutput',1)