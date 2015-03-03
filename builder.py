from httplib2 import Http

from apiclient.discovery import build

from auth import Authorize


class BuildService(object):
    """build the drive service with an authorized http object"""

    def __init__(self):
        self.credentials = Authorize().get_credentials()
        self.http_auth = self.credentials.authorize(Http())
        self.service = build('drive', 'v2', http=self.http_auth)







