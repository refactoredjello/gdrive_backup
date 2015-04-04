class Folder(object):
    def __init__(self, fid="", parents="", title="", is_root=False):
        self.fid = fid
        self.parent = parents["id"]
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

    @staticmethod
    def make_nodes(folders):
        for folder in folders:
            if folder.is_root:
                continue
            for other in folders:
                if other == folder:
                    continue
                if folder.id == other.parent:
                    folder.child = other





