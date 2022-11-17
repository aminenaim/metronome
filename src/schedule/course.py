import re
from typing import Tuple

from geometry import Area, AreaList, Axe, AxeType, Range

from .group import Group
from .time import Time


class Course:
    """Class with usable course data
    """
    
    __REGEX_LOCATION = re.compile(r'[a-zA-Z]\d-.*|\dA-.*|Amphi .*|.*Zoom|.*ZOOM')
    """Regex used to recognise course location
    """
    __REGEX_TEACHER = re.compile(r'( \([A-Z]{2,3}\)$)|( \([A-Z]{2,3}\/[A-Z]{2,3}\)$)|(-\s*[A-Z]{2,3}$)')
    """Regex used to recognise course teacher
    """
    __PERCENT_YELLOW_EXAM = 10
    """Treshold in percents of yellow pixels from the course area to be considered as an exam
    """
    
    def __init__(self, hour_axe: Axe, course_area: Area, days: AreaList, week_time: Time, yellow_percent: int) -> None:
        """Constructor of course object

        Args:
            hour_axe (Axe): hours axe with time by x position
            course_area (Area): the course area with content
            days (AreaList): list of days area
            week_time (Time): time of the course week
            yellow_percent (int): percent of yellow pixel from the course area
        """
        self.day = self.__get_day(days, course_area)
        if self.day is not None:
            self.begin = week_time.get_time(hour=hour_axe.closest(course_area.x1()), day=self.day.content)
            self.end = week_time.get_time(hour=hour_axe.closest(course_area.x2()), day=self.day.content)
            self.group = self.__get_group(day=self.day, course_area=course_area)
            self.location = self.__get_location(course_area=course_area)
            self.teacher = self.__get_teacher(course_area=course_area)
            self.name = self.__get_name(course_area=course_area)
            self.exam = yellow_percent >= self.__PERCENT_YELLOW_EXAM
        
    def __get_day(self, days: AreaList, course_area: Area) -> Area:
        """Get the day area of the course

        Args:
            days (AreaList): list of days area
            course_area (Area): course area

        Returns:
            Area: day area aligned to the course 
        """
        middle = course_area.center().y
        for d in days:
            full_day: Range = d.to_range(AxeType.ORDINATE)
            if full_day.is_contained(middle):
                return d
    
    def __get_group(self, day: Area, course_area: Area) -> Group:
        """Get the course group

        Args:
            day (Area): the day area of the course
            course_area (Area): the course area

        Returns:
            Group: course group
        """
        if abs(day.h() - course_area.h()) < abs(day.h()/2 - course_area.h()): # closest size (full or half)
            return Group.ALL # full
        if course_area.center().y <= day.center().y:
            return Group.GROUP1 # top
        else:
            return Group.GROUP2 # down
    
    def __get_location(self, course_area: Area) -> str:
        """Get the course location

        Args:
            course_area (Area): the course area

        Returns:
            str: course location
        """
        search_location = [self.__REGEX_LOCATION.search(e).group() for e in course_area.content if self.__REGEX_LOCATION.search(e)]
        for l in search_location:
            if l in course_area.content:
                course_area.content.remove(l)
            else:
                for ca in course_area.content:
                    ca.replace(l,'')
        location = "".join(search_location)
        return location
    
    def __get_teacher(self, course_area: Area) -> str:
        """Get the course teacher

        Args:
            course_area (Area): the course area

        Returns:
            str: course teacher
        """
        if not len(course_area.content):
            return ''
        if len(course_area.content) == 1:
            search_teacher = self.__REGEX_TEACHER.search(string=course_area.content[0])
            result = search_teacher.group(0) if search_teacher else ""
            course_area.content[0] = course_area.content[0].replace(result,'')
            teacher, _ = re.subn(r'[ \)\(\-]','',result)
        else:
            teacher = course_area.content[1]
        return teacher
    
    def __get_name(self, course_area: Area) -> str:
        """Get the course name

        Args:
            course_area (Area): the course area

        Returns:
            str: course name
        """
        if len(course_area.content) == 0:
            return 'Inconnu'
        return course_area.content[0]
    
    def __str__(self) -> str:
        """String function of this class

        Returns:
            str: formated string
        """
        return f'{self.name} : B[{self.begin}] - E[{self.end}] - L[{self.location}] - T[{self.teacher}]] - G[{self.group}] E[{self.exam}]'