# Todo create directory of folders in fs
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
from folders import Folder
from service import DriveProvider, FileDownloader

from pprint import pprint

if __name__ == '__main__':
    storage_path, json_path = path_config("..\\file_store")
    ensure_dir([storage_path, ])

    go = DriveProvider()

    handler = DF(json_path, go.get_files(), go.get_folders(), go.get_root())

    # filter files and folders & data store to json file
    drive_data = handler()

    if drive_data:
        dl_list, folders = drive_data

        #create folders
        folders = Folder.make_folders(*folders) # create the folder tree
        Folder.make_tree(storage_path)  # create the tree in the filesystem



        # for fid, folder in folders.iteritems():
        #     print folder.title, fid
        #     if folder.children:
        #         print "Children: {}".format(folder.children)
        #     if folder.parent:
        #         print "Parent: {}".format(folder.parent)

        # create files






