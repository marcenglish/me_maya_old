import maya.cmds as m

def meBuildMoveablePivot(control,amount):
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
    
    mePC(ctrl,control ,0)
    mePC(invCtrl,ctrl,0)
    m.parent(ctrl,parent)
    m.parent(invCtrl,ctrl)
    #meMakeCurves(ctrl,'','sphere','darkBlue',control,'',parent,'','',True,'')
    #meMakeCurves(control+'_PivotInv_'+alpha[i],'','sphere','blue',control,'',ctrl,'','',True,'')
    
    ctrlShape = m.listRelatives(ctrl)[0]

    meCreateNodeB('multiplyDivide',ctrl+'_MD', attrA= ['input2.input2X',-1], attrB= ['input2.input2Y',-1],attrC= ['input2.input2Z',-1])
    m.connectAttr(ctrl +'.translate',ctrl+'_MD.input1')
    m.connectAttr(ctrl+'_MD.output',invCtrl+'.translate')
    parent = invCtrl

    if i > 0:
      scale = 1-(i*.1)
      m.scale(scale,scale,scale,ctrl+'.cv[0:26]',r=True)

    m.connectAttr(control+'.pivotOffsetVis',ctrlShape+'.v')

  m.parent(control,invCtrl)

def meTempLockRig():
  everything = m.ls()
  keywords = ['_UTILS','_Space','_PivotInv','_plug','_Controls']
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



def meCreateNodeB(nodeType,name,**kwargs):
    flags = ['attr','conn']
    alpha = ['A','B','C','D','E','F','G','H']        
    errorMessage = ['[attr,value]','[connectionStart,connectionEnd]']
    command = ['setAttr','connectAttr']
    keywords = {}
    i = 0
    #Create the node
    if m.objExists(name):
        pass
    else: 
        m.createNode(nodeType)
        m.rename(name)
    
    #Use any flags to set or connect attrs
    for flag in flags:        
        for a in alpha:
            exec('keywords["'+flag+a+'"] = kwargs.setdefault("'+flag+a+'","None")')
            if keywords[flag+a] != 'None':

                if type(keywords[flag+a]) is list:                
                    strToggleA = ''
                    strToggleB = ''
                    attrPref = ''
                    force = ''
                    
                    if type(keywords[flag+a][0]) is str:
                        strToggleA = '"'
                    if type(keywords[flag+a][1]) is str:
                        strToggleB = '"'
                    if flag == 'attr':
                      attrPref = name+"."
                    if flag == 'conn':
                        force = ',f=True'

                    #print ('m.'+command[i]+'('+strToggleA+attrPref+str(keywords[flag+a][0])+strToggleA+','+strToggleB+str(keywords[flag+a][1])+strToggleB+force+')')
                    exec("m."+command[i]+'('+strToggleA+attrPref+str(keywords[flag+a][0])+strToggleA+','+strToggleB+str(keywords[flag+a][1])+strToggleB+force+')')
                else:
                    print "Error!  The flag input must be a list: "+errorMessage[i]
                    pass                    
                    

        i += 1            


def meMakeIKStretch(what,id):
    inv = 1
    if id == '_R': inv = -1    
    meLengthRatio('IK_'+what.joints[0]+id,'IK_'+what.joints[-1]+id,what,inv)
    obj = ['mid','end']
    objLen = []
    for i in range(len(what.joints)-1):        
        objLen.append(m.getAttr('IK_'+what.joints[i+1]+id+'.tx'))      

        meCreateNodeB('multiplyDivide',what.joints[i+1]+id+'_len_MD',
                      attrA= ['input1X',objLen[i]],
                      connA= [what.name+id+'_lenRatio_MD.outputX',what.joints[i+1]+id+'_len_MD.input2X'],
                      connB= [what.joints[i+1]+id+'_len_MD.outputX','Rig_'+what.joints[i+1]+id+'.tx'] )

        meCreateNodeB('multiplyDivide',what.joints[i+1]+id+'_FKIK_MD',
                      attrA= ['operation',3],
                      connA= [what.name+id+'_lenRatio_MD.outputX',what.joints[i+1]+id+'_FKIK_MD.input1X'],
                      connB= [what.joints[i+1]+id+'_FKIK_MD.outputX',what.joints[i+1]+id+'_len_MD.input2X'],
                      connC= [what.ik+id+'_SW.FK_IK',what.joints[i+1]+id+'_FKIK_MD.input2X'] )

    m.parentConstraint(what.name+id+'_plug_start_IN',what.name+id+'_lenRatio_start')
    
def meLengthRatio(start,end,what,inv):
    dist = 0.00000 
    joints = _meGetJointsBetween(start,end)
    makeCtrl(name = what.name+what.side+'_lenRatio_start',shape='locator',color='white',tgt=start,parentSpace=what.name+what.side+'_Extras',vis=0)
    makeCtrl(name=what.name+what.side+'_lenRatio_end',shape='locator',color='white',tgt=end,parentSpace=what.name+what.side+'_Extras',vis=0)

    meCreateNodeB('distanceBetween',what.name+what.side+'_lenRatio_DB',
                  connA= [what.name+what.side+'_lenRatio_startShape.worldPosition',what.name+what.side+'_lenRatio_DB.point2'],
                  connB= [what.name+what.side+'_lenRatio_endShape.worldPosition',what.name+what.side+'_lenRatio_DB.point1'] )    
  
    for ea in joints:
        if ea != joints[0]:
            dist = dist + abs(m.getAttr(ea+'.tx'))            


    meCreateNodeB('multiplyDivide',what.name+what.side+'_lenRatio_MD',
                attrA= ['operation',2],
                attrB= ['input2X',dist],
                connA= [what.name+what.side+'_lenRatio_DB.distance',what.name+what.side+'_lenRatio_MD.input1X'] )   

    meCreateNodeB('multiplyDivide',what.name+what.side+'_lenRatio_Switch_MD',
                attrA= ['input2X',dist],
                attrB= ['operation',2],
                connA= [what.name+what.side+'_lenRatio_DB.distance',what.name+what.side+'_lenRatio_Switch_MD.input1X'])

    meCreateNodeB('condition',what.name+what.side+'_lenRatio_CON',
                attrA= ['secondTerm',1],
                attrB= ['operation',2],
                attrC= ['colorIfFalseR',dist],
                connA= [what.name+what.side+'_lenRatio_DB.distance',what.name+what.side+'_lenRatio_CON.colorIfTrueR'],
                connB= [what.name+what.side+'_lenRatio_Switch_MD.outputX',what.name+what.side+'_lenRatio_CON.firstTerm'])      

    meCreateNodeB('remapValue',what.name+what.side+'_lenRatio_Fader_RMP',connA= [what.name+what.side+'_lenRatio_CON.outColorR',what.name+what.side+'_lenRatio_Fader_RMP.outputMax'],
                                                                         connB= [what.name+what.side+'_lenRatio_Fader_RMP.outValue',what.name+what.side+'_lenRatio_MD.input1X'],
                                                                         attrA=['outputMin',dist])
    


    
def _meDirectConnect(t,r,s,v,src,tgt):
    varSet = (t,r,s,v)
    set = ("t","r","s","v")
    i = 0
    for var in varSet:
        if var == 1:
          ea = '%s' % set[i]
          if ea == "r":
             m.connectAttr('%s.%sx' % (src,ea), '%s.%sx' % (tgt,ea))
             m.connectAttr('%s.%sy' % (src,ea), '%s.%sy' % (tgt,ea))
             m.connectAttr('%s.%sz' % (src,ea), '%s.%sz' % (tgt,ea))
          else:
             m.connectAttr('%s.%s' % (src,ea), '%s.%s' % (tgt,ea))
        i = i + 1

def meParent(obj):
    m.group (em=True,n='%s_Space' % obj)
    m.delete (m.parentConstraint(obj,'%s_Space' % obj))
    temp = m.ls(obj, l=True)[0]
    prnt = temp.split('|')
    if len(prnt) != 2:
        newPrnt = m.listRelatives(obj, p=True)[0]
        m.parent ('%s_Space' % obj, newPrnt)
    m.parent (obj,'%s_Space' % obj)

def _meGetJointsBetween(start,end):
    m.select(end)   
    kid = m.ls(sl=True,l=True)[0]
    joints = kid.split('|')
    startJnt = joints.index(start)
    endJnt = joints.index(end)
    del joints[0:(startJnt)]
    return joints

def meRollSkel(start,end,roll,side):
    prev = start
    joints = _meGetJointsBetween(start,end)
    print joints 
    j = 0 
    for ea in joints:
        if ea != joints[-1]:             
            start = joints[j]
            end = joints[j+1]
            prev = start
            for i in range(roll):
                tempJoint = m.insertJoint(prev)        
                m.rename (tempJoint,start+"_Roll_"+str(i))
                length = m.getAttr(end+".tx")
                m.setAttr(start+"_Roll_"+str(i)+".tx",length/(roll+1))
                prev = start+"_Roll_"+str(i)
                i += 1
            m.setAttr(end+".tx",length/(roll+1))    
            j += 1
    
def meStretchySpline(what,section,start,end,curve,twistSetup,parentUnder,flip):
  joints = _meGetJointsBetween(start,end)
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

    if what.sJoints[0] in section:
      #meMakeCurves(section+'Twist_aim','','locator','white',section+'Twist_start','',section+'Twist_start','','',1,'')
      makeCtrl(name=section+'Twist_aim',shape='locator',color='white',tgt=section+'Twist_start',parentSpace=section+'Twist_start',vis=1)
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
  if curve != '':
      meCreateNodeB('arcLengthDimension',section+'Spline_stretchRatio_arc',
                    attrA=['uParamValue',(m.getAttr(curve+'.maxValue'))],
                    connA=['%sShape.worldSpace[0]'% curve, '%sSpline_stretchRatio_arc.nurbsGeometry' % section])

  else:
      meCreateNodeB('arcLengthDimension',section+'Spline_stretchRatio_arc',
                    attrA=['uParamValue',(m.getAttr(section+'Spline_crv.maxValue'))],
                    connA=['%sSpline_crvShape.worldSpace[0]' % section, '%sSpline_stretchRatio_arc.nurbsGeometry' % section] )

  meCreateNodeB('multiplyDivide','%sCurveLengthRatio_MD' % section,
              attrA= ['operation',2],
              attrB= ['input2X',(m.getAttr('%sSpline_stretchRatio_arc.arcLength' % section))],
              connA= ['%sSpline_stretchRatio_arc.arcLength' % section,'%sCurveLengthRatio_MD.input1X' % section])  
  
  m.rename (m.listRelatives('%sSpline_stretchRatio_arc' % section,p=True),'%sSpline_ALR' % section)

  #stretchy follow (x axis)
  for ea in joints:
    if ea != joints[-1]:
      m.createNode('multiplyDivide', n='%sMultFactor_MD' % ea)
      m.connectAttr ('%sCurveLengthRatio_MD.outputX' % section,'%sMultFactor_MD.input1X' % ea)
      m.setAttr ('%sMultFactor_MD.input2X' % ea,(m.getAttr('%s.translateX' % ea)))
      m.connectAttr ('%sMultFactor_MD.outputX' % ea,'%s.translateX' % ea)
  
  m.parent (splineStuff[0],parentUnder)
  m.parent (splineStuff[0]+"_ALR",parentUnder)    
  return joints

##spineCurveLengthRatio_MD.outputX
def meSquash(what,start,end,ratioConn,hinge,factor,endCtrl):
  joints = _meGetJointsBetween(start,end)
  i = 0
  if hinge == 1:
    for ea in joints:      
      if 'Roll' in ea:
        joints[i] = ea.replace('base','Rig')
      i+=1



  ##get incremental power values (.2 div by # of joints)
  incr = (factor / len(joints))
  margin = incr
  i = 0
  meCreateNodeB('multiplyDivide','%s_Squash_MD' % what,attrA=['operation',2],attrB=['input1X',1])
  meCreateNodeB('remapValue','%s_Squash_Envelope_RVL' % what,attrA=['outputMin',1],
                                                            connA=[ratioConn,'%s_Squash_Envelope_RVL.outputMax' % what],                                                            
                                                            connB=['%s_Squash_Envelope_RVL.outValue' % what, '%s_Squash_MD.input2X' % what])
  for ea in joints:
      if ea != joints[0] and ea != joints[-1]:

        meCreateNodeB('multiplyDivide','%s_%sPOW_MD' % (what,ea),attrA=['input2X',(1 - margin)],attrB=['operation',3])        

        m.connectAttr ('%s_Squash_MD.outputX' % what,'%s_%sPOW_MD.input1X' % (what,ea))
        m.connectAttr('%s_%sPOW_MD.outputX' % (what,ea), '%s.scaleY' % ea)
        m.connectAttr('%s_%sPOW_MD.outputX' % (what,ea), '%s.scaleZ' % ea)
        i = i + 1
        if i < (len(joints)/2):
                margin = margin  - (incr *6)
        else:
                margin = margin  + (incr *6)

  

## (object,array of attrs, 1 for lock, 1 for make non keyable,0 for hide)
def meLock(obj,attrs,lock,hide,makeNonKey):    
    for ob in obj:        
        for ea in attrs:            
            m.setAttr (ob+"."+ea,l=lock,cb=hide,k=makeNonKey)

def _meTestForMismatch(name,tgt,parentSpace):
    manip = ('t','r','s')
    parentSpaceReq = 0
    for ea in manip:
      if m.getAttr('%s.%s' % (name, ea)) != m.getAttr('%s.%s' % (tgt, ea)) and parentSpace  == 0:
         print '%s mismatch! If something breaks, run script again with parentSpace option turned on' % ea

# def meMakeCurves(name,axis,shape,color,tgt,connection,parentSpace,orientMatch,attr,vis,lockType,**kwargs):
#     flags = kwargs.keys()
#     axes = {'x' : (1,0,0),'y' : (0,1,0),'z' : (0,0,1)}
#     colors = {'darkBlue':5, 'blue' : 6, 'purple' : 9, 'red' : 13, 'green' : 14, 'yellow' : 17, 'white':16 }
#     manip = ('t','r','s')
    

#     if shape is 'circle':
#        m.circle(n=name, ch=False, nr=axes[axis], c=(0, 0, 0) )
#     elif shape is 'box':
#        m.curve(n=name, d= 1, p=[(1,-1,1), (1,-1,-1), (-1,-1,-1), (-1,-1,1), (1,-1,1),(1,1,1), (1,1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1), (-1,-1,-1), (-1,1,-1), (-1,1,1), (-1,-1,1), (1,-1,1), (1,1,1), (-1,1,1)] )
#     elif shape is 'pin':
#        m.curve (n=name, d=1,p=[(0,0,0),(0.2,0,-1.5),(-0.2,0,-1.5),(0,0,0),(0,0.2,-1.5),(0.2,0,-1.5),(-0.2,0,-1.5),(0,0.2,-1.5)])
#     elif shape is 'null':
#        m.group (n=name,em=True)
#     elif shape is 'locator':
#        m.spaceLocator (n=name)
#     elif shape is 'sphere':   
#        m.curve(n=name,d=1, p=[(0,0,1.108194),(0.783612,0,0.783612),(1.108194,0,0),(0.783612,0,-0.783612),(0,0,-1.108194),(-0.783612,0,-0.783612),(-1.108194,0,0),(-0.783612,0,0.783612),(0,0,1.108194),(0,0,1.108194),(0,0.783612,0.783612),(0,1.108194,0),(0,0.783612,-0.783612),(0,0,-1.108194),(0,-0.783612,-0.783612),(0,-1.108194,0),(0,-0.783612,0.783612),(0,0,1.108194),(0,0,1.108194),(-0.783612,0,0.783612),(-1.108194,0,0),(-0.783612,0,-0.783612),(0,0,-1.108194),(0.783612,0,-0.783612),(1.108194,0,0),(0.783612,0,0.783612),(0,0,1.108194)])
#     elif shape is 'diamond':
#        m.curve(n=name, d=1, p=[(0,0,1), (0,0.25,0), (0,0,-1), (0,-0.25,0), (0,0,1),(0,0,1), (1,0,0), (0,0,-1), (-1,0,0), (0,0,1),(0,-0.25,0), (0,-0.25,0), (1,0,0), (0,0.25,0), (-1,0,0), (0,-0.25,0)] )


#     #color the object
#     if color != "":
#        colorShape = m.listRelatives(name,s=True)
#        m.setAttr('%s.overrideEnabled' % colorShape[0],1)
#        m.setAttr('%s.overrideColor' % colorShape[0],colors[color])

#     #rename shape node
#     if shape is not 'null' and 'locator':
#       shape = m.listRelatives(name,s=True)
#       m.rename (shape,'%sShape' % name)

#     ##snap to tgt object - value can be blank if no snap required
#     if tgt != "":
#        m.parentConstraint(tgt,name,mo=False,n='temp')
#        m.delete('temp')
#     else:
#        pass



#     if orientMatch != "":
#       m.delete(m.orientConstraint(orientMatch,name))

#     ##'space' = create single parent space, '%object' = create parent space and parents that space under object,
#     ##'obect = parent directly under object
#     if parentSpace == '':
#         pass
#     if parentSpace == 'space':
#         meParent(name)
#     else:    
#         if parentSpace.find('%')==0:
#             meParent(name)
#             parent = parentSpace.split('%')[1]
#             m.parent(name+"_Space",parent)
#         else:
#             m.parent(name,parentSpace)
    
#     m.setAttr(name+'.v',vis)

#     #setup moveable pivot
#     if 'pivot' in flags:
#       if kwargs['pivot']:
#         meBuildMoveablePivot(name,3)

#     ##connection configuration - add the following based on what you want:
#     ##d - direct connection, t -translate, r -rotate, s-scale
#     ##c - constraint, t -point constr, o -orient constraint, p -parent sconstraint


#     if connection.find('d') != -1 :
#        _meTestForMismatch(name,tgt,parentSpace)
#        for ea in manip:
#          if connection.find(ea) != -1 :
#             m.connectAttr ('%s.%s' % (name,ea), '%s.%s' % (tgt,ea))
#     elif connection.find('c') != -1:
#        if connection.find('t') != -1 :
#           m.pointConstraint(name,tgt,mo=False,n='%s_pointConstr' % name)
#        if connection.find('o') != -1 :
#           m.orientConstraint(name,tgt,mo=False,n='%s_orientConstr' % name)
#        if connection.find('p') != -1 :
#           m.parentConstraint(name,tgt,mo=False,n='%s_parentConstr' % name)
    
#     m.addAttr(name,ln="ctrl",dt="string")
#     m.setAttr(name+".ctrl",attr,type="string")
#     m.setAttr(name+".ctrl",l=1)
      
#     locks = lockType.split('%')
#     lockAttrs = ["t","r","s"]
#     axes = ["x","y","z"]
#     for ea in locks:
#         if ea == "all":
#             for attr in lockAttrs:
#                 for ax in axes:
#                     meLock([name],[attr+ax],1,0,0)
#             meLock([name],"v",1,0,0)    
#         else:
#            for attr in lockAttrs:
#                if ea == attr:
#                     for ax in axes:
#                         meLock([name],[attr+ax],1,0,0)
#            if ea == "v":
#                meLock([name],"v",1,0,0)             
            
def makeCtrl(**kwargs):
    name = kwargs['name']
    if 'axis' in kwargs.keys():           axis = kwargs['axis']
    if 'shape' in kwargs.keys():          shape = kwargs['shape']
    if 'color' in kwargs.keys():          color = kwargs['color']
    if 'tgt ' in kwargs.keys():           tgt = kwargs['tgt']
    if 'connection' in kwargs.keys():     connection = kwargs['connection']
    if 'parentSpace' in kwargs.keys():    parentSpace = kwargs['parentSpace']
    if 'orientMatch' in kwargs.keys():    orientMatch = kwargs['orientMatch']
    if 'attr' in kwargs.keys():           attr = kwargs['attr']
    if 'vis' in kwargs.keys():            vis = kwargs['vis']
    if 'lockType' in kwargs.keys():       lockType = kwargs['lockType']
    if 'pivot' in kwargs.keys():          pivot = kwargs['pivot']

    print 'USING NEW FOR '+kwargs['name']

    flags = kwargs.keys()
    axes = {'x' : (1,0,0),'y' : (0,1,0),'z' : (0,0,1)}
    colors = {'darkBlue':5, 'blue' : 6, 'purple' : 9, 'red' : 13, 'green' : 14, 'yellow' : 17, 'white':16 }
    manip = ('t','r','s')
    

    if shape is 'circle':
       m.circle(n=name, ch=False, nr=axes[axis], c=(0, 0, 0) )
    elif shape is 'box':
       m.curve(n=name, d= 1, p=[(1,-1,1), (1,-1,-1), (-1,-1,-1), (-1,-1,1), (1,-1,1),(1,1,1), (1,1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1), (-1,-1,-1), (-1,1,-1), (-1,1,1), (-1,-1,1), (1,-1,1), (1,1,1), (-1,1,1)] )
    elif shape is 'pin':
       m.curve (n=name, d=1,p=[(0,0,0),(0.2,0,-1.5),(-0.2,0,-1.5),(0,0,0),(0,0.2,-1.5),(0.2,0,-1.5),(-0.2,0,-1.5),(0,0.2,-1.5)])
    elif shape is 'null':
       m.group (n=name,em=True)
    elif shape is 'locator':
       m.spaceLocator (n=name)
    elif shape is 'sphere':   
       m.curve(n=name,d=1, p=[(0,0,1.108194),(0.783612,0,0.783612),(1.108194,0,0),(0.783612,0,-0.783612),(0,0,-1.108194),(-0.783612,0,-0.783612),(-1.108194,0,0),(-0.783612,0,0.783612),(0,0,1.108194),(0,0,1.108194),(0,0.783612,0.783612),(0,1.108194,0),(0,0.783612,-0.783612),(0,0,-1.108194),(0,-0.783612,-0.783612),(0,-1.108194,0),(0,-0.783612,0.783612),(0,0,1.108194),(0,0,1.108194),(-0.783612,0,0.783612),(-1.108194,0,0),(-0.783612,0,-0.783612),(0,0,-1.108194),(0.783612,0,-0.783612),(1.108194,0,0),(0.783612,0,0.783612),(0,0,1.108194)])
    elif shape is 'diamond':
       m.curve(n=name, d=1, p=[(0,0,1), (0,0.25,0), (0,0,-1), (0,-0.25,0), (0,0,1),(0,0,1), (1,0,0), (0,0,-1), (-1,0,0), (0,0,1),(0,-0.25,0), (0,-0.25,0), (1,0,0), (0,0.25,0), (-1,0,0), (0,-0.25,0)] )


    #color the object
    if 'color' in kwargs:
       colorShape = m.listRelatives(name,s=True)
       m.setAttr('%s.overrideEnabled' % colorShape[0],1)
       m.setAttr('%s.overrideColor' % colorShape[0],colors[color])

    #rename shape node
    if shape is not 'null' and 'locator':
      shape = m.listRelatives(name,s=True)
      m.rename (shape,'%sShape' % name)

    ##snap to tgt object - value can be blank if no snap required
    if 'tgt' in kwargs:

       if kwargs['tgt'] != '':
         m.parentConstraint(kwargs['tgt'],kwargs['name'],mo=False,n='temp')
         m.delete('temp')


    if 'orientMatch' in kwargs:
      if kwargs['orientMatch'] != '':
        m.delete(m.orientConstraint(orientMatch,name))

    ##'space' = create single parent space, '%object' = create parent space and parents that space under object,
    ##'obect = parent directly under object
    if 'parentSpace' in kwargs:
      if parentSpace == 'space':
          meParent(name)
      else:    
          if parentSpace.find('%')==0:
              meParent(name)
              parent = parentSpace.split('%')[1]
              m.parent(name+"_Space",parent)
          else:
              m.parent(name,parentSpace)
    
    m.setAttr(name+'.v',vis)

    #setup moveable pivot
    if 'pivot' in kwargs:
      if kwargs['pivot']:
        meBuildMoveablePivot(name,3)

    ##connection configuration - add the following based on what you want:
    ##d - direct connection, t -translate, r -rotate, s-scale
    ##c - constraint, t -point constr, o -orient constraint, p -parent sconstraint

    if ('connection' in kwargs) and ('tgt' in kwargs )and ('parentSpace' in kwargs):
      if kwargs['tgt'] != '':
        if connection.find('d') != -1 :
           _meTestForMismatch(name,kwargs['tgt'],parentSpace)
           for ea in manip:
             if connection.find(ea) != -1 :
                m.connectAttr ('%s.%s' % (name,ea), '%s.%s' % (kwargs['tgt'],ea))
        elif connection.find('c') != -1:
           if connection.find('t') != -1 :
              m.pointConstraint(name,kwargs['tgt'],mo=False,n='%s_pointConstr' % name)
           if connection.find('o') != -1 :
              m.orientConstraint(name,kwargs['tgt'],mo=False,n='%s_orientConstr' % name)
           if connection.find('p') != -1 :
              m.parentConstraint(name,kwargs['tgt'],mo=False,n='%s_parentConstr' % name)
    
    if 'attr' in kwargs.keys():
      m.addAttr(name,ln="ctrl",dt="string")    
      m.setAttr(name+".ctrl",attr,type="string")
      m.setAttr(name+".ctrl",l=1)
      
    if 'lockType' in kwargs.keys():
      locks = lockType.split('%')
      lockAttrs = ["t","r","s"]
      axes = ["x","y","z"]
      if 'locks' in kwargs:
        for ea in locks:
            if ea == "all":
                for attr in lockAttrs:
                    for ax in axes:
                        meLock([name],[attr+ax],1,0,0)
                meLock([name],"v",1,0,0)    
            else:
               for attr in lockAttrs:
                   if ea == attr:
                        for ax in axes:
                            meLock([name],[attr+ax],1,0,0)
               if ea == "v":
                   meLock([name],"v",1,0,0)             
            

def meJoints(what,joints,skelType,parent,parentSpace):    
    
    startJoint = joints[0]
    endJoint = joints[-1]
    if len(joints) == 2:
        jointSet = _meGetJointsBetween(startJoint,endJoint)
    else:
        jointSet = joints    
    for ea in jointSet:
        ea = ea.replace("base_",'')
        switch = 0
        if '%' in parent:
            switch = 1
            parent = parent.replace('%','')        
        if '_Roll' in ea:
            pass
        else:    
            m.duplicate('base_'+ea,n=skelType+'_'+ea,po=True)                            
            m.parent(skelType+'_'+ea,parent)           
            if 'base_'+ea != jointSet[0]:
                m.connectAttr(parent+".scale",skelType+'_'+ea+".inverseScale")
            parent = skelType+'_'+ea      
        if switch == 1:
            meParent(skelType+'_'+what.joints[0]+what.side)    
    if what.name == "Foot":
        pass
    else:    
        if skelType =='IK':
            m.select('IK_'+what.joints[-1]+what.side)
            m.joint(n='IK_'+what.joints[-1]+what.side+'_Spacer')
    if parentSpace == 1:        
        if what.name == "Foot":
            if skelType =='IK':
                pass
            else:
                meParent(skelType+'_'+what.joints[0]+what.side)
      
def meFramework(what):    
    id = what.side
    print "===="+what.name+"====="
    #build character framework
    if m.objExists('WorldOffset') is False:       
        #meMakeCurves('WorldOffset','y','circle','green','','','space','',"world_ctrl",1,"v")
        makeCtrl(name='WorldOffset',axis='y',shape='circle',color='green',parentSpace='space',attr="world_ctrl",vis=1,lockType="v")
        m.group(em=True,n='Rig_Controls')
        m.group(em=True,n='Rig_Utilities')
        m.group(em=True,n=what.charName+"_Rig")
        m.parent('WorldOffset_Space','Rig_Controls')
        m.parent('Rig_Controls','Rig_Utilities',what.charName+"_Rig")
        
        
    #build component framework        
    if m.objExists(what.name+id+"_UTILS") is True:
        pass            
    else:    
        m.group(em=True,n=what.name+id+"_UTILS")        
        m.parent(what.name+id+"_UTILS",'Rig_Utilities')
        m.group(em=True,n=what.name+id+"_Extras")
        m.parent(what.name+id+"_Extras",what.name+id+"_UTILS")
        m.group(em=True,n=what.name+id+"_Controls")
        m.parent(what.name+id+"_Controls",'WorldOffset_Space')
        
        if len(what.startPlugs) != 0:
            for ea in what.startPlugs:        
                #meMakeCurves(what.name+id+'_plug_start_'+ea,'white','locator','',what.startPlugs[ea]+id,'',what.name+id+"_UTILS",'','',1,"")     
                makeCtrl(name=what.name+id+'_plug_start_'+ea,color='white',shape='locator',tgt=what.startPlugs[ea]+id,parentSpace=what.name+id+"_UTILS",vis=1,lockType='')
                m.addAttr(what.name+id+'_plug_start_'+ea,ln="plugInput",dt="string",k=True)
            for ea in what.endPlugs:        
                #meMakeCurves(what.name+id+'_plug_end_'+ea,'white','locator','',what.endPlugs[ea]+id,'',what.name+id+"_UTILS",'','',1,"")
                makeCtrl(name=what.name+id+'_plug_end_'+ea,color='white',shape='locator',tgt=what.endPlugs[ea]+id,parentSpace=what.name+id+"_UTILS",vis=1,lockType='')
                m.addAttr(what.name+id+'_plug_end_'+ea,ln="plugInput",dt="string",k=True)                            

        mePlugRigs(what)
            
def meFilterNonExisting(list,prefix,id):
        remove = []
        i = 0
        for ea in list:
              if (m.objExists(prefix+ea+'_'+str(i)+id)):
                  
                  pass        
              else: 
                  remove.append(ea)        
        for ea in remove:            
            list.remove(ea)

def mePlugTo(what):
    for ea in what.twigConnections:        
        if '_->_' in ea:
            tokens = ea.split('_->_')
            src = what.name+what.side+'_'+tokens[0]        
            subTokens = tokens[1].split('_$_')
            tgt = subTokens[0]        
        if '_<-_' in ea:
            tokens = ea.split('_<-_')     
            tgt = what.name+what.side+'_'+tokens[0]        
            subTokens = tokens[1].split('_$_')
            src = subTokens[0]        
        
        tgt = tgt.replace('_id',what.side)
        src = src.replace('_id',what.side)    
        
        constraintName = src+'_to_'+tgt
        command = 'm.'+subTokens[1]+'("'+src+'","'+tgt+'",mo='+subTokens[2]+',n="'+constraintName+'")'        
                    
        if m.objExists(src) is True:
            if m.objExists(tgt) is True:
                if m.objExists(constraintName) is False:
                    #print command
                    exec(command)
                        
def mePlugRigs(what):
    for ea in what.branchConnections:
        tokens = ea.split('_->_')
        src = tokens[0]
        tgt = tokens[1]
        if '_id' in tgt:
            tgt = tgt.replace('_id',what.side)
        if '_id' in src:
            src = src.replace('_id',what.side)
        constraintName = src+'_to_'+tgt
        command = 'm.parentConstraint("'+src+'","'+tgt+'",mo=True,n="'+constraintName+'")'        
        if m.objExists(src) is True:
            if m.objExists(tgt) is True:
                if m.objExists(constraintName) is False: 
                    m.setAttr(tgt+'.plugInput',constraintName,type="string")
                    #print command
                    exec(command)

def meMultiAttr(nodeName,attrSettingsPairs):
    for ea in attrSettingsPairs:
        m.setAttr(nodeName+"."+ea,attrSettingsPairs[ea])
        
def mePC(obj,snapTo,keep):
    constraintName = m.parentConstraint(snapTo,obj,n=snapTo+"_to_"+obj+"_PCON")
    if keep == 0:
        m.delete(constraintName)