import maya.cmds as cmds
import maya.mel as mel
import os as os
from pymel import *
from functools import partial
from Tkinter import Tk
path = 'D:/EverythingCG/Resrc/SCRIPTS/'

execfile (path+'#skinning/helperSystems.py')


pushTextFields = ['activeJoint','jointLabel','weight','parent','acTarget','jointOffsetX','jointOffsetY','jointOffsetZ','acSpace','jointOrientationX','jointOrientationY','jointOrientationZ']
pushMenuItems = ['jot','av','auv','helpType']

class meBuild_UI():    
      def __init__(self):         
          # Store UI elements in a dictionary          
          launchSel = cmds.ls(sl=True)
          if len(launchSel) == 0:
              pass
          else:         
              if cmds.window("helperUIWindow", exists = True):
                 cmds.deleteUI("helperUIWindow")
              windowWidth = 350
              windowHeight = 100
              columnWidth = windowWidth /3    
              activeJoint = meGetMenuDeets("activeJoint")
              jointParent = meGetMenuDeets("jointParent")                 
              jointChild =  meGetMenuDeets("jointChild")
              minus = "-"
              space = " "
              side = "_l_"
              if '_r_' in activeJoint:
                  minus = " "
                  space = "-"
                  side = "_l_"  
              cmds.window("helperUIWindow", width= windowWidth, height=windowHeight,title="Helper Joint Setup", sizeable = False)          
              cmds.columnLayout('topLevelColumn',adjustableColumn=True,columnAlign = "center")
              cmds.rowColumnLayout('basicColumn',numberOfColumns=3,columnWidth=[(1,162),(2,162),(3,26)])                                       
              cmds.text(label='Active Joint',align='left')
              cmds.textField('activeJoint',it=activeJoint)
              cmds.button(label='<<',c='meUpdateField("activeJoint")')
              cmds.text(label='Helper type',align='left')
              cmds.optionMenu('helpType',label='',w=160, changeCommand=partial(self.meUpdateFields))
              cmds.menuItem( label='Offset Pivot - Direct' )  
              cmds.menuItem( label='Weighted - AimConst/PB' )
              #cmds.menuItem( label='Weighted - Dot Product',en=False )         
              cmds.text(label='')           
              cmds.text(label='Joint label',align='left')
              cmds.textField('jointLabel',it='')
              cmds.text(label='')
              cmds.text(label='Helper joint weight',align='left')
              cmds.textField('weight',it='0.5')
              cmds.text(label='')          
              cmds.text(label='Parent joint under',align='left')
              cmds.textField('parent',it=jointParent)
              cmds.button(label='<<',c='meUpdateField("parent")')
              cmds.text(label='AimConstraint Target',align='left')
              cmds.textField('acTarget',it=jointChild)
              cmds.button('acTargetBTN',label='<<',c=partial(self.meUpdateField,"acTarget"))
              cmds.text(label='Joint Offset',align='left')          
              cmds.rowColumnLayout('OffsetColumn',numberOfColumns=3,columnWidth=[(1,54),(2,54),(4,54)])                                     
              cmds.textField('jointOffsetX',it='0.5')
              cmds.textField('jointOffsetY',it='0')
              cmds.textField('jointOffsetZ',it='0')
              cmds.setParent('..')          
              cmds.button(label='<<',c='meUpdateField("offsets")')     
              cmds.text(label='Joint OffsetType',align='left')
              cmds.optionMenu('jot',label='',w=162, changeCommand='print ""' )
              cmds.menuItem( label='    Ratio' )
              cmds.menuItem(label='    WorldPosition' )      
              cmds.text(label='')                    
              cmds.setParent("basicColumn")
              cmds.text(label='')
              cmds.text(label='')
              cmds.text(label='')                    
              cmds.setParent("basicColumn")                   
              cmds.setParent("topLevelColumn")        
              
    
              cmds.frameLayout(label="Advanced", collapsable=True,collapse=True)          
              cmds.columnLayout('advColumn',adjustableColumn=True,columnAlign = "center")
              cmds.rowColumnLayout('advRows',numberOfColumns=3,columnWidth=[(1,160),(2,160),(3,30)])
              cmds.text('acSpace',label='AimConstraint Parent',align='left')
              cmds.textField('acSpace',it=jointParent)
              cmds.button('acSpaceBTN',label='<<',c=partial(self.meUpdateField,"acSpace"))
              cmds.text(label='AimConstraint Vector',align='left')
              cmds.optionMenu('av',label='',w=162, changeCommand='print ""')
              cmds.menuItem( label='    '+space+'X' )
              cmds.menuItem( label='    '+minus+'X' ) 
              cmds.menuItem( label='    '+space+'Y' )
              cmds.menuItem( label='    '+minus+'Y' )
              cmds.menuItem( label='    '+space+'Z' )
              cmds.menuItem( label='    '+minus+'Z' )          
              cmds.text(label='')                    
              cmds.text(label='AimConstraint UpVector',align='left')
              cmds.optionMenu('auv',label='',w=50, changeCommand='print ""')
              cmds.menuItem( label='    '+space+'Z' )
              cmds.menuItem( label='    '+minus+'Z' ) 
              cmds.menuItem( label='    '+space+'Y' )
              cmds.menuItem( label='    '+minus+'Y' )         
              cmds.menuItem( label='    '+space+'X' )
              cmds.menuItem( label='    '+minus+'X' )           
              cmds.text(label='')                              
              cmds.text(label='Joint Orientation',align='left')
              cmds.rowColumnLayout('OrientationColumn',numberOfColumns=3,columnWidth=[(1,54),(2,54),(4,54)])                                     
              cmds.textField('jointOrientationX',it='0')
              cmds.textField('jointOrientationY',it='0')
              cmds.textField('jointOrientationZ',it='0')
              cmds.setParent('..')
              cmds.setParent('..')
              cmds.setParent('..')
              cmds.setParent('..')
             
              cmds.button(label ='Build Helper Joint',align='center',c=partial(self.meConvertToCommand,"run"))
              cmds.button(label ='Refresh Details',align='center',c='reload(meHelperUI)')
              cmds.button(label ='Close Window',align='center',c='cmds.deleteUI("helperUIWindow")')                      
              cmds.button(label ='Get Script Output',align='center',c=partial(self.meConvertToCommand,"clipboard"))
              cmds.text(label='') 
              cmds.text(l="Copy the setup code to your clipboard:",align='left')
              cmds.scrollField('output',ww=True,h=70,editable=False)
              meUpdateFields()
              cmds.showWindow("helperUIWindow")
      def meConvertToCommand(self,what,*args):
          data = []
          
          for ea in pushTextFields:       data.append(cmds.textField(ea,q=True,text=True))
          for ea in pushMenuItems:        data.append(cmds.optionMenu(ea,q=True,v=True))
              
          jOffset = '('+data[5]+','+data[6]+','+data[7]+')' 
          jOrient =  '('+data[9]+','+data[10]+','+data[11]+')' 
          offsetType = data[12].replace('    ','')
          aimVector = meConvertLabelToVector(data[13])
          upVector = meConvertLabelToVector(data[14])
          side = '_l_' 
          if '_r_' in data[0]:                      side = '_r_'
          if data[15] == 'Weighted - AimConst/PB':  type = 'ac_pb'
          if data[15] == 'Offset Pivot - Direct':   type = 'direct'        
          outCommand = 'meHelper("'+data[0]+'","'+data[4]+'",'+jOffset+',"'+offsetType+'",'+data[2]+',"'+data[1]+'",'+aimVector+','+upVector+',"'+data[3]+'","'+data[8]+'",'+jOrient+',"'+side+'","'+type+'")'      

          if what == "clipboard":
              cmds.scrollField('output',e=True,tx=outCommand,ip=1)
          if what == "run":
              cmds.scrollField('output',e=True,tx=outCommand,ip=1)
              exec(outCommand)


      def meGetMenuDeets(self,what,*args):    
          if cmds.ls(sl=True):
              joint = cmds.ls(sl=True)[0]
              if what == 'activeJoint':   return cmds.ls(sl=True)[0]
              if what == 'jointParent':   return cmds.listRelatives(joint,p=True)[0]
              if what == 'jointChild':    return cmds.listRelatives(joint,c=True)[0]


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
          type = cmds.optionMenu('helpType',q=True,v=True)
          statusSwitches = {'weight':'textField','acTarget':'textField','acTargetBTN':'button','acSpace':'textField','acSpaceBTN':'button','auv':'optionMenu','av':'optionMenu'}
          if type == "Offset Pivot - Direct":
              for ea in statusSwitches:            
                  command = 'cmds.'+statusSwitches[ea]+'("'+ea+'",e=True,en=False)'
                  exec(command)
          if type ==  "Weighted - AimConst/PB" or type == "Weighted - Dot Product":
              for ea in statusSwitches:            
                  command = 'cmds.'+statusSwitches[ea]+'("'+ea+'",e=True,en=True)'
                  exec(command)
                              
      def meUpdateField(self,what,*args):
          obj = cmds.ls(sl=True)[0]
          if what == 'offsets':
              tgtObj = cmds.ls(sl=True)[0]
              tgtObjXf = cmds.xform(tgtObj,q=True,t=True,ws=True)
              cmds.textField('jointOffsetX',e=True,tx=round(tgtObjXf[0],4))
              cmds.textField('jointOffsetY',e=True,tx=round(tgtObjXf[1],4))
              cmds.textField('jointOffsetZ',e=True,tx=round(tgtObjXf[2],4))                
          else:
              cmds.textField(what,e=True,tx=obj)
          if what == 'parent':
              cmds.textField('acSpace',e=True,tx=obj)

meWindow = meBuild_UI()