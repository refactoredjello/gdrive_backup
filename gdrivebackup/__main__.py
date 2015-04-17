# Todo update json with new data
# TODO setup CLI and ability to choose save directory and type of file export
# Todo add loggers
# Todo handle if file moved to another folder
# TODO move file meta storage to sql database?

from utils.logconf import initialize_logger
initialize_logger('logs') # initialize main log  before importing modules

from configurator import ensure_dir, path_config
from handlers import DataFilter as DF
from handlers import make_folder_paths, write_files
from service import DriveProvider, FileDownloader

from pprint import pprint

if __name__ == '__main__':
    STORAGE_PATH, json_path = path_config("..\\file_store")
    ensure_dir([STORAGE_PATH, ])

    go = DriveProvider()
    DRIVE_ROOT_ID = go.get_root()

    # first pass basic filter and DataFilter instantiation
    handler = DF(json_path, go.get_files(), go.get_folders(), DRIVE_ROOT_ID)

    # filter files and folders
    drive_data = handler()

    if drive_data:
        dl_list, folders = drive_data

        # create folders
        updated_folders = make_folder_paths(STORAGE_PATH, *folders)

        # Download files
        dl_content = FileDownloader(dl_list, go())

        # Write to fs using the folder tree
        write_files(dl_content(), updated_folders, DRIVE_ROOT_ID, STORAGE_PATH)







