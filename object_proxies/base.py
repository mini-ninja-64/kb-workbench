from dataclasses import dataclass
import FreeCAD
import typing
import Part
from abc import ABC, abstractmethod

T = typing.TypeVar("T", bound=FreeCAD.DocumentObject)


class BaseProxy(ABC):
    @abstractmethod
    def execute(self, feature: Part.Feature):
        """Do something when a property has changed"""
        ...

    @abstractmethod
    def onChanged(self, feature: Part.Feature, prop: str):
        """Do something when doing a recomputation, this method is mandatory"""
        ...


@dataclass
class CustomIconViewProxy:
    icon: str

    def getIcon(self) -> str:
        return self.icon
