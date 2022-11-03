from typing import Any


class Axe(dict):
    def __init__(self) -> None:
        super().__init__()
    
    def add(self, x : int, value) -> None:
        self[x] = value
    
    def closest(self, x: int) -> Any:
        key = min(self, key=lambda l:abs(l-x))
        return self[key]