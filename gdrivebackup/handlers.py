import os
import json

class DataHandler(object):
    """All file and folder data passed throughout the obj is in the form of a
    dict with drive id as key and meta data as value. """

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
    writing to the filesystem. """

    def __init__(self, json_path, file_meta, folder_meta, drive_root):
        DataHandler.__init__(self, json_path)

        self.filtered = ()
        self.folders = () # a tuple containing two dicts (roots, children)
        self.stored = {}
        self.dl_list = {}  # key : fid, value: {download url, file extension}

        # store only files and folders which have parents
        self.parented_files = self._remove_orphans(file_meta)
        self.parented_folders = self._remove_orphans(folder_meta)
        self.drive_root = drive_root

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
    def _remove_orphans(meta={}):
        return {fid: v for fid, v in meta.iteritems() if v.get("parents")}

    def _find_parents(self, folder):
        pass

    def _find_folders(self):
        """Creates a tuple of two dicts, a dict of roots and a dict of
        children that are found in a file's meta data."""

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
        if not self.data_local:
            to_parse = self.filtered

        for fid, v in to_parse.iteritems():
            export_type, ext = export_types.get(v["mimeType"])
            url = v["exportLinks"][export_type]

            self.dl_list[fid] = {'url': url, 'ext': ext, 'title': v["title"]}

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