import time
import ctypes
import numpy as np
import bpy
import bmesh

from api_egres import DllReadMeshBin, MeshReadWriteFlags, PtrToNp, PtrListToPtrArray

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

    def LoadMesh(self, mesh_path):
        total = 9
        verts = np.zeros(1, dtype=np.float32)
        tris = np.zeros(1, dtype=np.float32)
        uv1 = np.zeros(1, dtype=np.float32)
        uv2 = np.zeros(1, dtype=np.float32)
        colors = np.zeros(1, dtype=np.uint8)
        normals = np.zeros(1, dtype=np.float32)
        tangents = np.zeros(1, dtype=np.float32)
        weights = np.zeros(1, dtype=np.float32)

        sizes = np.zeros(total, dtype=np.int64).ctypes.data_as(ctypes.POINTER(ctypes.c_size_t))

        ptrs = [
            tris.ctypes.data_as(ctypes.POINTER(ctypes.c_void_p)),
            verts.ctypes.data_as(ctypes.POINTER(ctypes.c_void_p)),
            uv1.ctypes.data_as(ctypes.POINTER(ctypes.c_void_p)),
            uv2.ctypes.data_as(ctypes.POINTER(ctypes.c_void_p)),
            colors.ctypes.data_as(ctypes.POINTER(ctypes.c_void_p)),
            normals.ctypes.data_as(ctypes.POINTER(ctypes.c_void_p)),
            tangents.ctypes.data_as(ctypes.POINTER(ctypes.c_void_p)),
            weights.ctypes.data_as(ctypes.POINTER(ctypes.c_void_p)),
        ]
        ptrs = PtrListToPtrArray(ptrs)

        DllReadMeshBin(mesh_path.encode('utf-8'), ctypes.byref(self.flags), ptrs, sizes)

        size_buf = PtrToNp(sizes, ctypes.c_size_t, np.int64, total)

        if size_buf[0] != 0:
            self.tris = PtrToNp(ptrs[0], ctypes.c_uint16, np.uint16, size_buf[0]).reshape(-1, 3)

        if size_buf[1] != 0:
            self.verts = PtrToNp(ptrs[1], ctypes.c_float, np.float32, size_buf[1]).reshape(-1, 3)

        if size_buf[2] != 0:
            self.uv1 = PtrToNp(ptrs[2], ctypes.c_float, np.float32, size_buf[2]).reshape(-1, 2)

        if size_buf[3] != 0:
            self.uv2 = PtrToNp(ptrs[3], ctypes.c_float, np.float32, size_buf[3]).reshape(-1, 2)

        if size_buf[4] != 0:
            self.colors = PtrToNp(ptrs[4], ctypes.c_uint8, np.uint8, size_buf[4]).reshape(-1, 4)

        if size_buf[5] != 0:
            normals_buf = PtrToNp(ptrs[5], ctypes.c_float, np.float32, size_buf[5]).reshape(-1, 3)
            self.normals = normals_buf / np.linalg.norm(normals_buf, axis=1)[:, np.newaxis]

        if size_buf[6] != 0:
            self.tangents = PtrToNp(ptrs[6], ctypes.c_float, np.float32, size_buf[6]).reshape(-1, 3)

        if size_buf[8] != 0:
            self.weights = PtrToNp(ptrs[7], ctypes.c_float, np.float32, size_buf[8] * int(size_buf[1] / 3)).reshape(
                size_buf[8], -1)

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