import maya.cmds as m
import maya.mel as mel


hotkeys = { 'ToggleLRA':[['a'],'toggle -localAxis'],
			'ToggleXray':[['x','alt'],'meHotkeys.toggleXray()'],
			'toggleWOS':[['w','alt'],'meHotkeys.toggleWOS()'],
			# 'toggleGeoVis':'`',
			 'moveSkinnedJnt':[['j'],'moveJointsToolScript 0'],
			 'smoothBind':[['b','alt'],'performSkinCluster false'],
			# 'setDrivenKey':['alt','k'],
			 'averageWeights':[['o'],'source copySmooth'],
			 'toggleIsolate':[['i'],'meHotkeys.toggleIsolate()'],
			 'connectionEditor':[['C','ctl'],'optionVar -iv "connectWindowActive" 1; connectWindow'],
			 'graphEditor':[['A','ctl'],'tearOffPanel "Graph Editor" "graphEditor" true;'],
			 'hypergraphEditor':[['H','ctl'],'tearOffPanel "Hypergraph" "hyperGraphPanel" true;'],
			 'referenceEditor':[['R','ctl'],'tearOffPanel "Reference Editor" referenceEditor true'],
			 'pluginEditor':[['P','ctl'],'pluginWin'],
			 'selectHierarchy':[['-','ctl'],'select -hierarchy'],
			 'swapSel':[['u'],'meHotkeys.swapSel()'],
			}

for ea in hotkeys:
	altMod = False
	ctlMod = False		
	if 'alt' in hotkeys[ea][0]: altMod = True
	if 'ctl' in hotkeys[ea][0]: ctlMod = True

	wrapper = ['','']
	if '()' in hotkeys[ea][-1]:
		wrapper[0] = 'python("'
		wrapper[1] = '")'
	
def enable():
	m.nameCommand(ea, annotation=ea+'_ann', command=wrapper[0]+hotkeys[ea][-1]+wrapper[1])
	m.hotkey(k=hotkeys[ea][0][0], alt=altMod, ctl= ctlMod, rn='', name=ea)

#Display Widgets
def toggleXray():
	currentPanel = m.getPanel(withFocus=True)
	state = m.modelEditor(currentPanel, q=True,xr=True)
	m.modelEditor(currentPanel,edit=True,xr= not state)

def toggleWOS():
	currentPanel = m.getPanel(withFocus=True)
	state = m.modelEditor(currentPanel, q=True,wos=True)
	m.modelEditor(currentPanel,edit=True,wos= not state)

def toggleIsolate():
	currentPanel = m.getPanel(withFocus=True)
	panelType = m.getPanel(to=currentPanel)
	if panelType == "modelPanel":
		onFlag = m.isolateSelect(currentPanel, q=True,s=True)
		if onFlag == 0:
			mel.eval('enableIsolateSelect modelPanel4 - 1')
		else:
			mel.eval('enableIsolateSelect modelPanel4 - 0')


def swapSel():
	count = [0,0]
	sel = m.ls(sl=True)
	if '.' not in sel[0]:
		mel.eval('PolySelectConvert 3')


