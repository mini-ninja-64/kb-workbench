import os
import typing
from pathlib import Path

import FreeCAD
import FreeCADGui
import PartDesign


def with_type(x: typing.Any) -> str:
    return f"{str(x)} ({type(x)})"


def get_plugin_path() -> Path:
    return Path(os.path.dirname(os.path.realpath(__file__)))


def try_add_to_body(
    document_obj: FreeCAD.DocumentObject, body: "PartDesign.Body | None"
) -> bool:
    """Tries to add a document object to an active body

    Args:
        document_obj (FreeCAD.DocumentObject): Document object to add to body
        active_body (PartDesign.Body | None): Body to add the object to

    Returns:
        bool: True if their was an active body to add the object to
    """
    if body is not None:
        body.addObject(document_obj)
        return True
    return False


def get_active_body() -> "PartDesign.Body | None":
    active_view = FreeCADGui.activeView()
    if active_view is not None:
        return typing.cast(
            "PartDesign.Body | None", active_view.getActiveObject("pdbody")
        )
    return None
