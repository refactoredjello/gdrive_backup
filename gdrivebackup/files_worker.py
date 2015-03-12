import logging

log = logging.getLogger('main.' + __name__)


class DriveTypes(object):
    def __init__(self, data):
        """
        :param data: google drive file meta data
        """
        self.title = data['title'].translate({ord(c): u'_' for c in u'/|/'})
        self.modifiedDate = data['modifiedDate']
        self.id = data['id']
        self.exportLinks = {}
        self.mimeType = data['mimeType']
        self.trash = ''
        self.parents = data['parents']


class DriveFolders(DriveTypes):
    pass

class DriveFiles(DriveTypes):
    def __init__(self, data):
        self.data = data
        DriveTypes.__init__(self, self.data)
        self.exportLinks = data['exportLinks']
        self.eurl = ''
        self.ext = ''
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
        #Get exporting data and file extension
        export_key = export_type_dict[self.mimeType]
        self.eurl = self.exportLinks[export_key[0]]
        self.ext = export_key[1]


