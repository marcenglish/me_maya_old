import maya.cmds as m
import json

def BuildMoveablePivot(control,amount):
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
    
    PC(obj=ctrl,snapTo=control ,keep=0)
    PC(obj=invCtrl,snapTo=ctrl,keep=0)
    m.parent(ctrl,parent)
    m.parent(invCtrl,ctrl)
    
    ctrlShape = m.listRelatives(ctrl)[0]

    Node('multiplyDivide',ctrl+'_MD', attrA= ['input2.input2X',-1], attrB= ['input2.input2Y',-1],attrC= ['input2.input2Z',-1])
    m.connectAttr(ctrl +'.translate',ctrl+'_MD.input1')
    m.connectAttr(ctrl+'_MD.output',invCtrl+'.translate')
    parent = invCtrl

    if i > 0:
      scale = 1-(i*.1)
      m.scale(scale,scale,scale,ctrl+'.cv[0:26]',r=True)

    m.connectAttr(control+'.pivotOffsetVis',ctrlShape+'.v')

  m.parent(control,invCtrl)

# def meTempLockRig():
#   everything = m.ls()
#   keywords = ['_UTILS','_Space','_PivotInv','_plug','_Controls']
#   for obj in everything:
#     for key in keywords:
#       if key in obj:        
#         attrs = m.listAttr(obj,k=True)
#         if attrs:
#           for attr in attrs:
#             try:
#               m.setAttr(obj+'.'+attr,l=True)
#             except:
#               pass





def Node(nodeType,name,**kwargs):
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
                    attrPref = ''
                    force = ''
                   
                    if flag == 'attr':
                      attrPref = name+"."
                    if flag == 'conn':
                        force = ',f=True'

                    if command[i] == 'setAttr':
                        exec("m."+command[i]+'("'+attrPref+str(keywords[flag+a][0])+'",'+str(keywords[flag+a][1])+')')
                    if command[i] == 'connectAttr':
                        exec("m."+command[i]+'("'+attrPref+str(keywords[flag+a][0])+'","'+str(keywords[flag+a][1])+'"'+force+')')
                else:
                    print "Error!  The flag input must be a list: "+errorMessage[i]
                    

        i += 1            

    
def DirectConnect(t,r,s,v,src,tgt):
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


## (object,array of attrs, 1 for lock, 1 for make non keyable,0 for hide)
def meLock(obj,attrs,lock,hide,makeNonKey):    
    for ob in obj:        
        for ea in attrs:            
            m.setAttr (ob+"."+ea,l=lock,cb=hide,k=makeNonKey)


def TestForMismatch(name,tgt,parentSpace):
    manip = ('t','r','s')
    parentSpaceReq = 0
    for ea in manip:
      if m.getAttr('%s.%s' % (name, ea)) != m.getAttr('%s.%s' % (tgt, ea)) and parentSpace  == 0:
         print '%s mismatch! If something breaks, run script again with parentSpace option turned on' % ea



def Ctrl(**kwargs):
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
    if 'pss' in kwargs.keys():            pss = kwargs['pss']
    if 'defaultPss' in kwargs.keys():     defaultPss = kwargs['defaultPss']

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
    elif shape is '3qtArrow':
      m.curve(n=name, d= 3, p=[(0,0,0.79314760978716659),(0.61780418618158039,0,0.72633694539114113),(0.87502772727525391,0,0),
(0.63638380165472963,0,-0.63638380165472963),(0,0,-0.90254163183833158),(-0.72075953851430896,-0.0035539292039762763,-0.5733057766459333),(-0.79844250218829749,0,0),(-0.79844250218829749,0,0),(-0.79844250218829749,0,0),(-1.0486295009621833,0,0),(-1.0486295009621833,0,0),
(-1.0486295009621833,0,0),(-0.60927468749097047,0,0.61946620063142133),(-0.60927468749097047,0,0.61946620063142133),(-0.60927468749097047,0,0.61946620063142133),(-0.15764456834942384,0,0),(-0.15764456834942384,0,0),(-0.15764456834942384,0,0),(-0.40803219383446088,0,0),(-0.40803219383446088,0,0),(-0.40803219383446088,0,0),(-0.33943491628815819,0,-0.31879678795500377),(0,0,-0.43549906494434815),(0.32852132361031128,0,-0.31183008041529048),(0.44942585261244217,0,0),(0.31573281484869292,0,0.33831854877126794),
(0,0,0.40561785427157426),(0,0,0.40561785427157426),(0,0,0.40561785427157426),(0,0,0.79314760978716659)] )
    elif shape is 'pinB':
      m.curve (n=name,d=1,p=[(0,0,0),(0,0,-3),(1,0,-3),(1,0,-5),(-1,0,-5),(-1,0,-3),(0,0,-3)])

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
        BuildMoveablePivot(name,3)

    ##connection configuration - add the following based on what you want:
    ##d - direct connection, t -translate, r -rotate, s-scale
    ##c - constraint, t -point constr, o -orient constraint, p -parent sconstraint

    if ('connection' in kwargs) and ('tgt' in kwargs )and ('parentSpace' in kwargs):
      if kwargs['tgt'] != '':
        if connection.find('d') != -1 :
           TestForMismatch(name,kwargs['tgt'],parentSpace)
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
      if 'lockType' in kwargs:
        for ea in locks:
            if ea == "all":
                for attr in lockAttrs:
                    for ax in axes:
                        meLock([name],[attr+ax],1,0,0)
                        #print '\nLOCKING\n'
                meLock([name],"v",1,0,0)    
            else:
               for attr in lockAttrs:
                   if ea == attr:
                        for ax in axes:
                            meLock([name],[attr+ax],1,0,0)
               if ea == "v":
                   meLock([name],"v",1,0,0)             
    
    if 'pss' in kwargs.keys():      
      
      if len(kwargs['pss']) >1:
        SpaceSwitch(obj=name,targets=kwargs['pss'],attrObj=name)
        

        if 'defaultPss' in kwargs.keys():

          if kwargs['defaultPss']:
            
              m.setAttr(name+'.parentSpace',kwargs['defaultPss'])
            

            
def FilterNonExisting(list,prefix,id):
        remove = []
        i = 0
        for ea in list:
              if (m.objExists(prefix+ea+'_'+str(i)+id)):                  
                  pass        
              else: 
                  remove.append(ea)        
        for ea in remove:            
            list.remove(ea)

def meMultiAttr(nodeName,attrSettingsPairs):
    for ea in attrSettingsPairs:
        m.setAttr(nodeName+"."+ea,attrSettingsPairs[ea])
        
def PC(**kwargs):
    sel = m.ls(sl=True)
    obj,snapTo, keep = '','',0

    if kwargs:
      obj = kwargs['obj']
      snapTo = kwargs['snapTo']
      keep = kwargs['keep']

    else:
      obj = sel[1]
      snapTo = sel[0]
      keep = 0

    constraintName = m.parentConstraint(snapTo,obj,n=snapTo+"_to_"+obj+"_PCON")
    if keep == 0:
        m.delete(constraintName)

    

def listSubstitute(listObj,stringPair):
  returnObj = []
  for i in range(len(listObj)):
    returnObj.append(listObj[i].replace(stringPair[0],stringPair[1],1))
  return returnObj

def listAppend(listObj,**kwargs):
  returnObj = []
  for i in range(len(listObj)):
    string = listObj[i]    
    if 'pre' in kwargs:
      string = (kwargs['pre']+string)

    if 'post' in kwargs:    
      string = (string+kwargs['post'])
      
    returnObj.append(string)
  
  return returnObj

def BB():
  sel = m.ls(sl=True)
  if len(sel) == 3:
      up = sel[2]
  if '.' in sel[0]:
    bb = m.exactWorldBoundingBox(sel)  
  else:
    bb = m.exactWorldBoundingBox([sel[0],sel[1]])
  px = (bb[0]+bb[3])*0.5
  py = (bb[1]+bb[4])*0.5
  pz = (bb[2]+bb[5])*0.5
  loc = m.spaceLocator(n='bbLoc')[0]
  m.setAttr(loc+'.t',px,py,pz)

  if len(sel) == 3:
      
      m.spaceLocator(n='tempUp')
      pos = m.xform(sel[2],q=True,t=True,ws=True)
      m.setAttr('tempUp.t',pos[0],pos[1],pos[2])
      
      m.spaceLocator(n='tempAim')
      pos = m.xform(sel[1],q=True,t=True,ws=True)
      m.setAttr('tempAim.t',pos[0],pos[1],pos[2])
          
      m.delete(m.aimConstraint('tempAim',loc,aim=[-1,0,0],wuo='tempUp',wut='object'))

  return loc

def MirrorCtrls():
  sel = m.ls(sl=True)
  for ea in sel:
      if m.objExists(ea.replace('_L','_R')):
          m.select(ea+'.cv[0:*]')
          cvs = m.ls(sl=True)[0].split(':')[-1][:-1]
          for i in range(int(cvs)+1):
              
              pos = m.xform(ea+'.cv['+str(i)+']',q=True,t=True,ws=True)
              m.xform(ea.replace('_L','_R')+'.cv['+str(i)+']',t=[pos[0]*-1,pos[1],pos[2]],ws=True)

def SaveShapes(*args):
  shapeDict = {}
  for ea in m.ls(typ='transform'):
    if m.objExists(ea+'.ctrl'): 
      if m.listRelatives(ea,p=False,s=True):
        for ea in m.filterExpand(ea+'Shape.cv[0:*]',sm=28):
          shapeDict[ea] = m.xform(ea,q=True,t=True,ws=True)

  filename = m.fileDialog2(fileMode=0, caption="Save Shapes",ff='.ma')[0]+'.shp'
  with open(filename, "w") as f:
    f.write(json.dumps(shapeDict))

def LoadShapes(*args):

  filename = m.fileDialog2(fileMode=1, caption="Load Shapes")[0]
  with open(filename, "r") as f:
      shapeDict = json.loads(f.read())

  for ea in shapeDict:
    if m.objExists(ea):
      m.move(shapeDict[ea][0],shapeDict[ea][1],shapeDict[ea][2],ea,ws=True)

def ExtractBindSkel(*args):
  root = m.ls(assemblies=True)[-1]  
  root = m.listRelatives(root,c=True,p=False,typ='joint')[0]
  bind_root = root.replace('base_','bind_')
  m.duplicate(root,n=bind_root)  
  m.delete(m.listRelatives(bind_root,ad=True,type='constraint',f=True))
  for ea in m.listRelatives(bind_root,ad=True,type='joint',f=True):
      name = ea.split('|')[-1]
      m.rename(ea,name.replace('base_','bind_'))
  m.setAttr(bind_root+'.rootType','BindSkel',type='string')


def AttachBindSkel(*args):  
  namespace = ''
  topJoint = None
  if 'Skn' in m.namespaceInfo(lon=True):
    namespace = 'Skn:'  
  for ea in m.ls(typ='joint'):
    if m.objExists(ea+'.rootType'):
      if str(m.getAttr(ea+'.rootType')) == 'BaseSkel':
        topJoint = ea

  

  for ea in m.listRelatives(topJoint,ad=True,type='joint')+[topJoint]:
    if m.objExists(ea.replace('base_',namespace+'bind_')):
        m.pointConstraint(ea,ea.replace('base_',namespace+'bind_'))
        m.orientConstraint(ea,ea.replace('base_',namespace+'bind_'))
        #m.connectAttr(ea+'.t',ea.replace('base_',namespace+'bind_')+'.t')
        m.connectAttr(ea+'.s',ea.replace('base_',namespace+'bind_')+'.s')
        #m.connectAttr(ea+'.rx',ea.replace('base_',namespace+'bind_')+'.rx')
        #m.connectAttr(ea+'.ry',ea.replace('base_',namespace+'bind_')+'.ry')
        #m.connectAttr(ea+'.rz',ea.replace('base_',namespace+'bind_')+'.rz')
    else:
      print ea.replace('base_',namespace+'bind_')+' does not exist.  skipping.'

def DetachBindSkel(*args):
  if 'Skn' in m.namespaceInfo(lon=True):
    namespace = 'Skn:'
  for ea in m.listRelatives('base_Spine_pelvis',ad=True,type='joint')+['base_Spine_pelvis']:
    m.disConnectAttr(ea+'.t',ea.replace('base_',namespace+'bind_')+'.t')
    m.disConnectAttr(ea+'.s',ea.replace('base_',namespace+'bind_')+'.s')
    m.disConnectAttr(ea+'.rx',ea.replace('base_',namespace+'bind_')+'.rx')
    m.disConnectAttr(ea+'.ry',ea.replace('base_',namespace+'bind_')+'.ry')
    m.disConnectAttr(ea+'.rz',ea.replace('base_',namespace+'bind_')+'.rz')

def SpaceSwitch(**kwargs):
  '''obj = object to be modified.  targets = objects to drive. attrObj = object with switch attr'''
  enumString = ''
  expressionString = '{\n'
  i = 0

  for tgt in kwargs['targets']:
    constraint = m.parentConstraint(tgt,kwargs['obj']+'_Space',mo=True)[0]
    if 'plug' in tgt:
      enumTgt = tgt.replace('_plug_start_IN','')
    else:
      enumTgt = tgt
    enumString += enumTgt+"="+str(i)+":"
    expressionString += "if ("+kwargs['attrObj']+".parentSpace == "+str(i)+"){\n"
    j = 0
    for tgtB in kwargs['targets']:
      switchVal = 0
      if i == j:
        switchVal = 1
      expressionString += constraint+"."+tgtB+"W"+str(j)+" = "+str(switchVal)+";\n"
      j += 1
    expressionString += "}\n"
    i+= 1
  
  m.addAttr(kwargs['attrObj'],ln="parentSpace",at='enum',en=enumString,k=True)
  expressionString += "}\n"
  expressionNode = m.expression(n=kwargs['obj']+'_Space'+"_switch",s=expressionString )    

  return expressionNode
