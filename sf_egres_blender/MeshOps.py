import time

import bpy
import os
from MeshFile import StarfieldMeshFile

class SF_EGRES_ImportMesh(bpy.types.Operator):
    bl_idname = "import_scene.egres_import_mesh"
    bl_label = "Import Mesh"

    filepath: bpy.props.StringProperty(options={'HIDDEN'})
    directory: bpy.props.StringProperty(options={'HIDDEN'})
    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement)
    filename: bpy.props.StringProperty(default='untitled.mesh')
    filter_glob: bpy.props.StringProperty(default="*.mesh", options={'HIDDEN'})

    def execute(self, context):
        if bpy.context.object is not None:
            if bpy.context.object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode='OBJECT')
            [o.select_set(False) for o in bpy.context.view_layer.objects if o.select_get()]

        start = time.time()
        for f in self.files:
            path = os.path.join(self.directory, f.name)
            mesh = StarfieldMeshFile(name=f.name[:-5])
            mesh.LoadMesh(path)
            mesh.CreateBlenderMesh()
            del mesh

        print("TIME: ", time.time() - start)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

ops = [
    SF_EGRES_ImportMesh,
]

def menu_func_sf_mesh_import(self, context):
    self.layout.operator(
        SF_EGRES_ImportMesh.bl_idname,
        text="[EGRES] Starfield Mesh (.mesh)",
    )

def register():
    for c in ops:
        bpy.utils.register_class(c)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_sf_mesh_import)


def unregister():
    for c in ops:
        bpy.utils.unregister_class(c)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_sf_mesh_import)
