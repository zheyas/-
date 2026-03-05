from typing import List, Optional
from .terrain import Terrain
from .unit import Unit

class BattleMap:
    def __init__(self, ground: Optional[List[Terrain]] = None, units: Optional[List[Unit]] = None):
        self._ground = ground[:] if ground else []
        self._units = units[:] if units else []

    @property
    def ground(self) -> List[Terrain]:
        return self._ground

    @property
    def units(self) -> List[Unit]:
        return self._units

    def get_terrain_at(self, x: int, y: int) -> Optional[Terrain]:
        for t in self._ground:
            if t.x == x and t.y == y:
                return t
        return None

    def get_unit_at(self, x: int, y: int) -> Optional[Unit]:
        for u in self._units:
            if u.x == x and u.y == y:
                return u
        return None

    def is_cell_passable(self, x: int, y: int, ignore_unit: Optional[Unit] = None) -> bool:
        terrain = self.get_terrain_at(x, y)
        if terrain and not terrain.is_passable():
            return False
        unit = self.get_unit_at(x, y)
        if unit and unit != ignore_unit:
            return False
        return True
