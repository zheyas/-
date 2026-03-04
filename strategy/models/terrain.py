from abc import ABC, abstractmethod

class Terrain(ABC):
    def __init__(self, x: int = 0, y: int = 0):
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: int):
        self._x = value

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, value: int):
        self._y = value

    @abstractmethod
    def is_passable(self) -> bool:
        pass

class Grass(Terrain):
    def is_passable(self) -> bool:
        return True

class Water(Terrain):
    def is_passable(self) -> bool:
        return False