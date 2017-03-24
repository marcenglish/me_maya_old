import maya.cmds as m
from functools import partial
import os
import sys
import os.path
import maya.mel as mel
import getpass
import json
import shutil

import anim
reload(anim)
import rigging
reload(rigging)
import admin
reload (admin)

class sceneSetup():
	def __init__(self,path):		
		self.name = 'CloudTools'
		self.dev = False
		self.admin = False
		self.config = {}
		self.path = path
		self.mayaVer = m.about(v=True).split(' ')[0]
		self.defaultTypes = ['Character','Prop','Vehicle','Set','SetElement','Other']
		self.namespaceDict = {}
		
		#All custom info is parsed from config.txt.  Lines with #'s are skipped.
		f = open(path+'CT_Admin/config.txt')
		for line in f.readlines():						
			if line:
				line = line.replace('\r\n','')
				if '#' not in line:
					items = line.split('=')
					if ',' not in items[-1]:
						self.config[items[0]] = items[-1]
					else:
						self.config[items[0]] = []
						for subItem in items[-1].split(','):
							self.config[items[0]].append(subItem)

		#load the widget directory.  This listing is a dictonary of pointers used for shelf generation.
		f = open(self.path+'CT_Admin/widgetDirectory.json')
		self.widgetDirectory = json.load(f)

		#Internal parameters are here		
		self.user = getpass.getuser()		
		
		if self.config['admin'] == self.user:
			self.admin = True			

		self.config['allRoles'] = self.config['assetRoles'] + self.config['geoRoles'] + self.config['renderRoles']

		

		self.iconPath = self.path+'CT_Public/icons/'
		
		self.role = False

		if 'Dev' in self.path:
				self.dev = True
				self.name = self.name+'_Dev'				
		
		self.initShelfContents()
		self.buildShelf()
		self.rootPath = self.path.replace('/CloudTools','').replace('_Dev','')
		print '\n'
		print self.name+' setup complete.'
		print 'Maya Version: '+self.mayaVer
		print 'Tools path: '+self.path
		print 'Root path: '+self.rootPath

		if self.admin:			
			print 'User is admin..'
			
	def buildShelf(self):
		shelves = m.tabLayout('ShelfLayout',q=True,ca=True)
		
		if 'CloudTools' in shelves:
			m.deleteUI('CloudTools')
		
		if 'CloudTools_Dev' in shelves:
			m.deleteUI('CloudTools_Dev')

		self.cloudShelf = m.shelfLayout(self.name,style='iconOnly',parent = 'ShelfLayout')
		
		for tool in self.shelfOrdered:
			icon = 'pythonFamily.xpm'
			if os.path.exists(self.iconPath+self.shelfContents[tool][0]): 
				icon = self.iconPath+self.shelfContents[tool][0]

			#Reload command has been made static so that the CT_Obj can be reinitialized from a newly opened maya session
			#which wouldn't contain the original objects.

			command=self.shelfContents[tool][1]
			if self.shelfContents[tool][1] == 'reloadStaticCmd':
				command =  ('import maya.cmds as m\n'
							'import sys\n'
							'sys.path = filter (lambda a: "CloudTools" not in a, sys.path)\n'
							'deleteModules = []\n'
							'for ea in sys.modules:\n'
							' if "cTools" in ea: deleteModules.append (ea)\n'
							'for ea in deleteModules:    del(sys.modules[ea])\n'
							'import os\n'
							'if os.path.exists("'+self.path+'CT_Public/INIT.txt'+'"):\n'
							' path = "'+self.path+'"\n'
							'else:\n'							
				            ' filename = m.fileDialog2(fileMode=1, caption="INIT.txt")[0]\n'
				 			' path = filename.replace("CT_Public/INIT.txt","")\n'
				 			'sys.path.append(path+"CT_Public/")\n'
						    'import cTools.setup\n'
				 			'reload( cTools.setup)\n'
				 			'if m.window("resetShelf_WIN",q=True,ex=True):\n'
				 			' m.deleteUI("resetShelf_WIN")\n'
				 			'm.window("resetShelf_WIN",height = 50,width=150)\n'
				 			'm.columnLayout(adjustableColumn=True)\n'
				            '''m.button("resetShelf",c="CT_Obj = cTools.setup.sceneSetup('"+path+"');m.deleteUI(('resetShelf_WIN'))")\n'''
				 			'm.showWindow("resetShelf_WIN")')
				

			btn = m.shelfButton (tool+'_SHLF',image=icon,command=command,ann=self.shelfContents[tool][2],l=tool)

			if self.admin and self.shelfContents[tool][1] == 'reloadStaticCmd':
				m.popupMenu(self.shelfContents[tool][1]+'_PU')
				if 'Dev' in self.path:
					m.menuItem('DevMode',l='Toggle out of DevMode',c=command.replace('CloudTools_Dev','CloudTools'))
				else:
					m.menuItem('DevMode',l='Toggle into DevMode',c=command.replace('CloudTools','CloudTools_Dev'))
				print 'new command is:'
				print command

		if self.admin:
			self.addShelfButtons('Admin')


	def save(self):
		if not self.role:
			m.error('Please setup a role/envionrment first')
		else:
			incrementedFiles = os.listdir(self.savePath+'Wrk')
			increments = []
			newIncrement = 0
			
			testFile = self.filename

			if len(incrementedFiles) > 0:
				for incrementedFile in incrementedFiles:
					if testFile.replace('.ma','') in incrementedFile:
						increments.append(int(incrementedFile.split('_')[-2]))					
			if len(increments) > 0:
				newIncrement = max(increments)+1

			result = m.promptDialog(title='Save Increment', message='Please enter save comments (no spaces or underscores)', button=['Save WIP','Publish', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel',tx='comment')
			
			if result != 'Cancel':
				comments = m.promptDialog(query=True, text=True)
				if result == 'Publish': comments = comments+'-PUB'

				m.file( rename=self.savePath+'/Wrk/'+testFile.replace('.ma','')+'_'+str(newIncrement).zfill(4)+'_'+comments+'.ma' )
				m.file( f=True, type='mayaAscii', save=True)

				if os.path.exists(self.savePath+testFile):
					os.remove(self.savePath+testFile)
				m.file( rename=self.savePath+testFile)
				m.file( f=True, type='mayaAscii', save=True)

				if result == 'Publish' and self.role in self.config['assetRoles']:

					pubPath = self.savePath.replace('/Dev/','/Pub/')
					if os.path.exists(pubPath+testFile):
							os.remove(pubPath+testFile)

					#If the role is asset based but not 'Geo' or 'Rig', import references before publishing
					if self.role in self.config['assetRoles']:
						buildSource = m.file(q=True,l=True)[-1]
						namespaces = {'Skn':'Tex','Tex':'Geo','Rig':'Skn'}
						roles_order = ['Skn','Tex','Geo']


						print self.role
						if self.role in ['Skn','Tex','Rig']:
							m.file(buildSource, f=True,ir=True)
							# print 'testing namespace '+self.namespace
							# #if there is no predefined namespace, figure it out by splitting the top transform node
							# if self.namespace == '':								
							# 	sel = m.ls(typ='transform')
							# 	print 'sel is'
							# 	print sel
							# 	for ea in sel:
							# 	    #if not m.listRelatives(ea,p=True) and ':' in ea:\
							# 	   	if ':' in ea:
							# 	   		self.namespace = ea.split(':')[0]
							# 	   		print 'found namespace '+self.namespace
								    	# break


							#remove namespaces
							for ns in roles_order:
								try:
									m.namespace(mv=(ns,':'),f=True)
									m.namespace(rm=ns)
								except:
									pass
						
					#save file to Pub path and refresh scene
					print pubPath+testFile
					print '---'
					m.file(rename=pubPath+testFile)
					m.file(f=True, type='mayaAscii', save=True)
					m.file(f=True,new=True)


				if result == 'Publish' and self.role in self.config['geoRoles']:
					#cache out geo and 
					Scene = admin.Scene(self)
					Scene.alembicExport()

					# if m.confirmDialog( title='Cache Anim', message='Cache dis bitch?', button=['Yea','Nah'], defaultButton='Yea', cancelButton='Nah', dismissString='Nah' ):

					# 	m.select(m.ls("*:*GEO"))
					# 	if os.path.exists(self.savePath+"cache"):
					# 		shutil.rmtree(self.savePath+"cache")							

					# 	else:
					# 		os.mkdir(self.savePath+"cache")

					# 	cmd = 'doCreateGeometryCache 5 { "2", "1", "10", "OneFile", "1", "'+self.savePath+'cache","0","'+testFile.replace('.ma','')+'_animCache","0", "add", "0", "1", "1","0","1","mcc"} ;'

					#mel.eval(cmd)







	def initShelfContents(self):
		self.shelfContents = 	{	'setStatus': 		['status.png',
														partial(self.setStatusBeta),
														'This will configure CloudTools to work with your scene.'],

									'reloadShelf': 		['reload.png',
														'reloadStaticCmd',
														'This will reload the CloudTools shelf.'],

									'incrementSave': 	['save.png',
														partial(self.save),
														'This will save increments of your work.'], 	


								}	

		self.shelfOrdered = ['setStatus','incrementSave','reloadShelf']


	def setStatusBeta(self):
		
		#Get rid of previous window instances
		if m.windowPref('CloudTools_Beta',q=True,ex=True): 
			m.windowPref('CloudTools_Beta', remove=True )
		if m.window('CloudTools_Beta',q=True,ex=True): 
		    m.deleteUI('CloudTools_Beta')

		window = m.window('CloudTools_Beta',title='CloudTools Beta', w=280,h=420)
		#m.columnLayout('CloudTools_Header',w=280)
		m.columnLayout(columnAttach=('both', 0), rowSpacing=10, columnWidth=300)
		m.image(image=self.path+'/CT_Public/icons/ctHeader_B.jpg',w=300)	

		m.columnLayout(columnAttach=('both', 5), rowSpacing=10, columnWidth=300)
			
		m.text('Choose Project:')
		m.optionMenu('Project_OPT',w=280)
		for project in self.config['projects']:
			if project:
				m.menuItem(label=project.replace('_SHOW',''))

		m.separator(height=2, style='singleDash')
		m.text('Choose role:')
		m.optionMenu('Role_OPT', changeCommand=partial(self.setMenu,menu='Role_OPT'),w=280)
		
		for role in self.config['allRoles']:
		    m.menuItem( label=role )

		m.separator(height=2, style='singleDash')
		m.text('Choose shot or asset:')
		m.optionMenu('TGT_OPT', changeCommand=partial(self.setMenu,menu='TGT_OPT'),w=280 )

		m.separator(height=2, style='singleDash')
		m.text('Choose action:')
		m.optionMenu('ACT_OPT', w=280 )

		m.separator(height=10, style='singleDash')
		m.button("Let's do this!",h=50,c=partial(self.actionButton))

		m.showWindow( 'CloudTools_Beta' )
		m.window( 'CloudTools_Beta',e=True,h=410 )


	def setMenu(self,*args,**kwargs):
		project = m.optionMenu('Project_OPT',q=True,v=True)
		role = m.optionMenu('Role_OPT',q=True,v=True)		
		actions = ['open','build','just set environment']

		#This code is run when the role menu is selected
		if kwargs['menu'] == 'Role_OPT':
			if m.optionMenu('TGT_OPT',q=True,ils=True):
				for menu in m.optionMenu('TGT_OPT',q=True,ils=True):
					m.deleteUI(menu)

			if role in self.config['assetRoles']:					
				print self.rootPath+project+'_SHOW/'+project+'_'+'Assets/Dev/'
				#assetTypes = os.listdir(self.rootPath+project+'_SHOW/'+project+'_'+'Assets/Dev/')
				print self.rootPath[:-1]
				assetTypes = os.listdir(os.path.join(self.rootPath[:-1], project+"_SHOW", "Assets", 'Dev'))
				for AT in assetTypes:
					if '.' not in AT:
						allAssets = os.listdir(self.rootPath+project+'_SHOW/'+'Assets/Dev/'+AT)
						for asset in allAssets:
							if '.' not in asset:
								for variation in os.listdir(self.rootPath+project+'_SHOW/'+'Assets/Dev/'+AT+'/'+asset):
									if '.' not in variation:
										m.menuItem('asset_'+asset+'_'+variation+'_Lo_MI', label=asset+'_'+variation+'_Lo',p='TGT_OPT',ann=AT)
										m.menuItem('asset_'+asset+'_'+variation+'_Hi_MI', label=asset+'_'+variation+'_Hi',p='TGT_OPT',ann=AT)


			if role in self.config['geoRoles']:
				for shot in os.listdir(self.rootPath+project+'_Show/'+project+'_GeoPipe'):
					m.menuItem( label=shot,p='TGT_OPT')

			if role in self.config['renderRoles']:
				for shot in os.listdir(self.rootPath+project+'_Show/'+project+'_RenderPipe'):
					m.menuItem( label=shot,p='TGT_OPT')
		
		#This code is run when the shot/asset menu is selected
		if kwargs['menu'] == 'TGT_OPT':	
			if m.optionMenu('ACT_OPT',q=True,ils=True):
				for menu in m.optionMenu('ACT_OPT',q=True,ils=True):
					m.deleteUI(menu)
			for action in actions:
				m.menuItem( label=action,p='ACT_OPT' )

	def actionButton(self,*args,**kwargs):
		#Assign object setup data
		self.project = m.optionMenu('Project_OPT',q=True,v=True)
		self.role = m.optionMenu('Role_OPT',q=True,v=True)
		self.target = m.optionMenu('TGT_OPT',q=True,v=True)		
		action = m.optionMenu('ACT_OPT',q=True,v=True)		
		fileName = []
		self.namespace = ''
		actionType =  m.optionMenu('ACT_OPT', q=True, v=True) 

		#Assign shot specific data
		if self.role in self.config['geoRoles']:
			self.target = self.target
			self.shot = self.target
			self.assetVariation = ''
			self.assetRez = ''
			self.filename = self.target+'_'+self.role+'.ma'
			self.midPath = '/'+self.project+'_geoPipe'+'/'+self.target+'/'+self.role+'/'
			self.savePath = self.rootPath+self.project+'_SHOW'+self.midPath
			fullFileName = self.rootPath+self.project+'_SHOW'+self.midPath+self.filename

		if self.role in self.config['renderRoles']:
			self.target = self.target
			self.shot = self.target
			self.assetVariation = ''
			self.assetRez = ''
			self.filename = self.target+'_'+self.role+'.ma'
			self.midPath = '/'+self.project+'_renderPipe'+self.target+'/'+self.role+'/'
			self.savePath = self.rootPath+self.project+'_SHOW'+self.midPath
			fullFileName = self.rootPath+self.project+'_SHOW'+self.midPath+self.filename

		#Assign asset specific data
		if self.role in self.config['assetRoles']:
			self.target = m.optionMenu('TGT_OPT',q=True,v=True).split('_')[-3]
			self.assetRez = '_'+m.optionMenu('TGT_OPT',q=True,v=True).split('_')[-1]
			self.assetVariation = '_'+m.optionMenu('TGT_OPT',q=True,v=True).split('_')[-2]			
			self.assetType = m.menuItem('asset_'+self.target+self.assetVariation+self.assetRez+'_MI',q=True,ann=True)						
			self.filename = self.target+self.assetVariation+self.assetRez+'_'+self.role+'.ma'
			self.midPath = '/'+self.project+'_'+'Assets/Dev/'+self.assetType+'/'+self.target+'/'+self.assetVariation.replace('_','')+'/'+self.assetRez.replace('_','')+'/'+self.role+'/'
			fullFileName = self.rootPath+self.project+'_SHOW'+self.midPath+self.filename

			fileOnly = fullFileName.split('/')[-1]
			self.savePath = fullFileName.replace(fileOnly,'')
			
			#If not Geo role, figure out the build source file and namespace.  In order for the autobuild to work, 
			#the following is assumptions are made:			
			# A published Geo file is required for a Tex File
			# A published Tex file should be used for Skn, but Geo can be used if Tex does not exist.
			# A published Skn file is required for a Rig

			#buildSource is the path to the file to be referenced when the setup is build.  The string starts as a 'Geo' file path 
			#and then 'Geo' is substituted with another role identifier as needed. 'Dev' is also substituted for the 'Pub' folder,
			#as only Pub files should be referenced into setups.

			if actionType == 'build':
				buildSource = fullFileName.replace(self.role,'Geo').replace('/Dev/','/Pub/')

				#If a Tex file needs to be built, buildSource is already correct
				if self.role != 'Tex':
					
					#Skn reads the Tex file (or Geo if Tex is not available)
					if self.role == 'Skn':
						if os.path.exists(buildSource.replace('Geo','Tex')):
							buildSource = buildSource.replace('Geo','Tex')
						else:
							if actionType == 'build':
								m.warning('No Tex file exists!  Reverting to Geo.')

					#Rig attempts to read the Skn file
					if self.role == 'Rig':
						testPath = ''
						for ea in ['Geo','Tex']:
							testPath = buildSource.replace('Skn',ea)
							if os.path.exists(testPath):
								testPath = buildSource.replace('Skn',ea)
								print testPath
						print 'reassign to ',testPath
						buildSource = testPath

						# if actionType == 'build':
						# 	m.error('There is no Skn file to build from!')
				print 'build source is'
				print buildSource
				
				self.namespace = buildSource.split('_')[-1].replace('.ma','')

		#Open/build/set environment

		#if opening: fix the file, open it 
		if actionType == 'open':			
			self.fixFileInfo(fullFileName)
			m.file(fullFileName,o=True,f=True)
			
		#If setting environment, do nothing.
		if actionType == 'just set environment':
			print 'Environment set.  Hover over button for environment details'
		
		#If building: 
		if actionType == 'build':
				if self.role in ['Skn','Rig','Tex']:
					self.fixFileInfo(buildSource)
					m.file(new=True,f=True)
					m.file(buildSource,r=True,ns=self.namespace)
				if self.role == 'Anim':
					self.loadSelective('UI',True)

		#remove any shelf buttons non related to core functionality.
		currentShelfContents = m.shelfLayout(self.cloudShelf,q=True,ca=True)
		for CSC in currentShelfContents:
			if CSC.replace('_SHLF','') not in self.shelfContents.keys():
				m.deleteUI(CSC)

		#add role specific tools to shelf
		self.addShelfButtons()

		#update shelf button and delete UI
		m.shelfButton(self.cloudShelf+'|setStatus_SHLF',
						e=True,
						image=self.iconPath+'/status'+self.role+'.png',
						ann='Project: '+self.project+', Role: '+self.role+', Shot/Asset: '+self.target)

		print self.savePath
		m.deleteUI('CloudTools_Beta')

	def loadSelective(self,mode,new,*args):
		#create a UI prompting user to select from available assets.
		self.getAssetNamespaces()
		print self.namespaceDict
		if mode == 'UI':
			assets = {}		
			#build a dictionary of what's been published (Lo,Hi,Cache)
			assetTypes = os.listdir(self.rootPath+self.project+'_SHOW/'+self.project+'_'+'Assets/Dev/')			
			for assetType in assetTypes:
				if '.' not in assetType:
					dirAssets = os.listdir(self.rootPath+self.project+'_SHOW/'+self.project+'_'+'Assets/Pub/'+assetType)		
					for dirAsset in dirAssets:
						if '.' not in dirAsset:
							assets[dirAsset] = {}
							assets[dirAsset]['type'] = assetType
							variations = os.listdir(self.rootPath+self.project+'_SHOW/'+self.project+'_'+'Assets/Pub/'+assetType+'/'+dirAsset)
							for var in variations:
								if '.' not in var:
									assets[dirAsset][var] = []

									if os.path.exists(self.rootPath+self.project+'_SHOW/'+self.project+'_'+'Assets/Pub/'+assetType+'/'+dirAsset+'/'+var+'/Lo/Rig/'+dirAsset+'_'+var+'_Lo_Rig.ma'):
										assets[dirAsset][var].append('Lo')
									if os.path.exists(self.rootPath+self.project+'_SHOW/'+self.project+'_'+'Assets/Pub/'+assetType+'/'+dirAsset+'/'+var+'/Hi/Rig/'+dirAsset+'_'+var+'_Hi_Rig.ma'):
										assets[dirAsset][var].append('Hi')

			#load the selection UI
			if m.window('Load_Assets',q=True,ex=True): 
				m.deleteUI('Load_Assets')
			window = m.window('Load_Assets',title='Load_Assets', w=300,h=100)
			m.rowColumnLayout('MASTER_CL', numberOfColumns=1, columnWidth=[(1, 300)])
			m.rowColumnLayout('SUB_CL', numberOfColumns=4, columnWidth=[(1, 90), (2,70), (3,70), (3,70)])
			
			for t in self.defaultTypes:
				m.text(t+'_header_A',l=t)
				m.text(t+'_header_B',l='')
				m.text(t+'_header_C',l='')
				m.text(t+'_header_D',l='')

				for asset in assets.keys():

				    if assets[asset]['type'] == t:
				    	if assets[asset][var]:

						    m.text(asset+'_TXT',l=asset)

						    #drop down variation selection
						    m.optionMenu(asset+'_VAR_OPT',ann=assets[asset]['type'])
						    for AT in assets[asset]:
						    	m.menuItem( label=AT )			    
							
							#drop down resolution selection
						    m.optionMenu(asset+'_REZ_OPT')			    
						    for v in assets[asset][var]:
						    	m.menuItem(v, label=v )

						    m.textField(asset+'_Quantity_FLD',tx='0')
			
			m.button(c=partial(self.loadSelective,'Action',new), l='Load Assets',p='MASTER_CL')
			m.showWindow( 'Load_Assets' )
		
		#load assets specified in UI
		loadAssets = {}
		if mode == 'Action':
			if new:
				m.file(f=True,new=True)
			for item in m.rowColumnLayout('SUB_CL',q=True,ca=True):
				if '_TXT' in item:								
					asset = item.split('_')[0]
					variation = m.optionMenu(asset+'_VAR_OPT',q=True,v=True)
					rez = m.optionMenu(asset+'_REZ_OPT',q=True,v=True)
					assetType = m.optionMenu(asset+'_VAR_OPT',q=True,ann=True)
					
					loadAssets[asset] = [variation,rez,assetType]

					quantity = m.textField(asset+'_Quantity_FLD',q=True,tx=True)
					loadAssets[asset].append(int(quantity))

			#reference each f the files
			for asset in loadAssets.keys():
				if loadAssets[asset][3]:
					preExistingAssets = 0
					info = loadAssets[asset]

					if asset+'_'+info[0]+'_'+info[1] in self.namespaceDict.keys():						
						preExistingAssets = len(self.namespaceDict[asset+'_'+info[0]+'_'+info[1]])
					
					for i in range(loadAssets[asset][3]):
						print 'preexistingAsset = ',preExistingAssets
						i += preExistingAssets
						suffix = ''
						if i > 0:
							suffix = '_'+admin.Scene.alphaIncrement(i-1)

						
						referenceDir = self.rootPath+self.project+'_SHOW/'+self.project+'_'+'Assets/Pub/'+info[2]+'/'+asset+'/'+info[0]+'/'+info[1]+'/Rig/'
						buildSource = referenceDir+asset+'_'+info[0]+'_'+info[1]+'_Rig.ma'
						self.fixFileInfo(buildSource)
						m.file(buildSource,r=True,ns=asset+'_'+info[0]+'_'+info[1]+suffix)
			
			m.deleteUI('Load_Assets')

	def getAssetNamespaces(self,*args):
		allNamespace = m.namespaceInfo(lon=True)
		self.namespaceDict = {}
		for ns in allNamespace:
			if len(ns.split('_')) == 3:
				self.namespaceDict[ns] = [ns]
		
		for ns in allNamespace:
			if len(ns.split('_')) == 4:
				increment = ns.split('_')[-1]
				incrementStringLength = len(increment)
				crop = incrementStringLength + 1
				asset = ns[:-1*crop]
				self.namespaceDict[asset].append(ns)


		





	def fixFileInfo(self,fullFileName,*args):
		'''This method changes the paths of the referenced files to reflect the current user's project paths.'''

		fileObj = open(fullFileName,'r')
		i = 0
		lines = fileObj.readlines()
		for i in range(len(lines)):
			if 'file' in lines[i] and '-rfn' in lines[i]:
				print 'fixing line:'
				print lines[i]
				print 'show is....',self.project
				oldPath = lines[i].split('"')[-2]
				relativePath = oldPath.split(self.project+'_SHOW')[-1]
				newPath = self.rootPath+self.project+'_SHOW'+relativePath
				lines[i] = lines[i].replace(oldPath,newPath)
				print 'fixed as:'
				print lines[i]

			if 'requires maya' in lines[i]:
				lineElements = lines[i].split('"')
				lines[i] = lineElements[0]+'"'+self.mayaVer+'";\n'

		with open (fullFileName,'w') as fileObj:
			fileObj.writelines(lines)


	def addShelfButtons(self,*args):
		if args:
			role = args[0]
		else:
			role = self.role

		#add role specific tools to shelf
		for tool in self.config[role+'Tools']:
			if tool:
				icon = 'pythonFamily.xpm'
				if os.path.exists(self.iconPath+self.widgetDirectory[tool][0]): 
					icon = self.iconPath+self.widgetDirectory[tool][0]

				command=self.widgetDirectory[tool][1]

				#double underscore is used to identify a tool that requires the CT object
				if '__' in command:
					if 'sceneEdit' in command:
						command = partial(self.loadSelective,'UI',False)





				btn = m.shelfButton (tool+'_SHLF',
									image=icon,
									command=command,
									ann=self.widgetDirectory[tool][2],
									l=tool,
									p=self.cloudShelf)