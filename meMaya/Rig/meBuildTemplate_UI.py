
import maya.cmds as m
import maya.mel as mel
import os as os
import pickle

import meBuildElements
reload(meBuildElements)

from pymel.core import *
from functools import partial

from Rig import meBuildTemplate
reload(meBuildTemplate)

from Rig import meBuildTools
reload(meBuildTools)

from Rig import meTools
reload(meTools)



class UI:    
      def __init__(self): 
          ann = m.shelfButton('setStatus_SHLF',q=True,ann=True)
          self.characterName = None

          ###TEMP PATH
          self.rootPath = "D:/Dropbox/"

          if 'Asset' in ann:
              self.project = ann.split(': ')[1].split(',')[0]
              self.characterName = ann.split(': ')[-1]
              print 'Project is ',self.project
              print 'CharacterName is ',self.characterName



          self.objDict = False
          if m.window("meBuild", exists = True):
             m.deleteUI("meBuild")
          if m.windowPref("meBuild",exists=True):
             m.windowPref("meBuild",remove =True)
          
          self.tempSavePath = 'C:/Users/Marc/Desktop/tempBuild.rb'          
          self.defaults = meBuildTemplate.buildOptions()

          self.windowWidth = 300
          self.windowHeight = 550
          self.connections = []
         
          self.window = m.window('meBuild', width= self.windowWidth,menuBar=True, height=self.windowHeight,title='Rig Builder Dev', sizeable = True)
          
          m.menu( label='File' )
          m.menuItem( label='Save',c=partial(self.saveTemplate))
          m.menuItem( label='Load',c=partial(self.loadTemplate))
          m.menuItem( label='Enable/Disable CT')


          
          m.menu( label='Tools')
          m.menuItem( label='SaveShapes',c=partial(meTools.SaveShapes))
          m.menuItem( label='LoadShapes',c=partial(meTools.LoadShapes))
          m.menuItem( label='ExtractBindSkel',c=partial(meTools.ExtractBindSkel))
          m.menuItem( label='AttachBindSkel',c=partial(meTools.AttachBindSkel))
          m.menuItem( label='DetachBindSkel',c=partial(meTools.DetachBindSkel))

          m.menu(label='CT')
          m.menuItem(label='ReferenceSkn',c=partial(self.loader,'Skn','Ref'))

          m.menu( label='Help', helpMenu=True )
          m.menuItem( 'Application..."', label='About' )

          topCol = m.columnLayout('TOP_COL')
          
          #ELEMENT CREATION/EDITING FRAME
          ceFrame = m.frameLayout('CE_FRM', l= 'Create/Edit Element',mh=5,width = self.windowWidth, height =490,p=topCol)
          ceTopCol = m.columnLayout('CE_TOP_COL')
          
          ceMidCol = m.rowColumnLayout('CE_MID_RCOL',numberOfColumns=2,columnAlign=[(1,'left'),(2,'left')],columnWidth=[(1,self.windowWidth*0.35),(2,self.windowWidth*0.55)])

          m.text(label='  Obj Naming',h=25)
          m.optionMenu('TEMPLATE_OPT',l='',w=self.windowWidth*0.55,cc=partial(self.autoComplete))
          for tt in self.defaults['primaryTemplates']:
          	m.menuItem(tt)

          m.setParent(ceMidCol)

          m.text(label='  Obj Type',h=25)
          m.optionMenu('CREATE_OPT',l='',w=self.windowWidth*0.55)
          for bt in self.defaults['build']:
          	m.menuItem(bt)

          ceLowCol = m.rowColumnLayout('CE_LOW_RCOL',p=ceTopCol,numberOfColumns=3,columnAlign=[(1,'left'),(2,'left'),(3,'left')],columnWidth=[(1,self.windowWidth*0.35),(2,self.windowWidth*0.27),(2,self.windowWidth*0.27),])

          m.text(label='  Number of Joints',h=25)
          m.intField('NUMJNTS_FLD',w=self.windowWidth*0.27)
          m.text(label='  ',h=25)

          m.text(label='  ID (Left/Right)',h=25)
          m.textField('SIDEL_FLD',w=self.windowWidth*0.27)
          m.textField('SIDER_FLD',w=self.windowWidth*0.27,en=False)

          m.text(label='  Mirror',h=25)
          m.checkBox('MIRROR_CHK',l='',onc='import maya.cmds as m;m.textField("SIDER_FLD",e=True,en=True)',ofc='import maya.cmds as m;m.textField("SIDER_FLD",e=True,en=False)')
          
          m.setParent('CE_TOP_COL')
          m.button(l='Build Component',w=self.windowWidth*0.99,c=partial(self.buildComponent))
          m.separator(style='double',height=7)  
          m.scrollLayout('CONTENTS_SCR',w=self.windowWidth*0.99,h=265)

          m.rowColumnLayout('CONN_RCOL',numberOfColumns=3,p=('CE_TOP_COL'),columnAlign=[(1,'left'),(2,'left'),(3,'left')],columnWidth=[(1,self.windowWidth*0.32),(2,self.windowWidth*0.32),(3,self.windowWidth*0.32)])
          m.text('A',l='',h=4)
          m.text('B',l='',h=4)
          m.text('C',l='',h=4)
          m.button('Connect',c=partial(self.connectFromUI))
          m.button('MatchOrient',c=partial(self.matchParentOrient))
          m.button('Disconnect',c=partial(self.disconnectFromUI))
          #ADVANCED FRAME
          bldFrame = m.frameLayout('BLD_FRM',l= 'Project Settings',mh=6,width = self.windowWidth, cll=True,cl=True,p=topCol,cc=partial(self.fixWindow))
          bldTopCol = m.rowColumnLayout('BLD_TOP_RCOL',numberOfColumns=2,columnAlign=[(1,'left'),(2,'left')],columnWidth=[(1,self.windowWidth*0.35),(2,self.windowWidth*0.55)])

          m.text('  Job Name:',h=25)
          m.optionMenu('JOB_OPT',l='',w=self.windowWidth*0.55)

          m.setParent(bldTopCol)
          m.text('  Char Name:',h=25)
          m.optionMenu('CHAR_OPT',l='',w=self.windowWidth*0.55)

          m.setParent(bldTopCol)
          m.text('  Variation:',h=25)
          m.optionMenu('VAR_OPT',l='',w=self.windowWidth*0.55)

          m.setParent(bldTopCol)
          m.text('  Resolution:',h=25)
          m.optionMenu('RES_OPT',l='',w=self.windowWidth*0.55)

          m.setParent(bldTopCol)
          m.text('  Export Template:',h=25)
          m.checkBox('TEMPL_CHK',l='')

          m.text('  Export Skeleton:',h=25)
          m.checkBox('SKEL_CHK',l='')

          m.text('  Build Rig:',h=25)
          m.checkBox('BLD_CHK',v=1,l='')

          m.text('  Connect Rig:',h=25)
          m.checkBox('CONN_CHK',v=1,l='')
          
          m.text('  Print Data:',h=25)
          m.checkBox('PRNT_CHK',v=0,l='')

          m.setParent(topCol)
          m.button(l='Build Rig!',w=self.windowWidth,h=40,c=partial(self.buildAll))

          m.showWindow(self.window)

      def loader(self,role,type,*args):
        path = self.rootPath+self.project+'/Assets/Pub/Character/'+self.characterName+'/Dft/Hi/Skn/'+self.characterName+'_Dft_Hi_Skn.ma'
        m.file(path,r=True,ns='Skn')



      def saveTemplate(self,*args):
        filename = m.fileDialog2(fileMode=0, caption="Export Rig Template",ff='.ma')
        
        m.file( rename = filename[0])
        m.file(ea=True,type='mayaAscii' )
        objFilename = filename[0].replace('.ma','.obj')        
        with open(objFilename, 'wb') as output:        
          pickle.dump(self,output,pickle.HIGHEST_PROTOCOL)
      
      def loadTemplate(self,*args):
        
        #load maya file and pickel object file.  namespaces are used when merging saved components with current ones because
        #they keep the filename from getting inserted into clashing nodes.  
        ns = ''
        filename = m.fileDialog2(fileMode=1, caption="Import Rig Template")
        if len(m.ls(assemblies=True)) > 4:          
          ns = 'template'
          m.file( filename[0], i=True ,ns=ns)
          ns += ":"
        else:
          m.file( filename[0], i=True)


        
        
        objFilename = filename[0].replace('.ma','.obj')        
        with open(objFilename, 'rb') as input:
            loadedObj = pickle.load(input)            
            
            #add namespaces to all attributes
            for ea in loadedObj.objDict:
              for i in range(len(ea['obj'].shapes)):
                ea['obj'].shapes[i] = ns+ea['obj'].shapes[i]
              for i in range(len(ea['obj'].primary)):
                ea['obj'].primary[i] = ns+ea['obj'].primary[i]              
              ea['obj'].upLoc = ns+ea['obj'].upLoc
              ea['obj'].group = ns+ea['obj'].group
              if ea['obj'].connectedTo:
                ea['obj'].connectedTo = ns+ea['obj'].connectedTo




        

        #merge with existing object dictionary
        if self.objDict:
          for ea in loadedObj.objDict:
            self.objDict.append(ea)
        else:
          self.objDict = loadedObj.objDict
        

        

        self.updateUIContents()
        meBuildTemplate.rigObj.objDict = self.objDict



          





      def saveTemplateCT(self,*args):
        print 'this function will save the rig template in the proper cloudtools folder'
      
      def loadTemplateCT(self,*args):
        print 'this function will save the rig template in the proper cloudtools folder'

      def fixWindow(self,*args):      	
      	m.window(self.window, e=True, height=self.windowHeight)


      def buildAll(self,*args):
        verbose = False
        meBuildTemplate.convertToSkel(self)
        #build rig if specified
        # if m.optionMenu('CHAR_OPT',q=True,v=True):
        #   characterName = m.optionMenu('CHAR_OPT',q=True,v=True)
        # else:
        #   characterName = 'unNamed'



        if m.checkBox('PRNT_CHK',q=True,v=True):
          verbose = True

        if m.checkBox('BLD_CHK',q=True,v=True):
          meBuildElements.meNewBuild(self,self.characterName,verbose)

        if m.checkBox('CONN_CHK',q=True,v=True):
          meBuildTools.ConnectRig()
        self.patchOfShame(True)

      def buildComponent(self,*args):
        #Get UI Data
      	name = m.optionMenu('CREATE_OPT',q=True,v=True)
      	templateType = m.optionMenu('TEMPLATE_OPT',q=True,v=True)
      	number = int(m.intField('NUMJNTS_FLD',q=True,v=True))
        
        if number != 0:      	
          if m.textField('SIDER_FLD',q=True,en=True):
            extraID = [m.textField('SIDEL_FLD',q=True,tx=True),m.textField('SIDER_FLD',q=True,tx=True)]
          else:
            extraID = [m.textField('SIDEL_FLD',q=True,tx=True)]
          
          #test for conflict with existing objects - this part's kind of screwy as I seemed to have given opposide defenitions for 
          #'name' and 'type' in the UI
          clashing = False
          if meBuildTemplate.rigObj.objDict:
            for obj in self.objDict:
              obj = obj['obj']
              if name == obj.type:
                if templateType == obj.name:
                  if extraID[0] == obj.sides[0]:
                    clashing = True

          if clashing:
            m.confirmDialog(title='Objects clashing!', message='This object clashes with another already in the list.\nPlease give it an extra identifier to differentiate it.',button=['ok'])
          
          else:
            if 'defaultRoll' in self.defaults['template'][templateType]:
            	roll = self.defaults['template'][templateType]['defaultRoll']
            else:
            	roll = False

            inBtwn = number-2

            self.tempObj = meBuildTemplate.rigObj(templateType,name,roll=roll,inBtwn=inBtwn,mirror=extraID,templateType=templateType,uiObj=self)
            self.tempObj.build(self)

            self.updateUIContents()
        

      def patchOfShame(self,run,*args):
        '''Always run after build.  Use this for any temporary fixes that wouldn't go into the characterScript.'''
        
        if run: 
          print 'running patchOfShame :('
          for ea in ['__L','__R']:
            if m.objExists('Arm_Rig_wrist'+ea) and m.objExists('base_Hand_wrist'+ea):
              m.parentConstraint('Arm_Rig_wrist'+ea,'base_Hand_wrist'+ea)
              m.parentConstraint('Hand'+ea+'_plug_start_IN','Hand'+ea+'_plug_end_OUT',mo=True)
        
            #just added for fix fk foot orientation issue
            m.parentConstraint("Leg_FK_ankle"+ea,"Foot_FK_ankle"+ea,mo=False)
            m.delete("Foot_FK_ankle"+ea+"_CTRL_Space_pointConstraint1")
            m.parentConstraint("Leg_FK_ankle"+ea,"Foot_FK_ankle"+ea+"_CTRL_Space")

        




      def autoComplete(self,*args):
      	'''This section attemps to complete the extra fields.  They are still modifiable, but populated with more likely settings.'''
      	
      	rigObj = m.optionMenu('CREATE_OPT',q=True,v=True)
      	templateType = m.optionMenu('TEMPLATE_OPT',q=True,v=True)

      	if templateType in self.defaults['commonSymmetricals']:
      		extraID = self.defaults['sideIds']
      		m.textField('SIDEL_FLD',e=True,tx=extraID[0])
      		m.textField('SIDER_FLD',e=True,tx=extraID[1],en=True)
      		m.checkBox('MIRROR_CHK',e=True,v=1)
      	else:
      		m.textField('SIDEL_FLD',e=True,tx='')
      		m.textField('SIDER_FLD',e=True,tx='',en=False)
      		m.checkBox('MIRROR_CHK',e=True,v=0)

      	m.optionMenu('CREATE_OPT',e=True,v=self.defaults['template'][templateType]['defaultType'])
      	m.intField('NUMJNTS_FLD',e=True,v=self.defaults['template'][templateType]['defaultLength'][0],ed=self.defaults['template'][templateType]['defaultLength'][1])

      def connectFromUI(self,*args):
      	meBuildTemplate.connectRigs('Manual',self)
      	self.updateUIContents()

      def disconnectFromUI(self,*args):
        meBuildTemplate.disconnectRigs('Manual',self)
        self.updateUIContents()

      def matchParentOrient(self,*args):
        obj = meBuildTemplate.getFromItem(m.ls(sl=True)[0],self,type='obj')
        print obj.connectedTo
        #get obj from parent, get obj.upLoc form parent and use as aimConstr upLoc

      def deleteFromUI(self,obj,UIid,id,UIObj,*args):
      	m.delete(obj.group)
      	del UIObj.objDict[id]

      	self.updateUIContents()

      def parseScene(self):
        for top in m.ls(typ='transform'):
          parent = m.listRelatives(top,p=True)
          if not parent and m.nodeType(top+'Shape') != 'camera':
            print top





      def updateUIContents(self,*args):
      	'''Updates the contents of the scroll layout to match the contents of meBuildTemplate.rigObj.objDict'''


      	scrollWidth = self.windowWidth*0.99

      	if m.scrollLayout('CONTENTS_SCR',q=True,ca=True):
      		for ea in m.scrollLayout('CONTENTS_SCR',q=True,ca=True):
      	#		print m.scrollLayout('CONTENTS_SCR',q=True,ca=True)
      			m.deleteUI(ea)
        #print range(len(self.objDict))
        self.connections = []
      	for i in range(len(self.objDict)):
          connectedToObject = False
          

          m.columnLayout('CONTENTS_'+str(i)+'_TOP_COL',p='CONTENTS_SCR')
          m.rowColumnLayout('CONTENTS_'+str(i)+'_TOP_RCOL',numberOfColumns=2,columnAlign=[(1,'left'),(2,'left')],columnWidth=[(1,scrollWidth*0.75),(2,scrollWidth*0.15)], p='CONTENTS_'+str(i)+'_TOP_COL')
          m.rowColumnLayout('CONTENTS_'+str(i)+'_RCOL',numberOfColumns=2,columnAlign=[(1,'left'),(2,'left')],columnWidth=[(1,scrollWidth*0.3),(2,scrollWidth*0.5)], p='CONTENTS_'+str(i)+'_TOP_RCOL')
          m.text('  Template: ')
          m.text('temp',l=self.objDict[i]['name'])
          m.text('  Type: ')
          m.text('type',l=self.objDict[i]['obj'].type)
          m.text('  Mirrored: ')
          m.text('mirr',l=self.objDict[i]['obj'].mirrored)
          m.text('  Connected To: ')
          m.text('conn',l=str(self.objDict[i]['obj'].connectedTo))
          m.text('  Extra ID(s): ')
          m.text('extraId',l=str(self.objDict[i]['obj'].sides))

          if self.objDict[i]['obj'].connectedTo:
            connectedToObject = meBuildTemplate.getFromItem(self.objDict[i]['obj'].connectedTo,self,type='obj')

          m.button(l='Delete',p='CONTENTS_'+str(i)+'_TOP_RCOL',bgc=(0.25,0,0),c=partial(self.deleteFromUI,self.objDict[i]['obj'],i,self.objDict[i]['obj'].id,self))

          m.separator(style='double',p='CONTENTS_'+str(i)+'_TOP_RCOL')
          m.separator(style='double',p='CONTENTS_'+str(i)+'_TOP_RCOL')

          self.connections.append([self.objDict[i]['obj'].connectedTo,self.objDict[i]['obj'],connectedToObject])