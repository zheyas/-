import pygame
import sys
import os
import random
import math
import requests
from typing import Optional, Tuple, Set, List

from strategy.models.player import Player
from strategy.models.unit import Unit
from strategy.models.archer import Archer
from strategy.models.catapult import Catapult
from strategy.models.horseman import Horseman
from strategy.models.swordsman import Swordsman
from strategy.models.warlock import Warlock
from strategy.models.terrain import Terrain, Grass, Water, Bridge
from strategy.models.battle_map import BattleMap
from strategy.controller.game_controller import GameController

# ================== НАСТРОЙКИ ИГРЫ ==================
CELL_SIZE = 64
MAP_WIDTH = 10
MAP_HEIGHT = 10
RIVER_Y = MAP_HEIGHT // 2
RIVER_WIDTH = 2

# Адаптивный размер окна
PANEL_HEIGHT = 380
SCREEN_WIDTH = CELL_SIZE * MAP_WIDTH
SCREEN_HEIGHT = CELL_SIZE * MAP_HEIGHT + PANEL_HEIGHT

# ================== ЦВЕТА ==================
COLORS = {
    'grass': (100, 200, 100),
    'water': (64, 164, 223),
    'bridge': (139, 69, 19),
    'archer': (255, 255, 0),
    'catapult': (128, 128, 128),
    'horseman': (255, 0, 0),
    'swordsman': (0, 255, 0),
    'warlock': (128, 0, 128),
    'dead': (0, 0, 0),
    'selected': (255, 255, 255, 128),
    'move_highlight': (0, 255, 0, 100),
    'attack_highlight': (255, 0, 0, 100),
    'earthquake_range': (255, 165, 0, 150),
    'earthquake_crack': (255, 100, 0, 200),
    'text': (255, 255, 255),
    'panel': (50, 50, 50),
    'border': (200, 200, 200),
    'player1': (0, 100, 255),
    'player2': (255, 50, 50),
    'hp_bg': (64, 64, 64),
    'hp_high': (0, 255, 0),
    'hp_med': (255, 255, 0),
    'hp_low': (255, 0, 0),
    'ability_bg': (30, 30, 30, 200),
    'ability_ready': (255, 255, 0),
    'ability_used': (100, 100, 100),
    'ability_selected': (255, 165, 0),
}

# ССЫЛКИ НА ИЗОБРАЖЕНИЯ
IMAGE_URLS = {
    'archer': 'https://opengameart.org/sites/default/files/archer_0.png',
    'catapult': 'https://opengameart.org/sites/default/files/catapult_0.png',
    'horseman': 'https://opengameart.org/sites/default/files/knight_0.png',
    'swordsman': 'https://opengameart.org/sites/default/files/swordsman_0.png',
    'warlock': 'https://opengameart.org/sites/default/files/wizard_0.png',
    'curse': 'https://cdn-icons-png.flaticon.com/128/484/484582.png',
    'trembling_earth': 'https://cdn-icons-png.flaticon.com/128/1791/1791336.png',
    'grass': 'https://opengameart.org/sites/default/files/grass_0.png',
    'water': 'https://opengameart.org/sites/default/files/water_0.png',
    'bridge': 'https://opengameart.org/sites/default/files/bridge_0.png',
    'dead': 'https://via.placeholder.com/64/000000/000000?text=+'
}


def download_image(url: str, save_path: str) -> bool:
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        if os.path.exists(save_path):
            return True
        print(f"Скачивание {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Ошибка загрузки {url}: {e}")
        return False


def create_placeholder(path: str, color: Tuple[int, int, int], size: int = 64):
    try:
        surf = pygame.Surface((size, size))
        surf.fill(color)
        pygame.image.save(surf, path)
    except:
        pass


def ensure_assets():
    os.makedirs("strategy/assets/units", exist_ok=True)
    os.makedirs("strategy/assets/ground", exist_ok=True)
    os.makedirs("strategy/assets/abilities", exist_ok=True)

    for key, url in IMAGE_URLS.items():
        if key in ('grass', 'water', 'bridge'):
            path = f"strategy/assets/ground/{key}.png"
        elif key in ('curse', 'trembling_earth'):
            path = f"strategy/assets/abilities/{key}.png"
        else:
            path = f"strategy/assets/units/{key}.png"

        success = download_image(url, path)
        if not success:
            if key == 'grass':
                create_placeholder(path, COLORS['grass'])
            elif key == 'water':
                create_placeholder(path, COLORS['water'])
            elif key == 'bridge':
                create_placeholder(path, COLORS['bridge'])
            elif key == 'archer':
                create_placeholder(path, COLORS['archer'])
            elif key == 'catapult':
                create_placeholder(path, COLORS['catapult'])
            elif key == 'horseman':
                create_placeholder(path, COLORS['horseman'])
            elif key == 'swordsman':
                create_placeholder(path, COLORS['swordsman'])
            elif key == 'warlock':
                create_placeholder(path, COLORS['warlock'])
            elif key == 'curse':
                create_placeholder(path, (255, 0, 0), 48)
            elif key == 'trembling_earth':
                create_placeholder(path, (255, 165, 0), 48)


class EarthquakeCrack:
    def __init__(self, x: int, y: int, intensity: float = 1.0):
        self.x = x
        self.y = y
        self.intensity = intensity
        self.lifetime = 30
        self.max_lifetime = 30
        self.redness = 100
        self.points = self._generate_crack()
        self.shake_offset = (0, 0)

    def _generate_crack(self) -> List[Tuple[float, float]]:
        points = []
        x, y = self.x, self.y
        num_points = random.randint(3, 6)

        for i in range(num_points):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(10, 25)
            x += math.cos(angle) * dist
            y += math.sin(angle) * dist
            points.append((x, y))
        return points

    def update(self):
        self.lifetime -= 1
        shake_intensity = 1 + (1 - self.lifetime / self.max_lifetime) * 2
        self.shake_offset = (
            random.randint(-int(shake_intensity), int(shake_intensity)),
            random.randint(-int(shake_intensity), int(shake_intensity))
        )
        progress = 1 - self.lifetime / self.max_lifetime
        self.redness = min(255, int(100 + 155 * progress))

    def draw(self, screen):
        if self.lifetime <= 0:
            return
        alpha = int(255 * self.lifetime / self.max_lifetime)
        color = (255, self.redness, 0, alpha)

        if len(self.points) > 1:
            shifted_points = [(p[0] + self.shake_offset[0], p[1] + self.shake_offset[1])
                              for p in self.points]

            for thickness in [3, 2, 1]:
                line_color = (color[0] // thickness, color[1] // thickness, color[2] // thickness)
                pygame.draw.lines(screen, line_color, False, shifted_points,
                                  max(1, int(3 * self.intensity * (thickness / 3))))


class GameGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Strategy Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.title_font = pygame.font.Font(None, 36)

        ensure_assets()
        self.images = self.load_images()
        self.setup_game()

        self.animation_frame = 0
        self.earthquake_cracks: List[EarthquakeCrack] = []
        self.moving_units: List[dict] = []

        self.selected_unit = None
        self.current_player_index = 0
        self.message = "Выберите юнита"
        self.message_timer = 0
        self.possible_moves: Set[Tuple[int, int]] = set()
        self.ability_mode = False
        self.ability_type = None
        self.earthquake_target: Optional[Tuple[int, int]] = None
        self.show_ability_panel = True

    def load_images(self) -> dict:
        images = {}
        base_path = "strategy/assets"

        for key in ['archer', 'catapult', 'horseman', 'swordsman', 'warlock']:
            path = f"{base_path}/units/{key}.png"
            try:
                if os.path.exists(path):
                    img = pygame.image.load(path)
                    if img.get_alpha() is None:
                        img = img.convert_alpha()
                    images[key] = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
                else:
                    images[key] = None
            except:
                images[key] = None

        for key in ['grass', 'water', 'bridge']:
            path = f"{base_path}/ground/{key}.png"
            try:
                if os.path.exists(path):
                    img = pygame.image.load(path)
                    images[key] = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
                else:
                    images[key] = None
            except:
                images[key] = None

        for key in ['curse', 'trembling_earth']:
            path = f"{base_path}/abilities/{key}.png"
            try:
                if os.path.exists(path):
                    img = pygame.image.load(path)
                    images[key] = pygame.transform.scale(img, (48, 48))
                else:
                    images[key] = None
            except:
                images[key] = None

        return images

    def setup_game(self):
        """Расстановка юнитов на всех доступных клетках"""
        self.players = [
            Player(1, "Синие"),
            Player(2, "Красные")
        ]

        ground = []
        bridge_x = random.randint(2, MAP_WIDTH - 3)

        print(f"Мост на позициях x={bridge_x} и {bridge_x + 1}")

        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                if RIVER_Y - 1 <= y <= RIVER_Y:
                    if bridge_x <= x <= bridge_x + 1:
                        ground.append(Bridge(x=x, y=y))
                    else:
                        ground.append(Water(x=x, y=y))
                else:
                    ground.append(Grass(x=x, y=y))

        # Все клетки, кроме воды
        free_cells = []
        for x in range(MAP_WIDTH):
            for y in range(MAP_HEIGHT):
                terrain = None
                for t in ground:
                    if t.x == x and t.y == y:
                        terrain = t
                        break
                if not isinstance(terrain, Water):
                    free_cells.append((x, y))

        print(f"Всего свободных клеток: {len(free_cells)}")

        left_cells = [c for c in free_cells if c[0] < MAP_WIDTH // 2]
        right_cells = [c for c in free_cells if c[0] >= MAP_WIDTH // 2]

        random.shuffle(left_cells)
        random.shuffle(right_cells)

        units = []
        unit_types = [Archer, Catapult, Horseman, Swordsman, Warlock]

        # Синие юниты
        for i, cls in enumerate(unit_types):
            if i < len(left_cells):
                x, y = left_cells[i]
                units.append(cls(self.players[0], x=x, y=y))
                print(f"Синий {cls.__name__} на ({x},{y})")

        # Красные юниты
        for i, cls in enumerate(unit_types):
            if i < len(right_cells):
                x, y = right_cells[i]
                units.append(cls(self.players[1], x=x, y=y))
                print(f"Красный {cls.__name__} на ({x},{y})")

        self.battle_map = BattleMap(ground=ground, units=units)
        self.controller = GameController(self.battle_map)

    def start_unit_move(self, unit: Unit, from_x: int, from_y: int, to_x: int, to_y: int):
        self.moving_units.append({
            'unit': unit,
            'from_x': from_x * CELL_SIZE,
            'from_y': from_y * CELL_SIZE,
            'to_x': to_x * CELL_SIZE,
            'to_y': to_y * CELL_SIZE,
            'progress': 0.0,
            'speed': 0.1
        })

    def update_moving_units(self):
        for move in self.moving_units[:]:
            move['progress'] += move['speed']
            if move['progress'] >= 1.0:
                move['unit'].x = move['to_x'] // CELL_SIZE
                move['unit'].y = move['to_y'] // CELL_SIZE
                self.moving_units.remove(move)
            else:
                move['unit'].x = (move['from_x'] + (move['to_x'] - move['from_x']) * move['progress']) / CELL_SIZE
                move['unit'].y = (move['from_y'] + (move['to_y'] - move['from_y']) * move['progress']) / CELL_SIZE

    def create_earthquake_effect(self, center_x: int, center_y: int):
        center_px = center_x * CELL_SIZE + CELL_SIZE // 2
        center_py = center_y * CELL_SIZE + CELL_SIZE // 2

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                x = center_x + dx
                y = center_y + dy
                if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                    for _ in range(random.randint(3, 5)):
                        crack_x = x * CELL_SIZE + random.randint(10, CELL_SIZE - 10)
                        crack_y = y * CELL_SIZE + random.randint(10, CELL_SIZE - 10)
                        intensity = random.uniform(0.8, 1.5)
                        self.earthquake_cracks.append(EarthquakeCrack(crack_x, crack_y, intensity))

    def update_earthquake_effects(self):
        for crack in self.earthquake_cracks[:]:
            crack.update()
            if crack.lifetime <= 0:
                self.earthquake_cracks.remove(crack)

    def draw_earthquake_effects(self):
        for crack in self.earthquake_cracks:
            crack.draw(self.screen)

    def draw_grass_tile(self, x: int, y: int, variant: int):
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        if self.images.get('grass'):
            self.screen.blit(self.images['grass'], rect)
        else:
            base_colors = [(58, 138, 58), (53, 133, 53), (64, 128, 64), (45, 122, 45)]
            color = base_colors[variant % 4]
            pygame.draw.rect(self.screen, color, rect)

    def draw_water_tile(self, x: int, y: int):
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        if self.images.get('water'):
            self.screen.blit(self.images['water'], rect)
        else:
            for i in range(CELL_SIZE):
                progress = i / CELL_SIZE
                r = int(74 + (90 - 74) * progress)
                g = int(158 + (239 - 158) * progress)
                b = int(223 + (255 - 223) * progress)
                pygame.draw.line(self.screen, (r, g, b),
                                 (rect.x, rect.y + i), (rect.x + CELL_SIZE, rect.y + i))

        offset = math.sin(self.animation_frame * 0.05) * 4
        for wave in range(2):
            y_pos = rect.y + 15 + wave * 25 + offset
            points = []
            for step in range(0, CELL_SIZE + 1, 8):
                x_pos = rect.x + step
                y_offset = math.sin(step * 0.1 + self.animation_frame * 0.1) * 3
                points.append((x_pos, y_pos + y_offset))
            if len(points) > 1:
                pygame.draw.lines(self.screen, (255, 255, 255, 80), False, points, 1)

    def draw_bridge_tile(self, x: int, y: int):
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        self.draw_water_tile(x, y)

        if self.images.get('bridge'):
            bridge_img = self.images['bridge'].copy()
            bridge_img.set_alpha(200)
            self.screen.blit(bridge_img, rect)
        else:
            s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            for i in range(4):
                y_pos = i * 16
                pygame.draw.rect(s, (139, 69, 19, 200), (0, y_pos, CELL_SIZE, 8))
                pygame.draw.line(s, (101, 67, 33, 150), (0, y_pos + 2), (CELL_SIZE, y_pos + 2), 2)
            self.screen.blit(s, rect)

    def draw_unit(self, unit, rect):
        team_color = COLORS['player1'] if unit.player.id == self.players[0].id else COLORS['player2']

        shadow_rect = rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        s.fill((0, 0, 0, 80))
        self.screen.blit(s, shadow_rect)

        unit_img = None
        if isinstance(unit, Archer):
            unit_img = self.images.get('archer')
        elif isinstance(unit, Catapult):
            unit_img = self.images.get('catapult')
        elif isinstance(unit, Horseman):
            unit_img = self.images.get('horseman')
        elif isinstance(unit, Swordsman):
            unit_img = self.images.get('swordsman')
        elif isinstance(unit, Warlock):
            unit_img = self.images.get('warlock')

        if unit_img and unit.is_alive():
            self.screen.blit(unit_img, rect)
        elif not unit.is_alive():
            s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            s.fill((30, 30, 30, 200))
            self.screen.blit(s, rect)
            if self.images.get('dead'):
                self.screen.blit(self.images['dead'], rect)
        else:
            color_map = {
                Archer: COLORS['archer'],
                Catapult: COLORS['catapult'],
                Horseman: COLORS['horseman'],
                Swordsman: COLORS['swordsman'],
                Warlock: COLORS['warlock']
            }
            color = color_map.get(type(unit), COLORS['swordsman'])
            pygame.draw.rect(self.screen, color, rect)

        pygame.draw.rect(self.screen, team_color, rect, 3)

    def draw_hp_bar(self, unit, rect):
        bar_width = CELL_SIZE - 4
        bar_height = 6
        bar_x = rect.x + 2
        bar_y = rect.y - bar_height - 4

        if bar_y < 0:
            bar_y = rect.y + 2

        ratio = unit.health / unit.max_health

        if ratio > 0.6:
            color = COLORS['hp_high']
        elif ratio > 0.3:
            color = COLORS['hp_med']
        else:
            color = COLORS['hp_low']

        pygame.draw.rect(self.screen, COLORS['hp_bg'],
                         (bar_x, bar_y, bar_width, bar_height), border_radius=2)

        if ratio > 0:
            fill_width = int(bar_width * ratio)
            pygame.draw.rect(self.screen, color,
                             (bar_x, bar_y, fill_width, bar_height), border_radius=2)

    def draw_ability_panel(self, unit):
        if not isinstance(unit, Warlock) or not unit.is_alive() or not self.show_ability_panel:
            return

        panel_x = SCREEN_WIDTH // 2 - 250
        panel_y = SCREEN_HEIGHT - PANEL_HEIGHT + 10
        panel_width = 500
        panel_height = 120

        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        s = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        s.fill((26, 26, 46, 230))
        self.screen.blit(s, panel_rect)
        pygame.draw.rect(self.screen, COLORS['border'], panel_rect, 3)

        title = self.font.render("⚡ СПОСОБНОСТИ КОЛДУНА", True, (255, 215, 0))
        self.screen.blit(title, (panel_x + 20, panel_y + 10))

        icon_size = 48
        icon_y = panel_y + 40

        icon_x = panel_x + 80
        curse_icon = self.images.get('curse')
        if curse_icon:
            icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)

            if self.ability_type == 'curse':
                border_color = COLORS['ability_selected']
            elif unit.can_use_curse():
                border_color = COLORS['ability_ready']
            else:
                border_color = COLORS['ability_used']

            pygame.draw.rect(self.screen, (42, 42, 62), icon_rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, icon_rect, 3, border_radius=8)
            self.screen.blit(curse_icon, icon_rect)

            key_bg = pygame.Rect(icon_x + 5, icon_y + 5, 20, 20)
            pygame.draw.rect(self.screen, COLORS['border'], key_bg, border_radius=3)
            key_text = self.small_font.render("1", True, (255, 255, 255))
            self.screen.blit(key_text, (key_bg.x + 6, key_bg.y + 2))

            name = self.small_font.render("Проклятие", True, border_color)
            self.screen.blit(name, (icon_x, icon_y + icon_size + 5))

        icon_x = panel_x + 280
        earth_icon = self.images.get('trembling_earth')
        if earth_icon:
            icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)

            if self.ability_type == 'earthquake':
                border_color = COLORS['ability_selected']
            elif unit.can_use_earthquake():
                border_color = COLORS['ability_ready']
            else:
                border_color = COLORS['ability_used']

            pygame.draw.rect(self.screen, (42, 42, 62), icon_rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, icon_rect, 3, border_radius=8)
            self.screen.blit(earth_icon, icon_rect)

            key_bg = pygame.Rect(icon_x + 5, icon_y + 5, 20, 20)
            pygame.draw.rect(self.screen, COLORS['border'], key_bg, border_radius=3)
            key_text = self.small_font.render("2", True, (255, 255, 255))
            self.screen.blit(key_text, (key_bg.x + 6, key_bg.y + 2))

            name = self.small_font.render("Дрожь земли", True, border_color)
            self.screen.blit(name, (icon_x, icon_y + icon_size + 5))

        if self.ability_type:
            mode_text = f"Режим: {'Проклятие' if self.ability_type == 'curse' else 'Дрожь земли'} (ПКМ - отмена)"
            text = self.small_font.render(mode_text, True, (255, 215, 0))
            self.screen.blit(text, (panel_x + 120, panel_y + 80))

    def draw_cell(self, x: int, y: int, terrain, unit: Optional = None, highlight: bool = False):
        if isinstance(terrain, Grass):
            self.draw_grass_tile(x, y, x + y)
        elif isinstance(terrain, Water):
            self.draw_water_tile(x, y)
        elif isinstance(terrain, Bridge):
            self.draw_bridge_tile(x, y)

        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

        if highlight:
            s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            s.set_alpha(100)
            s.fill(COLORS['move_highlight'][:3])
            self.screen.blit(s, rect)

        if unit:
            self.draw_unit(unit, rect)
            if unit.is_alive():
                self.draw_hp_bar(unit, rect)

        pygame.draw.rect(self.screen, COLORS['border'], rect, 1)

        if self.selected_unit == unit:
            s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            s.set_alpha(128)
            s.fill(COLORS['selected'])
            self.screen.blit(s, rect)

    def draw_earthquake_range(self, center_x: int, center_y: int):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                x, y = center_x + dx, center_y + dy
                if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    s.set_alpha(150)
                    s.fill(COLORS['earthquake_range'][:3])
                    self.screen.blit(s, rect)

                    pulse = abs(math.sin(self.animation_frame * 0.1)) * 3
                    pygame.draw.rect(self.screen, (255, 100, 0), rect, int(pulse) + 1)

    def draw_turn_indicator(self):
        current_player = self.players[self.current_player_index]
        player_color = COLORS['player1'] if current_player.id == self.players[0].id else COLORS['player2']

        text = f"⚔ ХОД: {current_player.name} ⚔"
        pulse = abs(math.sin(self.animation_frame * 0.03)) * 0.5 + 0.5

        text_surf = self.title_font.render(text, True, player_color)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))

        bg_rect = text_rect.inflate(40, 10)
        s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 200))
        self.screen.blit(s, bg_rect)
        pygame.draw.rect(self.screen, player_color, bg_rect, 2)

        self.screen.blit(text_surf, text_rect)

    def remove_dead_units(self):
        self.battle_map._units = [u for u in self.battle_map.units if u.is_alive()]

    def update_warlock_curses(self):
        for unit in self.battle_map.units:
            if isinstance(unit, Warlock) and unit.is_alive():
                unit.update_curse()

    def reset_warlock_abilities(self):
        for unit in self.battle_map.units:
            if isinstance(unit, Warlock) and unit.is_alive():
                unit.reset_abilities_for_new_turn()

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

    def get_cell_from_pos(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        x, y = pos
        if x < 0 or x >= SCREEN_WIDTH or y < 0 or y >= SCREEN_HEIGHT - 100:
            return None
        return (x // CELL_SIZE, y // CELL_SIZE)

    def switch_turn(self):
        self.remove_dead_units()
        self.update_warlock_curses()
        self.current_player_index = 1 - self.current_player_index
        self.reset_warlock_abilities()
        self.selected_unit = None
        self.possible_moves.clear()
        self.ability_mode = False
        self.ability_type = None
        self.earthquake_target = None
        self.show_ability_panel = True
        self.message = f"Ход {self.players[self.current_player_index].name}"
        self.message_timer = 180

    def handle_ability(self, unit: Warlock, ability: str):
        if ability == 'curse':
            if unit.can_use_curse():
                self.ability_mode = True
                self.ability_type = 'curse'
                self.show_ability_panel = False
                self.message = "Выберите цель для проклятия"
                self.message_timer = 180
            else:
                self.message = "❌ Проклятие уже использовано"
                self.message_timer = 120
        elif ability == 'earthquake':
            if unit.can_use_earthquake():
                self.ability_mode = True
                self.ability_type = 'earthquake'
                self.show_ability_panel = False
                self.message = "Выберите центр землетрясения"
                self.message_timer = 180
            else:
                self.message = "❌ Дрожь земли уже использована"
                self.message_timer = 120

    def handle_click(self, pos: Tuple[int, int], button: int):
        cell = self.get_cell_from_pos(pos)
        if not cell:
            return

        x, y = cell
        unit = self.battle_map.get_unit_at(x, y)

        # Отладка
        print(f"Клик: button={button}, клетка ({x},{y}), юнит={unit}")

        # Правая кнопка - отмена
        if button == 3:
            self.selected_unit = None
            self.possible_moves.clear()
            self.ability_mode = False
            self.ability_type = None
            self.earthquake_target = None
            self.show_ability_panel = True
            self.message = "Выбор отменён"
            self.message_timer = 120
            return

        # Левая кнопка
        if button != 1:
            return

        # Режим способности
        if self.ability_mode and isinstance(self.selected_unit, Warlock):
            if self.ability_type == 'curse':
                if unit and unit.player.id != self.selected_unit.player.id and unit.is_alive():
                    if self.selected_unit.cast_curse(unit):
                        self.create_earthquake_effect(x, y)
                        self.message = f"👻 Проклятие наложено на {type(unit).__name__}"
                        self.message_timer = 180
                        self.switch_turn()
                    else:
                        self.message = "Не удалось наложить проклятие"
                        self.message_timer = 120
                else:
                    self.message = "Выберите вражеского юнита для проклятия"
                    self.message_timer = 120
                self.ability_mode = False
                self.ability_type = None
                self.earthquake_target = None
                self.show_ability_panel = True
                return

            elif self.ability_type == 'earthquake':
                damaged = self.selected_unit.cast_earthquake(self.battle_map, x, y)
                self.create_earthquake_effect(x, y)
                self.message = f"🌋 Дрожь земли поразила {len(damaged)} юнитов"
                self.message_timer = 180
                self.switch_turn()
                self.ability_mode = False
                self.ability_type = None
                self.earthquake_target = None
                self.show_ability_panel = True
                return

        # Обычный режим
        if self.selected_unit:
            # Атака врага
            if unit and unit.player.id != self.selected_unit.player.id and unit.is_alive():
                if self.controller.can_attack_unit(self.selected_unit, unit):
                    self.controller.attack_unit(self.selected_unit, unit)
                    self.create_earthquake_effect(x, y)
                    self.message = f"⚔️ Атака! {type(unit).__name__} получил урон"
                    self.message_timer = 180
                    if not unit.is_alive():
                        self.message = f"💀 {type(unit).__name__} уничтожен!"
                    self.switch_turn()
                else:
                    self.message = "Невозможно атаковать"
                    self.message_timer = 120
                return

            # Перемещение
            if not unit:
                # ОТЛАДКА: подробная информация о попытке перемещения
                print(f"\n--- ПОПЫТКА ПЕРЕМЕЩЕНИЯ ---")
                print(f"Юнит: {type(self.selected_unit).__name__}")
                print(f"Откуда: ({self.selected_unit.x}, {self.selected_unit.y})")
                print(f"Куда: ({x}, {y})")
                print(f"Радиус движения: {self.selected_unit.move_range}")
                print(f"Расстояние: {abs(self.selected_unit.x - x) + abs(self.selected_unit.y - y)}")

                # Получаем тип местности в целевой клетке
                target_terrain = self.battle_map.get_terrain_at(x, y)
                terrain_type = type(target_terrain).__name__ if target_terrain else "None"
                print(f"Тип местности: {terrain_type}")

                # Проверяем, есть ли там другой юнит
                target_unit = self.battle_map.get_unit_at(x, y)
                if target_unit:
                    print(f"Клетка занята юнитом: {type(target_unit).__name__}")

                if self.controller.can_move_unit(self.selected_unit, x, y):
                    print(f"✅ РАЗРЕШЕНО! Перемещаем...")
                    old_x, old_y = self.selected_unit.x, self.selected_unit.y
                    self.controller.move_unit(self.selected_unit, x, y)
                    self.start_unit_move(self.selected_unit, old_x, old_y, x, y)
                    self.message = f"🏃 Перемещение на ({x}, {y})"
                    self.message_timer = 180
                    self.switch_turn()
                else:
                    print(f"❌ ЗАПРЕЩЕНО!")
                    self.message = "Невозможно переместиться"
                    self.message_timer = 120
                print(f"--- КОНЕЦ ПОПЫТКИ ---\n")
                return

            # Смена выбора
            if unit and unit.player.id == self.selected_unit.player.id and unit.is_alive():
                self.selected_unit = unit
                self.possible_moves = self.compute_possible_moves(unit)
                self.message = f"Выбран {type(unit).__name__}"
                self.message_timer = 180
                return

        # Выбор нового юнита
        if unit and unit.is_alive():
            if unit.player.id == self.players[self.current_player_index].id:
                self.selected_unit = unit
                self.possible_moves = self.compute_possible_moves(unit)
                self.ability_mode = False
                self.ability_type = None
                self.show_ability_panel = True
                self.message = f"Выбран {type(unit).__name__}"
                self.message_timer = 180
                print(f"✓ Выбран {type(unit).__name__} на ({x},{y})")
            else:
                self.message = f"Сейчас ход {self.players[self.current_player_index].name}"
                self.message_timer = 120
        else:
            if unit and not unit.is_alive():
                self.message = "Юнит мёртв"
            else:
                self.message = "Пустая клетка"
            self.message_timer = 120

    def handle_key(self, key: int):
        if key == pygame.K_SPACE:
            self.switch_turn()
            self.message = "⏭️ Ход пропущен"
            self.message_timer = 120
        elif key == pygame.K_1 and isinstance(self.selected_unit, Warlock):
            self.handle_ability(self.selected_unit, 'curse')
        elif key == pygame.K_2 and isinstance(self.selected_unit, Warlock):
            self.handle_ability(self.selected_unit, 'earthquake')
        elif key == pygame.K_ESCAPE:
            self.selected_unit = None
            self.possible_moves.clear()
            self.ability_mode = False
            self.ability_type = None
            self.earthquake_target = None
            self.show_ability_panel = True
            self.message = "Выбор отменён"
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
            self.animation_frame += 1
            self.update_earthquake_effects()
            self.update_moving_units()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    global SCREEN_WIDTH, SCREEN_HEIGHT
                    SCREEN_WIDTH, SCREEN_HEIGHT = event.size
                    self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos(), event.button)
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)
                elif event.type == pygame.MOUSEMOTION:
                    if self.ability_mode and self.ability_type == 'earthquake':
                        cell = self.get_cell_from_pos(pygame.mouse.get_pos())
                        if cell:
                            self.earthquake_target = cell

            self.screen.fill((20, 20, 30))

            for x in range(MAP_WIDTH):
                for y in range(MAP_HEIGHT):
                    terrain = self.battle_map.get_terrain_at(x, y) or Grass(x=x, y=y)
                    unit = self.battle_map.get_unit_at(x, y)
                    highlight = (x, y) in self.possible_moves
                    self.draw_cell(x, y, terrain, unit, highlight)

            self.draw_earthquake_effects()

            if self.earthquake_target:
                self.draw_earthquake_range(self.earthquake_target[0], self.earthquake_target[1])

            if self.selected_unit and isinstance(self.selected_unit, Warlock):
                self.draw_ability_panel(self.selected_unit)

            self.draw_turn_indicator()

            if self.message_timer > 0:
                msg_bg = pygame.Rect(SCREEN_WIDTH - 300, 10, 280, 30)
                s = pygame.Surface((280, 30), pygame.SRCALPHA)
                s.fill((0, 0, 0, 200))
                self.screen.blit(s, msg_bg)
                pygame.draw.rect(self.screen, COLORS['border'], msg_bg, 2)
                msg_text = self.small_font.render(self.message, True, COLORS['text'])
                self.screen.blit(msg_text, (msg_bg.x + 10, msg_bg.y + 5))
                self.message_timer -= 1

            winner = self.check_winner()
            if winner:
                win_text = self.title_font.render(f"🏆 ПОБЕДИТЕЛЬ: {winner.name}!", True, (255, 215, 0))
                text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                s.fill((0, 0, 0, 200))
                self.screen.blit(s, (0, 0))
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