from dataclasses import dataclass
from decimal import Decimal
import FreeCAD
import Part
import typing

from abc import ABC, abstractmethod
from keyboard_layout_editor.parser import Vector
from shapes.utils import as_freecad_vector


class Primitive(ABC):
    # TODO: Maybe this should not be an instance method, cos then its not decoupled from
    #       FreeCAD, anyway future problem
    @abstractmethod
    def to_shape(self) -> Part.Shape: ...


@dataclass
class Arc(Primitive):
    centre: Vector
    radius: Decimal
    start_angle: Decimal = Decimal(0)
    end_angle: Decimal = Decimal(360)

    @classmethod
    def from_top_left(
        cls,
        pos: Vector,
        radius: Decimal,
        start_angle: Decimal = Decimal(0),
        end_angle: Decimal = Decimal(360),
    ) -> typing.Self:
        return cls(
            centre=pos + Vector(radius, -radius),
            radius=radius,
            start_angle=start_angle,
            end_angle=end_angle,
        )

    @classmethod
    def from_top_right(
        cls,
        pos: Vector,
        radius: Decimal,
        start_angle: Decimal = Decimal(0),
        end_angle: Decimal = Decimal(360),
    ) -> typing.Self:
        return cls(
            centre=pos + Vector(-radius, -radius),
            radius=radius,
            start_angle=start_angle,
            end_angle=end_angle,
        )

    @classmethod
    def from_bottom_left(
        cls,
        pos: Vector,
        radius: Decimal,
        start_angle: Decimal = Decimal(0),
        end_angle: Decimal = Decimal(360),
    ) -> typing.Self:
        return cls(
            centre=pos + Vector(radius, radius),
            radius=radius,
            start_angle=start_angle,
            end_angle=end_angle,
        )

    @classmethod
    def from_bottom_right(
        cls,
        pos: Vector,
        radius: Decimal,
        start_angle: Decimal = Decimal(0),
        end_angle: Decimal = Decimal(360),
    ) -> typing.Self:
        return cls(
            centre=pos + Vector(-radius, radius),
            radius=radius,
            start_angle=start_angle,
            end_angle=end_angle,
        )

    def to_shape(self) -> Part.Shape:
        return Part.makeCircle(
            float(self.radius),
            as_freecad_vector(self.centre),
            FreeCAD.Vector(0, 0, 1),
            float(self.start_angle),
            float(self.end_angle),
        )


@dataclass
class Line(Primitive):
    point1: Vector
    point2: Vector

    def to_shape(self) -> Part.Shape:
        return Part.makeLine(
            as_freecad_vector(self.point1), as_freecad_vector(self.point2)
        )


@dataclass
class PrimitiveContainer:
    primitives: list[Primitive]

    def as_shapes(self) -> list[Part.Shape]:
        shapes = []
        for primitive in self.primitives:
            shapes.append(primitive.to_shape())
        return shapes
