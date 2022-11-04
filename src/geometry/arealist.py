import copy
from re import Pattern
from typing import List

from .area import Area
from .point import Point


class AreaList(List[Area]):
    """Class inherited from list and storing area with utils
    """
    
    def __init__(self) -> None:
        """Constructor of an AreaList from the list constructor
        """
        super().__init__()
    
    def last(self) -> Area:
        """Get last area from this list

        Returns:
            Area: the last area
        """
        return self[len(self) - 1]

    def first(self) -> Area:
        """Get first area from this list

        Returns:
            Area: the first area
        """
        return self[0]
    
    def contained(self, area: Area, remove: bool = False) -> 'AreaList':
        """Get areas contained by the given area

        Args:
            area (Area): area reference
            remove (bool, optional): if set to True, delete from the list any found area. Defaults to False.

        Returns:
            AreaList: list of found area
        """
        sub = AreaList()
        i = 0
        while(i < len(self)):
            if area.contain(self[i]):
                sub.append(copy.deepcopy(self[i]))
                if remove:
                    self.remove(self[i])
                    i-=1
            i+=1
        return sub

    def match(self, pattern: Pattern, remove: bool = False) -> 'AreaList':
        """Get areas with content matching this pattern.
        
        Area content should be string

        Args:
            pattern (Pattern): regex pattern
            remove (bool, optional): if set to True, delete from the list any found area. Defaults to False.

        Returns:
            AreaList: list of found area
        """
        sub = AreaList()
        i = 0
        while(i < len(self)):
            if pattern.match(self[i].content):
                sub.append(copy.deepcopy(self[i]))  
                if remove:
                    self.remove(self[i])
                    i-=1
            i+=1
        return sub
    
    def change_origin(self, point: Point) -> None:
        """Change the origin point of each area

        Args:
            point (Point): origin point
        """
        for w in self:
            w.change_origin(point)