from os import path
import json
from httplib2 import Http

from apiclient.discovery import build

from files_worker import DriveFile
from auth import Authorize


def build_service():
    """build the drive service with an authorized http object"""
    credentials = Authorize().get_credentials()
    http_auth = credentials.authorize(Http())
    return build('drive', 'v2', http=http_auth)


class DriveServiceWorker(object):
    def __init__(self):
        self.drive_service = build_service()
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
        print path.realpath(self.JSON_STORAGE)
        with open(self.JSON_STORAGE, "wb") as f:
            json.dump({fid: obj.__dict__ for fid, obj in
                       self.file_list.iteritems()}, f)

    def file_list_from_storage(self):
        with open(self.JSON_STORAGE, 'r') as f:
            f = json.load(f)
        return f

    def is_downloadable(self, k, v, stored_file_meta):
        if k not in stored_file_meta:
            #log.info("Found item new item: {}", self.file_list[k].title)
            return True
        if v.modifiedDate != stored_file_meta[k]['modifiedDate']:
            #log.info("Found item change in: %s", v.title)
            return True

    def filter_download_list(self):
        try:
            stored_file_meta = self.file_list_from_storage()
            store_len = len(stored_file_meta)
            #log.info('Json File Loaded \n %s entries found in meta.json',
                        #store_len)
        except:
            raise
        return {k: v for k, v in self.file_list.iteritems()
                if self.is_downloadable(k, v, stored_file_meta)}

    def download_files(self):
        export_list = self.file_list
        if path.isfile(self.JSON_STORAGE):
            export_list = self.filter_download_list()

        else:
            self._store_file_list()
            #log.info('Number of items stored: %s', len(export_list))

        download_count = 0
        for item in export_list.values():
            download_count += 1
            #log.debug('Download \#%s Name: %s', download_count, item.title)

            response, content = self.drive_service._http.request(item.eurl)
            #log.debug('response.status')
            f_name = path.join(self.STORAGE_PATH, item.title + "." + item.ext)
            with open(f_name, 'wb') as f:
                f.write(content)

        #log.info('%s files downloaded successfully', download_count)