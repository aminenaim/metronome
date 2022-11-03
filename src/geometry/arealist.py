import copy
from re import Pattern
from typing import List

from .area import Area
from .point import Point


class AreaList(List[Area]):
    def __init__(self) -> None:
        super().__init__()
    
    def last(self) -> Area:
        return self[len(self) - 1]

    def first(self) -> Area:
        return self[0]
    
    def contained(self, area: Area, remove: bool = False) -> 'AreaList':
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

    def match(self, pattern:  Pattern, remove: bool = False) -> 'AreaList':
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
        for w in self:
            w.change_origin(point)