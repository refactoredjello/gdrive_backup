from os import path
import json

from builder import BuildService

class DriveFiles(object):
    def __init__(self):
        self.drive_service = BuildService().service
        self.drive_files_service = self.drive_service.files()
        self.export_type_dict = {
            'application/vnd.google-apps.document':
                ('application/vnd.openxmlformats-officedocument.wordprocessingml'
                '.document', 'docx'),
            'application/vnd.google-apps.spreadsheet':
                ('application/vnd.openxmlformats-officedocument.spreadsheetml'
                '.sheet','xlsx')
        }
        self.STORAGE_PATH = "file_store"
        self.JSON_STORAGE = path.join(self.STORAGE_PATH, 'meta.json')
        self.file_list = {}

    def _get_file_list(self):
        #TODO DO NOT GET FILES FROM TRASH
        """sets file_list attr as a dict of file meta data which match
        payload and their meta  data as a dict"""

        payload_types = (
        "mimeType = 'application/vnd.google-apps.document'"
        "or mimeType = 'application/vnd.google-apps.presentation'"
        "or mimeType = 'application/vnd.google-apps.spreadsheet'"
        )
        payload = {"q": payload_types}
        items = self.drive_files_service.list(**payload).execute()['items']

        self.file_list = {item.pop('id'): item for item in items}

    def _store_file_list(self):
        with open(self.JSON_STORAGE, "wb") as f:
            json.dump(self.file_list, f)

    def file_list_from_storage(self):
        with open(self.JSON_STORAGE, 'r') as f:
            return json.load(f)

    def filter_download_list(self):
        # TODO handle deleted files they will cause a key error
        try:
            stored_file_meta = self.file_list_from_storage()
        except:
            raise
        return {k: v for k, v in stored_file_meta if v['modifiedDate'] !=
                self.file_list[k]['modifiedDate']}

    def get_export_links(self, file_meta):
        v = file_meta
        links = v['exportLinks']
        export_type = self.export_type_dict[v['mimeType']]
        export_link = links[export_type[0]]
        extension = export_type[1]

        # need to map unicode  to none if using translate
        replace_me = u'/|/'
        trans_table = {ord(c): u'_' for c in replace_me}
        return v['title'].translate(trans_table), export_link, extension

    def download_files(self):
        self._get_file_list()
        export_list = self.file_list

        if path.isfile(self.JSON_STORAGE):
            export_list = self.filter_download_list()

        self._store_file_list()

        for item in export_list.values():
            title, eurl, extension = self.get_export_links(item)
            response, content = self.drive_service._http.request(eurl)

            print response.status

            file_name = path.join(self.STORAGE_PATH, title + "." + extension)
            with open(file_name, 'wb') as f:
                f.write(content)


#TODO test this when you change a file


DF = DriveFiles()
DF.download_files()
#print len(DriveFiles().get_export_links())
#DF.store_file_list()
#pprint(DF.file_list_from_storage())


