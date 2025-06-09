import adsk.core
import os
import math
import adsk.core, adsk.fusion, adsk.cam, traceback
from ...lib import fusionAddInUtils as futil
from ... import config
import random
import tempfile
import re
from pathlib import Path
app = adsk.core.Application.get()
ui = app.userInterface


# TODO *** Specify the command identity information. ***
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_cmdDialog'
CMD_NAME = 'Display Fastener Sizes'
CMD_Description = 'Visualize fastener major diameters in the design and create a color key for each size.'

# Specify that the command will be promoted to the panel.
IS_PROMOTED = True

# TODO *** Define the location where the command button will be created. ***
# This is done by specifying the workspace, the tab, and the panel, and the 
# command it will be inserted beside. Not providing the command to position it
# will insert it at the end.
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'InspectPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []


# Executed when add-in is run.
def start():
    # Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)

    # ******** Add a button into the UI so the user can run the command. ********
    # Get the target workspace the button will be created in.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Get the panel the button will be created in.
    panel = workspace.toolbarPanels.itemById(PANEL_ID)

    # Create the button command control in the UI after the specified existing command.
    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)

    # Specify if the command is promoted to the main toolbar. 
    control.isPromoted = IS_PROMOTED


# Executed when add-in is stopped.
def stop():
    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()


# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def command_created(args: adsk.core.CommandCreatedEventArgs):

    def create_color_key_palette(screw_colors):
        app = adsk.core.Application.get()
        ui = app.userInterface

        palette_id = 'colorKeyPalette'
        palette_name = 'Color Key'

        # Check if the palette already exists and delete it
        palette = ui.palettes.itemById(palette_id)
        if palette:
            palette.deleteMe()

        # Extract screw types and colors separately
        titles = list(screw_colors.keys())
        screws = sorted(titles, key=lambda x: float(x[1:]))
        sorted_screw_colors = {screw: screw_colors[screw] for screw in screws}
        color_list = list(sorted_screw_colors.values())

        # Create HTML content
        html_content = "<html><body>"
        for screw_type, color in zip(screws, color_list):
            color_hex = "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
            html_content += f"<div style='margin-bottom: 10px;'><span style='display: inline-block; width: 20px; height: 20px; background-color: {color_hex};'></span> {screw_type}</div>"
        html_content += "</body></html>"
        
        # Save HTML content to a temporary file
        temp_dir = os.path.dirname(os.path.abspath(__file__))
        temp_file_path = Path(temp_dir) / 'color_key_palette.html'
        with open(temp_file_path, 'w') as temp_file:
            temp_file.write(html_content)

        # Convert file path to URL format
        file_url = temp_file_path.as_uri()
     
        # Create a new palette
        palette = ui.palettes.add(palette_id, palette_name, file_url, True, True, True, 300, len(screw_colors) * 20 + 50)
        palette.dockingState = adsk.core.PaletteDockingStates.PaletteDockStateRight
        
        # Show the palette
        palette.isVisible = True

    def hsl_to_rgb(h, s, l):
        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = l - c / 2
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        return [int((r + m) * 255), int((g + m) * 255), int((b + m) * 255), 255]


    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        des = adsk.fusion.Design.cast(app.activeProduct)
        root = des.rootComponent

        palette_id = 'colorKeyPalette'

        palette = ui.palettes.itemById(palette_id)

        # Check to see if a custom graphics groups already exists and delete it.
        if root.customGraphicsGroups.count > 0:
            root.customGraphicsGroups.item(0).deleteMe()

            palette.isVisible = False

            for occ in root.occurrences:
                occ.component.opacity = 1.0
                occ.isLightBulbOn = True

            app.activeViewport.refresh()
            return
        
        # Create a graphics group on the root component.
        graphics = root.customGraphicsGroups.add()

        # List of metric sizes (add more as needed)
        metric_sizes = [
            "M1", "M1.2", "M1.4", "M1.6", "M2", "M2.5", "M3", "M3.5", "M4", "M5", "M6", "M8", "M10", "M12", "M16", "M20", "M24", "M30", "M36", "M42", "M48", "M56", "M64"
            ]

        imperial_sizes = [
            "1-64", "2-56", "3-48", "4-40", "5-40", "6-32", "8-32", "10-24", "10-32",
            "1/4-20", "5/16-18", "3/8-16", "7/16-14", "1/2-13", "9/16-12", "5/8-11", "3/4-10", "7/8-9", "1-8",
            "1/2-20", "1/4-28", "5/16-24", "3/8-24", "7/16-20", "9/16-18", "5/8-18", "3/4-16", "7/8-14", "1-12"
            ]

        screw_colors = {}
        for idx, size in enumerate(metric_sizes):
            screw_colors[size] = hsl_to_rgb((idx * 137.508) % 360, 0.7, 0.5)

        key_colors = {}

        # Sort screw types by length (longest first) to avoid partial matches
        sorted_screw_types = sorted(screw_colors.keys(), key=len, reverse=True)

        for occ in root.occurrences:
            comp_name = occ.component.name.replace(" ", "")
            for screw_type in sorted_screw_types:
                color = screw_colors[screw_type]
                futil.log(f"Component: {comp_name}, Trying: {screw_type}")
                if re.search(rf"-{re.escape(screw_type)}([xX\-_]|\b)", comp_name):
                    futil.log(f"Matched: {comp_name} as {screw_type}")
                    # Get the first body in the component.
                    body = occ.component.bRepBodies.item(0)
                    # Get the display mesh from the body.
                    bodyMesh = body.meshManager.displayMeshes.bestMesh
                    # Transform the mesh coordinates to the world space.
                    transform = occ.transform
                    coordsArray = bodyMesh.nodeCoordinatesAsDouble
                    transformedCoords = []
                    for i in range(0, len(coordsArray), 3):
                        point = adsk.core.Point3D.create(coordsArray[i], coordsArray[i+1], coordsArray[i+2])
                        point.transformBy(transform)
                        transformedCoords.extend([point.x, point.y, point.z])
                    # Draw the mesh using custom graphics triangles.
                    coords = adsk.fusion.CustomGraphicsCoordinates.create(transformedCoords)
                    mesh = graphics.addMesh(coords, bodyMesh.nodeIndices, 
                                        bodyMesh.normalVectorsAsDouble, bodyMesh.nodeIndices)
                    # Apply a specific color to the fastener.
                    colorInfo = color * len(bodyMesh.nodeCoordinates)
                    coords.colors = colorInfo
                    # Set the mesh to be colored using a vertex color effect.
                    vertexColor = adsk.fusion.CustomGraphicsVertexColorEffect.create()
                    mesh.color = vertexColor
                    # Add to key_colors for the palette
                    key_colors[screw_type] = color
                    # Hide the fastener in the browser tree.
                    occ.isLightBulbOn = False
                    break

        # Apply 10% opacity to all components
        for occ in root.occurrences:
            occ.component.opacity = 0.1

        # Refresh the graphics.
        app.activeViewport.refresh()

        create_color_key_palette(key_colors)
        # If no fasteners were detected, show a message box.
        if not key_colors:
            ui.messageBox("No fasteners detected.\n\nNote: This add-in currently only supports metric.")
            return

        create_color_key_palette(key_colors)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Execute Event')

    # TODO ******************************** Your code here ********************************

    # Get a reference to your command's inputs.
    inputs = args.command.commandInputs
    text_box: adsk.core.TextBoxCommandInput = inputs.itemById('text_box')
    value_input: adsk.core.ValueCommandInput = inputs.itemById('value_input')

    # Do something interesting
    text = text_box.text
    expression = value_input.expression
    msg = f'Your text: {text}<br>Your value: {expression}'
    ui.messageBox(msg)


# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Preview Event')
    inputs = args.command.commandInputs


# This event handler is called when the user changes anything in the command dialog
# allowing you to modify values of other inputs based on that change.
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.inputs

    # General logging for debug.
    futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')


# This event handler is called when the user interacts with any of the inputs in the dialog
# which allows you to verify that all of the inputs are valid and enables the OK button.
def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Validate Input Event')

    inputs = args.inputs
    
    # Verify the validity of the input values. This controls if the OK button is enabled or not.
    valueInput = inputs.itemById('value_input')
    if valueInput.value >= 0:
        args.areInputsValid = True
    else:
        args.areInputsValid = False
        

# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')

    global local_handlers
    local_handlers = []
