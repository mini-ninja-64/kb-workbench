from dataclasses import dataclass
from decimal import Decimal
import FreeCAD
import Part
import typing

from abc import ABC, abstractmethod
from keyboard_layout_editor.parser import parseKLE, Vector, Key
from object_proxies import base


class PlateProxy(base.BaseProxy):
    @classmethod
    def create(cls, document: FreeCAD.Document):
        proxy = PlateProxy()
        internal_obj = typing.cast(
            Part.Part2DObject,
            document.addObject(
                type="Part::Part2DObjectPython", name="KeyboardPlate", objProxy=proxy
            ),
        )

        # For some reason type hinting is not able to find the inherited methods,
        # so a quick recast to one up the chain to "fix" it
        document_object = typing.cast(Part.Feature, internal_obj)
        document_object.addProperty(
            type="App::PropertyString",
            name="KLE",
            group="Keyboard Plate",
            doc="The Keyboard Layout Editor JSON contents",
        )
        document_object.addProperty(
            type="App::PropertyLength",
            name="Spacing",
            group="Keyboard Plate",
            doc="The spacing between consecutive key switches",
        ).Spacing = "19.05mm"  # type: ignore
        document_object.addProperty(
            type="App::PropertyLength",
            name="CutoutWidth",
            group="Keyboard Plate",
            doc="The width of a cutout between consecutive key switches",
        ).CutoutWidth = "14mm"  # type: ignore
        document_object.addProperty(
            type="App::PropertyLength",
            name="CutoutHeight",
            group="Keyboard Plate",
            doc="The width of a cutout between consecutive key switches",
        ).CutoutHeight = "14mm"  # type: ignore
        document_object.addProperty(
            type="App::PropertyLength",
            name="CutoutFilletRadius",
            group="Keyboard Plate",
            doc="The fillet radius of a cutout",
        ).CutoutFilletRadius = "0.5mm"  # type: ignore
        return (proxy, internal_obj)

    def onChanged(self, feature, prop):
        property_value = feature.getPropertyByName(prop)
        FreeCAD.Console.PrintMessage(
            f"Change property: {prop} = {property_value} ({type(property_value)})\n"
        )

    def execute(self, feature):
        kle_value: str = feature.getPropertyByName("KLE")  # type: ignore
        spacing = as_mm(feature.getPropertyByName("Spacing"))  # type: ignore

        cutout_width = as_mm(feature.getPropertyByName("CutoutWidth"))  # type: ignore
        cutout_height = as_mm(feature.getPropertyByName("CutoutHeight"))  # type: ignore

        cutout_radius = as_mm(feature.getPropertyByName("CutoutFilletRadius"))  # type: ignore

        layout = parseKLE(kle_value, spacing=spacing)
        print(layout)
        primitives: PrimitiveContainer = PrimitiveContainer([])

        if len(layout.keys) == 0:
            # TODO: HANDLE PROPERYL
            feature.Shape = None
            return
        plate_offset = -layout.keys[0].physical_centre
        for key in layout.keys:
            # FreeCAD uses inverted y-coords
            key_vec = (key.physical_centre + plate_offset) * Vector(
                Decimal(1), Decimal(-1)
            )
            cutout = RoundedRect(key_vec, cutout_radius, cutout_width, cutout_height)
            primitives.primitives += cutout.as_primitives().primitives

        feature.Shape = Part.makeCompound(primitives.as_shapes())


def as_mm(quant: FreeCAD.Units.Quantity) -> Decimal:
    mm_quant: float | FreeCAD.Units.Quantity = quant.getValueAs(
        FreeCAD.Units.MilliMetre
    )  #
    if isinstance(mm_quant, FreeCAD.Units.Quantity):
        return Decimal(mm_quant.toStr())
    elif isinstance(mm_quant, float):
        return Decimal(mm_quant)

    raise TypeError(
        f"Unexpected type {type(mm_quant)} produced by FreeCAD.Quantity::getValueAs"
    )


def as_freecad_vector(vec: Vector) -> FreeCAD.Vector:
    return FreeCAD.Vector(float(vec.x), float(vec.y), 0)


class Primitive(ABC):
    @abstractmethod
    def to_shape(self) -> typing.Optional[Part.Shape]: ...


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


# test kles
# [[{"a":7},"",{"x":-0.5},""]]
# [[{"a":7},""]]
# [["Num Lock","/","*","-"],["7\nHome","8\n↑","9\nPgUp",{"h":2},"+"],["4\n←","5","6\n→"],["1\nEnd","2\n↓","3\nPgDn",{"h":2},"Enter"],[{"w":2},"0\nIns",".\nDel"]]
# [["~\n`","!\n1","@\n2","#\n3","$\n4","%\n5","^\n6","&\n7","*\n8","(\n9",")\n0","_\n-","+\n=",{"w":2},"Backspace"],[{"w":1.5},"Tab","Q","W","E","R","T","Y","U","I","O","P","{\n[","}\n]",{"w":1.5},"|\n\\"],[{"w":1.75},"Caps Lock","A","S","D","F","G","H","J","K","L",":\n;","\"\n'",{"w":2.25},"Enter"],[{"w":2.25},"Shift","Z","X","C","V","B","N","M","<\n,",">\n.","?\n/",{"w":2.75},"Shift"],[{"w":1.5},"Ctrl",{"x":1,"w":1.5},"Alt",{"a":7,"w":7},"",{"a":4,"w":1.5},"Alt",{"x":1,"w":1.5},"Ctrl"]]
