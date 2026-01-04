from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Dimension:
    width: Decimal
    height: Decimal


@dataclass
class Vector:
    x: Decimal
    y: Decimal

    def __mul__(self, other: "Vector") -> "Vector":
        return Vector(self.x * other.x, self.y * other.y)

    def __sub__(self, other: "Vector") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y)

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __neg__(self) -> "Vector":
        return Vector(-self.x, -self.y)
