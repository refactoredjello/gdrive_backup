# TODO create tests - esp. for checking modified date and new file downloads
# TODO work out why there are duplicates on first download
# TODO save locally in a folder that matches the drive folder
# TODO add local file locations to data storage
# TODO update meta.json if new files downloaded
# TODO move file meta storage to sql database
# TODO setup CLI and ability to choose save directory


# Configured logger before importing modules
from utils.log_init import initialize_logger
from utils.console_status import BarLoading

initialize_logger('logs')

import drive_service

if __name__ == '__main__':
    working = BarLoading()
    working.start()
    try:
        DF = drive_service.DriveServiceWorker()
        DF.download_files()
        working.stop = True
    except KeyboardInterrupt or EOFError:
        working.kill = True
        working.stop = True