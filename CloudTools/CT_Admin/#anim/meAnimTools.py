import maya.cmds as m
import meTools
#Swaps the attrs between two controllers
def swapAttrs():
    sel = m.ls(sl=True)
    attrA = m.listAttr(sel[0],k=True)
    attrB = {}
    for attr in attrA:
        attrB[attr] = m.getAttr(sel[1]+'.'+attr)
        m.setAttr(sel[1]+'.'+attr,m.getAttr(sel[0]+'.'+attr))
        
    for attr in attrB:
        m.setAttr(sel[0]+'.'+attr,attrB[attr])

#Copies all attrs from first to second selection on a designated frame
def copyToFrame():
    result = m.promptDialog(
                    title='Rename Object',
                    message='Enter Name:',
                    button=['OK', 'Cancel'],
                    defaultButton='OK',
                    cancelButton='Cancel',
                    dismissString='Cancel')
    
    if result == 'OK':
        text = m.promptDialog(query=True, text=True)        
        frame = int(text)        
        sel = m.ls(sl=True)

        if len(sel) == 1:
            tgt = sel[0]
        else:
            tgt = sel[1]

        attrA = m.listAttr(sel[0],k=True)
        attrB = {}

        for attr in attrA:    
            attrB[attr] = m.getAttr(sel[0]+'.'+attr)

        m.currentTime(frame)    
 
        for attr in attrB:
            m.setAttr(tgt+'.'+attr,attrB[attr])           

def swapSpace():    
    if m.ls(sl=True):
        sel = m.ls(sl=True)[0]
        spaces = m.attributeQuery('parentSpace',node=sel,le=True)[0].split(':')
        window = 'SpaceSwitcher'
        if m.window('SpaceSwitcher',ex=True): m.deleteUI(window)
        win = m.window(window, title=window, widthHeight=(200, 55))
        m.columnLayout('SS_COL',cal='center') 
        m.optionMenu('SS_Space_OPT',l='Space',cc='import meAnimTools;meAnimTools.meSwitchSpace()')
        m.button('Close',c='m.deleteUI("'+win+'")',w= 150)

        for ea in spaces:
            m.menuItem(ea)

        m.showWindow(window)


def meSwitchSpace():
    sel = m.ls(sl=True)[0]
    control = m.optionMenu('SS_Space_OPT',q=True,v=True)
    spaces= m.attributeQuery('parentSpace',node=sel,le=True)[0].split(':')
    index= spaces.index(control)
    if m.objExists('SS_tempLoc'): m.delete('SS_tempLoc')
    m.spaceLocator(n='SS_tempLoc')
    meTools.mePC('SS_tempLoc',sel,0)
    m.setAttr(sel+'.parentSpace',index)
    meTools.mePC(sel,'SS_tempLoc',0)
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



def killFlatKeys():
    pass

def pbNoCurves():
    pass

#Cleanup animation on enumerators
def stepForEnums():
    pass
