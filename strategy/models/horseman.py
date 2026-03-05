from .unit import Unit

class Horseman(Unit):
    @property
    def max_health(self) -> int:
        return 200

    @property
    def move_range(self) -> int:
        return 10

    @property
    def attack_range(self) -> int:
        return 1

    @property
    def damage(self) -> int:
        return 75

    def calculate_damage(self, target: Unit) -> int:
        return self.damage
