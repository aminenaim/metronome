
from icalendar import Calendar, Event, vText
from typing import List, Tuple

from .group import Group
from .course import Course
from .time import Time

class EdtCalendar:
    """Class used to generate an ics
    """
    
    __PERIODID = "-//Google Inc//Google Calendar 70.9054//EN" # Google for better description
    """Callendar's Author
    """
    
    __VERSION = '2.0'
    """Calendar verions
    """
    
    def __init__(self, courses: List[Course], level: str, alt: str) -> None:
        """Constructor of EdtCalendar object

        Args:
            courses (List[Course]): list of courses
            level (str): level of the given courses
        """
        self.level = level
        self.alt = alt if alt else level
        self.name = {Group.ALL:f'{level}A', Group.GROUP1:f'{level}G1', Group.GROUP2:f'{level}G2', 'Exam':f'{level}E', 'Full':f'{level}', 'FullG1':f'{self.alt}_GROUPE1', 'FullG2':f'{self.alt}_GROUPE2'}
        self.calendar = {Group.ALL:Calendar(), Group.GROUP1:Calendar(), Group.GROUP2:Calendar(), 'Exam':Calendar(), 'Full':Calendar(), 'FullG1':Calendar(), 'FullG2':Calendar()}
        for c in self.calendar:
            self.calendar[c].add('prodid', self.__PERIODID)
            self.calendar[c].add('version', self.__VERSION)
        self.__gen_ics(courses)
    
    def __gen_ics(self, courses: List[Course]) -> None:
        """Generate ics(s) for the whole class, groups and exams
        
        Args:
            courses (List[Course]): list of courses
        """
        for c in courses:
            if c.exam:
                call: Calendar = self.calendar['Exam']
            else:
                call: Calendar = self.calendar[c.group]
            event = self.__gen_event(course=c)
            call.add_component(event)
            if c.group != Group.GROUP2:
                self.calendar['FullG1'].add_component(event)
            if c.group != Group.GROUP1:
                self.calendar['FullG2'].add_component(event)
            self.calendar['Full'].add_component(event)
    
    def __gen_event(self, course: Course) -> Event:
        """Generate an event from a given course

        Args:
            course (Course): course of the generated event

        Returns:
            Event: the generated event
        """
        event = Event()
        event.add('summary',course.name)
        event.add('dtstart',course.begin)
        event.add('dtend', course.end)
        event.add('dtstamp', Time.today())
        event.add('location', vText(course.location))
        if course.teacher != '':
            v,p = self.__person(name=course.teacher, mail=course.teacher, role='CHAIR', status='ACCEPTED', group=False)
            event.add(name='organizer', value=v, parameters=p, encode=1)
        v,p = self.__person(name=str(course.group), mail=str(course.group).lower().replace(' ',''), role='REQ-PARTICIPANT', status='ACCEPTED', group=True)
        event.add('attendee', value=v, parameters=p, encode=1)
        event.add('description',self.__description(course.teacher, str(course.group), 'Examen' if course.exam else ''))
        return event
        
    
    def __person(self, name:str, mail: str, role: str, status: str, group: bool) ->Tuple[str,dict]:
        """Format a ics person element

        Args:
            name (str): person name 
            mail (str): person email
            role (str): role (check rfc 5545)
            status (str): status (rfc 5545)
            group (bool): group (rfc 5545)

        Returns:
            Tuple[str,dict]: formated person
        """
        cutype = 'GROUP' if group else 'INDIVIDUAL'
        return f'MAILTO:{mail}', {'CUTYPE':cutype, 'ROLE':role, 'PARTSTAT':status, 'CN':name}

    def __description(self, teacher: str, group: str, exam: str) -> str:
        """Create a description with a teacher and a group

        Args:
            teacher (str): course teacher
            group (_type_): course group

        Returns:
            str: description created
        """
        return '<br>'.join([x for x in [teacher, group, exam] if x is not None and x != ''])

    def save(self, directory: str) -> None:
        """Save each event on a file

        Args:
            directory (str): folder where the files should be generated
        """
        for g, n in self.name.items():
            print(f"{self.level} : Creating {n}.ics")
            with open(f'{directory}/{n}.ics', 'wb') as f:
                f.write(self.calendar[g].to_ical())
    
    def get_files_name(self) -> List[str]:
        """Get the ics files names

        Returns:
            List[str]: files names
        """
        return [f'{self.name[n]}.ics' for n in self.name]

