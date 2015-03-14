import sys
import time
import threading


class BarLoading(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.kill = False
        self.stop = False

    def run(self):
        print 'Loading....  ',
        sys.stdout.flush()
        i = 0
        while not self.stop:
            if (i % 4) == 0:
                sys.stdout.write('/ \r')
            elif (i % 4) == 1:
                sys.stdout.write('- \r')
            elif (i % 4) == 2:
                sys.stdout.write('\\ \r')
            elif (i % 4) == 3:
                sys.stdout.write('| \r')

            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        if self.kill:
            print 'ABORT! \r',
        else:
            print 'done! \r',
