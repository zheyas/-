import pytest
from strategy.models.player import Player
from strategy.models.swordsman import Swordsman
from strategy.models.archer import Archer
from strategy.models.battle_map import BattleMap
from strategy.controller.game_controller import GameController

@pytest.mark.parametrize("target_x, target_y, expected", [
    (8, 9, False),
    (9, 8, False),
    (11, 12, False),
    (12, 11, False),
    (11, 11, True),
    (10, 11, True),
    (9, 9, True),
    (9, 10, True),
])
def test_swordsman_attack(target_x, target_y, expected):
    player1 = Player(1, "Player 1")
    player2 = Player(2, "Player 2")
    swordsman = Swordsman(player1, x=10, y=10)
    target = Archer(player2, x=target_x, y=target_y)
    game_map = BattleMap(units=[swordsman, target])
    controller = GameController(game_map)
    assert controller.can_attack_unit(swordsman, target) == expected