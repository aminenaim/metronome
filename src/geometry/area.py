import sys
from typing import Any, List

from .axetype import AxeType
from .point import Point
from .range import Range


class Area:
    """Class defining a surface with 2 points and optionaly a content in it
    """
    def __init__(self, p1: Point = None, p2: Point = None, x : int = None, y : int = None, w: int = None, h: int = None, content: Any = None) -> None:
        """Constructor of an Area with 2 points or x,y,w,h values

        Args:
            p1 (Point, optional): first point (top left corner). Defaults to None.
            p2 (Point, optional): second point (bottom right corner). Defaults to None.
            x (int, optional): x coordinate of top left corner. Defaults to None.
            y (int, optional): y coordinate of top left corner. Defaults to None.
            w (int, optional): area width. Defaults to None.
            h (int, optional): area height. Defaults to None.
            content (Any, optional): area content. Defaults to None.

        Raises:
            ValueError: _description_
        """
        if p1 is not None and p2 is not None:
            self.p1 = p1
            self.p2 = p2
            self.content = content
        elif x is not None and y is not None and w is not None and h is not None:
            self.p1 = Point(x=x, y=y)
            self.p2 = Point(x=(x+w), y=(y+h))
            self.content = content
        else:
            raise ValueError(f"You must pass 2 points or x,y,w,h values")
    
    def x1(self) -> int:
        """Get the top left x coordinate of the area

        Returns:
            int: top left x coordinate
        """
        return self.p1.x
    
    def x2(self) -> int:
        """Get the bottom right x coordinate of the area

        Returns:
            int: bottom right x coordinate
        """
        return self.p2.x
    
    def y1(self) -> int:
        """Get the top left y coordinate of the area

        Returns:
            int: top left y coordinate
        """
        return self.p1.y
    
    def y2(self) -> int:
        """Get the bottom right y coordinate of the area

        Returns:
            int: bottom right y coordinate
        """
        return self.p2.y
    
    def w(self) -> int:
        """Get the area width

        Returns:
            int: area width
        """
        return abs(self.p2.x - self.p1.x)
    
    def h(self) -> int:
        """Get the area height

        Returns:
            int: area height
        """
        return abs(self.p2.y - self.p1.y)
    
    def contain(self, area: 'Area') -> bool:
        """Check if a area is contained by this area

        Args:
            area (Area): area to check between this one

        Returns:
            bool: True if the given area is inside by this one
        """
        return  (self.x1() <= area.x1()) and \
                (self.x2() >= area.x2()) and \
                (self.y1() <= area.y1()) and \
                (self.y2() >= area.y2())
    
    def in_bound(self, point: Point) -> bool:
        """Check if a point is inside this area

        Args:
            point (Point): point to check with this area

        Returns:
            bool: True if the given point is inside this area
        """
        return (self.x1() <= point.x) and (point.x <= self.x2()) and \
                (self.y1() <= point.y) and (point.y <= self.y2())
    
    def slice(self, nb_slices: int,  axe: AxeType) -> 'AreaList':
        """Cut this area in equal slices on a given axe

        Args:
            nb_slices (int): number of slices
            axe (AxeType): axe (abscissa or ordinate) where the cut should be

        Returns:
            AreaList: list of area generated
        """
        slices = AreaList()
        if(axe == AxeType.ABSCISSA):
            for i in range (0,nb_slices):
                slices.append(Area(x=self.x1()  + i * self.w()//nb_slices, y=self.y1(), w=self.w()//nb_slices, h=self.h()))
        else:
            for i in range (0,nb_slices):
                slices.append(Area(x=self.x1(), y=self.y1() + i * self.h()//nb_slices, w=self.w(), h=self.h()//nb_slices))
        return slices
    
    def change_origin(self, point: Point) -> None:
        """Change the origin point of abscissa or ordinate axe

        Args:
            point (Point): new origin point
        """
        self.p1 = self.p1 - point
        self.p2 = self.p2 - point
    
    def to_range(self, axe: AxeType) -> Range:
        """Get the range (in one dimension) of this area

        Args:
            axe (AxeType): one dimension axe (abscissa or ordinate)

        Returns:
            Range: generated range
        """
        if axe == AxeType.ABSCISSA:
            return Range(self.x1(), self.x2(), axe)
        else:
            return Range(self.y1(), self.y2(), axe)
    
    def center(self) -> Point:
        """Get the center point of the Area

        Returns:
            Point: area center point
        """
        return Point((self.x2() + self.x1())/2, (self.y2() + self.y1())/2)
    
    def resize(self, area: 'Area') -> None:
        """Resize this area with the given area

        Args:
            area (Area): the new area
        """
        self.p1 = area.p1
        self.p2 = area.p2

# prevent circular import
from .arealist import AreaList