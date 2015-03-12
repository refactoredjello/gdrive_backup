#TODO create tests - esp. for checking modified date and new file downloads
#TODO work out why there are duplicates on first download
#TODO save locally in a folder that matches the drive folder
#TODO add local file locations to data storage
#TODO update meta.json if new files downloaded
#TODO move file meta storage to sql database
#TODO setup CLI and ability to choose save directory


#Configured logger before importing modules
from utils.log_init import initialize_logger

initialize_logger('logs')


import drive_service

if __name__ == '__main__':
    DF = drive_service.DriveServiceWorker()
    DF.download_files()