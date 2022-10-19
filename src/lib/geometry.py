from enum import Enum

class AxeType(Enum):
    ABSCISSA = 0
    ORDINATE = 1

class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
    
    def __add__(self,p: 'Point') -> 'Point':
        return Point(self.x + p.x, self.y + p.y)
    
    def __sub__(self,p: 'Point') -> 'Point':
        return Point(self.x - p.x, self.y - p.y)
    
    def tuple(self):
        return self.x, self.y

class Area:
    def __init__(self, p1: Point = None, p2: Point = None, x : int = None, y : int = None, w: int = None, h: int = None, content=None) -> None:
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
    
    def x1(self) -> int:
        return self.p1.x
    
    def x2(self) -> int:
        return self.p2.x
    
    def y1(self) -> int:
        return self.p1.y
    
    def y2(self) -> int:
        return self.p2.y
    
    def w(self) -> int:
        return abs(self.p2.x - self.p1.x)
    
    def h(self) -> int:
        return abs(self.p2.y - self.p1.y)
    
    def contain(self, area: 'Area') -> bool:
        return  (self.x1() <= area.x1()) and \
                (self.x2() >= area.x2()) and \
                (self.y1() <= area.y1()) and \
                (self.y2() >= area.y2())
    
    def in_bound(self, point: Point) -> bool:
        return (self.x1() <= point.x) and (point.x <= self.x2()) and \
                (self.y1() <= point.y) and (point.y <= self.y2())
    
    def slice(self, nb_slices: int,  axe: AxeType) -> list:
        slices = []
        if(axe == AxeType.ABSCISSA):
            for i in range (0,nb_slices):
                slices.append(Area(x=self.x1()  + i * self.w()//nb_slices, y=self.y1(), w=self.w()//nb_slices, h=self.h()))
        else:
            for i in range (0,nb_slices):
                slices.append(Area(x=self.x1(), y=self.y1() + i * self.h()//nb_slices, w=self.w(), h=self.h()//nb_slices))
        return slices
    
    def change_origin(self, point: Point):
        self.p1 = self.p1 - point
        self.p2 = self.p2 - point
    
    def to_range(self, axe: AxeType) -> 'Range':
        if axe == AxeType.ABSCISSA:
            return Range(self.x1(), self.x2(), axe)
        else:
            return Range(self.y1(), self.y2(), axe)

    def middle(self, axe: AxeType) -> int:
        if axe == AxeType.ABSCISSA:
            return (self.x2() + self.x1())/2
        else:
            return (self.y2() + self.y1())/2
    
    def center(self) -> Point:
        return Point((self.x2() + self.x1())/2, (self.y2() + self.y1())/2)
    
    def resize(self, area: 'Area'):
        self.p1 = area.p1
        self.p2 = area.p2

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
    
    def in_range(self, area: Area) -> bool:
        if self.axe == AxeType.ABSCISSA:
            return area.x1() < self.middle() and self.middle() < area.x2()
        else:
            return area.y1() < self.middle() and self.middle() < area.y2()
    
    def in_bound(self, area: Area) -> bool:
        if self.axe == AxeType.ABSCISSA:
            return self.a < area.x1() and area.x2() < self.b
        else:
            return self.a < area.y1() and area.y2() < self.b
    
    def between(self, value: int) -> bool:
        return self.a <= value and value <= self.b

class Axe(dict):
    def __init__(self) -> None:
        super().__init__()
    
    def add(self, x : int, value):
        self[x] = value
    
    def closest(self, x: int):
        key = min(self, key=lambda l:abs(l-x))
        return self[key]
        