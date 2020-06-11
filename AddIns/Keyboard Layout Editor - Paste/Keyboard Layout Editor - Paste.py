import adsk.core, adsk.fusion, adsk.cam, traceback
import html
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

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions
        
        # Create a button command definition.
        buttonSample = cmdDefs.addButtonDefinition('klejson_button', 
                                                   'Keyboard Layout Editor JSON', 
                                                   'JSON describing switch plate layout',
                                                   '')
        
        # Connect to the command created event.
        sampleCommandCreated = SampleCommandCreatedEventHandler()
        buttonSample.commandCreated.add(sampleCommandCreated)
        handlers.append(sampleCommandCreated)
        
        # Get the ADD-INS panel in the model workspace. 
        addInsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        
        # Add the button to the bottom of the panel.
        buttonControl = addInsPanel.controls.addCommand(buttonSample)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the commandCreated event.
class SampleCommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)        
        cmd = eventArgs.command
        inputs = cmd.commandInputs

        klejson = inputs.addTextBoxCommandInput('klejson', 'kle JSON', '', 5, False)

        onExecute = SampleCommandExecuteHandler()
        cmd.execute.add(onExecute)
        handlers.append(onExecute)

        onValidate = ValidateInputs()
        cmd.validateInputs.add(onValidate)
        handlers.append(onValidate)


# Event handler for the execute event.
class SampleCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            # Get the values from the command inputs. 
            inputs = eventArgs.command.commandInputs

            klejson = inputs.itemById('klejson').text
            unescaped = html.unescape(klejson)
            newlinesRemoved = unescaped.replace('\n', '')
            keyboardLayout = json.loads(newlinesRemoved)
            drawKeyboardPlate(keyboardLayout)

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class ValidateInputs(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)
            inputs = eventArgs.firingEvent.sender.commandInputs

            klejson = inputs.itemById('klejson').text        
            if len(klejson) > 0:
                eventArgs.areInputsValid = True
            else:
                eventArgs.areInputsValid = False

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))	


def drawKeyboardPlate(keyboardLayout):
    try:
        project = app.data.activeProject
        cherryMxPlateHoleFile = None
        for file in project.rootFolder.dataFiles:
            if file.name == 'cherry mx plate hole':
                cherryMxPlateHoleFile = file
                break

        des = adsk.fusion.Design.cast(app.activeProduct)
        root = des.rootComponent
        occ = root.occurrences.addByInsert(cherryMxPlateHoleFile, adsk.core.Matrix3D.create(), True)            

        # Get the active sketch. 
        app = adsk.core.Application.get()
        sketch = adsk.fusion.Sketch.cast(app.activeEditObject)
        sketch.isComputeDeferred = True

        # interpret the layout and place plate holes!
        
        sketch.isComputeDeferred = False

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