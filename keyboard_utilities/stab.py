import typing

from decimal import Decimal
from dataclasses import dataclass

from keyboard_layout_editor.parser import Key
from shapes.core import Dimension, Vector
from shapes.geometry import BaseGeom, RoundedRect


@dataclass
class KeyboardStab: ...


@dataclass
class CentreToCentreKeyboardStab(KeyboardStab):
    centre: Vector
    width_mm: Decimal
    vertical_offset_mm: Decimal


standard_stabilizer_widths = typing.Literal[
    "2u",
    "3u",
    # "4u", TODO: RESEARCH required for MCKRL
    "6u",
    "6.25u",
    "7u",
    "8u",
]


def cherry_mx_stab(
    width: Decimal,
) -> typing.Callable[[Vector], CentreToCentreKeyboardStab]:
    return lambda key_centre: CentreToCentreKeyboardStab(
        centre=key_centre,
        width_mm=width,
        vertical_offset_mm=Decimal("1.25"),
    )


stab_generator_type = typing.Callable[[Vector], KeyboardStab]
stab_family_type = typing.Literal["cherry_mx"]
stab_type_type = typing.Literal["std", "signature_plastics"]
stab_family_lookup_type = dict[
    stab_family_type, dict[stab_type_type, stab_generator_type]
]

stab_lookup: dict[standard_stabilizer_widths, stab_family_lookup_type] = {
    "2u": {"cherry_mx": {"std": cherry_mx_stab(Decimal("23.876"))}},
    "3u": {"cherry_mx": {"std": cherry_mx_stab(Decimal("38.1"))}},
    "6u": {
        "cherry_mx": {
            "std": cherry_mx_stab(Decimal("95.25")),
            "signature_plastics": cherry_mx_stab(Decimal("76.2")),
        },
    },
    "6.25u": {"cherry_mx": {"std": cherry_mx_stab(Decimal("100"))}},
    "7u": {"cherry_mx": {"std": cherry_mx_stab(Decimal("114.3"))}},
    "8u": {"cherry_mx": {"std": cherry_mx_stab(Decimal("133.35"))}},
}


def stab_for_key_size(
    physical_centre: Vector,
    key_dimension: Dimension,
    stab_family: stab_family_type,
    stab_type: stab_type_type = "std",
) -> typing.Optional[CentreToCentreKeyboardStab]:
    stab_size: typing.Optional[str] = None
    # TODO: handle vertical stabs
    # vertical = height > width
    key_size = max(key_dimension.width, key_dimension.height)

    if key_size >= Decimal("2") and key_size < Decimal("3"):
        stab_size = "2u"
    elif key_size == Decimal("3"):
        stab_size = "3u"
    elif key_size == Decimal("6"):
        stab_size = "6u"
    elif key_size == Decimal("6.25"):
        stab_size = "6.25u"
    elif key_size == Decimal("7"):
        stab_size = "7u"
    elif key_size >= Decimal("8") and key_size <= Decimal("10"):
        stab_size = "8u"

    if stab_size is None:
        return None

    return stab_lookup[stab_size][stab_family][stab_type](physical_centre)


def as_geometry(
    stab: CentreToCentreKeyboardStab,
    cutout_dimensions: Dimension,
    fillet_radius: Decimal,
) -> list[BaseGeom]:
    cutout_width = cutout_dimensions.width
    cutout_height = cutout_dimensions.height
    stab_half = stab.width_mm / 2
    return [
        RoundedRect(
            centre=stab.centre - Vector(stab_half, stab.vertical_offset_mm),
            fillet_radius=fillet_radius,
            width=cutout_width,
            height=cutout_height,
        ),
        RoundedRect(
            centre=stab.centre + Vector(stab_half, -stab.vertical_offset_mm),
            fillet_radius=fillet_radius,
            width=cutout_width,
            height=cutout_height,
        ),
    ]
