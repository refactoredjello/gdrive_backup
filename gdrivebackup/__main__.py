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
from handlers import DataFilter
from folders import Folder
from service import DriveProvider, FileDownloader

from pprint import pprint

if __name__ == '__main__':
    storage_path, json_path = path_config("..\\file_store")
    ensure_dir([storage_path,])

    go = DriveProvider()

    # Create a data filter object
    handler = DataFilter(json_path, go.get_files(), go.get_folders(),
                         go.get_root())

    drive_data = handler() # get filtered files and folders

    if drive_data:
        dl_list, folders = drive_data
        #pprint(dl_list)
        #create folders
        folders = Folder.make_folders(*folders) # dict of folder objs

        for fid, folder in folders.iteritems():
            print folder.title, fid
            if folder.children:
                print "Children: {}".format(folder.children)
            if folder.parent:
                print "Parent: {}".format(folder.parent)

        # create files






