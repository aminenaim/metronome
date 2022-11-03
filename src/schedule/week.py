import re
from datetime import timedelta
from typing import List, Tuple

from files import Image
from geometry import Area, AreaList, AxeType, Point, Range
from utils import Color

from .course import Course
from .hours import Hours
from .time import Time


class Week:
    __RANGE_CLASS = Range(80,1000,AxeType.ABSCISSA)
    REGEX_WEEK_ID = re.compile(r'^[Ss]?((\d)|([0-4]\d)|(5[0-3]))$')
    def __init__(self, image: Image , words: AreaList, times: List[Time], weeks: List['Week']) -> None:
        self.image = image
        self.words = words
        self.frames = self.image.find_contours(True, True, self.__RANGE_CLASS)
        words_days = self.words.match(Time.REGEX_DAY, remove=True)
        if not len(words_days) or not len(times):
            return
        words_id = self.words.match(pattern=self.REGEX_WEEK_ID, remove=True)
        self.__resize_words(self.frames, words_days, words_id)
        if self.__detect_multiple_weeks(words_days):
            y1, y2 = self.__get_separation_point_weeks(words_days, words_id)
            self.__cut_weeks(y1, y2, words_days, words_id, times, weeks)
        else:
            self.time = times[0]
        words_hours = self.words.match(pattern=Time.REGEX_HOUR, remove=True)
        self.hours = Hours(words_hours, words_id, image.area.to_range(AxeType.ABSCISSA), self.image)
        self.days = self.__get_day(words_days)
        self.id = self.__get_id(words_id)
        self.classes = self.__get_classes(self.frames)
    
    def __detect_multiple_weeks(self, words_days: AreaList) -> bool:
        duplicate = False
        for wd1 in words_days:
            for wd2 in words_days:
                if wd1 != wd2 and wd1.content == wd2.content:
                     duplicate = True
        return duplicate
    
    def __get_separation_point_weeks(self, words_days: AreaList, words_id: AreaList) -> Tuple[int,int]:
        words_days.sort(key=lambda wd: wd.p1.y)
        words_id.sort(key=lambda wi: wi.p1.y)
        days_id = 0
        while(days_id < len(words_days) - 1 and Time.DAYS[words_days[days_id].content] < Time.DAYS[words_days[days_id + 1].content]):
            days_id += 1
        if len(words_id) > 1:
            return words_days[days_id].p2.y, words_id[1].p1.y
        return words_days[days_id].p2.y, words_days[days_id + 1].p1.y

    def __cut_weeks(self, y1: int, y2: int, words_days: AreaList, words_id: AreaList,  times: List[Time], weeks: List['Week']):
        area_week1 = Area(self.image.area.p1, Point(self.image.area.p2.x,y1))
        area_week2 = Area(Point(self.image.area.p1.x, y2), self.image.area.p2)
        times.sort(key=lambda t: t.value)
        self.time = times[0]
        times_week2 = times[1:]
        image_week2 = self.image.sub(area_week2, copy_img=True)
        self.image = self.image.sub(area_week1, copy_img=True)
        words_week2 = self.words.contained(area_week2, remove=True)
        words_week2 += words_days.contained(area_week2, remove=True)
        words_week2 += words_id.contained(area_week2, remove=True)
        words_week2.change_origin(area_week2.p1)
        weeks.append(Week(image_week2, words_week2, times_week2, weeks))
    
    def __resize_words(self, frames: AreaList, words_days: AreaList, words_id: AreaList) -> None:
        for day in words_days:
            for frame in frames:
                if frame.in_bound(day.center()) and day.h() < frame.h():
                    day.resize(frame)
        for id in words_id:
            for frame in frames:
                if frame.in_bound(id.center()) and id.w() < frame.w():
                    id.resize(frame)
        
    def __get_day(self, words_days: AreaList) -> AreaList:
        for day in words_days:
            day.content = timedelta(days=Time.DAYS[day.content])
        return words_days
    
    def __get_id(self, word_id: AreaList) -> int:
        if word_id != 0 and len(word_id) != 0:
            return int(re.sub(r'[Ss]','',word_id[0].content))
        else:
            return 0 # week unknown
    
    def __get_classes(self, frames: AreaList) -> AreaList:
        classes = AreaList()
        self.__remove_overlapping(frames)
        frames.sort(key=lambda a: (a.p1.x, a.p1.y))
        for frame in frames:
            frame.content = [] # add words to each class frame
            for word in self.words: 
                if frame.in_bound(word.center()):
                    frame.content.append(word.content)
            if len(frame.content) != 0: # remove frame without content
                classes.append(frame)
        return classes

    def __remove_overlapping(self, classes: AreaList) -> None:
        overlapping = []
        for c1 in classes: # remove overlapping frames
            for c2 in classes:
                if c1 != c2 and c1.contain(c2):
                    overlapping.append(c2)
        for o in overlapping:
                classes.remove(o)
    
    def gen_courses(self) -> List[Course]:
        courses = []
        for c in self.classes:
            sub_img = self.image.sub(c, False)
            yellow_percent = sub_img.percent_color(Color.YELLOW, False)
            course = Course(self.hours.time_axe, c, self.days, self.time, yellow_percent)
            if course.day is not None:
                courses.append(course)
        return courses
        
    def frame_words(self) -> None:
        for a in self.words:
            self.image.frame(a)
    
    def frame_elements(self) -> None:
        for a in self.frames:
            self.image.frame(a,(216,191,216))
        for a in self.classes:
            self.image.frame(a)
        for a in self.days:
            self.image.frame(a, (0,255,0))
        for e in list(self.hours.time_axe):
            p1 = Point(e,0)
            p2 = Point(e,30)
            self.image.line(p1,p2, (255,0,0))
    
    def save(self, path: str) -> None:
        name_week = str(self.time).split(' ')[0]
        self.image.save(path, f'week{name_week}')