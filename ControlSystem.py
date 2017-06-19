from Box2D import b2Vec2, b2PolygonShape, b2ContactListener, b2World
import pygame
from enum import IntEnum
from pygame.locals import *

class SystemState(IntEnum):
    INTERRUPTED=0
    RUNNING=1
    PLACED=2
    CRUSHED=3


class ControlSystem(b2ContactListener):
    defObjDyn={'density' : 1.0,     'friction' : .44,   'restitution' : 0}
    fingerDyn={'density' : 0.001,   'friction' : 1.,    'restitution' : 0}

    MODEL_SCALE=100.
    objDim=b2Vec2(.08, .1)

    def __init__(self, dynProps=defObjDyn, impactT=10, dt=1./120.):
        SCALE=ControlSystem.MODEL_SCALE

        self.dt=dt
        self.objDynProps=dynProps

        self.refL= b2Vec2(.8, .5) * SCALE
        self.refR= b2Vec2(1., .5) * SCALE
        self.objVel_=b2Vec2(0., 0.)
        self.errorRprev=None
        self.errorLprev=None
        self.crushed=False
        self.impactT=impactT

        b2ContactListener.__init__(self)

    def buildWorld(self):
        SCALE=ControlSystem.MODEL_SCALE
        world = b2World(gravity=b2Vec2(0.0, -9.81)*SCALE, doSleep=True,contactListener=self)
        bodies = []

        ''' STATICS '''
        self.ground_body = world.CreateStaticBody(position=b2Vec2(1,.050) *SCALE)
        self.ground_body.CreatePolygonFixture(box=b2Vec2(1, 0.025)*SCALE,friction=5.)
        bodies.append(self.ground_body)
        self.platform = world.CreateStaticBody(position=b2Vec2(1.25,.2)*SCALE)
        self.platform.CreatePolygonFixture(box=b2Vec2(ControlSystem.objDim.x,0.025)*SCALE,friction=5.)
        bodies.append( self.platform)
        self.obstacle = world.CreateStaticBody(position=b2Vec2(.8,.2) *SCALE)
        self.obstacle.CreatePolygonFixture(box=b2Vec2(.025, 0.025)*SCALE,friction=5.)
        bodies.append(self.obstacle)

        ''' FINGERS '''
        self.fLeft = world.CreateDynamicBody(position=self.refL, angle=0, linearVelocity=b2Vec2(0, 0))
        self.fLeft.fixedRotation=True
        self.fLeft.CreatePolygonFixture(box=b2Vec2(.02, .05)*SCALE, **ControlSystem.fingerDyn)
        bodies.append(self.fLeft)
        self.fRight = world.CreateDynamicBody(position=self.refR, angle=0, linearVelocity=b2Vec2(0, 0))
        self.fRight.fixedRotation=True
        self.fRight.CreatePolygonFixture(box=b2Vec2(.02, .05)*SCALE, **ControlSystem.fingerDyn)
        bodies.append(self.fRight)

        ''' OBJECT '''
        self.object = world.CreateDynamicBody(position=b2Vec2(.5,.1)*SCALE, angle=0, linearVelocity=b2Vec2(0, 0))
        self.object.CreatePolygonFixture(box=ControlSystem.objDim*SCALE, **self.objDynProps)
        self.object.linearDamping = 0.0
        self.object.angularDamping = 0.01
        bodies.append(self.object)
        print "mass %f"%self.object.mass
        self.bodies=bodies
        return world

    def smallDistance(self):
        return 2e-2*ControlSystem.MODEL_SCALE

    def PostSolve(self, contact, impulse):
        SCALE=ControlSystem.MODEL_SCALE
        da=contact.fixtureA.body.position- self.object.position
        db=contact.fixtureB.body.position- self.object.position
        if da.length < self.smallDistance() or db.length < self.smallDistance():
            #print str(impulse.normalImpulses[0])
            if impulse.normalImpulses[0] > self.impactT*SCALE:
                print "boom "
                self.crushed=True

        for i in range(2,len(self.bodies)):
            body = self.bodies[i]
            dist=contact.fixtureB.body.position- body.position

            if dist.length<.1:
                pass#print "yes "+str(i)
        #distance=contact.fixtureA.transform.position-self.object.fixtures[0]
        #if distance.lenght<.1:
        #    print "obj contact prob"

    def applyInput(self, refL, refR, KP, KD):
        SCALE=ControlSystem.MODEL_SCALE
        # LEFT FINGER
        error=refL-self.fLeft.transform.position
        if self.errorLprev is None:
            self.errorLprev=error
        self.Lforce= KP * error + KD * (error - self.errorLprev) / self.dt
        self.fLeft.ApplyLinearImpulse(impulse=self.Lforce*SCALE, point=self.fLeft.GetWorldPoint(b2Vec2(0, 0)), wake=True)
        self.errorLprev=error

        # RIGHT FINGER
        error=refR-self.fRight.transform.position
        if self.errorRprev is None:
            self.errorRprev=error
        self.Rforce= KP * error + KD * (error - self.errorRprev) / self.dt
        self.fRight.ApplyLinearImpulse(impulse=self.Rforce*SCALE, point=self.fLeft.GetWorldPoint(b2Vec2(0, 0)), wake=True)
        self.errorRprev=error

    def getAccuracy(self):
        return 1. - abs(self.object.position.x - self.platform.position.x) \
               / (1. * ControlSystem.objDim.x * ControlSystem.MODEL_SCALE)

    def checkEvents(self):
        """
        Check for pygame events (mainly keyboard/mouse events).
        Passes the events onto the GUI also.
        """
        # print "checkEvents"
        for event in pygame.event.get():
            # print "event.type = ", event.type
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                print "early bailout"
                return SystemState.INTERRUPTED


        objVel=self.object.linearVelocity
        objOmega=self.object.angularVelocity



        self.objVel_=objVel
        ''' placed? '''
        if len(self.object.contacts) is 1 and self.object.contacts[0].contact.touching:
            if self.object.contacts[0].other == self.platform\
                    and (objVel.length == 0.) and (self.objVel_.length == 0.) and (objOmega == .0):
                print "placed "+str(objVel)
                return SystemState.PLACED

        if self.crushed:
            return SystemState.CRUSHED
        return SystemState.RUNNING



