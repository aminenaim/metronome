from typing import Tuple


class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
    
    def __add__(self,p: 'Point') -> 'Point':
        return Point(self.x + p.x, self.y + p.y)
    
    def __sub__(self,p: 'Point') -> 'Point':
        return Point(self.x - p.x, self.y - p.y)
    
    def tuple(self) -> Tuple[int]:
        return self.x, self.y