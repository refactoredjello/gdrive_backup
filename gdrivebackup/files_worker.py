class DriveFile(object):
    def __init__(self, json_flag=False, data={}):
        """
        :param data: file meta data as a dictionary
        """
        self.title = ''
        self.modifiedDate = ''
        self.id = ''
        self.exportLinks = {}
        self.mimeType = ''
        self.trash = ''
        self.eurl = ''
        self.ext = ''

        self.parse_data(json_flag, data)

    def parse_data(self, json_flag=False, data={}):
        if json_flag:
            pass
            #log.debug('setting DriveFile attributes from json file '
            #'meta.json')

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

        self.title = data['title'].translate({ord(c): u'_' for c in u'/|/'})
        self.modifiedDate = data['modifiedDate']
        self.id = data['id']

        #list of export url file options
        self.exportLinks = data['exportLinks']
        self.mimeType = data['mimeType']

        #Get exporting data and file extension
        export_key = export_type_dict[self.mimeType]
        self.eurl = self.exportLinks[export_key[0]]
        self.ext = export_key[1]

        #Depcrated, trashy items are filtered at first file list request
        if not json_flag:
            self.trash = data['labels']['trashed']


# DF = DriveFilesWorker()
#DF.download_files()



