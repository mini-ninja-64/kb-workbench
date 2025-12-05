from commands.base import ResourcesDict
from .base import BaseCommand
import FreeCADGui
import FreeCAD


class GeneratePlateCommand(BaseCommand):
    def GetResources(self) -> ResourcesDict:
        return {
            "Pixmap": "",
            "MenuText": "Generate Plate",
            "ToolTip": "Generate a plate object",
        }

    def Activated(self):
        print("Generating plate")
        active_body = FreeCADGui.ActiveDocument.ActiveView.getActiveObject("pdbody")

        if active_body is None:
            # insert anywhere
            pass
        else:
            # insert into active body
            pass
        plate_object = FreeCAD.ActiveDocument.addObjects("Part::Part2DObject", "Plate")
        FreeCAD.ActiveDocument.ActiveObject.addObject(plate_object)

    def IsActive(self) -> bool:
        # TODO: Proper checks
        return True


COMMAND_NAME = "Generate_Plate_Command"


def register():
    FreeCADGui.addCommand(COMMAND_NAME, GeneratePlateCommand())
    return COMMAND_NAME
