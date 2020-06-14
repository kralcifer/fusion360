import adsk.core, adsk.fusion, adsk.cam, traceback
from urllib.request import urlopen
import json

# Global list to keep all event handlers in scope.
# This is only needed with Python.
handlers = []

app = adsk.core.Application.cast(None)
ui  = adsk.core.UserInterface.cast(None)


def run(context):
    try:
        global app, ui
        app = adsk.core.Application.get()
        ui = app.userInterface

        cmdDefs = ui.commandDefinitions
        
        buttonSample = cmdDefs.addButtonDefinition('klejson_button', 
                                                   'Keyboard Layout Editor JSON', 
                                                   'JSON describing switch plate layout',
                                                   '')
        
        commandCreated = CommandCreatedHandler()
        buttonSample.commandCreated.add(commandCreated)
        handlers.append(commandCreated)
        
        addInsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')        
        buttonControl = addInsPanel.controls.addCommand(buttonSample)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)        
        cmd = eventArgs.command

        inputs = cmd.commandInputs
        inputs.addStringValueInput('kleGist', 'KLE Gist', '')

        onValidate = ValidateInputsHandler()
        cmd.validateInputs.add(onValidate)
        handlers.append(onValidate)

        onExecute = CommandExecuteHandler()
        cmd.execute.add(onExecute)
        handlers.append(onExecute)


class ValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)
            inputs = eventArgs.firingEvent.sender.commandInputs

            kleGist = inputs.itemById('kleGist').value      
            if kleGist.startswith('https://gist.'):
                eventArgs.areInputsValid = True
            else:
                eventArgs.areInputsValid = False

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))	


class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            inputs = eventArgs.command.commandInputs

            # https://gist.githubusercontent.com/kralcifer/8195a1b0ca5c1bd6ac15888fd85ee0ba
            kleGist = inputs.itemById('kleGist').value
            response = urlopen("{}/raw".format(kleGist))
            keyboardLayout = json.load(response.fp)
            drawKeyboardPlate(keyboardLayout)

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def drawKeyboardPlate(keyboardLayout):
    global app, ui

    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        unitsMgr = design.fusionUnitsManager
        unitsMgr.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits

        root = design.rootComponent

        alreadyExists = False
        for occ in root.allOccurrences:
            if occ.component.name == 'cherry mx plate hole':
                cherryMxPlateHoleOcc = occ
                alreadyExists = True

        if not alreadyExists:
            project = app.data.activeProject
            cherryMxPlateHoleFile = None
            for file in project.rootFolder.dataFiles:
                if file.name == 'cherry mx plate hole':
                    cherryMxPlateHoleFile = file
                    break

            if cherryMxPlateHoleFile:
                cherryMxPlateHoleOcc = root.occurrences.addByInsert(cherryMxPlateHoleFile, adsk.core.Matrix3D.create(), True)            

        plateName = 'keyboard plate'
        if len(keyboardLayout) and type(keyboardLayout[0]) is dict and 'name' in keyboardLayout[0]:
            plateName = keyboardLayout[0]['name']
        plateOcc = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        plateOcc.component.name = plateName
        plateSketch = plateOcc.component.sketches.add(root.xYConstructionPlane)
        plateSketch.name = plateName

        topLeft = adsk.core.Point3D.create(0, 0, 0)
        bottomRight = adsk.core.Point3D.create(50, 20, 0)
        plateSketch.sketchCurves.sketchLines.addTwoPointRectangle(topLeft, bottomRight)        

        # cherryProfile = cherryMxPlateHoleOcc.component.sketch.profiles[0]
        # cherryProfile.

        cherrySketch = cherryMxPlateHoleOcc.component.sketches[0]
        matrix = adsk.core.Matrix3D.create()
        vector = adsk.core.Vector3D.create(3, 15)
        matrix.translation = vector

        collection = adsk.core.ObjectCollection.create()
        for line in cherrySketch.sketchCurves.sketchLines:   
            # for constraint in line.geometricConstraints:
            #     constraint.deleteMe()         
            collection.add(line)
        
        cherrySketch.copy(collection, matrix, plateSketch)

        # newOcc = plateOcc.component.occurrences.addExistingComponent(cherryMxPlateHoleOcc.component, trans)
        # plateSketch.copy(sketchEntities, transform, targetSketch)

        # sketch.isComputeDeferred = True
        # # interpret the layout and place plate holes!
        # sketch.isComputeDeferred = False

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))	

def stop(context):
    try:
        cmdDef = ui.commandDefinitions.itemById('klejson_button')
        if cmdDef:
            cmdDef.deleteMe()
            
        addinsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        cntrl = addinsPanel.controls.itemById('klejson_button')
        if cntrl:
            cntrl.deleteMe()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))	

        # # Get Sketch All Entitys
        # sktEntitys = adsk.core.ObjectCollection.create()
        # [sktEntitys.add(c) for c in sketch.sketchCurves]
        # [sktEntitys.add(p) for p in sketch.sketchPoints]

        # # get Rotatione matrix
        # angRad = radians(TwistAngle)
        # rotationAxis = adsk.core.Vector3D.create(0,0,1)
        # rotationCenter = sktCenterPnt.geometry.copy()
        # rotationMat = adsk.core.Matrix3D.create()
        # rotationMat.setToRotation(angRad, rotationAxis, rotationCenter)

        # # get Move matrix
        # ori = origin.copy()
        # sktmat = sketch.transform
        # sktmat.invert()
        # ori.transformBy(sktmat)
        # centerGeo = sktCenterPnt.geometry
        # vecMove = centerGeo.vectorTo(ori)
        # moveMat = adsk.core.Matrix3D.create()
        # moveMat.translation = vecMove

        # # Execute Rotatione&Move
        # mat3d = rotationMat.copy()
        # mat3d.transformBy(moveMat)
        # sketch.move(sktEntitys, mat3d)
        # sketch.isComputeDeferred = False

        # sketch.name=f'{airfoilName}_{Offset}'
