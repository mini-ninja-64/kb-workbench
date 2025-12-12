import typing

from decimal import Decimal
from dataclasses import dataclass
from enum import Enum


@dataclass
class KeyboardStab: ...


@dataclass
class CentreToCentreKeyboardStab(KeyboardStab):
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


def cherry_mx_stab(width: Decimal) -> CentreToCentreKeyboardStab:
    return CentreToCentreKeyboardStab(
        width_mm=width,
        vertical_offset_mm=Decimal("1.25"),
    )


stab_family_type = typing.Literal["cherry_mx"]
stab_type_type = typing.Literal["std", "signature_plastics"]
stab_family_lookup_type = dict[stab_family_type, dict[stab_type_type, KeyboardStab]]

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
    key_size: typing.Tuple[Decimal, Decimal],
    stab_family: stab_family_type,
    stab_type: stab_type_type = "std",
) -> typing.Optional[KeyboardStab]:
    stab_size: typing.Optional[str] = None
    #
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

    return stab_lookup[stab_size][stab_family][stab_type]
