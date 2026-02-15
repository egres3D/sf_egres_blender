import bpy
import imp
import sys
import os

sys.path.append(os.path.dirname(__file__))

import MeshOps
import ArchFile
import ArchPanel

modules = [
MeshOps,
ArchPanel,

]

import MeshFile
import api_egres
import MeshOps

imp.reload(api_egres)
imp.reload(ArchFile)
imp.reload(ArchPanel)
imp.reload(MeshFile)
imp.reload(MeshOps)

[imp.reload(m) for m in modules]

def register():
    for m in modules: m.register()

def unregister():
    for m in modules: m.unregister()
