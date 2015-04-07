# Todo create folders objects from searching folders until you get to root
# Todo get export url
# Todo add loggers
# Todo update json with new data
# Todo create directory of folders in fs
# Todo write files to fs
# Todo handle if file moved to another folder

# TODO setup CLI and ability to choose save directory and type of file export
# TODO move file meta storage to sql database?

# Note: Does not look for multiple parents of a file or folder


from utils.logconf import initialize_logger
initialize_logger('logs') # initialize main log  before importing modules

from configurator import ensure_dir, path_config
from handlers import DataFilter
from folders import Folder
from service import DriveProvider, FileDownloader

from pprint import pprint

if __name__ == '__main__':
    STORAGE_PATH, ORPHANED_PATH, JSON_PATH = path_config("..\\file_store")
    ensure_dir((STORAGE_PATH, ORPHANED_PATH))

    go = DriveProvider()

    # Create a data filter object
    handler = DataFilter(JSON_PATH, go.get_files(), go.get_folders(),
                         go.get_root())

    drive_data = handler() # get filtered files and folders

    if drive_data:
        dl_list, found_folders = drive_data
        #create folders
        folders = Folder.make_folders(*found_folders) # dict of folder objs
        print len(folders)
        pprint(dl_list)
        # create files






