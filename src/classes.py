"""
utils
"""

class Cordinates:
   x1: float
   y1: float
   x2: float
   y2: float

   # Constructor of Cordinates class
   def __init__(self, x, y, w, h) -> None:
      self.x = x
      self.y = y
      self.w = w
      self.h = h
   
   def getWidth(self):
      return self.x2 - self.x1

   def getHeight(self):
      return self.y2 - self.y1
   