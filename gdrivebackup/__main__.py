# TODO create tests - esp. for checking modified date and new file downloads
# TODO update meta.json if new files downloaded
# TODO move file meta storage to sql database
# TODO setup CLI and ability to choose save directory
# TODO add support for slides


# Configured logger before importing modules
from .utils.logconf import initialize_logger
initialize_logger('logs')

from .utils.status import BarLoading
from .auth import Authorize, build_service
from .service import DriveWorker


if __name__ == '__main__':
    working = BarLoading()
    working.start()
    try:
        authorization = Authorize()
        service = build_service(authorization)
        DF = DriveWorker(service)
        DF.download_files()
        working.stop = True
    except KeyboardInterrupt or EOFError:
        working.kill = True
        working.stop = True