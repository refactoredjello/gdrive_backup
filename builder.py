from httplib2 import Http

from apiclient.discovery import build

from auth import Authorize


class BuildService:
    def __init__(self):
        """ Get credentials and create a http authorize object"""
        self.credentials = Authorize().get_credentials()
        self.http_auth = self.credentials.authorize(Http())

    def build_drive_service(self):
        """Build an authenticated drive service object"""
        return build('drive', 'v2', http=self.http_auth)





