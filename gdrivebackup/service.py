# TODO test updating json file - use a max results list or update actual
# drive files
import os
import json
import logging

from .drive import DriveFolders, DriveFiles



DEBUG_FLAG = False
log = logging.getLogger("main." + __name__)


def ensure_dir(directories):
    for d in directories:
        if not os.path.exists(d):
            os.mkdir(d)


class DriveWorker(object):
    def __init__(self, service):
        self.SERVICE = service
        self.FILES_SERVICE = service.files()
        self.STORAGE_PATH = "..\\file_store"
        self.ORPHANED_PATH = self.STORAGE_PATH + "\\orphaned"
        self.JSON_STORAGE = os.path.join(self.STORAGE_PATH, "meta.json")
        self.file_list = self._get_file_list()
        self.folder_list = self._get_folder_list()
        ensure_dir([self.STORAGE_PATH, self.ORPHANED_PATH])

    def _get_drive_list(self, payload_query):
        payload = {"q": 'trashed=false and ' + payload_query,
                   "fields": 'items(id,title,exportLinks,'
                             'mimeType,modifiedDate,labels,'
                             'parents(id,isRoot))'
                   }

        if DEBUG_FLAG:
            payload["maxResults"] = 10

        items = self.FILES_SERVICE.list(**payload).execute()["items"]
        return items

    def _get_folder_list(self):
        """ Returns a dict of folders objects with their drive id as key
        only if the folder is found in a downloadable file"""
        pl_q = "mimeType = 'application/vnd.google-apps.folder'"
        folders = {d["id"]: DriveFolders(data=d) for d in
                   self._get_drive_list(pl_q)}
        file_folders = [f.parents["id"] for f in self.file_list.values()
                        if f.parents]
        return {fid: obj for fid, obj in folders.iteritems()
                if id in file_folders}

    def _get_file_list(self):
        payload_query = (
            "("
            "mimeType = 'application/vnd.google-apps.document'"
            "or mimeType = 'application/vnd.google-apps.presentation'"
            "or mimeType = 'application/vnd.google-apps.spreadsheet'"
            ")"
        )
        items = self._get_drive_list(payload_query)
        return {d["id"]: DriveFiles(data=d) for d in items}

    def _store_file_list(self):
        with open(self.JSON_STORAGE, 'wb') as f:
            json.dump({fid: obj.__dict__ for fid, obj in
                       self.file_list.iteritems()}, f)

    def file_list_from_storage(self):
        with open(self.JSON_STORAGE, 'r') as f:
            return json.load(f)

    def _update_json(self, new_files):
        json_data = self.file_list_from_storage()
        for fid, obj in new_files.iteritems():
            new_meta = obj.__dict__
            current_meta = json_data[fid]
            log.debug("Current Data: %s", current_meta)
            log.debug("New Meta: %s", new_meta)
            if fid not in json_data:
                json_data[fid] = new_meta
            elif new_meta["modifiedDate"] != current_meta["modifiedDate"]:
                json_data[fid]["modifiedDate"] = new_meta["modifiedDate"]

    def is_downloadable(self, k, v, stored_file_meta):
        if k not in stored_file_meta:
            log.info('Found  new item: %s', v.title)
            return True
        if v.modifiedDate != stored_file_meta[k]["modifiedDate"]:
            log.info('Found item change in: %s', v.title)
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

    def write_to_fs(self, not_storage, item, content, wr_count):
        storage_path = self.STORAGE_PATH
        if item.orphaned:
            storage_path = self.ORPHANED_PATH
        f_name = os.path.join(storage_path, item.title + "." + item.ext)
        if not_storage and os.path.exists(f_name):
            log.error('File %s already exists', f_name)
        else:
            with open(f_name, "wb") as f:
                f.write(content)
                wr_count += 1
        return wr_count

    def download_files(self):
        # Get the proper list of files to download
        export_list = self.file_list
        not_storage = True
        if os.path.isfile(self.JSON_STORAGE):
            export_list = self.filter_download_list()
            self._update_json(export_list)
            log.info('Getting files meta from storage')
            not_storage = False
        else:
            self._store_file_list()
        log.info('Number of items found: %s', len(export_list))
        dl_success = 0
        dl_count = 0
        wr_count = 0
        if len(export_list) != 0:
            log.info('Starting Download of {} files...', len(export_list))

            for item in export_list.values():
                dl_count += 1
                log.debug('Try download: %s File Name: %s', dl_count, item.title)
                try:
                    # Download the file using an authorized http object
                    response, content = self.SERVICE._http.request(item.eurl)
                    log.debug('status: %s', response.status)

                    if response.status == 200:
                        dl_success += 1
                        payload = [not_storage, item, content, wr_count]
                        wr_count = self.write_to_fs(*payload)
                except Exception, e:
                    log.exception('%s', e)

        log.info('%s files downloaded successfully', dl_success)
        log.info('%s files writen successfully', wr_count)