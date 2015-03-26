# TODO test updating json file - use a max results list or update actual
# drive files
import os
import json
import logging

from drive import DriveFolders, DriveFiles
from utils.tqdm import tqdm



log = logging.getLogger("main." + __name__)


def ensure_dir(directories):
    for d in directories:
        if not os.path.exists(d):
            os.mkdir(d)


class DriveProvider(object):
    def __init__(self, service, storage_path):
        self.service = service
        self.files_service = service.files()

        self.storage_path = storage_path
        self.orphaned_path = self.storage_path + "\\orphaned"
        self.json_storage = os.path.join(self.storage_path, "meta.json")

        self.file_list = self._get_file_list()
        self.folder_list = self._get_folder_list()

        ensure_dir([self.storage_path, self.orphaned_path])

    def _get_drive_list(self, payload_query):

        payload = {"q": 'trashed=false and ' + payload_query,
                   "fields": 'items(id,title,exportLinks,'
                             'mimeType,modifiedDate,labels,'
                             'parents(id,isRoot))'
                   }



        return self.files_service.list(**payload).execute()["items"]

    def _get_folder_list(self):
        pl_q = "mimeType = 'application/vnd.google-apps.folder'"
        log.info('Querying for folders')
        folders = {d["id"]: DriveFolders(**d) for d in
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
        log.info('Querying for matching files')
        items = self._get_drive_list(payload_query)

        return {d["id"]: DriveFiles(**d) for d in items}

    def _store_file_list(self):
        with open(self.json_storage, 'wb') as f:
            json.dump({fid: obj.__dict__ for fid, obj in
                       self.file_list.iteritems()}, f)

    def file_list_from_storage(self):
        with open(self.json_storage, 'r') as f:
            return json.load(f)

    def _update_json(self, new_files):
        json_data = self.file_list_from_storage()
        for fid, obj in new_files.iteritems():
            new_meta = obj.__dict__
            current_meta = json_data[fid]

            log.debug("Old Data: %s /n New Meta: %s", current_meta, new_meta)

            if fid not in json_data:
                json_data[fid] = new_meta

            elif new_meta["modifiedDate"] != current_meta["modifiedDate"]:
                json_data[fid]["modifiedDate"] = new_meta["modifiedDate"]

    def filter_download_list(self):

        def is_downloadable(k, v, stored_file_meta):
            if k not in stored_file_meta:
                log.info('Found  new item: %s', v.title)
                return True

            if v.modifiedDate != stored_file_meta[k]["modifiedDate"]:
                log.info('Found item change in: %s', v.title)
                return True

        stored_file_meta = self.file_list_from_storage()
        log.info('Json File Loaded \n %s entries found in meta.json',
                 len(stored_file_meta))

        return {k: v for k, v in self.file_list.iteritems()
                if is_downloadable(k, v, stored_file_meta)}

    def write_to_fs(self, not_storage, item, content, wr_count):

        storage_path = self.storage_path

        if item.orphaned:
            storage_path = self.orphaned_path

        f_name = os.path.join(storage_path, item.title + "." + item.ext)

        if not_storage and os.path.exists(f_name):
            log.error('\rFile %s already exists', f_name)
        else:
            with open(f_name, "wb") as f:
                f.write(content)
                wr_count += 1

        return wr_count

    def download_files(self):

        export_list = self.file_list

        not_storage = True

        if os.path.isfile(self.json_storage):
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
            log.info('Starting Download of %s files...', len(export_list))

            for item in tqdm(export_list.values(), leave=True):
                dl_count += 1
                log.debug('Trying Download: %s File Name: %s', dl_count,
                          item.title)
                try:
                    # Download file using an authorized http object
                    response, content = self.service._http.request(item.eurl)
                    log.debug('status: %s', response.status)

                    if response.status == 200:
                        dl_success += 1
                        payload = [not_storage, item, content, wr_count]
                        wr_count = self.write_to_fs(*payload)
                except Exception, e:
                    log.exception('%s', e)

        log.info('%s files downloaded successfully', dl_success)
        log.info('%s files writen successfully', wr_count)