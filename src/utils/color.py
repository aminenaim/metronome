from enum import Enum


class Color(Enum):
    """Color class listing used colors
    """
    YELLOW = [[0, 220, 220], [50, 255, 255]] # BGR
    """Yellow color for exams in BGR
    """
    BLACK = [100,255] # BGR
    """Black color for contours
    """
