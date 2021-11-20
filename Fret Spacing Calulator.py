#Author-James Cherry (TwoCherriesInstruments.com)
#string instrument Fret generatord
#Scale Lenth and nuber of frets are used to calculate lines in acurate position of frets.


import adsk.core, adsk.fusion, adsk.cam, traceback

DEFAULT_SCALE_LENGTH = 64.77
DEFAULT_FRET_CONSTANT = 17.817
DEFAULT_NUMBER_OF_FRETS = 21
MAX_NUMBER_OF_FRETS = 50
DEFAULT_NUT_WIDTH = 4.2
DEFAULT_BRIDGE_WIDTH = 5.4

ui = adsk.core.UserInterface.cast(None)

handlers = []
selected_sketch_plane = None

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        cmdD = ui.commandDefinitions
            
        button = cmdD.addButtonDefinition('FretCalcButtonId','Fret Spacing Calculator','Create custom fret spacing based on scale Length and vary the spacing constant','./Resources/Buttons')
        button.toolClipFilename = './Resources/Buttons/ToolClip.png'
        
        CommandCreated = CommandCreatedEventHandler()
        button.commandCreated.add(CommandCreated)
        handlers.append(CommandCreated)
       #Old Location  
        #addInsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        #buttonControl = addInsPanel.controls.addCommand(button)
        
       #New Location
        SolidCreatePanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        #sketchPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        #sketchPanel.controls.itemById('PatternDropDown')
        SolidCreatePanel.controls.addCommand(button)
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface  
        # Clean up the UI.
        cmdDef = ui.commandDefinitions.itemById('FretCalcButtonId')
        if cmdDef:
            cmdDef.deleteMe()   
        SolidCreatePanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        
        cntrl = SolidCreatePanel.controls.itemById('FretCalcButtonId')
        if cntrl:
           cntrl.deleteMe()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))	      

def drawFrets(ScaleLength, Fret_Constant, Number_of_frets, nutWidth, bridgeWidth, SketchPlane):
    ui = None
    
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct
        
        #root component
        rootComp = design.rootComponent
        sketches = rootComp.sketches
       
        sketch = sketches.add(SketchPlane)
        #draw a line
        lines = sketch.sketchCurves.sketchLines
        
        #draw points for nut and bridge lines
        sketchPoints = sketch.sketchPoints
    
        point1 = sketchPoints.add(adsk.core.Point3D.create(ScaleLength,-nutWidth/2,0))
        point2 = sketchPoints.add(adsk.core.Point3D.create(ScaleLength,nutWidth/2,0))
        point3 = sketchPoints.add(adsk.core.Point3D.create(0,-bridgeWidth/2,0))
        point4 = sketchPoints.add(adsk.core.Point3D.create(0,bridgeWidth/2,0))
        #draw brige and nut line from points
        bridgeLine = lines.addByTwoPoints(point3, point4)    
        nutLine = lines.addByTwoPoints(point1, point2)
        fbTopLine = lines.addByTwoPoints(nutLine.endSketchPoint, bridgeLine.endSketchPoint)
        fbBottomLine = lines.addByTwoPoints(nutLine.startSketchPoint, bridgeLine.startSketchPoint)
        
        working_scale_length = ScaleLength

        for i in range(Number_of_frets):    
           #draw fret lines 
           #distance from nut to first fret
           frets = working_scale_length / Fret_Constant
           #fret position
           x = working_scale_length - frets
           #draw fret lines
           fretLine = lines.addByTwoPoints(adsk.core.Point3D.create(x,-bridgeWidth/2,0), adsk.core.Point3D.create(x,bridgeWidth/2,0))
           #fretLine.trim(fretLine.endSketchPoint)
           #make fret line = to x
           working_scale_length = x
          
           
           
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class CommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
        cmd = eventArgs.command
        inputs = cmd.commandInputs
        app = adsk.core.Application.get()
        des = adsk.fusion.Design.cast(app.activeProduct) 

        # Scale Length, constant, nut width, bridge width,  numenr of frets inputs 
        inputs.addValueInput('scaleLength', 'Scale Length', des.unitsManager.defaultLengthUnits, adsk.core.ValueInput.createByReal(DEFAULT_SCALE_LENGTH))                            
        constant = inputs.addValueInput('constant', 'Fret Spacing Constant', '', adsk.core.ValueInput.createByReal(DEFAULT_FRET_CONSTANT)) 
        constant.isEnabled = False
        inputs.addBoolValueInput('checkbox', 'Change Default Constant', True, '', False)
        inputs.addIntegerSpinnerCommandInput("number_of_frets","Number Of Frets",1,MAX_NUMBER_OF_FRETS,1,DEFAULT_NUMBER_OF_FRETS)       
        inputs.addValueInput('nutWidth', 'Nut Width', des.unitsManager.defaultLengthUnits, adsk.core.ValueInput.createByReal(DEFAULT_NUT_WIDTH))
        inputs.addValueInput('bridgeWidth', 'Bridge Width', des.unitsManager.defaultLengthUnits, adsk.core.ValueInput.createByReal(DEFAULT_BRIDGE_WIDTH))
        face = inputs.addSelectionInput('planeSelection', 'Sketch Plane', 'Select a constrution plane')
        face.addSelectionFilter(adsk.core.SelectionCommandInput.ConstructionPlanes)
        face.setSelectionLimits(1, 1)

        onExecute = CommandExecuteHandler()
        cmd.execute.add(onExecute)
        handlers.append(onExecute)
        
        onInputChanged = InputChangedHandler()
        cmd.inputChanged.add(onInputChanged)
        handlers.append(onInputChanged)
        
        onPreview = CommandExecutePreviewHandler()
        cmd.executePreview.add(onPreview)
        handlers.append(onPreview)

        onSelect = SelectHandler()
        cmd.select.add(onSelect)
        handlers.append(onSelect)


class SelectHandler(adsk.core.SelectionEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        global selected_sketch_plane
        try:
            selected = adsk.fusion.ConstructionPlane.cast(args.selection.entity) 
            if selected:
                selected_sketch_plane = selected
            else:
                selected_sketch_plane = None
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def GetDefaultConstructionPlane():
    app = adsk.core.Application.get()
    design = app.activeProduct
    rootComp = design.rootComponent
    return rootComp.xYConstructionPlane

def DrawFromEventArgs(eventArgs):
    # Get the values from the command inputs. 
    inputs = eventArgs.command.commandInputs

    # Pull out the values from the inputs.
    scaleLength = inputs.itemById('scaleLength').value        
    constant = inputs.itemById('constant').value
    number_of_frets = inputs.itemById('number_of_frets').value
    nut_width = inputs.itemById('nutWidth').value
    bridge_width = inputs.itemById('bridgeWidth').value

    number_of_frets = min(number_of_frets, MAX_NUMBER_OF_FRETS)

    sp = selected_sketch_plane
    if not sp:
        sp = GetDefaultConstructionPlane()
    drawFrets(scaleLength, constant, number_of_frets, nut_width, bridge_width, sp)

class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandEventArgs.cast(args)
        DrawFromEventArgs(eventArgs)
       
        
class InputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.InputChangedEventArgs.cast(args)
        # Check the value of the check box.
        changedInput = eventArgs.input
        if changedInput.id == 'checkbox':
            inputs = eventArgs.firingEvent.sender.commandInputs
            constantValue = inputs.itemById('constant')
			
            # Change the visibility of the constant
            if changedInput.value == True:
                constantValue.isEnabled = True
            else:
                constantValue.isEnabled = False 
            
class CommandExecutePreviewHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = adsk.core.CommandEventArgs.cast(args)
        DrawFromEventArgs(eventArgs)
       
        # This will result in the execute event not being fired.
        eventArgs.isValidResult = True

            
