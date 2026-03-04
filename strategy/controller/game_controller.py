from typing import Union, Optional
from ..models.battle_map import BattleMap
from ..models.unit import Unit
from ..models.terrain import Terrain, Grass, Water
from ..models.coordinates import Coordinates
from ..models.archer import Archer
from ..models.catapult import Catapult
from ..models.horseman import Horseman
from ..models.swordsman import Swordsman

class GameController:
    def __init__(self, game_map: BattleMap):
        self._game_map = game_map

    def get_object_coordinates(self, obj: Union[Unit, Terrain]) -> Coordinates:
        return Coordinates(obj.x, obj.y)

    def can_move_unit(self, unit: Unit, x: int, y: int) -> bool:
        if not unit.is_alive():
            return False
        if x == unit.x and y == unit.y:  # НЕЛЬЗЯ СТОЯТЬ НА МЕСТЕ
            return False
        if not unit.can_move(x, y):
            return False
        return self._game_map.is_cell_passable(x, y, ignore_unit=unit)

    def move_unit(self, unit: Unit, x: int, y: int):
        if self.can_move_unit(unit, x, y):
            unit.x = x
            unit.y = y

    def can_attack_unit(self, attacker: Unit, target: Unit) -> bool:
        return attacker.can_attack(target)

    def attack_unit(self, attacker: Unit, target: Unit):
        if not self.can_attack_unit(attacker, target):
            return
        damage = attacker.calculate_damage(target)
        target.take_damage(damage)

    def get_object_source(self, obj: Union[Unit, Terrain]) -> Optional[str]:
        if isinstance(obj, Unit):
            if not obj.is_alive():
                return "strategy/assets/units/dead.png"
            if isinstance(obj, Archer):
                return "strategy/assets/units/archer.png"
            if isinstance(obj, Catapult):
                return "strategy/assets/units/catapult.png"
            if isinstance(obj, Horseman):
                return "strategy/assets/units/horseman.png"
            if isinstance(obj, Swordsman):
                return "strategy/assets/units/swordsman.png"
        elif isinstance(obj, Grass):
            return "strategy/assets/ground/grass.png"
        elif isinstance(obj, Water):
            return "strategy/assets/ground/water.png"
        return None

    def get_unit_health(self, unit: Unit) -> int:
        return unit.health

    def get_max_health(self, unit: Unit) -> int:
        return unit.max_health