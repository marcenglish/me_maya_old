#mayaSetup
import meHotkeys
#import meShelfSetup
import maya.cmds as m


meHotkeys.enable()

#------------
# SHELF SETUP
#------------


#shelf contents 
iconPath = 'D:/EverythingCG/Resrc/Icons/'
scriptPath = 'D:/EverythingCG/Resrc/SCRIPTS/'

shelves = { 'meRigging':	{'toolA': ['builderUI','builderUI','meChar.bmp','import meBuildUI;reload(meBuildUI);UI = meBuildUI.meBuild_UI()','toolApopupCommandA'],
							 'toolB':  ['curveBuilder','curveBuilder','meCrv.bmp','toolBpopuplabel','toolBpopupCommandA'],
							 'toolC' : ['devView','devView','meDevView.bmp','toolCpopuplabel','toolCpopupCommandA'],
							 'toolD' : ['skinningTools','skinningTools','Ctools.bmp','''import maya.mel as mel;mel.eval('source "'''+scriptPath+'''#skinning/skinningTools.mel"')''' ,'toolCpopupCommandA'],
							 'toolE' : ['weightedJoints','weightedJoints','weightedJoint.png','import meHelperUI;reload(meHelperUI)' ,'toolCpopupCommandA'],
							 'toolF' : ['mirror','mirror','~split.png','import meWidgets;meWidgets.mirrorAny()','popup'],
							 'toolG' : ['cometOrient','cometOrient','Ctools.bmp','''import maya.mel as mel;mel.eval('source "'''+scriptPath+'''comet/cometJointOrient.mel";cometJointOrient')''' ,'toolCpopupCommandA'],
							 #TBD - comet import
							 #TBD - JTD


							 'dev': 	['dev','dev','dev.bmp','import dev;reload(dev)']},

			'meAnim':		{'toolA': ['swapAttrs','swapAttrs','swapAttr.bmp','toolApopuplabel','toolApopupCommandA'],
							'toolB':  ['copyToFrame','copyToFrame','copyAttr.bmp','toolBpopuplabel','toolBpopupCommandA'],
							'toolD':  ['swapLR','swapLR','swapLR.png','import meAnimTools;meAnimTools.swapLR()','meSwapLR'],
							'toolC':  ['swapSpaces','swapSpaces','spaceSwitch.png','import meAnimTools;meAnimTools.swapSpace()','toolCpopupCommandA']},
			}


#shelf updater
currentShelves = m.tabLayout('ShelfLayout',q=True,ca=True)
print 'Shelf contents:'
print currentShelves

for shelf in shelves:
	if shelf in currentShelves:
		print m.deleteUI(shelf)

	
	m.shelfLayout(shelf,style='iconOnly',parent = 'ShelfLayout')
	for tool in shelves[shelf]:
		m.shelfButton (shelves[shelf][tool][0],image=iconPath+shelves[shelf][tool][2],command=shelves[shelf][tool][3],ann=shelves[shelf][tool][1])

