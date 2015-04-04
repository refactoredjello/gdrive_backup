import os
import json

from folders import Folder


class DataHandler(object):
    def __init__(self, JSON_PATH, file_meta, folder_meta, drive_root):
        self.drive_root = drive_root
        self.file_meta = file_meta
        self.folder_meta = folder_meta
        self.data_local = os.path.isfile(JSON_PATH)
        self.json_path = JSON_PATH

    def to_json(self):
        with open(self.json_path, 'wb') as f:
            json.dump(self.file_meta, f, indent=0)

    def from_json(self):
        with open(self.json_path, 'r') as f:
            return json.load(f)




class DataFilter(DataHandler):
    """
    Handlers for filtering files and folders.  It will find new or changed
    files from a list of drive files, and folders which are found in a
    file's meta data.

    :param drive_meta: a list of drive files as dicts
    """
    def __init__(self, *args):
        DataHandler.__init__(self, *args)

        self.filtered = ()
        self.folders = {} # filtered folders as objects
        self.stored = {}

    def _is_new(self, fid):
        return fid not in self.stored.keys()

    def _is_changed(self, fid, data):
        stored = self.stored[fid]
        return data["modifiedDate"] != stored["modifiedDate"]

    def _filter(self):
        """filters out files which have been changed or are new since last
        download"""
        for fid, data in self.file_meta.iteritems():
            if self._is_new(fid):
                self.filtered += (fid, data),

            elif self._is_changed(fid, data):
                self.filtered += (fid, data),

    def _build_folders(self):
        """Create a dict of folder objects if folder is found to contain a
        google format document, sheet, or slide.

        Note: Discards folders which have no parent or not root. This may mean
        folders shared with you.
        """
        roots = []
        children = []
        for item in self.file_meta.values():
            parents = item["parents"]
            if not parents:
                continue

            fid, is_root = parents["id"], parents["isRoot"]
            if (fid in children or roots) or fid == self.drive_root:
                continue

            if is_root:
                roots.append(fid)
            elif fid in self.folder_meta.keys():
                children.append(fid)

        for fid in roots:
            folder = self.folder_meta[fid]
            title = folder["title"]
            self.folders[fid] = Folder(fid, None, title, True)

        for fid in children:
            folder = self.folder_meta[fid]
            title = folder["title"]
            parents = folder["parents"]
            self.folders[fid] = Folder(fid, parents, title, False)

    def __call__(self):
        if not self.data_local:
            self.to_json()
            return None

        if self.data_local:
            self.stored = self.from_json()
            self._filter()
            self._build_folders()
            return self.filtered, self.folders







