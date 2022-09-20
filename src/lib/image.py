from array import ArrayType
import cv2
import numpy as np
from lib.geometry import Area, AxeType, Point, Range

class Image:
    def __init__(self, path: str, margin: Area = Area(Point(0,0),Point(0,0))) -> None:
        self.path = path
        self.color = cv2.imread(path, cv2.IMREAD_COLOR)
        h, w, _ = self.color.shape
        self.color = self.color[margin.y1():h - margin.y2(), margin.x1():w - margin.x2()]
        self.gray = cv2.cvtColor(self.color, cv2.COLOR_BGR2GRAY)
        self.area = Area(margin.p1, Point(w - margin.x2(),h - margin.y2()))
        
    def find_contours(self, dilate: bool = False, all: bool = True, width: Range = None, avg_height: int = None) -> ArrayType:
        _, modified_image = cv2.threshold(self.gray, 130, 255, cv2.THRESH_BINARY_INV)
        mode = cv2.RETR_TREE if all else cv2.RETR_EXTERNAL
        if dilate:
            kernel = np.ones((4,4), np.uint8)
            modified_image = cv2.dilate(modified_image, kernel, iterations = 1)
        contours, _ = cv2.findContours(modified_image, mode, cv2.CHAIN_APPROX_SIMPLE)
        coordinates = []
        for contour in contours:
            area = Area(cv2.boundingRect(contour))

            if width is None or width.between(area.w()):
                if avg_height is None:
                    coordinates.append(area)
                else:
                    nb_slices = round(area.h()/avg_height)
                    coordinates = coordinates + area.slice(nb_slices, AxeType.ORDINATE)
        return coordinates
    
    def sub(self, margin: Area = Area(Point(0,0),Point(0,0))) -> 'Image':
        return Image(self, self.path, Area(margin.p1 + self.area.p1, self.area.p2 - margin.p2))
    
    def show(self, title: str = "", color: bool = True) -> None:
        cv2.imshow(title,self.color if color else self.gray)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    def save(self, path: str, name: str, color: bool = True) -> None:
        cv2.imwrite(f"{path}/{name}.jpg", self.color if color else self.gray)
