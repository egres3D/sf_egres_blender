import ctypes
import os

import numpy as np


class RawBuffer(ctypes.Structure):
    _fields_ = [
        ("ptr", ctypes.c_void_p),
        ("len", ctypes.c_size_t),
    ]

scr_path = os.path.dirname(__file__)
dll = ctypes.CDLL(os.path.join(scr_path, "lib_egres.dll"))

DllReadMeshBin = dll.LoadMesh
DllReadMeshBin.argtypes = [
    ctypes.c_char_p,
    ctypes.c_void_p
]
DllReadMeshBin.restype = ctypes.c_void_p

DllFreeMesh = dll.FreeMeshFile
DllFreeMesh.argtypes = [
    ctypes.c_void_p
]
DllFreeMesh.restype = ctypes.c_void_p

ArchiveIterFree = dll.arch_iter_free
ArchiveIterFree.argtypes = [
        ctypes.c_void_p
    ]
ArchiveIterFree.restype = ctypes.c_void_p

ArchiveIterNext = dll.arch_iter_next
ArchiveIterNext.argtypes = [
    ctypes.c_void_p
]
ArchiveIterNext.restype = ctypes.c_char_p

ArchiveIterNew = dll.arch_iter_new
ArchiveIterNew.restype = ctypes.c_void_p

ArchiveReadMesh = dll.LoadMeshFromArchive
ArchiveReadMesh.argtypes = [
    ctypes.c_char_p,
    ctypes.c_char_p,
    ctypes.c_void_p
]
ArchiveReadMesh.restype = ctypes.c_void_p

class MeshReadWriteFlags(ctypes.Structure):
    _fields_ = [
        ("TRIS", ctypes.c_uint8, 1),
        ("VERTS", ctypes.c_uint8, 1),
        ("UV", ctypes.c_uint8, 1),
        ("COLOR", ctypes.c_uint8, 1),
        ("NORMALS", ctypes.c_uint8, 1),
        ("TANGENTS", ctypes.c_uint8, 1),
        ("WEIGHTS", ctypes.c_uint8, 1),
        ("LOD", ctypes.c_uint8, 1),
        ("MESHLETS", ctypes.c_uint8, 1),
    ]

def PtrListToPtrArray(py_list):
    ptr = (ctypes.POINTER(ctypes.c_void_p) * len(py_list))()
    for i, l in enumerate(py_list):
        ptr[i] = l
    return ptr

def PtrToNp(ptr, c_data_type, np_data_type, size):
    buf = ctypes.cast(ptr, ctypes.POINTER(c_data_type * size))
    array = np.ctypeslib.as_array(buf.contents).astype(np_data_type)
    return array
