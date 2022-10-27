from datetime import datetime,timedelta
from dateutil import tz
import re
import arrow

class Time:
    REGEX_WEEK = re.compile(r'^\d{2}(/|-)[a-z-À-ÿ]{3,4}$')
    REGEX_HOUR = re.compile(r'^\d{1,2}h$')
    REGEX_DAY = re.compile(r'^(Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche)$')
    MONTHS = {"jan":1,"janv":1, "fév":2,"fev":2, "févr":2,"fevr":2, "mar":3,"mars":3, "avr":4, "avri":4, "mai":5, "jui":6, "juin":6, "juil":7, "aoû":8, "aou":8,"août":8,"aout":8,"sept":9, "sep":9, "oct":10,"octo":10, "nov":11,"nove":11, "déc":12,"dec":12,"déce":12,"dece":12}
    DAYS = {"Lundi":0,"Mardi":1,"Mercredi":2,"Jeudi":3,"Vendredi":4,"Samedi":5,"Dimanche":6}
    
    def __init__(self, value: str) -> None:
        assert self.REGEX_WEEK.match(value), f"Wrong format \"{value}\", must match {self.REGEX_WEEK.pattern}"
        day, month = re.split('[/-]', value)
        assert month in self.MONTHS, f"Month value \"{month}\", isn't known"
        today: datetime = datetime.today()
        day = int(day)
        month = self.MONTHS[month]
        year = self.calcul_year(today, month)
        self.value = datetime(day = day, month = month, year=year)
    
    def get_time(self, day: timedelta, hour: timedelta, timezone: str = "") -> arrow:
        return arrow.get(self.value + day + hour, tz.gettz(timezone))
    
    def calcul_year(self, today: datetime, month: int):
        if month < 7 and today.month > 7:
            return today.year + 1
        if month > 7 and today.month < 7:
            return today.year - 1
        return today.year
        
    def __str__(self) -> str:
        return str(self.value)