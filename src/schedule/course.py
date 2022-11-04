import re
from typing import Tuple

from geometry import Area, AreaList, Axe, AxeType, Range

from .group import Group
from .time import Time


class Course:
    __REGEX_LOCATION = re.compile(r'[a-z-A-Z]\d-.*|Amphi .*|.*Zoom|.*ZOOM')
    __REGEX_TEACHER = re.compile(r'( \([A-Z]{2,3}\)$)|( \([A-Z]{2,3}\/[A-Z]{2,3}\)$)|(-\s*[A-Z]{2,3}$)')
    __PERCENT_YELLOW_EXAM = 10
    __GRP_NAME = {Group.ALL:'All', Group.GROUP1:'Groupe 1', Group.GROUP2:'Groupe 2'}
    
    def __init__(self, hour_axe: Axe, course_area: Area, days: AreaList, week_time: Time, yellow_percent: int) -> None:
        self.day = self.__get_day(days, course_area)
        if self.day is not None:
            self.begin = week_time.get_time(hour=hour_axe.closest(course_area.x1()), day=self.day.content)
            self.end = week_time.get_time(hour=hour_axe.closest(course_area.x2()), day=self.day.content)
            self.group = self.__get_group(self.day, course_area)
            self.name, self.teacher, self.location = self.__get_content(course_area)
            self.exam = yellow_percent >= self.__PERCENT_YELLOW_EXAM
        
    def __get_day(self, days: AreaList, course_area: Area) -> Area:
        middle = course_area.center().y
        for d in days:
            full_day: Range = d.to_range(AxeType.ORDINATE)
            if full_day.between(middle):
                return d
    
    def __get_group(self, day: Area, course_area: Area) -> Group:
        if abs(day.h() - course_area.h()) < abs(day.h()/2 - course_area.h()): # closest size (entire or half)
            return Group.ALL
        if course_area.center().y <= day.center().y:
            return Group.GROUP1
        else:
            return Group.GROUP2
    
    def __get_content(self, course_area: Area) -> Tuple[str, str, str]:
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
    
    def get_group_name(self):
        return self.__GRP_NAME[self.group]
    
    def __str__(self):
        return f'{self.name} : B[{self.begin}] - E[{self.end}] - L[{self.location}] - T[{self.teacher}]] - G[{self.group}] E[{self.exam}]'