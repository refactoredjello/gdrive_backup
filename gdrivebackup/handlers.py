import os
import json


class DataHandler(object):
    """All file and folder data passed throughout the instance is in the form
    of a dict with drive id as key and meta data as value. """

    def __init__(self, json_path):
        self.data_local = os.path.isfile(json_path)
        self.json_path = json_path

    def to_json(self, to_dump):
        with open(self.json_path, 'wb') as f:
            json.dump(to_dump, f, indent=0)

    def from_json(self):
        with open(self.json_path, 'r') as f:
            return json.load(f)


class DataFilter(DataHandler):
    """Filters and parses downloaded folder and file data in preparation for
    writing to the filesystem.
    """

    def __init__(self, json_path, file_meta, folder_meta, drive_root):
        DataHandler.__init__(self, json_path)
        self.drive_root = drive_root

        # Removes orphans, and is used as base data throughout filter object.
        self.parented_folders = {fid: v for fid, v in folder_meta.iteritems()
                                 if v.get("parents")}
        self.parented_files = {fid: v for fid, v in file_meta.iteritems() if
                               v.get("parents")}
        self._shared_orphans()  # removes orphans shared via link

        # secondary filter stores
        self.filtered = ()
        self.stored = {}
        self.children = {}
        self.roots = {}

        # returned attributes if instance is called
        self.folders = () # a tuple containing two dicts (roots, children)
        self.dl_list = {}  # key : fid, value: {download url, file extension}

    def _shared_orphans(self):
        for fid, v in self.parented_files.copy().iteritems():
            pid = v["parents"]["id"]
            if pid not in self.parented_folders and pid != self.drive_root:
                self.parented_files.pop(fid)

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

    def _get_export_links(self):
        export_types = {
            'application/vnd.google-apps.document': (
                'application/vnd.openxmlformats-officedocument.wordprocessingml'
                '.document', 'docx'
            ),
            'application/vnd.google-apps.spreadsheet': (
                'application/vnd.openxmlformats-officedocument.spreadsheetml'
                '.sheet', 'xlsx'
            ),
            'application/vnd.google-apps.presentation': (
                'application/vnd.openxmlformats-officedocument.presentationml'
                '.presentation', 'pptx'
            )

        }

        to_parse = self.parented_files
        if self.data_local:
            if not self.filtered:
                raise Exception("self.filter does not have any new or changed "
                                "items")
            to_parse = self.filtered

        for fid, v in to_parse.iteritems():
            export_type, ext = export_types.get(v["mimeType"])
            url = v["exportLinks"][export_type]

            self.dl_list[fid] = {'url': url, 'ext': ext, 'title': v["title"]}

    def _find_folders(self):
        """Creates a tuple with two dicts, one of root folders and one of
        children, either of which were found in a file's meta data."""

        parented_folders = self.parented_folders

        def find_parents(node_id, drive_root):

            current_node = parented_folders.get(node_id)
            parent_id = current_node["parents"]["id"]

            if parent_id == drive_root:
                return [node_id]
            else:
                return [node_id] + find_parents(parent_id, drive_root)

        # find all the folders found in a file meta
        for item in self.parented_files.values():
            parents = item["parents"]
            pid, is_root = parents["id"], parents["isRoot"]

            if (pid in self.children or self.roots) or pid == self.drive_root:
                continue

            folder = parented_folders.get(pid)
            # skip items shared with you via link
            if not folder:
                continue

            if is_root:
                self.roots[pid] = folder
            else:
                self.children[pid] = folder

        # find the remaining parent folders up to drive root
        remaining = []
        for folder in self.children.copy().values():
            p = folder["parents"]["id"]
            if p == self.drive_root:
                continue
            new_folders = (find_parents(p, self.drive_root))
            if new_folders:
                remaining += new_folders
        print remaining

        self.folders = self.children, self.roots,

    def __call__(self):
        """
        Starts the filter using data downloaded via the DriveProvider.

        :returns:
        1.Dict: file id as key, and dict of export url, file extension and
        title as value.
        2.Dict: filtered folders fid as key and it's downloaded meta data as
        value.
        """
        if not self.data_local:  # filter on first run
            print "First run!"
            self.to_json(self.parented_files)

        if self.data_local:  # filter with local json
            print "Using json store!"
            self.stored = self.from_json()
            self._filter_files()

        self._get_export_links()
        self._find_folders()

        return self.dl_list, self.folders