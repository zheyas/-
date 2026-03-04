import pytest
from strategy.models.player import Player
from strategy.models.swordsman import Swordsman
from strategy.models.battle_map import BattleMap
from strategy.controller.game_controller import GameController

@pytest.mark.parametrize("target_x, target_y, expected", [
    (4, 5, False),
    (5, 4, False),
    (15, 16, False),
    (16, 15, False),
    (10, 10, False),
    (5, 5, True),
    (15, 15, True),
    (9, 10, True),
    (12, 7, True),
])
def test_swordsman_movement(target_x, target_y, expected):
    player = Player(1, "Player 1")
    swordsman = Swordsman(player, x=10, y=10)
    game_map = BattleMap(units=[swordsman])
    controller = GameController(game_map)
    assert controller.can_move_unit(swordsman, target_x, target_y) == expected