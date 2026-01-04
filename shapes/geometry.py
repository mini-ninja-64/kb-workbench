from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

from shapes.core import Vector
from shapes.primitive import Arc, Line, Primitive, PrimitiveContainer


class BaseGeom(ABC):
    """
    A Class representing a higher geometric concept than a primitive, this is
    using millimetres which map 1:1 with the spatial co-ords in FreeCAD
    """

    @abstractmethod
    def as_primitives(self) -> PrimitiveContainer: ...


@dataclass
class RoundedRect(BaseGeom):
    centre: Vector
    fillet_radius: Decimal
    width: Decimal
    height: Decimal

    def as_primitives(self) -> PrimitiveContainer:
        # FreeCAD uses inverted y-coords
        top_left = self.centre - Vector(self.width / 2, -self.height / 2)
        bottom_left = top_left - Vector(Decimal(0), self.height)
        top_right = top_left + Vector(self.width, Decimal(0))
        bottom_right = bottom_left + Vector(self.width, Decimal(0))

        fillets_enabled = self.fillet_radius > 0

        primitives: list[Primitive] = [
            trim_y(Line(top_left, bottom_left), self.fillet_radius),
            trim_x(Line(bottom_left, bottom_right), self.fillet_radius),
            trim_y(Line(bottom_right, top_right), self.fillet_radius),
            trim_x(Line(top_left, top_right), self.fillet_radius),
        ]
        if fillets_enabled:
            primitives += [
                Arc.from_top_left(
                    top_left, self.fillet_radius, Decimal(90), Decimal(180)
                ),
                Arc.from_bottom_left(
                    bottom_left, self.fillet_radius, Decimal(180), Decimal(270)
                ),
                Arc.from_bottom_right(
                    bottom_right, self.fillet_radius, Decimal(270), Decimal(360)
                ),
                Arc.from_top_right(
                    top_right, self.fillet_radius, Decimal(360), Decimal(90)
                ),
            ]

        return PrimitiveContainer(primitives)


def trim_x(line: Line, dimension: Decimal) -> Line:
    if line.point1.x > line.point2.x:
        return Line(
            point1=line.point1 + Vector(-dimension, Decimal(0)),
            point2=line.point2 + Vector(dimension, Decimal(0)),
        )
    else:
        return Line(
            point1=line.point1 + Vector(dimension, Decimal(0)),
            point2=line.point2 + Vector(-dimension, Decimal(0)),
        )


def trim_y(line: Line, dimension: Decimal) -> Line:
    if line.point1.y > line.point2.y:
        return Line(
            point1=line.point1 + Vector(Decimal(0), -dimension),
            point2=line.point2 + Vector(Decimal(0), dimension),
        )
    else:
        return Line(
            point1=line.point1 + Vector(Decimal(0), dimension),
            point2=line.point2 + Vector(Decimal(0), -dimension),
        )
