import maya.cmds as m

#places a locator at the selected object's bounding box centre
def meBB():
	sel = m.ls(sl=True)	
	componentMode = False
	for ea in sel:
		if '.' not in sel:
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
		m.spaceLocator(n=sel[0].split('.')[0]+'_components_LOC')
		m.setAttr(sel[0].split('.')[0]+'_components_LOC.t',[px,py,pz])


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


print 'meWidgets loaded'