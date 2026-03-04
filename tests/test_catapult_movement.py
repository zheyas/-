import pytest
from strategy.models.player import Player
from strategy.models.catapult import Catapult
from strategy.models.battle_map import BattleMap
from strategy.controller.game_controller import GameController

@pytest.mark.parametrize("target_x, target_y, expected", [
    (8, 9, False),
    (9, 8, False),
    (10, 10, False),
    (11, 12, False),
    (12, 11, False),
    (9, 10, True),
    (11, 10, True),
    (9, 9, True),
    (11, 11, True),
])
def test_catapult_movement(target_x, target_y, expected):
    player = Player(1, "Player 1")
    catapult = Catapult(player, x=10, y=10)
    game_map = BattleMap(units=[catapult])
    controller = GameController(game_map)
    assert controller.can_move_unit(catapult, target_x, target_y) == expected