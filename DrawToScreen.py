import os

import pygame
from Box2D import b2Color, b2_staticBody, b2_dynamicBody, b2Vec2

imSize=(113, 113)
screenXY = SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 1000

class DrawToScreen:

    def __init__(self):
        self.viewZoom          = 10.
        self.viewCenter        = b2Vec2(0., 0.)
        self.viewOffset        = b2Vec2(0., 0.)
        self.flipY = True
        self.screenSize        = b2Vec2(*screenXY)

        self.pointSize = 10.

        self.colors={
            'grey1'       : (150,150,150),
            'grey2'       : (200,200,200),
            'force_point' : (0,255,0)
        }

        self.colorsbt = {
            b2_dynamicBody  : (255,255,255,255),
            b2_staticBody : (127,127,127,255),
        }
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (200,50)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
        #self.imgFragile = pygame.image.load('fragile.bmp')
        self.imgFragile =   pygame.transform.scale(pygame.image.load('pics/fragile.bmp'), imSize)
        self.imgHeavy =     pygame.transform.scale(pygame.image.load('pics/heavy.bmp'), imSize)
        self.imgBoom =      pygame.transform.scale(pygame.image.load('pics/boom.bmp'), imSize)


    def drawMiniMap(self, pt, pi):
        #mask=1-((pt+pi)/2).y/100
        #print mask
        mask=.8
        center=b2Vec2(1300,115)
        self.__drawSegment( self.__vec2tupleInt(center+b2Vec2(-100,0)),
                            self.__vec2tupleInt(center+b2Vec2(+100,0)),self.colors['grey1'])
        self.__drawPoint(   self.__vec2tupleInt(pt+center),5, (255,255,255,int(mask*255)))
        self.__drawPoint(   self.__vec2tupleInt(pi+center),5, (255,255,255,int(mask*255)))
        self.__drawSegment( self.__vec2tupleInt(pt+center),
                            self.__vec2tupleInt(pi+center),(255,255,255,int(mask*255)))

    def drawCocoBar(self, val, thr, cmin=0., cmax=60.):
        rangepx=500.
        xpx=(SCREEN_WIDTH-rangepx)/2
        valpx=val/(cmax-cmin)*rangepx
        pygame.draw.rect(self.screen, (127,127,127,255), [xpx, 100, valpx, 30])
        pygame.draw.rect(self.screen, (255,255,255,255), [xpx, 100, rangepx, 30], 2)
        thrpx=thr/(cmax-cmin)*rangepx
        pygame.draw.rect(self.screen, (255,255,255,255), [xpx+thrpx-2, 100, 4, 30], 4)

    def renderBodies(self,bodies):
        self.screen.fill((0, 0, 0, 0))
        # Draw the world
        #print "peder"
        nBody=0

        for body in bodies: # or: world.bodies
            # The body gives us the position and angle of its shapes
            for fixture in body.fixtures:
                # The fixture holds information like density and friction,
                # and also the shape.
                shape = fixture.shape

                vertices_screen = []
                for vertex_object in shape.vertices:
                    vertex_world = body.transform * vertex_object # Overload operation
                    vertex_screen = self.__convertWorldtoScreen(vertex_world) # This returns a tuple
                    vertices_screen.append( vertex_screen) # Append to the list.


                #print vertices_screen
                pygame.draw.polygon(self.screen, self.colorsbt[body.type], vertices_screen,0)

            nBody+=1

    def renderImage(self, body, imType=None):
        pos= self.__convertWorldtoScreen(body.position) # This returns a tuple
        pp=b2Vec2(*pos)- b2Vec2(imSize) / 2

        angle=0#body.angle*180./3.14
        if imType is not None:
            img=pygame.transform.rotate(self.imgFragile if imType.value is 1 else self.imgHeavy,angle)
        else:
            img=pygame.transform.rotate(self.imgBoom, angle)
        self.screen.blit(img, pp.tuple)

    def textMode(self,t):
        # initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
        myfont = pygame.font.SysFont("monospace", 36)
        # render text
        label = myfont.render(t, 1, (255,255,255))
        self.screen.blit(label, (100, 100))

    def text(self,t):
        # initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
        myfont = pygame.font.SysFont("monospace", 36)
        # render text
        label = myfont.render(t, 1, (255,255,255))
        self.screen.blit(label, (100, 250))


    def drawForcePoint(self, forcePoint_2d_m):
        forcePoint_screen = self.__convertWorldtoScreen(forcePoint_2d_m)
        self.__drawPoint(forcePoint_screen, self.pointSize, self.colors['force_point'])


    def __drawPoint(self, p, size, color):
        """
        Draw a single point at point p given a pixel size and color.
        """
        self.__drawCircle(p, size / self.viewZoom, color, drawwidth=0)

    def __drawSegment(self, p1, p2, color):
        """
        Draw the line segment from p1-p2 with the specified color.
        """
        pygame.draw.aaline(self.screen, color, p1, p2)

    def __drawCircle(self, center, radius, color, drawwidth=1):
        """
        Draw a wireframe circle given the center, radius, axis of orientation and color.
        """
        radius *= self.viewZoom
        if radius < 1: radius = 1
        else: radius = int(radius)

        pygame.draw.circle(self.screen, color, center, radius, drawwidth)

    def __convertWorldtoScreen(self, point):
        self.viewOffset = self.viewCenter

        x = (point.x * self.viewZoom) - self.viewOffset.x
        y = (point.y * self.viewZoom) - self.viewOffset.y
        if self.flipY:
            y = self.screenSize.y - y

        return int(x), int(y)  # return tuple of integers

    def __vec2tupleInt(self, vec):
        return (int(vec.x),int(vec.y))