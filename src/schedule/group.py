from enum import Enum


class Group(Enum):
    ALL = 0
    GROUP1 = 1
    GROUP2 = 2
    
    def __str__(self) -> str:
        value = {Group.ALL: 'ALL', Group.GROUP1: 'GROUP1', Group.GROUP2: 'GROUP2'}
        return value[self]