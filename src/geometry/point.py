from typing import Tuple


class Point:
    """Class representing a point with too coordinates
    """
    
    def __init__(self, x: int, y: int) -> None:
        """Costructor of Point with too coordinates

        Args:
            x (int): the abscissa coordinate
            y (int): the ordinate coordinate
        """
        self.x = x
        self.y = y
    
    def __add__(self,p: 'Point') -> 'Point':
        """Add this point to an other

        Args:
            p (Point): point to add

        Returns:
            Point: point resultant of this addition
        """
        return Point(self.x + p.x, self.y + p.y)
    
    def __sub__(self,p: 'Point') -> 'Point':
        """Subtract this point to an other

        Args:
            p (Point): point to subtract

        Returns:
            Point: point resultant of this subtraction
        """
        return Point(self.x - p.x, self.y - p.y)
    
    def tuple(self) -> Tuple[int]:
        """Get a tupple with the x and y coordinate

        Returns:
            Tuple[int]: the tupple (x,y)
        """
        return self.x, self.y