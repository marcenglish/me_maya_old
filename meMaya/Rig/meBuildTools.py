import maya.cmds as m

from Rig import meTools
reload(meTools)

def MoveablePivot(control,amount):
  alpha = ['A','B','C','D','E','F','G','H']
  parent = m.listRelatives(control,c=False,p=True)[0]
  m.addAttr(control,ln='pivotOffsetVis',at='enum',en='off:on',k=True)

  for i in range(amount):
    
    ctrl = control+'_Pivot_'+alpha[i]
    invCtrl = control+'_PivotInv_'+alpha[i]
    #can't use meMakeCurve b/c this function is ref'd by that script
    m.curve(n=ctrl,d=1, p=[(0,0,1.108194),(0.783612,0,0.783612),(1.108194,0,0),(0.783612,0,-0.783612),(0,0,-1.108194),(-0.783612,0,-0.783612),(-1.108194,0,0),(-0.783612,0,0.783612),(0,0,1.108194),(0,0,1.108194),(0,0.783612,0.783612),(0,1.108194,0),(0,0.783612,-0.783612),(0,0,-1.108194),(0,-0.783612,-0.783612),(0,-1.108194,0),(0,-0.783612,0.783612),(0,0,1.108194),(0,0,1.108194),(-0.783612,0,0.783612),(-1.108194,0,0),(-0.783612,0,-0.783612),(0,0,-1.108194),(0.783612,0,-0.783612),(1.108194,0,0),(0.783612,0,0.783612),(0,0,1.108194)])
    m.rename(m.listRelatives(ctrl,s=True)[0],ctrl+'Shape')
    m.addAttr(ctrl,ln="ctrl",dt="string")
    m.setAttr(ctrl+".ctrl",'pivot',type="string")
    m.setAttr(ctrl+".ctrl",l=1)
    m.group(n=invCtrl,em=True)
    
    meTools.PC(ctrl,control ,0)
    meTools.PC(invCtrl,ctrl,0)
    m.parent(ctrl,parent)
    m.parent(invCtrl,ctrl)
    
    ctrlShape = m.listRelatives(ctrl)[0]

    meTools.Node('multiplyDivide',ctrl+'_MD', attrA= ['input2.input2X',-1], attrB= ['input2.input2Y',-1],attrC= ['input2.input2Z',-1])
    m.connectAttr(ctrl +'.translate',ctrl+'_MD.input1')
    m.connectAttr(ctrl+'_MD.output',invCtrl+'.translate')
    parent = invCtrl

    if i > 0:
      scale = 1-(i*.1)
      m.scale(scale,scale,scale,ctrl+'.cv[0:26]',r=True)

    m.connectAttr(control+'.pivotOffsetVis',ctrlShape+'.v')

  m.parent(control,invCtrl)

def TempLockRig():
  everything = m.ls()
  keywords = ['_Utils','_Space','_PivotInv','_plug','_Controls']
  for obj in everything:
    for key in keywords:
      if key in obj:        
        attrs = m.listAttr(obj,k=True)
        if attrs:
          for attr in attrs:
            try:
              m.setAttr(obj+'.'+attr,l=True)
            except:
              pass



class FKIK():

    @staticmethod
    def Bendy(obj):
        #MAKE BENDYS

        colors = {'__L':'blue','__R':'red'}
        id = obj.sides[obj.s]
        incr = ''   
        radius = m.getAttr(obj.baseJ[0]+'.radius')
        seg = 'start'    
        
        if m.getAttr(obj.baseJ[1]+'.tx') < 0:
            flip = -1
        else:
            flip = 1
        
        CTRL = obj.name+'_'+obj.coreJoints[-1]+id+'_CTRL'
        m.addAttr(CTRL,ln='squashAmt',min=0,max=1,dv=0.5,k=True)

        # Build spline curve and joint set at origin
        for j in range(len(obj.coreJoints)-1):        
            roll = obj.extraInfo['roll']

            length  = abs(m.getAttr(obj.baseJ[j+1]+'.tx')*(roll+1))
           
            curve = obj.name+'_'+obj.coreJoints[j]+id+'_bendy_crv'
            bendy = obj.name+'_Bendy_'+obj.coreJoints[j]+id

            m.curve(p=([0,0,0],[length*0.5,0,0],[length,0,0]),n=curve,d=2)
            
            shape = m.listRelatives(curve,c=True)
            m.rename(shape, curve+'Shape')    
            m.joint(n=bendy+"_start",p=[0,0,0],rad=radius)
            m.joint(n=bendy+"_end",p=[(length/(roll+1)),0,0],rad=radius)
            insertFrom = bendy+"_start"

            
            for i in range(roll):
                m.insertJoint(insertFrom)            
                jointName = obj.name+'_'+'Rig_'+obj.coreJoints[j]+'_Roll_'+str(i)+id#.replace('_L',"_Roll_"+str(i)+id)
                m.rename(jointName)
                m.setAttr(jointName+'.tx',length/(roll+1))
                m.setAttr(jointName+'.radius',radius)
                insertFrom = jointName
            m.parent(bendy+"_start",w=True)
                   
            StretchySpline(obj,curve.replace('_crv',''),bendy+"_start",bendy+"_end",curve+'',1,obj.utilsTop,1)
            


            # Position spline           
            currentJnt =  obj.name+'_'+obj.coreJoints[j]+id
            meTools.PC(obj=bendy+"_start",snapTo='base_'+currentJnt,keep=0)
            meTools.PC(obj=curve+'',snapTo='base_'+currentJnt,keep=0)



            if flip == -1:
                m.setAttr(curve+'.rx',l=False)
                m.setAttr(curve+'.ry',l=False)
                m.setAttr(curve+'.rz',l=False)
                m.rotate(180,curve,z=True,r=True,os=True)

            # Setup bend joint
            m.select(obj.RigJ[j])
            m.joint(n=obj.name+'_Bend_'+obj.coreJoints[j]+id+'_Space',rad=radius)
            bendJnt = m.joint(n=obj.name+'_Bend_'+obj.coreJoints[j]+id,rad=radius)
            
            m.pointConstraint(obj.RigJ[j],bendJnt+'_Space') 
            m.pointConstraint(obj.RigJ[j+1],bendJnt+'_Space')
            m.orientConstraint(obj.RigJ[j],bendJnt+'_Space')        
            m.parent(curve+'',obj.utilsTop)
            
            m.parent(bendy+"_start",obj.utilsTop)            
            
            m.skinCluster(obj.RigJ[j],obj.RigJ[j+1],bendJnt,curve+'',tsb=True,n=currentJnt+'_bendy_skinCluster')                
            
            m.skinPercent(currentJnt+'_bendy_skinCluster',curve+'.cv[0]',tv=(obj.RigJ[j],1))  
            m.skinPercent(currentJnt+'_bendy_skinCluster',curve+'.cv[1]',tv=(bendJnt,1))    
            m.skinPercent(currentJnt+'_bendy_skinCluster',curve+'.cv[2]',tv=(obj.RigJ[j+1],1))
       
            #Squash
            length = m.getAttr(currentJnt+'_bendySpline_stretchRatio_arc.arcLength')
            

            meTools.Node('multiplyDivide',currentJnt+'_Length_MD',connA=[currentJnt+'_bendySpline_stretchRatio_arc.arcLength',currentJnt+'_Length_MD.input1X'],
                                                                        attrA=['input2X',length],
                                                                        attrB=['operation',2])


            firstRoll = obj.baseJ[j].replace(id,'_Roll_0'+id)
            lastRoll = obj.baseJ[j].replace(id,'_Roll_'+str(roll-1)+id)
            #non-DAG node prefix.
            ndnPrefix = obj.name+'_'+obj.coreJoints[j]+id

            Squash(obj,ndnPrefix,firstRoll,lastRoll,currentJnt+'_Length_MD.outputX',1,.3)

        
            m.parentConstraint(obj.RigJ[j],ndnPrefix+'_bendyTwist_start')    
            m.delete(m.parentConstraint(obj.RigJ[j+1],ndnPrefix+'_bendyTwist_end'))
            m.delete(m.orientConstraint(ndnPrefix+'_bendyTwist_start',ndnPrefix+'_bendyTwist_end'))        
            #m.pointConstraint(obj.RigJ[j+1],ndnPrefix+'_bendyTwist_end')
            m.connectAttr(CTRL+".squashAmt", ndnPrefix+'_Squash_Envelope_RVL.inputValue') 

        m.addAttr(CTRL+'_SW',ln="bendCtrlVisibility",at='enum',en='off:on:',k=0)
        m.setAttr(CTRL+'_SW.bendCtrlVisibility',cb=True)    
        

        #BENDY CONTROLS
        for j in range(2):
            ndnPrefix = obj.name+'_'+obj.coreJoints[j]+id
            bendJnt = obj.name+'_Bend_'+obj.coreJoints[j]+id
            meTools.Ctrl(name=ndnPrefix+"_Bend",axis='x',shape='circle',color=colors[id],tgt=bendJnt,connection='dt',parentSpace='%'+obj.controlsTop,attr="ctrl_body_"+id,vis=1,lockType="r%s%v")
            m.parentConstraint(bendJnt+'_Space',ndnPrefix+"_Bend_Space")
            m.connectAttr(CTRL+'_SW.bendCtrlVisibility',ndnPrefix+'_Bend_Space.v')
            
        #ik twist follow
        m.aimConstraint(obj.RigJ[1],obj.name+'_'+obj.coreJoints[0]+id+'_bendyTwist_aim_Space',aimVector=(1*flip,0,0), upVector = (0,1,0),wut='objectrotation',wuo=obj.name+id+'_plug_start_IN')
        m.setAttr(obj.name+'_'+obj.coreJoints[0]+id+'_bendyTwist_aim.ry',l=True,k=False)
        m.setAttr(obj.name+'_'+obj.coreJoints[0]+id+'_bendyTwist_aim.rz',l=True,k=False)


        #limb twist upVectors    
        
        #joint[0] twist end was previously orient constrained to next joint start.  Twist deformations were nicer but
        #joint values would flip when >90.  Would be nice to figure out how to get it working right, in the meantime,
        #end joint follows segment root

        #m.parentConstraint(obj.RigJ[1],obj.name+'_'+obj.coreJoints[0]+id+'_bendyTwist_end',mo=True)

        m.parentConstraint(obj.RigJ[0],obj.name+'_'+obj.coreJoints[0]+id+'_bendyTwist_end',mo=True)
        m.parentConstraint(obj.RigJ[2],obj.name+'_'+obj.coreJoints[1]+id+'_bendyTwist_end')  
        m.rename(obj.RigJ[0],obj.name+'_Driver_'+obj.coreJoints[0]+id)
        m.rename(obj.name+'_Bendy_'+obj.coreJoints[0]+id+"_start",obj.RigJ[0])  


        #add bonelessArm functionality        
        #temporary setup for ninjago
        
        dist = 0
        for ea in obj.baseJ:
            
            if ea != obj.baseJ[0]:
                print 'test ',ea
                print m.getAttr(ea+'.tx')
                print roll
                print abs(m.getAttr(ea+'.tx'))*(roll+1)
                dist = dist + (abs(m.getAttr(ea+'.tx'))*(roll+1))

        m.addAttr(CTRL+'_SW',ln="bonelessArms",min=0,max=1,dv=0,k=True)
        m.setAttr(CTRL+'_SW.bonelessArms',cb=True)
        
        meTools.Node('multiplyDivide',obj.name+id+'+bonelessArms_MD',
                        connA=[CTRL+'_SW.bonelessArms',obj.name+id+'_bonelessArms_MD.input1X'],
                        connB=[CTRL+'_SW.bonelessArms',obj.name+id+'_bonelessArms_MD.input1Y'],
                        # connC=[obj.name+id+'_bonelessArms_MD.outputX',obj.name+'_'+obj.coreJoints[0]+id+'_Bend.tz'],
                        # connD=[obj.name+id+'_bonelessArms_MD.outputY',obj.name+'_'+obj.coreJoints[1]+id+'_Bend.tz'],
                        connC=[obj.name+id+'_bonelessArms_MD.outputX',obj.name+'_'+obj.coreJoints[0]+id+'_Bend_Space_parentConstraint1.target[0].targetOffsetTranslateZ'],
                        connD=[obj.name+id+'_bonelessArms_MD.outputY',obj.name+'_'+obj.coreJoints[1]+id+'_Bend_Space_parentConstraint1.target[0].targetOffsetTranslateZ'],                    )

        m.connectAttr(obj.name+id+'_bonelessArms_MD.outputX',obj.name+'_Bend_'+obj.coreJoints[0]+id+'_Space_pointConstraint1.offsetZ')
        m.connectAttr(obj.name+id+'_bonelessArms_MD.outputY',obj.name+'_Bend_'+obj.coreJoints[1]+id+'_Space_pointConstraint1.offsetZ')

        sdkValues = {}
        sdkValues['Arm'] = [[0,dist],[-3*flip,dist*0.5],[-4*flip,dist*.2]]
        sdkValues['Leg'] = [[0,dist],[2.5*flip,dist*0.5],[4*flip,dist*.2]]

        if obj.name in ['Arm','Leg']:
            for j, alpha in enumerate(['X','Y']):        
                print 'dist is '+str(dist)
                m.setDrivenKeyframe( obj.name+id+'_bonelessArms_MD.input2'+alpha, cd=obj.name+id+'_lenRatio_DB.distance',v=sdkValues[obj.name][0][0],dv=sdkValues[obj.name][0][1])
                m.setDrivenKeyframe( obj.name+id+'_bonelessArms_MD.input2'+alpha, cd=obj.name+id+'_lenRatio_DB.distance',v=sdkValues[obj.name][1][0],dv=sdkValues[obj.name][1][1])
                m.setDrivenKeyframe( obj.name+id+'_bonelessArms_MD.input2'+alpha, cd=obj.name+id+'_lenRatio_DB.distance',v=sdkValues[obj.name][2][0],dv=sdkValues[obj.name][2][1])

        m.rename(obj.RigJ[1],obj.RigJ[1].replace('Rig','Driver'))
        m.rename(obj.name+'_Bendy_'+obj.coreJoints[j]+id+'_start',obj.RigJ[1])




        




    @staticmethod
    def Stretch(obj,id):

        base = obj.baseJ
        IK = obj.IKJ
        Rig= obj.RigJ
        inv = 1
        if id == '_R': inv = -1    
        LengthRatio(IK[0],IK[-1],obj,inv)
        seg = ['mid','end']
        objLen = []
        lastJnt = obj.coreJoints[-1]+id

        for i in range(len(base)-1):
            if 'Roll' not in IK[i]:
                currentJnt = obj.coreJoints[i+1]+id

                objLen.append(m.getAttr(IK[i+1]+'.tx'))

                meTools.Node('multiplyDivide',currentJnt+'_len_MD',
                              attrA= ['input1X',objLen[i]],
                              connA= [obj.name+id+'_lenRatio_MD.outputX',currentJnt+'_len_MD.input2X'],
                              connB= [currentJnt+'_len_MD.outputX',Rig[i+1]+'.tx'] )

                meTools.Node('multiplyDivide',currentJnt+'_FKIK_MD',
                              attrA= ['operation',3],
                              connA= [obj.name+id+'_lenRatio_MD.outputX',currentJnt+'_FKIK_MD.input1X'],
                              connB= [currentJnt+'_FKIK_MD.outputX',currentJnt+'_len_MD.input2X'],
                              connC= [obj.name+'_'+lastJnt+'_CTRL_SW.FK_IK',currentJnt+'_FKIK_MD.input2X'] )

        m.connectAttr(obj.name+'_'+lastJnt+'_CTRL_SW.FK_IK',obj.name+'_'+lastJnt+'_PV_CTRL_Space.v')

        m.addAttr(obj.name+'_'+lastJnt+'_CTRL',ln='stretchAmt',min=0,max=1,dv=1,k=True)
        m.connectAttr(obj.name+'_'+lastJnt+"_CTRL.stretchAmt", '%s%s_lenRatio_Fader_RMP.inputValue' % (obj.name,id)) 

        m.parentConstraint(obj.name+id+'_plug_start_IN',obj.name+id+'_lenRatio_start')
        m.parentConstraint(obj.name+'_'+lastJnt+'_CTRL',obj.name+id+'_lenRatio_end')

    @staticmethod
    def Scale(obj,id):
        m.addAttr(obj.switchHandle,ln='allScale',min=0.01,max=10,dv=1,k=True)
        
        for axis in ['x','y','z']:
            m.connectAttr(obj.switchHandle+'.allScale',obj.name+"_IK"+id+"_GRP.s"+axis)
            m.connectAttr(obj.switchHandle+'.allScale',obj.name+"_Rig"+id+"_GRP.s"+axis)
        
        origLength = m.getAttr(obj.name+id+'_lenRatio_Switch_MD.input2X')
        m.createNode("multiplyDivide",n=obj.name+'_ikOverallScale'+id+'_MD')
        m.connectAttr(obj.switchHandle+'.allScale',obj.name+'_ikOverallScale'+id+'_MD.input1X')
        m.setAttr(obj.name+'_ikOverallScale'+id+'_MD.input2X',origLength)
        m.connectAttr(obj.name+'_ikOverallScale'+id+'_MD.outputX',obj.name+id+'_lenRatio_Switch_MD.input2X')
        m.connectAttr(obj.name+'_ikOverallScale'+id+'_MD.outputX',obj.name+id+'_lenRatio_CON.colorIfFalseR')
        m.connectAttr(obj.name+'_ikOverallScale'+id+'_MD.outputX',obj.name+id+'_lenRatio_Fader_RMP.outputMin')
        m.connectAttr(obj.name+'_ikOverallScale'+id+'_MD.outputX',obj.name+id+"_lenRatio_MD.input2X")


def Spline(obj,**kwargs):        
    curve = ''
    if 'sine' in kwargs.keys():
        #create a 3 pt curve        
        start = m.xform(kwargs['joints'][0],q=True,t=True,ws=True)
        end = m.xform(kwargs['joints'][-1],q=True,t=True,ws=True)
        mid = []
        for i in range(len(start)):
            mid.append(((end[i]-start[i])*0.5)+start[i])

        curve = m.curve(n=obj.name+'Spline_crv',d=2,p=[start,mid,end])
        #m.move(0,0,0.571322,obj.name+'Spline_crv.cv[1]',r=True,os=True,wd=True)
        m.rename(m.listRelatives(curve,s=True)[0],obj.name+'Spline_crvShape')


    joints = GetJointsBetween(obj,obj.joints[0],obj.joints[-1])               
    
    StretchySpline(obj,obj.name,obj.RigJ[0],obj.RigJ[-1],curve,'',obj.name+"_Utils",1)       

     
    Squash(obj.name,obj.name,obj.RigJ[0],obj.RigJ[-1],obj.name+'CurveLengthRatio_MD.outputX',0,.3)

    
    #setup twist
    meTools.Ctrl(name=obj.name+'_twistStart',shape='locator',tgt=obj.joints[0],parentSpace=obj.name+"_Utils",vis=0)
    meTools.Ctrl(name=obj.name+'_twistEnd',shape='locator',tgt=obj.joints[-1],parentSpace=obj.name+"_Utils",vis=0)
    m.connectAttr(obj.name+'_twistStart.worldMatrix[0]',obj.name+'Spline.dWorldUpMatrix')
    m.connectAttr(obj.name+'_twistEnd.worldMatrix[0]',obj.name+'Spline.dWorldUpMatrixEnd')
    
    meTools.meMultiAttr(obj.name+'Spline',{'dTwistControlEnable':1,
                                            'dWorldUpType':4,
                                            'dWorldUpVectorY':0,
                                            'dWorldUpVectorZ':1,
                                            'dWorldUpVectorEndY':0,
                                            'dWorldUpVectorEndZ':1,
                                            'dWorldUpAxis':3})





    
def LengthRatio(start,end,obj,inv):
    id = obj.sides[obj.s]
    dist = 0.00000 

    joints = GetJointsBetween(obj,start,end)
    meTools.Ctrl(name = obj.name+id+'_lenRatio_start',shape='locator',color='white',tgt=start,parentSpace=obj.utilsTop,vis=0)
    meTools.Ctrl(name=obj.name+id+'_lenRatio_end',shape='locator',color='white',tgt=end,parentSpace=obj.utilsTop,vis=0)

    meTools.Node('distanceBetween',obj.name+id+'_lenRatio_DB',
                  connA= [obj.name+id+'_lenRatio_startShape.worldPosition',obj.name+id+'_lenRatio_DB.point2'],
                  connB= [obj.name+id+'_lenRatio_endShape.worldPosition',obj.name+id+'_lenRatio_DB.point1'] )    
  
    for ea in joints:
        if ea != joints[0]:
            dist = dist + abs(m.getAttr(ea+'.tx'))            


    meTools.Node('multiplyDivide',obj.name+id+'_lenRatio_MD',
                attrA= ['operation',2],
                attrB= ['input2X',dist],
                connA= [obj.name+id+'_lenRatio_DB.distance',obj.name+id+'_lenRatio_MD.input1X'] )   

    meTools.Node('multiplyDivide',obj.name+id+'_lenRatio_Switch_MD',
                attrA= ['input2X',dist],
                attrB= ['operation',2],
                connA= [obj.name+id+'_lenRatio_DB.distance',obj.name+id+'_lenRatio_Switch_MD.input1X'])

    meTools.Node('condition',obj.name+id+'_lenRatio_CON',
                attrA= ['secondTerm',1],
                attrB= ['operation',2],
                attrC= ['colorIfFalseR',dist],
                connA= [obj.name+id+'_lenRatio_DB.distance',obj.name+id+'_lenRatio_CON.colorIfTrueR'],
                connB= [obj.name+id+'_lenRatio_Switch_MD.outputX',obj.name+id+'_lenRatio_CON.firstTerm'])      

    meTools.Node('remapValue',obj.name+id+'_lenRatio_Fader_RMP',connA= [obj.name+id+'_lenRatio_CON.outColorR',obj.name+id+'_lenRatio_Fader_RMP.outputMax'],
                                                                         connB= [obj.name+id+'_lenRatio_Fader_RMP.outValue',obj.name+id+'_lenRatio_MD.input1X'],
                                                                         attrA=['outputMin',dist])


def GetJointsBetween(obj,start,end):
    #start = start.replace('base_','base_'+obj.name+'_')
    #end = end.replace('base_','base_'+obj.name+'_')
    m.select(end)   
    kid = m.ls(sl=True,l=True)[0]
    joints = kid.split('|')
    startJnt = joints.index(start)
    endJnt = joints.index(end)
    del joints[0:(startJnt)]
    return joints
    
def StretchySpline(obj,section,start,end,curve,twistSetup,parentUnder,flip):
  id = obj.sides[obj.s]
  joints = GetJointsBetween(obj,start,end)
  m.scriptEditorInfo(sw=True)
  twistStart = section+'Twist_start'
  
  if curve != '':    
    splineStuff = m.ikHandle(sj=start, ee=end, sol='ikSplineSolver', n='%sSpline' % section, p=2, w=.5,scv=False,ccv=False,c=curve)    
    
  else:
    splineStuff = m.ikHandle(sj=start, ee=end, sol='ikSplineSolver', n='%sSpline' % section, p=2, w=.5,scv=False)
    curve = '%s_crv' % splineStuff[0]
    m.rename('curve1',curve)
  
  m.scriptEditorInfo(sw=False)  
  upAxis = 3  

  if flip == -1: upAxis = 4    
  if twistSetup == 1:
    
    #setup Twist
    m.spaceLocator (n='%sTwist_start'% section)    

    if obj.coreJoints[0] in section:
      meTools.Ctrl(name=section+'Twist_aim',shape='pinB',color='white',tgt=section+'Twist_start',parentSpace='%'+obj.controlsTop,vis=1,attr="ctrl_body_"+id,lockType='s%t%v')
      m.delete(m.parentConstraint(obj.name+id+'_plug_start_IN',section+'Twist_aim_Space'))
      m.pointConstraint(obj.name+id+'_plug_start_IN',section+'Twist_aim_Space')

      twistStart = section+'Twist_aim'

    m.parent ('%sTwist_start'% section,parentUnder,r=True)
    m.setAttr ('%sTwist_start.v' % section, 0)
    m.spaceLocator (n='%sTwist_end' % section)
    m.parent ('%sTwist_end' % section,parentUnder,r=True)    
    m.setAttr ('%sTwist_end.v' % section, 0)
    m.setAttr('%sSpline.dTwistControlEnable' % section,1)
    m.setAttr ('%sSpline.dWorldUpType' % section, 4)
    m.setAttr ('%sSpline.dTwistValueType' % section, 1)
    m.setAttr ('%sSpline.dWorldUpAxis' % section, upAxis)
    m.setAttr ('%sSpline.dWorldUpVectorY' % section, 0)
    m.setAttr ('%sSpline.dWorldUpVectorEndY' % section, 0)
    m.setAttr ('%sSpline.dWorldUpVectorZ' % section, flip)
    m.setAttr ('%sSpline.dWorldUpVectorEndZ' % section, 1)
    
    m.connectAttr(twistStart+'.worldMatrix[0]','%sSpline.dWorldUpMatrix' % section)
    
    m.connectAttr('%sTwist_end.worldMatrix[0]' % section,'%sSpline.dWorldUpMatrixEnd' % section)

  curve = str(curve)
  # if obj.id == obj.sides[1]:
  #   m.error(section)
  if curve != '':
      meTools.Node('arcLengthDimension',section+'Spline_stretchRatio_arc',
                    attrA=['uParamValue',(m.getAttr(curve+'.maxValue'))],
                    connA=['%sShape.worldSpace[0]'% curve, '%sSpline_stretchRatio_arc.nurbsGeometry' % section])

  else:
      meTools.Node('arcLengthDimension',section+'Spline_stretchRatio_arc',
                    attrA=['uParamValue',(m.getAttr(section+'Spline_crv.maxValue'))],
                    connA=['%sSpline_crvShape.worldSpace[0]' % section, '%sSpline_stretchRatio_arc.nurbsGeometry' % section] )

  
  meTools.Node('multiplyDivide','%sCurveLengthRatio_MD' % section,
              attrA= ['operation',2],
              attrB= ['input2X',(m.getAttr('%sSpline_stretchRatio_arc.arcLength' % section))],
              connA= ['%sSpline_stretchRatio_arc.arcLength' % section,'%sCurveLengthRatio_MD.input1X' % section])  
  
  m.rename (m.listRelatives('%sSpline_stretchRatio_arc' % section,p=True),'%sSpline_ALR' % section)

  #stretchy follow (x axis)
  for ea in joints:
    #if ea != joints[-1]:
      m.createNode('multiplyDivide', n='%sMultFactor_MD' % ea)
      m.connectAttr ('%sCurveLengthRatio_MD.outputX' % section,'%sMultFactor_MD.input1X' % ea)
      m.setAttr ('%sMultFactor_MD.input2X' % ea,(m.getAttr('%s.translateX' % ea)))
      m.connectAttr ('%sMultFactor_MD.outputX' % ea,'%s.translateX' % ea)
  
  m.parent (splineStuff[0],parentUnder)
  m.parent (splineStuff[0]+"_ALR",parentUnder)    
  return joints

##spineCurveLengthRatio_MD.outputX
def Squash(obj,element,start,end,ratioConn,hinge,factor):

  joints = GetJointsBetween(obj,start,end)

  i = 0
  if hinge == 1:
    for ea in joints:      
      if 'Roll' in ea:
        joints[i] = ea.replace('base_'+obj.name,obj.name+'_Rig')
      i+=1


  ##get incremental power values (.2 div by # of joints)
  incr = (factor / len(joints))
  margin = incr
  i = 0
  meTools.Node('multiplyDivide','%s_Squash_MD' % element,attrA=['operation',2],attrB=['input1X',1])
  meTools.Node('remapValue','%s_Squash_Envelope_RVL' % element,attrA=['outputMin',1],
                                                            connA=[ratioConn,'%s_Squash_Envelope_RVL.outputMax' % element],                                                            
                                                            connB=['%s_Squash_Envelope_RVL.outValue' % element, '%s_Squash_MD.input2X' % element])
  

  
  for ea in joints:
      if ea != joints[0] and ea != joints[-2]:

        meTools.Node('multiplyDivide','%s_%sPOW_MD' % (element,ea),attrA=['input2X',(1 - margin)],attrB=['operation',3])        

        m.connectAttr ('%s_Squash_MD.outputX' % element,'%s_%sPOW_MD.input1X' % (element,ea))
        #if ea != joints[-2]:
        m.connectAttr('%s_%sPOW_MD.outputX' % (element,ea), '%s.scaleY' % ea)
        m.connectAttr('%s_%sPOW_MD.outputX' % (element,ea), '%s.scaleZ' % ea)
        
        i = i + 1
        if i < (len(joints)/2):
                margin = margin  - (incr *6)
        else:
                margin = margin  + (incr *6)
      # else:
      #   print 'skipping '
      #   print ea

  

## (object,array of attrs, 1 for lock, 1 for make non keyable,0 for hide)
def Lock(obj,attrs,lock,hide,makeNonKey):    
    for ob in obj:        
        for ea in attrs:            
            m.setAttr (ob+"."+ea,l=lock,cb=hide,k=makeNonKey)

       
            


def Joints(obj,skelType,**kwargs):    
    id = obj.id
    new = ''
    jointSet = {'FK':obj.FKJ,'IK':obj.IKJ,'Rig':obj.RigJ,'Post_IK':obj.PIKJ,'PreIK':obj.PreIKJ}
    parent = obj.name+'_Utils'+id

    for i in range(len(obj.baseJ)):
        
        new = jointSet[skelType][i]
        m.duplicate(obj.baseJ[i],n=new,po=True)

        m.parent(new,parent)           

        if  i != 0:
            if not m.isConnected(parent+".scale",new+".inverseScale"):
                m.connectAttr(parent+".scale",new+".inverseScale")
        parent = new

    if skelType =='IK':
        m.select(new)
        m.joint(n=new.replace(id,'_Spacer'+id))

    if kwargs:
        if kwargs['ps']:
            topGrp = m.group(em=True,n=obj.name+'_'+skelType+id+'_GRP')
            meTools.PC(obj=topGrp,snapTo=obj.baseJ[0],keep=0)
           
            m.parent(topGrp,obj.name+'_Utils'+id)
            m.parent(jointSet[skelType][0],topGrp)
        
        if kwargs['plug']:
            meTools.PC(obj=obj.name+'_'+skelType+id+'_GRP',snapTo=obj.name+obj.id+'_plug_start_IN',keep=1)



def RenameEndJoint(obj):
    connected = m.listRelatives(obj.baseJ[-1],p=False,c=True)

    runOriginal =False

    if runOriginal:
        if connected:
            elements = connected[0].split('_')
            newJointName = obj.baseJ[-1].replace(obj.name,elements[1])

            if not m.objExists(newJointName):
                m.rename(obj.baseJ[-1],newJointName)
    else:
        #TESTING ALT VERION THAT RENAMES PROCEDURALLY
        if connected:
            parentElements = obj.baseJ[-1].split('_')
            childElements = connected[0].split('_')
            newJointName = obj.baseJ[-1].replace(parentElements[1],childElements[1])

            if not m.objExists(newJointName):
                m.rename(obj.baseJ[-1],newJointName)
        


def ConnectToDriver(obj):
    if obj.verbose:
        print 'connecting ',obj.name,' to ',obj.connectedTo    
    for id in obj.sides:
        if not m.objExists(obj.name+id+'_plug_start_IN_parentConstraint1'):
            srcId = id
            if obj.connectedToObj:
                if not m.objExists(obj.connectedToObj.name+id+'_plug_end_OUT'):
                    srcId = ''

                if 'End' in obj.connectedTo:
                    #get the object's outPlug 
                    m.parentConstraint(obj.connectedToObj.name+srcId+'_plug_end_OUT',obj.name+id+'_plug_start_IN',mo=True)
                else:
                    #create a driver locator for the given joint and connect to taht
                    if 'Start' in obj.connectedTo:
                        m.parentConstraint(obj.connectedToObj.name+srcId+'_plug_start_OUT',obj.name+id+'_plug_start_IN',mo=True)
      
def Framework(obj):        
    id = obj.sides[obj.s]
  
    #build character framework
    if m.objExists('WorldOffset') is False:       
        meTools.Ctrl(name='WorldOffset',axis='y',shape='circle',color='green',parentSpace='space',attr="world_ctrl",vis=1,lockType="v")
        m.scale(12,12,12,'WorldOffset.cv[0:7]')
        m.group(em=True,n='Rig_Controls')
        m.group(em=True,n='Rig_Utilities')
        m.group(em=True,n=obj.charName+"_Rig")
        m.parent('WorldOffset_Space','Rig_Controls')
        m.parent('Rig_Controls','Rig_Utilities',obj.charName+"_Rig")

        #setup character name label
        m.addAttr(obj.charName+"_Rig",ln="rootType",dt="string")
        m.setAttr(obj.charName+'_Rig.rootType','Rig',type='string')
        text = m.textCurves( f='Times-Roman', t=obj.charName)
        m.rotate(-90,0,0,text[0])
        ctr = m.objectCenter(text[0])
        m.move(ctr[0]*-1,ctr[1]*-1,ctr[2]*-1,text[0])
        m.move(0,0,0,text[0]+".scalePivot",a=True)
        m.move(0,0,0,text[0]+".rotatePivot",a=True)
        m.move(0,0,9,text[0],r=True)
        for ea in m.listRelatives(text[0],c=True,ad=True,type='transform'):
            if 'curve' in ea:
                m.parent (ea,'WorldOffset')
                for attr in ['.t','.r','.s','.v']:
                    m.setAttr(ea+attr,l=True)
                    m.setAttr(ea+'.overrideEnabled',True)
                    m.setAttr(ea+'.overrideColor',14)
        m.delete(text[0],'makeTextCurves1')

        #build proxy geo switch
        m.addAttr('WorldOffset',ln="geoType",at="enum",en="Hi:Lo:")
        m.setAttr('WorldOffset.geoType',e=True,k=True)
        m.createNode('reverse',n='geoType_REV')
        m.connectAttr('WorldOffset.geoType','geoType_REV.inputX')
        m.addAttr('WorldOffset',ln="geoMode",at="enum",en="Normal:Template:Reference:")
        m.setAttr('WorldOffset.geoMode',e=True,k=True)
        m.setAttr('WorldOffset.geoMode',2)
        m.addAttr('WorldOffset',ln="ctrlVisibility",at='float',dv=1,min=0,max=1)
        m.setAttr('WorldOffset.ctrlVisibility',e=True,k=True)


        
    #build component framework        
    if m.objExists(obj.name+id+"_Utils") is True:
        pass            
    else:    
        obj.utilsTop = m.group(em=True,n=obj.name+"_Utils"+id)
        m.parent(obj.utilsTop,'Rig_Utilities')
        meTools.Ctrl(name=obj.name+id+'_plug_start_IN',color='white',shape='locator',tgt=obj.baseJ[0],parentSpace=obj.utilsTop,vis=1,lockType='')
        obj.inPlug = obj.name+id+'_plug_start_IN'       

        meTools.Ctrl(name=obj.name+id+'_plug_end_OUT',color='white',shape='locator',tgt=obj.baseJ[-1],parentSpace=obj.utilsTop,vis=1,lockType='')
        obj.outPlug = obj.name+id+'_plug_end_OUT'

        for extraOut in obj.extraOuts:
            if 'Start' in extraOut:
                if not m.objExists(obj.name+id+'_plug_start_OUT'):
                    meTools.Ctrl(name=obj.name+id+'_plug_start_OUT',color='white',shape='locator',tgt=obj.baseJ[0],parentSpace=obj.utilsTop,vis=1,lockType='')
                


        obj.controlsTop = m.group(em=True,n=obj.name+"_Controls"+id)
        m.parentConstraint(obj.name+id+'_plug_start_IN',obj.controlsTop,mo=False)
        m.parent(obj.controlsTop,'WorldOffset_Space')


    if 'Foot' in obj.name:
        meTools.Ctrl(name=obj.name+id+'_plug_start_OUT',color='white',shape='locator',tgt=obj.baseJ[0],parentSpace=obj.utilsTop,vis=1,lockType='')
        
def postFramework(obj):
    id = obj.sides[obj.s]
    for extraOut in obj.extraOuts:
        if 'Start' in extraOut:
            m.parentConstraint(obj.RigJ[0],obj.name+id+'_plug_start_OUT')

def FKChain(obj):
    id = obj.sides[obj.s]
    parent = obj.controlsTop
    for ea in obj.FKJ:      
        meTools.Ctrl(name=ea+"_CTRL",axis='x',shape='circle',color=obj.colors['PrimaryLR'][id],tgt=ea,parentSpace='%'+parent,attr='ctrl_body_'+id,vis=1,lockType='t%s%v')
        for a in ['x','y','z']:
            m.connectAttr(ea+"_CTRL.r"+a,ea+'.r'+a)

        parent = ea+"_CTRL"
        m.addAttr(ea+"_CTRL",ln="fkRotateOrder",at="enum",en="xyz=0:yzx=1:zxy=2:xzy=3:yxz=4:zyx=5:",k=False)
        m.setAttr(ea+"_CTRL"+".fkRotateOrder",channelBox=True)
        m.connectAttr(ea+"_CTRL"+".fkRotateOrder",ea+'.rotateOrder')
        m.connectAttr(ea+"_CTRL"+".fkRotateOrder",ea+'_CTRL.rotateOrder')
    
      
                        
def PlugRigs(obj):
    for ea in obj.branchConnections:
        tokens = ea.split('_->_')
        src = tokens[0]
        tgt = tokens[1]
        if '_id' in tgt:
            tgt = tgt.replace('_id',obj.side)
        if '_id' in src:
            src = src.replace('_id',obj.side)
        constraintName = src+'_to_'+tgt
        command = 'm.parentConstraint("'+src+'","'+tgt+'",mo=True,n="'+constraintName+'")'        
        if m.objExists(src) is True:
            if m.objExists(tgt) is True:
                if m.objExists(constraintName) is False: 
                    m.setAttr(tgt+'.plugInput',constraintName,type="string")
                    #print command
                    exec(command)

def ConnectRig():
    broken = []
    for ea in m.ls("base_*"):
        element = ea.split('_')        
        try :
            m.parentConstraint(ea.replace(element[0]+'_','').replace(element[1],element[1]+'_Rig'),ea,mo=True)            
        except:
            broken.append(ea.replace(element[0]+'_','').replace(element[1],element[1]+'_Rig')+"--->"+ea)

        try:
            

            #m.connectAttr(ea.replace(element[0]+'_','').replace(element[1],element[1]+'_Rig')+'.sx',ea+'.sx')
            m.connectAttr(ea.replace(element[0]+'_','').replace(element[1],element[1]+'_Rig')+'.sy',ea+'.sy')
            m.connectAttr(ea.replace(element[0]+'_','').replace(element[1],element[1]+'_Rig')+'.sz',ea+'.sz')
        except:
            pass

    for ea in broken:
        print 'could not connect ',ea
        


