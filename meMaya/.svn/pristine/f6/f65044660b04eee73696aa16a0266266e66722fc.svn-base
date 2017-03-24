print 'configuring shelves...'
import maya.cmds as m

iconPath = 'D:/EverythingCG/Resrc/Icons/'
 
shelves = { 'meRigging':	{'toolA': ['toolAName','toolAIcon','meChar.bmp','toolApopuplabel','toolApopupCommandA'],
							 'toolB':  ['toolBName','toolBIcon','meChar.bmp','toolBpopuplabel','toolBpopupCommandA'],
							 'toolC' : ['toolCName','toolCIcon','meChar.bmp','toolCpopuplabel','toolCpopupCommandA']},

			'meAnim':		{'toolA': ['toolAName','toolAIcon','meChar.bmp','toolApopuplabel','toolApopupCommandA'],
							'toolB':  ['toolBName','toolBIcon','meChar.bmp','toolBpopuplabel','toolBpopupCommandA'],
							'toolC':  ['toolCName','toolCIcon','meChar.bmp','toolCpopuplabel','toolCpopupCommandA']},

			}

currentShelves = m.tabLayout('ShelfLayout',q=True,ca=True)

for shelf in shelves:
	if shelf in currentShelves:
		m.deleteUI(shelf)
	
	m.shelfLayout(shelf,style='iconOnly',parent = 'ShelfLayout')
	print shelf
	for tool in shelves[shelf]:
		m.shelfButton (shelves[shelf][tool][0],image=iconPath+shelves[shelf][tool][2],command=shelves[shelf][tool][3])
