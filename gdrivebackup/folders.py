class Folder(object):
    """ Folder objects and methods, used to create the folder directory
    tree"""
    folders = {}

    def __init__(self, fid="", pid=None, title="", is_root=False):
        self.fid = fid
        self.parent = pid
        self.title = title
        self.is_root = is_root
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

            # update the parent
            parent = cls.folders.get(pid)
            parent.child = fid
            cls.folders[pid] = parent

            cls.folders[fid] = Folder(fid, pid, title, False)

        return cls.folders