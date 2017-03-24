#mayaSetup
import maya.cmds as m
from mayaData import shelfContents
reload(shelfContents)

reload(shelfContents)
class setup():
	def __init__(self):
		print 'setup obj created'
	
	def buildShelf(self,type):		

		shelfData = shelfContents.returnData()

		#temporary paths 
		iconPath = 'D:/Dropbox/meMaya/icons/'		

		self.removeShelf(type)

		m.shelfLayout(type,style='iconOnly',parent = 'ShelfLayout')
		
		for tool in shelfData[type]['ORDER']:
			m.shelfButton (	shelfData[type][tool][0],
							image=iconPath+shelfData[type][tool][1],
							command=shelfData[type][tool][2],
							ann=shelfData[type][tool][0])

		

		print type+' shelf created'


	def removeShelf(self,type):
		currentShelves = m.tabLayout('ShelfLayout',q=True,ca=True)
		if type in currentShelves:
			m.deleteUI(type)		

	def reloadHotkeys(self):
		pass
