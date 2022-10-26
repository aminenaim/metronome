from copy import deepcopy
from datetime import timedelta
from enum import Enum
import re
from typing import List
from lib.geometry import Area, Axe, AxeType, Point, Range, AreaList
from lib.image import Color, Image
from lib.time import Time


class Week:
    __RANGE_CLASS = Range(100,1000,AxeType.ABSCISSA)
    
    REGEX_WEEK_ID = re.compile(r'^[Ss]?((\d)|([0-4]\d)|(5[0-3]))$')
    def __init__(self, image: Image , words: AreaList, time: Time) -> None:
        self.image = image
        self.words = words
        self.time = time
        frames = self.image.find_contours(True, True, self.__RANGE_CLASS)
        words_days = self.words.match(Time.REGEX_DAY, remove=True)
        words_hours = self.words.match(pattern=Time.REGEX_HOUR, remove=True)
        words_id = self.words.match(pattern=self.REGEX_WEEK_ID, remove=True)
        self.hours = Hours(words_hours, words_id, Range(image.area.x1(),image.area.x2(), AxeType.ABSCISSA), self.image)
        self.days = self.__get_day(frames, words_days)
        self.id = self.__get_id(words_id)
        self.classes = self.__get_classes(frames)
        
    def __get_day(self, frames: AreaList, words_days: AreaList) -> AreaList:
        days = deepcopy(words_days)
        for day in days:
            for frame in frames:
                if frame.in_bound(day.center()):
                    day.resize(frame)
                    day.content = timedelta(days=Time.DAYS[day.content])
        return days
    
    def __get_id(self, word_id: AreaList) -> int:
        if word_id != 0 and len(word_id) != 0:
            return int(re.sub(r'[Ss]','',word_id[0].content))
        else:
            return 0 # week unknown
    
    def __get_classes(self, frames: AreaList) -> AreaList:
        classes = []
        for frame in frames:
            frame.content = [] # add words to each class frame
            for word in self.words: 
                if frame.in_bound(word.center()):
                    frame.content.append(word.content)
            if len(frame.content) != 0: # remove frame without content
                classes.append(frame)
            self.__remove_overlapping(classes)
        return classes

    def __remove_overlapping(self, classes: AreaList) -> None:
        overlapping = []
        for c1 in classes: # remove overlapping frames
            for c2 in classes:
                if c1 != c2 and c1.contain(c2):
                    overlapping.append(c2)
        for o in overlapping:
                classes.remove(o)
    
    def gen_courses(self) -> List['Course']:
        courses = []
        for c in self.classes:
            sub_img = self.image.sub(c, False)
            yellow_percent = sub_img.percent_color(Color.YELLOW, False)
            courses.append(Course(self.hours.time_axe, c, self.days, self.time, yellow_percent))
        return courses
        
    def frame_words(self) -> None:
        for a in self.words:
            self.image.frame(a)
    
    def frame_elements(self) -> None:
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

class Hours:
    def __init__(self, words_hours: AreaList, words_id: AreaList, margin : Range, week_image: Image) -> None:
        self.image = self.__get_image(words_hours, words_id, margin, week_image)
        lines = self.__detect_time_scale()
        hour_axe = self.__get_hours_axe(words_hours, lines, margin)
        self.time_axe = self.__get_time_axe(lines, hour_axe)
    
    def __get_image(self, words_hours: AreaList, words_id: AreaList, margin : Range, week_image: Image) -> Image:
        image = None
        if len(words_hours):
            hour_area = Area(Point(margin.a, words_hours.first().y1()), Point(margin.b, words_hours.first().y2()))
            image = week_image.sub(hour_area)
            upper_words_hours = deepcopy(words_hours)
            upper_words_id = deepcopy(words_id)
            upper_words_hours.change_origin(hour_area.p1)
            upper_words_id.change_origin(hour_area.p1)
            for wd in upper_words_hours:
                image.frame(wd, 255, -1)
            for wi in upper_words_id:
                image.frame(wi, 255, -1)
        return image
            
    def __detect_time_scale(self) -> List[int]:
        lines = []
        if self.image is not None:
            one_d = self.image.one_dimension(True)
            i = 0
            while i < len(one_d):
                if one_d[i] < 150:
                    lines.append(i)
                    while i < len(one_d) and one_d[i] < 200 :
                        i+=1
                else:
                    i+=1
        return lines
    
    def __get_hours_axe(self, words_hours: AreaList, lines: List[int], margin: Range) -> Axe:
        hour_axe = Axe()
        words_hours.sort(key=lambda x: x.p1.x)
        if len(words_hours):
            hour = int(words_hours.first().content.replace('h','')) - 1
            hour_axe.add(margin.a, hour)
        for wh in words_hours:
            hour = int(wh.content.replace('h',''))
            middle = wh.middle(AxeType.ABSCISSA)
            i = -1
            while((i + 1) < len(lines) and lines[i + 1] < middle):
                i+=1
            hour_axe.add(lines[i], hour)
        if len(words_hours) and (len(lines) - 1 - i > 2):
            hour = int(words_hours.last().content.replace('h','')) + 1
            hour_axe.add(lines[len(lines) - 1], hour)
        return hour_axe
    
    def __get_time_axe(self, lines: List[int], hour_axe: Axe):
        list_key = list(hour_axe)
        time_axe = Axe()
        matrice_hour = self.__sublist_hour(lines, list_key)
        for lst in matrice_hour:
            hour = hour_axe[lst[0]]
            if len(lst) == 3:
                lst.insert(1, int((lst[0] + lst[1])/2))
            elif len(lst) != 4 and len(lst) != 1:
                nexts = [l for l in lines if l > lst[len(lst) - 1]]
                if len(nexts):
                    step = (nexts[0] - lst[0])/4
                    lst = [int(lst[0] + i*step) for i in range(0,4)]
            for id, element in enumerate(lst):
                time_axe.add(element,timedelta(hours=hour, minutes=15*id))
        return time_axe
    
    def __sublist_hour(self, lines: List[int], list_key: List[int]):
        matrice_hour: List[List[int]] = []
        id_key,id_line = 0,0
        while(id_key + 1 < len(list_key)):
            matrice_hour.append([lines[id_line]])
            id_line+=1
            while(id_line < len(lines) and lines[id_line] < list_key[id_key + 1]):
                matrice_hour[id_key].append(lines[id_line])
                id_line+=1
            id_key+=1
        if id_line < len(lines):
            matrice_hour.append([])
        while(id_line < len(lines)):
            matrice_hour[id_key].append(lines[id_line])
            id_line+=1

        return matrice_hour        
            

class Group(Enum):
    ALL = 0
    GROUP1 = 1
    GROUP2 = 2

class Course:
    __REGEX_LOCATION = re.compile(r'[a-z-A-Z]\d-.*|Amphi .*|.*Zoom|.*ZOOM')
    __REGEX_TEACHER = re.compile(r'( \([A-Z]{2,3}\)$)|( \([A-Z]{2,3}\/[A-Z]{2,3}\)$)')
    __PERCENT_YELLOW_EXAM = 10
    
    def __init__(self, hour_axe: Axe, course_area: Area, days: AreaList, week_time: Time, yellow_percent: int) -> None:
        day = self.__get_day(days, course_area)

        self.begin = week_time.get_time(hour=hour_axe.closest(course_area.x1()), day=day.content, timezone="Europe/Paris")
        self.end = week_time.get_time(hour=hour_axe.closest(course_area.x2()), day=day.content, timezone="Europe/Paris")
        self.group = self.__get_group(day, course_area)
        self.name, self.teacher, self.location = self.__get_content(course_area, self.group)
        self.exam = yellow_percent >= self.__PERCENT_YELLOW_EXAM
        
    def __get_day(self, days: AreaList, course_area: Area) -> Area:
        middle = course_area.middle(AxeType.ORDINATE)
        for d in days:
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
            if l in course_area.content:
                course_area.content.remove(l)
            else:
                for ca in course_area.content:
                    ca.replace(l,'')
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
        return f'{self.name} : B[{self.begin}] - E[{self.end}] - L[{self.location}] - T[{self.teacher}]] - G[{self.group}] E[{self.exam}]'