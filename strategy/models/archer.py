from .unit import Unit

class Archer(Unit):
    @property
    def max_health(self) -> int:
        return 50

    @property
    def move_range(self) -> int:
        return 3

    @property
    def attack_range(self) -> int:
        return 5

    @property
    def damage(self) -> int:
        return 50

    def calculate_damage(self, target: Unit) -> int:
        dx = abs(self.x - target.x)
        dy = abs(self.y - target.y)
        if dx <= 1 and dy <= 1:
            return self.damage // 2
        return self.damage
