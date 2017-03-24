print 'skinning module loaded'
import maya.cmds as m

class toolset():
	def __init__(self,gDriveRootPath,cloudShelf,adminPrefix):		
		self.gDriveRootPath = gDriveRootPath
		self.cloudShelf = cloudShelf
		self.adminPrefix = adminPrefix
		skinningToolsOrdered = ['helperSystems','skinningTools']
		skinningToolDetails = 	{	'skinningTools':	['skinningTools.png',
														'import maya.mel as mel\n'
														'''mel.eval('source "'''+self.gDriveRootPath+self.adminPrefix+'''Public/skinning/skinningTools.mel" ')''',
														'David Waldens skinning tools.'],

									'helperSystems': 	['helperSystems.png',
														'import skinning.helperSystems;meWindow = skinning.helperSystems.meBuild_UI()',
														'Helper joint creation tool.']
								}	
		for tool in skinningToolsOrdered:
			print tool
			result = m.shelfButton (tool+'_SHLF',image='pythonFamily.xpm',command=skinningToolDetails[tool][1],ann=skinningToolDetails[tool][2],l=tool,p=self.cloudShelf)
			print result