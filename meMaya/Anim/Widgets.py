import maya.cmds as m

def animDict(ctrls=False):	
	if not ctrls:
		ctrls = m.ls(sl=True)

	animDict = {}
	animDict['ALL_minFrame'] = 0
	animDict['ALL_maxFrame'] = 0
	animDict['ALL_minValue'] = 0
	animDict['ALL_maxValue'] = 0
	

	for ctrl in ctrls:		
		animDict[ctrl] = {}
		animDict[ctrl]['attrs'] = {}
		for attr in m.listAttr(ctrl,k=True):			
			if m.listConnections(ctrl+'.'+attr,t='animCurve'):

				animDict[ctrl]['attrs'][attr] = {}
				keyframes = m.keyframe( ctrl, at =attr, time=(0,99999), query=True, valueChange=True, timeChange=True)
				animDict[ctrl]['attrs'][attr]['frames'] = keyframes[::2]
				animDict[ctrl]['attrs'][attr]['values'] = keyframes[1::2]

				if min(keyframes[::2]) < animDict['ALL_minFrame']:	animDict['ALL_minFrame'] = min(keyframes[::2])
				if max(keyframes[::2]) > animDict['ALL_maxFrame']:	animDict['ALL_maxFrame'] = max(keyframes[::2])				
				if min(keyframes[1::2]) < animDict['ALL_minValue']:	animDict['ALL_minValue'] = min(keyframes[1::2])
				if max(keyframes[1::2]) > animDict['ALL_maxValue']:	animDict['ALL_maxValue'] = max(keyframes[1::2])

	return animDict