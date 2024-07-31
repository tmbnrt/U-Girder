'''
Main program of the girder calculation
it has a small case, because its not a class
Run file in Abaqus:
execfile(r"C:\Users\Tim\Documents\UNI\MASTER\MODULE\AoS\PROJECT\PROGRAMS\ugirder\runUGirder.py")
execfile()
'''

# set work directory
import os
os.chdir(r"C:\Users\Tim\Documents\UNI\MASTER\MODULE\AoS\PROJECT\PROGRAMS\ugirder")

from UGirder import UGirder

import UGirder
reload(UGirder)

from UGirder import UGirder

#create UGirder instance and run methods
sys = UGirder()
sys.createSystem()                      # geometry, mesh
sys.createStep(sys.input.LINEAR)        # run linear calculation
#sys.createStep(sys.input.BUCKLING)      # run buckling calculation
#sys.createStep(sys.input.FREQUENCY)     # run buckling calculation
sys.runJob()
#sys.openDatabase()
sys.analyseResults()

