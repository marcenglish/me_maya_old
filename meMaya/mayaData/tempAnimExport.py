import maya.cmds as cmds
import os

#PUT YOUR DESKTOP PATH HERE. BE SURE TO USE FORWARD SLAHES, NOT BACK SLASHES
path = "C:/Users/Marc/Desktop/"

def saveAnim():
    exportCurves = []
    
    if 'savedAnimationClips' not in os.listdir(path):
        os.mkdir(path+'savedAnimationClips')
    
    controls = []
    
    #gather curves for export
    for ea in cmds.ls(type='transform'):
        if cmds.objExists(ea+'.ctrl'):
            if cmds.listConnections(ea,type='animCurve'):
                for animCurves in cmds.listConnections(ea,type='animCurve'):
                        exportCurves.append(animCurves)

	#export data                    
    if len(exportCurves) != 0:
        result = cmds.promptDialog(title = 'AnimSaver',message= 'Please Enter Clip Name',button=['OK','Cancel'],defaultButton='OK',cancelButton='Cancel',dismissString='Cancel')	
        if result == 'OK':
            cmds.select(exportCurves)
            clipName = cmds.promptDialog(q=True,text=True)
            os.mkdir(path+'savedAnimationClips/'+clipName)
            cmds.file(path+'savedAnimationClips/'+clipName+'/'+clipName+'.ma',es=True,typ='mayaAscii')




def loadAnim():
	filename = cmds.fileDialog2(fileMode=1, caption="Import Clip")
	cmds.file( filename[0], i=True )
	controls = []
	animCurves = []
	namespace = ''

	for ea in cmds.ls(type='transform'):
		if cmds.objExists(ea+'.ctrl'):
			if ':' in ea:
				controls.append(ea.split(':')[-1])
				namespace = ea.split(':')[0]+':'
			else:
				controls.append(ea)
				print 'nop'

	print controls 

	for ac in cmds.ls(type='animCurve'):
		for ctrl in controls:
			if ctrl in ac:				
				print ctrl+' is a match for '+ac
				
				attr = ac.split(ctrl)[-1][1:]
				sections = attr.split('_')				
				camelCase = sections[0]	
				if len(sections) > 1:
					print sections
					print '--'
					for i in range(len(sections)):
						if i != 0:
							camelCase += sections[i][0].upper()+sections[i][1:]

				try:
					cmds.connectAttr(ac+'.output',namespace+ctrl+'.'+camelCase)
				except:
					pass


loadAnim()



