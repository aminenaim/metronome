
from typing import List

from files import Image
from geometry import AreaList, AxeType, Range
from schedule import Time, Week


class Page:
    """Class parsing each page of a pdf into single weeks
    """
    __RANGE_WEEK = Range(1900, 2200, AxeType.ABSCISSA)
    """Range (width) of a week
    """
    
    def __init__(self, image: Image , words: AreaList, id: int) -> None:
        """Constructor of Page
        Get the week contours and detected week date
        Args:
            image (Image): image of the page
            words (AreaList): list of words with its area
            id (int): id of the page
        """
        self.image = image
        self.id = id
        self.words = words
        self.dates = self.__gen_week_dates()
        self.week_coordinate = self.image.find_contours(dilate=False, all=False, width=self.__RANGE_WEEK)

    def __gen_week_dates(self) -> AreaList:
        """Get the list of dates present on the page (with its area)

        Returns:
            AreaList: date list (beginning of each week)
        """
        dates = self.words.match(pattern=Time.REGEX_WEEK, remove=True)
        for t in dates:
            t.content = Time(value=t.content)
        return dates
            
    def gen_weeks(self) -> List[Week]:
        """Get the list of weeks (from the detected contours)

        Returns:
            List[Week]: list of weeks on the page
        """
        weeks = []
        for c in self.week_coordinate:
            r: Range = c.to_range(axe=AxeType.ORDINATE)
            times = []
            for t in self.dates:
                if r.in_bound(area=t):
                    times.append(t.content)
            image = self.image.sub(area=c)
            # make sure there is contour around the week
            image.frame(area=image.area, color=(0,0,0), size=5)
            image.frame(area=image.area, color=0, size=5)
            week_word = self.words.contained(area=c)
            week_word.change_origin(point=c.p1)
            week = Week(image=image, words=week_word, times=times, weeks=weeks)
            if hasattr(week,'days'): #if there is no days, this is not a week
                weeks.append(week)
        return weeks

    def frame_elements(self) -> None:
        """Frame words and week boundaries
        """
        for a in self.words:
            self.image.frame(area=a)
        for a in self.week_coordinate:
            self.image.frame(area=a, color=(0,255,0))
    
    def save(self, path: str) -> None:
        """Save page image on a file

        Args:
            path (str): path where the image should be saved
        """
        self.image.save(path=path, name=f'page-{self.id}')
