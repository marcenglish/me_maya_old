
def returnData():
	scriptPath = 'D:/Dropbox/meMaya/'

	returnVar = {

	#RIGGING SHELF
	'meRig':	{

					 'ORDER':			['init','dev','cometOrient','mirror','weightedJoints','skinningTools','devView','curveBuilder','builderUI','legoExtras','snap','BB'],

					 'builderUI': 		['builderUI','meChar.bmp','from Rig import meBuildTemplate_UI;reload(meBuildTemplate_UI);BLD_UI = meBuildTemplate_UI.UI()','toolApopupCommandA'],
					 
					 'curveBuilder': 	['curveBuilder','meCrv.bmp','toolBpopuplabel','toolBpopupCommandA'],
					 
					 'devView' : 		['devView','meDevView.bmp','toolCpopuplabel','toolCpopupCommandA'],

					 'skinningTools' : 	['skinningTools','Ctools.bmp','''import maya.mel as mel;mel.eval('source "'''+scriptPath+'''Rig/skinningTools.mel"')''' ,'toolCpopupCommandA'],

					 'weightedJoints' : ['weightedJoints','weightedJoint.png','from Rig import meHelper_UI;reload(meHelper_UI);HS_UI = meHelper_UI.meBuild_UI()' ,'toolCpopupCommandA'],

					 'mirror' : 		['mirror','~split.png','import Rig.Widgets;Rig.Widgets.mirrorAny()','popup'],

					 'cometOrient' : 	['cometOrient','cometJointOrient.bmp','''import maya.mel as mel;mel.eval('source "'''+scriptPath+'''comet/cometJointOrient.mel";cometJointOrient')''' ,'toolCpopupCommandA'],

					 'cometOrient' : 	['cometSave','cometSaveWeights.bmp','''import maya.mel as mel;mel.eval('source "'''+scriptPath+'''comet/cometSaveWeights.mel";cometSaveWeights')''' ,'toolCpopupCommandA'],

					 'dev': 			['testAnim','dev.bmp','execfile("'+scriptPath+'Rig/Dev.py")'],

					 'init':			['initShelf','','execfile("'+scriptPath+'mayaData/initShelf.py")'],

					 'legoExtras':		['legoExtras','','execfile("D:/Dropbox/NinjaGo_PROD/Resources/Rig/genericLego_BuildExtras.py")'],

					 'snap':			['snap','animSnap.bmp','from Rig import meTools;meTools.PC()'],

					 'BB':				['BB','asterisk.png','from Rig import meTools;meTools.BB()'],

					 }
	
	#ANIM SHELF

	}

	return returnVar
print 'shelfContents reloaded'