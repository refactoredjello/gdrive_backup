import logging
from datetime import datetime
from os import path, mkdir


def initialize_logger(log_dir):
    if not path.exists(log_dir):
        mkdir(log_dir)

    main_log = logging.getLogger('main')
    main_log.setLevel(logging.DEBUG)
    _format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: '
                                '%(message)s')

    log_name = datetime.now().strftime('%Y_%m_%d-%H-%M_%S') + '.log'
    fh = logging.FileHandler(path.join(log_dir, log_name))
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(_format)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(message)s'))

    main_log.addHandler(ch)
    main_log.addHandler(fh)

    #use logging in __main__
    return main_log