from abc import ABC, abstractmethod
from .player import Player

class Unit(ABC):
    def __init__(self, player: Player, x: int = 0, y: int = 0):
        self.player = player
        self._x = x
        self._y = y
        self.health = self.max_health

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

    @property
    @abstractmethod
    def max_health(self) -> int:
        pass

    @property
    @abstractmethod
    def move_range(self) -> int:
        pass

    @property
    @abstractmethod
    def attack_range(self) -> int:
        pass

    @property
    @abstractmethod
    def damage(self) -> int:
        pass

    def is_alive(self) -> bool:
        return self.health > 0

    def take_damage(self, amount: int):
        self.health = max(self.health - amount, 0)

    def can_move(self, target_x: int, target_y: int) -> bool:
        if not self.is_alive():
            return False
        return abs(self.x - target_x) <= self.move_range and abs(self.y - target_y) <= self.move_range

    def can_attack(self, target: 'Unit') -> bool:
        if not self.is_alive() or not target.is_alive():
            return False
        if self.player == target.player:
            return False
        dx = abs(self.x - target.x)
        dy = abs(self.y - target.y)
        return dx <= self.attack_range and dy <= self.attack_range

    @abstractmethod
    def calculate_damage(self, target: 'Unit') -> int:
        pass
