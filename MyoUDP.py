
__author__ = 'mLocal'

import collections
import socket
import struct
import sys
import threading

HOST = ''   # Symbolic name meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port
SAMPLES=100
'''
example = Myo()
example.start()
example.join()
'''
class Myo(threading.Thread):
    def __init__(self):
        try :
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s.settimeout(1.0)
            print 'Socket created'
        except socket.error, msg :
            print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()
        # Bind socket to local host and port
        try:
            self.s.bind((HOST, PORT))
        except socket.error , msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()

        print 'Socket bind complete'

        self.__emg=[]
        self.buffers=[]
        for i in xrange(8):
            self.__emg.append(0)
            self.buffers.append(collections.deque(maxlen=SAMPLES))
        self.__shouldRun=True

        threading.Thread.__init__(self)

    def cancel(self,join=True):
        """
        call from main
        """
        self.__shouldRun=False
        if join:
            self.join()


    def run(self):
        while self.__shouldRun:
            self.recData()

        print "myo finished"
        self.s.close()

    def recData(self):
        d = self.s.recvfrom(1024)
        data = d[0]
        #print str(type(data))+str(data)
        row = struct.unpack("Qbbbbbbbb", data)
        # time=row[0]
        self.__emg = row[1:]
        for i in xrange(8):
            self.buffers[i].append(abs(row[i + 1]))
            # print "running"

    def getCoco(self):
        mavgs=[]
        for row in self.buffers:
            mavgs.append(sum(row)/float(SAMPLES))

        flexion = max(mavgs[0:3])
        extension=max(mavgs[5:])
        return min([flexion, extension])

    def getEMG(self):
        return self.__emg

def main(argv):
    for i in range(0,15):
        m=Myo()
        m.start()
        try:
            while True:
                #time.sleep(.025)
                emg= str(m.getEMG())
                print str(m.getCoco()<21) +" - "+ emg
                #print str(m.getCoco()>30)
        except KeyboardInterrupt:
            print "Bye"
            m.cancel()
            print "canceled"
            m.join()
            print "joined"
            #return

if __name__ == "__main__":
    main(sys.argv)