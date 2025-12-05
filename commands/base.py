from abc import ABC, abstractmethod
from typing import Literal, NotRequired, TypedDict


class ResourcesDict(TypedDict, total=True):
    Pixmap: str
    Accel: NotRequired[str]
    MenuText: str
    ToolTip: str


class BaseCommand(ABC):
    @abstractmethod
    def GetResources(self) -> ResourcesDict: ...

    @abstractmethod
    def Activated(self):
        """Runs when it gets activated"""
        ...

    @abstractmethod
    def IsActive(self) -> bool:
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        ...
