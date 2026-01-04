from decimal import Decimal
import FreeCAD
import Part
import typing

from keyboard_layout_editor.parser import parseKLE, Vector, Key
from keyboard_utilities.stab import as_geometry, stab_for_key_size, stab_family_type
from object_proxies import base
import plugin_utils
from shapes.core import Dimension
from shapes.geometry import RoundedRect
from shapes.primitive import PrimitiveContainer
from shapes.utils import as_mm

stabilizer_dimensions: dict[stab_family_type, Dimension] = {
    "cherry_mx": Dimension(Decimal("7"), Decimal("15"))
}


class PlateProxy(base.BaseProxy):
    @classmethod
    def create(cls, document: FreeCAD.Document):
        proxy = PlateProxy()
        internal_obj = typing.cast(
            Part.Part2DObject,
            document.addObject(
                type="Part::Part2DObjectPython",
                name="KeyboardPlate",
                objProxy=proxy,
                viewProxy=base.CustomIconViewProxy(
                    plugin_utils.get_plugin_resource("cut-plate.svg")
                ),
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
        ).KLE = "[[]]"  # type: ignore
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
        document_object.addProperty(
            type="App::PropertyEnumeration",
            name="StabilizerType",
            group="Keyboard Plate",
            doc="The type of stabilizer to use",
            enum_vals=["None", "CherryMX"],
        ).StabilizerType = "CherryMX"  # type: ignore
        # TODO: leaving empty for future feature
        document_object.addProperty(
            type="App::PropertyEnumeration",
            name="AcousticCutouts",
            group="Keyboard Plate",
            doc="The type of acoustic cutouts to use",
            enum_vals=["None"],
        ).StabilizerType = "None"  # type: ignore
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

        stab_family = as_stab_family(feature.getPropertyByName("StabilizerType"))  # type: ignore

        layout = parseKLE(kle_value, spacing=spacing)
        primitives: PrimitiveContainer = PrimitiveContainer([])

        if layout.has_keys():
            plate_offset = -layout.keys[0].physical_centre
            for key in layout.keys:
                # FreeCAD uses inverted y-coords
                key_vec = (key.physical_centre + plate_offset) * Vector(
                    Decimal(1), Decimal(-1)
                )
                cutout = RoundedRect(
                    key_vec, cutout_radius, cutout_width, cutout_height
                )
                if stab_family is not None:
                    stab = stab_for_key_size(
                        key_vec, Dimension(key.w, key.h), stab_family
                    )
                    if stab is not None:
                        stab_geoms = as_geometry(
                            stab, stabilizer_dimensions[stab_family], cutout_radius
                        )
                        for geom in stab_geoms:
                            print(geom)
                            primitives.primitives += geom.as_primitives().primitives
                    else:
                        # TODO: Handle
                        print("Error stab")

                primitives.primitives += cutout.as_primitives().primitives
            feature.Shape = Part.makeCompound(primitives.as_shapes())
        else:
            feature.Shape = Part.Shape()


def as_stab_family(string: str) -> typing.Optional[stab_family_type]:
    print(string)
    if string == "CherryMX":
        return "cherry_mx"
    return None


# test kles
# [[{"a":7},"",{"x":-0.5},""]]
# [[{"a":7},""]]
# [["Num Lock","/","*","-"],["7\nHome","8\n↑","9\nPgUp",{"h":2},"+"],["4\n←","5","6\n→"],["1\nEnd","2\n↓","3\nPgDn",{"h":2},"Enter"],[{"w":2},"0\nIns",".\nDel"]]
# [["~\n`","!\n1","@\n2","#\n3","$\n4","%\n5","^\n6","&\n7","*\n8","(\n9",")\n0","_\n-","+\n=",{"w":2},"Backspace"],[{"w":1.5},"Tab","Q","W","E","R","T","Y","U","I","O","P","{\n[","}\n]",{"w":1.5},"|\n\\"],[{"w":1.75},"Caps Lock","A","S","D","F","G","H","J","K","L",":\n;","\"\n'",{"w":2.25},"Enter"],[{"w":2.25},"Shift","Z","X","C","V","B","N","M","<\n,",">\n.","?\n/",{"w":2.75},"Shift"],[{"w":1.5},"Ctrl",{"x":1,"w":1.5},"Alt",{"a":7,"w":7},"",{"a":4,"w":1.5},"Alt",{"x":1,"w":1.5},"Ctrl"]]
