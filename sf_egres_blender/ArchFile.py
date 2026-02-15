import ctypes
import os.path

import api_egres


class ArchiveItem:
    def __init__(self, full_path):
        self.full_path = full_path

        f = os.path.basename(full_path).rpartition(".")
        self.filename = f[0]
        self.extension = f[2]

class BArchive:
    def __init__(self, path):
        self.path = path
        self.page = 0
        self.page_size = 20
        self.archive_items = []

    def loadPaths(self):
        it = api_egres.ArchiveIterNew(self.path.encode('utf-8'))
        result = []

        while True:
            s = api_egres.ArchiveIterNext(it)
            if not s:
                break
            result.append(
                ArchiveItem(ctypes.string_at(s).decode('utf-8'))
            )

        api_egres.ArchiveIterFree(it)

        self.archive_items = result
