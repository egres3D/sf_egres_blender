import bpy
import imp
import sys
import os

sys.path.append(os.path.dirname(__file__))

import MeshOps

modules = [
    MeshOps
]

import MeshFile
import api_egres
import MeshOps

imp.reload(API_EGRES)
imp.reload(MeshFile)
imp.reload(MeshOps)

[imp.reload(m) for m in modules]

def register():
    for m in modules: m.register()

def unregister():
    for m in modules: m.unregister()
