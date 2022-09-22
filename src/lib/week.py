from array import ArrayType
from datetime import timedelta
from enum import Enum
import re
from lib.geometry import Area, Axe, AxeType, Point, Range
from lib.image import Image
from lib.time import Time
from lib.words import Words


class Week:
    REGEX_WEEK_ID = re.compile(r'^((\d)|([0-4]\d)|(5[0-3]))$')
    def __init__(self, image: Image , words: Words, time: Time) -> None:
        self.image = image
        self.words = words
        self.time = time
        frames = self.image.find_contours(True, True, Range(100,1000,AxeType.ABSCISSA))
        
        self.days = self.__get_day(frames)
        self.hours = self.__get_hour(Range(image.area.x1(),image.area.x2(), AxeType.ABSCISSA))
        self.id = self.__get_id()
        self.classes = self.__get_classes(frames)
        
        self.time_axe = self.__get_time_axe()
        
    def __get_day(self, frames: ArrayType) -> Words:
        days: Words = Words(words=self.words, pattern=Time.REGEX_DAY, remove=True)
        for day in days.list:
            for frame in frames:
                if frame.in_bound(day.center()):
                    day.resize(frame)
                    day.content = timedelta(days=Time.DAYS[day.content])
        return days
        
    def __get_hour(self, margin: Range) -> Words:
        hours = Words(words=self.words, pattern=Time.REGEX_HOUR, remove=True)
        for hour in hours.list:
            hour.content = int(hour.content.replace('h','')) # transform '10h' in '10'
            hour.p1.x = hour.p1.x - 7 # hour space between word (10h) and de border of the hour cell
        hours.list.sort(key=lambda x: x.p1.x)
        for i in range(0,len(hours.list) - 1): # match right hour border with the next hour
            hours.list[i].p2.x = hours.list[i + 1].p1.x - 1
        hours.last().p2.x = margin.b - 3 # match last hour with the border
        hours.add(Area(p1=Point(margin.a + 3, hours.first().y1()), p2=Point(hours.first().x1() - 1, hours.first().y2()), content=hours.first().content - 1),0) # add first hour (7h)
        return hours
    
    def __get_time_axe(self) -> Axe:
        time_axe = Axe()
        for hour in self.hours.list:
            for i in range(0,4): # cut hours in quarters
                time_axe.add(hour.x1() + (hour.w()/4)*i,timedelta(hours=hour.content, minutes=i*15))
        time_axe.add(self.hours.last().x2(),timedelta(hours=self.hours.last().content + 1, minutes=i*15))
        return time_axe
    
    def __get_id(self) -> int:
        week_id = Words(words=self.words, pattern=self.REGEX_WEEK_ID, remove=True)
        if week_id != 0:
            return int(week_id.list[0].content)
        else:
            return 0 # week unknown
    
    def __get_classes(self, frames: ArrayType) -> ArrayType:
        classes = []
        for frame in frames:
            frame.content = [] # add words to each class frame
            for word in self.words.list: 
                if frame.in_bound(word.center()):
                    frame.content.append(word.content)
            if len(frame.content) != 0: # remove frame without content
                classes.append(frame)
        overlapping = []
        for c1 in classes: # remove overlapping frames
            for c2 in classes:
                if c1 != c2 and c1.contain(c2):
                    overlapping.append(c2)
        for o in overlapping:
            classes.remove(o)
        return classes
    
    def gen_courses(self) -> ArrayType:
        courses = []
        for c in self.classes:
            courses.append(Course(self.time_axe, c, self.days, self.time))
        return courses
        
    def frame_words(self) -> None:
        for a in self.words.list:
            self.image.frame(a)
    
    def frame_elements(self) -> None:
        for a in self.classes:
            self.image.frame(a)
        for a in self.days.list:
            self.image.frame(a, (0,255,0))
        for a in self.hours.list:
            self.image.frame(a, (255,0,0))
    
    def save(self, path: str) -> None:
        name_week = str(self.time).split(' ')[0]
        self.image.save(path, f'week{name_week}')

class Group(Enum):
    ALL = 0
    GROUP1 = 1
    GROUP2 = 2

class Course:
    __REGEX_LOCATION = re.compile(r'[a-z-A-Z]\d-.*|Amphi .*|.*Zoom|.*ZOOM')
    __REGEX_TEACHER = re.compile(r'( \([A-Z]{2,3}\)$)|( \([A-Z]{2,3}\/[A-Z]{2,3}\)$)')
    
    def __init__(self, hour_axe: Axe, course_area: Area, days: Words, week_time: Time) -> None:
        day = self.__get_day(days, course_area)

        self.begin = week_time.get_time(hour=hour_axe.closest(course_area.x1()), day=day.content, timezone="Europe/Paris")
        self.end = week_time.get_time(hour=hour_axe.closest(course_area.x2()), day=day.content, timezone="Europe/Paris")
        self.group = self.__get_group(day, course_area)
        self.name, self.teacher, self.location = self.__get_content(course_area, self.group)
        
    def __get_day(self, days: Words, course_area: Area) -> Area:
        middle = course_area.middle(AxeType.ORDINATE)
        for d in days.list:
            full_day: Range = d.to_range(AxeType.ORDINATE)
            if full_day.between(middle):
                return d
    
    def __get_group(self, day: Area, course_area: Area) -> Group:
        if abs(day.h() - course_area.h()) < abs(day.h()/2 - course_area.h()): # closest size (entire or half)
            return Group.ALL
        if course_area.middle(AxeType.ORDINATE) <= day.middle(AxeType.ORDINATE):
            return Group.GROUP1
        else:
            return Group.GROUP2
    
    def __get_content(self, course_area: Area, group: Group):
        search_location = [self.__REGEX_LOCATION.search(e).group() for e in course_area.content if self.__REGEX_LOCATION.search(e)]
        for l in search_location:
            course_area.content.remove(l)
        location = "".join(search_location)
        if len(course_area.content) == 0:
            return 'Unknown','',location
        if group == Group.ALL:
            name = course_area.content[0]
            teacher = course_area.content[1] if len(course_area.content) > 1 else ''
        else:
            search_teacher = self.__REGEX_TEACHER.search(course_area.content[0])
            result = search_teacher.group(0) if search_teacher else ""
            name = course_area.content[0].replace(result,'')
            teacher = re.sub(r'[ \)\(]','',result)
        return name, teacher, location
    
    def __str__(self):
        return f'{self.name} : B[{self.begin}] - E[{self.end}] - L[{self.location}] - T[{self.teacher}]] - G[{self.group}]'