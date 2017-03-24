import meTools as meTools
reload(meTools)
import os as os
import sys
import maya.cmds as m
#execfile (scriptPath+"meBuildClasses.py")
from meBuildClasses import *

from pymel.core import *   
ids = {'_L':'blue','_R':'red'}
axes = {'x':'X','y':'Y','z':'Z'}
skelOO = {'base_clavicle_id':0,'base_shoulder_id':2,'base_elbow_id':2,'base_wrist_id':0,
          'base_hip_id':2,'base_knee_id':3,'base_ankle_id':3} 
ctrlOO = {'Hip':2,'Hip_IK':3,'hip_L_FK':3,'knee_L_FK':3,'ankle_L_FK':3,'foot_IK_L':3,'hip_R_FK':3,'knee_R_FK':3,'ankle_R_FK':3,
          'foot_IK_R':3,'Chest_IK':2,'Neck':4,'Neck_IK':4,'Head_IK':4,'clavicle_L_FK':0,'shoulder_L_FK':2,'elbow_L_FK':2,
          'wrist_L_FK':0,'clavicle_R_FK':0,'shoulder_R_FK':2,'elbow_R_FK':2,'wrist_L_FK':0}          
          
def meBuild(what,roll,name,commands):              
    rigObject = commands[what][1]
    rigObject.charName = name
    print "name is---"+rigObject.name
    if commands[what][2]== 1:
        for id in ids:
            if commands[what][0] == 'FKIK':                
                rigObject.assignDetails(id,roll)
                Clavicle.assignDetails(id,roll)
            else:
                rigObject.assignDetails(id)    
            runCommand = 'meMake'+commands[what][0]+'(rigObject)'
            meTools.meFramework(rigObject)
            exec(runCommand)
    else:    
        runCommand = 'meMake'+commands[what][0]+'(rigObject)'
        meTools.meFramework(rigObject)
        exec(runCommand)   

def meMakeSpaceSwitch(what,**kwargs):
        cnst = ''
        follows = []
        if type(what) == type(''):
            ctrl = what.split('|')[0]
            space = ctrl+'_Space'
            follows = what.split('|')[1].split(',')
            #nasty but necessary temp condition:
            side = kwargs['side']
            if 'Arm_ikHandle'+side in follows:               
                follows.remove('Arm_ikHandle'+side)
        else:
            follows = what.defIkFollow
            space = what.ik+'_IK'+what.side+'_Space'
            ctrl = what.ik+'_IK'+what.side
        for ea in follows:
            cnst = m.parentConstraint(ea,space,mo=True)[0]
       
        m.addAttr(ctrl,ln='parentSpace',at='enum',en=':'.join(follows)+':',k=0)
        m.setAttr(ctrl+'.parentSpace',cb=True)
        i = 0
        stSwitch = ''
        
        expressionBody = []
        for ea in follows:
            stSwitch = '\nif ('+ctrl+'.parentSpace == '+str(i)+'){\n'
            setAttrLine = []
            j = 0
            for prnt in follows:
                k = 0 
                if i == j: 
                    k = 1
                setAttrLine.append(cnst+'.'+prnt+'W'+str(j)+' = '+str(k)+';\n')
                j += 1
            expressionBody.append(stSwitch+''.join(setAttrLine)+'}')
            i += 1

        result = '{'+''.join(expressionBody)+'}'
        m.expression( s=result )


def subFKIK(what,**kwargs):   
    spacer = ''    
    
    
    if 'manualMode' in kwargs.keys():
        sJoints = kwargs['sJoints']
        defIkFollow = kwargs['defIkFollow']
        ik = kwargs['ik']
        ikHandleOrienter = kwargs['ikHandleOrienter']
        pvPositionOffset = kwargs['pvPositionOffset']
        switchDefault= kwargs['switchDefault']
        ctrlParent = kwargs['ctrlParent']
        name = kwargs['name']
        utils = '%'+kwargs['utils']
        ctrlParentGRP = '%'+kwargs['ctrlParent']
        pvAngle = kwargs['pvAngle']


    else:
        ik = what.ik
        sJoints = what.sJoints
        ikHandleOrienter = what.ikHandleOrienter
        pvPositionOffset = what.pvPositionOffset
        switchDefault = what.switchDefault
        defIkFollow = what.defIkFollow
        ctrlParent = what.ctrlParent
        name = what.name
        utils = '%'+name+what.side+"_Extras"
        ctrlParentGRP = '%'+name+what.side+'_Controls'
        pvAngle = (0,0,1)

    #FK
    print sJoints
    meTools.meJoints(what,['base_'+sJoints[0],'base_'+sJoints[-1]],'FK',utils,1)
    
    #IK
    meTools.meJoints(what,['base_'+sJoints[0],'base_'+sJoints[-1]],'IK',utils,1)    
    m.ikHandle(sj='IK_'+sJoints[0],ee='IK_'+sJoints[-1],n=name+"_ikHandle"+what.side,sol='ikRPsolver')        
    handles = [name+"_ikHandle"+what.side]
    m.parent(name+"_ikHandle"+what.side,utils.replace('%',''))

    #PV
    alpha = ['A','B']
    flipDir = [1,-1]
    i = 0
    for handle in handles:        
        #meTools.meMakeCurves(ik+'_PV'+alpha[i]+what.side,'','diamond',ids[what.side],'','',ctrlParentGRP,'','',1,"s%r%v")
        meTools.makeCtrl(name=ik+'_PV'+alpha[i]+what.side,shape='diamond',color=ids[what.side],parentSpace=ctrlParentGRP,vis=1,lockType='s%r%v')
        cnst = meTools.mePC(ik+'_PV'+alpha[i]+what.side+'_Space','base_'+sJoints[1],0)
        pvPosition = [pvPositionOffset*flipDir[i]*pvAngle[0],pvPositionOffset*flipDir[i]*pvAngle[1],pvPositionOffset*flipDir[i]*pvAngle[2]]

        m.move (pvPosition[0],pvPosition[1],pvPosition[2],ik+'_PV'+alpha[i]+what.side+'_Space',r=True,os=True)
        m.poleVectorConstraint(ik+'_PV'+alpha[i]+what.side,handle)
        if type(defIkFollow) != type(''):
            meMakeSpaceSwitch(ik+'_PV'+alpha[i]+what.side+'|'+','.join(defIkFollow)+','+handle,side=what.side)
        i += 1

    #BLEND
    meTools.meJoints(what,['base_'+sJoints[0],'base_'+sJoints[-1]],'Rig',utils,1)
    for ea in sJoints:
        if ea == sJoints[-1]: spacer = "_Spacer"
        for ax in axes:
            meTools.meCreateNodeB('pairBlend',ea+"_BLN",
                                attrA= ['weight',0.5],
                                attrB= ['rotInterpolation',0],
                                connA= ['FK_'+ea+'.r'+ax,ea+'_BLN.inRotate'+axes[ax]+'1'],
                                connB= [ea+'_BLN.outRotate'+axes[ax],'Rig_'+ea+'.r'+ax],
                                connC= ['IK_'+ea+spacer+'.r'+ax,ea+'_BLN.inRotate'+axes[ax]+'2'])
                
    #meTools.meMakeCurves(ik+what.side+"_SW",'y','circle',ids[what.side],ikHandleOrienter,'',ctrlParentGRP,'',"ctrl_body_"+what.side,1,"all")
    meTools.makeCtrl(name=ik+what.side+"_SW",axis='y',shape='circle',color=ids[what.side],tgt=ikHandleOrienter,parentSpace=ctrlParentGRP,attr='ctrl_body_'+what.side,vis=1,lockType='all')

    m.parentConstraint('Rig_'+sJoints[-1],ik+what.side+"_SW_Space")
    
    if m.objExists(name+what.side+'_plug_end_OUT'):
        m.parentConstraint('Rig_'+sJoints[-1],name+what.side+'_plug_end_OUT')
    
    m.addAttr(ik+what.side+'_SW',ln='FK_IK',min=0,max=1,dv=switchDefault,k=1)            
    meTools.meCreateNodeB('reverse',ik+what.side+'_SW_REV',connA= [ik+what.side+'_SW.FK_IK',ik+what.side+'_SW_REV.inputX'])            
            
    for ea in what.joints:
        connectAttr(ik+what.side+'_SW.FK_IK',ea+what.side+'_BLN.weight')                               

    #FK CONTROLS
    parent = ctrlParent
    for ea in sJoints:
        #meTools.meMakeCurves(ea+"_FK",'x','circle',ids[what.side],'FK'+'_'+ea,'dr','%'+parent,'',"ctrl_body_"+what.side,1,"t%s%v")
        meTools.makeCtrl(name=ea+"_FK",axis='x',shape='circle',color=ids[what.side],tgt='FK'+'_'+ea,connection='dr',parentSpace='%'+parent,attr='ctrl_body_'+what.side,vis=1,lockType='t%s%v')
        parent = ea+'_FK'
        m.addAttr(ea+"_FK",ln="fkRotateOrder",at="enum",en="xyz=0:yzx=1:zxy=2:xzy=3:yxz=4:zyx=5:",k=False)
        m.setAttr(ea+"_FK.fkRotateOrder",channelBox=True)
        m.connectAttr(ea+"_FK.fkRotateOrder",ea+'_FK.rotateOrder')
        m.connectAttr(ea+"_FK.fkRotateOrder",'FK'+'_'+ea+'.rotateOrder')
        m.connectAttr(ea+"_FK.fkRotateOrder",'Rig'+'_'+ea+'.rotateOrder')
        connectAttr(ik+what.side+'_SW_REV.outputX',ea+"_FK_Space.v")     
            
    #IK CONTROLS
    #meTools.meMakeCurves(ik+'_IK'+what.side,'','box',ids[what.side],name+"_ikHandle"+what.side,'',ctrlParentGRP,ikHandleOrienter,"ctrl_body_"+what.side,1,"s%v",pivot=True)
    meTools.makeCtrl(name=ik+'_IK'+what.side,shape='box',color=ids[what.side],tgt=name+"_ikHandle"+what.side,parentSpace=ctrlParentGRP,orientMatch=ikHandleOrienter,attr="ctrl_body_"+what.side,vis=1,lockType='s%v',pivot=True)
    m.parentConstraint(ik+'_IK'+what.side,'IK_'+sJoints[-1]+'_Spacer',mo=True)
    m.parentConstraint(ik+'_IK'+what.side,name+"_ikHandle"+what.side)    
    m.connectAttr(ik+what.side+'_SW.FK_IK',ik+'_IK'+what.side+'_Space.v')
    m.addAttr(ik+'_IK'+what.side,ln="ikRotateOrder",at="enum",en="xyz=0:yzx=1:zxy=2:xzy=3:yxz=4:zyx=5:",k=False)
    m.setAttr(ik+'_IK'+what.side+".ikRotateOrder",channelBox=True)
    m.connectAttr(ik+'_IK'+what.side+".ikRotateOrder",ik+'_IK'+what.side+'.rotateOrder')
    
    #add space swich
    if type(defIkFollow) == type(''):
        m.parentConstraint(defIkFollow,ik+'_IK'+what.side+'_Space',mo=True)
    else:
        meMakeSpaceSwitch(what)
        
    if 'manualMode' not in kwargs.keys():
        meTools.mePlugTo(what) 
        meTools.mePlugRigs(what)
    
    if name == "Arm":
        meTools.meFramework(Clavicle)
        meMakeSingleFKIK(Clavicle)

def meMakeFKIK(what,**kwargs):
    id = what.side
    handles = [what.name+"_ikHandle"+what.side]
    spacer = ''    
    flip = 1

    alpha = ['A','B']

    if id == '_R':
        flip = -1
    #FK
    subFKIK(what)
    
    meTools.meMakeIKStretch(what,id)    
    #MAKE BENDYS   
    incr = ''   
    id = what.side
    radius = m.getAttr('base_'+what.sJoints[0]+'.radius')
    obj = 'start'    
    flip = 1
        
    # Build spline curve and joint set at origin
    for j in range(len(what.joints)-1):
        length  = what.lengths[j]*(what.roll+1)
        curve(p=([0,0,0],[length*0.5,0,0],[length,0,0]),n=what.sJoints[j]+'_bendy_crv',d=2)
        shape = m.listRelatives(what.sJoints[j]+'_bendy_crv',c=True)
        m.rename(shape, what.sJoints[j]+'_bendy_crvShape')    
        m.joint(n='Bendy_'+what.sJoints[j]+"_start",p=[0,0,0],rad=radius)
        m.joint(n='Bendy_'+what.sJoints[j]+"_end",p=[(length/(what.roll+1)),0,0],rad=radius)
        insertFrom = 'Bendy_'+what.sJoints[j]+"_start"
        
        for i in range(what.roll):
            m.insertJoint(insertFrom)
            m.rename('Rig_'+what.sJoints[j]+"_Roll_"+str(i))
            m.setAttr('Rig_'+what.sJoints[j]+"_Roll_"+str(i)+'.tx',length/(what.roll+1))
            m.setAttr('Rig_'+what.sJoints[j]+"_Roll_"+str(i)+'.radius',radius)
            insertFrom = 'Rig_'+what.sJoints[j]+"_Roll_"+str(i)
        m.parent('Bendy_'+what.sJoints[j]+"_start",w=True)
                    
        # Setup stretchy spline
        if what.name == "Leg":
            if what.joints[j] == "knee":
                if id == '_R': flip = -1
        meTools.meStretchySpline(what,what.sJoints[j]+'_bendy','Bendy_'+what.sJoints[j]+"_start",'Bendy_'+what.sJoints[j]+"_end",what.sJoints[j]+'_bendy_crv',1,what.name+id+'_Extras',flip)        

        # Position spline            
        meTools.mePC('Bendy_'+what.sJoints[j]+"_start",'base_'+what.sJoints[j],0)
        meTools.mePC(what.sJoints[j]+'_bendy_crv','base_'+what.sJoints[j],0)
        
        if id == '_R':
            m.rotate(0,180,0,'Bendy_'+what.sJoints[j]+"_start",r=True,os=True)
            m.rotate(0,180,0,what.sJoints[j]+'_bendy_crv',r=True,os=True)
            
        # Setup bend joint
        m.select('Rig_'+what.sJoints[j])
        m.joint(n='Bend_'+what.sJoints[j]+'_Space',rad=radius)
        m.joint(n='Bend_'+what.sJoints[j],rad=radius)
        m.pointConstraint('Rig_'+what.sJoints[j],'Bend_'+what.sJoints[j]+'_Space') 
        m.pointConstraint('Rig_'+what.sJoints[j+1],'Bend_'+what.sJoints[j]+'_Space')
        m.orientConstraint('Rig_'+what.sJoints[j],'Bend_'+what.sJoints[j]+'_Space')
        m.parent(what.sJoints[j]+'_bendy_crv',what.name+id+"_Extras")
        m.parent('Bendy_'+what.sJoints[j]+"_start",what.name+id+"_Extras")            
        m.skinCluster('Rig_'+what.sJoints[j],'Rig_'+what.sJoints[j+1],'Bend_'+what.sJoints[j],what.sJoints[j]+'_bendy_crv',tsb=True,n=what.sJoints[j]+'_bendy_skinCluster')
        m.skinPercent(what.sJoints[j]+'_bendy_skinCluster',what.sJoints[j]+'_bendy_crv.cv[0]',tv=('Rig_'+what.sJoints[j],1))  
        m.skinPercent(what.sJoints[j]+'_bendy_skinCluster',what.sJoints[j]+'_bendy_crv.cv[1]',tv=('Bend_'+what.sJoints[j],1))    
        m.skinPercent(what.sJoints[j]+'_bendy_skinCluster',what.sJoints[j]+'_bendy_crv.cv[2]',tv=('Rig_'+what.sJoints[j+1],1))
    
    #meSquash
    print 'check '+what.name+what.side
    lastRoll = m.listRelatives('base_'+what.sJoints[-1],p=True)[0]

    meTools.meCreateNodeB('plusMinusAverage',what.name+what.side+'_TotalLength_PMA',connA=[what.sJoints[0]+'_bendySpline_stretchRatio_arc.arcLength',what.name+what.side+'_TotalLength_PMA.input2D[0].input2Dx'],
                                                                    connB=[what.sJoints[1]+'_bendySpline_stretchRatio_arc.arcLength',what.name+what.side+'_TotalLength_PMA.input2D[1].input2Dx'])
    
    strtLength = m.getAttr(what.sJoints[0]+'_bendySpline_stretchRatio_arc.arcLength')
    endLength = m.getAttr(what.sJoints[1]+'_bendySpline_stretchRatio_arc.arcLength')
    meTools.meCreateNodeB('multiplyDivide',what.name+what.side+'_TotalLength_MD',connA=[what.name+what.side+'_TotalLength_PMA.output2D.output2Dx',what.name+what.side+'_TotalLength_MD.input1X'],
                                                                 attrA=['input2X',strtLength+endLength],
                                                                 attrB=['operation',2])

    meTools.meSquash(what.name+what.side,'base_'+what.sJoints[0]+'_Roll_0',lastRoll,what.name+what.side+'_TotalLength_MD.outputX',1,.3,what.ctrls[1])
    m.parentConstraint('Rig_'+what.sJoints[1],what.sJoints[1]+'_bendyTwist_start')    
    m.parentConstraint('Rig_'+what.sJoints[0],what.sJoints[0]+'_bendyTwist_end')
    m.parentConstraint(what.name+id+'_plug_start_IN',what.sJoints[0]+'_bendyTwist_start')

    addAttr(what.ik+id+'_SW',ln="bendCtrlVisibility",at='enum',en='off:on:',k=0)
    m.setAttr(what.ik+what.side+'_SW.bendCtrlVisibility',cb=True)
    m.parentConstraint(what.ik+'_IK'+what.side,what.name+what.side+'_lenRatio_end')        

    for i in range(len(handles)):
        m.connectAttr(what.ik+id+'_SW.FK_IK',what.ik+'_PV'+alpha[i]+id+'_Space.v')
    m.addAttr(what.ik+'_IK'+id,ln='squashAmt',min=0,max=1,dv=0.5,k=True)
    m.addAttr(what.ik+'_IK'+id,ln='squashBias',min=0,max=1,dv=0.5,k=True)     
    m.connectAttr(what.ik+'_IK'+id+".squashAmt", '%s%s_Squash_Envelope_RVL.inputValue' % (what.name,id)) 
    m.addAttr(what.ik+'_IK'+id,ln='stretchAmt',min=0,max=1,dv=1,k=True)
    m.connectAttr(what.ik+'_IK'+id+".stretchAmt", '%s%s_lenRatio_Fader_RMP.inputValue' % (what.name,id)) 

    #BENDY CONTROLS
    for j in range(2):
        #meTools.meMakeCurves(what.sJoints[j]+"_Bend",'x','circle',ids[id],'Bend_'+what.sJoints[j],'dt','%'+what.name+id+'_Controls','',"ctrl_body_"+id,1,"r%s%v")
        meTools.makeCtrl(name=what.sJoints[j]+"_Bend",axis='x',shape='circle',color=ids[id],tgt='Bend_'+what.sJoints[j],connection='dt',parentSpace='%'+what.name+id+'_Controls',attr="ctrl_body_"+id,vis=1,lockType="r%s%v")
        m.parentConstraint('Bend_'+what.sJoints[j]+'_Space',what.sJoints[j]+"_Bend_Space")
        m.connectAttr(what.ik+id+'_SW.bendCtrlVisibility',what.sJoints[j]+'_Bend_Space.v')
   
    #ik twist follow
    if '_R' in what.side:
        flip = -1
    m.aimConstraint(what.ik+what.side+'_SW',what.sJoints[0]+'_bendyTwist_aim',aimVector=(1*flip,0,0), upVector = (0,1,0),wut='objectrotation',wuo=what.sJoints[0]+'_bendyTwist_start')
    m.addAttr(what.ik+id+'_SW',ln='twistFix',at='double',min=-180,max=180,dv=0,k=1)
    m.connectAttr(what.ik+id+'_SW.twistFix', what.sJoints[0]+'_bendyTwist_aim_aimConstraint1.offsetX')

    #limb twist upVectors
    if 'wrist' in what.sJoints[2]:
        m.parentConstraint('Rig_'+what.sJoints[2],what.sJoints[1]+'_bendyTwist_end')
    else:
        m.parentConstraint(what.ik+'_IK'+id,what.sJoints[-2]+'_bendyTwist_end')
  
 #   if what.name == "Arm":
    m.rename('Rig_'+what.sJoints[0],'Driver_'+what.sJoints[0])
    m.rename('Bendy_'+what.sJoints[0]+"_start",'Rig_'+what.sJoints[0])  

def meMakeFKIKSpline(what):
        fkDivisions = what.fkDiv                            
        incr = 0
        pos = ('low','mid','high')
        segments = fkDivisions + 0

        #setup spline       
        meSpline(what,sine=True,joints=what.joints)
        crvLen = m.getAttr (what.name+'Spline_ALR.uParamValue')

        #setup three joint IK spline driver
        m.duplicate('base_'+what.joints[0],n='IK_'+what.joints[0],po=True)
        m.parent('IK_'+what.joints[0],what.name+'_UTILS')      
        m.duplicate('base_'+what.joints[-1],n='IK_'+what.joints[-1],po=True)
        
        m.duplicate('base_'+what.joints[-1],n='IK_'+what.name+'_mid_Space',po=True)
        constraintA = m.parentConstraint('IK_'+what.joints[-1],'IK_'+what.name+'_mid_Space')
        constraintB = m.parentConstraint('IK_'+what.joints[0],'IK_'+what.name+'_mid_Space')
        m.delete(constraintA,constraintB)
        m.select('IK_'+what.name+'_mid_Space')
        m.joint(n='IK_'+what.name+'_mid')
        
        m.skinCluster( 'IK_'+what.joints[0], 'IK_'+what.joints[-1],'IK_'+what.name+'_mid',what.name+'splineCrv',sw=True,tsb=True,n=what.name+'Spline_SkinCluster')
        
        m.duplicate('IK_'+what.name+'_mid_Space',n='IK_'+what.name+'_midTop',po=True)
        m.parent('IK_'+what.name+'_midTop','IK_'+what.joints[-1])
        m.parentConstraint('IK_'+what.name+'_midTop','IK_'+what.name+'_mid_Space')

        m.duplicate('IK_'+what.name+'_mid_Space',n='IK_'+what.name+'_midBtm',po=True)
        m.parent('IK_'+what.name+'_midBtm','IK_'+what.joints[0])
        m.parentConstraint('IK_'+what.name+'_midBtm','IK_'+what.name+'_mid_Space')


        m.parent('IK_'+what.joints[-1],'IK_'+what.joints[0])
        m.parent('IK_'+what.name+'_mid_Space','IK_'+what.joints[0])


        #FK
        for i in range(fkDivisions+1):
            if i != 0:
              poc = (m.pointOnCurve (what.name+'splineCrv', pr = (crvLen / segments) + incr))
              #meTools.meMakeCurves(what.name+'_FK_'+pos[i - 1],'z','pin','red','','','space','base_'+what.joints[1],'ctrl_body',1,"t%s%v")
              meTools.makeCtrl(name=what.name+'_FK_'+pos[i - 1],axis='z',shape='pin',color='red',parentSpace='space',orientMatch='base_'+what.joints[1],attr='ctrl_body',vis=1,lockType='t%s%v')
              m.setAttr(what.name+'_FK_'+pos[i - 1]+"_Space.t",poc[0],poc[1],poc[2])                            
              if i > 1:
                m.parent(what.name+'_FK_'+pos[i-1]+'_Space',what.name+'_FK_%s' % pos[i-2])
              else:
                m.parent(what.name+'_FK_'+pos[i-1]+'_Space',what.name+'_Controls')   
              incr = (incr + (crvLen / segments))
              i += 1            

        #IK
        #meTools.meMakeCurves(what.ctrls[0],'x','circle','green','IK_'+what.joints[0],'','%'+what.name+'_Controls','',"ctrl_body_c",1,"s%v")
        meTools.makeCtrl(name=what.ctrls[0],axis='x',shape='circle',color='green',tgt='IK_'+what.joints[0],parentSpace='%'+what.name+'_Controls',attr="ctrl_body_c",vis=1,lockType="s%v")
        #meTools.meMakeCurves(what.ctrls[2],'','box','yellow','IK_'+what.joints[0],'','%'+what.name+'_Controls','',"ctrl_body_c",1,"s%v",pivot=True)        
        meTools.makeCtrl(name=what.ctrls[2],shape='box',color='yellow',tgt='IK_'+what.joints[0],parentSpace='%'+what.name+'_Controls',attr="ctrl_body_c",vis=1,lockType="s%v",pivot=True)
        #meTools.meMakeCurves(what.ctrls[1],'x','box','yellow','IK_'+what.joints[-1],'','%'+what.name+'_Controls','',"ctrl_body_c",1,"s%v",pivot=True)
        meTools.makeCtrl(name=what.ctrls[1],axis='x',shape='box',color='yellow',tgt='IK_'+what.joints[-1],parentSpace='%'+what.name+'_Controls',attr="ctrl_body_c",vis=1,lockType="s%v",pivot=True)
        #meTools.meMakeCurves(what.name+'_mid_IK','x','circle','green','IK_'+what.name+'_mid','','%'+what.name+'_Controls','',"ctrl_body_c",1,"s%v")
        meTools.makeCtrl(name=what.name+'_mid_IK',axis='x',shape='circle',color='green',tgt='IK_'+what.name+'_mid',parentSpace='%'+what.name+'_Controls',attr="ctrl_body_c",vis=1,lockType="s%v")
        m.delete(m.orientConstraint('WorldOffset',what.ctrls[1]+'_Space'))
        m.delete(m.orientConstraint('WorldOffset',what.ctrls[2]+'_Space'))

        m.parentConstraint('IK_'+what.name+'_mid_Space',what.name+'_mid_IK_Space')
        m.parentConstraint(what.name+'_mid_IK','IK_'+what.name+'_mid')


        for ctrl in what.ctrls:
            m.addAttr(ctrl,ln="ikRotateOrder",at="enum",en="xyz=0:yzx=1:zxy=2:xzy=3:yxz=4:zyx=5:",k=False)
            m.setAttr(ctrl+".ikRotateOrder",channelBox=True)
            m.connectAttr(ctrl+".ikRotateOrder",ctrl+'.rotateOrder')

        m.addAttr(what.ctrls[1],ln='squashAmt',min=0,max=1,dv=0.5,k=True)
        m.addAttr(what.ctrls[1],ln='squashBias',min=0,max=1,dv=0.5,k=True)
        m.addAttr(what.ctrls[1],ln='stretchAmt',min=0,max=1,dv=1,k=True)
        #m.addAttr(what.ctrls[1],ln='splineEndTangent',min=0.1,max=1,dv=0.5,k=True)
        
        #connect stretch amt attr
        meTools.meCreateNodeB(  'remapValue',
                        what.name+'_lenRatio_Fader_RMP',
                        connA= [what.name+'_lenRatio_Fader_RMP.outValue',what.name+'CurveLengthRatio_MD.input1X'],
                        attrA= ['outputMin',m.getAttr(what.name+'Spline_stretchRatio_arc.uParamValue')],
                        connB= [what.name+'Spline_stretchRatio_arc.arcLength', what.name+'_lenRatio_Fader_RMP.outputMax'],
                        attrB= ['inputValue',1]

                        )
        m.rename('Rig_'+what.joints[-1],'Spline_'+what.name+'_End')
        m.rename('IK_'+what.joints[-1],'Rig_'+what.joints[-1])


    


        #parent spaces
        meMakeSpaceSwitch(what)

        #connect controls                
        #m.parentConstraint(what.ctrls[1],'IK_'+what.joints[-1],mo=True)
        m.parentConstraint(what.ctrls[0],'IK_'+what.joints[0],mo=True)                
        m.parentConstraint(what.ctrls[1],'Rig_'+what.joints[-1],mo=True)
        m.parent(what.ctrls[1]+'_Space',what.name+'_FK_'+pos[fkDivisions-1])
        m.parent(what.ctrls[0]+'_Space',what.name+'_FK_'+pos[0]+'_Space',what.ctrls[2])                       
        m.parentConstraint(what.ctrls[0],what.name+'_twistStart',mo=True)
        m.connectAttr(what.ctrls[1]+".squashAmt", '%s_Squash_Envelope_RVL.inputValue' % what.name) 
        #m.connectAttr(what.ctrls[1]+".splineEndTangent",'IK_'+what.joints[-1]+'.sx')

        #m.connectAttr(what.ctrls[1]+".stretchAmt", '%s_lenRatio_Fader_RMP.inputValue' % what.name+what.side) 

        m.rename('Rig_'+what.joints[0],'Spline_'+what.name+'_Start')
        m.rename('IK_'+what.joints[0],'Rig_'+what.joints[0])

        meTools.mePlugTo(what)
        meTools.mePlugRigs(what)
      
def meSpline(what,**kwargs):        
    curve = ''
    if 'sine' in kwargs.keys():
        #create a 3 pt curve        
        start = m.xform('base_'+kwargs['joints'][0],q=True,t=True,ws=True)
        end = m.xform('base_'+kwargs['joints'][-1],q=True,t=True,ws=True)
        mid = []
        for i in range(len(start)):
            mid.append(((end[i]-start[i])*0.5)+start[i])

        curve = m.curve(n=what.name+'splineCrv',d=2,p=[start,mid,end])
        rename(m.listRelatives(curve,s=True)[0],what.name+'splineCrvShape')


    joints = meTools._meGetJointsBetween('base_'+what.joints[0],'base_'+what.joints[-1])               
    meTools.meJoints(what,['base_'+what.joints[0],'base_'+what.joints[-1]],'Rig',what.name+"_UTILS",0)        
    meTools.meStretchySpline(what,what.name,'Rig_'+what.joints[0],'Rig_'+what.joints[-1],curve,'',what.name+"_UTILS",1)
    meTools.meSquash(what.name,'Rig_'+what.joints[0],'Rig_'+what.joints[-1],what.name+'CurveLengthRatio_MD.outputX',0,.3,what.ctrls[1])
    
    #setup twist
    #meTools.meMakeCurves(what.name+'_twistStart','','locator','','base_'+what.joints[0],'',what.name+"_UTILS",'','',0,"")
    meTools.makeCtrl(name=what.name+'_twistStart',shape='locator',tgt='base_'+what.joints[0],parentSpace=what.name+"_UTILS",vis=0)
    #meTools.meMakeCurves(what.name+'_twistEnd','','locator','','base_'+what.joints[-1],'',what.name+"_UTILS",'','',0,"")        
    meTools.makeCtrl(name=what.name+'_twistEnd',shape='locator',tgt='base_'+what.joints[-1],parentSpace=what.name+"_UTILS",vis=0)
    m.connectAttr(what.name+'_twistStart.worldMatrix[0]',what.name+'Spline.dWorldUpMatrix')
    m.connectAttr(what.name+'_twistEnd.worldMatrix[0]',what.name+'Spline.dWorldUpMatrixEnd')
    
    meTools.meMultiAttr(what.name+'Spline',{'dTwistControlEnable':1,
                                    'dWorldUpType':4,
                                    'dWorldUpVectorY':0,
                                    'dWorldUpVectorZ':1,
                                    'dWorldUpVectorEndY':0,
                                    'dWorldUpVectorEndZ':1,
                                    'dWorldUpAxis':3})

    meTools.mePlugTo(what)  

def meMakeSingleFKIK(what):
    print "clav"
    
    #meTools.meMakeCurves(what.name+"_FK"+what.side+"_GRP",'','null','','base_'+what.joints[0]+what.side,'','Clavicle'+what.side+'_UTILS','base_'+what.joints[0]+what.side,'',1,'s%v')
    meTools.makeCtrl(name=what.name+"_FK"+what.side+"_GRP",shape='null',tgt='base_'+what.joints[0]+what.side,parentSpace='Clavicle'+what.side+'_UTILS',orientMatch='base_'+what.joints[0]+what.side,attr="ctrl_body_"+what.side,vis=1,lockType='s%v')
    meTools.meJoints(what,['base_'+what.joints[0]+what.side,'base_'+what.joints[1]+what.side],'Clav_IK',what.name+"_FK"+what.side+"_GRP",1)    
    m.ikHandle(sj='Clav_IK_'+what.joints[0]+what.side,ee='Clav_IK_'+what.joints[1]+what.side,sol="ikSCsolver",n='Clavicle_ikHandle'+what.side)
    #meTools.meMakeCurves(what.name+what.side+"_FK",'x','circle',ids[what.side],what.name+"_FK"+what.side+"_GRP",'cp','%'+what.name+what.side+'_Controls','base_'+what.joints[0]+what.side,"ctrl_body_"+what.side,1,'')
    meTools.makeCtrl(name=what.name+what.side+"_FK",axis='x',shape='circle',color=ids[what.side],tgt=what.name+"_FK"+what.side+"_GRP",connection='cp',parentSpace='%'+what.name+what.side+'_Controls',orientMatch='base_'+what.joints[0]+what.side,attr="ctrl_body_"+what.side,vis=1)
    #meTools.meMakeCurves(what.joints[1].capitalize()+what.side+"_IK",'','box',ids[what.side],'Clavicle_ikHandle'+what.side,'ct','%'+what.name+what.side+"_FK",'base_'+what.joints[1]+what.side,"ctrl_body_"+what.side,1,'')
    meTools.makeCtrl(name=what.joints[1].capitalize()+what.side+"_IK",shape='box',color=ids[what.side],tgt='Clavicle_ikHandle'+what.side,connection='ct',parentSpace='%'+what.name+what.side+"_FK",orientMatch='base_'+what.joints[1]+what.side,attr="ctrl_body_"+what.side,vis=1)
    
    m.rename('Clav_IK_'+what.joints[0]+what.side,'Rig_'+what.joints[0]+what.side)
    m.parent('Clavicle_ikHandle'+what.side,'Clavicle_FK'+what.side+"_GRP")
    m.setAttr('Clavicle'+what.side+'_plug_end_OUT_to_Arm'+what.side+'_plug_start_IN.Spine_plug_end_OUTW0',0);
    m.parentConstraint('Shoulder'+what.side+'_IK','Clavicle'+what.side+'_plug_end_OUT',mo=True)
    m.parentConstraint('Spine_plug_end_OUT','Clavicle'+what.side+'_Controls',mo=True)
    meTools.mePlugTo(what)


def meMakeExtras(what):    
    id = what.side
    incr = ''
    if 'Foot' in what.name:              
      print "parent is..."+what.parent.name
      print "knee shoulde be "+what.parent.joints[-2]
      m.delete(what.parent.name+'_ikHandle'+id+'_parentConstraint1',what.parent.name+id+'_lenRatio_end_parentConstraint1',what.parent.joints[-2]+id+'_bendyTwist_end_parentConstraint1')

      #BUILD JOINTS AND CONNECT VIA PB
      #meTools.meJoints(what,['base_heel'+id,'base_toe'+id],'IK','IK_ankle'+id,1)
      meTools.meJoints(what,['base_'+what.joints[0]+id,'base_'+what.joints[2]+id],'IK','IK_'+what.parent.joints[-1]+id,1)
      meTools.meJoints(what,['base_'+what.joints[0]+id,'base_'+what.joints[2]+id],'FK','FK_'+what.parent.joints[-1]+id,1)
      meTools.meJoints(what,['base_'+what.joints[0]+id,'base_'+what.joints[2]+id],'Rig','Rig_'+what.parent.joints[-1]+id,1)              
      prefix = ''
      for ea in what.joints:
              for ax in axes:
                    meTools.meCreateNodeB('pairBlend', ea+id+"_BLN",
                                  attrA= ['weight',0.5],
                                  attrB= ['rotInterpolation',1],
                                  connA= ['FK_'+ea+id+'.r'+ax,ea+id+'_BLN.inRotate'+axes[ax]+'1'],
                                  connB= [ea+id+'_BLN.outRotate'+axes[ax],'Rig_'+ea+id+'.r'+ax],
                                  connC= ['IK_'+ea+id+'.r'+ax, ea+id+'_BLN.inRotate'+axes[ax]+'2'])   

              connectAttr(what.auxName+id+'_SW.FK_IK', ea+id+'_BLN.weight')

      #BUILD INVERSE DRIVER HEIRARCHY
      previous = what.name+id+"_UTILS"      
      for ea in what.spaces:
            pair = ea.split(':') 
            split = pair[0].split('%')
            if len(split) == 2:
                object = split[0]+id+split[1]
            else:
                object = split[0]+id                       
            m.select(previous)
            m.joint(n='INV_IK_'+object)            
            if ea == what.spaces[-3]:
                m.parent('INV_IK_'+object,'INV_IK_'+what.spaces[-6].split(':')[0]+id)
                m.setAttr('INV_IK_'+object+'.r',0,0,0)
                m.setAttr('INV_IK_'+object+'.jointOrient',0,0,0)
                m.parent('INV_IK_'+object,previous)

            m.delete(m.parentConstraint('base_'+pair[1]+id,'INV_IK_'+object))
            previous = 'INV_IK_'+object
            
      
      m.ikHandle( sj='IK_'+what.parent.joints[-1]+id, ee='IK_'+what.joints[1]+id,n=what.auxName+'_A'+id+'_IK', sol='ikRPsolver')
      m.parent(what.auxName+'_A'+id+'_IK','INV_IK_'+what.joints[1]+id)
      m.ikHandle( sj='IK_'+what.joints[1]+id, ee='IK_'+what.joints[2]+id,n=what.auxName+'_B'+id+'_IK', sol='ikRPsolver')
      m.parent(what.auxName+'_B'+id+'_IK','INV_IK_'+what.joints[2]+id)   
      m.parentConstraint(what.auxName+'_IK'+id,'INV_IK_'+what.parent.joints[-1]+id, mo=True)
      


      #CONNECT TO FOOT ATTRS
      meTools.meCreateNodeB('clamp',what.name+'INV_IK'+id+'_CLMP',attrA=['minR',-180],attrB=['maxG',180],attrC=['minG',0])
      for attr in what.attrs:  
          m.addAttr(what.auxName+'_IK'+id,ln=attr,at='double',min=-180,max=180,dv=0,k=1);
                        
          if what.attrs[attr] != '':
              conn = what.attrs[attr].split('_id_')               
              m.connectAttr(what.auxName+'_IK'+id+'.'+attr,conn[0]+id+conn[1])

      m.setAttr (what.name+'INV_IK'+id+'_CLMP.maxR',0)        
      m.connectAttr (what.auxName+'_IK'+id+'.footRoll' , what.name+'INV_IK'+id+'_CLMP.inputG')
      m.connectAttr (what.name+'INV_IK'+id+'_CLMP.outputR' ,'INV_IK_'+what.joints[0]+id+'.ry'  )
      m.connectAttr (what.name+'INV_IK'+id+'_CLMP.outputG' ,'INV_IK_'+what.joints[1]+id+'.rotateY' )   
      m.select(what.name+id+'_plug_start_IN')
      m.joint(n=what.parent.joints[0]+id+'_reader')

      m.connectAttr('IK_'+what.parent.joints[-1]+id+'.rx',what.parent.joints[-1]+id+'_BLN.inRotateX2',f=True)
      m.connectAttr('IK_'+what.parent.joints[-1]+id+'.ry',what.parent.joints[-1]+id+'_BLN.inRotateY2',f=True)
      m.connectAttr('IK_'+what.parent.joints[-1]+id+'.rz',what.parent.joints[-1]+id+'_BLN.inRotateZ2',f=True)
      
      m.parentConstraint('INV_IK_'+what.joints[1]+id,what.parent.name+id+'_lenRatio_end',mo=True)
      m.parentConstraint('INV_IK_'+what.joints[1]+id,what.parent.name+'_ikHandle%s' % id,mo=True,n=what.parent.name+'_PCON%s' % id)
      m.parentConstraint('INV_IK_'+what.joints[1]+id,what.parent.joints[-2]+id+'_bendyTwist_end',mo=True)
      m.connectAttr(what.parent.name+id+'_lenRatio_MD.outputX','IK_'+what.parent.joints[1]+id+'.scaleX')
      m.connectAttr(what.parent.name+id+'_lenRatio_MD.outputX','IK_'+what.parent.joints[0]+id+'.scaleX')

      #add FK control to ball
      #meTools.meMakeCurves('ball'+id+'_FK','x','circle',ids[id],'FK_ball'+id,'dr','%ankle'+id+'_FK','',"ctrl_body_"+id,1,"t%s%v")
      meTools.makeCtrl(name='ball'+id+'_FK',axis='x',shape='circle',color=ids[id],tgt='FK_ball'+id,connection='dr',parentSpace='%ankle'+id+'_FK',attr="ctrl_body_"+id,vis=1,lockType="t%s%v")

      #extra FKb stuff to me organized later
      m.select('INV_IK_toe'+id)
      m.joint(n='INV_FKb_ball'+id)
      m.delete(m.parentConstraint('INV_IK_ball'+id,'INV_FKb_ball'+id))
      m.parent('foot_B'+id+'_IK','INV_FKb_ball'+id)
      #meTools.meMakeCurves('ball'+id+'_FKb','x','circle',ids[id],'INV_FKb_ball'+id,'dr','%foot'+id+'_SW','',"ctrl_body_"+id,1,"t%s%v")
      meTools.makeCtrl(name='ball'+id+'_FKb',axis='x',shape='circle',color=ids[id],tgt='INV_FKb_ball'+id,connection='dr',parentSpace='%foot'+id+'_SW',attr="ctrl_body_"+id,vis=1,lockType="t%s%v")
      # m.connectAttr('foot'+id+'_SW.FK_IK','ball'+id+'_FKb_Space.v')
      # m.delete(m.pointConstraint('base_heel'+id,'foot_IK'+id+'_Pivot_A' ))
      # m.move(0,'foot_IK'+id+'_Pivot_A',y = True,ws=True)
      # m.delete(m.pointConstraint('base_ball'+id,'foot_IK'+id+'_Pivot_B' ))
      # m.move(0,'foot_IK'+id+'_Pivot_B',y = True,ws=True)
      # m.delete(m.pointConstraint('base_toe'+id,'foot_IK'+id+'_Pivot_C' ))
      # m.move(0,'foot_IK'+id+'_Pivot_C',y = True,ws=True)
      # m.setAttr('foot_IK'+id+'.pivotOffsetVis',1)




      if len(what.parent.joints) == 4:
            m.connectAttr(what.parent.name+id+'_lenRatio_MD.outputX','IK_'+what.parent.joints[2]+id+'.scaleX')

    if what.name == 'Hand':      
         fingers = ['pinky','ring','middle','index','thumb']
         for finger in fingers:
            

            #setup IK
            sJoints = []
            joints = []
            for i in range(4):
                i += 1
                sJoints.append(finger+'_'+str(i)+id)
                joints.append(finger+'_'+str(i))
            what.joints = joints
            m.parentConstraint('Arm'+id+'_plug_end_OUT','Hand'+id+'_Extras')
            subFKIK(    what,
                        name = finger,
                        manualMode=True,
                        sJoints=sJoints,
                        defIkFollow=what.name.lower()+id+'_SW',
                        ik=finger,
                        ikHandleOrienter='base_'+finger+'_4'+id,
                        pvPositionOffset=m.getAttr('base_'+sJoints[1]+".tx"),
                        switchDefault=0,
                        ctrlParent = what.name.lower()+id+'_SW',
                        utils='Hand'+id+'_Extras',
                        pvAngle = (0,1,0),
                        )
            m.connectAttr(finger+id+'_SW.FK_IK',finger+'_PVA'+id+'_Space.v')
            m.delete(finger+id+'_SW_Space_parentConstraint1')
            m.parentConstraint('hand'+id+'_SW', finger+id+'_SW_Space')




    meTools.mePlugTo(what)                              