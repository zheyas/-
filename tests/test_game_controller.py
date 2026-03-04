import pytest
from strategy.models.player import Player
from strategy.models.archer import Archer
from strategy.models.catapult import Catapult
from strategy.models.horseman import Horseman
from strategy.models.swordsman import Swordsman
from strategy.models.terrain import Grass, Water
from strategy.models.battle_map import BattleMap
from strategy.controller.game_controller import GameController

def test_get_object_coordinates():
    player = Player(1, "Player 1")
    units = [
        Archer(player, x=1, y=2),
        Catapult(player, x=3, y=4),
        Horseman(player, x=5, y=6),
        Swordsman(player, x=7, y=8)
    ]
    grounds = [
        Grass(x=9, y=10),
        Water(x=11, y=12)
    ]
    game_map = BattleMap(ground=grounds, units=units)
    controller = GameController(game_map)

    for unit in units:
        coords = controller.get_object_coordinates(unit)
        assert coords.x == unit.x and coords.y == unit.y

    for ground in grounds:
        coords = controller.get_object_coordinates(ground)
        assert coords.x == ground.x and coords.y == ground.y

def test_move_unit_on_grass():
    player = Player(1, "Player 1")
    swordsman = Swordsman(player, x=10, y=10)
    grass = Grass(x=15, y=15)
    game_map = BattleMap(ground=[grass], units=[swordsman])
    controller = GameController(game_map)
    assert controller.can_move_unit(swordsman, 15, 15) is True
    controller.move_unit(swordsman, 15, 15)
    assert swordsman.x == 15 and swordsman.y == 15

def test_move_unit_on_water():
    player = Player(1, "Player 1")
    swordsman = Swordsman(player, x=10, y=10)
    water = Water(x=15, y=15)
    game_map = BattleMap(ground=[water], units=[swordsman])
    controller = GameController(game_map)
    assert controller.can_move_unit(swordsman, 15, 15) is False

def test_move_unit_on_occupied_cell():
    player = Player(1, "Player 1")
    catapult = Catapult(player, x=10, y=10)
    horseman = Horseman(player, x=15, y=15)
    game_map = BattleMap(units=[catapult, horseman])
    controller = GameController(game_map)
    assert controller.can_move_unit(catapult, 15, 15) is False

def test_attack_friendly_unit():
    player = Player(1, "Player 1")
    archer = Archer(player, x=10, y=10)
    target = Archer(player, x=11, y=11)
    game_map = BattleMap(units=[archer, target])
    controller = GameController(game_map)
    assert controller.can_attack_unit(archer, target) is False

def test_attack_kill_counts():
    player1 = Player(1, "Player 1")
    player2 = Player(2, "Player 2")
    archer = Archer(player1, x=8, y=8)
    targets = [
        Archer(player2, x=10, y=10),
        Catapult(player2, x=10, y=10),
        Horseman(player2, x=10, y=10),
        Swordsman(player2, x=10, y=10),
    ]
    expected_hits = [1, 2, 4, 2]

    for target, expected in zip(targets, expected_hits):
        archer.health = archer.max_health
        target.health = target.max_health
        game_map = BattleMap(units=[archer, target])
        controller = GameController(game_map)
        hits = 0
        while controller.can_attack_unit(archer, target):
            controller.attack_unit(archer, target)
            hits += 1
        assert hits == expected

def test_get_object_source_not_none():
    player = Player(1, "Player 1")
    game_map = BattleMap()
    controller = GameController(game_map)
    assert controller.get_object_source(Archer(player)) is not None
    assert controller.get_object_source(Catapult(player)) is not None
    assert controller.get_object_source(Horseman(player)) is not None
    assert controller.get_object_source(Swordsman(player)) is not None
    assert controller.get_object_source(Grass()) is not None
    assert controller.get_object_source(Water()) is not None