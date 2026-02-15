import ctypes

import bmesh
import bpy
import numpy as np

from api_egres import MeshReadWriteFlags, PtrToNp, RawBuffer, DllReadMeshBin, ArchiveReadMesh, \
    DllFreeMesh


def CreateUv(mesh, vertex_indices, uv_data_array, n):
    if isinstance(uv_data_array, np.ndarray):
        uv_layer = mesh.uv_layers.new(name=f"UV{n}")
        uv_data_array[:, 1] = 1 - uv_data_array[:, 1]
        uv_layer.data.foreach_set("uv", uv_data_array[vertex_indices].ravel())

class StarfieldMeshFile:
    def __init__(self, name="UNKNOWN", read_flags=MeshReadWriteFlags(1, 1, 1, 1, 1, 0, 1, 0, 0)):
        self.name = name
        self.verts = None
        self.tris = None
        self.uv1 = None
        self.uv2 = None
        self.colors = None
        self.normals = None
        self.tangents = None
        self.weights = None
        self.flags = read_flags

    def Buffers_Load(self):
        TOTAL = 8
        buffers = (RawBuffer * TOTAL)()
        return buffers

    def Buffers_Collect(self, buffers):
        if buffers[0].len > 0:
            self.tris = PtrToNp(buffers[0].ptr, ctypes.c_uint16, np.uint16, buffers[0].len).reshape(-1, 3)

        if buffers[1].len != 0:
            self.verts = PtrToNp(buffers[1].ptr, ctypes.c_float, np.float32, buffers[1].len).reshape(-1, 3)

        if buffers[2].len != 0:
            self.uv1 = PtrToNp(buffers[2].ptr, ctypes.c_float, np.float32, buffers[2].len).reshape(-1, 2)

        if buffers[3].len != 0:
            self.uv2 = PtrToNp(buffers[3].ptr, ctypes.c_float, np.float32, buffers[3].len).reshape(-1, 2)

        if buffers[4].len != 0:
            self.colors = PtrToNp(buffers[4].ptr, ctypes.c_uint8, np.uint8, buffers[4].len).reshape(-1, 4)

        if buffers[5].len != 0:
            normals_buf = PtrToNp(buffers[5].ptr, ctypes.c_float, np.float32, buffers[5].len).reshape(-1, 3)
            self.normals = normals_buf / np.linalg.norm(normals_buf, axis=1)[:, np.newaxis]

        if buffers[6].len != 0:
            self.tangents = PtrToNp(buffers[6].ptr, ctypes.c_float, np.float32, buffers[6].len).reshape(-1, 3)

        if buffers[7].len != 0:
            self.weights = PtrToNp(buffers[7].ptr, ctypes.c_float, np.float32,
                                   buffers[7].len * (int(buffers[1].len / 3))).reshape(buffers[7].len, int(buffers[1].len / 3))

        DllFreeMesh(buffers)

    def LoadMesh_Archive(self, archive_path, mesh_path):
        buffers = self.Buffers_Load()
        ArchiveReadMesh(
            archive_path.encode('utf-8'),
            mesh_path.encode('utf-8'),
            buffers)
        self.Buffers_Collect(buffers)

    def LoadMesh_Bin(self, mesh_path):
        buffers = self.Buffers_Load()
        DllReadMeshBin(mesh_path.encode('utf-8'), buffers)
        self.Buffers_Collect(buffers)

    def CreateBlenderMesh(self):
        """Expects object mode."""

        mesh = bpy.data.meshes.new(self.name)
        obj = bpy.data.objects.new(self.name, mesh)
        bm = bmesh.new()

        # verts
        [bm.verts.new(self.verts[i]) for i in range(self.verts.shape[0])]
        bm.verts.ensure_lookup_table()
        bm.verts.index_update()

        # tris
        for i in range(self.tris.shape[0]):
            v1 = bm.verts[self.tris[i][0]]
            v2 = bm.verts[self.tris[i][1]]
            v3 = bm.verts[self.tris[i][2]]

            try:
                bm.faces.new((v1, v2, v3))
            except ValueError:
                continue

        # to mesh
        bm.to_mesh(mesh)
        bm.free()

        vertex_indices = np.empty(len(mesh.loops), dtype=np.int32)
        mesh.loops.foreach_get('vertex_index', vertex_indices)

        # uv
        CreateUv(mesh, vertex_indices, self.uv1, 1)
        CreateUv(mesh, vertex_indices, self.uv2, 2)

        # normals
        if isinstance(self.normals, np.ndarray):
            mesh.normals_split_custom_set_from_vertices(self.normals)

        # weights
        if isinstance(self.weights, np.ndarray):
            for bone_id in range(self.weights.shape[0]):
                bone = self.weights[bone_id]
                nonzero = bone.nonzero()[0].tolist()
                vg = obj.vertex_groups.new(name=f"bone_{bone_id}")

                if len(nonzero) == 0:
                    continue

                [vg.add([idx], bone[idx], 'REPLACE') for idx in nonzero]

        bpy.context.scene.collection.objects.link(obj)
