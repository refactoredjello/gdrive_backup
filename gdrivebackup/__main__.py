#TODO FIX LOGGER!
#TODO work out why there are duplicates on first download
#TODO save locally in a folder that matches the drive folder
#TODO add local file locations to data storage
#TODO update meta.json if new files downloaded
#TODO move file meta storage to sql database

import drive_service
from os import path
# from datetime import datetime
# import logging
#
#
#
# #_format = '%(levelname)s %(asctime): %(message)s'
# log_name = 'log' + datetime.now().strftime('%Y_%m_%d-%H-%M_%S') + '.txt'
# log = logging.getLogger(__name__)
# log.basicConfig(filename=log_name, level=logging.DEBUG,)


if __name__ == '__main__':
    DF = drive_service.DriveServiceWorker()
    DF.download_files()