import webbrowser
import logging
from httplib2 import Http

from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from apiclient.discovery import build


# TODO add error handling and logging
log = logging.getLogger('main.' + __name__)


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
            credentials = self.flow.step2_exchange(code)
            self.storage.put(credentials)
            return credentials
        if credentials is not None:
            return credentials


def build_service(authorization):
    """Returns a drive service object with an authorized http object"""
    credentials = authorization.get_credentials()
    http_auth = credentials.authorize(Http())
    return build('drive', 'v2', http=http_auth)
