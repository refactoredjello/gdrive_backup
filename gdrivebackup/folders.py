from os import path
from os import mkdir
from os import makedirs


class Folder(object):
    """ Folder objects and methods, used to create the folder tree"""
    folders = {}

    def __init__(self, fid="", pid=None, title="", is_root=False):
        self.fid = fid
        self.pid = pid
        self.title = title
        self.is_root = is_root  # relative to drive_root :: "My Drive"
        self.children = []

    @property
    def child(self):
        if self.children:
            return self.children

    @child.setter
    def child(self, child_id):
        self.children.append(child_id)

    @classmethod
    def make_folders(cls, children, roots):
        """Creates folder objects found by the DataFilter"""
        for fid, folder in roots.iteritems():
            title = folder["title"]
            cls.folders[fid] = Folder(fid, None, title, True)

        for fid, folder in children.iteritems():
            title = folder["title"]
            pid = folder["parents"]["id"]

            # update the parent folder children
            parent = cls.folders.get(pid)
            parent.child = fid
            cls.folders[pid] = parent

            cls.folders[fid] = Folder(fid, pid, title, False)

        return cls.folders

    @classmethod
    def make_tree(cls, storage_path):
        folders = cls.folders  # localized for recursive scope
        path_tree = []

        def make_paths(folder):
            parent = folders.get(folder.pid)
            if not parent:
                path_tree.append(folder.title)
                return None
            elif parent:
                path_tree.append(folder.title)
                make_paths(parent)

        for folder_obj in cls.folders.values():
            child = folder_obj.child
            pid = folder_obj.pid
            title = folder_obj.title

            if not child and not pid:  # mk roots with no children
                folder_path = path.join(storage_path, title)
                mkdir(folder_path)

            elif not child and pid:  # mk tree starting with leafs
                make_paths(folder_obj)
                leaf_path = path.join(storage_path, *path_tree[-1::-1])
                makedirs(leaf_path)

