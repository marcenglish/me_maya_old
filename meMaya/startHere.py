#COPY AND PASTE THIS TO GET STARTED

import sys
import maya.cmds as m
paths = ['D:/Dropbox/meMaya/','D:/Dropbox/meMaya/mayaData/']
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

import mayaSetup
from mayaData import meHotkeys

meSetup = mayaSetup.setup()
meSetup.buildShelf('meRig')