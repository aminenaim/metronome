from array import ArrayType
from re import Pattern
from lib.geometry import Area
import copy


class Words:
    def __init__(self, words: 'Words' = None, area: Area = None, pattern: Pattern = None, remove: bool = False) -> None:
        self.list = []
        assert (words is None and (area is None and pattern is None)) or (words is not None and (area is not None or pattern is not None)), "word and area/pattern must be ether not set, or set together"
        if area is not None:
            self.list = words.contained(area, remove)
        if pattern is not None:
            self.list = words.match(pattern, remove)
            
    def add(self, area: Area, index=None) -> None:
        if index is None:
            self.list.append(area)
        else:
            self.list.insert(0,area)
    
    def remove(self, word: Area):
        self.list.remove(word)
    
    def last(self) -> Area:
        return self.list[len(self.list) - 1]

    def first(self) -> Area:
        return self.list[0]
    
    def contained(self, area: Area, remove: bool = False) -> ArrayType:
        res = [copy.deepcopy(a) for a in self.list if area.contain(a)]
        if remove:
            for a in res:
                self.list.remove(a)
        return res

    def match(self, pattern:  Pattern, remove: bool = False) -> ArrayType:
        res = [a for a in self.list if pattern.match(a.content)]
        if remove:
            for a in res:
                self.list.remove(a)
        return res
    
    def change_origin(self, area: Area) -> None:
        for w in self.list:
            w.change_origin(area)
    