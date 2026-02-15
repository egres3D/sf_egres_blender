import os.path

import bpy
from ArchFile import BArchive
from MeshFile import StarfieldMeshFile

archive = None

def updateArchiveList():
    if archive == None: return

    bpy.context.window_manager.egres_archive.archive_items.clear()
    bpy.context.window_manager.egres_archive.path = archive.path

    for a in archive.archive_items:
        item = bpy.context.window_manager.egres_archive.archive_items.add()
        item.name = a.full_path
        item.display_name = a.filename
        item.extension = a.extension
        item.path = a.full_path

class EGRES_Archive_PickArchive(bpy.types.Operator):
    bl_idname = "scene.egres_sf_archive_picker"
    bl_label = "Select archive"

    filter_glob: bpy.props.StringProperty(
        default="*.ba2",
        options={'HIDDEN'}
    )

    filepath: bpy.props.StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        global archive
        path = self.filepath

        if path.startswith("//"):
            path = bpy.path.abspath(path)

        archive = BArchive(path)
        archive.loadPaths()
        updateArchiveList()
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class EGRES_Archive_ImportMesh(bpy.types.Operator):
    bl_idname = "scene.egres_sf_import_mesh_from_archive"
    bl_label = "Import mesh"
    def execute(self, context):
        global archive
        a = bpy.context.window_manager.egres_archive
        l = a.archive_items
        idx = bpy.context.window_manager.egres_archive.active_item_index
        item = l[idx]
        print(item.path)
        print(a.path)

        mesh = StarfieldMeshFile(os.path.basename(item.path).rpartition(".")[0])
        mesh.LoadMesh_Archive(a.path, item.path)
        mesh.CreateBlenderMesh()

        return {'FINISHED'}

class EGRES_Archive_LoadPaths(bpy.types.Operator):
    bl_idname = "scene.egres_sf_archive_load_paths"
    bl_label = "Load"
    def execute(self, context):
        global archive
        archive.loadPaths()
        updateArchiveList()
        return {'FINISHED'}

class ArchiveListItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="")
    path: bpy.props.StringProperty(default="")
    extension: bpy.props.StringProperty(default="")
    display_name: bpy.props.StringProperty(default="")

class ArchiveListCollection(bpy.types.PropertyGroup):
    archive_items: bpy.props.CollectionProperty(type=ArchiveListItem, name="Archive items")
    active_item_index: bpy.props.IntProperty(default=0)
    path: bpy.props.StringProperty(default="", subtype="FILE_PATH")

class EGRESARCHIVE_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.display_name)

class EGRES_ArchivePanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_hello_world"
    bl_label = "EGRES Starfield Archive"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'EGRES Starfield Archive'

    def draw(self, context):
        global archive
        layout = self.layout

        layout.operator("scene.egres_sf_archive_picker")

        if archive == None: return
        box = layout.box()
        box.template_list(
            "EGRESARCHIVE_UL_List",
            "",
            context.window_manager.egres_archive,
            "archive_items",

            context.window_manager.egres_archive,
            "active_item_index")

        #row = layout.row()
        box.operator("scene.egres_sf_import_mesh_from_archive")

panels = [
ArchiveListItem,
ArchiveListCollection,
EGRES_Archive_PickArchive,
EGRES_Archive_ImportMesh,
EGRESARCHIVE_UL_List,
EGRES_Archive_LoadPaths,
EGRES_ArchivePanel
]

def register():
    global archive_paths

    for c in panels:
        bpy.utils.register_class(c)

    w = bpy.types.WindowManager

    w.egres_archive = bpy.props.PointerProperty(type=ArchiveListCollection)

def unregister():
    for c in panels:
        bpy.utils.unregister_class(c)

    w = bpy.types.WindowManager

    del w.egres_archive