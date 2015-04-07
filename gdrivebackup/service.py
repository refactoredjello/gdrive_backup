import logging

from httplib2 import Http
from apiclient.discovery import build

from utils.tqdm import tqdm
from auth import Authorize

log = logging.getLogger("main." + __name__)


class DriveProvider(Authorize):
    """Provides an api for getting meta data of  files that are in
    google docs, slides,or sheets format, and drive folders.

    :return: authorized drive service
    """
    def __init__(self):
        Authorize.__init__(self)
        self.service = self._build_service()

    def _build_service(self):
        credentials = self.get_credentials()
        http_auth = credentials.authorize(Http())

        return build('drive', 'v2', http=http_auth)

    def get_root(self):
        root = self.service.files().get(fileId="root").execute()
        return root["id"]

    def _get_meta(self, payload_query, get_type):
        """
        :param payload_query: type of meta data to get (folder or file)
        :return: a dict of drive files and folders as dicts
        """
        print 'Downloading {} Data...'.format(get_type)

        payload = {
            "maxResults": 1000,
            "q": 'trashed=False and ' + payload_query,
            "fields": 'items(id,title,exportLinks,'
                      'mimeType,modifiedDate,labels,'
                      'parents(id,isRoot)), nextPageToken'
            }
        items = []
        page_token = None
        while True:
            if page_token:
                payload['pageToken'] = page_token
            batch = self.service.files().list(**payload).execute()

            items.extend(batch["items"])

            page_token = batch.get("nextPageToken")
            if not page_token:
                break

        # We only need the first parent of a resource
        for item in items:
            if item["parents"]:
                item["parents"] = item["parents"][0]
        print "Done!"
        return {item.pop("id"): item for item in items}

    def get_folders(self):
        payload = "mimeType = 'application/vnd.google-apps.folder'"
        return self._get_meta(payload, "folder")

    def get_files(self):
        payload_query = (
            "(mimeType = 'application/vnd.google-apps.document'"
            "or mimeType = 'application/vnd.google-apps.presentation'"
            "or mimeType = 'application/vnd.google-apps.spreadsheet')"
            )
        return self._get_meta(payload_query, "file")

    def __call__(self):
        return self.service


class FileDownloader(object):
    """Downloads a list of files using an export url.

    :return: a tuple of downloaded file content objects and it's drive id
    """
    def __init__(self):
        self.dl_count = 0
        self.downloaded_content = ()

    def __call__(self, dl_list, service):
        """
        :param dl_list: dict with file id as key and export url as value
        :param service: an authorized drive service object
        """
        for fid, v in tqdm(dl_list.iteritens(), leave=True,):
            # Download file using an authorized http object
            response, content = service._http.request(v.get("url"))

            if response.status == 200:
                self.downloaded_content += ((fid, content),)
                self.dl_count += 1
            else:
                log.error('An error occurred', response)

        return self.downloaded_content