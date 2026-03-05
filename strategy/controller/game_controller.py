from typing import Union, Optional
from ..models.battle_map import BattleMap
from ..models.unit import Unit
from ..models.terrain import Terrain, Grass, Water, Bridge
from ..models.coordinates import Coordinates
from ..models.archer import Archer
from ..models.catapult import Catapult
from ..models.horseman import Horseman
from ..models.swordsman import Swordsman
from ..models.warlock import Warlock


class GameController:
    def __init__(self, game_map: BattleMap):
        self._game_map = game_map

    def get_object_coordinates(self, obj: Union[Unit, Terrain]) -> Coordinates:
        return Coordinates(obj.x, obj.y)

    def can_move_unit(self, unit: Unit, x: int, y: int) -> bool:
        if not unit.is_alive():
            print(f"  ❌ Юнит мёртв")
            return False
        if x == unit.x and y == unit.y:
            print(f"  ❌ Та же клетка")
            return False
        if not unit.can_move(x, y):
            print(f"  ❌ Слишком далеко")
            return False

        # Получаем тип местности в целевой клетке
        target_terrain = self._game_map.get_terrain_at(x, y)

        # Отладка
        terrain_type = type(target_terrain).__name__ if target_terrain else "None"
        print(f"  🏞️ Terrain at ({x},{y}): {terrain_type}")

        # Нельзя ходить по воде!
        if isinstance(target_terrain, Water):
            print(f"  ❌ Это вода! Нельзя ходить")
            return False

        # Проверяем, не занята ли клетка другим юнитом
        target_unit = self._game_map.get_unit_at(x, y)
        if target_unit and target_unit != unit:
            print(f"  ❌ Клетка занята юнитом {type(target_unit).__name__}")
            return False

        print(f"  ✅ Можно идти")
        return True

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
            if isinstance(obj, Warlock):
                return "strategy/assets/units/warlock.png"
        elif isinstance(obj, Grass):
            return "strategy/assets/ground/grass.png"
        elif isinstance(obj, Water):
            return "strategy/assets/ground/water.png"
        elif isinstance(obj, Bridge):
            return "strategy/assets/ground/bridge.png"
        return None

    def get_unit_health(self, unit: Unit) -> int:
        return unit.health

    def get_max_health(self, unit: Unit) -> int:
        return unit.max_health
