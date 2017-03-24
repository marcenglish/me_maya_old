#COPY AND PASTE THIS TO GET STARTED

import sys
import maya.cmds as m

scriptPath = 'D:/Dropbox/meMaya/'

paths = [scriptPath,scriptPath+'mayaData/',scriptPath+'Rig/']
#paths = ['E:\Test\SCRIPTS','E:\Test\SCRIPTS\Rig']
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

import mayaSetup
reload(mayaSetup)
from mayaData import meHotkeys
import Rig
#import meBuildUI;reload(meBuildTemplate_UI);BLD_UI = meBuildTemplate_UI.UI()

meSetup = mayaSetup.setup()
meSetup.buildShelf('meRig')