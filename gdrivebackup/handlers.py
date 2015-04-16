import os
import json


class DataHandler(object):
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
    """Filters and parses downloaded folder and file meta data in
    preparation for writing to the filesystem. All file and folder data passed
    throughout an instance is in the form of a dict with drive id as key and
    meta data as value."""

    def __init__(self, json_path, file_meta, folder_meta, drive_root):
        DataHandler.__init__(self, json_path)
        self.drive_root = drive_root

        # Removes orphans :: is used as base data throughout filter object.
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

        # returned attributes when filter is called
        self.folders = ()  # a tuple containing two dicts (roots, children)
        self.dl_list = {}  # fid: {download url, file extension, title}

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
                raise Exception("file filter did not report any new or "
                                "changed items")
            to_parse = self.filtered

        for fid, v in to_parse.iteritems():
            export_type, ext = export_types.get(v["mimeType"])
            url = v["exportLinks"][export_type]

            self.dl_list[fid] = {
                'url': url,
                'ext': ext,
                'title': v["title"],
                'pid': v["parents"]["id"]
            }

    def _find_folders(self):
        """Searches for folders in two steps:
                1. Searches filtered files for their parent ids
                2. Recursively finds their parents up till root
        """

        # set local vars for recursive scope
        parented_folders = self.parented_folders
        root_id = self.drive_root
        roots = {}
        children = {}

        def find_parents(child_id, node_id):
            """Recursively create and find the parents of each folder and store
            store each parents child ids.

            :param child_id: id of previous folder id
            :param node_id: parent id of child_id set to be the current node
            """
            node = parented_folders.get(node_id)
            if not node:
                return None

            if not node.get("child"):
                node[u"child"] = []

            # update the parent with child
            node["child"].append(child_id)

            # catch roots with no files
            if node["parents"]["id"] == root_id:
                roots[node_id] = node

            elif node["parents"]["id"] != root_id:
                children[node_id] = node
                find_parents(node_id, node["parents"]["id"])

        # Step 1, find folders ids in filtered files resources
        for folder_data in self.parented_files.values():

            file_parent_id = folder_data["parents"]["id"]

            if file_parent_id in children or file_parent_id in roots:
                continue

            f = parented_folders.get(file_parent_id)  # get folder meta data
            if not f:  # skip accessible to anyone with url & not in My Drive
                continue

            if f["parents"]["id"] == self.drive_root:
                roots[file_parent_id] = f
            elif file_parent_id != self.drive_root:
                children[file_parent_id] = f  # leaf node
                # Step 2, find folders up till root
                find_parents(file_parent_id, f["parents"]["id"])

        self.children.update(children)
        self.roots.update(roots)

        self.folders = self.children, self.roots,

    def __call__(self):
        """Starts the filter using data downloaded via the DriveProvider.

        :returns:
        1.Dict: file id as key, and dict of export url, file extension and
        title as value.
        2.Dict: filtered folders fid as key and it's downloaded meta data as
        value."""
        print "Started filter"
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