from os import path
from pprint import pprint

from builder import BuildService

class DriveFiles:
    def __init__(self):
        # build the drive service with an http object
        self.drive_service = BuildService().build_drive_service()

        self.drive_files_service = self.drive_service.files()

        self.payload_types = (
        "mimeType = 'application/vnd.google-apps.document'"
        "or mimeType = 'application/vnd.google-apps.presentation'"
        "or mimeType = 'application/vnd.google-apps.spreadsheet'"
        )
        self.export_type_dict = {
            'application/vnd.google-apps.document':
                ('application/vnd.openxmlformats-officedocument.wordprocessingml'
                '.document', 'docx'),
            'application/vnd.google-apps.spreadsheet':
                ('application/vnd.openxmlformats-officedocument.spreadsheetml'
                '.sheet','xlsx')
        }

    def get_file_list(self):
        """returns a list of files and their meta data which match the payload"""
        payload = self.payload_types
        return self.drive_files_service.list(maxResults=5, q=payload).execute()

    def get_export_links(self):
        """adds each file drive id as a key, and title and exportLink as
        values to the file_meta dict """
        file_meta = {}
        files_list = self.get_file_list()
        for f in files_list['items']:
            links = f['exportLinks']
            export_type = self.export_type_dict[f['mimeType']]
            export_link = links[export_type[0]]
            extension = export_type[1]
            file_meta[f['id']] = (f['title'], export_link, extension)
        return file_meta

    def download_files(self):
        file_list = self.get_export_links()# change this to a function that
        # contains the download list based on db check
        for title, furl, extension in file_list.values():
            response, content = self.drive_service._http.request(furl)
            print response.status
            file_name = path.join('file_store', title + "." + extension)
            with open(file_name,'wb' ) as f:
                f.write(content)

DriveFiles().download_files()
#pprint((drive_files))


#TODO store file id and modified date and download url in a db
#TODO check against local db if they have changed since last download
#TODO if they changed add them to download list

#TODO Download files listed in download list in proper ms office format
