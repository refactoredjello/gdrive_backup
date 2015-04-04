# Todo create directory of folders
# Todo handle file moved to another folder

# TODO move file meta storage to sql database
# TODO setup CLI and ability to choose save directory
# Note: Does not look for multiple parents of a file or folder


from utils.logconf import initialize_logger
initialize_logger('logs') # initialize main log  before importing modules

from configurator import ensure_dir, path_config
from handlers import DataFilter
from service import DriveProvider, FileDownloader

from pprint import pprint

if __name__ == '__main__':
    STORAGE_PATH, ORPHANED_PATH, JSON_PATH = path_config("..\\file_store")
    ensure_dir((STORAGE_PATH, ORPHANED_PATH))

    Go = DriveProvider()

    # Create a data filter object
    Handler = DataFilter(JSON_PATH, Go.get_files(), Go.get_folders(),
                         Go.get_root())

    filtered = Handler()
    if filtered:
        files, folders = filtered
        print len(folders)
        print len(Handler.file_meta)







