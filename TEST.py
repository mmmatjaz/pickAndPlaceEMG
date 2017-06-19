import numpy as np
from Box2D import b2Vec2

npa=np.empty([3,2])
boom=[]
boom.append(b2Vec2(1,2))
boom.append(b2Vec2(2,3))
boom.append(b2Vec2(4,3))

for i,b in enumerate(boom):
    print i
    print b
    print " "
    npa[i,:]=[b.x,b.y]


print npa