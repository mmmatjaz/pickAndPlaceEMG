import collections
import sys
from time import time

import myo as libmyo

SAMPLES=100
class Myo(libmyo.DeviceListener):

    def __init__(self):
        super(Myo, self).__init__()
        self.counter=0
        self.lastPrint=0
        self.emg=[]
        self.buffers=[]
        self.tLast=time()
        for i in xrange(8):
            self.emg.append(0)
            self.buffers.append(collections.deque(maxlen=SAMPLES))
        self.hub=None

    ''' callbacks '''
    def on_pair(self, myo, *args):
        print("on_pair")

    def on_connect(self, myo, *args):
        print("on_connect")

    def on_arm_sync(self, myo, *args):
        print("on_arm_sync")
        myo.set_stream_emg(libmyo.StreamEmg.enabled)

    def on_emg_data(self, myo, timestamp, emg):
        if self.emg is None:
            same=False
        else:
            same=True
            for i in xrange(8):
                same &= emg[i] is self.emg[i]

        if not same:
            self.emg=emg
            for i in xrange(8):
                self.buffers[i].append(abs(emg[i]))

        self.counter+=1
        if time()-self.lastPrint>1.:
            #print "listener f=%d " % self.counter
            self.counter=0
            self.lastPrint=time()

        self.tLast=time()

    ''' public stuff '''
    def start(self):
        try:
            libmyo.init("C:/opt/myo-sdk-win-0.9.0/bin")
        except RuntimeError:
            print "kr neki"
        self.hub = libmyo.Hub()
        self.hub.run(1, self)

    def isAlive(self):
        return self.hub is not None and self.hub.running

    def cancel(self,join=True):
        self.hub.stop(join)
        self.hub.shutdown()

    def getCoco(self):
        mavgs=[]
        for row in self.buffers:
            mavgs.append(sum(row)/float(SAMPLES))

        flexion = max(mavgs[0:3])
        extension=max(mavgs[5:])
        return min([flexion, extension])

def main():
    lastPrint=0.
    myo = Myo()
    myo.start()
    counter=0
    print "going while-d"
    try:
        while True:
            counter+=1
            if time()-lastPrint>1.:
                print "main     f=%d " % counter
                counter=0
                lastPrint=time()
            '''
            if time()-lastPrint>.2:
                print myo.emg
                print myo.getCoco()
                lastPrint=time()
            sys.stdout.flush()
            '''
    finally:
        myo.cancel()


if __name__ == '__main__':
    main()