from typing import Any, Dict


class Axe(Dict[int, Any]):
    """Class inherited from dict defining a one dimention axe with element in it
    """
    def __init__(self) -> None:
        """Constructor of and Axe from the dict constructor
        """
        super().__init__()
    
    def add(self, x : int, value) -> None:
        """Add coordinate with value to the dict

        Args:
            x (int): _description_
            value (_type_): _description_
        """
        self[x] = value
    
    def closest(self, x: int) -> Any:
        """Get the closest element form the Axe

        Args:
            x (int): coordinate reference

        Returns:
            Any: content of the closest element from the reference
        """
        key = min(self, key=lambda l:abs(l-x))
        return self[key]