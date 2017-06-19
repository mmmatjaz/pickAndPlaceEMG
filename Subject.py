import json
import random
import argparse

from Trial import *
from CalibMyo import CalibMyo
from TKwins import IntroWin,PopUp

class Subject(object):
    def __init__(self, name='jdoe', logging=True, cocoOnly=False, cocoThresh=10.):
        self.cocoThresh=cocoThresh
        self.logging=logging
        self.fname= "../results/"+name+\
                    '_c'+str(cocoThresh)+\
                    time.strftime("%Y%m%d_%H%M%S")+\
                    ".json"
        self.table=self.generateProtocol(cocoOnly)
        self.saveJson()

    def go(self):
        i=0
        for trialInfo in self.table:
            print "\n\ntrial %d\n\n" % (i+1)
            if i==0 or trialInfo['condition'] is not self.table[i-1]['condition']:
                str='The controller stiffness\n is '
                if trialInfo['condition'] is Condition.VAR:
                    str+="in your control"
                elif trialInfo['condition'] is Condition.LOW:
                    str+="LOW"
                else:
                    str+="HIGH"
                PopUp(str)

            i+=1
            trial = Trial(
                condition = trialInfo['condition'],
                objType   = trialInfo['object'],
                shouldLog = self.logging,
                cocoThr   = self.cocoThresh)
            trial.loop()
            outcome,trialTime,accuracy,trialLog=trial.getTrialData()
            trialInfo['outcome']=outcome
            trialInfo['time']=trialTime
            trialInfo['file']=trialLog
            trialInfo['accuracy']=accuracy
            self.saveJson()

            time.sleep(1.)
            if outcome is SystemState.INTERRUPTED:
                choice = raw_input("finish?")
                if 'y' in choice:
                    return

    @staticmethod
    def generateProtocol(cocoOnly=False):
        trialsEach=5#5
        trialTable=[]
        for x in range(0,2):
            for cond in Condition:
                if cocoOnly:
                    cond=Condition.VAR
                trialSet=[]
                for i in range(0,trialsEach):
                    for ot in ObjectType:
                        trialInfo={'condition' : cond,
                                    'object' : ot,
                                    'outcome': None,
                                    'accuracy' : None,
                                    'time' : None,
                                    'file' : None}
                        trialSet.append(trialInfo)
                random.shuffle(trialSet)
                trialTable+=trialSet
        return trialTable

    def saveJson(self):
        if not self.logging:
            return
        with open(self.fname, 'w') as outfile:
            js=json.dumps(self.table)
            js=js.replace('},','},\n').replace('../results/','')
            for x in Condition:
                js=js.replace(str(x),'"%s"' % x.name)
            for x in ObjectType:
                js=js.replace(str(x),'"%s"' % x.name)
            for x in SystemState:
                js=js.replace(str(x),'"%s"' % x.name)
            #print js
            outfile.write(js)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Subject class')
    parser.add_argument('-nl',action="store_false", dest="log",     default=True,
                        help='Flag to DISABLE logging')
    parser.add_argument('-c', action="store",       dest="coco",    type=float,     default=0.,
                        help='Set coco threshold')
    parser.add_argument('-n', action="store",       dest="name",    default='janez',
                        help='Set subject name')
    parser.add_argument('-p', action="store_true",  dest="cocoOnly",default=False,
                        help='Set practice mode - coco only')

    res=parser.parse_args()

    if res.coco == 0.:
        res.coco = CalibMyo().go()

    IntroWin()

    Subject(name      = res.name,
            logging   = res.log,
            cocoOnly  = res.cocoOnly,
            cocoThresh= res.coco).go()
