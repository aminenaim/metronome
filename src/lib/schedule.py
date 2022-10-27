from copy import deepcopy
from datetime import timedelta
from enum import Enum
import re
from typing import List, Tuple
from lib.geometry import Area, Axe, AxeType, Point, Range, AreaList
from lib.image import Color, Image
from lib.time import Time


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
        classes = []
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
    
    def gen_courses(self) -> List['Course']:
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
        words_hours.sort(key=lambda wh: wh.p1.x)
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
        if len(words_hours):
            self.__add_last_hour(words_hours, lines, hour_axe)
        return hour_axe
    
    def __add_last_hour(self, words_hours: AreaList, lines: List[int], hour_axe: Axe):
        hour = int(words_hours.last().content.replace('h','')) + 1
        list_hour = list(hour_axe)
        lenght_previous_hour = abs(list_hour[len(list_hour) - 2] - list_hour[len(list_hour) - 1])
        lenght_current_hour = abs(list_hour[len(list_hour) - 1] - lines[len(lines) - 1])
        if abs(lenght_previous_hour - lenght_current_hour) > abs(lenght_previous_hour/2 - lenght_current_hour):
            lines.append(lines[len(lines) - 1] + int(lenght_current_hour/2)) # Add last quarter
            lines.append(lines[len(lines) - 1] + int(lenght_current_hour)) # Add last hour
            hour_axe.add(lines[len(lines) - 1] + int(lenght_current_hour), hour) 
        else:
            hour_axe.add(lines[len(lines) - 1], hour)
    
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
    __REGEX_TEACHER = re.compile(r'( \([A-Z]{2,3}\)$)|( \([A-Z]{2,3}\/[A-Z]{2,3}\)$)|(-\s*[A-Z]{2,3}$)')
    __PERCENT_YELLOW_EXAM = 10
    
    def __init__(self, hour_axe: Axe, course_area: Area, days: AreaList, week_time: Time, yellow_percent: int) -> None:
        self.day = self.__get_day(days, course_area)
        if self.day is not None:
            self.begin = week_time.get_time(hour=hour_axe.closest(course_area.x1()), day=self.day.content, timezone="Europe/Paris")
            self.end = week_time.get_time(hour=hour_axe.closest(course_area.x2()), day=self.day.content, timezone="Europe/Paris")
            self.group = self.__get_group(self.day, course_area)
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
    
    def __get_content(self, course_area: Area, group: Group) -> Tuple[str, str, str]:
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
        if len(course_area.content) > 1:
            name = course_area.content[0]
            teacher = course_area.content[1]
        else:
            search_teacher = self.__REGEX_TEACHER.search(course_area.content[0])
            result = search_teacher.group(0) if search_teacher else ""
            name = course_area.content[0].replace(result,'')
            teacher = re.sub(r'[ \)\(]\-','',result)
        return name, teacher, location
    
    def __str__(self):
        return f'{self.name} : B[{self.begin}] - E[{self.end}] - L[{self.location}] - T[{self.teacher}]] - G[{self.group}] E[{self.exam}]'