import maya.cmds as m
import maya.mel as mel
from functools import partial

def ssWindow():    
    if m.ls(sl=True):
        sel = m.ls(sl=True)[0]
        spaces = m.attributeQuery('parentSpace',node=sel,le=True)[0].split(':')
        window = 'SpaceSwitcher'
        if m.window('SpaceSwitcher',ex=True): m.deleteUI(window)
        win = m.window(window, title=window, widthHeight=(200, 55))
        m.columnLayout('SS_COL',cal='center') 
        m.optionMenu('SS_Space_OPT',l='Space',cc='switchSpace()')
        m.button('Close',c='m.deleteUI("'+win+'")',w= 150)

        for ea in spaces:
            m.menuItem(ea)

        m.showWindow(window)

def switchSpace(*args):
    sel = m.ls(sl=True)[0]
    control = m.optionMenu('SS_Space_OPT',q=True,v=True)
    spaces= m.attributeQuery('parentSpace',node=sel,le=True)[0].split(':')
    index= spaces.index(control)
    if m.objExists('SS_tempLoc'): m.delete('SS_tempLoc')
    m.spaceLocator(n='SS_tempLoc')
    m.delete(m.parentConstraint(sel,'SS_tempLoc'))
    m.setAttr(sel+'.parentSpace',index)
    m.delete(m.parentConstraint('SS_tempLoc',sel))
    m.delete('SS_tempLoc')
    m.select(sel)

def swapLR():
    sel = m.ls(sl=True)
    newSel = []
    left = '_L'
    right = '_R'
    for ea in sel:
        old = left
        new = right
        if right+'_' in ea or ea.endswith(right):
            old = right
            new = left      
        if ea.endswith(old):
            newSel.append(ea.replace(old,new))
        else:
            newSel.append(ea.replace(old+'_',new+'_'))
    m.select(newSel)

def curveVis():
	currentPanel = m.getPanel(withFocus=True)
	state = m.modelEditor(currentPanel, q=True,av=True,nc=True)
	m.modelEditor(currentPanel,edit=True,av=True,nc= not state)

def curveAll():
	curves = m.ls(typ='nurbsCurve')
	curveSelectionSet = []
	for curve in curves:
		parent = m.listRelatives(curve,p=True,c=False)[0]
		if m.objExists(parent+'.ctrl'):
			curveSelectionSet.append(parent)
	m.select(curveSelectionSet)

def graph():
	print 'show graph editor'
	mel.eval('tearOffPanel "Graph Editor" "graphEditor" true;')
