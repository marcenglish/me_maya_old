print 'hey!'
class test():
	def confirmSetup(self):
		import maya.cmds as m
		m.confirmDialog(title='It Worked', message="Cloud Tools install successful!", button=['Nice one'], defaultButton='Nice one')