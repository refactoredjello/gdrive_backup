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
        log.info('Loading meta.json')
        with open(self.json_storage, 'r') as f:
            return json.load(f)

    def _update_json(self, stored_file_meta, new_files, changed_files):
        json_data = stored_file_meta

        for fid, fobj in changed_files.iteritems():
            new_meta = fobj.modifiedDate
            current = json_data[fid]["modifiedDate"]
            log.info("Current Data: %s --- New Data: %s", current, new_meta)
            json_data[fid]["modifiedDate"] = new_meta

        for fid, fobj in new_files.iteritems():
            log.info("New file added to json named: %s", fobj.title)
            json_data[fid] = fobj.__dict__

        with open(self.json_storage, 'wb') as f:
            json.dump(json_data, f)

    def filter_download_list(self, stored_file_meta):

        def is_new(k, v, stored_file_meta):
            if k not in stored_file_meta:
                log.info('Found new file: %s', v.title)
                return True

        def is_changed(k, v, stored_file_meta, new):
            if k in new:
                return False
            if v.modifiedDate != stored_file_meta[k]["modifiedDate"]:
                log.info('Found file change in: %s', v.title)
                return True

        log.info('%s entries found', len(stored_file_meta))
        print "\n\n"
        log.info('Searching for new or changed files...')

        new = {k: v for k, v in self.file_list.iteritems()
               if is_new(k, v, stored_file_meta)}

        changed = {k: v for k, v in self.file_list.iteritems()
                   if is_changed(k, v, stored_file_meta, new)}

        log.info('Found: %s new files, %s changed files', len(new),
                 len(changed))
        if len(changed) + len(new):
            self._update_json(stored_file_meta, new, changed)

        return new, changed

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
            print "\n"
            log.info('Getting files meta data from storage.')
            stored_file_meta = self.file_list_from_storage()
            new, changed = self.filter_download_list(stored_file_meta)
            export_list = new.copy()
            export_list.update(changed)
            not_storage = False
        else:
            self._store_file_list()

        dl_success = 0
        dl_count = 0
        wr_count = 0

        if export_list:
            print "\n"
            log.info('Starting Download of %s file(s):', len(export_list))

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