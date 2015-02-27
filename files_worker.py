from builder import BuildService

from pprint import pprint

drive_service = BuildService().build_drive_service()
files = drive_service.files().list(maxResults=1).execute()

pprint(files)