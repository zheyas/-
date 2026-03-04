from strategy.models.player import Player
from strategy.models.archer import Archer
from strategy.models.swordsman import Swordsman
from strategy.models.battle_map import BattleMap
from strategy.controller.game_controller import GameController

def test_dead_unit_cannot_move():
    player = Player(1, "Player 1")
    archer = Archer(player, x=10, y=10)
    swordsman = Swordsman(player, x=15, y=15)
    game_map = BattleMap(units=[archer, swordsman])
    controller = GameController(game_map)

    archer.take_damage(archer.max_health)
    assert not archer.is_alive()
    assert controller.can_move_unit(archer, 11, 11) is False

def test_dead_unit_occupies_cell():
    player1 = Player(1, "Player 1")
    player2 = Player(2, "Player 2")
    archer = Archer(player1, x=10, y=10)
    swordsman = Swordsman(player2, x=9, y=9)
    game_map = BattleMap(units=[archer, swordsman])
    controller = GameController(game_map)

    archer.take_damage(archer.max_health)
    assert not archer.is_alive()
    assert controller.can_move_unit(swordsman, 10, 10) is False