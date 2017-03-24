print "skinExport"
import maya.mel as mel


mode = 'save'
if mode == 'save':
	for ea in m.ls(sl=True):
		componentType = ''
		selectionMask = 0
		shape = m.listRelatives(ea,p=False,s=True)[0]
		if m.nodeType(shape) == 'mesh':
			componentType = 'vtx'
			selectionMask = 31
		if m.nodeType(shape) == 'nurbsSurface':
			componentType = 'cv'
			selectionMask = 28
		skinCluster = m.listConnections('chest_GEOShape',type='skinCluster')[0]
		m.select(ea+'Shape.'+componentType+'[0:*]')
		comps = m.filterExpand(m.ls(sl=True),sm=selectionMask)
		compsMel = '{'
		for comp in comps:
			compsMel = compsMel +'"'+comp+'",'
		compsMel = compsMel[:-1] + '}'
		print compsMel

		mel.eval('string $comps[] = libSkin_getSelComps("'+skinCluster+'");cSaveW_save("'+skinCluster+'", "C:/Users/Marc/Desktop/temp/'+ea+'.wt", '+compsMel+', 0,0)')


if mode == 'load':
	

	cmdString = 'cSaveW_load($skinCl, $file, $comps, $mode, $tol, $mirrorMode, $search, $replace, $bDoPrune, $prunePlaces);'	