class Folder(object):
    folders = {}

    def __init__(self, fid="", parents=None, title="", is_root=False):
        self.fid = fid
        if parents:
            self.parent = parents["id"]
        else:
            self.parent = []
        self.title = title
        self._child = []
        self.is_root = is_root

    @property
    def child(self):
        if self._child:
            return self._child

    @child.setter
    def child(self, child_id):
        self._child.append(child_id)

    @classmethod
    def make_folders(cls, children, roots):
        """Creates folder objects found by the DataFilter"""
        for fid, folder in roots.iteritems():
            title = folder["title"]
            cls.folders[fid] = Folder(fid, None, title, True)

        for fid, folder in children.iteritems():
            title = folder["title"]
            parents = folder["parents"]
            cls.folders[fid] = Folder(fid, parents, title, False)

        return cls.folders