# Todo write folders to file system start from root down
# Todo write files to fs
# Todo update json with new data
# TODO setup CLI and ability to choose save directory and type of file export
# Todo add loggers
# Todo handle if file moved to another folder
# TODO move file meta storage to sql database?

from utils.logconf import initialize_logger
initialize_logger('logs') # initialize main log  before importing modules

from configurator import ensure_dir, path_config
from handlers import DataFilter as DF
from handlers import make_folder_paths
from service import DriveProvider, FileDownloader

from pprint import pprint

if __name__ == '__main__':
    storage_path, json_path = path_config("..\\file_store")
    ensure_dir([storage_path, ])

    go = DriveProvider()

    # first pass basic filter and DataFilter instantiation
    handler = DF(json_path, go.get_files(), go.get_folders(), go.get_root())

    # filter files and folders
    drive_data = handler()


    if drive_data:
        dl_list, folders = drive_data
        print "Children: "
        pprint(folders[0])
        print "Roots: "
        pprint(folders[1])

        # create folders
        make_folder_paths(storage_path, *folders)

        # write folder tree in the filesystem and update folders with paths
       # Folder.make_tree(storage_path)

        # create files







