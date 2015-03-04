#Create tests
#TODO work out why there are duplicates on first download

from os import path
import json

from builder import BuildService


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
            print 'setting DriveFile attributes from json file meta.json'

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


class DriveFilesWorker(object):
    def __init__(self):
        self.drive_service = BuildService().service
        self.drive_files_service = self.drive_service.files()

        self.STORAGE_PATH = 'file_store'
        self.JSON_STORAGE = path.join(self.STORAGE_PATH, 'meta.json')
        self.file_list = self._get_file_list()

    def _get_file_list(self):

        """sets file_list attr as a dict of file meta data which match
        payload and their meta data as a dict"""

        payload_types = (
            "trashed = false"
            "and ("
                "mimeType = 'application/vnd.google-apps.document'"
                "or mimeType = 'application/vnd.google-apps.presentation'"
                "or mimeType = 'application/vnd.google-apps.spreadsheet'"
                ")"
        )

        payload = {"q": payload_types}
        items = self.drive_files_service.list(**payload).execute()['items']
        return {d['id']: DriveFile(data=d) for d in items}

    def _store_file_list(self):
        with open(self.JSON_STORAGE, "wb") as f:
            json.dump({fid: obj.__dict__ for fid, obj in
                       self.file_list.iteritems()}, f)

    def file_list_from_storage(self):
        with open(self.JSON_STORAGE, 'r') as f:
            return json.load(f)

    def is_downloadable(self, k, v, stored_file_meta):
        if k not in stored_file_meta:
            print "Found item new item: {}".format(self.file_list[k].title)
            return True
        if v.modifiedDate != stored_file_meta[k]['modifiedDate']:
            print "Found item change in: {}".format(v.title)
            return True

    def filter_download_list(self):
        # TODO handle deleted files they will cause a key error
        try:
            stored_file_meta = self.file_list_from_storage()
            print "File Loaded"
            print "{} entries found in meta.json".format(len(
                stored_file_meta))
        except:
            raise
        return {k: v for k, v in self.file_list.iteritems()
                if self.is_downloadable(k, v, stored_file_meta)}

    def download_files(self):
        export_list = self.file_list
        if path.isfile(self.JSON_STORAGE):
            export_list = self.filter_download_list()
            #TODO update meta.json if new files downloaded
        else:
            self._store_file_list()
            print 'Number of items stored:{}'.format(len(export_list))

        download_count = 0
        for item in export_list.values():
            download_count += 1
            print "Download #{} Name: {}".format(download_count, item.title)

            response, content = self.drive_service._http.request(item.eurl)
            print response.status

            f_name = path.join(self.STORAGE_PATH, item.title + "." + item.ext)
            with open(f_name, 'wb') as f:
                f.write(content)

        print '{} Files downloaded successfully'.format(download_count)



DF = DriveFilesWorker()
DF.download_files()



