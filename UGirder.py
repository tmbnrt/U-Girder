'''
main class to control the Ugirder analysis
'''

# import abaqus package
from abaqus import *
from abaqusConstants import *
from caeModules import *

# to improve the development cycle
# reload everything
import Base
reload(Base)
import InputData
reload(InputData)
import ResultData
reload(ResultData)

#    |module     |class
from Base import Base
from InputData import InputData
from ResultData import ResultData

from math import sqrt,fabs

# U girder should be derived from the base class
class UGirder(Base):

    # Constructor
    def __init__(self):
        # Calling the Base class to intialize
        Base.__init__(self)

        # input data object
        # This is connection from Ugirder to Input data
        self.input = InputData()


        # result data object
        self.result = ResultData()

        ## helpers
        self.myModel        = None
        self.squareFaces    = None
        self.flangeFaces    = None
        self.webFaces       = None
        self.flatFaces      = None


    #create the system
    def createSystem(self):

        # do the following functions
        self.createModel()
        self.createPart()
        self.createMaterial()
        self.createProperties()
        self.assignSections()
        self.createMesh()

        # check the part
        ##print self.myPart
        ##print self.myPart.nodes
        ##print self.myPart.nodes[0]
        self.getFiberNodes()
        self.createInstance()



    # create the model
    def createModel(self):
        self.appendLog("> create model '%s'..." % self.input.prjName)

        try:
            del mdb.models[self.input.prjName]                  # object container
        except:
            pass
        self.myModel = mdb.Model(name=self.input.prjName)       # class

        # delete standard model
        try:
            del mdb.models['Model-1']
        except:
            pass

    # create part using a sketch
    def createPart(self):
        self.appendLog("> create part...")
        data = self.input

        # create the sketch
        s = self.myModel.ConstrainedSketch(name=data.prjName,
                                         sheetSize=data.h*3.)
        # create nodes
        xyPoints = ( (-data.uh , data.svt), (-data.sho, data.svt),
                     (-data.sho, data.svb), (-data.uh , data.svb),
                     (-data.uh ,-data.uv ), ( data.uh ,-data.uv ),
                     ( data.uh , data.svb), ( data.sho, data.svb),
                     ( data.sho, data.svt), ( data.uh , data.svt) )

        # create lines
        for i in range(1,len(xyPoints)):
            s.Line(point1 = xyPoints[i-1],
                   point2 = xyPoints[i])
        s.Line(point1 = xyPoints[0] , point2 = xyPoints[9])
        s.Line(point1 = xyPoints[6] , point2 = xyPoints[9])
        s.Line(point1 = xyPoints[0] , point2 = xyPoints[3])

        # create the part        (taken from macro recording)
        self.myPart = self.myModel.Part(name=data.prjName)
        # set depth (taken from macro recording ->  - create part - from sketch - set depth)
        self.myPart.BaseShellExtrude(sketch=s, depth=data.len)

    # create the material
    def createMaterial(self):
        self.appendLog("> create material...")
        data = self.input
        myMaterial = self.myModel.Material(name=self.input.material)
        myMaterial.Elastic(table=((data.yMod, data.nue),))
        myMaterial.Density(table=((data.density, ), ))

    # create properties    (thickness of the shells)
    def createProperties(self):
        data = self.input
        self.appendLog("> create properties")

        self.myModel.HomogeneousShellSection(name=data.square,
                                             material=data.material,
                                             thickness=data.t)
        self.myModel.HomogeneousShellSection(name=data.flange,
                                             material=data.material,
                                             thickness=data.tf)
        self.myModel.HomogeneousShellSection(name=data.web,
                                             material=data.material,
                                             thickness=data.tw)
        self.myModel.HomogeneousShellSection(name=data.flat,
                                             material=data.material,
                                             thickness=data.t)

    # assign the sections       --> select face!
    def assignSections(self):
        self.appendLog("> assign sections...")

        data = self.input

        ## Square
        #                               |give points to select face
        faces = self.myPart.faces.findAt( ( (-data.uh, data.sq/2.,data.len/2.),),
                                          ( (-data.uh-data.sq+data.t, data.sq/2.,data.len/2.),),
                                          ( (-data.uh-data.sq/2., data.svb,data.len/2.),),#
                                          ( (-data.uh-data.sq/2., data.svt,data.len/2.),),
                                          ( ( data.uh, data.sq/2.,data.len/2.),),
                                          ( ( data.uh+data.sq-data.t, data.sq/2.,data.len/2.),),
                                          ( ( data.uh+data.sq/2., data.svb,data.len/2.),),
                                          ( ( data.uh+data.sq/2., data.svt,data.len/2.),),)
        region = regionToolset.Region(faces=faces)
        self.myPart.SectionAssignment(region=region,
                                 sectionName=data.square)
        self.squareFaces = faces

        ## U-flange
        #                               |give points to select face
        faces = self.myPart.faces.findAt( ( (-data.uh,-data.uv/2.,data.len/2.),),
                                          ( ( data.uh,-data.uv/2.,data.len/2.),),)
        region = regionToolset.Region(faces=faces)
        self.myPart.SectionAssignment(region=region,
                                 sectionName=data.flange)
        self.flangeFaces = faces

        ## U-web
        #        (regarding geometry)           |give points to select face
        faces = self.myPart.faces.findAt( ( (0.,-data.uv,data.len/2.),),)
        region = regionToolset.Region(faces=faces)
        self.myPart.SectionAssignment(region=region,
                                 sectionName=data.web)
        self.webFaces = faces

        ## Flat steel
        #        (regarding geometry)           |give points to select face
        faces = self.myPart.faces.findAt( ( (0. , data.svt,data.len/2.),),)
        region = regionToolset.Region(faces=faces)
        self.myPart.SectionAssignment(region=region,
                                 sectionName=data.flat)
        self.flatFaces = faces


    # create mesh
    def createMesh(self):
        self.appendLog("> create mesh...")

        data = self.input

        # element type assignment
        elemType1 = mesh.ElemType(elemCode=S4)
        elemType2 = mesh.ElemType(elemCode=S3)
        #                                     |                 | set faces to mesh
        self.myPart.setElementType(regions=(self.squareFaces, self.flangeFaces, self.webFaces, self.flatFaces),
                                   elemTypes=(elemType1, elemType2))

        ## assign seeds: flat steel
        edges = self.myPart.edges.findAt( ( (0., data.svt,       0.), ),
                                          ( (0., data.svt, data.len), ) )
        self.myPart.seedEdgeByNumber(edges = edges,
                                     number = data.flatSeed)  # number of elements

        ## assign seeds: web
        edges = self.myPart.edges.findAt( ( (0.,-data.uv,       0.), ),
                                          ( (0.,-data.uv, data.len), ) )
        self.myPart.seedEdgeByNumber(edges = edges,
                                     number = data.webSeed)  # number of elements

        ## assign seeds: flange
        edges = self.myPart.edges.findAt( ( (-data.uh,-data.uv/2.,      0.), ),
                                          ( ( data.uh,-data.uv/2.,      0.), ),
                                          ( (-data.uh,-data.uv/2.,data.len), ),
                                          ( ( data.uh,-data.uv/2.,data.len), ), )
        self.myPart.seedEdgeByNumber(edges = edges,
                                     number = data.flangeSeed)

        ## assign seeds: square
        edges = self.myPart.edges.findAt(   ( (-data.uh               , data.sq/2.,                0.), ),
                                            ( (-data.uh-data.sq+data.t, data.sq/2.,                0.), ),
                                            ( (-data.uh-data.sq/2.    , data.svb  ,                0.), ),
                                            ( (-data.uh-data.sq/2.    , data.svt  ,                0.), ),
                                            ( ( data.uh               , data.sq/2.,                0.), ),
                                            ( ( data.uh+data.sq-data.t, data.sq/2.,                0.), ),
                                            ( ( data.uh+data.sq/2.    , data.svb  ,                0.), ),
                                            ( ( data.uh+data.sq/2.    , data.svt  ,                0.), ),
                                            ( (-data.uh               , data.sq/2.,          data.len), ),
                                            ( (-data.uh-data.sq+data.t, data.sq/2.,          data.len), ),
                                            ( (-data.uh-data.sq/2.    , data.svb  ,          data.len), ),
                                            ( (-data.uh-data.sq/2.    , data.svt  ,          data.len), ),
                                            ( ( data.uh               , data.sq/2.,          data.len), ),
                                            ( ( data.uh+data.sq-data.t, data.sq/2.,          data.len), ),
                                            ( ( data.uh+data.sq/2.    , data.svb  ,          data.len), ),
                                            ( ( data.uh+data.sq/2.    , data.svt  ,          data.len), ), )
        self.myPart.seedEdgeByNumber(edges = edges,
                                     number = data.squareSeed)

        # assign seeds: length
        edges = self.myPart.edges.findAt(   ( (-data.uh , data.svt, data.len/2.), ),
                                            ( (-data.sho, data.svt, data.len/2.), ),
                                            ( (-data.sho, data.svb, data.len/2.), ),
                                            ( (-data.uh , data.svb, data.len/2.), ),
                                            ( (-data.uh ,-data.uv , data.len/2.), ),
                                            ( ( data.uh ,-data.uv , data.len/2.), ),
                                            ( ( data.uh , data.svb, data.len/2.), ),
                                            ( ( data.sho, data.svb, data.len/2.), ),
                                            ( ( data.sho, data.svt, data.len/2.), ),
                                            ( ( data.uh , data.svt, data.len/2.), ), )
        self.myPart.seedEdgeByNumber(edges = edges,
                                     number = data.lengthSeed)

        # create mesh
        self.myPart.generateMesh()

    ### select nodes along a line through the system
    def getFiberNodes(self):
        self.appendLog("> select nodes...")

        data = self.input

        for node in self.myPart.nodes:

            # filter nodes
            dst = sqrt((node.coordinates[0] - data.uh)**2           # select nodes on the bottom
                       + (node.coordinates[1] + data.uv)**2)
            if dst > 1.: continue

            # store node
            self.result.nodePos[node.label] = node.coordinates

        self.appendLog("--no ---------x ---------y ---------z")
        for label in self.result.nodePos:
            node = self.result.nodePos[label]
            self.appendLog("%4d %10.2f %10.2f %10.2f" %
                           (label, node[0], node[1], node[2]) )

        self.appendLog("> %d nodes created." % len(self.myPart.nodes))
        self.appendLog("> %d elements created." % len(self.myPart.elements))
        self.appendLog("> %d nodes along fiber." % len(self.result.nodePos))

        # create instance
    def createInstance(self):
        self.appendLog("> create instance...")
        self.myInstance = self.myModel.rootAssembly.Instance(name = self.input.prjName,
                                                             part = self.myPart,
                                                             dependent = ON)

    # create a step
    def createStep(self,type):
        data = self.input
        self.appendLog("> create a '%s' step..." % data.stepName[type])

        data.stepType = type
        # linear calculation
        if type == data.LINEAR:
            self.myModel.StaticStep(name=data.stepName[type],
                                    previous = "Initial")
            self.createLoads();

        # stability analysis
        elif type == data.BUCKLING:
            self.myModel.BuckleStep(name=data.stepName[type],
                                    previous='Initial',
                                    numEigen=10,
                                    vectors=18,
                                    maxIterations=30)
            self.createLoads();

        # frequency analysis
        elif type == data.FREQUENCY:
            self.myModel.FrequencyStep(name=data.stepName[type],
                                       previous='Initial',
                                       numEigen=20,
                                       vectors=28,
                                       maxIterations=30,
                                       eigensolver=SUBSPACE)
            #self.createLoads();   # (WITHOUT LOADS)

        self.createBCs();

    def createBCs(self):
        data = self.input
        self.appendLog("> create BCs...")
        # vertical boundary conditions
        #                             |put in the edges
        edges = self.myInstance.edges.findAt(((0.,-data.uv,   0.   ),),
                                             ((0.,-data.uv,data.len),),)
        self.myModel.DisplacementBC(name='vertical support',
                                    createStepName=data.stepName[data.stepType],
                                    region=(edges,),
                                    u2=0.0)

        # --> select ONE node to fix all degrees of freedom that are necessary
        # fix rigid body modes
        vertices = self.myInstance.vertices.findAt(((data.uh,-data.uv,0.),),)
        self.myModel.DisplacementBC(name='rigid body modes',
                                    createStepName=data.stepName[data.stepType],
                                    region=(vertices,),
                                    u1=0.0,u3=0.0,ur2=0.0)

    # create pressure load
    def createLoads(self):
        data = self.input
        self.appendLog("> create loads...")

        faces1 = self.myInstance.faces.findAt(((         0.        ,data.svt,data.len/2.),),)
                                             #(( data.uh+data.sq/2.,data.svt,data.len/2.),),    #--> additional loads
                                             #((-data.uh-data.sq/2.,data.svt,data.len/2.),),)   #--> additional loads
        region = regionToolset.Region(side2Faces=faces1)     # side1Faces / side2Faces :  Brown / ... (up,down)
        self.myModel.Pressure(name='Pressure',
                              createStepName=data.stepName[data.stepType],
                              region=region,
                              magnitude=data.pressure)
        ############################################### Additional Loads ################################################
        faces2 = self.myInstance.faces.findAt((( data.uh+data.sq/2.,data.svt,data.len/2.),),)
        region2 = regionToolset.Region(side1Faces=faces2)
        self.myModel.Pressure(name='Pressure2',
                               createStepName=data.stepName[data.stepType],
                               region=region2,
                               magnitude=data.pressure)
        faces3 = self.myInstance.faces.findAt(((-data.uh-data.sq/2.,data.svt,data.len/2.),),)
        region3 = regionToolset.Region(side2Faces=faces3)
        self.myModel.Pressure(name='Pressure3',
                               createStepName=data.stepName[data.stepType],
                               region=region3,
                               magnitude=data.pressure)
        ################################################################################################################

    # create a job and run the calculation waiting for completion
    def runJob(self):
        data = self.input
        data.jobName = data.prjName + "-" + data.stepName[data.stepType]
        self.appendLog("> run Job '%s'..." % data.jobName)

        myJob = mdb.Job(name=data.jobName, model=data.prjName)
        myJob.submit()
        myJob.waitForCompletion()   # stop until job is ready

    # set the font size
    def setFontSize(self,size):
        fsize = int(size)*10
        self.viewport.viewportAnnotationOptions.setValues(
        triadFont='-*-verdana-medium-r-normal-*-*-%d-*-*-p-*-*-*' % fsize,
        legendFont='-*-verdana-medium-r-normal-*-*-%d-*-*-p-*-*-*' % fsize,
        titleFont='-*-verdana-medium-r-normal-*-*-%d-*-*-p-*-*-*' % fsize,
        stateFont='-*-verdana-medium-r-normal-*-*-%d-*-*-p-*-*-*' % fsize)
        self.viewport.viewportAnnotationOptions.setValues(
        legendMinMax=ON)

    # open result database and do the post processing
    def analyseResults(self):
        data = self.input

        # open database
        data.odbName = data.jobName + ".odb"
        self.appendLog("> open result data base '%s'..." % data.odbName)
        self.myOdb = session.openOdb(name=data.odbName)

        # select view-port and assign the result object
        self.viewport = session.viewports["Viewport: 1"]
        self.viewport.setValues(displayedObject = self.myOdb)
        self.setFontSize(14)

        # select vertical displacements
        self.viewport.odbDisplay.display.setValues(plotState=CONTOURS_ON_DEF)   # print vertical displacement

        self.viewport.odbDisplay.setPrimaryVariable(variableLabel='U',
                                                    outputPosition=NODAL,
                                                    refinement=(COMPONENT, 'U2'),)

        if data.stepType == data.LINEAR:
            self.analyseLinearStep()

    def analyseLinearStep(self):
        data   = self.input
        result = self.result

        # reaction forces
        result.sumRFo = [0.,0.,0.]

        frame = self.myOdb.steps[data.stepName[data.stepType]].frames[-1]
        rfo = frame.fieldOutputs['RF']

        # value.label -> node number
        # value.data  -> reaction force vector
        for value in rfo.values:
            if sqrt(value.data[0]**2
                   +value.data[1]**2
                   +value.data[2]**2) < 1.e-10: continue

            result.nodeRFo[value.nodeLabel] = value.data
            self.appendLog("%5d %10.3e %10.3e %10.3e" %
                           (value.nodeLabel,
                            value.data[0],value.data[1],value.data[2]))

            for i in range(3): result.sumRFo[i] += value.data[i]

        # print reaction forces
        self.appendLog("> reaction force: %10.3f %10.3f %10.3f kN" %
                       (result.sumRFo[0]/1000.,
                        result.sumRFo[1]/1000.,
                        result.sumRFo[2]/1000.,))

        # copy displacements into result container
        disp = frame.fieldOutputs['U']              # displacement: 'U' ,  reaction forces: 'RF'
        for value in disp.values:
            result.nodeDis[value.nodeLabel] = value.data

        # calculate the maximum displacement along the selected line
        maxDisp = 0.
        for label in result.nodePos:
            disp = result.nodeDis[label]
            if fabs(disp[1]) > maxDisp: maxDisp = fabs(disp[1])
        self.appendLog("> max. vertical displacement: %.2f mm" % maxDisp)

        # create result plot files
        varList = ['U1','U2','U3']
        for var in varList:
            # select the component of the displacements
            self.viewport.odbDisplay.setPrimaryVariable(variableLabel='U',
                                                        outputPosition=NODAL,
                                                        refinement=(COMPONENT, var),)

            # fit the plot
            self.viewport.view.fitView()

            # set file name
            png = data.jobName + "+" + var
            self.printPngFile(png)

        # print a png file
    def printPngFile(self,name):
        session.printOptions.setValues(vpBackground=OFF)    # switch off for white background in the graphic
        session.printToFile(fileName=name,
                            format=PNG,
                            canvasObjects=(self.viewport,))