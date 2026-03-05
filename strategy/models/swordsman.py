from .unit import Unit

class Swordsman(Unit):
    @property
    def max_health(self) -> int:
        return 100

    @property
    def move_range(self) -> int:
        return 5

    @property
    def attack_range(self) -> int:
        return 1

    @property
    def damage(self) -> int:
        return 50

    def calculate_damage(self, target: Unit) -> int:
        return self.damage
