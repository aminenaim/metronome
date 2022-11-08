from enum import Enum


class Group(Enum):
    ALL = 0
    GROUP1 = 1
    GROUP2 = 2
    
    def __str__(self) -> str:
        value = {Group.ALL: 'Classe Entière', Group.GROUP1: 'Groupe 1', Group.GROUP2: 'Groupe 2'}
        return value[self]