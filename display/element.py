from gtt import GttDisplay

from abc import ABC, abstractmethod


class Element(ABC):
    """An abstract base class for a UI element"""

    def __init__(self, display: GttDisplay):
        self.display: GttDisplay = display

    @abstractmethod
    def update(self, value):
        pass
