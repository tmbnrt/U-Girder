# -*- coding: mbcs -*-
# Do not delete the following import lines
from abaqus import *
from abaqusConstants import *
import __main__

def createPart():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    s1 = mdb.models['U-Girder'].ConstrainedSketch(name='__profile__', 
        sheetSize=200.0)
    g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
    s1.setPrimaryObject(option=STANDALONE)
    s1.sketchOptions.setValues(gridOrigin=(23.5, 0.0))
    s1.retrieveSketch(sketch=mdb.models['U-Girder'].sketches['U-Girder'])
    session.viewports['Viewport: 1'].view.fitView()
    p = mdb.models['U-Girder'].Part(name='Part-1', dimensionality=THREE_D, 
        type=DEFORMABLE_BODY)
    p = mdb.models['U-Girder'].parts['Part-1']
    p.BaseShellExtrude(sketch=s1, depth=140.0)
    s1.unsetPrimaryObject()
    p = mdb.models['U-Girder'].parts['Part-1']
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    del mdb.models['U-Girder'].sketches['__profile__']


def createSection():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    mdb.models['U-Girder'].HomogeneousShellSection(name='Section-1', 
        preIntegrate=OFF, material='steel', thicknessType=UNIFORM, 
        thickness=123.0, thicknessField='', idealization=NO_IDEALIZATION, 
        poissonDefinition=DEFAULT, thicknessModulus=None, temperature=GRADIENT, 
        useDensity=OFF, integrationRule=SIMPSON, numIntPts=5)


def assignSection():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=OFF, 
        engineeringFeatures=OFF)
    session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
        referenceRepresentation=ON)
    p1 = mdb.models['U-Girder'].parts['U-Girder']
    session.viewports['Viewport: 1'].setValues(displayedObject=p1)
    session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON, 
        engineeringFeatures=ON)
    session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
        referenceRepresentation=OFF)
    p = mdb.models['U-Girder'].parts['U-Girder']
    f = p.faces
    faces = f.getSequenceFromMask(mask=('[#5 ]', ), )
    region = p.Set(faces=faces, name='Set-1')
    p = mdb.models['U-Girder'].parts['U-Girder']
    p.SectionAssignment(region=region, sectionName='flange', offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)


def createBCs():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    a = mdb.models['U-Girder'].rootAssembly
    v1 = a.instances['U-Girder'].vertices
    verts1 = v1.getSequenceFromMask(mask=('[#11550 ]', ), )
    region = a.Set(vertices=verts1, name='Set-1')
    mdb.models['U-Girder'].DisplacementBC(name='BC-1', createStepName='Linear', 
        region=region, u1=0.0, u2=0.0, u3=0.0, ur1=UNSET, ur2=UNSET, ur3=UNSET, 
        amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', 
        localCsys=None)
    a = mdb.models['U-Girder'].rootAssembly
    v1 = a.instances['U-Girder'].vertices
    verts1 = v1.getSequenceFromMask(mask=('[#a8000 ]', ), )
    region = a.Set(vertices=verts1, name='Set-2')
    mdb.models['U-Girder'].DisplacementBC(name='BC-2', createStepName='Linear', 
        region=region, u1=0.0, u2=0.0, u3=UNSET, ur1=UNSET, ur2=UNSET, 
        ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, 
        fieldName='', localCsys=None)


def createAddLoads():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    a = mdb.models['U-Girder'].rootAssembly
    s1 = a.instances['U-Girder'].faces
    side1Faces1 = s1.getSequenceFromMask(mask=('[#8 ]', ), )
    region = a.Surface(side1Faces=side1Faces1, name='Surf-3')
    mdb.models['U-Girder'].Pressure(name='AddLoad', createStepName='Linear', 
        region=region, distributionType=UNIFORM, field='', magnitude=15.0, 
        amplitude=UNSET)


def editBackground():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    session.graphicsOptions.setValues(backgroundStyle=SOLID, 
        backgroundColor='#FFFFFF')


