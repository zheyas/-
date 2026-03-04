import pytest
from strategy.models.player import Player
from strategy.models.horseman import Horseman
from strategy.models.battle_map import BattleMap
from strategy.controller.game_controller import GameController

@pytest.mark.parametrize("target_x, target_y, expected", [
    (10, 9, False),
    (9, 10, False),
    (30, 31, False),
    (31, 30, False),
    (20, 20, False),
    (10, 10, True),
    (30, 30, True),
    (11, 15, True),
    (25, 12, True),
])
def test_horseman_movement(target_x, target_y, expected):
    player = Player(1, "Player 1")
    horseman = Horseman(player, x=20, y=20)
    game_map = BattleMap(units=[horseman])
    controller = GameController(game_map)
    assert controller.can_move_unit(horseman, target_x, target_y) == expected