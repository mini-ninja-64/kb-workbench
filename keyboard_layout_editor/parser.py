# https://github.com/ijprest/keyboard-layout-editor/wiki/Serialized-Data-Format
import json
import typing
from decimal import Decimal

from plugin_utils import with_type

from dataclasses import dataclass

from shapes.core import Vector


class SettingScope:
    Global = 0  # Effects all subsequent keys
    Local = 1  # Only effects the next key


class Setting:
    def __init__(self, s, v, t, keyUpdate=None):
        self.scope = s
        self.value = v
        self.expectedType = t
        self.__updater = keyUpdate  # (varName, keyObject, proposedValue)

    def keyUpdate(self, varName, key):
        # TODO: type check
        # if setting has no value we can skip it
        if self.value is None:
            return

        if self.__updater is not None:
            self.__updater(varName, key, self.value)

        # if locally scoped reset after updating a key
        if self.scope is SettingScope.Local:
            self.value = None


def setKeyVariable(varName, key, value):
    return setattr(key, varName, Decimal(value))


def addToKeyVariable(varName, key, value):
    return setattr(key, varName, getattr(key, varName) + Decimal(value))


settings = {
    "x": Setting(
        SettingScope.Local, None, Decimal, keyUpdate=addToKeyVariable
    ),  # These specify x and y values to be added to the current coordinates.
    "y": Setting(
        SettingScope.Local, None, Decimal, keyUpdate=addToKeyVariable
    ),  # For example, specifying x = 1 will leave a 1.0x gap between the previous key and the next one.
    "w": Setting(
        SettingScope.Local, None, Decimal, keyUpdate=setKeyVariable
    ),  # These specify the width and height of the next key.
    "h": Setting(SettingScope.Local, None, Decimal, keyUpdate=setKeyVariable),
    "x2": Setting(
        SettingScope.Local, None, Decimal, keyUpdate=setKeyVariable
    ),  # These specify the offset and size of the second rectangle that is used to define oddly-shaped keys.
    "y2": Setting(SettingScope.Local, None, Decimal, keyUpdate=setKeyVariable),
    "w2": Setting(SettingScope.Local, None, Decimal, keyUpdate=setKeyVariable),
    "h2": Setting(SettingScope.Local, None, Decimal, keyUpdate=setKeyVariable),
    "l": Setting(
        SettingScope.Local, None, bool
    ),  # Specifies that the next key is a "stepped" key (often used for "Caps Lock" keys).
    "n": Setting(
        SettingScope.Local, None, bool
    ),  # Specifies that the next key is a "homing" key (which usually renders as a little "nub").
    "d": Setting(
        SettingScope.Local, None, bool
    ),  # Specifies that the next key is a "decal" (does not render the keycap, only the legends).
    "c": Setting(
        SettingScope.Global, None, str
    ),  # Specifies the color of the keycap, in "#rrggbb" format, e.g., "#ff0000" indicates red.
    "t": Setting(
        SettingScope.Global, None, str
    ),  # Specifies the color of the text on the keycap, in "#rrggbb" format.
    "g": Setting(
        SettingScope.Global, None, bool
    ),  # Specifies that the following keys are 'ghosted'
    "a": Setting(
        SettingScope.Global, None, int
    ),  # Specifies the text alignment. This is a bit field of one or more of the following:
    # 0x01 - Center labels in the X direction
    # 0x02 - Center labels in the Y direction
    # 0x04 - Center the side-printed text
    "f": Setting(
        SettingScope.Global, None, int
    ),  # Specifies the primary & secondary font heights, on a scale of 1-9 (default 3)
    "p": Setting(
        SettingScope.Global, None, str
    ),  # Specifies the profile & row of the keycaps. Supported profiles: DCS, DSA, SA. Supported profile "modifiers": SPACE, R1, R2, R3, R4, R5
    # The following properties are not implemented, but are proposed for future use:
    "s": Setting(
        SettingScope.Global, None, str
    ),  # Style of the keycap; this is a reference to a keycap prototype.
}


@dataclass
class Key:
    x: Decimal
    y: Decimal
    w: Decimal
    h: Decimal
    parent: "KeyboardLayout"
    x2: Decimal | None = None
    y2: Decimal | None = None
    w2: Decimal | None = None
    h2: Decimal | None = None

    def position(self) -> Vector:
        return Vector(self.x, self.y)

    def centre(self) -> Vector:
        return Vector(
            self.x + (self.w / Decimal("2")), self.y + (self.h / Decimal("2"))
        )

    @property
    def physical_position(self) -> Vector:
        return self.position() * Vector(self.parent.spacing, self.parent.spacing)

    @property
    def physical_centre(self) -> Vector:
        return self.centre() * Vector(self.parent.spacing, self.parent.spacing)

    @property
    def physical_width(self) -> Decimal:
        return self.w * self.parent.spacing

    @property
    def physical_height(self) -> Decimal:
        return self.h * self.parent.spacing


@dataclass
class KeyboardLayout:
    spacing: Decimal
    keys: list[Key]

    def has_keys(self):
        return len(self.keys) > 0


def parseKLE(string: str, spacing: Decimal = Decimal("19.05")) -> KeyboardLayout:
    kleJSON = json.loads(string)

    keyboardLayout = KeyboardLayout(spacing=spacing, keys=[])
    y = Decimal("0")
    for keyset in kleJSON:
        if type(keyset) is dict:
            # TODO: handling author info etc in keyboard layout class
            continue
        elif type(keyset) is list:
            x = Decimal("0")
            for kleItem in keyset:
                if type(kleItem) is dict:
                    for settingCode in kleItem:
                        settings[settingCode].value = kleItem[settingCode]
                elif type(kleItem) is str:
                    # generate default key item
                    key = Key(x, y, Decimal("1"), Decimal("1"), keyboardLayout)

                    # apply setting modifiers to key
                    for settingCode in settings:
                        setting = settings[settingCode]

                        if setting.value is not None:
                            if settingCode == "y":
                                y += Decimal(setting.value)

                            if settingCode == "x":
                                x += Decimal(setting.value)

                        if hasattr(key, settingCode):
                            setting.keyUpdate(settingCode, key)

                    x += Decimal(key.w)

                    # print(
                    #     f"x: {with_type(key.x)}, y: {with_type(key.y)}, w: {with_type(key.w)}, h: {with_type(key.h)}"
                    # )
                    keyboardLayout.keys.append(key)

        y += Decimal("1")

    return keyboardLayout
