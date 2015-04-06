import os
import json

class DataHandler(object):
    """All file and folder data passed throughout the obj is in the form of a
    dict with drive id as key and meta data as value. """

    def __init__(self, json_path, file_meta, folder_meta, drive_root):
        self.drive_root = drive_root
        self.file_meta = file_meta
        self.folder_meta = folder_meta
        self.data_local = os.path.isfile(json_path)
        self.json_path = json_path

    def to_json(self, files_dump):
        with open(self.json_path, 'wb') as f:
            json.dump(files_dump, f, indent=0)

    def from_json(self):
        with open(self.json_path, 'r') as f:
            return json.load(f)


class DataFilter(DataHandler):
    """Filters and parses downloaded folder and file data in preparation for
    writing to the filesystem. """

    def __init__(self, *args):
        DataHandler.__init__(self, *args)

        self.filtered = ()
        self.folders = ()
        self.stored = {}

        # store files and folders which have parents
        r = self._remove_orphans
        self.parented_files = r(self.file_meta)
        self.parented_folders = r(self.folder_meta)

    def _is_new(self, fid):
        return fid not in self.stored.keys()

    def _is_changed(self, fid, data):
        stored = self.stored[fid]
        return data["modifiedDate"] != stored["modifiedDate"]

    def _filter_files(self):
        """Filters out files which have been changed or are new since last
        download."""
        for fid, v in self.parented_files.iteritems():
            if self._is_new(fid):
                print 'Found new file: ', v["title"]
                self.filtered += (fid, v),

            elif self._is_changed(fid, v):
                print 'Found changed file: ', v["title"]
                self.filtered += (fid, v),

    @staticmethod
    def _remove_orphans(meta):
        return {fid: v for fid, v in meta.iteritems() if v.get("parents")}

    def _find_parents(self, folder):
        raise NotImplementedError

    def _find_folders(self):
        """Creates two dicts, a dict of roots and a dict of children that
        are found in a file's meta data.

        Note: Discards folders which have no parent or is not a root. This may
        mean folders shared with you.
        """

        roots = {}
        children = {}
        for item in self.parented_files.values():
            parents = item["parents"]

            fid, is_root = parents["id"], parents["isRoot"]
            if (fid in children or roots) or fid == self.drive_root:
                continue

            folder = self.parented_folders.get(fid)
            if is_root:
                roots[fid] = folder
            elif folder:
                children[fid] = folder

        self.folders = children, roots,
        self._find_parents()

    def __call__(self):
        """
        Starts the filter using data from downloaded via the DriveProvider.

        :returns: two dicts, 1.files 2.folders
        """
        if not self.data_local:  # filter on first run
            print "First run!"
            self.to_json(self.parented_files)
            self._find_folders()
            return self.parented_files, self.folders

        if self.data_local:  # filter with local data to compare
            print "Using json store!"
            self.stored = self.from_json()
            self._filter_files()
            self._find_folders()
            return self.filtered, self.folders