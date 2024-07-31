'''
class to store and analyse result data
'''

from Base import Base

class ResultData(Base):

    #constructor
    def __init__(self):
        Base.__init__(self)

        self.nodePos = {}           # selection of nodes to get the max. displacement
        self.nodeDis = {}           # node displacements
        self.nodeRFo = {}           # reaction forces
        self.sumRF0  = [0.,0.,0.]   # sum of reaction forces