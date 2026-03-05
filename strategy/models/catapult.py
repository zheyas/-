from .unit import Unit

class Catapult(Unit):
    @property
    def max_health(self) -> int:
        return 70

    @property
    def move_range(self) -> int:
        return 1

    @property
    def attack_range(self) -> int:
        return 10

    @property
    def damage(self) -> int:
        return 100

    def calculate_damage(self, target: Unit) -> int:
        dx = abs(self.x - target.x)
        dy = abs(self.y - target.y)
        if dx <= 1 and dy <= 1:
            return self.damage // 2
        return self.damage
