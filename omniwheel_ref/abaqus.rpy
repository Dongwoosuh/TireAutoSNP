# -*- coding: mbcs -*-
#
# Abaqus/Viewer Release 2020 replay file
# Internal Version: 2019_09_14-02.49.31 163176
# Run by water on Mon Jan 13 16:16:08 2025
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=316.706268310547, 
    height=173.8037109375)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from viewerModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
o2 = session.openOdb(name='Design_IDEA3.odb')
#: Model: E:/Dongwoo/TeamWork/Hyunday_omni_wheels/TireAutoSNP/omniwheel_ref/Design_IDEA3.odb
#: Number of Assemblies:         1
#: Number of Assembly instances: 0
#: Number of Part instances:     10
#: Number of Meshes:             11
#: Number of Element Sets:       18
#: Number of Node Sets:          41
#: Number of Steps:              5
session.viewports['Viewport: 1'].setValues(displayedObject=o2)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].view.setValues(nearPlane=238.159, 
    farPlane=871.672, width=215.83, height=100.582, viewOffsetX=-0.450587, 
    viewOffsetY=-38.221)
session.viewports['Viewport: 1'].view.setValues(nearPlane=243.002, 
    farPlane=866.829, width=182.911, height=85.2406, viewOffsetX=1.83141, 
    viewOffsetY=-36.7186)
session.viewports['Viewport: 1'].view.setValues(nearPlane=245.814, 
    farPlane=885.938, width=185.027, height=86.2269, cameraPosition=(383.548, 
    242.996, 357.365), cameraUpVector=(-0.44589, 0.725302, -0.524518), 
    cameraTarget=(108.133, 47.7175, 16.6286), viewOffsetX=1.8526, 
    viewOffsetY=-37.1435)
