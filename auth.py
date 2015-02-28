import webbrowser

from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets


class Authorize(object):
    def __init__(self):
        self.storage = Storage('credentials')
        self.flow = flow_from_clientsecrets(
            'client_secrets.json',
            'https://www.googleapis.com/auth/drive',
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






