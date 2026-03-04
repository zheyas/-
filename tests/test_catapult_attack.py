import pytest
from strategy.models.player import Player
from strategy.models.catapult import Catapult
from strategy.models.archer import Archer
from strategy.models.battle_map import BattleMap
from strategy.controller.game_controller import GameController

@pytest.mark.parametrize("target_x, target_y, expected", [
    (10, 9, False),
    (9, 10, False),
    (30, 31, False),
    (31, 30, False),
    (10, 10, True),
    (30, 30, True),
    (11, 15, True),
    (25, 12, True),
])
def test_catapult_attack(target_x, target_y, expected):
    player1 = Player(1, "Player 1")
    player2 = Player(2, "Player 2")
    catapult = Catapult(player1, x=20, y=20)
    target = Archer(player2, x=target_x, y=target_y)
    game_map = BattleMap(units=[catapult, target])
    controller = GameController(game_map)
    assert controller.can_attack_unit(catapult, target) == expected