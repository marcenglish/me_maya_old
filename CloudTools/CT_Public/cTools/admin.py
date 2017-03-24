import maya.cmds as m
import maya.mel as mel
from functools import partial
import os

class projectSetupUI():
	def __init__(self,CT_Obj,*arg):
		
		self.defaultTypes = ['Type','Character','Prop','Vehicle','Set','Other']
		self.defaultVariations = ['Dft','Other']

		#make window
		#Get rid of previous window instances
		if m.windowPref('CloudTools_Project_Setup',q=True,ex=True): 
			m.windowPref('CloudTools_Project_Setup', remove=True )
		if m.window('CloudTools_Project_Setup',q=True,ex=True): 
		    m.deleteUI('CloudTools_Project_Setup')

		window = m.window('CloudTools_Project_Setup',title='CloudTools Project Setup')
		row = m.rowColumnLayout( numberOfColumns=1, columnWidth=[(1, 460)] )
		m.paneLayout()
		m.image(image=CT_Obj.path+'/CT_Public/icons/ctHeader_A.jpg')
		m.setParent(row)
		#title and project section
		m.text('')
		m.rowColumnLayout(numberOfColumns=2,columnWidth = [(1,80),(2,110)])
		
		m.text(l='  Project Name:',h=30)
		m.textField('project_FLD',w=110)
		m.text(l='  Mode:',h=50)
		m.optionMenu('Mode_OPT',w=110,en=False)
		m.menuItem('Build_MI',l='Build')
		m.menuItem('Edit_MI',l='Edit')

		#make asset Frame
		assetsFrame = m.frameLayout( label='Assets', borderStyle='in',h=60, p=row )
		m.rowLayout(numberOfColumns=5,h=10, columnWidth = [(1,80),(2,120),(3,85),(4,85),(5,30)])
		m.text('  Asset Info:')
		self.assetName = m.textField('AssetName_TFLD',w=110,tx='Name')
		
		self.assetType = m.optionMenu('Type_OPT',w=80,cc=partial(self.addMenuOption,'Type'))
		for dt in self.defaultTypes:
			m.menuItem(dt)
		
		self.assetVariation = m.optionMenu('Variation_OPT',w=80,cc=partial(self.addMenuOption,'Variation'))
		m.menuItem('Variation')
		for dv in self.defaultVariations:
			m.menuItem(dv)

		m.button(w=25,l='+',h=20,c=partial(self.addAsset),ann='Add Asset to List')

		m.rowLayout(numberOfColumns=1,columnWidth = [(1,430)],p=row)
		self.scrollLayout = m.scrollLayout(horizontalScrollBarThickness=0,h=300,hst=5)
		self.scroll_rc = m.rowColumnLayout( numberOfColumns=5,w=450,columnWidth = [(1,80),(2,120),(3,85),(4,90),(5,20)])

		#make shots frame
		shotsFrame = m.frameLayout( label='Shots', borderStyle='in',h=100, p=row )
		m.rowLayout(numberOfColumns=3,columnWidth = [(1,80),(2,120),(3,130)])
		m.text('  Shot Range:')
		m.textField('StartShot_FLD',tx='0100')
		m.textField('EndShot_FLD',tx='0200')
		m.rowLayout(numberOfColumns=2,columnWidth = [(1,80),(2,150)],p=shotsFrame)
		m.text('  Shot Incrment:',h=40)
		m.textField('Increment_FLD',tx='0100')

		#Setup button
		m.button(p=row,h=40,l='Setup the Project',c=partial(self.projectSetup,CT_Obj))

		m.showWindow(window)


	def addAsset(self,*args):
		#get info from fields
		assetName = m.textField(self.assetName,q=True,tx=True)
		assetType = m.optionMenu(self.assetType,q=True,v=True)
		assetVariation = m.optionMenu(self.assetVariation,q=True,v=True)
		
		#test if any values are still defaults
		if assetName == 'Name' or assetType == 'Type' or assetVariation == 'Variation':
			m.error('One of the fields have not been specified.')
		
		#test if name/type/variation combo already exists
		m.setParent(self.scroll_rc)
		if m.rowColumnLayout(self.scroll_rc,q=True,ca=True):
			if assetName+'_'+assetType+'_'+assetVariation+'_INFO' in m.rowColumnLayout(self.scroll_rc,q=True,ca=True):
				m.error("That's already in the list.")
				
		#add to scroll layout
		asset =assetName+'_'+assetType+'_'+assetVariation 
		m.text(asset +'_INFO',l='',h=25)
		m.text(asset+'_NAME',l=assetName,al='left')
		m.text(asset+'_TYPE',l=assetType,al='left')
		m.text(asset+'_VAR',l=assetVariation,al='left')
		m.button(asset+'_BTN',l='-',c=partial(self.removeAsset,asset),w=15,h=20)

		#reset fields
		m.textField(self.assetName,e=True,tx='Name')
		m.optionMenu(self.assetType,e=True,v='Type')
		m.optionMenu(self.assetVariation,e=True,v='Variation')

	def addMenuOption(self,menu,*args):
		if m.optionMenu(menu+'_OPT',q=True,v=True) == 'Other':

			result = m.promptDialog(
                title='Add '+menu,
                message='Enter Custom '+menu+':',
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')

			if result == 'OK':							        
			        text = m.promptDialog(query=True, text=True)
			        currentItems = m.optionMenu(menu+'_OPT',query=True, ils=True)
			        if text not in currentItems:
			        	m.menuItem(text,p=menu+'_OPT',ia=currentItems[-2])
			        	if menu == 'Type':
			        		self.defaultTypes.append(text)
			        	if menu == 'Variation':
			        		self.defaultVariations.append(text)
		

	def removeAsset(self,asset,*args):
		#remove the selected item ui elements
		m.deleteUI(asset+'_INFO')
		m.deleteUI(asset+'_NAME')
		m.deleteUI(asset+'_TYPE')
		m.deleteUI(asset+'_VAR')
		#cannot delete the ui elment that triggered this script or maya will crash.  Instead they're being dumped
		#in the scrollLayout.
		m.button(asset+'_BTN',e=True,en=False,vis=False,p=self.scrollLayout) 

	def projectSetup(self,CT_Obj,*args):
		#gather info from all fields
		project = m.textField('project_FLD',q=True,tx=True)
		assets = []
		if m.rowColumnLayout(self.scroll_rc,q=True,ca=True):
			for asset in m.rowColumnLayout(self.scroll_rc,q=True,ca=True):
				if '_INFO' in asset:
					assetInfo = asset.split('_')
					assetName = assetInfo[0]
					assetType = assetInfo[1]
					assetVariation = assetInfo[2]
				
					assets.append([assetName,assetType,assetVariation])

		start = int(m.textField('StartShot_FLD',q=True,tx=True))
		end = int(m.textField('EndShot_FLD',q=True,tx=True))
		increment = int(m.textField('Increment_FLD',q=True,tx=True))	
		shots = []

		for i in range(end/increment):
			currentShot = i*increment+start
			if currentShot <= end:
				shots.append(str(currentShot).zfill(4) )

		#print out info
		print project
		print assets
		print shots

		if len(shots) == 0:
			m.error('No shots specified.')

		if len(assets) == 0:
			m.error('No assets added to list.')

		if project == '':
			m.error('No project name specified.')

		m.confirmDialog( title='Confirm', message="Now building folder structure and adding project to config.txt.  Are you sure everything's correct?", button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )

		#create folder structure
		group = ['Assets','Resources','Shots']
		phase = ['Dev','Pub']

		#check which asset types need a folder setup
		types = []
		for asset in assets:
			if asset[1] in self.defaultTypes:
				if asset[1] not in types:
					types.append([asset[1],asset[0],asset[2]])

		#create the folder structure
		os.mkdir(CT_Obj.rootPath+project)
		for g in group:
			os.mkdir(CT_Obj.rootPath+project+'/'+g)
			
			#Assets Branch
			if g == 'Assets':
				for p in phase:
					print 'phase is '+p
					print 'trying to make '+CT_Obj.rootPath+project+'/'+g+'/'+p
					os.mkdir(CT_Obj.rootPath+project+'/'+g+'/'+p)
					for t in types:
						typeRoot = CT_Obj.rootPath+project+'/'+g+'/'+p+'/'+t[0]
						if not os.path.exists(typeRoot): 	os.mkdir(typeRoot)
						if not os.path.exists(typeRoot+'/'+t[1]): 	os.mkdir(typeRoot+'/'+t[1])
						os.mkdir(typeRoot+'/'+t[1]+'/'+t[2])
						if t == 'Character':
							for ea in ['Face','Hi','Lo','Utils']:
								os.mkdir(typeRoot+'/'+t[1]+'/'+t[2]+'/'+ea)
								if ea != 'Utils':
									for dept in CT_Obj.config['assetRoles']:
										os.mkdir(typeRoot+'/'+t[1]+'/'+t[2]+'/'+ea+'/'+dept)
										if p != 'Pub':
											os.mkdir(typeRoot+'/'+t[1]+'/'+t[2]+'/'+ea+'/'+dept+'/'+'Wrk')
			
						else:
							for ea in ['Hi','Lo','Utils']:
								os.mkdir(typeRoot+'/'+t[1]+'/'+t[2]+'/'+ea)
								if ea != 'Utils':
									for dept in CT_Obj.config['assetRoles']:
										os.mkdir(typeRoot+'/'+t[1]+'/'+t[2]+'/'+ea+'/'+dept)
										if p != 'Pub':
											os.mkdir(typeRoot+'/'+t[1]+'/'+t[2]+'/'+ea+'/'+dept+'/'+'Wrk')		
			
			#Resources Branch
			if g == 'Resources':
				for role in CT_Obj.config['assetRoles']:
					os.mkdir(CT_Obj.rootPath+project+'/'+g+'/'+role)
				for role in CT_Obj.config['shotRoles']:
					os.mkdir(CT_Obj.rootPath+project+'/'+g+'/'+role)


			#Shots Branch		
			if g == 'Shots':
				for shot in shots:
					print 'creating shot '+shot
					os.mkdir(CT_Obj.rootPath+project+'/'+g+'/'+shot)
					for dept in CT_Obj.config['shotRoles']:
						os.mkdir(CT_Obj.rootPath+project+'/'+g+'/'+shot+'/'+dept)
						os.mkdir(CT_Obj.rootPath+project+'/'+g+'/'+shot+'/'+dept+'/Wrk')
						if dept == 'Anim':
							os.mkdir(CT_Obj.rootPath+project+'/'+g+'/'+shot+'/'+dept+'/Playblasts')
						else:
							os.mkdir(CT_Obj.rootPath+project+'/'+g+'/'+shot+'/'+dept+'/Renders')

		#edit config.txt
		fileObj = open(CT_Obj.path+'CT_Admin/config.txt','r')
		lines = fileObj.readlines()
		for i in range(len(lines)):
			if 'projects=' in lines[i]:
				lines[i] = lines[i].replace('\r\n','')
				leadingComma = ''
				if lines[i][-1] != ',':
					if lines[i][-1] != '=':
						leadingComma = ','
				lines[i] = lines[i]+leadingComma+project+',\r\n'
		with open (CT_Obj.path+'CT_Admin/config.txt','w') as fileObj:
			fileObj.writelines(lines)

		m.deleteUI('CloudTools_Project_Setup')
		print 'Project directory setup complete.'

#Scene is a class for general procedural scene based tools
class Scene():
	def __init__(self,CT_Obj,*arg):
		self.obj = CT_Obj
		print 'GST loaded'

	def getContents(self):
		topNodes = m.ls(assemblies=True)
		assets = {}

		for tn in topNodes:
			if ':' in tn:
				tnType = ''
				ns = tn.split(':')
				elements = ns[0].split('_')
				if m.objExists(tn+'.rootType'):
					tnType = m.getAttr (tn+'.rootType')
					print tn,' is a root asset of type ',tnType
					if tnType not in assets.keys():
						assets[tnType] = {}					

					if len(elements) == 3:
						assets[tnType][elements[0]] = elements
					if len(elements) == 4:
						assets[tnType][elements[0]+"_"+elements[-1]] = elements

		return assets


	def alembicExport(self):
		plugs=m.pluginInfo( query=True, listPlugins=True )
		basicFilter = "*.abc"
		min =  int(m.playbackOptions(q=True,min=True))
		max =  int(m.playbackOptions(q=True,max=True))

		if "AbcExport" not in plugs :
				m.loadPlugin( 'AbcExport.mll')
		
		assets = self.getContents()
		print assets
		if 'Rig' in assets.keys():
			for rigA in assets['Rig']:
				elements = assets['Rig'][rigA]
				
				filePath = self.obj.savePath.replace('/Dev/','/Pub/')
				if len(elements) == 4:
					character = elements[0]+'_'+elements[1]+'_'+elements[2]+'_'+elements[3]
					geoGrp = elements[0]+'_'+elements[1]+'_'+elements[2]+'_'+elements[3]+':'+elements[0]+"_"+elements[1]+"_Geo_GRP"
				else:
					character = elements[0]+'_'+elements[1]+'_'+elements[2]
					geoGrp = elements[0]+'_'+elements[1]+'_'+elements[2]+':'+elements[0]+"_"+elements[1]+"_Geo_GRP"

				characterFilePath = filePath+'/cache/'+character+'_ANIM.abc'



				cmd = 'AbcExport -j "-fr '+str(min)+' '+str(max)+' -ws -uv -nn -sn -wfg -wv -root '+geoGrp+' -file '+characterFilePath+'"'
				print cmd
			
				mel.eval(cmd)

	@staticmethod
	def alphaIncrement(i):
		alpha = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']	
		div = i/26
		suffix = ''

		if i > 25:
			for cd in range(div):
				suffix += 'A'

		if i-(26*div) < 26:
			suffix += alpha[i-(26*div)]

		return suffix










