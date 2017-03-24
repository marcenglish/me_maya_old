#ATTRIBUTE PROXY SETUP - Simple ui for quick attribute proxy representation.


import maya.cmds as m
from functools import partial
print 'attributeProxy'

class AttributeProxySetup():
	def __init__(self,*args):
		self.obj_attr_data = {}
		self.toggleStatus = True
		so = m.ls(sl=True)
		if so:			
			self.analyzeObject(so[0])	
			self.attributeProxyUI(so[0])
		else:
			self.attributeProxyUI()
		


	def analyzeObject(self,source_object,*args):

		

		#build a dictionary of all attrs, types, values and limits for source object
		for attr in m.listAnimatable(source_object):

			#to keep things simple for now, the script does not support compound attributes	
			if len(attr.split('.')) == 2:		
				attr = attr.split('.')[-1]

				self.obj_attr_data[attr] = {}
				self.obj_attr_data[attr]['type'] = m.getAttr(source_object+'.'+attr,typ=True)		
				self.obj_attr_data[attr]['value'] = m.getAttr(source_object+'.'+attr)

				if self.obj_attr_data[attr]['type'] == 'enum':
					self.obj_attr_data[attr]['extra'] = m.attributeQuery(attr,node=source_object,listEnum=True)
				else:
					if m.attributeQuery(attr, node=source_object,minExists=True):
						attr_min = m.attributeQuery(attr, node=source_object,min=True)[0]
					else:
						attr_min = None
					if m.attributeQuery(attr, node=source_object,maxExists=True):
						attr_max = m.attributeQuery(attr, node=source_object,max=True)[0]
					else:
						attr_max = None
					self.obj_attr_data[attr]['extra'] = [attr_min,attr_max]

		self.obj_attrs_sorted = []
		for attr_sorted in m.listAttr(source_object,k=True):
			if attr_sorted in self.obj_attr_data.keys():
				self.obj_attrs_sorted.append(attr_sorted)


		return self.obj_attr_data

	def attributeProxyUI(self,*args):
		#Get rid of previous window instances
		if m.windowPref('AttributeProxy_WIN',q=True,ex=True): 
			m.windowPref('AttributeProxy_WIN', remove=True )
		if m.window('AttributeProxy_WIN',q=True,ex=True): 
		    m.deleteUI('AttributeProxy_WIN')

		window = m.window('AttributeProxy_WIN',title='Attribute Proxy Maker', w=280,h=420)

		m.columnLayout(columnAttach=('both', 0), rowSpacing=10, columnWidth=300)

		m.columnLayout(columnAttach=('both', 5), rowSpacing=10, columnWidth=300)
			
		m.text('Choose Source:')
		m.rowLayout( numberOfColumns=2, columnWidth2=(250,30), adjustableColumn=2, columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0)] )

		default_text = ''
		if args:
			default_text = args[0]
		
		m.textField('Source_FLD',w=250,tx=default_text)
		m.button('SourcePop_BTN',l='<<',c=partial(self.UI_populate,'source'))
		m.setParent('..')

		m.separator(height=2, style='singleDash')
		m.text('Choose Proxy:')

		m.rowLayout( numberOfColumns=2, columnWidth2=(250,30), adjustableColumn=2, columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0)] )
		m.textField('Proxy_FLD',w=250)
		m.button('ProxyPop_BTN',l='<<',c=partial(self.UI_populate,'proxy'))
		m.setParent('..')
		m.separator(height=2, style='singleDash')

		m.scrollLayout(verticalScrollBarThickness=16)
		m.rowColumnLayout( numberOfColumns=2 ,cw=[20,200],cal=(2,'left'))
		
		m.button('all',w=20,c=partial(self.UI_toggleAll))
		m.text('')
		for attr in self.obj_attrs_sorted:
			m.checkBox(attr+'_APMCHK',l='',w=20,v=1)
			m.text(l=attr,w=200)
		m.setParent('..')
		m.setParent('..')



		m.button("Connect",h=50,c=partial(self.UI_connectProxyGather))

		m.showWindow( 'AttributeProxy_WIN' )
		m.window( 'AttributeProxy_WIN',e=True,h=410 )

	def UI_connectProxyGather(self,*args):
		specific_attrs = []
		for cb in m.lsUI(type='checkBox'):
			if 'APMCHK' in cb:
				if m.checkBox(cb,q=True,v=True):
					specific_attrs.append(cb.split('_')[0])
		

		self.source = m.textField('Source_FLD',q=True,tx=True)
		self.proxy = m.textField('Proxy_FLD',q=True,tx=True)
		
		self.connectProxy(self.obj_attr_data,self.source,self.proxy,specific_attrs)

	#This function can work independent of the UI 
	def connectProxy(self,obj_attr_data,source_object,proxy_object,specific_attrs=False,*args):
		
		#define the list of attributes to be connected 
		connections_list = []
		if specific_attrs:
			for sa in specific_attrs:
				connections_list.append(sa)				
		else:
			for sa in self.obj_attr_data:
				connections_list.append(sa)

		self.obj_attrs_sorted = []
		for attr_sorted in m.listAttr(source_object,k=True):
			if attr_sorted in connections_list:
				self.obj_attrs_sorted.append(attr_sorted)


		print 'connections list is '
		print connections_list

		print proxy_object+'---->'+source_object

		#connect things
		for cl in self.obj_attrs_sorted:

			if obj_attr_data[cl]['type'] in ['enum','float','long','bool']:

				if obj_attr_data[cl]['type'] == 'enum':
					print obj_attr_data[cl]['extra']
					m.addAttr(proxy_object,ln=cl,at='enum',en=obj_attr_data[cl]['extra'][0])
					
				if obj_attr_data[cl]['type'] == 'float':
					m.addAttr(proxy_object,ln=cl,at='double')

				if obj_attr_data[cl]['type'] == 'long':
					m.addAttr(proxy_object,ln=cl,at='long')
				
				if obj_attr_data[cl]['type'] == 'bool':
					m.addAttr(proxy_object,ln=cl,at='bool')


				print obj_attr_data[cl]['type']
				m.setAttr(proxy_object+'.'+cl,obj_attr_data[cl]['value'])
				m.setAttr(proxy_object+'.'+cl,k=True)
				m.connectAttr(proxy_object+'.'+cl,source_object+'.'+cl)



	def UI_populate(self,*args):
		if args[0] == 'source':
			m.textField('Source_FLD',e=True,tx=m.ls(sl=True)[0])

		if args[0] == 'proxy':
			m.textField('Proxy_FLD',e=True,tx=m.ls(sl=True)[0])

	def UI_toggleAll(self,*args):
		for cb in m.lsUI(type='checkBox'):
			if 'APMCHK' in cb:
				m.checkBox(cb,e=True,v=self.toggleStatus)

		self.toggleStatus = not self.toggleStatus



APS = AttributeProxySetup()

