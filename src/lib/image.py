import copy
from enum import Enum
import cv2
import numpy as np
from lib.geometry import Area, AxeType, Point, Range
from lib.words import Words

class Color(Enum):
    YELLOW = [[0, 220, 220], [50, 255, 255]] # BGR
    BLACK = [100,255] # BGR

class Image:
    def __init__(self, path: str = None, margin: Area = None, img = None) -> None:
        assert path is not None or img is not None, "You need to add at least one source (path or img)"
        self.path = path
        self.color = cv2.imread(path, cv2.IMREAD_COLOR) if img is None else img
        h, w, _ = self.color.shape
        if margin is not None:
            self.color = self.color[margin.y1():margin.y2(), margin.x1():margin.x2()]
        self.gray = cv2.cvtColor(self.color, cv2.COLOR_BGR2GRAY)
        h, w, _ = self.color.shape
        self.area = Area(Point(0,0), Point(w,h))
        
    def find_contours(self, dilate: bool = False, all: bool = True, width: Range = None, avg_height: int = None) -> list:
        _, modified_image = cv2.threshold(self.gray, 130, 255, cv2.THRESH_BINARY_INV)
        mode = cv2.RETR_TREE if all else cv2.RETR_EXTERNAL
        if dilate:
            kernel = np.ones((4,4), np.uint8)
            modified_image = cv2.dilate(modified_image, kernel, iterations = 1)
        contours, _ = cv2.findContours(modified_image, mode, cv2.CHAIN_APPROX_SIMPLE)
        coordinates = []
        for contour in contours:
            x,y,w,h = cv2.boundingRect(contour)
            area = Area(x=x,y=y,w=w,h=h)

            if width is None or width.between(area.w()):
                if avg_height is None:
                    coordinates.append(area)
                else:
                    nb_slices = round(area.h()/avg_height)
                    coordinates = coordinates + area.slice(nb_slices, AxeType.ORDINATE)
        return coordinates
    
    def percent_color(self, color: Color, gray: bool):
        total = (self.area.x2() - self.area.x1()) * (self.area.y2() - self.area.y1())
        count = 0
        img = self.gray if gray else self.color
        for y in range(self.area.y1(), self.area.y2()):
            for x in range(self.area.x1(), self.area.x2()):
                if  (self.__in_range(gray, img[y][x], color)):
                    count+=1
        return (count*100)/total
    
    @classmethod
    def __in_range(cls, gray: bool, value, ref):
        if gray: # Gray 1 value
            return ref.value[0] <= value and value <= ref.value[1]
        else: # BGR 3 values
            return (ref.value[0][0] <= value[0] and value[0] <= ref.value[1][0] and
                    ref.value[0][1] <= value[1] and value[1] <= ref.value[1][1] and
                    ref.value[0][2] <= value[2] and value[2] <= ref.value[1][2])
    
    def sub(self, margin: Area = Area(Point(0,0),Point(0,0)), copy_img: bool = True) -> 'Image':
        if copy_img:
            return Image(margin=Area(margin.p1, margin.p2), img=copy.deepcopy(self.color))
        else:
            return Image(margin=Area(margin.p1, margin.p2), img=self.color)

    def show(self, title: str = "", color: bool = True) -> None:
        cv2.imshow(title,self.color if color else self.gray)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    def remove_word(self, words: Words):
        for a in words.list:
            cv2.rectangle(self.color, (a.p1.x,a.p1.y), (a.p2.x,a.p2.y), (255,255,255), -1)
    
    def frame(self, area: Area, color=(0,0,255), size=2) -> None:
        if isinstance(color, int):
            cv2.rectangle(self.gray, area.p1.tuple(), area.p2.tuple(), color, size)
        else:
            cv2.rectangle(self.color, area.p1.tuple(), area.p2.tuple(), color, size)
            
        cv2.rectangle(self.color, area.p1.tuple(), area.p2.tuple(), color, size)
    
    def save(self, path: str, name: str, color: bool = True) -> None:
        cv2.imwrite(f"{path}/{name}.jpg", self.color if color else self.gray)
