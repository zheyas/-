import pytest
from strategy.models.player import Player
from strategy.models.archer import Archer
from strategy.models.battle_map import BattleMap
from strategy.controller.game_controller import GameController

@pytest.mark.parametrize("target_x, target_y, expected", [
    (6, 7, False),
    (7, 6, False),
    (14, 13, False),
    (13, 14, False),
    (10, 10, False),
    (9, 10, True),
    (11, 10, True),
    (7, 7, True),
    (13, 13, True),
])
def test_archer_movement(target_x, target_y, expected):
    player = Player(1, "Player 1")
    archer = Archer(player, x=10, y=10)
    game_map = BattleMap(units=[archer])
    controller = GameController(game_map)
    assert controller.can_move_unit(archer, target_x, target_y) == expected