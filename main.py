import pygame
import sys
import os
import random
import requests
from typing import Optional, Tuple, Set

from strategy.models.player import Player
from strategy.models.archer import Archer
from strategy.models.catapult import Catapult
from strategy.models.horseman import Horseman
from strategy.models.swordsman import Swordsman
from strategy.models.terrain import Grass, Water
from strategy.models.battle_map import BattleMap
from strategy.controller.game_controller import GameController

# ================== НАСТРОЙКИ ИГРЫ ==================
CELL_SIZE = 64
MAP_WIDTH = 10
MAP_HEIGHT = 10
SCREEN_WIDTH = CELL_SIZE * MAP_WIDTH
SCREEN_HEIGHT = CELL_SIZE * MAP_HEIGHT + 100  # +100 для панели информации

# Цвета-заглушки (если нет изображений)
COLORS = {
    'grass': (100, 200, 100),
    'water': (64, 164, 223),
    'archer': (255, 255, 0),
    'catapult': (128, 128, 128),
    'horseman': (255, 0, 0),
    'swordsman': (0, 255, 0),
    'dead': (0, 0, 0),
    'selected': (255, 255, 255, 128),
    'move_highlight': (0, 255, 0, 100),
    'text': (255, 255, 255),
    'panel': (50, 50, 50),
    'border': (200, 200, 200)
}

# РАБОЧИЕ ССЫЛКИ НА ИЗОБРАЖЕНИЯ
IMAGE_URLS = {
    'archer': 'https://opengameart.org/sites/default/files/archer_0.png',
    'catapult': 'https://opengameart.org/sites/default/files/catapult_0.png',
    'horseman': 'https://opengameart.org/sites/default/files/knight_0.png',
    'swordsman': 'https://opengameart.org/sites/default/files/swordsman_0.png',
    'dead': 'https://via.placeholder.com/64/000000/000000?text=+',
    'grass': 'https://opengameart.org/sites/default/files/grass_0.png',
    'water': 'https://opengameart.org/sites/default/files/water_0.png'
}

# ================== ФУНКЦИИ ЗАГРУЗКИ ==================
def download_image(url: str, save_path: str) -> bool:
    """Скачивает изображение по URL и сохраняет в указанный путь."""
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        if os.path.exists(save_path):
            print(f"Файл уже существует: {save_path}")
            return True
        print(f"Скачивание {url} -> {save_path}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Успешно загружено: {save_path}")
        return True
    except Exception as e:
        print(f"Ошибка загрузки {url}: {e}")
        return False

def ensure_assets():
    """Создаёт папки и скачивает изображения, если их нет."""
    os.makedirs("strategy/assets/units", exist_ok=True)
    os.makedirs("strategy/assets/ground", exist_ok=True)
    for key, url in IMAGE_URLS.items():
        if key in ('grass', 'water'):
            path = f"strategy/assets/ground/{key}.png"
        else:
            path = f"strategy/assets/units/{key}.png"
        download_image(url, path)

# ================== ГРАФИЧЕСКИЙ КЛАСС ==================
class GameGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Strategy Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 32)

        ensure_assets()
        self.images = self.load_images()
        self.setup_game()

        self.selected_unit = None
        self.current_player_index = 0
        self.message = "Выберите юнита"
        self.message_timer = 0
        self.possible_moves: Set[Tuple[int, int]] = set()

    def load_images(self) -> dict:
        images = {}
        base_path = "strategy/assets"
        paths = {
            'grass': os.path.join(base_path, "ground", "grass.png"),
            'water': os.path.join(base_path, "ground", "water.png"),
            'archer': os.path.join(base_path, "units", "archer.png"),
            'catapult': os.path.join(base_path, "units", "catapult.png"),
            'horseman': os.path.join(base_path, "units", "horseman.png"),
            'swordsman': os.path.join(base_path, "units", "swordsman.png"),
            'dead': os.path.join(base_path, "units", "dead.png")
        }
        for key, path in paths.items():
            try:
                if os.path.exists(path):
                    img = pygame.image.load(path)
                    images[key] = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
                else:
                    images[key] = None
                    print(f"Файл {path} не найден, будет использован цвет-заглушка")
            except Exception as e:
                images[key] = None
                print(f"Ошибка загрузки {path}: {e}")
        return images

    def setup_game(self):
        random.seed(42)
        self.players = [
            Player(1, "Игрок 1"),
            Player(2, "Игрок 2")
        ]

        ground = []
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if random.random() < 0.1:
                    ground.append(Water(x=x, y=y))
                else:
                    ground.append(Grass(x=x, y=y))

        free_cells = [(x, y) for x in range(MAP_WIDTH) for y in range(MAP_HEIGHT)
                      if not any(isinstance(t, Water) for t in ground if t.x == x and t.y == y)]

        left_cells = [c for c in free_cells if c[0] < MAP_WIDTH // 2]
        right_cells = [c for c in free_cells if c[0] >= MAP_WIDTH // 2]

        random.shuffle(left_cells)
        random.shuffle(right_cells)

        units = []
        unit_types = [Archer, Catapult, Horseman, Swordsman]
        for i, cls in enumerate(unit_types):
            if i < len(left_cells):
                x, y = left_cells[i]
                units.append(cls(self.players[0], x=x, y=y))

        for i, cls in enumerate(unit_types):
            if i < len(right_cells):
                x, y = right_cells[i]
                units.append(cls(self.players[1], x=x, y=y))

        self.battle_map = BattleMap(ground=ground, units=units)
        self.controller = GameController(self.battle_map)

    def compute_possible_moves(self, unit) -> Set[Tuple[int, int]]:
        moves = set()
        if not unit or not unit.is_alive():
            return moves
        for dx in range(-unit.move_range, unit.move_range + 1):
            for dy in range(-unit.move_range, unit.move_range + 1):
                nx, ny = unit.x + dx, unit.y + dy
                if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                    if self.controller.can_move_unit(unit, nx, ny):
                        moves.add((nx, ny))
        return moves

    def draw_cell(self, x: int, y: int, terrain, unit: Optional = None, highlight: bool = False):
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        if isinstance(terrain, Water) and self.images.get('water'):
            self.screen.blit(self.images['water'], rect)
        elif isinstance(terrain, Grass) and self.images.get('grass'):
            self.screen.blit(self.images['grass'], rect)
        else:
            color = COLORS['water'] if isinstance(terrain, Water) else COLORS['grass']
            pygame.draw.rect(self.screen, color, rect)

        if unit:
            unit_img = None
            if not unit.is_alive() and self.images.get('dead'):
                unit_img = self.images['dead']
            elif isinstance(unit, Archer):
                unit_img = self.images.get('archer')
            elif isinstance(unit, Catapult):
                unit_img = self.images.get('catapult')
            elif isinstance(unit, Horseman):
                unit_img = self.images.get('horseman')
            elif isinstance(unit, Swordsman):
                unit_img = self.images.get('swordsman')

            if unit_img:
                self.screen.blit(unit_img, rect)
            else:
                color = COLORS['dead'] if not unit.is_alive() else {
                    Archer: COLORS['archer'],
                    Catapult: COLORS['catapult'],
                    Horseman: COLORS['horseman'],
                    Swordsman: COLORS['swordsman']
                }.get(type(unit), COLORS['swordsman'])
                pygame.draw.rect(self.screen, color, rect)

        pygame.draw.rect(self.screen, COLORS['border'], rect, 1)

        if highlight:
            s = pygame.Surface((CELL_SIZE, CELL_SIZE))
            s.set_alpha(100)
            s.fill(COLORS['move_highlight'][:3])
            self.screen.blit(s, rect)

        if self.selected_unit == unit:
            s = pygame.Surface((CELL_SIZE, CELL_SIZE))
            s.set_alpha(128)
            s.fill(COLORS['selected'])
            self.screen.blit(s, rect)

    def draw_info_panel(self):
        panel_rect = pygame.Rect(0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100)
        pygame.draw.rect(self.screen, COLORS['panel'], panel_rect)
        pygame.draw.rect(self.screen, COLORS['border'], panel_rect, 2)

        y_offset = SCREEN_HEIGHT - 90

        current_player = self.players[self.current_player_index]
        player_text = f"Ход: {current_player.name}"
        text = self.font.render(player_text, True, COLORS['text'])
        self.screen.blit(text, (10, y_offset))

        if self.selected_unit:
            unit_type = type(self.selected_unit).__name__
            health = self.controller.get_unit_health(self.selected_unit)
            max_health = self.controller.get_max_health(self.selected_unit)
            health_text = f"{unit_type}: HP {health}/{max_health}"
            text = self.font.render(health_text, True, COLORS['text'])
            self.screen.blit(text, (10, y_offset + 25))

            stats_text = f"Атака: {self.selected_unit.damage} | Дальность: {self.selected_unit.attack_range} | Движение: {self.selected_unit.move_range}"
            text = self.font.render(stats_text, True, COLORS['text'])
            self.screen.blit(text, (10, y_offset + 50))

        if self.message_timer > 0:
            text = self.font.render(self.message, True, COLORS['text'])
            self.screen.blit(text, (SCREEN_WIDTH - 300, y_offset + 25))
            self.message_timer -= 1

    def get_cell_from_pos(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        x, y = pos
        if x < 0 or x >= SCREEN_WIDTH or y < 0 or y >= SCREEN_HEIGHT - 100:
            return None
        return (x // CELL_SIZE, y // CELL_SIZE)

    def handle_click(self, pos: Tuple[int, int], button: int):
        cell = self.get_cell_from_pos(pos)
        if not cell:
            return

        x, y = cell
        unit = self.battle_map.get_unit_at(x, y)
        terrain = self.battle_map.get_terrain_at(x, y) or Grass(x=x, y=y)

        # Отладка
        print(f"Клик: button={button}, клетка ({x},{y}), юнит={unit}")

        # Правая кнопка (или средняя на некоторых Mac) — сброс выбора
        if button in (2, 3):
            self.selected_unit = None
            self.possible_moves.clear()
            self.message = "Выбор отменён"
            self.message_timer = 120
            return

        # Левая кнопка (button == 1)
        if button != 1:
            return  # игнорируем другие кнопки

        # Если есть выбранный юнит
        if self.selected_unit:
            # Попытка атаковать врага
            if unit and unit.player != self.selected_unit.player:
                if self.controller.can_attack_unit(self.selected_unit, unit):
                    self.controller.attack_unit(self.selected_unit, unit)
                    self.message = f"Атака! {type(unit).__name__} получил урон"
                    self.message_timer = 180
                    if not unit.is_alive():
                        self.message = f"{type(unit).__name__} уничтожен!"
                    self.current_player_index = 1 - self.current_player_index
                    self.selected_unit = None
                    self.possible_moves.clear()
                else:
                    self.message = "Невозможно атаковать"
                    self.message_timer = 120
                return

            # Попытка переместиться на пустую клетку
            if not unit:
                if self.controller.can_move_unit(self.selected_unit, x, y):
                    self.controller.move_unit(self.selected_unit, x, y)
                    self.message = f"Перемещение на ({x}, {y})"
                    self.message_timer = 180
                    self.current_player_index = 1 - self.current_player_index
                    self.selected_unit = None
                    self.possible_moves.clear()
                else:
                    self.message = "Невозможно переместиться"
                    self.message_timer = 120
                return

            # Если кликнули на дружественного юнита — просто сменить выбор
            if unit and unit.player == self.selected_unit.player:
                self.selected_unit = unit
                self.possible_moves = self.compute_possible_moves(unit)
                self.message = f"Выбран {type(unit).__name__}"
                self.message_timer = 180
                return

        # Если нет выбранного юнита — пробуем выбрать
        if unit and unit.player == self.players[self.current_player_index] and unit.is_alive():
            self.selected_unit = unit
            self.possible_moves = self.compute_possible_moves(unit)
            self.message = f"Выбран {type(unit).__name__}"
            self.message_timer = 180
        else:
            self.message = "Нельзя выбрать этого юнита"
            self.message_timer = 120

    def check_winner(self) -> Optional[Player]:
        players_alive = {}
        for unit in self.battle_map.units:
            if unit.is_alive():
                players_alive[unit.player] = True
        if len(players_alive) == 1:
            return list(players_alive.keys())[0]
        return None

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos(), event.button)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.current_player_index = 1 - self.current_player_index
                        self.selected_unit = None
                        self.possible_moves.clear()
                        self.message = "Ход пропущен"
                        self.message_timer = 120

            self.screen.fill((0, 0, 0))
            for x in range(MAP_WIDTH):
                for y in range(MAP_HEIGHT):
                    terrain = self.battle_map.get_terrain_at(x, y) or Grass(x=x, y=y)
                    unit = self.battle_map.get_unit_at(x, y)
                    highlight = (x, y) in self.possible_moves
                    self.draw_cell(x, y, terrain, unit, highlight)

            self.draw_info_panel()

            winner = self.check_winner()
            if winner:
                win_text = self.big_font.render(f"Победитель: {winner.name}!", True, (255, 215, 0))
                text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(win_text, text_rect)
                pygame.display.flip()
                pygame.time.wait(3000)
                running = False

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = GameGUI()
    game.run()