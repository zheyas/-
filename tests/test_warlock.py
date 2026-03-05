import pytest
from strategy.models.player import Player
from strategy.models.warlock import Warlock
from strategy.models.archer import Archer
from strategy.models.battle_map import BattleMap


def test_warlock_creation():
    player = Player(1, "Player 1")
    warlock = Warlock(player, x=5, y=5)
    assert warlock.max_health == 80
    assert warlock.move_range == 4
    assert warlock.attack_range == 3
    assert warlock.damage == 40
    assert warlock.health == 80


def test_warlock_curse():
    player1 = Player(1, "Player 1")
    player2 = Player(2, "Player 2")  # другой игрок!
    warlock = Warlock(player1, x=5, y=5)
    target = Archer(player2, x=6, y=6)  # цель - враг

    assert warlock.can_use_curse() is True
    result = warlock.cast_curse(target)
    assert result is True
    assert warlock.curse_target == target
    assert warlock.curse_timer == 2
    assert warlock.can_use_curse() is False

    # Проклятие не сработало сразу
    assert target.health == 50

    # Проходит ход
    warlock.update_curse()
    assert warlock.curse_timer == 1

    # Ещё ход - проклятие срабатывает
    warlock.update_curse()
    assert target.health == 0  # target умер
    assert warlock.curse_target is None


def test_warlock_earthquake():
    player1 = Player(1, "Player 1")
    player2 = Player(2, "Player 2")
    warlock = Warlock(player1, x=5, y=5)

    units = [
        warlock,
        Archer(player2, x=3, y=3),
        Archer(player2, x=4, y=4),
        Archer(player2, x=5, y=5),
        Archer(player2, x=7, y=7),
    ]
    for u in units[1:]:
        u.health = u.max_health

    game_map = BattleMap(units=units)

    assert warlock.can_use_earthquake() is True
    damaged = warlock.cast_earthquake(game_map, 4, 4)
    assert len(damaged) == 3
    assert units[1].health == 0
    assert units[2].health == 0
    assert units[3].health == 0
    assert units[4].health == 50
    assert warlock.can_use_earthquake() is False


def test_warlock_abilities_reset():
    player1 = Player(1, "Player 1")
    player2 = Player(2, "Player 2")  # два разных игрока
    warlock = Warlock(player1, x=5, y=5)

    # Используем проклятие на ВРАГА
    target = Archer(player2, x=6, y=6)  # теперь это враг
    warlock.cast_curse(target)
    assert warlock.can_use_curse() is False
    assert warlock.can_use_earthquake() is True

    # Сбрасываем способности
    warlock.reset_abilities_for_new_turn()
    assert warlock.can_use_curse() is True
    assert warlock.can_use_earthquake() is True