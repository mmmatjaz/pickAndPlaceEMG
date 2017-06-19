from MyoUDP import Myo
import matplotlib.pyplot as plt

class CalibMyo(object):

    def __init__(self):
        pass

    def go(self):
        myo = Myo()
        coco0=[]
        print "Relax"
        try:
            while True:
                myo.recData()
                emg= str(myo.getEMG())
                coco0.append(myo.getCoco())
                #print str(m.getCoco()>30)
        except KeyboardInterrupt:
            print "ok"

        print "Fist!"
        cocoF=[]
        try:
            while True:
                myo.recData()
                emg= str(myo.getEMG())
                cocoF.append(myo.getCoco())
                #print str(m.getCoco()>30)
        except KeyboardInterrupt:
            print "ok"

        plt.plot(coco0, 'r', cocoF, 'b')
        plt.show()

        choice = int(input("Threshold?"))
        return choice


if __name__ == "__main__":
    CalibMyo().go()