
from typing import List

from files import Image
from geometry import AreaList, AxeType, Range
from schedule import Time, Week


class Page:
    __RANGE_WEEK = Range(1900, 2200, AxeType.ABSCISSA)
    
    def __init__(self, image: Image , words: AreaList, id: int) -> None:
        self.image = image
        self.id = id
        self.words = words
        self.times = self.__gen_week_time()
        self.week_coordinate = self.image.find_contours(False, False, self.__RANGE_WEEK)

    def __gen_week_time(self) -> AreaList:
        times = self.words.match(pattern=Time.REGEX_WEEK, remove=True)
        for t in times:
            t.content = Time(t.content)
        return times
            
    def gen_weeks(self) -> List[Week]:
        weeks = []
        for c in self.week_coordinate:
            r: Range = c.to_range(AxeType.ORDINATE)
            times = []
            for t in self.times:
                if r.in_bound(t):
                    times.append(t.content)
            image = self.image.sub(c)
            # make sure there is contour around the week
            image.frame(image.area, color=(0,0,0), size=5)
            image.frame(image.area, color=0, size=5)
            week_word = self.words.contained(c)
            week_word.change_origin(c.p1)
            week = Week(image, week_word, times, weeks)
            if hasattr(week,'days'):
                weeks.append(week)
        return weeks

    def frame_elements(self) -> None:
        for a in self.words:
            self.image.frame(a)
        for a in self.week_coordinate:
            self.image.frame(a, (0,255,0))
    
    def save(self, path: str):
        self.image.save(path, f'page-{self.id}')