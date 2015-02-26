from httplib2 import Http
from pprint import pprint

from apiclient.discovery import build

from auth import Authorize

def build_service(credentials):
    http_auth = credentials.authorize(Http())
    return build('drive', 'v2', http=http_auth)

drive_service = build_service(Authorize().get_credentials())

files = drive_service.files().list(maxResults=1).execute()


pprint(files)