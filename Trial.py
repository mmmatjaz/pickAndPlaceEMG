import argparse
import time

import pygame
from Box2D import b2Vec2
from enum import IntEnum # pip install enum34

from ControlSystem import ControlSystem, SystemState
from DrawToScreen import DrawToScreen
from Leaper import Leaper
from MyoUDP import Myo

'''
    The model is scaled by ControlSystem.KINEMATICS_SCALE!!!
    this includes:
        dimensions and positions
    to compensate, gravity is scaled up too and mass is scaled down

    SCALE should be passed
        to Leaper for scaling the position reference
        to Drawer for zoom adjustment
'''


''' experimental conditions (PD gains), last optional '''

TARGET_FPS = 120
TIME_STEP = 1.0/TARGET_FPS

LOG_TS=.02


class Condition(IntEnum):
    __order__ = 'LOW HIGH VAR'# PROP'
    LOW=1
    HIGH=2
    VAR=3
    #PROP=4
    def __json__(self):
        return '"%s"'%self.name

CtrlProps={
    Condition.HIGH:   {'KP':.008, 'KD':.0005},
    Condition.LOW:    {'KP':.003, 'KD':.0003}}

''' object type and params '''
class ObjectType(IntEnum):
    __order__ = 'ROBUST FRAGILE'
    ROBUST=0
    FRAGILE=1
DynProps={
    ObjectType.ROBUST:
    {'density' : 0.001,  'friction' : 0.44, 'restitution' : 0.},
    ObjectType.FRAGILE:
    {'density' : 0.0001, 'friction' : 0.44, 'restitution' : 0.}}
ImpactThresh={
    ObjectType.ROBUST : .5,
    ObjectType.FRAGILE: .1}

''' input params and scaling '''
COCO_THRESH=10.
LEAP_WS_SCALE=1./380.
LEAP_WS_OFFSET=b2Vec2(0.9, -0.2)


'''  T R I A L    C L A S S  '''
class Trial(object):
    def __init__(self, condition = Condition.VAR,
                 objType   = ObjectType.ROBUST,
                 shouldLog = True,
                 cocoThr   = COCO_THRESH):

        self.cocoThr=cocoThr
        self.shouldLog= shouldLog
        self.condition= condition
        self.objType=   objType

        ''' trial data '''
        self.outcome=None
        self.trialDuration=None
        self.accuracy=None
        self.fileName="../results/"+time.strftime("%Y%m%d_%H%M%S")+".csv" \
            if shouldLog else None

        ''' mocap '''
        self.posInput=Leaper(scale= LEAP_WS_SCALE *ControlSystem.MODEL_SCALE,
                             offset=LEAP_WS_OFFSET*ControlSystem.MODEL_SCALE)
        self.posInput.start()

        ''' myo '''
        self.myo = Myo()
        self.myo.start()

        # workaround leap service bugs
        time.sleep(.2)

    def getTrialData(self):
        return self.outcome, self.trialDuration, self.accuracy, self.fileName

    def loop(self):
        print "setting up"
        ''' pygame setup '''
        pygame.init()
        clock = pygame.time.Clock()
        cSys = ControlSystem(dynProps=  DynProps    [self.objType],
                             impactT=   ImpactThresh[self.objType])
        world = cSys.buildWorld()
        draw = DrawToScreen()
        if self.shouldLog:
            logFileObj = open(self.fileName, 'w')
            logFileObj.write('t, rlx, rly, rrx, rry, px, py, fi, myo \n')

        # trial states
        systemState = SystemState.RUNNING
        startPosReached=False
        # init prev. reference to the current position
        refL_=cSys.refL
        refR_=cSys.refR
        coco=0.
        # time of print
        lastPrint=time.time()
        # log table
        lastLogLine=time.time()
        # trial actually starts when init pos reached
        tStart=time.time()
        print "entering main loop"

        while systemState is SystemState.RUNNING:
            t = time.time()
            ''' process position input '''
            bEyeL,bEyeR=self.posInput.getBirdsEye()

            tLeap,leapLL,leapRR=self.posInput.getPosScaled()
            # check if fingers tracked at all
            if leapLL.length * leapRR.length > 0:
                # leap becomes position reference only after user reaches init positions
                if startPosReached:
                    refL=leapLL
                    refR=leapRR
                    refL_=refL.copy()
                    refR_=refR.copy()
                # use previous reference
                else:
                    refL=refL_
                    refR=refR_
                    # if JUST reached
                    # tmp
                    e1=leapLL-refL_
                    e2=leapRR-refR_
                    dpMax=cSys.smallDistance()
                    if not startPosReached and e1.length<dpMax and e2.length<dpMax:
                        startPosReached=True
                        tStart=time.time()
            else:
                refL=refL_
                refR=refR_

            ''' process myo input '''
            coco=self.myo.getCoco()
            if self.condition is Condition.VAR:
                ctrlPar=CtrlProps[Condition.LOW] if coco < self.cocoThr \
                    else CtrlProps[Condition.HIGH]
            else:
                ctrlPar=CtrlProps[self.condition]

            ''' simulate '''
            cSys.applyInput(refL, refR, **ctrlPar)
            world.Step(TIME_STEP, 10, 10)
            systemState = cSys.checkEvents()

            ''' draw '''
            draw.renderBodies(cSys.bodies)
            draw.renderImage(cSys.object,self.objType)
            draw.drawForcePoint(cSys.object.position)
            draw.drawForcePoint(cSys.platform.position)
            draw.drawMiniMap(bEyeL,bEyeR)
            if not startPosReached:
                draw.text('Please move to starting points')
                if leapLL is not None and leapRR is not None:
                    draw.drawForcePoint(leapLL)
                    draw.drawForcePoint(leapRR)
                    draw.drawForcePoint(refL)
                    draw.drawForcePoint(refR)


            if self.condition is Condition.VAR:
                draw.drawCocoBar(coco,self.cocoThr)
            else:
                draw.textMode('{0}'.format(self.condition.name))

            #draw.drawForcePoint(refL)
            #draw.drawForcePoint(refR)
            pygame.display.flip()
            clock.tick(TARGET_FPS)

            ''' print '''
            if t-lastPrint>1.:
                # print coco
                lastPrint=t

            ''' log '''
            if self.shouldLog and startPosReached and systemState is SystemState.RUNNING \
                    and (t-lastLogLine) > LOG_TS:
                po=cSys.object.position
                logRow='%6.3f, %7.3f, %7.3f, %7.3f, %7.3f, %7.3f, %7.3f, %5.3f, %5.2f\n' % (
                        t-tStart, refL.x,refL.y, refR.x,refR.y,
                        po.x,po.y, cSys.object.angle, coco)
                logFileObj.write(logRow)
                lastLogLine=t

        ''' collect trial info '''
        self.trialDuration=time.time()-tStart
        self.outcome=systemState
        self.accuracy=cSys.getAccuracy()

        ''' show message '''
        if systemState is not SystemState.INTERRUPTED:
            tEnd=time.time()
            while (time.time()-tEnd)<2.:
                cSys.applyInput(refL, refR, **ctrlPar)
                world.Step(TIME_STEP, 10, 10)
                draw.drawForcePoint(refR)
                draw.renderBodies(cSys.bodies)
                draw.renderImage(cSys.object,
                     self.objType   if systemState is SystemState.PLACED else None)
                draw.text(
                    'Done in %f s'%(self.trialDuration)
                    if systemState is SystemState.PLACED else 'oh-oh')
                pygame.display.flip()
                clock.tick(TARGET_FPS)

        ''' clean up and quit '''
        if self.shouldLog and startPosReached:
            logFileObj.close()

        pygame.quit()
        if self.myo.isAlive():
            print "killing myo"
            self.myo.cancel()
            #self.myo.join()

        self.posInput.cancel()

        print('Ajde')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Trial class')
    parser.add_argument('-l',action="store_true", default=False, dest="log",
                        help='Flag to ENABLE logging')
    parser.add_argument('-f', action="store_true", default=False, dest="fragile",
                        help='Flag to use fragile object')
    parser.add_argument('-c', action="store", type=float, default=10., dest="coco",
                        help='Set coco threshold')
    #parser.add_argument('-h', action="store_true", default=False, dest="help")
    res=parser.parse_args()

    #if res.help:
    #    parser.print_help()
    #    exit()

    Trial(shouldLog = res.log,  #res.log,
          objType   = ObjectType.FRAGILE if res.fragile else ObjectType.ROBUST,
          cocoThr   = res.coco,
          condition = Condition.VAR if res.coco > 0 else Condition.HIGH).loop()
