from httplib2 import Http
import webbrowser
from pprint import pprint

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets


class Authorize(object):
    def __init__(self):
        self.storage = Storage('credentials')
        self.flow = flow_from_clientsecrets(
            'client_secrets.json',
            'https://www.googleapis.com/auth/drive.readonly',
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )
        self.auth_url = self.flow.step1_get_authorize_url()

    def get_credentials(self):
        credentials = self.storage.get()
        if credentials is None:
            webbrowser.open(self.auth_url)
            code = raw_input('Enter Verification Code: ').strip()
            self.storage.put(self.flow.step2_exchange(code))
        if credentials.refresh_token is not None:
            return credentials


def build_service(credentials):
    http_auth = credentials.authorize(Http())
    return build('drive', 'v2', http=http_auth)

drive_service = build_service(Authorize().get_credentials())


files = drive_service.files().list(maxResults=1).execute()

pprint(files)

