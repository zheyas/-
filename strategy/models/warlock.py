from typing import List, Optional
from .unit import Unit
from .player import Player
from .battle_map import BattleMap


class Warlock(Unit):
    def __init__(self, player: Player, x: int = 0, y: int = 0):
        super().__init__(player, x, y)
        self.curse_target: Optional[Unit] = None
        self.curse_timer: int = 0
        self.curse_used: bool = False
        self.earthquake_used: bool = False

    @property
    def max_health(self) -> int:
        return 80

    @property
    def move_range(self) -> int:
        return 4

    @property
    def attack_range(self) -> int:
        return 3

    @property
    def damage(self) -> int:
        return 40

    def calculate_damage(self, target: Unit) -> int:
        return self.damage

    def can_use_curse(self) -> bool:
        return self.is_alive() and not self.curse_used

    def can_use_earthquake(self) -> bool:
        return self.is_alive() and not self.earthquake_used

    def cast_curse(self, target: Unit) -> bool:
        if not self.can_use_curse() or not target.is_alive() or target.player == self.player:
            return False

        self.curse_target = target
        self.curse_timer = 2
        self.curse_used = True
        return True

    def cast_earthquake(self, battle_map: BattleMap, target_x: int, target_y: int) -> List[Unit]:
        if not self.can_use_earthquake():
            return []

        damaged_units = []
        for unit in battle_map.units:
            if unit == self or not unit.is_alive():
                continue
            if abs(unit.x - target_x) <= 1 and abs(unit.y - target_y) <= 1:
                unit.take_damage(60)
                damaged_units.append(unit)

        self.earthquake_used = True
        return damaged_units

    def update_curse(self):
        if self.curse_target and self.curse_target.is_alive():
            self.curse_timer -= 1
            if self.curse_timer <= 0:
                self.curse_target.take_damage(100)
                self.curse_target = None
                self.curse_timer = 0

    def reset_abilities_for_new_turn(self):
        self.curse_used = False
        self.earthquake_used = False
