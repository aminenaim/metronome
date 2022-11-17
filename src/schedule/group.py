from enum import Enum


class Group(Enum):
    """Group enumeration
    """
    ALL = 0
    """Whole class
    """
    GROUP1 = 1
    """First group
    """
    GROUP2 = 2
    """Second group
    """
    
    def __str__(self) -> str:
        """String formating of group

        Returns:
            str: formated group
        """
        value = {Group.ALL: 'Classe Entière', Group.GROUP1: 'Groupe 1', Group.GROUP2: 'Groupe 2'}
        return value[self]