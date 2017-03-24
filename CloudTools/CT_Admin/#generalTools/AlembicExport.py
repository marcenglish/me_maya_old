"""
  Copyright (C) 2012 Jon Macey
		jmacey@bournemouth.ac.uk
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import maya.OpenMaya as OM
import maya.OpenMayaAnim as OMA
import maya.cmds as cmds
import maya.mel as mel

# our basic class to do the Alembic output


class AlembicExport() :
	########################################################################################################################
	# @brief ctor
	########################################################################################################################

	def __init__(self) :
		# check to see if plugin is loaded
		plugs=cmds.pluginInfo( query=True, listPlugins=True )
		if "AbcExport" not in plugs :
				print "AbcExport not loaded please load it"
		else :
			# get the currently selected objects and make sure we have only one object
			selected = OM.MSelectionList()
			OM.MGlobal.getActiveSelectionList(selected)
			self.selectedObjects = []
			selected.getSelectionStrings(self.selectedObjects)
			if len(self.selectedObjects) == 0 :
				cmds.confirmDialog( title='No objects Selected', message='Select a Mesh Object', button=['Ok'], defaultButton='Ok', cancelButton='Ok', dismissString='Ok' )
			else :
				# get the start and end values for our UI sliders
				anim=OMA.MAnimControl()
				minTime=anim.minTime()
				maxTime=anim.maxTime()
				# set the attributes to some default values
				self.start=int(minTime.value())
				self.end=int(maxTime.value())
				self.uv=True
				self.ws=False
				self.steps=1
				self.normals=True
				self.verbose=False
				# now we create a window ready to populate the components
				# rtf re-size to children and s means no re-size
				self.window = cmds.window( title='NCCA Alembic Export',rtf=True )
				# create a layout
				cmds.scrollLayout( 'scrollLayout' )
				frame=cmds.frameLayout( label='Frame Control', borderStyle='in' )
				cmds.setParent("..")
				# create two sliders for start and end we also attach methods to be called when the slider
				# this is just tedious ui code and attaching callbacks
				cmds.setParent(frame)
				startSlider=cmds.intSliderGrp( changeCommand=self.startChanged,field=True, label='Start Frame', minValue=self.start, maxValue=self.end, fieldMinValue=self.start, fieldMaxValue=self.end, value=self.start )
				endSlider=cmds.intSliderGrp( changeCommand=self.endChanged ,field=True, label='End Frame', minValue=self.start, maxValue=self.end, fieldMinValue=self.end, fieldMaxValue=self.end, value=self.end )
				frameStep=cmds.intSliderGrp( changeCommand=self.stepChanged,field=True, label='Frame step', minValue=1, maxValue=50, fieldMinValue=0, fieldMaxValue=50, value=1 )
				# do some toggles for export flags will set sensible defaults
				cmds.frameLayout( label='Mesh Values', borderStyle='in' )
				uvCheck=cmds.checkBox( label='export UV', changeCommand=self.uvChanged,enable=True,value=True )
				normalCheck=cmds.checkBox( label='export Normals', changeCommand=self.normalChanged,enable=True,value=True )
				wsCheck=cmds.checkBox( label='World Space Transforms', changeCommand=self.wsChanged,enable=True,value=False )
				cmds.frameLayout( label='Advanced Commands', borderStyle='in' )
				self.minusSL=False
				cmds.checkBox( label='-sl all selected nodes  root', changeCommand=self.slChanged,enable=True,value=False )
				self.renderOnly=False
				cmds.checkBox( label='-rl render only', changeCommand=self.renderOnlyChanged,enable=True,value=False )
				self.stripNS=False
				cmds.checkBox( label='strip namespaces', changeCommand=self.stripNSChanged,enable=True,value=False )
				self.writeColourSet=False
				cmds.checkBox( label='Write Colour sets', changeCommand=self.writeColourSetsChanged,enable=True,value=False )
				self.wholeFrameGeo=False
				cmds.checkBox( label='Whole Frame Geo', changeCommand=self.wholeFrameGeoChanged,enable=True,value=False )
				self.writeVisibility=False
				cmds.checkBox( label='Write visibility', changeCommand=self.writeVisibilityChanged,enable=True,value=False )
				self.preRoll=0
				cmds.intSliderGrp( changeCommand=self.preRollChanged,field=True, label='preroll start frame', minValue=0, maxValue=self.end, fieldMinValue=self.start, fieldMaxValue=self.end, value=1 )
				frame=cmds.frameLayout( label='Mel Per Frame Callback', borderStyle='in' )
				self.melPerFrame=cmds.textField()
				frame=cmds.frameLayout( label='Python Per Frame Callback', borderStyle='in' )
				self.pythonPerFrame=cmds.textField()
				frame=cmds.frameLayout( label='Mel Post Job Callback', borderStyle='in' )
				self.melPostJob=cmds.textField()
				frame=cmds.frameLayout( label='Python Post Job Callback', borderStyle='in' )
				self.pythonPostJob=cmds.textField()
				frame=cmds.frameLayout( label='Alembic Output', borderStyle='in' )
				verboseCheck=cmds.checkBox( label='verbose', changeCommand=self.verboseChanged,enable=True,value=False )
				cmds.text(label="job string")
				self.jobstring=cmds.textField()

				cmds.frameLayout( label='Export', borderStyle='in' )
				# create a button and add the method called when pressed
				export=cmds.button( label='Export', command=self.export )
				# finally show the window
				cmds.setParent(self.window)
				cmds.showWindow( self.window )



	def ExportAlembic(self,file) :
		print "exporting alembic"
		# here we just build up our job string based on the ui components selected
		jobstring="AbcExport "
		if self.verbose == True :
			jobstring+=" -v "
		jobstring+="-j \" -fr %d %d -s %d" %(self.start,self.end,self.steps)
		if self.ws == True :
			jobstring+=" -ws "
		if self.uv == True :
			jobstring+=" -uv "
		if self.normals == False :
			jobstring+=" -nn "
		if self.minusSL == True :
			jobstring+=" -sl "
		if self.renderOnly == True :
			jobstring+=" -ro "
		if self.stripNS == True :
			jobstring+=" -sn "
		if self.writeColourSet == True :
			jobstring+=" -wcs "
		if self.wholeFrameGeo == True :
			jobstring+=" -wfg "
		if self.writeVisibility == True :
			jobstring+=" -wv "
		if self.preRoll !=0 :
			jobstring+=" -prs %d " %(self.preRoll)
		# get the job strings if present
		jobText=cmds.textField(self.melPerFrame, query=True,text=True)
		if len(jobText) !=0 :
			jobstring+=" -mfc %s " %(jobText)
		jobText=cmds.textField(self.pythonPerFrame, query=True,text=True)
		if len(jobText) !=0 :
			jobstring+=" -pfc %s " %(jobText)
		jobText=cmds.textField(self.melPostJob, query=True,text=True)
		if len(jobText) !=0 :
			jobstring+=" -mpc %s " %(jobText)
		jobText=cmds.textField(self.pythonPostJob, query=True,text=True)
		if len(jobText) !=0 :
			jobstring+=" -ppc %s " %(jobText)
		# now loop through all the selected objects and add as a root I don't check
		# to see if they are valid alembic objects as alembic does that for us
		for prim in self.selectedObjects :
			jobstring+=" -root %s" %(prim)
		jobstring+=" -file %s \"" %(file[0])
		# this puts the job string into the debug bar so we can copy it
		cmds.textField(self.jobstring, edit=True, text=jobstring)
		# now execute the string (as a mel one)
		mel.eval(jobstring)

	########################################################################################################################
	# @brief export method attached ot the button, this will be executed once every time
	# the button is pressed
	# @param *args the arguments passed from the button
	########################################################################################################################

	def export(self,*args) :
		# get the file name to save too
		basicFilter = "*.abc"
		file=cmds.fileDialog2(caption="Please select file to save",fileFilter=basicFilter, dialogStyle=2)
		# check we get a filename and then save
		if file !="" :
			if self.start >= self.end :
				cmds.confirmDialog( title='Range Error', message='start >= end', button=['Ok'], defaultButton='Ok', cancelButton='Ok', dismissString='Ok' )
			else :
				self.ExportAlembic(file)
				# finally remove the export window uncomment this if you want gui to exit at end
				#cmds.deleteUI( self.window, window=True )

	########################################################################################################################
	# @brief this is called every time the slider is changed (i.e. a new value)
	# @param *args the arguments passed from the button [0] is the numeric value
	########################################################################################################################

	def startChanged(self, *args) :
		self.start=args[0]

	########################################################################################################################
	# @brief this is called every time the slider is changed (i.e. a new value)
	# @param *args the arguments passed from the button [0] is the numeric value
	########################################################################################################################

	def endChanged(self, *args) :
		self.end=args[0]

	def uvChanged(self, *args) :
		self.uv=args[0]
	def wsChanged(self, *args) :
		self.ws=args[0]

	def normalChanged(self, *args) :
		self.normals=args[0]

	def stepChanged(self, *args) :
		self.steps=args[0]

	def verboseChanged(self, *args) :
		self.verbose=args[0]

	def slChanged(self, *args) :
		self.minusSL=args[0]

	def renderOnlyChanged(self, *args) :
		self.renderOnly=args[0]

	def stripNSChanged(self, *args) :
		self.stripNS=args[0]

	def writeColourSetsChanged(self, *args) :
		self.writeColourSets=args[0]

	def wholeFrameGeoChanged(self, *args) :
		self.wholeFrameGeo=args[0]

	def writeVisibilityChanged(self, *args) :
		self.writeVisibility=args[0]

	def preRollChanged(self, *args) :
		self.preRoll=args[0]


