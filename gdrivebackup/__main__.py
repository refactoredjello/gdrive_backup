# TODO move all the dir configurations
# TODO save files based on drive folder tree
# TODO move file meta storage to sql database
# TODO setup CLI and ability to choose save directory
# TODO add support for slides

from utils.logconf import initialize_logger
initialize_logger('logs') # initialize main log  before importing modules

from auth import Authorize, build_service
from service import DriveProvider


if __name__ == '__main__':
        authorization = Authorize()
        service = build_service(authorization)

        storage_path = "..\\file_store"

        DF = DriveProvider(service, storage_path)
        DF.download_files()
