import pytest
from strategy.models.player import Player
from strategy.models.archer import Archer
from strategy.models.battle_map import BattleMap
from strategy.controller.game_controller import GameController

@pytest.mark.parametrize("target_x, target_y, expected", [
    (4, 5, False),
    (5, 4, False),
    (15, 16, False),
    (16, 15, False),
    (5, 5, True),
    (15, 15, True),
    (9, 10, True),
    (12, 7, True),
])
def test_archer_attack(target_x, target_y, expected):
    player1 = Player(1, "Player 1")
    player2 = Player(2, "Player 2")
    archer = Archer(player1, x=10, y=10)
    target = Archer(player2, x=target_x, y=target_y)
    game_map = BattleMap(units=[archer, target])
    controller = GameController(game_map)
    assert controller.can_attack_unit(archer, target) == expected