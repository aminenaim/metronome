import importlib

from .axetype import AxeType


class Range:
    def __init__(self, a: int, b: int, axe: AxeType) -> None:
        assert axe == AxeType.ABSCISSA or axe == AxeType.ORDINATE, f"You must pass the axe Axe.ABSCISSA ({AxeType.ABSCISSA}) or Axe.ORDONATE ({AxeType.ORDINATE})"
        self.a = a
        self.b = b
        self.axe = axe
    
    def middle(self) -> int:
        return (self.b + self.a)/2
    
    def size(self) -> int:
        return abs(self.b - self.a)
    
    def in_range(self, area: 'area.Area') -> bool:
        if self.axe == AxeType.ABSCISSA:
            return area.x1() < self.middle() and self.middle() < area.x2()
        else:
            return area.y1() < self.middle() and self.middle() < area.y2()
    
    def in_bound(self, area: 'area.Area') -> bool:
        if self.axe == AxeType.ABSCISSA:
            return self.a < area.x1() and area.x2() < self.b
        else:
            return self.a < area.y1() and area.y2() < self.b
    
    def between(self, value: int) -> bool:
        return self.a <= value and value <= self.b

from . import area