import sys
import time


for i in range(10):
    time.sleep(1)
    sys.stdout.write('\r%d / %d' % (i+1, 10));


    