from array import ArrayType
from enum import Enum
from typing import OrderedDict
from sortedcontainers import SortedDict

class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
    
    def __add__(self,p: 'Point') -> 'Point':
        return Point(self.x + p.x, self.y + p.y)
    
    def __sub__(self,p: 'Point') -> 'Point':
        return Point(self.x - p.x, self.y - p.y)

class Area:
    def __init__(self, p1: Point = None, p2: Point = None, x : float = None, y : float = None, w: float = None, h: float = None, content=None) -> None:
        if p1 is not None and p2 is not None:
            self.p1 = p1
            self.p2 = p2
            self.content = content
        elif x is not None and y is not None and w is not None and h is not None:
            self.p1 = Point(x,y)
            self.p2 = Point(x+w,y+h)
            self.content = content
        else:
            raise ValueError(f"You must pass 2 points or x,y,w,h values")
    
    def x1(self) -> float:
        return self.p1.x
    
    def x2(self) -> float:
        return self.p2.x
    
    def y1(self) -> float:
        return self.p1.y
    
    def y2(self) -> float:
        return self.p2.y
    
    def w(self) -> float:
        return abs(self.p2.x - self.p1.x)
    
    def h(self) -> float:
        return abs(self.p2.y - self.p1.y)
    
    def in_bound(self, area: 'Area', uncertainty: int = 0) -> bool:
        return  (self.x1() <= area.x1() + uncertainty) and \
                (self.x2() >= area.x2() - uncertainty) and \
                (self.y1() <= area.y1() + uncertainty) and \
                (self.y2() >= area.y2() - uncertainty)


class AxeType(Enum):
    ABSCISSA = 0
    ORDINATE = 1

class Range:
    def __init__(self, a: float, b: float, axe: AxeType) -> None:
        assert axe == AxeType.ABSCISSA or axe == AxeType.ORDINATE, f"You must pass the axe Axe.ABSCISSA ({AxeType.ABSCISSA}) or Axe.ORDONATE ({AxeType.ORDINATE})"
        self.a = a
        self.b = b
        self.axe = axe
    
    def middle(self) -> float:
        return (self.b + self.a)/2
    
    def in_range(self, area: Area) -> bool:
        if self.axe == AxeType.ABSCISSA:
            return area.x1() < self.middle() < area.x2()
        else:
            return area.y1() < self.middle() < area.y2()
    
    def between(self, value: float) -> bool:
        return self.a <= value and value <= self.b

class Axe(dict):
    def __init__(self) -> None:
        super().__init__()
    
    def add(self, x : float, value):
        self[x] = value
    
    def closest(self, x):
        key = min(self, key=lambda l:abs(l-x))
        return self[key]
        