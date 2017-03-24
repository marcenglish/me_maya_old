import maya.cmds as m
import Anim.Widgets
dir(Anim.Widgets)

#places a locator at the selected object's bounding box centre
def meBB():
	sel = m.ls(sl=True)	
	componentMode = False
	for ea in sel:
		if '.' not in ea:
			bb = m.exactWorldBoundingBox(ea)
			px = (bb[0]+bb[3])*0.5
			py = (bb[1]+bb[4])*0.5
			pz = (bb[2]+bb[5])*0.5
			m.spaceLocator(n=ea+'_LOC')
			m.setAttr(ea+'_LOC.t',px,py,pz)
		else:
			componentMode = True
	
	if componentMode:	
		bb = m.exactWorldBoundingBox(sel)
		px = (bb[0]+bb[3])*0.5
		py = (bb[1]+bb[4])*0.5
		pz = (bb[2]+bb[5])*0.5
		loc = m.spaceLocator(n=sel[0].split('.')[0]+'_components_LOC')[0]
		m.setAttr(loc+'.t',px,py,pz)

def alphaIncrement(staticName='',staticSuffix=''):
	alpha = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']	
	sel = m.ls(sl=True)
	div = len(sel)/26


	for i, ea in enumerate(sel):
		suffix = ''
		currDiv = i/26
		if i > 25:
			for cd in range(currDiv):
				suffix += 'A'

		if i-(26*currDiv) < 26:
			suffix += alpha[i-(26*currDiv)]
		print suffix
		print i-(26*currDiv)

		if staticName:
			m.rename(ea,staticName+'_'+suffix+'_'+staticSuffix)
		else:
			m.rename(ea,ea+'_'+suffix+'_'+staticSuffix)



def swap(items):
	sel = m.ls(sl=True)
	m.select(cl=True)
	for ea in sel:
		m.select(ea.replace(items[0],items[1]),add=True)


def meFindDupes():
	scene = m.ls()
	testGroup = scene
	alreadyCounted = []
	print '--Duplicate names test: START--'
	for ea in scene:
		ea = ea.split('|')[-1]
		if ea in alreadyCounted:
			print ea+' is a duplicate.'	
		else:
			alreadyCounted.append(ea)
	print '--Duplicate names test: END--'


def meSwapSel():
	sel = m.ls(sl=True)
	for ea in sel:
	    shape = m.listRelatives(ea,s=True)[0]
	    verts = m.getAttr(shape+'.spans')+3
	    m.select(cl=True)
	    for i in range(verts):
	        print ea+'.cv['+str(i)+']'        
	        try:
	            m.select(ea+'.cv['+str(i)+']',add=True)
	        except:
	            pass

def mirrorAny():
	sel = m.ls(sl=True)[0]
	objType = m.nodeType(sel)
	swapIds = ['_L','_R']
	if objType == 'transform':
		objType = m.nodeType(m.listRelatives(sel,s=True)[0])
		if objType == 'nurbsCurve':
			meSwapSel()
			newSel = m.ls(sl=True)
			for ea in m.filterExpand( ex=True, sm=28 ):
				t = []
				t = m.xform(ea,q=True, t=True,ws=True)
				m.xform(ea.replace(swapIds[0],swapIds[1]),ws=True,t=[t[0]*-1,t[1],t[2]])
		else:
			print 'nope'
			print objType
	else:
		print 'nope'

def snap():
	sel = m.ls(sl=True)
	m.delete(m.parentConstraint(sel[0],sel[1],mo=False))

def testAnim():
	sel = m.ls(sl=True)

	animDict = Anim.Widgets.animDict([sel[0]])
	
	for k in animDict.keys():
		if 'ALL_' not in k:
			srcCtrl = k

	origRange = animDict['ALL_maxFrame'] - animDict['ALL_minFrame']
	animRange = origRange

	for ea in animDict[srcCtrl]:	
		print ea+'-'

	for i in range (len(sel)):		
		if i != 0:
			print sel[i]
			print 'offset is '+str(animRange)
			for attr in animDict[srcCtrl]['attrs']:
				f = 0
				for frame in animDict[srcCtrl]['attrs'][attr]['frames']:
					value = animDict[srcCtrl]['attrs'][attr]['values'][f]
					m.setKeyframe(sel[i], at=attr, time=(frame+animRange-1,frame+animRange-1),v=value)
					f+=1
			animRange += origRange-1

def DirectConnect(mode,**kwargs):
	src, tgt = '',''
	sel = m.ls(sl=True)
	if kwargs:
		src = kwargs['src']
		sel = kwargs['tgt']
	else:
		src = sel.pop(0)
	
	for s in sel:
		if mode == 'mesh':
			outAttr = ''
			if m.objExists(src+'.outMesh'):
				outAttr = src+'.outMesh'
			if m.objExists(src+'.outputGeometry'):
				outAttr = src+'.outMesh'
			
			m.connectAttr(src+outAttr,s+'.inMesh')
		
		elif mode == 'r':			
			m.connectAttr(src+'.rx',s+'.rx')
			m.connectAttr(src+'.ry',s+'.ry')
			m.connectAttr(src+'.rz',s+'.rz')
	
		else:
			m.connectAttr(src+'.'+mode,s+'.'+mode)


def quickStretchSpline(curve=''):
	print "quickStretchSpline"

	#select all joints
	result = m.promptDialog(
	                title='QuickStretchSpline',
	                message='Enter Name:',
	                button=['OK', 'Cancel'],
	                defaultButton='OK',
	                cancelButton='Cancel',
	                dismissString='Cancel')

	if result == 'OK':
		text = m.promptDialog(query=True, text=True)
		sel = m.ls(sl=True)

		start = m.xform(sel[0],q=True,t=True,ws=True)
		end = m.xform(sel[-1],q=True,t=True,ws=True)
		mid = []

		for i in range(len(start)):
		    mid.append(((end[i]-start[i])*0.5)+start[i])

		if curve == '':
			curve = m.curve(n=text+'Spline_crv',d=2,p=[start,mid,end])

		m.rename(m.listRelatives(curve,s=True)[0],text+'Spline_crvShape')

		shape = m.listRelatives(curve,s=True)[0]

		#setup curve length reader
		arcLen = m.createNode('arcLengthDimension',n=curve+'_arcLen')
		m.connectAttr(curve+'Shape.worldSpace[0]',arcLen+'.nurbsGeometry')
		m.setAttr(arcLen+".uParamValue", 1)

		#setup ratio node
		md = m.createNode('multiplyDivide',n=arcLen+'_ratio_MD')
		m.connectAttr(arcLen+'.arcLength',md+'.input1X')	
		m.setAttr(md+'.input2X',m.getAttr(arcLen+'.arcLength'))
		m.setAttr(md+'.operation',2)

		#setup spline
		splineStuff = m.ikHandle(sj=sel[0], ee=sel[-1], sol='ikSplineSolver', n=text+'_Spline', p=2, w=.5,scv=False,ccv=False,c=curve)    


		#connect to scale
		for ea in sel[:-1]:
			m.connectAttr(md+'.outputX',ea+'.sx')

def resetControllers():
	print 'resetControllers'
	sel = m.ls(typ='nurbsCurve')
	swapIds = ['_L','_R']	
	print sel
	print '--'
	for ea in sel:

		ctrl = m.listRelatives(ea,p=True)[0]
		if m.objExists(ctrl+'.ctrl'):			
			print ctrl
			try:
				m.setAttr(ctrl+'.t',0,0,0)
			except:
				print 'could not set translate'

			try:
				m.setAttr(ctrl+'.r',0,0,0)
			except:
				print 'could not set rotate'

			try:
				m.setAttr(ctrl+'.s',1,1,1)
			except:
				print 'could not set scale'				


			m.select(ctrl)
			m.setKeyframe()






print 'meWidgets loaded'

