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

import maya.cmds as m
import maya.mel as mel
import os as os
from pymel import *
from functools import partial
path = 'D:/EverythingCG/Resrc/SCRIPTS/'


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
    m.select(obj)
    m.joint(n=name)    
    m.parent(name,naturalParent)
    
    radius = matchRadius
    if matchRadius == 0:
        radius = m.getAttr(obj+".radius")            
    m.setAttr(name+'.radius',radius)
    
    if offsetType == "Ratio":        
        new_pos = [0.0,0.0,0.0]   
        objSpace_pos = m.getAttr(obj+".t")[0]     
        new_pos[0] = objSpace_pos[0] * offset[0]
        new_pos[1] = objSpace_pos[0] * offset[1]
        new_pos[2] = objSpace_pos[0] * offset[2]
        m.setAttr(name+".t",new_pos[0],new_pos[1],new_pos[2])
    if offsetType == "WorldPosition":
        m.xform(name,ws=True,t=(offset[0],offset[1],offset[2]))

    if jo != '':
        m.setAttr(name+".jointOrientX",jo[0])
        m.setAttr(name+".jointOrientY",jo[1])
        m.setAttr(name+".jointOrientZ",jo[2])
    
    if naturalParent != postParent:
        m.parent(name,postParent)

def meNull(null,snapTo,parent,adopt):
    #snapTo - snaps to object
    #parent - parent under object
    #adopt - array with objects to be parented under this null
    m.group(em=True,n=null)
    m.delete(m.parentConstraint(snapTo,null))
    m.parent(null,parent)    
    if adopt != '':
        for ea in adopt:
            m.parent(ea,null)

def meParentSpace(name):
    parent = m.listRelatives(name,p=True)[0]
    meNull(name+'_Space',name,parent,[name])

def meBBLOC():
    sel = m.ls(sl=True)
    bb =  m.exactWorldBoundingBox(sel)
    x = (bb[0] + bb[3]) / 2
    y = (bb[1] + bb[4]) / 2
    z = (bb[2] + bb[5]) / 2
    name = sel[0].split('.')
    m.spaceLocator(n=name[0]+"_LOC")
    m.setAttr(name[0]+"_LOC.t",x,y,z)

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
    naturalParent = m.listRelatives(obj,c=False,p=True)[0]
    position = m.getAttr(obj+".t")[0]
    meJoint(obj,obj+"_helper"+label,naturalParent,parent,0,offset,offsetType,jo,aimVector)        
    if tgt == '':
        tgt = m.listRelatives(obj,p=False,c=True)            
    if parent == '':
        parent = m.listRelatives(obj)[0]
            
    if driverType == "ac_pb":        
        meNull(obj+"_helper"+label+"_AC",obj,parent,'')    
        meParentSpace(obj+"_helper"+label+"_AC")
        if parent != acParent:
            m.parent(obj+"_helper"+label+"_AC_Space",acParent)
        m.aimConstraint(tgt,obj+"_helper"+label+"_AC",aimVector=aimVector,upVector=upVector,worldUpType='objectrotation',worldUpVector=upVector,worldUpObject=obj+"_helper"+label+"_AC_Space",n=obj+"_helper"+label+"_ACON")
        m.createNode('pairBlend',n=obj+"_helper"+label+"_PB")
        m.setAttr(obj+"_helper"+label+"_PB.rotInterpolation",1) 
        m.setAttr(obj+"_helper"+label+"_PB.weight",0.5)
        m.connectAttr(obj+"_helper"+label+"_ACON.constraintRotateX",obj+"_helper"+label+"_PB.inRotateX2")
        m.connectAttr(obj+"_helper"+label+"_ACON.constraintRotateY",obj+"_helper"+label+"_PB.inRotateY2")
        m.connectAttr(obj+"_helper"+label+"_ACON.constraintRotateZ",obj+"_helper"+label+"_PB.inRotateZ2")
        m.connectAttr(obj+"_helper"+label+"_PB.outRotateX",obj+"_helper"+label+".rx")
        m.connectAttr(obj+"_helper"+label+"_PB.outRotateY",obj+"_helper"+label+".ry")
        m.connectAttr(obj+"_helper"+label+"_PB.outRotateZ",obj+"_helper"+label+".rz")
        m.addAttr(obj+"_helper"+label,ln="weight",at='double',dv=0.5)
        m.setAttr(obj+"_helper"+label+".weight",e=True, k=True, l=False)
        m.connectAttr(obj+"_helper"+label+".weight", obj+"_helper"+label+"_PB.weight")
       
        print "AimConstraint weighted joint setup complete."
        
    if driverType == "direct":
        m.connectAttr(obj+".rx",obj+"_helper"+label+".rx")
        m.connectAttr(obj+".ry",obj+"_helper"+label+".ry")
        m.connectAttr(obj+".rz",obj+"_helper"+label+".rz")
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


pushTextFields = ['activeJoint','jointLabel','weight','parent','acTarget','jointOffsetX','jointOffsetY','jointOffsetZ','acSpace','jointOrientationX','jointOrientationY','jointOrientationZ']
pushMenuItems = ['jot','av','auv','helpType']

class meBuild_UI():    
      def __init__(self):         
          print '\nCHECK\n'
          # Store UI elements in a dictionary          
          launchSel = m.ls(sl=True)
          if len(launchSel) == 0:
              print 'Select a joint, then run the tool.'
          else:         
              if m.window("helperUIWindow", exists = True):
                 m.deleteUI("helperUIWindow")
              windowWidth = 350
              windowHeight = 100
              columnWidth = windowWidth /3    
              activeJoint = self.meGetMenuDeets("activeJoint")
              jointParent = self.meGetMenuDeets("jointParent")                 
              jointChild =  self.meGetMenuDeets("jointChild")
              minus = "-"
              space = " "
              side = "_l_"
              if '_r_' in activeJoint:
                  minus = " "
                  space = "-"
                  side = "_l_"  
              m.window("helperUIWindow", width= windowWidth, height=windowHeight,title="Helper Joint Setup", sizeable = False)          
              m.columnLayout('topLevelColumn',adjustableColumn=True,columnAlign = "center")
              m.rowColumnLayout('basicColumn',numberOfColumns=3,columnWidth=[(1,162),(2,162),(3,26)])                                       
              m.text(label='Active Joint',align='left')
              m.textField('activeJoint',it=activeJoint)
              m.button(label='<<',c=partial(self.meUpdateField,"activeJoint"))
              m.text(label='Helper type',align='left')
              m.optionMenu('helpType',label='',w=160, changeCommand=partial(self.meUpdateFields))
              m.menuItem( label='Offset Pivot - Direct' )  
              m.menuItem( label='Weighted - AimConst/PB' )
              #m.menuItem( label='Weighted - Dot Product',en=False )         
              m.text(label='')           
              m.text(label='Joint label',align='left')
              m.textField('jointLabel',it='')
              m.text(label='')
              m.text(label='Helper joint weight',align='left')
              m.textField('weight',it='0.5')
              m.text(label='')          
              m.text(label='Parent joint under',align='left')
              m.textField('parent',it=jointParent)
              m.button(label='<<',c=partial(self.meUpdateField,"parent"))
              m.text(label='AimConstraint Target',align='left')
              m.textField('acTarget',it=jointChild)
              m.button('acTargetBTN',label='<<',c=partial(self.meUpdateField,"acTarget"))
              m.text(label='Joint Offset',align='left')          
              m.rowColumnLayout('OffsetColumn',numberOfColumns=3,columnWidth=[(1,54),(2,54),(4,54)])                                     
              m.textField('jointOffsetX',it='0.5')
              m.textField('jointOffsetY',it='0')
              m.textField('jointOffsetZ',it='0')
              m.setParent('..')          
              m.button(label='<<',c=partial(self.meUpdateField,"offsets"))     
              m.text(label='Joint OffsetType',align='left')
              m.optionMenu('jot',label='',w=162, changeCommand='print ""' )
              m.menuItem( label='    Ratio' )
              m.menuItem(label='    WorldPosition' )      
              m.text(label='')                    
              m.setParent("basicColumn")
              m.text(label='')
              m.text(label='')
              m.text(label='')                    
              m.setParent("basicColumn")                   
              m.setParent("topLevelColumn")        
              
    
              m.frameLayout(label="Advanced", collapsable=True,collapse=True)          
              m.columnLayout('advColumn',adjustableColumn=True,columnAlign = "center")
              m.rowColumnLayout('advRows',numberOfColumns=3,columnWidth=[(1,160),(2,160),(3,30)])
              m.text('acSpace',label='AimConstraint Parent',align='left')
              m.textField('acSpace',it=jointParent)
              m.button('acSpaceBTN',label='<<',c=partial(self.meUpdateField,"acSpace"))
              m.text(label='AimConstraint Vector',align='left')
              m.optionMenu('av',label='',w=162, changeCommand='print ""')
              m.menuItem( label='    '+space+'X' )
              m.menuItem( label='    '+minus+'X' ) 
              m.menuItem( label='    '+space+'Y' )
              m.menuItem( label='    '+minus+'Y' )
              m.menuItem( label='    '+space+'Z' )
              m.menuItem( label='    '+minus+'Z' )          
              m.text(label='')                    
              m.text(label='AimConstraint UpVector',align='left')
              m.optionMenu('auv',label='',w=50, changeCommand='print ""')
              m.menuItem( label='    '+space+'Z' )
              m.menuItem( label='    '+minus+'Z' ) 
              m.menuItem( label='    '+space+'Y' )
              m.menuItem( label='    '+minus+'Y' )         
              m.menuItem( label='    '+space+'X' )
              m.menuItem( label='    '+minus+'X' )           
              m.text(label='')                              
              m.text(label='Joint Orientation',align='left')
              m.rowColumnLayout('OrientationColumn',numberOfColumns=3,columnWidth=[(1,54),(2,54),(4,54)])                                     
              m.textField('jointOrientationX',it='0')
              m.textField('jointOrientationY',it='0')
              m.textField('jointOrientationZ',it='0')
              m.setParent('..')
              m.setParent('..')
              m.setParent('..')
              m.setParent('..')
             
              m.button(label ='Build Helper Joint',align='center',c=partial(self.meConvertToCommand,"run"))
              m.button(label ='Refresh Details',align='center',c='reload(meHelperUI)')
              m.button(label ='Close Window',align='center',c='m.deleteUI("helperUIWindow")')                      
              m.button(label ='Get Script Output',align='center',c=partial(self.meConvertToCommand,"clipboard"))
              m.text(label='') 
              m.text(l="Copy the setup code to your clipboard:",align='left')
              m.scrollField('output',ww=True,h=70,editable=False)
              self.meUpdateFields()
              m.showWindow("helperUIWindow")



      def meConvertToCommand(self,what,*args):
          data = []
          
          for ea in pushTextFields:       data.append(m.textField(ea,q=True,text=True))
          for ea in pushMenuItems:        data.append(m.optionMenu(ea,q=True,v=True))
              
          jOffset = '('+data[5]+','+data[6]+','+data[7]+')' 
          jOrient =  '('+data[9]+','+data[10]+','+data[11]+')' 
          offsetType = data[12].replace('    ','')
          aimVector = self.meConvertLabelToVector(data[13])
          upVector = self.meConvertLabelToVector(data[14])
          side = '_l_' 
          if '_r_' in data[0]:                      side = '_r_'
          if data[15] == 'Weighted - AimConst/PB':  type = 'ac_pb'
          if data[15] == 'Offset Pivot - Direct':   type = 'direct'        
          outCommand = 'meHelper("'+data[0]+'","'+data[4]+'",'+jOffset+',"'+offsetType+'",'+data[2]+',"'+data[1]+'",'+aimVector+','+upVector+',"'+data[3]+'","'+data[8]+'",'+jOrient+',"'+side+'","'+type+'")'      

          if what == "clipboard":
              m.scrollField('output',e=True,tx=outCommand,ip=1)
          if what == "run":
              m.scrollField('output',e=True,tx=outCommand,ip=1)
              exec(outCommand)


      def meGetMenuDeets(self,what,*args):    
          if m.ls(sl=True):
              joint = m.ls(sl=True)[0]
              if what == 'activeJoint':   return m.ls(sl=True)[0]
              if what == 'jointParent':   return m.listRelatives(joint,p=True)[0]
              if what == 'jointChild':    return m.listRelatives(joint,c=True)[0]


      def meConvertLabelToVector(self,what,*args):
          vector = [1,0,0]
          if what == "    -X":  vector = [-1,0,0]
          if what == "     Y":  vector = [0,1,0]
          if what == "    -Y":  vector = [0,-1,0]
          if what == "     Z":  vector = [0,0,-1]
          if what == "    -Z":  vector = [0,0,-1]
          vectorString = '('+str(vector[0])+','+str(vector[1])+','+str(vector[2])+')'
          return vectorString

      def meUpdateFields(self,*args):
          type = m.optionMenu('helpType',q=True,v=True)
          statusSwitches = {'weight':'textField','acTarget':'textField','acTargetBTN':'button','acSpace':'textField','acSpaceBTN':'button','auv':'optionMenu','av':'optionMenu'}
          if type == "Offset Pivot - Direct":
              for ea in statusSwitches:            
                  command = 'm.'+statusSwitches[ea]+'("'+ea+'",e=True,en=False)'
                  exec(command)
          if type ==  "Weighted - AimConst/PB" or type == "Weighted - Dot Product":
              for ea in statusSwitches:            
                  command = 'm.'+statusSwitches[ea]+'("'+ea+'",e=True,en=True)'
                  exec(command)
                              
      def meUpdateField(self,what,*args):
          obj = m.ls(sl=True)[0]
          if what == 'offsets':
              tgtObj = m.ls(sl=True)[0]
              tgtObjXf = m.xform(tgtObj,q=True,t=True,ws=True)
              m.textField('jointOffsetX',e=True,tx=round(tgtObjXf[0],4))
              m.textField('jointOffsetY',e=True,tx=round(tgtObjXf[1],4))
              m.textField('jointOffsetZ',e=True,tx=round(tgtObjXf[2],4))                
          else:
              m.textField(what,e=True,tx=obj)
          if what == 'parent':
              m.textField('acSpace',e=True,tx=obj)

