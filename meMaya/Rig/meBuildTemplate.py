import maya.cmds as m
from Rig import meTools
reload (meTools)

#TBD: add functionality for dynamic naming conventions


def buildOptions():
	'''Returns a dictionary containing currently available build and template types.  As new template types are created, they should
	be added to this list so they can populate the UI.'''

	sideIds = ['__L','__R']
	returnVar = {}	
	returnVar['commonSymmetricals'] = ['Arm','ArmA','Leg','LegA','LegB','LegC','Hand','Foot','Clavicle','Femur','Palm','Metacarpal','PhalangeB','Finger','Thumb','Index','Middle','Ring','Pinky','Eye','thumbSingle','indexSingle','middleSingle','pinkySingle','ringSingle',]
	returnVar['sideIds'] = sideIds
	returnVar['build'] = ['IKFK_spline','IKFK_hinge','IKFK_single','INV_foot','hand','Static','Wheel','IKFK_doubleHinge']
	returnVar['primaryTemplates'] = ['Spine','Neck','Arm','ArmA','Leg','LegA','LegB','LegC','frontWheel','rearWheel','Hand','Foot','Clavicle','AxleFront','AxleRear','Femur','Palm','Finger','Thumb','Index','Middle','Ring','Pinky','Custom','Head','PhalangeB','Jaw','Prop','thumbSingle','indexSingle','middleSingle','pinkySingle','ringSingle','SpineSegmentA']

	returnVar['ctrlColors'] = {'PrimaryLR':{sideIds[0]:'blue',sideIds[1]:'red'},
								'SecondaryLR':{sideIds[0]:'lightBlue',sideIds[1]:'pink'}}

	returnVar['buildComplex'] = ['Hand']
	returnVar['template'] = {	'Arm':{'isIterator':False,

									'joints':['shoulder','elbow','wrist'],

									'defaultType':'IKFK_hinge',

									'defaultLength':[3,True], #first value is default number of joints, second val is editable flag.

									'defaultRoll':4,

									'defaultPss':1,

									'switchLoc':-1,

									'upVector':(0,1,0),

									'ikHandleOrient':'LastJoint'

									}, 

								'ArmA':{'isIterator':False,

									'joints':['shoulderA','elbowA','wristA'],

									'defaultType':'IKFK_hinge',

									'defaultLength':[3,True], #first value is default number of joints, second val is editable flag.

									'defaultRoll':4,

									'defaultPss':1,

									'switchLoc':-1,

									'upVector':(0,1,0),

									'ikHandleOrient':'LastJoint'

									}, 


								'Leg':{'isIterator':False,

									'joints':['hip','knee','ankle'],

									'defaultType':'IKFK_hinge',

									'defaultLength':[3,True],

									'defaultRoll':4,

									'defaultPss':1,

									'switchLoc':-1,

									'upVector':(0,1,0),

									'ikHandleOrient':'World'

									},



								'LegA':{'isIterator':False,

									'joints':['hipA','kneeA','ankleA'],

									'defaultType':'IKFK_hinge',

									'defaultLength':[3,True],

									'defaultRoll':4,

									'defaultPss':1,

									'switchLoc':-1,

									'upVector':(0,1,0),

									'ikHandleOrient':'World'

									},
								'LegB':{'isIterator':False,

									'joints':['hipB','kneeB','ankleB'],

									'defaultType':'IKFK_hinge',

									'defaultLength':[3,True],

									'defaultRoll':4,

									'defaultPss':1,

									'switchLoc':-1,

									'upVector':(0,1,0),

									'ikHandleOrient':'World'

									},
								'LegC':{'isIterator':False,

									'joints':['hipC','kneeC','ankleC'],

									'defaultType':'IKFK_hinge',

									'defaultLength':[3,True],

									'defaultRoll':4,

									'defaultPss':1,

									'switchLoc':-1,

									'upVector':(0,1,0),

									'ikHandleOrient':'World'

									},






								
								'Spine':{'isIterator':'spine',

									'joints':['pelvis','spine'],

									'defaultType':'IKFK_spline',

									'defaultLength':[7,True],

									'defaultIkHandleName':['hip','chest'],

									'ikSpaces':[''],

									'defaultPss':1,

									'upVector':(0,1,0),

									'ikHandleOrient':['World','LastJoint']

									},

								'Neck':{'isIterator':'neck',

									'joints':['neck','head'],

									'defaultType':'IKFK_spline',

									'defaultLength':[4,True],

									'defaultIkHandleName':['neck','head'],

									'defaultPss':1,

									'upVector':(0,1,0),

									'ikHandleOrient':['LastJoint','LastJoint']

									},

								'Foot':{'isIterator':False,

									'joints':['ankle','heel','ball','toe'],

									'defaultType':'INV_foot',

									'defaultIkHandleName':['foot'],

									'defaultLength':[4,False],

									'switchLoc':0,

									'upVector':(0,1,0)
									},

								'Clavicle':{'isIterator':False,

									'joints':['clavicle','shoulder'],

									'defaultType':'IKFK_single',

									'defaultLength':[2,False],

									'defaultIkHandleName':['shoulder'],

									'defaultPss':1,
									'upVector':(0,1,0),

									'ikHandleOrient':'LastJoint'

									},


								'AxleFront':{'isIterator':False,

									'joints':['base','end'],

									'defaultType':'IKFK_single',

									'defaultLength':[2,False],

									'defaultIkHandleName':['frontWheel'],

									'defaultPss':1,
									'upVector':(0,1,0),

									'ikHandleOrient':'LastJoint'

									},


								'SpineSegmentA':{'isIterator':False,

									'joints':['base','end'],

									'defaultType':'IKFK_single',

									'defaultLength':[2,False],

									'defaultIkHandleName':['SpineSegmentA'],

									'defaultPss':1,
									'upVector':(0,1,0),

									'ikHandleOrient':'LastJoint'

									},


								'AxleRear':{'isIterator':False,

									'joints':['base','end'],

									'defaultType':'IKFK_single',

									'defaultLength':[2,False],

									'defaultIkHandleName':['rearWheel'],

									'defaultPss':1,
									'upVector':(0,1,0),

									'ikHandleOrient':'LastJoint'

									},

								'Jaw':{'isIterator':False,

									'joints':['start','end'],

									'defaultType':'IKFK_single',

									'defaultLength':[2,False],

									'defaultIkHandleName':['Jaw'],

									'defaultPss':1,
									'upVector':(0,1,0),

									'ikHandleOrient':'LastJoint'

									},

								'Femur':{'isIterator':False,

									'joints':['femur','hip'],

									'defaultType':'IKFK_single',

									'defaultLength':[2,False],

									'defaultIkHandleName':['hip'],

									'defaultPss':1,

									'upVector':(0,1,0),

									'ikHandleOrient':'LastJoint'

									},



								'Palm':{'isIterator':False,

									'joints':['wrist','palm'],

									'defaultType':'IKFK_single',

									'defaultLength':[2,False],

									'defaultIkHandleName':['palm']

									},


								'Metacarpal': {'isIterator':'phal_~',
									
									'joints':['meta_~','phal_~'],

									'proceduralName' : 'meta',

									'staticName' : 'Metacarpal',

									'defaultType':'IKFK_single',

									'defaultIkHandleName':['getFromName'],

									'upVector':(0,0,1),

									'ikHandleOrient':'LastJoint'

									},

								'Phalange': {'isIterator':'phal_~',

									'proceduralName' : 'phal',

									'staticName' : 'Phalange',
											
									'joints':['phal_~'],

									'defaultType':'IKFK_hinge',

									'defaultIkHandleName':['getFromName'],

									'defaultPss':1,

									'switchLoc':0,

									'upVector':(0,0,1),
									
									'defaultLength':[4,True],

									'ikHandleOrient':'LastJoint'

									},



								'PhalangeB': {'isIterator':False,

									'joints':['index_A','index_B','index_C','index_D'],

									'defaultType':'IKFK_doubleHinge',

									'defaultPss':1,

									'switchLoc':0,

									'upVector':(0,0,1),
									
									'defaultLength':[4,True],

									'ikHandleOrient':'LastJoint'

									},
									
								'Index': {'isIterator':False,

									'joints':['index_A','index_B','index_C','index_D'],

									'defaultType':'IKFK_doubleHinge',

									'defaultPss':1,

									'switchLoc':0,

									'upVector':(0,0,1),
									
									'defaultLength':[4,True],

									'ikHandleOrient':'LastJoint'

									},





								'Middle': {'isIterator':False,

									'joints':['middle_A','middle_B','middle_C','middle_D'],

									'defaultType':'IKFK_doubleHinge',

									'defaultPss':1,

									'switchLoc':0,

									'upVector':(0,0,1),
									
									'defaultLength':[4,True],

									'ikHandleOrient':'LastJoint'

									},

								'Ring': {'isIterator':False,

									'joints':['ring_A','ring_B','ring_C','ring_D'],

									'defaultType':'IKFK_doubleHinge',

									'defaultPss':1,

									'switchLoc':0,

									'upVector':(0,0,1),
									
									'defaultLength':[4,True],

									'ikHandleOrient':'LastJoint'

									},

								'Pinky': {'isIterator':False,

									'joints':['pinky_A','pinky_B','pinky_C','pinky_D'],

									'defaultType':'IKFK_doubleHinge',

									'defaultPss':1,

									'switchLoc':0,

									'upVector':(0,0,1),
									
									'defaultLength':[4,True],

									'ikHandleOrient':'LastJoint'

									},
								'Finger': {'isIterator':False,

									'joints':['finger_A','finger_B','finger_C','finger_D'],

									'defaultType':'IKFK_doubleHinge',

									'defaultPss':1,

									'switchLoc':0,

									'upVector':(0,0,1),
									
									'defaultLength':[4,True],

									'ikHandleOrient':'LastJoint'

									},










								'Thumb': {'isIterator':False,

									'joints':['thumb_A','thumb_B','thumb_C','thumb_D'],

									'defaultType':'IKFK_doubleHinge',

									'defaultPss':1,

									'switchLoc':0,

									'upVector':(0,0,1),
									
									'defaultLength':[4,True],

									'ikHandleOrient':'LastJoint'

									},									


								'Hand':{'isIterator':False,
										
									'joints':['wrist','palm'],

									'defaultType':'hand',

									'defaultLength':[2,False]},

								'Head':{'isIterator':False,
										
									'joints':['base','end'],

									'defaultType':'Static',

									'defaultLength':[2,False]},

								'Eye':{'isIterator':False,
										
									'joints':['base','end'],

									'defaultType':'Static',

									'defaultLength':[2,False]},
								
								'Prop':{'isIterator':False,
										
									'joints':['base','end'],

									'defaultType':'Static',

									'defaultLength':[2,False]},

								'frontWheel':{'isIterator':False,
										
									'joints':['base','end'],

									'defaultType':'Wheel',

									'defaultLength':[2,False]},

								'rearWheel':{'isIterator':False,
										
									'joints':['base','end'],

									'defaultType':'Wheel',

									'defaultLength':[2,False]},									


								'thumbSingle':{'isIterator':False,

									'joints':['thumb_A','thumb_B'],

									'defaultType':'IKFK_single',

									'defaultLength':[2,False],

									'defaultIkHandleName':['thumb'],

									'defaultPss':1,
									'upVector':(0,1,0),

									'ikHandleOrient':'LastJoint'},

								'indexSingle':{'isIterator':False,

									'joints':['index_A','index_B'],

									'defaultType':'IKFK_single',

									'defaultLength':[2,False],

									'defaultIkHandleName':['index'],

									'defaultPss':1,
									'upVector':(0,1,0),

									'ikHandleOrient':'LastJoint'},

								'middleSingle':{'isIterator':False,

									'joints':['middle_A','middle_B'],

									'defaultType':'IKFK_single',

									'defaultLength':[2,False],

									'defaultIkHandleName':['middle'],

									'defaultPss':1,
									'upVector':(0,1,0),

									'ikHandleOrient':'LastJoint'},								

								'ringSingle':{'isIterator':False,

									'joints':['ring_A','ring_B'],

									'defaultType':'IKFK_single',

									'defaultLength':[2,False],

									'defaultIkHandleName':['ring'],

									'defaultPss':1,
									'upVector':(0,1,0),

									'ikHandleOrient':'LastJoint'},	


								'pinkySingle':{'isIterator':False,

									'joints':['pinky_A','pinky_B'],

									'defaultType':'IKFK_single',

									'defaultLength':[2,False],

									'defaultIkHandleName':['pinky'],

									'defaultPss':1,
									'upVector':(0,1,0),

									'ikHandleOrient':'LastJoint'},



								}

	return returnVar

def buildShaders():	
	colors = {'red':[1,0,0],'blue':[0,0,1],'green':[0,1,0],'orange':[1,0.5,0],'teal':[0.5,0.75,0.75],'lightBlue':[0,0.5,1]}

	for color in colors.keys():
		if not m.objExists('template_'+color):
			#create a shader
			shader=m.shadingNode("lambert",asShader=True,n='template_'+color)
			# a shading group
			shading_group= m.sets(n='template_'+color+'_SG',renderable=True,noSurfaceShader=True,empty=True)
			#connect shader to sg surface shader
			m.connectAttr('%s.outColor' %shader ,'%s.surfaceShader' %shading_group)
			#set color
			m.setAttr(shader+'.color',colors[color][0],colors[color][1],colors[color][2],type='double3')

class rigObj():
	'''docstring for rigObj'''
	objDict = False

	
	def __init__(self, name,objType,**kwargs):
		'''Initialize object variables'''

		self.templateData = buildOptions()

		buildShaders()
		self.name = name
		self.type = objType
		self.mirrored = False
		self.runOnce = False
		self.shapes = []
		self.sides = ['']
		UIObj = kwargs['uiObj']
		if not rigObj.objDict:
			UIObj.objDict = []
			rigObj.objDict = True

		self.id = len(UIObj.objDict)
		self.connectedTo = False

		self.connectionJoint = False
		self.keepRoot = True
		self.connSurfaces = []
		self.primary = []
		self.defIkFollow = '' #temporary!!
		self.ikHandleOrient = ''#add ikHandleOrient attribute to build module!
		self.ikSwitchDefault = ''#add this too
		self.connectedToObj = False
		self.parentOffset = False		
		self.isDriver = False
		self.parentSpaceSwitch = []
		
		self.extraOuts = []
		self.keepEnd = False
		

		UIObj.objDict.append({})
		UIObj.objDict[self.id]['name'] = name
		UIObj.objDict[self.id]['obj'] = self

		if kwargs:	
			self.extraInfo = kwargs
		else:
			self.extraInfo = {}


	def root(self,*args):
		'''Create the root framework for each object.'''
		
		#build the microrig
		self.i = str(self.getIncrement(self.type+'_grp'))

		#an extra underscore is added at the end of the string to prevent confusion caused by name conflict- 
		#related incrementation in maya.
		self.group = self.type+'_grp_'+str(self.i)+'_'		
					
		#build the setup root objects
		meTools.Ctrl(name=self.group,shape='box',color='red',vis=True,lockType='%s')
		m.addAttr(ln='objectScale',at='double',min=0.01,max=2,dv=1,k=True)
		m.addAttr(ln='objectName',dt='string',k=True)
		m.setAttr(self.group+'.objectName',self.name,type='string')
		m.createNode('multiplyDivide',n=self.group+'_MD')
		m.connectAttr(self.group+'.objectScale',self.group+'_MD.input1X')
		m.setAttr(self.group+'_MD.input2X',0.4)

		self.upLoc = m.spaceLocator(n=self.type+'_upLoc_'+str(self.i)+'_')[0]

		m.setAttr(self.upLoc+'.ty',2)
		m.setAttr(self.upLoc+'.overrideEnabled',True)
		m.setAttr(self.upLoc+'.overrideDisplayType',2)
		m.parent(self.upLoc,self.type+'_grp_'+str(self.i)+'_')

	def build(self,UIObj,*args):
		'''Build the object.  Create root, base shapes and rig the display object.'''

		self.composite = False
		if self.runOnce: 
			print 'This object already has a rig.  If you want to build another rig, instantiate another rigObj.'
		
		else:

			if self.name not in self.templateData['buildComplex']:

				self.root()			
				
				self.baseShapes()
				
				self.rigSetup(UIObj)

				#setup object's mirroring and/or extraId configuration.
				self.sides = self.extraInfo['mirror']

				if len(self.extraInfo['mirror']) > 1:
					self.mirrorRig()
					self.mirrored = True

				m.select(self.group)

				self.runOnce = True
			else:

				
				self.buildComplex(UIObj)
			
	def buildComplex(self,UIObj,*args):
		'''Used for compound objects, like hands, bipeds, quadrupeds, etc..'''

		self.composite = True
		self.subRigs = {}
		self.root()
			
		self.baseShapes()			

		mirror = False	
	
		self.sides = self.extraInfo['mirror']

		if len(self.extraInfo['mirror']) > 1:
			self.mirrorRig()
			self.mirrored = True
	
		
		if self.type == 'hand':
			self.fingerData = {}
			fingers = ['thumb','index','middle','ring','pinky']

			if self.extraInfo:
				if 'fingers' in self.extraInfo:
					fingers = self.extraInfo['fingers']
			
			i=0
			for finger in fingers:

				#build and position metacarpals
				self.fingerData[finger] = {}

				self.fingerData[finger]['meta'] =  rigObj('Metacarpal','IKFK_single',procedural=finger,parent=self,mirror=self.extraInfo['mirror'], uiObj=UIObj)		
				self.fingerData[finger]['meta'].build(UIObj)
				self.fingerData[finger]['meta'].extraInfo['templateType'] = 'Metacarpal'

				zOffset = (float(i)/len(fingers))*len(fingers)-(len(fingers)*0.5)
				
				m.move(3,0,zOffset,self.fingerData[finger]['meta'].group)
				m.move(5,self.fingerData[finger]['meta'].shapes[1],x=True)
							
				connectRigs(True,UIObj,[self.shapes[1],self.fingerData[finger]['meta'].shapes[1]])

				if len(self.extraInfo['mirror'])== 2:
					self.fingerData[finger]['meta'].sides = self.extraInfo['mirror']
					
					self.fingerData[finger]['meta'].mirror = self.extraInfo['mirror']
					self.fingerData[finger]['meta'].mirrorRig(test=True,parent=self)

				#build and position phalanges
				self.fingerData[finger]['phal'] = rigObj('Phalange','IKFK_hinge',inBtwn=2,procedural=finger,parent=self,mirror=self.extraInfo['mirror'],uiObj=UIObj)
				self.fingerData[finger]['phal'].build(UIObj)
				self.extraInfo['templateType'] = 'Metacarpal'
				self.fingerData[finger]['phal'].extraInfo['templateType'] = 'Phalange'

				m.rotate(90,self.fingerData[finger]['phal'].group,x=True)
				
				connectRigs(False,UIObj,[self.fingerData[finger]['meta'].shapes[1],self.fingerData[finger]['phal'].shapes[1]])

				if len(self.extraInfo['mirror']) == 2:
				 	self.fingerData[finger]['phal'].sides = self.extraInfo['mirror']
				 	self.fingerData[finger]['phal'].mirrorRig(parent=self)


				i+=1


		self.runOnce = True


	def baseShapes(self,*args):
		'''Create the start and end shapes for objects.'''

		
		name = self.type+'_'+self.i+'_'

		if self.type == 'IKFK_hinge':
			self.component('sphere',color='red',name=name+'Start')
			self.component('sphere',color='red',pss=True,pos=[10,0,0],name=name+'End')

		if self.type == 'IKFK_spline':
			self.component('sphere',color='red',name=name+'Start')
			self.component('sphere',color='red',pss=True,pos=[10,0,0],name=name+'End')

		if self.type == 'IKFK_single':
			self.component('sphere',color='red',name=name+'Start')
			self.component('sphere',color='red',pss=True,pos=[10,0,0],name=name+'End')

		if self.type == 'INV_foot':
			self.component('sphere',color='red',name=name+'Start')
			self.component('sphere',color='red',pss=True,pos=[4,0,4],name=name+'End',lock='tx')
			

		if self.type == 'hand':
			self.component('sphere',color='red',name=name+'Start')
			self.component('sphere',color='red',pss=True,pos=[1,0,0],name=name+'End')

		if self.type == 'Static' or self.type == 'Wheel':
			self.component('sphere',color='red',name=name+'Start')
			self.component('sphere',color='red',pss=True,pos=[1,0,0],name=name+'End')

		if self.type == 'IKFK_doubleHinge':
			self.component('sphere',color='red',name=name+'Start')
			self.component('sphere',color='red',pss=True,pos=[1,0,0],name=name+'End')
		
		for shape in self.shapes:
			if '_Space' in shape:
				m.parent(shape+'_Space',self.group)
			else:
				m.parent(shape,self.group)

		m.parent(self.upLoc,name+'Start')

	def rigSetup(self,UIObj,*args):
		'''Rig the display object.  It won't necessarily behave like the rig it represents, 
		it should behave more like a template guide.'''

		connectSets = []
		name = self.type+'_'+self.i+'_'

		if 'IKFK' in self.type:

			if self.type == 'IKFK_hinge' or self.type == 'IKFK_doubleHinge':	

				if 'inBtwn' in self.extraInfo:
					btwn = self.extraInfo['inBtwn']
				else:
					btwn = 1

				
				for i in range(btwn):
					stri = str(i)
					
					#build inBetween spheres
					comp = self.component('sphere',color='orange',pos=[5,0,-2],ps=True,i=stri,lock='ty',ib=i+1)
					m.parent(name+stri+'__Space',name+'Start')

					#orient base to follow tip
					m.aimConstraint(name+'End',name+'Start',aimVector=[1,0,0],upVector=[0,0,-1],worldUpType='objectRotation',wu=[0,0,-1],wuo=self.group)
					
					#determine constraint weight blend for each position
					constrWeight = (i+1)/(btwn+1.0)
					constr = m.pointConstraint(name+'Start',name+stri+'__Space')
					m.setAttr(constr[0]+'.'+name+'StartW0',1-constrWeight)
					contrs = m.pointConstraint(name+'End',name+stri+'__Space')
					m.setAttr(constr[0]+'.'+name+'EndW1',constrWeight)

					#offset in between
					m.setAttr(name+stri+'_.tz',-5)

					#Add info to connectSets list
					if i == 0:
						connectSets.append([name+'Start',comp])
					
					if i == btwn-1:
						connectSets.append([comp,name+'End'])
					
					if i != btwn and i != 0:
						connectSets.append([previous,comp])

					previous = comp


			if self.type == 'IKFK_spline':

				totLen = self.extraInfo['inBtwn']+2
				defSeg = totLen/2
				m.addAttr(self.group,ln="fkSegments",at="long",min=1,max=5,dv=defSeg,k=True)

				if self.extraInfo:
					xIncr = 10.0/(self.extraInfo['inBtwn']+1)
					iIncr = xIncr

					for i in range(self.extraInfo['inBtwn']):
						comp = self.component('sphere',color='orange',parent=self.type+'_'+self.i+'_Start',ps=True,i=str(i),lock='ty',ib=i+1)

						constrWeight = (i+1)/(self.extraInfo['inBtwn']+1.0)
						constr = m.pointConstraint(name+'Start',comp+'_Space')
						m.setAttr(constr[0]+'.'+name+'StartW0',1-constrWeight)
						constr = m.pointConstraint(name+'End',comp+'_Space')
						m.setAttr(constr[0]+'.'+name+'EndW1',constrWeight)
						

						if i == 0:
							connectSets.append([name+'Start',comp])
						if i == self.extraInfo['inBtwn']-1:
							connectSets.append([comp,name+'End'])
						if 0 < i < self.extraInfo['inBtwn']:
							connectSets.append([previous,comp])
						previous = comp

						iIncr += xIncr
				
				m.aimConstraint(name+'End',name+'Start',aimVector=[1,0,0],upVector=[0,0,-1],worldUpType='objectRotation',wu=[0,0,-1],wuo=self.group)

			if self.type == 'IKFK_single':
				connectSets.append([name+'Start',name+'End'])

		elif self.type == 'INV_foot':
			compA = self.component('sphere',color='orange',parent=self.type+'_'+self.i+'_Start',pos=[4,0,-2],i=0,lock='ty',ib=1)
			compB = self.component('sphere',color='orange',parent=self.type+'_'+self.i+'_Start',pos=[4,0,1],i=1,lock='ty',ib=2)

			connectSets = ([name+'Start',compA],[compA,compB],[compB,name+'End'])

		else:
			connectSets.append(self.shapes)
		
		self.connectComponents(self,connectSets,uiObj=UIObj)

		# if self.type == 'INV_foot':
		# 	m.setAttr(self.group+'.rz',-90)

	@staticmethod
	def connectComponents(self,targetSets,*args,**kwargs):
		'''Connect components together.  This can be done as either an object method or straight function.'''
		UIObj = kwargs['uiObj']
		connectionVisObjects = []
		for ts in targetSets:
			startPos = m.xform(ts[0],q=True,t=True,ws=True)
			endPos = m.xform(ts[1],q=True,t=True,ws=True)
			curve = ts[0]+'_'+ts[1]+'_connCurve'
			m.curve(d=1,p=[startPos,endPos],k=[0,1],n=curve)
			m.select(ts[0])
			m.joint(n=ts[0]+'_'+ts[1]+'_startJnt')
			m.select(ts[1])
			m.joint(n=ts[0]+'_'+ts[1]+'_endJnt')
			cluster = m.skinCluster(ts[0]+'_'+ts[1]+'_startJnt',ts[0]+'_'+ts[1]+'_endJnt',curve,tsb=True)[0]
			
			circle = m.circle(n=ts[0]+'_'+ts[1]+'_cc_profile',r=0.25)		

			
			
			if self == '':
				srcObj = getFromItem(ts[0],UIObj,type='obj')
				m.connectAttr(srcObj.group+'_MD.outputX',circle[1]+'.radius')
			else:
				m.connectAttr(self.group+'_MD.outputX',circle[1]+'.radius')
			circle = circle[0]
			
			m.aimConstraint(ts[1],ts[0]+'_'+ts[1]+'_cc_profile',aimVector=[0,0,-1],upVector=[0,0,-1],worldUpType='objectRotation',wu=[0,0,-1],wuo=ts[0])
			
			m.parent(ts[0]+'_'+ts[1]+'_cc_profile',ts[0],r=True)

			m.hide(ts[0]+'_'+ts[1]+'_startJnt',ts[0]+'_'+ts[1]+'_endJnt',circle,curve)

			m.setAttr(curve+'.inheritsTransform',0)
			
			surf = m.extrude (ts[0]+'_'+ts[1]+'_cc_profile', curve,n=ts[0]+'_'+ts[1]+'_EXTR',et=2,ucp=0)[0]			
			
			connectionVisObjects = [surf,cluster,circle[1],ts[0]+'_'+ts[1]+'_endJnt',ts[0]+'_'+ts[1]+'_startJnt',curve]
			
			m.setAttr(surf+'.inheritsTransform',0)
			m.setAttr(surf+'.overrideEnabled',1)
			m.setAttr(surf+'.overrideDisplayType',2)
			
			if self == '':
				m.sets(surf, e=True, forceElement='template_lightBlue_SG')
			else:
				m.sets(surf, e=True, forceElement='template_blue_SG')

			if self != '':
				group = self.group
				self.connSurfaces.append(surf)
			else:
				group = ts[1]

			
			m.parent(curve,surf,group)			
			m.setAttr(surf+'.t',0,0,0)
			m.setAttr(surf+'.r',0,0,0)
			m.select(cl=True)
			



		#add roll joint indicators if required:		
		k = 1
		if self != '':
			previous = ''
			if self.extraInfo:
				if 'roll' in self.extraInfo:
					for i in range(len(targetSets)):						
						for j in range(self.extraInfo['roll']):							
							comp = self.component('disc',color='orange',parent=targetSets[i][0],i=i,iSub=j,lock='all',ib=k,secondary=True)
							if j == 0:
								m.aimConstraint(targetSets[i][1],comp,aimVector=[1,0,0],upVector=[0,0,-1],worldUpType='objectRotation',wu=[0,0,-1],wuo=targetSets[i][0])
							else:
								m.connectAttr(previous+'.r',comp+'.r')
							previous = comp

							#determine constraint weight blend for each position
							constrWeight = (j+1)/(self.extraInfo['roll']+1.0)
							constr = m.pointConstraint(targetSets[i][0],comp)
							m.setAttr(constr[0]+'.'+targetSets[i][0]+'W0',1-constrWeight)
							contrs = m.pointConstraint(targetSets[i][1],comp)
							m.setAttr(constr[0]+'.'+targetSets[i][1]+'W1',constrWeight)
							k+=1
						k+=1

		
		return connectionVisObjects
		
	
	def mirrorRig(self,**kwargs):
		'''Make a mirrored representation of template objects.'''

		if not kwargs:
			kwargs = []
		
		if 'parent' in kwargs:
			mirrorGroup = kwargs['parent'].group+'mirror'

		else:
			if not m.objExists(self.group+'mirror'):
				mirrorGroup = m.group(em=True,n=self.group+'mirror')
				m.parent(mirrorGroup,self.group)
				m.setAttr(mirrorGroup+'.sx',-1)
				m.setAttr(mirrorGroup+'.inheritsTransform',0)				
			else:
				mirrorGroup = self.group+'mirror'
		
		if 'connection' in kwargs:
			allShapes = [kwargs['connection']]
		else:
			allShapes = self.shapes + self.connSurfaces
		for shape in allShapes:	
			type = m.nodeType(shape+'Shape')
			if not m.objExists(shape+'_mirrorShape'):
				m.createNode(type,n=shape+'_mirrorShape')
				m.rename(m.listRelatives(shape+'_mirrorShape',p=True)[0],shape+'_mirror')
				m.parent(shape+'_mirror',mirrorGroup)
				m.createNode('decomposeMatrix',n= shape+'_mirror_DCM')
				m.connectAttr(shape+'.worldMatrix[0]',shape+'_mirror_DCM.inputMatrix')
				m.connectAttr(shape+'_mirror_DCM.outputTranslate',shape+'_mirror.t')
				m.connectAttr(shape+'_mirror_DCM.outputRotate',shape+'_mirror.r')
				m.connectAttr(shape+'_mirror_DCM.outputScale',shape+'_mirror.s')

				if type == 'nurbsSurface':
					m.connectAttr(shape+'Shape.worldSpace[0]',shape+'_mirrorShape.create')
				if type == 'mesh':
					m.connectAttr(shape+'Shape.outMesh',shape+'_mirrorShape.inMesh')

				shader = m.listConnections(shape+'Shape',type='shadingEngine')[0].replace('_SG','')
				m.select(shape+'_mirror')
				
				m.sets(e=True,forceElement=shader+'_SG')
		


	def component(self,comp,**kwargs):
		#kwargs include:
		#
		# - position -> pos=
		# - scale
		# - color
		# - parent -> parent=
		# - parentSpace -> ps= 
		# - iterator -> i=
		# - lock -> lock=
		# - parentSpaceSwitch -> pss = 


		if 'i' in kwargs:
			name = self.type+'_'+self.i+'_'+str(kwargs['i'])+'_'
			if 'iSub' in kwargs:
				name = self.type+'_'+self.i+'_'+comp+'_'+str(kwargs['i'])+'_'+str(kwargs['iSub'])+'_'
		else:		
			name = self.type+'_'+comp+'_'+self.i+'_'

		if 'name' in kwargs:
			name = kwargs['name']

		if comp == 'disc':
			comp = m.polyCylinder(n=name,ax=[1,0,0],h=0.3)

		if comp == 'sphere':
			comp = m.sphere(n=name)

		if comp == 'footprint':
			comp = m.polyCube(name=name,d=5,h=0.2,sz=4)
			m.scale(2,1,1,name+'.vtx[4:5]',name+'.vtx[18:19]')
			m.scale(1.5,1,1,name+'.vtx[8:9]',name+'.vtx[14:15]')
			m.move (-.5, name+'.vtx[6:9]',name+'.vtx[14:17]',z=True,r=True)

		if comp[1]:
			m.connectAttr(self.group+'.objectScale',comp[1]+'.radius')

		if 'pos' in kwargs:
			p = kwargs['pos']
			m.setAttr(comp[0]+'.t',p[0],p[1],p[2])

		if 'parent' in kwargs:
			m.parent(comp[0],kwargs['parent'])

		if 'ps' in kwargs:
			if 'ps':
				meTools.meParent(comp[0])

		if 'lock' in kwargs:
			if kwargs['lock'] == 'all':
				attrs = m.listAttr(comp[0],l=True)
				if attrs:
					for ea in attrs:					
							m.setAttr(comp[0]+'.'+ea,l=True)
			else:
				m.setAttr(comp[0]+'.'+kwargs['lock'],l=True)

		if 'color' in kwargs:
			colorTgt = comp[0]
			m.sets(e=True,forceElement='template_'+kwargs['color']+'_SG')


		if 'ib' in kwargs:
			self.shapes.insert(kwargs['ib'],comp[0])
		else:
			self.shapes.append(comp[0])

		if 'secondary' not in kwargs:
			self.primary.append(comp[0])

		if 'pss' in kwargs:
			if kwargs['pss']:
				m.addAttr(name,ln='parentSpaceSwitch',dt='string')
				m.setAttr(name+'.parentSpaceSwitch',k=True)
				m.setAttr(name+'.parentSpaceSwitch','WorldOffset,RigRoot',type='string')

		return comp[0]

	def getIncrement(self,target,*args):
		allObjects = m.ls(typ='transform')
		i = 0
		for obj in allObjects:
			if target in obj:
					if '_Space' not in obj:
						i += 1

		return i
	
def connectRigs(mo,UIObj,*args):
	if args:
		sel= args[0]
	else:
		sel = m.ls(sl=True)

	#get the source object from the source selection and assign it to drv.  
	#set drv.keepEnd to true or false depending on offset toggle.
	drv = getFromItem(sel[0],UIObj,type='obj')
	if type(mo) == type(''):
		result = m.confirmDialog( title='Connect Rigs', message='Maintain Offset?', button=['Yes','No','Cancel'], defaultButton='Yes', cancelButton='Cancel', dismissString='No' )
		if result:
			if result == 'Yes':
				mo = True
				drv.keepEnd = True

			else: 
				mo = False
				drv.keepEnd = False
				
			sel = m.ls(sl=True)

	try:
		tgtTopNode = m.listRelatives(sel[1],c=False,p=True,f=True)[0].split('|')[1]
	except:
		tgtTopNode = sel[1]
	

	#snap the object in place if necessary.  
	#give the target a parentSpace and constrain that to the selection.
	#set the override color to reflect its connected state.
	m.delete(m.pointConstraint(sel[0],tgtTopNode,mo=mo))
	meTools.meParent(tgtTopNode)
	m.parentConstraint(sel[0],tgtTopNode+'_Space',mo=True)	
	m.setAttr(tgtTopNode+'Shape.overrideColor',20)

	topShape = tgtTopNode.replace('_grp','')+'Start'


	#get object from target selection and assign it to self.
	#assign source selection to self.connectedTo
	#assign offset toggle value to self.parentOffset	
	#assign the source object to self.connectedToObj
	#assign the source object's .isDriver attribute to True
	#add the source selection to the source object's .extraOuts list attribute

	self = getFromItem(sel[1],UIObj,type='obj')
	self.connectedTo = sel[0]
	self.parentOffset = mo	

	self.connectedToObj = drv
	drv.isDriver = True	
	drv.extraOuts.append(sel[0])

	#if offset is True, use .connectComponents to draw a link between components:
		#make a curve, a start and end joint, skin that curve and extrude a tube
	#if offset is False, parent the shape of the target selection under the source selection
		#connect the objScale attribute from the source to the target.
		#hide the selection's Shape node
		#set the current objket's .keepRoot attribute to False

	if mo:
		connectionVisObjects = rigObj.connectComponents('',[[sel[0],topShape]],uiObj=UIObj)[0]
		surf = connectionVisObjects
		if len(self.extraInfo['mirror']) ==2:
			self.mirrorRig(connection=surf)
		self.connectionVisObjects = connectionVisObjects

	else:
		m.parent(tgtTopNode+'Shape',sel[0],r=True,s=True)
		if not m.objExists(sel[0]+'.objectScale'):
			m.addAttr(sel[0],ln='objectScale',at='double',min=0,max=2,dv=1,k=True)

		m.connectAttr(sel[0]+'.objectScale',tgtTopNode+'.objectScale')
		
		m.hide(topShape+'Shape')
		self.keepRoot = False

def disconnectRigs(mo,UIObj,*args):
	tgtSel = m.ls(sl=True)[0]
	tgt = getFromItem(tgtSel.replace('_grp_0_','_0_Start'),UIObj,type='obj')
	drv = tgt.connectedToObj
	drvSel = m.parentConstraint(tgtSel+'_Space',q=True,tl=True)[0]

	#get the source object from the source selection and assign it to drv.  
	#set drv.keepEnd to true or false depending on offset toggle.
	drv.keepEnd = True

	#snap the object in place if necessary.  
	#give the target a parentSpace and constrain that to the selection.
	#set the override color to reflect its connected state.
	m.parent(tgtSel,w=True)
	m.setAttr(tgtSel+'Shape.overrideColor',13)
	m.delete(tgtSel+'_Space')

	#get object from target selection and assign it to self.
	#assign source selection to self.connectedTo
	#assign offset toggle value to self.parentOffset	
	#assign the source object to self.connectedToObj
	#assign the source object's .isDriver attribute to True
	#add the source selection to the source object's .extraOuts list attribute
	tgt.connectedTo = False
	tgt.connectedToObj = False
	drv.isDriver = False
	drv.extraOuts.remove(drvSel)


	#if offset is True, use .connectComponents to draw a link between components:
		#make a curve, a start and end joint, skin that curve and extrude a tube
	
	m.delete(tgt.connectionVisObjects)

	#if offset is False, parent the shape of the target selection under the source selection
		#connect the objScale attribute from the source to the target.
		#hide the selection's Shape node
		#set the current objket's .keepRoot attribute to False	


def getFromItem(item,UIObj,**kwargs):
	returnObj = None

	if 'type' in kwargs:		
		for i in range(len(UIObj.objDict)):
			obj = UIObj.objDict[i]['obj']


			for shape in obj.shapes:


				if item == shape:
					returnObj = obj


			if kwargs['type'] == 'joint':
				joints = convertToJoint(obj,build=False)
				if item in obj.shapes:
					index = obj.shapes.index(item)
					returnObj = joints[index]

	return returnObj
	


def orderByConnection(UIObj,*args,**kwargs):
	newDict = []
	newDictNames = []
	for rig in UIObj.objDict:
		if not rig['obj'].connectedTo:
			newDict.append(rig)
			newDictNames.append(rig['obj'].name)
	i = 0
	#for j in range(20):
	while len(newDict) != len(UIObj.objDict):
		for rig in UIObj.objDict:
			if rig['obj'].connectedTo:
				if rig not in newDict:
					testObject = getFromItem(rig['obj'].connectedTo,UIObj,type='obj')
					if testObject.name in newDictNames:
						newDict.append(rig)
						newDictNames.append(rig['obj'].name)
						print rig['obj'].name+' is sorted'
						i+=1

	print newDict						
	# for ea in UIObj.objDict:
	# 	print ea['obj'].name,'--->',ea['obj'].connectedTo
	# for ea in newDict:
	# 	print ea['obj'].name

	# print UIObj.objDict
	# print newDict
	UIObj.objDict = newDict

def convertToSkel(UIObj,*args,**kwargs):
	
	parentDeferred = []
	data = buildOptions()
	jointSets = data['template']
	orderByConnection(UIObj)
	#list all the base nodes, find the 'root' node, which has no incoming connections.  If there is more than one node without
	#incoming connections, error out.
	cleanup = []
	
	for ro in range(len(UIObj.objDict)):
		
		obj = UIObj.objDict[ro]['obj']	
		name = UIObj.objDict[ro]['name']
		
		#if not obj.composite:
		joints = []		
		origJoints = []
		prev = ''

		#gather custom info from group node
		if m.objExists(obj.group+'.fkSegments'):
			obj.fkSegments = m.getAttr(obj.group+'.fkSegments')
		
		obj.joints = convertToJoint(obj,build=True)		

		if 'mirror' not in obj.extraInfo:
			sides = ['']
		elif not obj.extraInfo['mirror']:
			sides = ['']
		else:
			sides = obj.extraInfo['mirror']
		
		if 'parent' in obj.extraInfo:
			if obj.extraInfo['parent']:
				sides = obj.extraInfo['parent'].sides

		for id in sides:
			test = False
			aimFlip = 1
			if len(sides) > 1:
				if id == sides[1]:

					obj.joints = meTools.listSubstitute(obj.joints,sides)

					aimFlip = -1
					m.parent(obj.upLoc,obj.shapes[0]+'_mirror',r=True)
					m.move(-10,obj.upLoc,y=True,os=True,r=True)

			for i in range(len(obj.joints)):
				flip = 1

				if m.getAttr(obj.shapes[i]+'.tz') > 0:
					flip = -1
					



				#algin joints.
				if 0 < i < (len(obj.joints)-1):					
					
					m.delete(m.aimConstraint(obj.joints[i+1],obj.joints[i],aimVector=(1*aimFlip,0,0),upVector=(0,1,0),worldUpType='objectRotation',wuo=prevJoint))

					
					m.parent(obj.joints[i],prevJoint)
					
				else:					
					if i==0:
						if len(obj.joints) > 1:
							m.delete(m.aimConstraint(obj.joints[i+1],obj.joints[i],aimVector=(1*aimFlip,0,0),upVector=(0,1,0),worldUpType='object',wuo=obj.upLoc))

					else:						
						m.parent(obj.joints[-1],prevJoint)
						m.setAttr(obj.joints[-1]+'.jo',0,0,0)
			
				
				

				upVector = [0,1,0]
				if 'upVector' in jointSets[name].keys():				
					upVector = jointSets[name]['upVector']
				
				if upVector == (0,0,1):
					if i == 0:
						m.rotate(-90,obj.joints[i],x=True,r=True,os=True)


				m.makeIdentity(obj.joints[i],a=True,r=True,t=False,s=False,n=False)

				prevJoint = obj.joints[i]	


			if obj.connectedTo:			
				mirr = False
				#if 'mirror' in the connection name, then make sure the connJnt variable is corrected before getting parented to
				if '_mirror' in obj.connectedTo:
					mirr =True

				srcObj = getFromItem(obj.connectedTo.replace('_mirror',''),UIObj,type='obj')
				shapeIndex = srcObj.shapes.index(obj.connectedTo.replace('_mirror',''))

				if obj.keepRoot == False:
					topJoint = 1

				else:
					topJoint = 0

				#getFromItem returns the joint for a given shape, if the connection was originally to a mirror, replace the side
				#id with the mirrored side

				connJnt = getFromItem(obj.connectedTo,UIObj,type='joint')
				obj.connectionJoint = connJnt
				if mirr:
					connJnt = srcObj.joints[shapeIndex].replace(srcObj.sides[0],srcObj.sides[1])
				if len(sides) >1 and len(srcObj.sides) > 1:
					if id == sides[1]:
						if mirr:
							connJnt = srcObj.joints[shapeIndex].replace(srcObj.sides[1],srcObj.sides[0])
						else:
							connJnt = srcObj.joints[shapeIndex].replace(srcObj.sides[0],srcObj.sides[1])

				prevParent = False
				if m.listRelatives(obj.joints[topJoint],p=True,c=False):

					prevParent = m.listRelatives(obj.joints[topJoint],p=True,c=False)[0]


				parentDeferred.append([obj.joints[topJoint],connJnt,prevParent])
				obj.connectedToJoint = srcObj
				

			if len(sides) > 1:
				if id == sides[1]:
					
					obj.joints = meTools.listSubstitute(obj.joints,(sides[0],sides[1]))
					cleanup.append(obj.upLoc)

			cleanup.append(obj.group)
			cleanup.append(obj.group+'_Space')

		#get pv vector:
		for j in obj.joints:	
			jo = m.getAttr(j+'.jointOrientY')
			if jo > 0: obj.pv = 1
			if jo < 0: obj.pv = -1

	for clean in cleanup:
		if m.objExists(clean):
			m.delete(clean)

	for pd in parentDeferred:
			if m.objExists(pd[1]+'_deleteMe'):
				m.delete(m.parentConstraint(pd[1]+'_deleteMe',pd[1]))

	for pd in parentDeferred:
		#get t,r,s,jo
		if pd[2]:			
			connParent = m.listRelatives(pd[1],p=True,c=False)[0]
			m.parent(pd[2],connParent)
			t= m.getAttr(pd[2]+'.t')[0]
			r= m.getAttr(pd[2]+'.r')[0]
			s= m.getAttr(pd[2]+'.s')[0]
			jo = m.getAttr(pd[2]+'.jo')[0]



			m.setAttr(pd[1]+'.t',t[0],t[1],t[2])
			m.setAttr(pd[1]+'.r',r[0],r[1],r[2])
			m.setAttr(pd[1]+'.s',s[0],s[1],s[2])
			m.setAttr(pd[1]+'.jo',jo[0],jo[1],jo[2])
		


		m.parent(pd[0],pd[1])

	for joint in m.ls(typ='joint'):
		if '_deleteMe' in joint:
			m.delete(joint)
			#if joint in obj.joints:
			
			#freeze rotations
			
			#m.makeIdentity(joint.replace('_deleteMe',''),r=True,t=False,s=False,n=False,apply=True)


	obj.jointCore = meTools.listSubstitute(obj.joints,['base_',''])

def convertToJoint(obj,**kwargs):

	#iterate through joints in the set.  This is a mess right now because both incremental and non-incremental setups are being 
	#accounted for.  TO DO: organize this section for better readability.

	data = buildOptions()
	jointSets = data['template']
	obj.colors = data['ctrlColors']
	#if 'defaultIkHandleName' in jointSets[obj.name]:
	#obj.ikHandleName = jointSets[obj.name]['defaultIkHandleName'][0]

	#if the number of joints in the specified joint set doesn't match the number of primary (sphere shape) joints in the jointSet
	#index, error out.
	name = obj.name
	primaries = obj.shapes
	joints = []		
	obj.jointRoots = []
	obj.jointBase = []
	obj.subName = 'nothing'
	
	id =''
	if 'id' in obj.extraInfo:
		id = obj.extraInfo['id']

	if not jointSets[name]['isIterator']:
		if jointSets[name]['isIterator'] != 'Complex':
			if len(obj.primary) != len(jointSets[name]['joints']):
				m.error('Incorrect number of joints for specified rig name')

	if 'mirror' not in obj.extraInfo:
		sides = ['']
	elif not obj.extraInfo['mirror']:
		sides = ['']

	else:
		sides = obj.extraInfo['mirror']
	
	if 'parent' in obj.extraInfo:
		if obj.extraInfo['parent']:
			sides = obj.extraInfo['parent'].sides


	mirror = ''
	for id in sides:
		i = 0
		k = 0
		j = 0
		pr = 0
		l= 0
		j = 0		
		
		if len(sides) > 1:
			if id == sides[1]: 
				mirror = '_mirror'
		for ea in obj.shapes:
			m.select(cl=True)
			p = m.xform(ea+mirror,q=True,t=True,ws=True)
			
			
			if ea in obj.primary:
				currentJoint = 'base_'+name+'_'+jointSets[name]['joints'][k]+id				
				
				if jointSets[name]['isIterator']:				
					if len(ea.split('_') ) == 5 or jointSets[name]['isIterator'] in jointSets[name]['joints'][l]:
						currentJoint = 'base_'+name+'_'+jointSets[name]['joints'][k-1]+'_'+str(j)+id
						if 'procedural' in obj.extraInfo:
							obj.subName = obj.extraInfo['procedural']
						j+=1
					else:
						l+=1
				else:
					k += 1
					j = 0

				pr +=1

			else:
				if 'disc' in ea:
					rollNum = ea.split('_')[-2]
					currentJoint = 'base_'+name+'_'+jointSets[name]['joints'][k-1]+'_Roll_'+str(j)+id
				
				j+=1

			if '_~' in currentJoint:
				currentJoint = currentJoint.replace('~',obj.extraInfo['procedural'])
				


			if ea ==  obj.shapes[0] and not obj.keepRoot:
				#print 'deleteMe '+currentJoint
				currentJoint += '_deleteMe'
				

			if kwargs['build']:
				m.joint(n=currentJoint)
				m.addAttr(currentJoint,ln='src',dt='string')
				m.setAttr(currentJoint+'.src',ea,type='string')

				m.xform(currentJoint,t=(p[0],p[1],p[2]),ws=True,a=True)
				if m.objExists(ea+mirror+'.parentSpaceSwitch'):
					for pss in m.getAttr(ea+mirror+'.parentSpaceSwitch').split(','):
						obj.parentSpaceSwitch.append(pss)


				

			if id == sides[0]:				
				joints.append(currentJoint)		
				obj.jointRoots.append(currentJoint.replace('base_',''))
				if 'Roll' not in currentJoint:
					obj.jointBase.append(currentJoint.replace('base_',''))
			prevJoint = currentJoint
			i+=1

	return joints

	
def exportTemplate():
	pass

