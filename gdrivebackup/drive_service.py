import os.path
import json
from httplib2 import Http
import logging

from apiclient.discovery import build

from files_worker import DriveFolders, DriveFiles
from auth import Authorize

log = logging.getLogger('main.' + __name__)


def build_service():
    """returns a  drive service object with an authorized http object"""
    credentials = Authorize().get_credentials()
    http_auth = credentials.authorize(Http())
    return build('drive', 'v2', http=http_auth)


class DriveServiceWorker(object):
    def __init__(self):
        self.drive_service = build_service()
        self.drive_files_service = self.drive_service.files()

        self.STORAGE_PATH = '..\\file_store'
        self.JSON_STORAGE = os.path.join(self.STORAGE_PATH, 'meta.json')
        self.file_list = {}
        self.folder_list = {}

        self._get_file_list()

    # TODO get folder of each file
    def _get_file_list(self):
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
        self.file_list = {d['id']: DriveFiles(data=d) for d in items}
        print 'Downloaded file meta data...'

    def _store_file_list(self):
        with open(self.JSON_STORAGE, "wb") as f:
            json.dump({fid: obj.__dict__ for fid, obj in
                       self.file_list.iteritems()}, f)

    def file_list_from_storage(self):
        with open(self.JSON_STORAGE, 'r') as f:
            f = json.load(f)
        return f

    def is_downloadable(self, k, v, stored_file_meta):
        if k not in stored_file_meta:
            log.info("Found item new item: {}", self.file_list[k].title)
            return True
        if v.modifiedDate != stored_file_meta[k]['modifiedDate']:
            log.info("Found item change in: %s", v.title)
            return True

    def filter_download_list(self):
        try:
            stored_file_meta = self.file_list_from_storage()
            store_len = len(stored_file_meta)
            log.info('Json File Loaded \n %s entries found in meta.json',
                     store_len)
        except:
            raise
        return {k: v for k, v in self.file_list.iteritems()
                if self.is_downloadable(k, v, stored_file_meta)}

    def write_to_fs(self, not_storage, item, content, dl_count, wr_count):
        f_name = os.path.join(self.STORAGE_PATH, item.title + "." + item.ext)
        if not_storage and os.path.exists(f_name):
            log.error('File %s already exists', f_name)
            dl_count -= 1
        else:
            with open(f_name, 'wb') as f:
                    f.write(content)
                    wr_count += 1
        return dl_count, wr_count

    def download_files(self):
        # Get the proper list of files to download
        export_list = self.file_list
        not_storage = True
        if os.path.isfile(self.JSON_STORAGE):
            export_list = self.filter_download_list()
            log.info('Getting files meta from storage')
            not_storage = False
        else:
            self._store_file_list()
        log.info('Number of items found: %s', len(export_list))

        dl_count = 0
        wr_count = 0
        if len(export_list) != 0:
            print 'Starting Download of {} files...'.format(len(export_list))

        for item in export_list.values():
            log.debug('Try download \#%s File Name: %s', dl_count, item.title)

            try:
                # Download the file using an authorized http object
                response, content = self.drive_service._http.request(item.eurl)
                log.debug('status: %s', response.status)
                dl_count += 1
                payload = [not_storage, item, content, dl_count, wr_count]
                dl_count, wr_count = self.write_to_fs(*payload)
            except Exception, e:
                log.exception('%s', e)

        log.info('%s files downloaded successfully', dl_count)
        log.info('%s files writen successfully', wr_count)