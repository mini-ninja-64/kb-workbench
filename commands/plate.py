from commands.base import ResourcesDict
from .base import BaseCommand
import FreeCADGui
import FreeCAD
import object_proxies.plate
import plugin_utils


class GeneratePlateCommand(BaseCommand):
    def GetResources(self) -> ResourcesDict:
        return {
            "Pixmap": plugin_utils.get_plugin_resource("cut-plate.svg"),
            "MenuText": "Generate Plate",
            "ToolTip": "Generate a plate object",
        }

    def Activated(self):
        active_document = FreeCAD.activeDocument()
        if active_document is None:
            return

        (_, document_obj) = object_proxies.plate.PlateProxy.create(active_document)

        plugin_utils.try_add_to_body(document_obj, plugin_utils.get_active_body())

    def IsActive(self) -> bool:
        active_document = FreeCAD.ActiveDocument
        return active_document is not None


COMMAND_NAME = "Generate_Plate_Command"


def register():
    FreeCADGui.addCommand(COMMAND_NAME, GeneratePlateCommand())
    return COMMAND_NAME
