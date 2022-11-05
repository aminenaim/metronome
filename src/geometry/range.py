import importlib

from .axetype import AxeType


class Range:
    """Class representing a range on an axe
    """
    
    def __init__(self, a: int, b: int, axe: AxeType) -> None:
        """Constructor of range

        Args:
            a (int): first coordinate
            b (int): second coordinate
            axe (AxeType): axe of theses coordinates
        """
        assert axe == AxeType.ABSCISSA or axe == AxeType.ORDINATE, f"You must pass the axe Axe.ABSCISSA ({AxeType.ABSCISSA}) or Axe.ORDONATE ({AxeType.ORDINATE})"
        self.a = a
        self.b = b
        self.axe = axe
    
    def middle(self) -> int:
        """Get the middle of this range

        Returns:
            int: middle of the range
        """
        return (self.b + self.a)/2
    
    def size(self) -> int:
        """Get the size of this range

        Returns:
            int: size of the range
        """
        return abs(self.b - self.a)
    
    def is_between(self, area: 'area.Area') -> bool:
        """Check if an area is between this range

        Args:
            area (area.Area): area to check

        Returns:
            bool: True if this area is between this range, false otherwise
        """
        if self.axe == AxeType.ABSCISSA:
            return self.a < area.x1() and area.x2() < self.b
        else:
            return self.a < area.y1() and area.y2() < self.b
    
    def is_contained(self, value: int) -> bool:
        """Check if a coordinate is contained (not strictly) by this range

        Args:
            value (int): the coordinate to check

        Returns:
            bool: True if it's contained by this range, False otherwise
        """
        return self.a <= value and value <= self.b

# prevent circular import
from . import area