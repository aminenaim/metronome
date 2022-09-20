from datetime import datetime,timedelta
from dateutil import tz
import re
import arrow

class Timetable:
    REGEX_HOUR = re.compile(r'^\d{1,2}h$')
    REGEX_DAY = re.compile(r'^(Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche)$')
    __DAYS = {"Lundi":0,"Mardi":1,"Mercredi":2,"Jeudi":3,"Vendredi":4,"Samedi":5,"Dimanche":6}
    
    def __init__(self, value: str) -> None:
        assert self.REGEX_HOUR.match(value), f"Wrong format \"{value}\", hour must be in format 24h"
        self.value = timedelta(hours=int(value.replace('h', '')))
    
    def set_day(self, day: str) -> None:
        assert self.REGEX_DAY.search(day), f"Must be a day matching {self.REGEX_DAY.pattern}"
        self.value += timedelta(days=self.__DAYS[day])

    def __str__(self) -> str:
        return str(self.value)

class Time:
    REGEX_WEEK = re.compile(r'^\d{2}/[a-z-À-ÿ]{3,4}$')
    __MONTHS = {"jan":1,"janv":1, "fév":2,"fev":2, "févr":2,"fevr":2, "mar":3,"mars":3, "avr":4, "avri":4, "mai":5, "jui":6, "juin":6, "juil":7, "aoû":8, "aou":8,"août":8,"aout":8,"sept":9, "sep":9, "oct":10,"octo":10, "nov":11,"nove":11, "déc":12,"dec":12,"déce":12,"dece":12}
    
    def __init__(self, value: str) -> None:
        assert self.REGEX_WEEK.match(value), f"Wrong format \"{value}\", must match {self.REGEX_WEEK.pattern}"
        day, month = re.split("/", value)
        assert month in self.__MONTHS, f"Month value \"{month}\", isn't known"
        
        today: datetime = datetime.today()
        if today <= datetime(day = int(day), month = self.__MONTHS[month], year=today.year):
            year = today.year
        else:
            year = today.year - 1
        self.value = datetime(day = int(day), month = self.__MONTHS[month], year=year)
    
    def from_today(self, delta: Timetable, timezone: str = "") -> arrow:
        return arrow.get(self.value + delta.value, tz.gettz(timezone))
    
    def __str__(self) -> str:
        return str(self.value)