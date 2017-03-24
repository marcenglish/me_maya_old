import maya.cmds as m
import maya.mel as mel
import os as os
from pymel.core import *
from functools import partial
import meBuildClasses as meCL
reload(meCL)
import meBuildElements as meBE
reload(meBE)


scriptPath = "D:/EverythingCG/Resrc/SCRIPTS/build/"

fields = ('CharType','CharVar','CharType','CharType_bi','CharType_quad','spine','neck','arm','hand','leg','foot','rollCount','hideExtra','postBuild')
fieldTypes = (0,0,0,1,1,2,2,2,2,2,2,0,0,2)

class meBuild_UI:    
      def __init__(self):         
          # Store UI elements in a dictionary          
          self.UIElements = {}          
          rigElements = ('spine','neck','arm','hand','leg','foot')
          rigElementLabels = ('Spine','Neck','Arm','Hand','Leg','Foot',) 
          rigElementSubDependency = (0,0,3,0,0,6)
          rigElementUpDependency = (0,0,0,2,0,5)
          rigElementLabelPos = ('left','left','left','center','left','center')
          
          if m.window("rigBuilderWindow", exists = True):
             m.deleteUI("rigBuilderWindow")
          
          types = ['biped','quad']
          windowWidth = 300
          windowHeight = 598
          columnWidth = windowWidth /2
          
          self.UIElements["window"] = m.window("rigBuilderWindow", width= windowWidth, height=windowHeight,title="Rig Builder Dev", sizeable = True)          
          self.UIElements["topLevelColumn"] = m.columnLayout('topLevelColumn',adjustableColumn=True,columnAlign = "center")
          self.UIElements["typeColumn"] = m.rowColumnLayout('typeColumn',numberOfColumns=2)                    
          
          self.UIElements["char_Txt"] = m.text(label='Character Name')
          self.UIElements["char_Fld"] = m.textField('CharName',it='anatomicalMan',ec=self.updateAllFields)
          self.UIElements["var_Txt"] = m.text(label='Character Variation')
          self.UIElements["var_Fld"] = m.textField('CharVar',it='Dft',ec=self.updateAllFields)
          self.UIElements["typ_Txt"] = m.text(label='Character Type')
          self.UIElements["typ_Fld"] = m.textField('CharType',it='Human',ec=self.updateAllFields)          
                   
          m.text(label='')
          m.text(label='')
          m.separator()
          m.separator()
          m.text(label='')
          m.text(label='')
          self.UIElements["radioCollection"] = m.radioCollection('CharType')
          m.setParent(self.UIElements["typeColumn"])
          ##          
          self.UIElements["biped"] = m.radioButton('CharType_bi',label='biped')
          self.UIElements["quad"] = m.radioButton('CharType_quad',label='quadruped')

          m.text(label='')
          m.text(label='')
          
          
          i = 0 
          for ea in rigElements:              
              if rigElementLabelPos[i] == 'center':
                indent = '           '
              else:
                indent = '       '              
                
                if i != 0:  
                    m.text(label='')
                    m.text(label='')

                else:      
                    m.text(label='')
                    m.text(label='')
                  
              self.UIElements[ea] = m.text(label=indent+rigElementLabels[i],align='left')
              
              if type(rigElementSubDependency[i]) is tuple:                                    
                    sendElements = []
                    for d in rigElementSubDependency[i]:
                        sendElements.append(rigElements[d])
                    self.UIElements[ea+"_check"] = m.checkBox(rigElements[i],label='',v=1,ofc=partial(self.updateCheckBoxes,sendElements,0))                                      
              else:
                  self.UIElements[ea+"_check"] = m.checkBox(rigElements[i],label='',v=1)                         

              i += 1
              
              
          m.text(label='')
          m.text(label='')    
          m.setParent(self.UIElements["typeColumn"])          
          
          m.setParent(self.UIElements["topLevelColumn"])

          self.UIElements["secondColumn"] = m.columnLayout('secondColumn',adjustableColumn=True,columnAlign = "center")
          self.UIElements["extrasColumn"] = m.rowColumnLayout('extrasColumn',numberOfColumns=2)                              
          self.UIElements["roll_Txt"] = m.text(label='Number of roll joints',align='left')
          self.UIElements["roll_Fld"] = m.textField('rollCount',it='')
          self.UIElements["hide_Txt"] = m.text(label='Hide extra nodes',align='left')
          self.UIElements["hide_Fld"] = m.textField('hideExtra',it='Rig_Utilities')
          m.text(label='')
          m.text(label='')  
          self.UIElements["post_Txt"] = m.text('Run Post-Build',align='left')
          self.UIElements["post_check"] = m.checkBox('postBuild',label='',v=0)   
          m.text(label='')
          m.text(label='')                            
          m.setParent(self.UIElements["extrasColumn"])
          m.setParent(self.UIElements["secondColumn"])         

          self.UIElements["build"] = m.button(label ='Build Rig',align='center',c=partial(self.buttonAction,rigElements))
          self.UIElements["closeWindow"] = m.button(label ='Close Window',align='center',c='m.deleteUI("rigBuilderWindow")')
          
          self.UIElements["advFrame"] = m.frameLayout(label="Advanced", collapsable=True,collapse=True)          
          self.UIElements["advColumn"] = m.columnLayout('advColumn',adjustableColumn=True,columnAlign = "center")
          self.UIElements["advRows"] = m.rowColumnLayout('advRows',numberOfColumns=2)
          self.UIElements["advFit_Txt"] = m.text(label='Fit Shapes',align='left')
          self.UIElements["advFit_Fld"] = m.checkBox('advFit_Chk',label='',v=1)
          self.UIElements["advAtt_Txt"] = m.text(label='Attach Rig',align='left')
          self.UIElements["advAtt_Fld"] = m.checkBox('advAtt_Chk',label='',v=1)
          self.UIElements["saveShapes"] = m.button(label ='Save Ctrl Shapes',align='center',c=self.exportShapes)
          self.UIElements["saveTemplate"] = m.button(label ='Save Template',align='center',c=self.saveTemplate)
          m.setParent(self.UIElements["advRows"])
          m.setParent(self.UIElements["advColumn"])
          m.setParent(self.UIElements["advFrame"])          
          m.showWindow(self.UIElements["window"])
      
      def buttonAction(self,rigElements,*args):

           ##GET THE UI INFO
           name = m.textField('CharName',q=True,text=True)
           var = m.textField('CharVar',q=True,text=True)
           type = 'unspecified'
           buildList= []
           i = 0
           if m.radioButton('CharType_bi',q=True,sl=True) is True:
               type = "biped"
           if m.radioButton('CharType_quad',q=True,sl=True) is True:
               type = "quad"    
           for ea in rigElements:
              test = m.checkBox('rigBuilderWindow|topLevelColumn|typeColumn|'+ea,q=True,value=True)
              if test is True:
                  buildList.append(ea)
                  
                  i +=1
           ##DISPLAY IT   
           print "============"    
           print "Name: "+name
           print "Variation: "+var
           print "Type: "+type
           print 'Builds:'
           print buildList
           print "============"
           ##RUN IT
           
           roll = int(m.textField('rollCount',q=True,text=True)) # needs to be an int
           hidesString = m.textField('hideExtra',q=True,text=True)               
           hidesString = hidesString.replace("'", "")
           hides = hidesString.rsplit(',')               
           buildExtra = m.checkBox('postBuild',q=True,value=True)
           fitShapes = m.checkBox('advFit_Chk',q=True,value=True)
           attach = m.checkBox('advAtt_Chk',q=True,value=True)
           charPath = self.getCharPath()
           
           meCL.createObjSet(type)
           print 'hey'
           if type == 'biped':
               commands =     {'fkA':['FK',meCL.Arm,1],
                    'spine':['FKIKSpline',meCL.Spine,0],
                    'neck':['FKIKSpline',meCL.Neck,0],
                    'hand':['Extras',meCL.Hand,1],
                    'foot':['Extras',meCL.Foot,1],
                    'arm':['FKIK',meCL.Arm,1],
                    'leg':['FKIK',meCL.Leg,1]
                    } 
           if type == 'quad':
               commands =     {'fkA':['FK',meCL.Arm,1],                    
                    'spine':['FKIKSpline',meCL.Spine,0],
                    'neck':['FKIKSpline',meCL.Neck,0],
                    'hand':['Extras',meCL.FrontFoot,1],
                    'foot':['Extras',meCL.Foot,1],
                    'arm':['FKIK',meCL.Arm,1],
                    'leg':['FKIK',meCL.Leg,1]
                    }           
           
           for ea in buildList:           
               print 'Now building '+ea+'....'
               print ''                     
               meBE.meBuild(ea,roll,name,commands)               
           
           
               
           if buildExtra ==1:
               print "building post-script in: "+charPath+name+"_"+var+"_Extra.py"
               execfile (charPath+name+"_"+var+"_Extra.py")
                      
           for hide in hides:
               m.setAttr(hide+".visibility",0) 
           
           if fitShapes is True:
               print "shaping controls.."    
               try:
                   mel.eval('source "'+charPath+'/'+name+'_'+var+'_Shapes.mel"')
               except:
                   print "there's no control shape file"    
               
           
           if attach is True:    
                print "attaching rig"              
                m.select("Rig_*")
                list = m.ls (sl=True, typ="joint")
                #get numjoints in spine:
                numSpine = 0
                for i in range(10):
                  if m.objExists('base_spine_%d' % i):
                    numSpine += 1

                
                



                for ea in list:                  
                    tgt = ea.replace('Rig_','base_')
                    m.parentConstraint(ea,tgt,mo=True)              
                    if 'Roll' in ea:
                      m.connectAttr(ea+'.sy',tgt+'.sy')
                      m.connectAttr(ea+'.sz',tgt+'.sz')

                for i in range(numSpine - 1):
                  m.connectAttr('Rig_spine_%d.sy'%i,'base_spine_%d.sy'%i)
                  m.connectAttr('Rig_spine_%d.sz'%i,'base_spine_%d.sz'%i)




                    
                           
           
      def saveTemplate(self,*args):
          name = m.textField('CharName',q=True,text=True)
          var = m.textField('CharVar',q=True,text=True)
          charPath = self.getCharPath()
          file = charPath+"/"+name+"_"+var+".bld"         
          print charPath
          i = 0
          if os.path.exists(charPath):
              print "path exists"
              try:
                  open(file)
                  print 'Template already exists.'
              except IOError as e:
                  print 'Saving template...'
                  FILE = open(file,"w")
                  for field in fields:
                      state= ''
                      print "for field "+field
                      if fieldTypes[i] == 0:
                          print 'field is text'
                          if m.textField(field,q=True,text=True) == '':
                              state = '[Empty]'
                          else:
                              state = m.textField(field,q=True,text=True)     
                      if fieldTypes[i] == 1:
                          print 'field is radio'
                          if m.radioButton(field,q=True,sl=True) is True:
                              state = 'True'
                          else:
                              state = 'False'    
                      if fieldTypes[i] == 2:
                          print 'field is checkbox'
                          if m.checkBox(field,q=True,value=True) is True:
                              state = 'True'
                          else:
                              state = 'False'                                                           
                      
                      FILE.writelines(field)
                      FILE.writelines(':')                      
                      FILE.writelines(state)
                      FILE.writelines('|')                      
                      i+=1
                  FILE.close()    
                  print 'done.'
          else:
              print "No character path exists"                      

      def updateCheckBoxes(self,index,switch,*args):
          print type(index)
          if type(index) is list:
              for ea in index:    
                  m.checkBox('rigBuilderWindow|topLevelColumn|typeColumn|'+ea,e=True,value=switch)
          else:        
              print index
              m.checkBox('rigBuilderWindow|topLevelColumn|typeColumn|'+index,e=True,value=switch)

      def updateAllFields(self,*args):          
          name = m.textField('CharName',q=True,text=True)
          var = m.textField('CharVar',q=True,text=True)
          i = 0
          charPath = self.getCharPath()
          file = charPath+"/"+name+"_"+var+".bld" 
          linestring = open(file, 'r').read()
          refreshFields= linestring.rsplit('|')
          for rf in refreshFields:
              if rf != '':
                  action = rf.rsplit(':')

                  if fieldTypes[i] == 0:
                      if action[1] == '[Empty]':
                          action[1] = ''
                                                
                      m.textField(action[0],e=True,tx=action[1])     
                  if fieldTypes[i] == 1:
                      if action[1] == 'True':
                          m.radioButton(action[0],e=True,sl=True)
                      else:
                          m.radioButton(action[0],e=True,sl=False)    
                  if fieldTypes[i] == 2:
                      swith = 0
                      if action[1] == 'True':
                          switch = 1
                      else:
                          switch = 0                                            
                      m.checkBox(action[0],e=True,value=switch)                                                           
                  i+=1
                  
      def getCharPath(self):
           name = m.textField('CharName',q=True,text=True)
           charPath = "D:/EverythingCG/Projects/demo/Wrk/Asset/%type%/%name%/Dft/Utils/"           
           charPath = charPath.replace('%type%',m.textField('CharType',q=True,text=True))
           charPath = charPath.replace('%name%',name)
           return charPath            
     
      def exportShapes(self,*args):
          name = m.textField('CharName',q=True,text=True)
          curves = m.ls(typ="nurbsCurve")
          charPath = self.getCharPath()
          file = charPath+"/"+name+"_Dft_Shapes.mel" 
          print "Testing "+charPath
          if os.path.exists(charPath):
              
              print "path exists"
              try:
                  open(file)
                  print 'Shapes file already exists.'
              except IOError as e:
                  print 'Saving shapes...'                  
                  FILE = open(file,"w")                                                              
                  for ea in curves:
                       obj = listRelatives(ea,p=True,c=False)[0]

                       if m.objExists(obj+".ctrl"):
                            print "  exporting "+obj
                            spans = m.getAttr(obj+"Shape.spans")
                            degree = m.getAttr(obj+"Shape.degree")
                            if degree == 1:
                                spans += 1    
                            print "//obj "+obj+" has %d verts" % spans
                            i = 0
                            while i < spans:
                                tx = m.xform(obj+".cv[%d]" % i,q=True,t=True,ws=True)

                                FILE.writelines('move -ws '+str(tx[0])+' '+str(tx[1])+' '+str(tx[2])+' '+obj+'.cv['+str(i)+'];\n' )
                                
                                i += 1
                  FILE.close()    
              print 'done.'
          else:
              print "No character path exists"                              
               