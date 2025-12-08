import FreeCAD
import FreeCADGui
import typing
import Part
import PartDesign
from abc import ABC, abstractmethod

T = typing.TypeVar("T", bound=FreeCAD.DocumentObject)


# , typing.Generic[T]


class BaseProxy(ABC):
    @abstractmethod
    def execute(self, feature: Part.Feature):
        """Do something when a property has changed"""
        ...

    @abstractmethod
    def onChanged(self, feature: Part.Feature, prop: str):
        """Do something when doing a recomputation, this method is mandatory"""
        ...
