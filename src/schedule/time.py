import re
import pytz
from datetime import datetime, timedelta


class Time:
    """Class managing time elements
    """
    REGEX_WEEK = re.compile(r'^\d{2}[\/-][a-zA-Zéû]{3,4}$')
    """Regex of week date (left of the schedule)
    """
    REGEX_HOUR = re.compile(r'^\d{1,2}h$')
    """Regex of hours elements 
    """
    REGEX_DAY = re.compile(r'^(Lundi|Mardi|Mercredi|Jeudi|Vendredi|Samedi|Dimanche)$')
    """Regex of week days
    """
    MONTHS = {"jan":1,"janv":1, "fév":2,"fev":2, "févr":2,"fevr":2, "mar":3,"mars":3, "avr":4, "avri":4, "mai":5, "jui":6, "juin":6, "juil":7, "aoû":8, "aou":8,"août":8,"aout":8,"sept":9, "sep":9, "oct":10,"octo":10, "nov":11,"nove":11, "déc":12,"dec":12,"déce":12,"dece":12}
    """Month to number dictionnary
    """
    DAYS = {"Lundi":0,"Mardi":1,"Mercredi":2,"Jeudi":3,"Vendredi":4,"Samedi":5,"Dimanche":6}
    """Days to number dictionnary
    """
    TIMEZONE = "Europe/Paris"
    """Timezone of this schedule
    """
    
    def __init__(self, value: str) -> None:
        """Constructor of Time object

        Args:
            value (str): week date string
        """
        assert self.REGEX_WEEK.match(value), f"Wrong format \"{value}\", must match {self.REGEX_WEEK.pattern}"
        day, month = re.split('[/-]', value)
        assert month in self.MONTHS, f"Month value \"{month}\", isn't known"
        today: datetime = datetime.today()
        day = int(day)
        month = self.MONTHS[month]
        year = self.calcul_year(today, month)
        self.value = datetime(day = day, month = month, year=year, tzinfo=pytz.timezone(self.TIMEZONE))
    
    def get_time(self, day: timedelta, hour: timedelta) -> datetime:
        """Get the real time with the given day and hour

        Args:
            day (timedelta): time relative to the first day of the week
            hour (timedelta): time relative to the first hour of the day 

        Returns:
            datetime: real time
        """
        return self.value + day + hour
    
    def calcul_year(self, today: datetime, month: int) -> int:
        """Calcul the years of the week (using scolar year finishing in August)

        Args:
            today (datetime): current time
            month (int): given month of the week

        Returns:
            int: year of the week
        """
        if month < 7 and today.month > 7:
            return today.year + 1
        if month > 7 and today.month < 7:
            return today.year - 1
        return today.year

    @classmethod
    def today(cls) -> datetime:
        """Get current date and time

        Returns:
            datetime: current date and time
        """
        return datetime.utcnow().replace(tzinfo=pytz.timezone(cls.TIMEZONE))
        
    def __str__(self) -> str:
        """Transform time to human readable string

        Returns:
            str: transformed string
        """
        return str(self.value)