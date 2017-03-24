import meBuildTools as meBuildTools
reload(meBuildTools)

from Rig import meTools 

import os as os
import sys
import maya.cmds as m
#execfile (scriptPath+"meBuildClasses.py")
from pymel.core import *   

#Last edit: 11-27-2013

def meNewBuild(objList,characterName,verbose):
    
    #Rigs should not need to be in order until the final, connecting stage
    
    #build rigs
    for j, obj in enumerate(objList.objDict):
        obj = obj['obj']
        obj.verbose = verbose
        startJoint= obj.joints[0].replace('_deleteMe','')

        if j == 0:
            obj.isTop = True
        else:
            obj.isTop = False

        if m.objExists(startJoint):
            #add builder attributes to object
            obj.s = 0
            obj.charName = characterName

            #build the rigs
            for id in obj.sides:
                prepObject(obj,id)
                if obj.s == 0:
                    obj.polarity = 1
                else:
                    obj.polarity = -1

                meBuildTools.Framework(obj)                

                if obj.type == 'IKFK_spline':   FKIK_spline(obj)
                if obj.type == 'IKFK_single':   FKIK_single(obj)
                if obj.type == 'IKFK_hinge':    FKIK_singleHinge(obj)
                if obj.type == 'IKFK_doubleHinge': FKIK_doubleHinge(obj)


                if obj.type == 'INV_foot':      INV_foot(obj)
                if obj.type == 'hand':          hand(obj)
                if obj.type == 'Static':        Static(obj)
                if obj.type == 'Wheel':         Wheel(obj)



                if obj.isDriver:
                
                    #if obj.name != 'Hand':
                    if not obj.keepEnd:
                        meBuildTools.RenameEndJoint(obj)
            
                meBuildTools.postFramework(obj)

                obj.s += 1

            meBuildTools.ConnectToDriver(obj)

                
        if obj.isTop:
            m.parentConstraint('WorldOffset',obj.inPlug,mo=True)

    #post build cleanup
    assemblies = m.ls(assemblies=True)
    topJoint = ''
    for a in assemblies:
        if 'base_' in a:
            topJoint = a

    m.hide('Rig_Utilities',topJoint) 
    m.parent(topJoint,characterName+'_Rig')

    m.addAttr(topJoint,ln="rootType",dt="string")
    m.setAttr(topJoint+'.rootType','BaseSkel',type='string')


    for ctrl in m.listRelatives('WorldOffset_Space',c=True):
        if 'World' not in ctrl:
            m.connectAttr('WorldOffset.ctrlVisibility',ctrl+'.v')

def prepObject(obj,id):
    '''simplifies rig build by preparing target lists for later functions'''
    #base, fk, ik, rig, core skels    

    if 'procedural' in obj.extraInfo:
        
        #print obj.extraInfo['procedural']+'_'+obj.templateData['template'][obj.extraInfo['templateType']]['staticName']
        obj.name = obj.templateData['template'][obj.extraInfo['templateType']]['staticName']
        
    #format root joint names set
    obj.jointRoots = meTools.listSubstitute(obj.jointRoots,['_deleteMe',''])
    obj.jointRoots = meTools.listSubstitute(obj.jointRoots,[obj.name+'_',''])    
    if id == obj.sides[0]:
        obj.jointRoots = meTools.listSubstitute(obj.jointRoots,[id,''])

    #format core joint names set
    obj.allJoints = obj.jointRoots
    obj.coreJoints = []
    for ea in obj.allJoints:
        if 'Roll' not in ea: obj.coreJoints.append(ea)

    #format other joint names sets
    obj.idJ = meTools.listAppend(obj.coreJoints,post=id)
    obj.FKJ = meTools.listAppend(obj.coreJoints,pre=obj.name+'_FK_',post=id)
    obj.IKJ = meTools.listAppend(obj.coreJoints,pre=obj.name+'_IK_',post=id)
    obj.RtrnIKJ = meTools.listAppend(obj.coreJoints,pre=obj.name+'Rtrn_IK_',post=id)
    obj.PreIKJ = meTools.listAppend(obj.coreJoints,pre=obj.name+'_Pre_IK_',post=id)
    obj.PIKJ = meTools.listAppend(obj.coreJoints,pre=obj.name+'_Post_IK_',post=id)
    obj.RigJ = meTools.listAppend(obj.coreJoints,pre=obj.name+'_Rig_',post=id)
    obj.baseJ = meTools.listAppend(obj.coreJoints,pre='base_'+obj.name+'_',post=id)   
    obj.allBaseJ = meTools.listAppend(obj.allJoints,pre='base_'+obj.name+'_',post=id)    

    if obj.verbose:
        print '\n\n======================================='
        print 'Start Rig info:'
        print obj.name
        print 'parent offset is ',str(obj.parentOffset)
        if obj.connectedToObj:
            print 'connected to object: ',obj.connectedToObj.name
        print 'obj.allJoints'
        print obj.allJoints
        print 'obj.coreJoints'
        print obj.coreJoints    
        print  'obj.FKJ'
        print  obj.FKJ
        print  'obj.IKJ'
        print  obj.IKJ
        print  'obj.RigJ'
        print  obj.RigJ
        print  'obj.baseJ'
        print  obj.baseJ
        print 'obj.allBaseJ'
        print obj.allBaseJ    
        print '=======================================\n\n'

        if obj.connectionJoint:
            print obj.name+' is connected to '+obj.connectionJoint


    if 'defaultIkHandleName' in obj.templateData['template'][obj.extraInfo['templateType']]:
        if obj.templateData['template'][obj.extraInfo['templateType']]['defaultIkHandleName'][0]=='getFromName':
            obj.ikHandles=[obj.subName]

        else:
            obj.ikHandles=obj.templateData['template'][obj.extraInfo['templateType']]['defaultIkHandleName']

    if 'procedural' in obj.extraInfo:
        obj.name = obj.extraInfo['procedural']+'_'+obj.templateData['template'][obj.extraInfo['templateType']]['proceduralName']


    if 'defaultPss' in obj.templateData['template'][obj.extraInfo['templateType']]:
        obj.defaultPss = obj.templateData['template'][obj.extraInfo['templateType']]['defaultPss']

    if 'switchLoc' in obj.templateData['template'][obj.extraInfo['templateType']]:
        obj.switchLoc = obj.templateData['template'][obj.extraInfo['templateType']]['switchLoc']

    if 'upVector' in obj.templateData['template'][obj.extraInfo['templateType']]:
        obj.upVector = obj.templateData['template'][obj.extraInfo['templateType']]['upVector']

    if 'ikHandleOrient' in obj.templateData['template'][obj.extraInfo['templateType']]:
        obj.ikHandleOrient = obj.templateData['template'][obj.extraInfo['templateType']]['ikHandleOrient']

    obj.id = id

def Static(obj):    
    meBuildTools.Joints(obj,'Rig',ps=True,plug=True)
    meTools.Ctrl(name=obj.name+"_CTRL",shape='box',color='yellow',tgt=obj.RigJ[0],connection='cp',parentSpace='%'+obj.controlsTop,orientMatch=obj.joints[0],attr="ctrl_body",pivot=True,vis=1)
    m.parentConstraint(obj.name+"_CTRL",obj.outPlug,mo=True)

def Wheel(obj):    
    meBuildTools.Joints(obj,'Rig',ps=True,plug=True)
    meTools.Ctrl(name=obj.name+"_CTRL",shape='circle',axis='z',color='yellow',tgt=obj.RigJ[0],connection='cp',parentSpace='%'+obj.controlsTop,orientMatch=obj.joints[0],attr="ctrl_body",pivot=True,vis=1)
    m.parentConstraint(obj.name+"_CTRL",obj.outPlug,mo=True)

def FKIK(obj):   
    id = obj.id
    utils = obj.utilsTop
    name = obj.name
    follows = []

    ####
    #FK
    ####    
    meBuildTools.Joints(obj,'FK',ps=True,plug=True)
    meBuildTools.FKChain(obj)

    ####
    ##IK
    ####   
    meBuildTools.Joints(obj,'IK',ps=True,plug=True)
    meBuildTools.Joints(obj,'Rtrn_IK',ps=True,plug=True)


    handle = m.ikHandle(sj=obj.IKJ[0],
                        ee=obj.IKJ[-1],
                        n=name+'_'+obj.coreJoints[-1]+"_ikHandle"+id,sol='ikRPsolver')[0].replace(id,'')
    rtnHandle = m.ikHandle(sj=obj.RtrnIKJ[0],
                        ee=obj.RtrnIKJ[-1],
                        n=name+'_'+obj.coreJoints[-1]+"_RtnikHandle"+id,sol='ikRPsolver')[0].replace(id,'')
    

    m.parent(handle+id,rtnHandle+id,utils)
    m.parentConstraint(obj.name+id+'_plug_end_IN',rtnHandle+id)

    
    #PV

    PV_CTRL = handle.replace('_ikHandle','')+id+'_PV_CTRL'    
    meTools.Ctrl(name=PV_CTRL,shape='diamond',color=obj.colors['PrimaryLR'][id],parentSpace='%'+name+'_Controls'+id,vis=1,lockType='s%r%v',attr='PV_ctrl_body_'+id)
    
    #adjust pv position to match bend angle
    cnst = meTools.PC(obj=PV_CTRL+'_Space',snapTo=obj.baseJ[0],keep=0)


    if 'roll' in obj.extraInfo:

        roll =  obj.extraInfo['roll']
        if roll == 0:
            roll = 1
        #angle = m.getAttr(base[roll+1]+'.jointOrientY')/2        
        length = m.getAttr(obj.baseJ[1]+'.tx')*roll
    else:
        #angle = m.getAttr(base[1]+'.jointOrientY')/2        
        length = m.getAttr(obj.baseJ[1]+'.tx')

    m.parent(PV_CTRL+'_Space',obj.baseJ[0])
    
    #position PV control
    m.setAttr(PV_CTRL+'_Space.tx',length)
    
    rotations = {'y':m.getAttr(obj.IKJ[1]+'.jointOrientY'),'z':m.getAttr(obj.IKJ[1]+'.jointOrientZ')}

    axis = ''
    polarity = -1 
    for rot in rotations:    
        if -0.01 < rotations[rot] < 0.01:
            axis = rot
        else:
            if rotations[rot] >1:
                polarity = 1
    
    if obj.upVector == (0,0,1):
        polarity = 1
        m.setAttr(PV_CTRL+'_Space.rx',90)



    


    m.setAttr(PV_CTRL+'_Space.t'+axis,length*polarity)


    
    m.parent(PV_CTRL+'_Space',obj.controlsTop)

    m.poleVectorConstraint(PV_CTRL,handle+id)
    m.poleVectorConstraint(PV_CTRL,rtnHandle+id)

    ####
    #CONTROLS
    ####

    obj.ikHandle = handle.replace('_ikHandle','')+id+'_CTRL'

    #deterime parent space switch setup:
    if obj.isTop:
        obj.parentSpaceSwitch.remove('RigRoot')
        follows = obj.parentSpaceSwitch
    else:
        follows = obj.parentSpaceSwitch
        follows[1] = obj.inPlug


    orient = obj.baseJ[-2]
    



    if obj.ikHandleOrient == 'World':
        orient = 'WorldOffset'

    elif m.getAttr(obj.baseJ[-1]+'.tx') < 0:
            print obj.name+' needs flip!'
            m.spaceLocator(n='tempRightSideOrient')
            meTools.PC(obj='tempRightSideOrient',snapTo=obj.baseJ[-1],keep=0)
            
            orient = 'tempRightSideOrient'
            m.rotate(180,'tempRightSideOrient',y=True,r=True,os=True)
            



    CTRL = handle.replace('_ikHandle','')+id+'_CTRL'
    meTools.Ctrl(name=CTRL,     
                shape='box',
                color=obj.colors['PrimaryLR'][id],
                tgt=handle+id,parentSpace='%'+obj.controlsTop,
                orientMatch=orient,
                attr="ctrl_body_"+id,
                vis=1,
                lockType='s%v',
                pivot=True,
                pss=follows,
                defaultPss=obj.defaultPss,
                
                )

    if m.objExists('tempRightSideOrient'):
        m.delete('tempRightSideOrient')
        orient = obj.baseJ[-2]

    m.parentConstraint(CTRL,obj.IKJ[-1].replace(id,'_Spacer'+id),mo=True)        
    m.parentConstraint(CTRL,handle+id)
    
    m.addAttr(CTRL,ln="fkRotateOrder",at="enum",en="xyz=0:yzx=1:zxy=2:xzy=3:yxz=4:zyx=5:",k=False)
    m.setAttr(CTRL+".fkRotateOrder",channelBox=True)
    m.connectAttr(CTRL+".fkRotateOrder",CTRL+'.rotateOrder')

    #parentSpace blend for PV
    constr = m.parentConstraint(obj.inPlug,PV_CTRL+'_Space',mo=True)[0]
    m.parentConstraint(CTRL,PV_CTRL+'_Space',mo=True)
    m.addAttr(PV_CTRL,ln='parentSpaceFollow',at='double',min=0,max=1,dv=0)
    m.setAttr(PV_CTRL+'.parentSpaceFollow',k=True)
    meTools.Node('reverse',PV_CTRL+'_REV',connA=[PV_CTRL+'.parentSpaceFollow',PV_CTRL+'_REV.inputX'],
                                         connB=[PV_CTRL+'_REV.outputX',constr+'.'+obj.inPlug+'W0'])
    m.connectAttr(PV_CTRL+'.parentSpaceFollow',constr+'.'+CTRL+'W1')

    for ea in obj.FKJ:    
        if m.objExists(ea+"_CTRL"):
            m.connectAttr(ea+"_CTRL.fkRotateOrder",ea.replace('FK','IK')+'.rotateOrder')


    ####
    #BLEND
    ####

    meBuildTools.Joints(obj,'Rig',ps=True,plug=True)
    j = 0
    for ea in obj.coreJoints:
        spacer = obj.IKJ[j]
        if ea == obj.coreJoints[-1]: 
            spacer = obj.name+'_IK_'+ea+"_Spacer"+id        
        ea += id

        meTools.Node('pairBlend',obj.name+'_'+ea+"_BLN",
                            attrA= ['weight',0.5],
                            attrB= ['rotInterpolation',1])
        for ax in ['x','y','z']:
            m.connectAttr(obj.FKJ[j]+'.r'+ax,obj.name+'_'+ea+'_BLN.inRotate'+ax.upper()+'1')
            m.connectAttr(obj.name+'_'+ea+'_BLN.outRotate'+ax.upper(),obj.RigJ[j]+'.r'+ax)
            if m.objExists(spacer+'.r'+ax):
                m.connectAttr(spacer+'.r'+ax,obj.name+'_'+ea+'_BLN.inRotate'+ax.upper()+'2')
        j+=1


    ####
    #CONTROLS
    ####
    obj.switchHandle = CTRL+"_SW" 
    meTools.Ctrl(name=obj.switchHandle,
                axis='y',
                shape='circle',
                color='white',
                tgt=orient,
                parentSpace='%'+obj.controlsTop,
                attr='ctrl_body_'+id,
                vis=1,
                lockType='all')
    

    if obj.switchLoc == -1:
        m.parentConstraint(obj.RigJ[-1],CTRL+"_SW_Space")
    if obj.switchLoc == 0:
        m.parentConstraint(obj.inPlug,CTRL+"_SW_Space")
    
    m.addAttr(CTRL+'_SW',ln='FK_IK',min=0,max=1,dv=1,k=1)            

    meTools.Node('reverse',CTRL+'_SW_REV',connA= [CTRL+'_SW.FK_IK',CTRL+'_SW_REV.inputX'])            
    
    j = 0
    for rt in obj.coreJoints:
        connectAttr(CTRL+'_SW_REV.outputX',obj.FKJ[j]+"_CTRL_Space.v")
        m.connectAttr(obj.FKJ[j]+"_CTRL.fkRotateOrder",obj.RigJ[j]+'.rotateOrder')
        connectAttr(CTRL+'_SW.FK_IK',obj.name+'_'+rt+id+'_BLN.weight')
        j+=1

    m.connectAttr(CTRL+'_SW.FK_IK',CTRL+'_Space.v')
    
    ####
    ## CONNECT OUTPUT
    ####

    if m.objExists(name+id+'_plug_end_OUT'):
        m.parentConstraint(obj.RigJ[-1],name+id+'_plug_end_OUT')

def FKIK_single(obj):
    id = obj.sides[obj.s]
    meTools.Ctrl(name=obj.name+"_FK"+id+"_GRP",shape='null',tgt=obj.baseJ[0],parentSpace=obj.utilsTop,orientMatch=obj.baseJ[0],attr="ctrl_body_"+id,vis=1,lockType='s%v')
    meBuildTools.Joints(obj,'IK',ps=True,plug=True)
    
    #meBuildTools.Joints(obj,[obj.baseJ[0],obj.baseJ[1]],obj.name+'_IK',obj.name+"_FK"+id+"_GRP",1)    
    m.ikHandle(sj=obj.IKJ[0],ee=obj.IKJ[1],sol="ikSCsolver",n=obj.name+'_ikHandle'+id)
    
    color = ''

    if id != '':
        color = obj.colors['PrimaryLR'][id]
    else:
        color = 'green'

    meTools.Ctrl(name=obj.name+id+"_FK",axis='x',shape='circle',color=color,tgt=obj.name+"_FK"+id+"_GRP",connection='cp',parentSpace='%'+obj.controlsTop,orientMatch=obj.baseJ[0],attr="ctrl_body_"+id,vis=1)

    meTools.Ctrl(name=obj.ikHandles[0]+id+"_IK",
                shape='box',
                color=color,
                tgt=obj.name+'_ikHandle'+id,
                connection='ct',
                parentSpace='%'+obj.name+id+"_FK",
                orientMatch=obj.baseJ[-1],
                attr="ctrl_body_"+id,
                vis=1)    

    obj.ikHandle = obj.ikHandles[0]+id+"_IK"
    m.rename(obj.IKJ[0],obj.RigJ[0])
    

    m.parent(obj.name+'_ikHandle'+id,obj.name+'_FK'+id+"_GRP")    
    m.parentConstraint(obj.name+id+'_plug_start_IN',obj.RigJ[0])
    m.parentConstraint(obj.ikHandles[0]+id+"_IK",obj.name+id+'_plug_end_OUT',mo=True)

def FKIK_singleHinge(obj):

    FKIK(obj)

    meBuildTools.FKIK.Stretch(obj,obj.sides[obj.s])

    meBuildTools.FKIK.Scale(obj,obj.sides[obj.s])

    if 'roll' in obj.extraInfo:
        if obj.extraInfo['roll']:
            meBuildTools.FKIK.Bendy(obj)


def FKIK_doubleHinge(obj):
    
        
    FKIK(obj)

    meBuildTools.FKIK.Stretch(obj,obj.sides[obj.s])
    
  
    meBuildTools.Joints(obj,'PreIK',ps=True,plug=True) 

    handle = obj.ikHandle.replace(obj.id+'_CTRL','_ikHandle'+obj.id)
    m.delete(handle)
    
    PV_CTRL = obj.ikHandle.replace('_CTRL','_PV_CTRL')

    m.ikHandle( sj=obj.PreIKJ[0], ee=obj.PreIKJ[3],n=handle, sol='ikRPsolver')

    

    
    m.ikHandle( sj=obj.IKJ[0], ee=obj.IKJ[2],n=handle+'_B', sol='ikRPsolver')
    m.poleVectorConstraint(PV_CTRL,handle)
    m.poleVectorConstraint(PV_CTRL,handle+'_B')

    m.parentConstraint(obj.ikHandle,handle,mo=True)


    m.group(em=True,n=handle+'_aim_Space')
    m.delete(m.parentConstraint(obj.ikHandle,handle+'_aim_Space'))
    
    m.parentConstraint(obj.ikHandle,handle+'_aim_Space')
    m.duplicate(handle+'_aim_Space',n=handle+'_aim',po=True)
    m.duplicate(handle+'_aim_Space',n=handle+'_rotate_Space')
    
    m.parent(handle+'_aim',handle+'_aim_Space')

    #aim constraint from aim group to 

    m.aimConstraint(obj.PreIKJ[2],handle+'_aim',aimVector=(1*obj.polarity,0,0),upVector=[0,0,-1],wu=[0,0,-1],worldUpType='objectRotation',wuo=obj.ikHandle)
    m.aimConstraint(obj.ikHandle,obj.IKJ[2],aimVector=(1*obj.polarity,0,0),upVector=[0,0,-1],wu=[0,0,-1],worldUpType='objectRotation',wuo=obj.ikHandle)

  
    m.parent(handle+'_rotate_Space',handle+'_aim')
    m.duplicate(handle+'_rotate_Space',n=handle+'_rotate')
    m.parent(handle+'_rotate',handle+'_rotate_Space')
    
    m.parent(handle+'_B',handle+'_rotate')
    
    m.connectAttr(obj.ikHandle+'.rx',handle+'_rotate.rx')
    m.connectAttr(obj.ikHandle+'.ry',handle+'_rotate.ry')
    m.connectAttr(obj.ikHandle+'.rz',handle+'_rotate.rz')
    
    m.parent(handle,handle+'_aim_Space',obj.utilsTop)








def FKIK_spline(obj):
        fkDivisions = obj.fkSegments                            
        incr = 0
        pos = ('A','B','C','D','E','F','G','H','I','J','K','L')
        segments = fkDivisions + 1

        #setup spline
        meBuildTools.Joints(obj,'Rig')
        
        meBuildTools.Spline(obj,joints=obj.baseJ,sine=True)
        crvLen = m.getAttr (obj.name+'Spline_ALR.uParamValue')
        # start = m.xform(obj.baseJ[0],q=True,t=True,ws=True)        
        # end = m.xform(obj.baseJ[-1],q=True,t=True,ws=True)
        # mid = [0,0,0]
        # mid[0] = (end[0]-start[0])*0.5
        # mid[1] = (end[1]-start[1])*0.5
        # mid[2] = (end[2]-start[2])*0.5
        # tempCrv = m.curve(n='tempCurve',d=1,p=(start,mid,end),k=[0,1,2])

        # m.error()
        #setup three joint IK spline driver
        m.duplicate(obj.joints[0],n=obj.IKJ[0],po=True)
        m.parent(obj.IKJ[0],obj.name+'_Utils')      
        m.duplicate(obj.joints[-1],n=obj.IKJ[-1],po=True)        
        m.duplicate(obj.joints[-1],n=obj.name+'_IK_mid_Space',po=True)
        constraintA = m.parentConstraint(obj.IKJ[-1],obj.name+'_IK_mid_Space')
        constraintB = m.parentConstraint(obj.IKJ[0],obj.name+'_IK_mid_Space')
        m.delete(constraintA,constraintB)
        m.select(obj.name+'_IK_mid_Space')
        m.joint(n=obj.name+'_IK_mid')
        
        m.parent(obj.IKJ[-1],w=True)
        m.parent(obj.name+'_IK_mid_Space',w=True)
        
        m.skinCluster( obj.IKJ[0], obj.IKJ[-1],obj.name+'_IK_mid',obj.name+'Spline_crv',sw=True,tsb=True,n=obj.name+'Spline_SkinCluster')
        
        m.duplicate(obj.name+'_IK_mid_Space',n=obj.name+'_IK_midTop',po=True)
        m.parent(obj.name+'_IK_midTop',obj.IKJ[-1])
        m.parentConstraint(obj.name+'_IK_midTop',obj.name+'_IK_mid_Space')

        m.duplicate(obj.name+'_IK_mid_Space',n=obj.name+'_IK_midBtm',po=True)
        m.parent(obj.name+'_IK_midBtm',obj.IKJ[0])
        m.parentConstraint(obj.name+'_IK_midBtm',obj.name+'_IK_mid_Space')


        m.parent(obj.IKJ[-1],obj.IKJ[0])
        m.parent(obj.name+'_IK_mid_Space',obj.IKJ[0])


        #FK
        topFk = ''
        for i in range(fkDivisions+1):
            if i != 0:
              poc = (m.pointOnCurve (obj.name+'Spline_crv', pr = (crvLen / segments) + incr))
              meTools.Ctrl(name=obj.name+'_FK_'+pos[i - 1],axis='z',shape='pin',color='red',parentSpace='space',orientMatch=obj.joints[1],attr='ctrl_body',vis=1,lockType='t%s%v')
              topFk = obj.name+'_FK_'+pos[i - 1]
              m.setAttr(obj.name+'_FK_'+pos[i - 1]+"_Space.t",poc[0],poc[1],poc[2])                            
              if i > 1:
                m.parent(obj.name+'_FK_'+pos[i-1]+'_Space',obj.name+'_FK_%s' % pos[i-2])

              else:
                m.parent(obj.name+'_FK_'+pos[i-1]+'_Space',obj.name+'_Controls')   
              incr = (incr + (crvLen / segments))
              i += 1            


        #IK
        

        #deterime parent space switch setup:
        follows=[]
        if obj.isTop:
            obj.parentSpaceSwitch.remove('RigRoot')
            follows = obj.parentSpaceSwitch
        else:
            follows = obj.parentSpaceSwitch
            follows[1] = obj.inPlug
        
        follows.append(obj.ikHandles[0])
        follows.append(topFk)



        
        meTools.Ctrl(name=obj.ikHandles[0]+'_IK',
                    axis='x',
                    shape='circle',
                    color='green',
                    tgt=obj.IKJ[0],
                    parentSpace='%'+obj.name+'_Controls',
                    attr="ctrl_body_c",
                    vis=1,
                    lockType="s%v")

        meTools.Ctrl(name=obj.ikHandles[0],
                    shape='box',
                    color='yellow',
                    tgt=obj.IKJ[0],
                    parentSpace='%'+obj.name+'_Controls',
                    attr="ctrl_body_c",
                    vis=1,
                    lockType="s%v",
                    orientMatch='WorldOffset',
                    pivot=True)

        meTools.Ctrl(name=obj.ikHandles[1],
                    shape='box',
                    color='yellow',
                    tgt=obj.IKJ[-1],
                    parentSpace='%'+obj.name+'_Controls',
                    attr="ctrl_body_c",
                    vis=1,
                    lockType="s%v",
                    pivot=True,
                    pss=follows,
                    orientMatch='WorldOffset')

        meTools.Ctrl(name=obj.name+'_mid_IK',
                    axis='x',
                    shape='circle',
                    color='green',
                    tgt=obj.name+'_IK_mid',
                    parentSpace='%'+obj.name+'_Controls',
                    attr="ctrl_body_c",
                    vis=1,
                    lockType="s%v")

        
        obj.ikHandle = obj.ikHandles[1]
        m.delete(m.orientConstraint('WorldOffset',obj.ikHandles[0]+'_IK_Space'))

        m.addAttr(obj.name+'_mid_IK',ln='topBtmFollow',min=0,max=1,dv=0.5,k=True)
        meTools.Node('reverse', obj.name+'_IK_mid_REV',
                                  connA= [obj.name+'_mid_IK.topBtmFollow',obj.name+'_IK_mid_REV.inputX'],
                                  connB= [obj.name+'_IK_mid_REV.outputX',obj.name+'_IK_mid_Space_parentConstraint1.'+obj.name+'_IK_midTopW0'],
                                  connC= [obj.name+'_mid_IK.topBtmFollow',obj.name+'_IK_mid_Space_parentConstraint1.'+obj.name+'_IK_midBtmW1'])   

        m.pointConstraint(obj.name+'_IK_mid_Space',obj.name+'_mid_IK_Space')
        m.parentConstraint(obj.name+'_mid_IK',obj.name+'_IK_mid')

        for ctrl in obj.ikHandles:
            m.addAttr(ctrl,ln="ikRotateOrder",at="enum",en="xyz=0:yzx=1:zxy=2:xzy=3:yxz=4:zyx=5:",k=False)
            m.setAttr(ctrl+".ikRotateOrder",channelBox=True)
            m.connectAttr(ctrl+".ikRotateOrder",ctrl+'.rotateOrder')

        m.addAttr(obj.ikHandles[0],ln='squashAmt',min=0,max=1,dv=0.5,k=True)
        m.addAttr(obj.ikHandles[0],ln='squashBias',min=0,max=1,dv=0.5,k=True)
        m.addAttr(obj.ikHandles[0],ln='stretchAmt',min=0,max=1,dv=1,k=True)
        
        #connect stretch amt attr
        meTools.Node(  'remapValue',
                        obj.name+'_lenRatio_Fader_RMP',
                        connA= [obj.name+'_lenRatio_Fader_RMP.outValue',obj.name+'CurveLengthRatio_MD.input1X'],
                        attrA= ['outputMin',m.getAttr(obj.name+'Spline_stretchRatio_arc.uParamValue')],
                        connB= [obj.name+'Spline_stretchRatio_arc.arcLength', obj.name+'_lenRatio_Fader_RMP.outputMax'],
                        attrB= ['inputValue',1]  )

        m.rename(obj.name+'_Rig_'+obj.idJ[-1],'Spline_'+obj.name+'_End')
        m.rename(obj.IKJ[-1],obj.name+'_Rig_'+obj.idJ[-1])

        #connect controls                
        m.parentConstraint(obj.ikHandles[0]+'_IK',obj.IKJ[0],mo=True)
        m.parentConstraint(obj.ikHandles[1],obj.name+'_Rig_'+obj.idJ[-1],mo=True)
        
        m.parent(obj.ikHandles[1]+'_Space',obj.name+'_FK_'+pos[fkDivisions-1])
        m.parent(obj.ikHandles[0]+'_IK_Space',obj.name+'_FK_'+pos[0]+'_Space',obj.ikHandles[0])                       
        m.parentConstraint(obj.ikHandles[0]+'_IK',obj.name+'_twistStart',mo=True)
        m.parentConstraint(obj.ikHandles[-1],obj.name+'_twistEnd',mo=True)
        
        m.connectAttr(obj.ikHandles[0]+".squashAmt", '%s_Squash_Envelope_RVL.inputValue' % obj.name) 
        m.parentConstraint(obj.name+'_plug_start_IN',obj.ikHandles[0]+'_Space',mo=True)
        m.parentConstraint(obj.name+'_Rig_'+obj.idJ[-1],obj.name+'_plug_end_OUT')

        m.rename(obj.name+'_Rig_'+obj.idJ[0],'Spline_'+obj.name+'_Start')
        m.rename(obj.IKJ[0],obj.name+'_Rig_'+obj.idJ[0])


#def SingleFKIK(obj):


def INV_foot(obj):
    id = obj.sides[obj.s]
    incr = ''
    utils=obj.utilsTop    
            
    #BUILD JOINTS AND CONNECT VIA PB
    meBuildTools.Joints(obj,'FK',ps=True,plug=True)
    meBuildTools.Joints(obj,'IK',ps=True,plug=True)
    meBuildTools.Joints(obj,'Post_IK',ps=True,plug=True)
    meBuildTools.Joints(obj,'Rig',ps=True,plug=True)

    meTools.Ctrl(name=obj.name+id+"_SW",axis='y',shape='circle',color=obj.colors['PrimaryLR'][id],tgt=obj.baseJ[0],parentSpace='%'+obj.controlsTop,attr='ctrl_body_'+id,vis=1,lockType='all')
    m.addAttr(obj.name+id+"_SW",ln='FK_IK',k=True,min=0,max=1,dv=1)
    prefix = ''

    for ea in obj.coreJoints:
        ea += id
        meTools.Node('pairBlend', obj.name+'_'+ea+"_BLN",attrA= ['weight',0.5],attrB= ['rotInterpolation',1])
          
        for ax in ['x','y','z']:
            cmds.connectAttr(obj.name+'_FK_'+ea+'.r'+ax,obj.name+'_'+ea+'_BLN.inRotate'+ax.upper()+'1')
            cmds.connectAttr(obj.name+'_Post_IK_'+ea+'.r'+ax, obj.name+'_'+ea+'_BLN.inRotate'+ax.upper()+'2')
            cmds.connectAttr(obj.name+'_'+ea+'_BLN.outRotate'+ax.upper(),obj.name+'_Rig_'+ea+'.r'+ax)

        connectAttr(obj.name+id+'_SW.FK_IK', obj.name+'_'+ea+'_BLN.weight')

    #BUILD INVERSE DRIVER HEIRARCHY
    previous = obj.utilsTop      
    spaces = ("ankle:ankle","heel%_Space:heel","heel:heel","toe%_Space:toe","ballPivot:ball","toePivot:toe","toe:toe","ball:ball")
    for ea in spaces:
        pair = ea.split(':') 
        split = pair[0].split('%')
        if len(split) == 2:
            object = split[0]+id+split[1]
        else:
            object = split[0]+id                       
        m.select(previous)
        m.joint(n='INV_IK_'+object)            
        if ea == spaces[-3]:
            m.parent('INV_IK_'+object,'INV_IK_'+spaces[-6].split(':')[0]+id)
            m.setAttr('INV_IK_'+object+'.r',0,0,0)
            m.setAttr('INV_IK_'+object+'.jointOrient',0,0,0)
            m.parent('INV_IK_'+object,previous)

        m.delete(m.parentConstraint('base_'+obj.name+'_'+pair[1]+id,'INV_IK_'+object))
        previous = 'INV_IK_'+object

    m.ikHandle( sj=obj.IKJ[0], ee=obj.IKJ[1],n=obj.ikHandles[0]+id+'_A_IK', sol='ikRPsolver')
    m.parent(obj.ikHandles[0]+id+'_A_IK','INV_IK_'+obj.coreJoints[1]+id)
    m.ikHandle( sj=obj.IKJ[1], ee=obj.IKJ[2],n=obj.ikHandles[0]+id+'_B_IK', sol='ikRPsolver')
    m.parent(obj.ikHandles[0]+id+'_B_IK','INV_IK_'+obj.coreJoints[2]+id)   

    m.parentConstraint(obj.name+id+'_plug_start_IN','INV_IK_'+obj.coreJoints[0]+id, mo=True)
  
    attrs = {'heelPivot':'INV_IK_heel_id_.rotateZ' ,
          'ballPivot':'INV_IK_ballPivot_id_.rotateZ',
          'toePivot':'INV_IK_toePivot_id_.rotateZ',
          'footRoll':'FootINV_IK_id__CLMP.inputR',
          'ballRoll':'INV_IK_ballPivot_id_.rotateY' ,
          'toeRoll':'INV_IK_toe_id_.rotateY',
          'tilt':'INV_IK_heel_id_.rotateX'}

    #CONNECT TO FOOT ATTRS
    meTools.Node('clamp',obj.name+'INV_IK'+id+'_CLMP',attrA=['minR',-180],attrB=['maxG',180],attrC=['minG',0])
    footAttrs = ['ball','toe','heel','foot']
    for attr in attrs:  
      m.addAttr(obj.name+id+'_plug_start_IN',ln=attr,at='double',min=-180,max=180,dv=0,k=1);
      
      for footAttr in footAttrs:
        if footAttr in attr:
            if not m.objExists(footAttr+id+'_PR'):                    
                tgt = footAttr
                if footAttr == 'foot':
                    tgt = 'ankle'
                meTools.Ctrl(name=footAttr+id+'_PR',axis='x',shape='3qtArrow',color=obj.colors['PrimaryLR'][id],tgt='base_'+obj.name+'_'+tgt+id ,parentSpace='%'+'Foot_Controls'+id,attr="ctrl_body_"+id,vis=1,lockType="t%s%v")
                cmds.connectAttr(obj.name+id+'_SW.FK_IK',footAttr+id+'_PR_Space.v')

                    
      
      if attrs[attr] != '':
          conn = attrs[attr].split('_id_')               
          m.connectAttr(obj.name+id+'_plug_start_IN'+'.'+attr,conn[0]+id+conn[1])

    for footAttr in footAttrs:
        m.setAttr(footAttr+id+'_PR.rotateX',l=True,k=False)
        if m.objExists(obj.name+id+'_plug_start_IN'+'.'+footAttr+'Roll'):
            m.connectAttr(footAttr+id+'_PR.rotateY',obj.name+id+'_plug_start_IN'+'.'+footAttr+'Roll')
        else:
            m.setAttr(footAttr+id+'_PR.rotateY',l=True,k=False)
        if m.objExists(obj.name+id+'_plug_start_IN'+'.'+footAttr+'Pivot'):
            m.connectAttr(footAttr+id+'_PR.rotateZ',obj.name+id+'_plug_start_IN'+'.'+footAttr+'Pivot')


    m.connectAttr('foot'+id+'_PR.rotateZ',obj.name+id+'_plug_start_IN'+'.tilt')
    m.setAttr (obj.name+'INV_IK'+id+'_CLMP.maxR',0)        
    m.connectAttr (obj.name+id+'_plug_start_IN'+'.footRoll' , obj.name+'INV_IK'+id+'_CLMP.inputG')
    m.connectAttr (obj.name+'INV_IK'+id+'_CLMP.outputR' ,'INV_IK_'+obj.coreJoints[1]+id+'.rotateY' )   
    m.connectAttr (obj.name+'INV_IK'+id+'_CLMP.outputG' ,'INV_IK_'+obj.coreJoints[2]+id+'.rotateY' )   
    
    m.parentConstraint('INV_IK_'+obj.coreJoints[2]+id,obj.PIKJ[0],mo=True)
    m.parentConstraint('INV_IK_'+obj.coreJoints[3]+id,obj.PIKJ[2],mo=True)

    m.parentConstraint('INV_IK_'+obj.coreJoints[2]+id,obj.name+id+'_plug_start_OUT',mo=True)
    m.pointConstraint(obj.PIKJ[0],obj.RigJ[0])

    m.parentConstraint(obj.RigJ[0],obj.name+id+'_plug_end_OUT')

    #add FK control to ball
    meBuildTools.FKChain(obj)
    
    #hide the FK/IK switch as it is connected to the parent rig's switch 
    m.connectAttr(obj.connectedToObj.name+'_'+obj.connectedToObj.coreJoints[-1]+id+"_CTRL_SW.FK_IK",obj.name+id+'_SW.FK_IK')
    m.setAttr(obj.name+id+"_SW_Space.v",0)

    pcon = m.pointConstraint(obj.connectedToObj.name+'_FK_'+obj.connectedToObj.coreJoints[-1]+id, obj.RigJ[0])[0]

    meTools.Node('reverse',obj.name+id+'_RigLink_REV',connA=[obj.connectedToObj.name+'_'+obj.connectedToObj.coreJoints[-1]+id+"_CTRL_SW.FK_IK",
                                                        obj.name+id+'_RigLink_REV.inputX'],
                                                    connB=[obj.name+id+'_RigLink_REV.outputX',
                                                        pcon+'.'+obj.connectedToObj.name+'_FK_'+obj.connectedToObj.coreJoints[-1]+id+'W1'],
                                                    connC=[obj.name+id+'_RigLink_REV.outputX',
                                                        obj.name+'_FK_'+obj.coreJoints[0]+id+'_CTRL_Space.v'])


    #a bunch of stuff is reconnected to make the reverse ik drive the parent
    #m.parentConstraint(obj.connectedToObj.name+id+'_plug_end_IN',obj.connectedToObj.name+id+'_lenRatio_end')

    # for ea in obj.connectedToObj.IKJ:
    #     ea = ea.split('__')[0]+id
    #     print obj.connectedToObj.IKJ
    #     for a in ['X','Y','Z']:
    #         #print ea.replace('_IK','Rtrn_IK')+'.r'+a.lower()+"  TO  "+ea.replace('_IK','')+'_BLN.inRotate'+a+'2'
    #         m.connectAttr(ea.replace('_IK','Rtrn_IK')+'.r'+a.lower(),ea.replace('_IK','')+'_BLN.inRotate'+a+'2',f=True)

    m.connectAttr(obj.connectedToObj.name+'_'+obj.connectedToObj.coreJoints[-1]+id+"_CTRL_SW.FK_IK",
                    pcon+'.'+obj.name+'_Post_IK_'+obj.coreJoints[0]+id+'W0')
    

    
    

    m.pointConstraint(obj.connectedToObj.name+id+'_plug_end_OUT',obj.name+'_FK_'+obj.coreJoints[0]+id+'_CTRL_Space')
    #m.delete(obj.connectedToObj.name+id+'_plug_end_IN_parentConstraint1')

    m.pointConstraint(obj.name+id+'_plug_start_OUT',obj.connectedToObj.name+id+'_plug_end_IN')
    
    m.connectAttr(obj.connectedToObj.name+'_FK_'+obj.connectedToObj.coreJoints[-1]+id+'_CTRL.rx',
                         obj.name+'_FK_'+obj.coreJoints[0]+id+'_CTRL.rx')
    m.connectAttr(obj.connectedToObj.name+'_FK_'+obj.connectedToObj.coreJoints[-1]+id+'_CTRL.ry',
                         obj.name+'_FK_'+obj.coreJoints[0]+id+'_CTRL.ry')
    m.connectAttr(obj.connectedToObj.name+'_FK_'+obj.connectedToObj.coreJoints[-1]+id+'_CTRL.rz',
                         obj.name+'_FK_'+obj.coreJoints[0]+id+'_CTRL.rz')


    m.hide(obj.name+'_FK_'+obj.coreJoints[0]+id+'_CTRLShape')

