'''
Input Data to control the calculation
-geometry
-loads
-meshing
-analysis type
'''
from Base import Base

class InputData(Base):

    # constructor
    def __init__(self):
        Base.__init__(self)       # call the Base class

        self.prjName = "U-Girder"

        self.sq     =  140.0        # [mm]      Square profile
        self.t      =    5.6        # [mm]      Square thickness
        self.h      =  200.0        # [mm]      U-profile height
        self.w      =   75.0        # [mm]      U-profile width
        self.tf     =   11.5        # [mm]      U-profile flange
        self.tw     =    8.5        # [mm]      U-profile web
        self.len    = 3300.0        # [mm]      Length of the structure

        self.material   = "steel"
        self.yMod       = 210000.   # [N/mm^2]
        self.nue        = 0.3
        self.density    = 7.84e-06

        self.load       = 36.0      # [kN]

        self.square     = "square"
        self.flange     = "flange"
        self.web        = "web"
        self.flat       = "flat"    # Flat steel

        # mesh parameters
        self.maxNumber      = 1000  # (student version)
        self.squareSeed     = 1
        self.flatSeed       = 1
        self.flangeSeed     = 1
        self.webSeed        = 2
        self.lengthSeed     = None

        # calculation parameters
        self.LINEAR         = 0         # linear elastic
        self.BUCKLING       = 1         # stability
        self.FREQUENCY      = 2         # dynamic sensitive system
        self.stepType       = self.LINEAR                           # edit for calculation mode
        self.stepName       = ("Linear","Buckling","Frequency")     # (names for output files)
        self.jobName        = None

        self.setHelpers()

    # create some helpers
    def setHelpers(self):
        # U-profile
        self.uv = self.w - self.tw/2.               # exact points for the U-Profile's weld/flange nodes (vertical)
        self.uh = (self.h - self.tf)/2.             # exact points for the U-Profile's flange/weld (horizontal)
        self.sho = self.uh + self.sq - self.t       # horizontal outer coordinate for the square
        self.svb = self.t/2.                        # vertical coordinate (bottom) for the square
        self.svt = self.svb + self.sq - self.t      # vertical coordinate (top) for the square

        # optimize length seed for max number of elements (1000)
        self.lengthSeed = self.maxNumber/(2*self.flangeSeed + self.flatSeed + 8*self.squareSeed + self.webSeed + 1) - 1

        self.pressure = -self.load*1.e3/((self.uh*2.+(self.sq-self.t)*2.)*self.len)  #(PROJECT - pressure on all upper faces) # nachdem presure2 hinzugefuegt wurde, sind die RFo nicht mehr gleich der Gesamtkraft!

    # read the input data from an input file
    def readData(self):
        pass