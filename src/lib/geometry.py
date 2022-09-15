from array import ArrayType
from enum import Enum

class Axe(Enum):
    ABSCISSA = 0
    ORDINATE = 1

class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
    
    def __add__(self,p: 'Point') -> 'Point':
        return Point(self.x + p.x, self.y + p.y)
    
    def __sub__(self,p: 'Point') -> 'Point':
        return Point(self.x - p.x, self.y - p.y)

class Area:
    def __init__(self, p1: Point, p2: Point, content=None) -> None:
        self.p1 = p1
        self.p2 = p2
        self.content = content
        
    def __init__(self, x : float, y : float, w: float, h: float, content=None) -> None:
        self.p1 = Point(x,y)
        self.p2 = Point(x+w,y+h)
        self.content = content
    
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
        return  (self.x1 <= area.x1 + uncertainty) and \
                (self.x2 >= area.x2 - uncertainty) and \
                (self.y1 <= area.y1 + uncertainty) and \
                (self.y2 >= area.y2 - uncertainty)
    
    def slice(self, nb_slices: int,  axe: Axe) -> ArrayType:
        slices = []
        if(axe == Axe.ABSCISSA):
            for i in range (0,nb_slices):
                slices.append(Area(self.x1  + i * self.w//nb_slices, self.y1, self.w//nb_slices, self.h))
        else:
            for i in range (0,nb_slices):
                slices.append(Area(self.x1, self.y1 + i * self.h//nb_slices, self.w, self.h//nb_slices))
        return slices

    def range(self, axe: Axe) -> 'Range':
        if axe == Axe.ABSCISSA:
            return Range(self.x1, self.x2, axe)
        else:
            return Range(self.y1, self.y2, axe)

class Range:
    def __init__(self, a: float, b: float, axe: Axe) -> None:
        assert axe == Axe.ABSCISSA or axe == Axe.ORDINATE, f"You must pass the axe Axe.ABSCISSA ({Axe.ABSCISSA}) or Axe.ORDONATE ({Axe.ORDINATE})"
        self.a = a
        self.b = b
        self.axe = axe
    
    def middle(self) -> float:
        return (self.b + self.a)/2
    
    def in_range(self, area: Area) -> bool:
        if self.axe == Axe.ABSCISSA:
            return area.x1 < self.middle < area.x2
        else:
            return area.y1 < self.middle < area.y2
    
    def between(self, value: float) -> bool:
        return self.a <= value and value <= self.b