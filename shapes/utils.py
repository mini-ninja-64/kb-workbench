from decimal import Decimal
import FreeCAD

from shapes.core import Vector


def as_mm(quant: FreeCAD.Units.Quantity) -> Decimal:
    mm_quant: float | FreeCAD.Units.Quantity = quant.getValueAs(
        FreeCAD.Units.MilliMetre
    )
    if isinstance(mm_quant, FreeCAD.Units.Quantity):
        return Decimal(mm_quant.toStr())
    elif isinstance(mm_quant, float):
        return Decimal(mm_quant)

    raise TypeError(
        f"Unexpected type {type(mm_quant)} produced by FreeCAD.Quantity::getValueAs"
    )


def as_freecad_vector(vec: Vector) -> FreeCAD.Vector:
    return FreeCAD.Vector(float(vec.x), float(vec.y), 0)
