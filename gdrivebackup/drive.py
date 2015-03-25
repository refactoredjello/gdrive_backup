import logging

log = logging.getLogger('main.' + __name__)


class DriveTypes(object):
    def __init__(self, id="", title="", modifiedDate="", mimeType="",
                 parents=[], labels=[]):

        self.id = id
        self.title = title.translate({ord(c): u'_' for c in u'/|/'})
        self.modifiedDate = modifiedDate
        self.mimeType = mimeType
        self.orphaned = False

        self.labels = labels

        if not parents:
            self.parents = parents
            self.orphaned = True  # locally generated field
        else:
            self.parents = parents[0]


class DriveFiles(DriveTypes):
    def __init__(self, exportLinks=[], **kwargs):
        DriveTypes.__init__(self, **kwargs)
        self.exportLinks = exportLinks
        self.eurl = ''  # locally generated field
        self.ext = ''  # locally generated field
        self._get_export_links()

    def _get_export_links(self):
        export_type_dict = {
            'application/vnd.google-apps.document': (
                'application/vnd.openxmlformats-officedocument.wordprocessingml'
                '.document', 'docx'
            ),
            'application/vnd.google-apps.spreadsheet': (
                'application/vnd.openxmlformats-officedocument.spreadsheetml'
                '.sheet', 'xlsx'
            )
        }
        # parse for exporting link and file extension
        export_key = export_type_dict[self.mimeType]
        self.eurl = self.exportLinks[export_key[0]]
        self.ext = export_key[1]


class DriveFolders(DriveTypes):
    pass