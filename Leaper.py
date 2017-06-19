from Box2D import b2Vec2

import Leap
from math import sqrt


class Leaper(Leap.Listener):
    def __init__(self,scale=1./4/10., offset=b2Vec2(6.0,0.)):
        self.__thumbPos=Leap.Vector(0., 0., 0.)
        self.__indexPos=Leap.Vector(0., 0., 0.)
        self.__time=0.
        self.controller = Leap.Controller()
        self.scale=scale
        self.offset=offset
        super(Leaper, self).__init__()

    def start(self):
        self.controller.add_listener(self)

    def cancel(self):
        self.controller.remove_listener(self)

    def on_frame(self, controller):
        frame = controller.frame()
        for hand in frame.hands:
            if len(hand.fingers)>1:
                self.__thumbPos=hand.fingers[0].tip_position
                self.__indexPos=hand.fingers[1].tip_position
                #print (self.__thumbPos)

    def getBirdsEye(self):
        return b2Vec2(int(self.__thumbPos.x),int(self.__thumbPos.z)), \
               b2Vec2(int(self.__indexPos.x),int(self.__indexPos.z))

    def getPos2D(self):
        '''
        deltaP=self.__thumbPos-self.__indexPos
        p0=(self.__thumbPos+self.__indexPos)
        D=deltaP.magnitude
        deltaP.z=0
        dp=deltaP.normalized*D
        pt=.5*b2Vec2(p0.x,p0.y)+.5*b2Vec2(dp.x,dp.y)
        pi=.5*b2Vec2(p0.x,p0.y)-.5*b2Vec2(dp.x,dp.y)
        #return self.__time, pt,pi
        '''
        return self.__time, \
               b2Vec2([self.__thumbPos.x,self.__thumbPos.y]), \
               b2Vec2([self.__indexPos.x,self.__indexPos.y])
        #return self.__time, np.array([0,0])*scale, np.array([0,0])*scale

    def getPosScaled(self):
        tLeap,leapL,leapR=self.getPos2D()
        leapL=(leapL*self.scale+self.offset) if leapL.length != 0. else leapL
        leapR=(leapR*self.scale+self.offset) if leapR.length != 0. else leapR
        return self.__time, leapL, leapR

    def on_init(self, controller):
        pass

    def on_connect(self, controller):
        pass

    def on_disconnect(self, controller):
        pass

    def on_exit(self, controller):
        pass