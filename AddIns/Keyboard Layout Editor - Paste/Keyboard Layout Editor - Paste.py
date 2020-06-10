import adsk.core, adsk.fusion, adsk.cam, traceback
import html
import json

# Global list to keep all event handlers in scope.
# This is only needed with Python.
handlers = []

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

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
        
        # Get the command
        cmd = eventArgs.command

        # Get the CommandInputs collection to create new command inputs.            
        inputs = cmd.commandInputs

        # Create a string input to get the kle JSON.
        klejson = inputs.addTextBoxCommandInput('klejson', 'kle JSON', '', 5, False)

        # Connect to the execute event.
        onExecute = SampleCommandExecuteHandler()
        cmd.execute.add(onExecute)
        handlers.append(onExecute)


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

# Event handler for the validateInputs event.
class SampleCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)
        inputs = eventArgs.firingEvent.sender.commandInputs

        # Check to see if the check box is checked or not.
        # klejson = inputs.itemById('klejson').valueOne        
        # _ui.messageBox('hi')
        
        # if klejson.value == True:
        #     eventArgs.isValid = True
        # else:
        #     # Verify that the scale is greater than 0.1.
        #     scaleInput = inputs.itemById('heightScale')
        #     if scaleInput.value < .1:
        #         eventArgs.areInputsValid = False
        #     else:
        #         eventArgs.areInputsValid = True

def drawKeyboardPlate(keyboardLayout):
    # Get the active sketch. 
    app = adsk.core.Application.get()
    sketch = adsk.fusion.Sketch.cast(app.activeEditObject)
    sketch.isComputeDeferred = True

    # interpret the layout and place plate holes!
    
    sketch.isComputeDeferred = False

def stop(context):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        # Clean up the UI.
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