import copy
from typing import Any, Tuple, Union

import cv2
import numpy as np

from geometry import Area, AreaList, Point, Range
from utils import Color


class Image:
    """Class used to manipulate image (with OpenCv library)
    """
    def __init__(self, path: str = None, margin: Area = None, img: 'Image' = None) -> None:
        """Init an image from a path or a another image
        
        You need to add at least one source (path or img)

        Args:
            path (str, optional): image path. Defaults to None.
            margin (Area, optional): image area. Defaults to None.
            img (Image, optional): an other image when no path is defined. Defaults to None.
        """
        assert path is not None or img is not None, "You need to add at least one source (path or img)"
        self.path = path
        self.color = cv2.imread(filename=path, flags=cv2.IMREAD_COLOR) if img is None else img
        h, w, _ = self.color.shape
        if margin is not None:
            self.color = self.color[margin.y1():margin.y2(), margin.x1():margin.x2()]
        self.gray = cv2.cvtColor(src=self.color, code=cv2.COLOR_BGR2GRAY)
        h, w, _ = self.color.shape
        self.area = Area(p1=Point(0,0), p2=Point(w,h))
        
    def find_contours(self, dilate: bool = False, all: bool = True, width: Range = None) -> AreaList:
        """Find contours (in rectangle shape) of an image

        Args:
            dilate (bool, optional): delate the image, used when there is image noise. Defaults to False.
            all (bool, optional): search for all contours or only the firsts hierarchically. Defaults to True.
            width (Range, optional): search contours between the given range. Defaults to None.

        Returns:
            AreaList: List of found area  
        """
        _, modified_image = cv2.threshold(src=self.gray, thresh=130, maxval=255, type=cv2.THRESH_BINARY_INV)
        mode = cv2.RETR_TREE if all else cv2.RETR_EXTERNAL
        if dilate:
            kernel = np.ones(shape=(4,4), dtype=np.uint8)
            modified_image = cv2.dilate(src=modified_image, kernel=kernel, iterations=1)
        contours, _ = cv2.findContours(image=modified_image, mode=mode, method=cv2.CHAIN_APPROX_SIMPLE)
        coordinates = AreaList()
        for contour in contours:
            x,y,w,h = cv2.boundingRect(array=contour)
            area = Area(x=x,y=y,w=w,h=h)
            if width is None or width.between(value=area.w()):
                coordinates.append(area)
        return coordinates
    
    def percent_color(self, color: Color, gray: bool) -> int:
        """Search a color percentage within an image area

        Args:
            color (Color): the color to search
            gray (bool): search on grayscale

        Returns:
            int: the percentage of found color 
        """
        total = (self.area.x2() - self.area.x1()) * (self.area.y2() - self.area.y1())
        count = 0
        img = self.gray if gray else self.color
        for y in range(self.area.y1(), self.area.y2()):
            for x in range(self.area.x1(), self.area.x2()):
                if self.__in_range(gray, img[y][x], color):
                    count+=1
        return (count*100)/total
    
    def one_dimension(self, rotate: bool = False) -> list:
        """Transform the image to one dimention list with average color

        Args:
            rotate (bool, optional): Rotate image to the right (when you need to swap colomn and lines). Defaults to False.

        Returns:
            list: one dimention image 
        """
        res = []
        if rotate:
            rotated = cv2.rotate(src=self.gray, rotateCode=cv2.ROTATE_90_CLOCKWISE)
        for y in rotated:
            res.append(int(sum(y)/len(y)))
        return res
    
    @classmethod
    def __in_range(cls, gray: bool, value: Union[int,Tuple[int,int,int]], ref: Color) -> bool:
        """Check if a color is in range of an given range

        Args:
            gray (bool): use gray scale
            value (Union[int,Tuple[int,int,int]]): color to check
            ref (Color): reference of the color

        Returns:
            bool: True if the color is in range, False otherwise
        """
        if gray: # Gray 1 value
            return ref.value[0] <= value and value <= ref.value[1]
        else: # BGR 3 values
            return (ref.value[0][0] <= value[0] and value[0] <= ref.value[1][0] and
                    ref.value[0][1] <= value[1] and value[1] <= ref.value[1][1] and
                    ref.value[0][2] <= value[2] and value[2] <= ref.value[1][2])
    
    def sub(self, margin: Area = Area(Point(0,0),Point(0,0)), copy_img: bool = True) -> 'Image':
        """Create a sub image from this one

        Args:
            margin (Area, optional): the area where image is taken from. Defaults to Area(Point(0,0),Point(0,0)).
            copy_img (bool, optional): Whether created image should be a copy of the original . Defaults to True.

        Returns:
            Image: sub image created
        """
        if copy_img:
            return Image(margin=margin, img=copy.deepcopy(self.color))
        else:
            return Image(margin=margin, img=self.color)

    def show(self, title: str = "", color: bool = True) -> None:
        """Show the image in another windows

        Args:
            title (str, optional): title of the windows. Defaults to "".
            color (bool, optional): Whether it should show the colored or the gray image. Defaults to True.
        """
        cv2.imshow(winname=title ,mat=self.color if color else self.gray)
        cv2.waitKey(delay=0)
        cv2.destroyAllWindows()
    
    def frame(self, area: Area, color: Union[int,Tuple[int, int, int]]=(0,0,255), size:int=2) -> None:
        """Frame an area of the image with the given color

        Args:
            area (Area): area to frame
            color (Union[int,Tuple[int, int, int]], optional): color of the stroke. Defaults to (0,0,255).
            size (int, optional): size of the stroke (-1 is filled area). Defaults to 2.
        """
        if isinstance(color, int):
            cv2.rectangle(img=self.gray, pt1=area.p1.tuple(), pt2=area.p2.tuple(), color=color, thickness=size)
        else:
            cv2.rectangle(img=self.color, pt1=area.p1.tuple(), pt2=area.p2.tuple(), color=color, thickness=size)
                
    def line(self, p1: Point, p2: Point, color:Union[int,Tuple[int, int, int]]=(0,0,255), size:int=2):
        """Draw a line on the image with a given color

        Args:
            p1 (Point): first point of the line
            p2 (Point): second point of the line
            color (Union[int,Tuple[int, int, int]], optional): color of the stroke. Defaults to (0,0,255).
            size (int, optional): size of the stroke. Defaults to 2.
        """
        if isinstance(color, int):
            cv2.line(img=self.gray, pt1=p1.tuple(), pt2=p2.tuple(), color=color, thickness=size)
        else:
            cv2.line(img=self.color, pt1=p1.tuple(), pt2=p2.tuple(), color=color, thickness=size)
    
    def save(self, path: str, name: str, color: bool = True) -> None:
        """Save the image on a given file

        Args:
            path (str): folder where the image should be saveed
            name (str): name of the file (without extension)
            color (bool, optional): whether it should be the colored one or the gray. Defaults to True.
        """
        cv2.imwrite(f"{path}/{name}.jpg", self.color if color else self.gray)
