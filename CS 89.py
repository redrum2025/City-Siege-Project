import pygame
import random
import sys
import os
import math

# Initialize Pygame
print("Initializing Pygame...")
pygame.init()
print("Pygame initialized.")

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 200, 0)
BROWN = (139, 69, 19)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
PINK = (255, 105, 180)
MAGENTA = (255, 0, 255)
GOLDEN = (218, 165, 32)
DARK_GREEN = (34, 139, 34)

# Set up display
print("Setting up display...")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("City Siege")
clock = pygame.time.Clock()
print("Display set up.")

# Fonts
print("Loading fonts...")
title_font = pygame.font.SysFont("Arial", 60, bold=True)
menu_font = pygame.font.SysFont("Arial", 30)
bubble_font = pygame.font.SysFont("Comic Sans MS", 20, bold=True)
print("Fonts loaded.")

# Game states
MENU, LEVEL_SELECT, GAME, LEADERBOARD, GAME_OVER, FINAL_BOSS, CREDITS, CONTROLS = "menu", "level_select", "game", "leaderboard", "game_over", "final_boss", "credits", "controls"
state = MENU

# Player variables
player_x = WIDTH // 2
player_y = 40
player_hp = 5
missiles_left = 20
bombs_left = 0
missile_speed = 5
bomb_speed = 7
player_speed = 5
score = 0
level = 1
MAX_LEVELS = 20
firing_cooldown = 0
bomb_cooldown = 0
enemy_spawn_timer = 0
bomb_package_timer = 60
boss_active = False
boss = None
final_boss_form = 0
power_up_effects = {"missiles": 0, "health": 0}
title_scroll_y = HEIGHT
title_timer = 0
name_input = ""
baxter_tail_angle = 0
text_particles = []
credits_scroll_y = HEIGHT
fireworks = []
beat_final_boss = False
player_flash_timer = 0
player_color_index = 0
player_colors = [RED, BLUE, GREEN, YELLOW, PURPLE]

# Level themes
level_themes = {
    1: {"name": "Sahara Siege", "ground_color": (237, 201, 175), "building_color": (194, 178, 128), "effect_color": (255, 230, 153), "env_effect": "wind"},
    2: {"name": "Coastal Clash", "ground_color": (255, 215, 0), "building_color": (173, 216, 230), "effect_color": (0, 191, 255), "env_effect": "rain"},
    3: {"name": "Frostbite Frenzy", "ground_color": (245, 245, 220), "building_color": (135, 206, 235), "effect_color": (255, 250, 250), "env_effect": "snow"},
    4: {"name": "Volcano Vanguard", "ground_color": (139, 0, 0), "building_color": (105, 105, 105), "effect_color": (255, 69, 0), "env_effect": "wind"},
    5: {"name": "Jungle Joust", "ground_color": (34, 139, 34), "building_color": (139, 69, 19), "effect_color": (0, 100, 0), "env_effect": "rain"},
}
for i in range(6, MAX_LEVELS + 1):
    level_themes[i] = level_themes[i % 5 + 1]

# Menu button class
class MenuButton:
    def __init__(self, text, x, y, key, target_state):
        self.original_text = text
        self.text = menu_font.render(text, True, WHITE)
        self.rect = self.text.get_rect(center=(x, y))
        self.key = key
        self.target_state = target_state
        self.hovered = False

    def draw(self):
        color = YELLOW if self.hovered else WHITE
        text = menu_font.render(self.original_text, True, color)
        self.rect = text.get_rect(center=self.rect.center)
        screen.blit(text, self.rect)
        if self.hovered:
            pygame.draw.rect(screen, BLUE, self.rect.inflate(20, 10), 2)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def check_click(self, pos):
        return self.rect.collidepoint(pos)

# Environmental particle class
class EnvParticle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.type = level_themes[level]["env_effect"] if state != FINAL_BOSS else "wind"
        self.dx = random.uniform(-1, 1) if self.type == "wind" else 0
        self.dy = random.uniform(1, 3) if self.type in ["rain", "snow"] else 0
        self.size = random.randint(2, 4) if self.type == "snow" else 2
        self.color = BLUE if self.type == "rain" else WHITE if self.type == "snow" else (255, 230, 153)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        if self.x < 0 or self.x > WIDTH or self.y > HEIGHT:
            self.x = random.randint(0, WIDTH)
            self.y = 0 if self.type in ["rain", "snow"] else random.randint(0, HEIGHT)

    def draw(self):
        if self.type == "rain":
            pygame.draw.line(screen, self.color, (self.x, self.y), (self.x, self.y + 5), 2)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

# Text particle class
class TextParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = random.uniform(-2, 2)
        self.dy = random.uniform(-2, 2)
        self.life = random.randint(20, 40)
        self.size = random.randint(2, 5)
        self.color = random.choice([RED, ORANGE, YELLOW])

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1

    def draw(self):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

# Bomb Package class
class BombPackage:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = -40
        self.speed = 2
        self.parachute_color = WHITE
        self.package_color = ORANGE
        self.sway_angle = 0

    def update(self):
        self.y += self.speed
        self.sway_angle += 0.1
        self.x += math.sin(self.sway_angle) * 2
        return self.y < HEIGHT + 20

    def draw(self):
        parachute_top = (self.x, self.y)
        parachute_left = (self.x - 15, self.y + 20)
        parachute_right = (self.x + 15, self.y + 20)
        pygame.draw.polygon(screen, self.parachute_color, [parachute_top, parachute_left, parachute_right])
        package_center_x = self.x
        package_center_y = self.y + 40
        pygame.draw.line(screen, self.parachute_color, (self.x - 10, self.y + 20), (package_center_x - 5, package_center_y), 1)
        pygame.draw.line(screen, self.parachute_color, (self.x + 10, self.y + 20), (package_center_x + 5, package_center_y), 1)
        package_rect = pygame.Rect(package_center_x - 10, package_center_y - 10, 20, 20)
        pygame.draw.rect(screen, self.package_color, package_rect)
        pygame.draw.circle(screen, RED, (int(package_center_x), int(package_center_y)), 3)

# Bomb class
class Bomb:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 5, y, 10, 15)
        self.speed = bomb_speed
        self.color = ORANGE
        self.damage = 10

    def move(self, trails):
        self.rect.y += self.speed
        if len(trails) < 100:
            trails.append(MissileTrail(self.rect.centerx, self.rect.top, RED))

    def draw(self):
        pygame.draw.ellipse(screen, self.color, self.rect)
        pygame.draw.circle(screen, RED, (self.rect.centerx, self.rect.bottom), 5)

# Boss types
boss_types = [
    {"name": "Scorpion", "color": (255, 140, 0)},
    {"name": "Shark", "color": (70, 130, 180)},
    {"name": "Bear", "color": (139, 69, 19)},
    {"name": "Dragon", "color": (255, 215, 0)},
    {"name": "Tiger", "color": (255, 165, 0)}
]

# Power-up class
class PowerUp:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 10, y - 10, 20, 20)
        self.type = random.choice(["missiles", "health"])
        self.timer = 300
        self.color = {"missiles": CYAN, "health": GREEN}[self.type]

    def update(self):
        self.timer -= 1
        return self.timer > 0

    def draw(self):
        if self.type == "missiles":
            pygame.draw.rect(screen, self.color, self.rect, 2)
            pygame.draw.line(screen, self.color, self.rect.topleft, self.rect.bottomright, 2)
            pygame.draw.line(screen, self.color, self.rect.topright, self.rect.bottomleft, 2)
        elif self.type == "health":
            pygame.draw.circle(screen, self.color, self.rect.center, 10)
            pygame.draw.line(screen, WHITE, (self.rect.centerx - 5, self.rect.centery), 
                            (self.rect.centerx + 5, self.rect.centery), 2)
            pygame.draw.line(screen, WHITE, (self.rect.centerx, self.rect.centery - 5), 
                            (self.rect.centerx, self.rect.centery + 5), 2)

# UFO class
class MenuUFO:
    def __init__(self):
        self.x = random.randint(0, WIDTH - 40)
        self.y = random.randint(0, HEIGHT - 40)
        self.dx = random.choice([-1, 1]) * random.uniform(1, 2)
        self.dy = random.choice([-1, 1]) * random.uniform(1, 2)
        self.colors = [RED, BLUE, GREEN, YELLOW, PURPLE]
        self.color_index = random.randint(0, len(self.colors) - 1)
        self.flash_timer = 0
        self.flash_interval = 30

    def move(self):
        self.x += self.dx
        self.y += self.dy
        if self.x < 0 or self.x > WIDTH - 40:
            self.dx = -self.dx
        if self.y < 0 or self.y > HEIGHT - 40:
            self.dy = -self.dy
        self.flash_timer += 1
        if self.flash_timer >= self.flash_interval:
            self.color_index = (self.color_index + 1) % len(self.colors)
            self.flash_timer = 0

    def draw(self):
        color = self.colors[self.color_index]
        pygame.draw.ellipse(screen, color, (self.x, self.y, 40, 20))
        pygame.draw.circle(screen, WHITE, (int(self.x + 20), int(self.y + 5)), 12)
        pygame.draw.circle(screen, GREEN, (int(self.x + 10), int(self.y + 10)), 3)
        pygame.draw.circle(screen, GREEN, (int(self.x + 30), int(self.y + 10)), 3)

# Particle classes
class StarParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(1, 3)
        self.color_options = [WHITE, YELLOW, BLUE]  # White, Yellow, Blue twinkling colors
        self.color_index = random.randint(0, len(self.color_options) - 1)  # Start with a random color
        self.twinkle_timer = 0
        self.twinkle_interval = random.randint(10, 20)  # Frames between color changes

    def update(self):
        self.twinkle_timer += 1
        if self.twinkle_timer >= self.twinkle_interval:
            self.color_index = (self.color_index + 1) % len(self.color_options)  # Cycle through colors
            self.twinkle_timer = 0
            self.twinkle_interval = random.randint(10, 20)  # Randomize next interval for variety

    def draw(self):
        pygame.draw.circle(screen, self.color_options[self.color_index], (int(self.x), int(self.y)), self.size)

class ThrusterParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(2, 4)
        self.life = random.randint(10, 20)
        self.dx = random.uniform(-0.2, 0.2)
        self.dy = random.uniform(1, 2)
        self.color = BLUE

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1

    def draw(self):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

class MissileTrail:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.size = random.randint(1, 3)
        self.life = random.randint(5, 10)
        self.color = color

    def update(self):
        self.life -= 1

    def draw(self):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

class ExplosionParticle:
    def __init__(self, x, y, is_enemy=False, is_bomb=False):
        self.x = x
        self.y = y
        self.size = random.randint(2, 8 if is_bomb else 6)
        self.life = random.randint(15, 35 if is_bomb else 25)
        self.dx = random.uniform(-5 if is_bomb else -3, 5 if is_bomb else 3)
        self.dy = random.uniform(-5 if is_bomb else -3, 5 if is_bomb else 3)
        self.color = PURPLE if is_enemy else RED if is_bomb else random.choice([RED, ORANGE, YELLOW])

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1

    def draw(self):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

class FireworkParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(2, 6)
        self.life = random.randint(20, 40)
        self.dx = random.uniform(-3, 3)
        self.dy = random.uniform(-3, 3)
        self.color = random.choice([RED, GREEN, BLUE, YELLOW, PURPLE, CYAN, MAGENTA])

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1

    def draw(self):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

class Shockwave:
    def __init__(self, x, y, is_bomb=False):
        self.x = x
        self.y = y
        self.radius = 5
        self.life = 15 if is_bomb else 10
        self.color = RED if is_bomb else (level_themes[level]["effect_color"] if state != FINAL_BOSS else PURPLE)

    def update(self):
        self.radius += 4 if self.color == RED else 2
        self.life -= 1

    def draw(self):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.radius), 1)

# Missile class for game
class Missile:
    def __init__(self, x, y, angle=0):
        self.rect = pygame.Rect(x - 2, y, 4, 10)
        self.speed = missile_speed
        self.color = RED
        self.is_powered = power_up_effects["missiles"] > 0
        self.dx = angle if self.is_powered else 0

    def move(self, trails):
        self.rect.y += self.speed
        self.rect.x += self.dx
        if len(trails) < 100:
            trails.append(MissileTrail(self.rect.centerx, self.rect.top, ORANGE if not self.is_powered else CYAN))

    def draw(self):
        if self.is_powered:
            pygame.draw.polygon(screen, self.color, [(self.rect.centerx, self.rect.top), 
                                                     (self.rect.left, self.rect.bottom), 
                                                     (self.rect.right, self.rect.bottom)])
            pygame.draw.circle(screen, CYAN, (self.rect.centerx, self.rect.bottom), 4)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.circle(screen, ORANGE, (self.rect.centerx, self.rect.bottom), 3)

# Projectile classes
class TurretProjectile:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 2, y, 4, 8)
        self.speed = -4
        self.color = YELLOW

    def move(self, trails):
        self.rect.y += self.speed
        if len(trails) < 100:
            trails.append(MissileTrail(self.rect.centerx, self.rect.bottom, WHITE))

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.circle(screen, WHITE, (self.rect.centerx, self.rect.top), 2)

class EnemyProjectile:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 2, y, 4, 8)
        self.speed = -3
        self.color = CYAN

    def move(self, trails):
        self.rect.y += self.speed
        if len(trails) < 100:
            trails.append(MissileTrail(self.rect.centerx, self.rect.bottom, WHITE))

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.circle(screen, WHITE, (self.rect.centerx, self.rect.top), 2)

# Building class
class Building:
    def __init__(self, x, y, type_):
        self.type = type_
        self.firing_cooldown = random.randint(60, 120)
        if type_ == "tower":
            self.rect = pygame.Rect(x, y, 30, 100)
            self.hp = 3
        elif type_ == "house":
            self.rect = pygame.Rect(x, y, 40, 60)
            self.hp = 1
        elif type_ == "factory":
            self.rect = pygame.Rect(x, y, 50, 80)
            self.hp = 2
        elif type_ == "turret":
            self.rect = pygame.Rect(x, y, 35, 70)
            self.hp = 2
        self.color = MAGENTA if self.type == "turret" else level_themes[level]["building_color"]
        self.flash_timer = 0
        self.flash_interval = 60
        self.flash_state = True

    def draw(self):
        if self.type == "turret":
            self.flash_timer += 1
            if self.flash_timer >= self.flash_interval:
                self.flash_state = not self.flash_state
                self.flash_timer = 0
            draw_color = self.color if self.flash_state else GRAY
        else:
            draw_color = self.color
        pygame.draw.rect(screen, draw_color, self.rect)
        window_color = (255, 255, 153) if level % 2 == 0 else (173, 216, 230)
        for y in range(self.rect.top + 5, self.rect.bottom - 5, 15):
            for x in range(self.rect.left + 5, self.rect.right - 5, 10):
                pygame.draw.rect(screen, window_color, (x, y, 6, 10))
        for i in range(self.hp):
            pygame.draw.rect(screen, GREEN, (self.rect.x + i * 5, self.rect.y - 5, 4, 2))

    def fire(self, projectiles):
        if self.type == "turret" and self.firing_cooldown <= 0:
            if len(projectiles) < 50:
                projectiles.append(TurretProjectile(self.rect.centerx, self.rect.top))
            self.firing_cooldown = random.randint(60, 120)
        elif self.type == "turret":
            self.firing_cooldown -= 1

# Enemy ship class
class EnemyShip:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 20)
        self.hp = 1
        self.speed = random.choice([-2, 2])
        self.firing_cooldown = random.randint(60, 120)

    def move(self, projectiles):
        self.rect.x += self.speed
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.speed = -self.speed
        if self.firing_cooldown <= 0 and len(projectiles) < 50:
            projectiles.append(EnemyProjectile(self.rect.centerx, self.rect.top))
            self.firing_cooldown = random.randint(60, 120)
        else:
            self.firing_cooldown -= 1

    def draw(self):
        pygame.draw.rect(screen, (85, 107, 47), self.rect)
        pygame.draw.ellipse(screen, GRAY, (self.rect.centerx - 15, self.rect.top - 15, 30, 10))
        window_x = self.rect.left + 5 if self.speed > 0 else self.rect.right - 15
        pygame.draw.rect(screen, (0, 0, 100), (window_x, self.rect.top + 2, 10, 6))
        tail_x = self.rect.left - 15 if self.speed < 0 else self.rect.right + 15
        pygame.draw.line(screen, (85, 107, 47), (self.rect.left if self.speed < 0 else self.rect.right, self.rect.centery), 
                        (tail_x, self.rect.centery), 3)
        pygame.draw.ellipse(screen, GRAY, (tail_x - 2, self.rect.centery - 5, 4, 10))
        pygame.draw.line(screen, GRAY, (self.rect.left + 5, self.rect.bottom + 5), (self.rect.right - 5, self.rect.bottom + 5), 2)
        pygame.draw.line(screen, GRAY, (self.rect.left + 5, self.rect.bottom), (self.rect.left + 5, self.rect.bottom + 5), 2)
        pygame.draw.line(screen, GRAY, (self.rect.right - 5, self.rect.bottom), (self.rect.right - 5, self.rect.bottom + 5), 2)

# Boss class (for GAME state)
class Boss:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 50, 400, 100, 50)
        self.max_hp = 10 + level * 3
        self.hp = self.max_hp
        self.speed = 2 + level * 0.2
        self.firing_cooldown = max(10, 30 - level)
        self.type = boss_types[(level - 1) % len(boss_types)]
        self.color = self.type["color"]
        self.missile_color = PINK

    def move(self, projectiles):
        self.rect.x += self.speed
        if self.rect.left < 50 or self.rect.right > WIDTH - 50:
            self.speed = -self.speed
        if self.firing_cooldown <= 0 and len(projectiles) < 50:
            projectiles.append(BossProjectile(self.rect.centerx, self.rect.top))
            self.firing_cooldown = max(10, 30 - level)
        else:
            self.firing_cooldown -= 1

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)

# Final Boss class (dragon design for all forms)
class FinalBoss:
    def __init__(self, form):
        self.rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 - 70, 150, 100)
        self.form = form
        self.max_hp = 50 + form * 25
        self.hp = self.max_hp
        self.speed = 3 + form
        self.firing_cooldown = 20 - form * 2
        self.color = {1: GREEN, 2: CYAN, 3: PURPLE}[form]
        self.y_speed = 1
        self.fire_length = 0
        print(f"FinalBoss initialized: form={self.form}, color={self.color}")

    def move(self, projectiles):
        self.rect.x += self.speed
        self.rect.y += self.y_speed
        if self.rect.left < 50 or self.rect.right > WIDTH - 50:
            self.speed = -self.speed
        if self.rect.top < 50 or self.rect.bottom > HEIGHT - 50:
            self.y_speed = -self.y_speed
        if self.firing_cooldown <= 0 and len(projectiles) < 50:
            projectiles.append(BossProjectile(self.rect.x + 160, self.rect.y + 25))
            self.firing_cooldown = 20 - self.form * 2
            self.fire_length = 50
        else:
            self.firing_cooldown -= 1
            self.fire_length = max(0, self.fire_length - 1)

    def draw(self):
        print(f"Drawing FinalBoss: form={self.form}, color={self.color}")
        pygame.draw.ellipse(screen, self.color, (self.rect.x, self.rect.y + 20, 150, 60))
        pygame.draw.polygon(screen, self.color, [(self.rect.x + 50, self.rect.y + 20), (self.rect.x + 80, self.rect.y - 40), (self.rect.x + 110, self.rect.y + 20)])
        pygame.draw.polygon(screen, self.color, [(self.rect.x + 50, self.rect.y + 40), (self.rect.x + 80, self.rect.y + 100), (self.rect.x + 110, self.rect.y + 40)])
        pygame.draw.ellipse(screen, self.color, (self.rect.x + 120, self.rect.y + 10, 40, 30))
        pygame.draw.circle(screen, RED, (self.rect.x + 140, self.rect.y + 20), 5)
        pygame.draw.circle(screen, BLACK, (self.rect.x + 140, self.rect.y + 20), 2)
        for i in range(min(self.fire_length, 200)):
            fire_x = self.rect.x + 160 + i
            fire_y = self.rect.y + 25 + random.randint(-5, 5)
            pygame.draw.circle(screen, random.choice([RED, ORANGE, YELLOW]), (fire_x, fire_y), random.randint(2, 5))

# Boss projectile class
class BossProjectile:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 2, y, 4, 8)
        self.speed = -3
        self.color = PINK
        self.dx = 0
        self.speed_x = 0
        self.speed_y = 0
        self.bounce = False
        self.zigzag = False
        self.zigzag_dir = 0

    def move(self, trails):
        self.rect.y += self.speed
        if len(trails) < 100:
            trails.append(MissileTrail(self.rect.centerx, self.rect.bottom, WHITE))

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)

# Function definitions
def load_leaderboard():
    global leaderboard
    if os.path.exists(leaderboard_file):
        with open(leaderboard_file, "r") as f:
            leaderboard = [line.strip().split(",", 1) for line in f.readlines()]
            leaderboard = [(name, int(score)) for name, score in leaderboard]
    leaderboard.sort(key=lambda x: x[1], reverse=True)
    leaderboard = leaderboard[:10]

def save_leaderboard(name, score):
    global leaderboard
    leaderboard.append((name, score))
    leaderboard.sort(key=lambda x: x[1], reverse=True)
    leaderboard = leaderboard[:10]
    with open(leaderboard_file, "w") as f:
        for name, score in leaderboard:
            f.write(f"{name},{score}\n")

def reset_game():
    global player_x, player_y, player_hp, score, missiles_left, bombs_left, missiles, bombs, buildings, explosions, turret_projectiles, thrusters, missile_trails, shockwaves, enemy_ships, enemy_projectiles, power_ups, bomb_packages, boss_active, boss, power_up_effects, level, final_boss_form
    player_x = WIDTH // 2
    player_y = 40
    player_hp = 5
    level = min(level, MAX_LEVELS)
    missiles_left = max(10, 30 - level)
    bombs_left = 0
    score = 0
    power_up_effects = {"missiles": 0, "health": 0}
    missiles.clear()
    bombs.clear()
    buildings.clear()
    explosions.clear()
    turret_projectiles.clear()
    thrusters.clear()
    missile_trails.clear()
    shockwaves.clear()
    enemy_ships.clear()
    enemy_projectiles.clear()
    power_ups.clear()
    bomb_packages.clear()
    env_particles = [EnvParticle() for _ in range(50)]
    boss_active = False
    boss = None
    final_boss_form = 0
    num_buildings = 5 + level * 2
    building_types = ["tower", "house", "factory", "turret"]
    used_x = []
    max_attempts = 100
    for i in range(min(num_buildings, 20)):
        attempts = 0
        while attempts < max_attempts:
            x = random.randint(50, WIDTH - 100)
            if all(abs(x - ux) > 60 for ux in used_x):
                used_x.append(x)
                y = HEIGHT - random.randint(40, 100)
                type_ = random.choice(building_types)
                buildings.append(Building(x, y, type_))
                break
            attempts += 1
        if attempts >= max_attempts:
            break
    for _ in range(min(level, 5)):
        enemy_ships.append(EnemyShip(random.randint(50, WIDTH - 50), random.randint(300, 450)))

def draw_menu():
    global title_scroll_y, title_timer, state, baxter_tail_angle, text_particles
    screen.fill(BLACK)
    for star in stars:
        star.update()
        star.draw()
    for ufo in menu_ufos:
        ufo.move()
        ufo.draw()

    if title_timer < 15 * FPS:
        full_text = "Created by Clint Regenold"
        title = title_font.render(full_text, True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        if title_timer < 10 * FPS or len(text_particles) < len(full_text) * 10:
            screen.blit(title, title_rect)

        if title_timer >= 10 * FPS:
            dragon_x = WIDTH - (title_timer - 10 * FPS) * (WIDTH // (5 * FPS)) - 150
            dragon_y_base = HEIGHT // 2 - 70
            dragon_y_offset = 30 * math.sin(title_timer * 0.1)
            dragon_y = dragon_y_base + dragon_y_offset
            
            pygame.draw.ellipse(screen, DARK_GREEN, (dragon_x, dragon_y + 20, 150, 60))
            pygame.draw.polygon(screen, DARK_GREEN, [(dragon_x + 50, dragon_y + 20), (dragon_x + 80, dragon_y - 40), (dragon_x + 110, dragon_y + 20)])
            pygame.draw.polygon(screen, DARK_GREEN, [(dragon_x + 50, dragon_y + 40), (dragon_x + 80, dragon_y + 100), (dragon_x + 110, dragon_y + 40)])
            pygame.draw.ellipse(screen, DARK_GREEN, (dragon_x + 120, dragon_y + 10, 40, 30))
            pygame.draw.circle(screen, RED, (dragon_x + 140, dragon_y + 20), 5)
            pygame.draw.circle(screen, BLACK, (dragon_x + 140, dragon_y + 20), 2)

            fire_progress = (title_timer - 10 * FPS) / (5 * FPS)
            fire_length = min(200, int(fire_progress * 300))
            for i in range(fire_length):
                fire_x = dragon_x + 160 + i
                fire_y = dragon_y + 25 + random.randint(-5, 5)
                fire_color = random.choice([RED, ORANGE, YELLOW])
                pygame.draw.circle(screen, fire_color, (fire_x, fire_y), random.randint(2, 5))
                if fire_x > title_rect.left and fire_x < title_rect.right and len(text_particles) < len(full_text) * 10:
                    if random.random() < 0.1:
                        text_particles.append(TextParticle(fire_x, title_rect.centery + random.randint(-title_rect.height // 2, title_rect.height // 2)))

            for particle in text_particles[:]:
                particle.update()
                particle.draw()
                if particle.life <= 0:
                    text_particles.remove(particle)

            if title_timer >= 12 * FPS:
                bubble_text = bubble_font.render("...also made by Grok 3", True, BLACK)
                bubble_rect = bubble_text.get_rect(center=(dragon_x + 90, dragon_y - 60))
                pygame.draw.ellipse(screen, WHITE, (bubble_rect.x - 10, bubble_rect.y - 10, bubble_rect.width + 20, bubble_rect.height + 20))
                pygame.draw.polygon(screen, WHITE, [(dragon_x + 90, dragon_y - 30), (dragon_x + 80, dragon_y - 40), (dragon_x + 100, dragon_y - 40)])
                screen.blit(bubble_text, bubble_rect)

        title_timer += 1
    else:
        glow = (pygame.time.get_ticks() // 500) % 2
        title_color = WHITE if glow else YELLOW
        title = title_font.render("City Siege", True, title_color)
        title_rect = title.get_rect(center=(WIDTH // 2, 100))
        screen.blit(title, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        for button in menu_buttons:
            button.check_hover(mouse_pos)
            button.draw()

        baxter_x = WIDTH - 160
        baxter_y = HEIGHT - 50
        bubble_text = bubble_font.render("Approved by Baxter", True, BLACK)
        bubble_rect = bubble_text.get_rect(center=(baxter_x, baxter_y - 130))
        pygame.draw.ellipse(screen, WHITE, (bubble_rect.x - 10, bubble_rect.y - 5, bubble_rect.width + 20, bubble_rect.height + 10))
        pygame.draw.polygon(screen, WHITE, [(baxter_x, baxter_y - 110), (baxter_x - 10, baxter_y - 120), (baxter_x + 10, baxter_y - 120)])
        screen.blit(bubble_text, bubble_rect)

        pygame.draw.polygon(screen, GOLDEN, [(baxter_x - 40, baxter_y), (baxter_x + 40, baxter_y), (baxter_x + 30, baxter_y - 60), (baxter_x - 30, baxter_y - 60)])
        pygame.draw.ellipse(screen, GOLDEN, (baxter_x - 35, baxter_y - 95, 70, 60))
        pygame.draw.polygon(screen, GOLDEN, [(baxter_x - 25, baxter_y - 95), (baxter_x - 50, baxter_y - 45), (baxter_x - 20, baxter_y - 70)])
        pygame.draw.polygon(screen, GOLDEN, [(baxter_x + 25, baxter_y - 95), (baxter_x + 50, baxter_y - 45), (baxter_x + 20, baxter_y - 70)])
        pygame.draw.polygon(screen, GOLDEN, [(baxter_x - 30, baxter_y - 60), (baxter_x - 20, baxter_y - 10), (baxter_x - 30, baxter_y - 10)])
        pygame.draw.polygon(screen, GOLDEN, [(baxter_x + 30, baxter_y - 60), (baxter_x + 30, baxter_y - 10), (baxter_x + 20, baxter_y - 10)])
        tail_angle = math.sin(pygame.time.get_ticks() * 0.005) * 20
        tail_base_x = baxter_x + 40
        tail_base_y = baxter_y - 20
        tail_tip_x = tail_base_x + 20 * math.cos(math.radians(tail_angle))
        tail_tip_y = tail_base_y - 20 * math.sin(math.radians(tail_angle))
        pygame.draw.polygon(screen, GOLDEN, [(tail_base_x, tail_base_y), (tail_tip_x, tail_tip_y), (tail_base_x + 5, tail_base_y - 10)])
        pygame.draw.ellipse(screen, BLACK, (baxter_x - 15, baxter_y - 75, 8, 6))
        pygame.draw.ellipse(screen, BLACK, (baxter_x + 7, baxter_y - 75, 8, 6))
        pygame.draw.ellipse(screen, BLACK, (baxter_x - 5, baxter_y - 65, 10, 6))
        pygame.draw.circle(screen, GOLDEN, (baxter_x - 25, baxter_y - 85), 6)
        pygame.draw.circle(screen, GOLDEN, (baxter_x + 25, baxter_y - 85), 6)
        pygame.draw.circle(screen, GOLDEN, (baxter_x - 20, baxter_y - 40), 5)
        pygame.draw.circle(screen, GOLDEN, (baxter_x + 20, baxter_y - 40), 5)

    pygame.display.update()

def draw_game():
    global score, level, missiles_left, bombs_left, player_hp, firing_cooldown, bomb_cooldown, enemy_spawn_timer, bomb_package_timer, boss_active, boss, player_flash_timer, player_color_index
    screen.fill(BLACK)
    for star in stars:
        star.update()
        star.draw()
    pygame.draw.rect(screen, level_themes[level]["ground_color"], (0, HEIGHT - 50, WIDTH, 50))

    for particle in env_particles:
        particle.update()
        particle.draw()

    player_flash_timer += 1
    if player_flash_timer >= 30:
        player_color_index = (player_color_index + 1) % len(player_colors)
        player_flash_timer = 0
    player_color = player_colors[player_color_index]
    pygame.draw.ellipse(screen, player_color, (player_x - 20, player_y, 40, 20))
    pygame.draw.circle(screen, WHITE, (player_x, player_y + 5), 12)
    pygame.draw.circle(screen, GREEN, (player_x - 10, player_y + 10), 3)
    pygame.draw.circle(screen, GREEN, (player_x + 10, player_y + 10), 3)
    if random.random() < 0.5 and len(thrusters) < 20:
        thrusters.append(ThrusterParticle(player_x, player_y + 20))
    for thruster in thrusters[:]:
        thruster.update()
        thruster.draw()
        if thruster.life <= 0:
            thrusters.remove(thruster)
    if firing_cooldown > 0:
        pygame.draw.circle(screen, ORANGE, (player_x, player_y + 22), 6)
    if bomb_cooldown > 0:
        pygame.draw.circle(screen, RED, (player_x - 10, player_y + 22), 6)

    for missile in missiles[:]:
        missile.move(missile_trails)
        missile.draw()
        if missile.rect.y > HEIGHT:
            missiles.remove(missile)
    for bomb in bombs[:]:
        bomb.move(missile_trails)
        bomb.draw()
        if bomb.rect.y > HEIGHT:
            bombs.remove(bomb)

    for building in buildings[:]:
        building.draw()
        building.fire(turret_projectiles)

    bomb_package_timer -= 1
    if bomb_package_timer <= 0 and len(bomb_packages) < 3:
        bomb_packages.append(BombPackage())
        bomb_package_timer = random.randint(180, 300)
    for package in bomb_packages[:]:
        if not package.update():
            bomb_packages.remove(package)
        else:
            package.draw()
            player_rect = pygame.Rect(player_x - 20, player_y, 40, 20)
            package_rect = pygame.Rect(package.x - 10, package.y + 30, 20, 20)
            if package_rect.colliderect(player_rect):
                bombs_left += 1
                bomb_packages.remove(package)

    enemy_spawn_timer -= 1
    if enemy_spawn_timer <= 0 and len(enemy_ships) < 5 and not boss_active:
        enemy_ships.append(EnemyShip(random.randint(50, WIDTH - 50), random.randint(300, 450)))
        enemy_spawn_timer = random.randint(120, 240)
    for ship in enemy_ships[:]:
        ship.move(enemy_projectiles)
        ship.draw()

    if boss_active and boss:
        boss.move(enemy_projectiles)
        boss.draw()

    player_rect = pygame.Rect(player_x - 20, player_y, 40, 20)
    for proj in turret_projectiles[:]:
        proj.move(missile_trails)
        proj.draw()
        if proj.rect.y < 0:
            turret_projectiles.remove(proj)
        elif proj.rect.colliderect(player_rect):
            player_hp -= 1
            turret_projectiles.remove(proj)
            if player_hp <= 0:
                return "game_over"

    for proj in enemy_projectiles[:]:
        proj.move(missile_trails)
        proj.draw()
        if proj.rect.y < 0:
            enemy_projectiles.remove(proj)
        elif proj.rect.colliderect(player_rect):
            player_hp -= 1
            enemy_projectiles.remove(proj)
            if player_hp <= 0:
                return "game_over"

    for power_up in power_ups[:]:
        if not power_up.update():
            power_ups.remove(power_up)
        else:
            power_up.draw()
            if power_up.rect.colliderect(player_rect):
                if power_up.type == "missiles":
                    power_up_effects["missiles"] = 300
                    missiles_left += 10
                elif power_up.type == "health":
                    player_hp = min(5, player_hp + 1)
                power_ups.remove(power_up)

    for effect in power_up_effects:
        if power_up_effects[effect] > 0:
            power_up_effects[effect] -= 1

    for exp in explosions[:]:
        exp.update()
        exp.draw()
        if exp.life <= 0:
            explosions.remove(exp)
    for shock in shockwaves[:]:
        shock.update()
        shock.draw()
        if shock.life <= 0:
            shockwaves.remove(shock)

    for trail in missile_trails[:]:
        trail.update()
        trail.draw()
        if trail.life <= 0:
            missile_trails.remove(trail)

    score_text = menu_font.render(f"Score: {score}", True, WHITE)
    level_text = menu_font.render(f"Level: {level} - {level_themes[level]['name']}", True, WHITE)
    missiles_text = menu_font.render(f"Missiles: {missiles_left}", True, WHITE)
    bombs_text = menu_font.render(f"Bombs: {bombs_left}", True, WHITE)
    hp_text = menu_font.render(f"Ship HP: {player_hp}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (10, 40))
    screen.blit(missiles_text, (10, 70))
    screen.blit(bombs_text, (10, 100))
    screen.blit(hp_text, (10, 130))
    pygame.draw.rect(screen, RED, (150, 130, 100, 10))
    pygame.draw.rect(screen, GREEN, (150, 130, player_hp * 20, 10))

    return None

def draw_final_boss():
    global score, missiles_left, bombs_left, player_hp, firing_cooldown, bomb_cooldown, boss, final_boss_form, bomb_package_timer, state, beat_final_boss, player_flash_timer, player_color_index
    screen.fill(BLACK)
    for star in stars:
        star.update()
        star.draw()
    for particle in env_particles:
        particle.update()
        particle.draw()

    player_flash_timer += 1
    if player_flash_timer >= 30:
        player_color_index = (player_color_index + 1) % len(player_colors)
        player_flash_timer = 0
    player_color = player_colors[player_color_index]
    pygame.draw.ellipse(screen, player_color, (player_x - 20, player_y, 40, 20))
    pygame.draw.circle(screen, WHITE, (player_x, player_y + 5), 12)
    pygame.draw.circle(screen, GREEN, (player_x - 10, player_y + 10), 3)
    pygame.draw.circle(screen, GREEN, (player_x + 10, player_y + 10), 3)
    if random.random() < 0.5 and len(thrusters) < 20:
        thrusters.append(ThrusterParticle(player_x, player_y + 20))
    for thruster in thrusters[:]:
        thruster.update()
        thruster.draw()
        if thruster.life <= 0:
            thrusters.remove(thruster)
    if firing_cooldown > 0:
        pygame.draw.circle(screen, ORANGE, (player_x, player_y + 22), 6)
    if bomb_cooldown > 0:
        pygame.draw.circle(screen, RED, (player_x - 10, player_y + 22), 6)

    for missile in missiles[:]:
        missile.move(missile_trails)
        missile.draw()
        if missile.rect.y > HEIGHT:
            missiles.remove(missile)
    for bomb in bombs[:]:
        bomb.move(missile_trails)
        bomb.draw()
        if bomb.rect.y > HEIGHT:
            bombs.remove(bomb)

    if not isinstance(boss, FinalBoss):
        if final_boss_form <= 3:
            boss = FinalBoss(final_boss_form if final_boss_form > 0 else 1)
    if boss:
        boss.move(enemy_projectiles)
        boss.draw()
        print(f"FinalBoss drawn: type={type(boss).__name__}, form={boss.form}, color={boss.color}")

    bomb_package_timer -= 1
    if bomb_package_timer <= 0 and len(bomb_packages) < 3:
        bomb_packages.append(BombPackage())
        bomb_package_timer = 180
    for package in bomb_packages[:]:
        if not package.update():
            bomb_packages.remove(package)
        else:
            package.draw()
            player_rect = pygame.Rect(player_x - 20, player_y, 40, 20)
            package_rect = pygame.Rect(package.x - 10, package.y + 30, 20, 20)
            if package_rect.colliderect(player_rect):
                bombs_left += 1
                bomb_packages.remove(package)

    player_rect = pygame.Rect(player_x - 20, player_y, 40, 20)
    for proj in enemy_projectiles[:]:
        proj.move(missile_trails)
        proj.draw()
        if proj.rect.y < 0:
            enemy_projectiles.remove(proj)
        elif proj.rect.colliderect(player_rect):
            player_hp -= 1
            enemy_projectiles.remove(proj)
            if player_hp <= 0:
                return "game_over"

    for exp in explosions[:]:
        exp.update()
        exp.draw()
        if exp.life <= 0:
            explosions.remove(exp)
    for shock in shockwaves[:]:
        shock.update()
        shock.draw()
        if shock.life <= 0:
            shockwaves.remove(shock)

    for trail in missile_trails[:]:
        trail.update()
        trail.draw()
        if trail.life <= 0:
            missile_trails.remove(trail)

    form_text = menu_font.render(f"Form: {'Fire' if final_boss_form == 1 else 'Ice' if final_boss_form == 2 else 'Storm'} Dragon", True, WHITE)
    score_text = menu_font.render(f"Score: {score}", True, WHITE)
    missiles_text = menu_font.render(f"Missiles: {missiles_left}", True, WHITE)
    bombs_text = menu_font.render(f"Bombs: {bombs_left}", True, WHITE)
    hp_text = menu_font.render(f"Ship HP: {player_hp}", True, WHITE)
    screen.blit(form_text, (10, 10))
    screen.blit(score_text, (10, 40))
    screen.blit(missiles_text, (10, 70))
    screen.blit(bombs_text, (10, 100))
    screen.blit(hp_text, (10, 130))
    pygame.draw.rect(screen, RED, (150, 130, 100, 10))
    pygame.draw.rect(screen, GREEN, (150, 130, player_hp * 20, 10))

    if state == GAME_OVER:
        return "game_over"

    return None

def draw_level_select():
    screen.fill(BLACK)
    for star in stars:
        star.update()
        star.draw()
    title = title_font.render("Select Level", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

    mouse_pos = pygame.mouse.get_pos()
    clicked = pygame.mouse.get_pressed()[0]
    for i in range(MAX_LEVELS):
        row = i // 5
        col = i % 5
        x = WIDTH // 6 * (col + 1)
        y = 150 + row * 60
        level_text = menu_font.render(str(i + 1), True, WHITE)
        level_rect = level_text.get_rect(center=(x, y))
        screen.blit(level_text, level_rect)
        border_color = YELLOW if level_rect.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(screen, border_color, level_rect.inflate(20, 10), 2)

    back_text = menu_font.render("Press B to go Back", True, WHITE)
    screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 50))

def draw_leaderboard():
    global leaderboard
    screen.fill(BLACK)
    for star in stars:
        star.update()
        star.draw()
    
    rainbow_colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, MAGENTA]
    color_index = (pygame.time.get_ticks() // 200) % len(rainbow_colors)
    
    title = menu_font.render("Leaderboard", True, rainbow_colors[color_index])
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
    for i, (name, score_val) in enumerate(leaderboard):
        text = menu_font.render(f"{i + 1}. {name} - {score_val}", True, rainbow_colors[(color_index + i) % len(rainbow_colors)])
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 100 + i * 40))
    back_text = menu_font.render("Press B to go Back", True, WHITE)
    screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 50))

def draw_game_over():
    screen.fill(BLACK)
    for star in stars:
        star.update()
        star.draw()
    over_text = menu_font.render("Game Over", True, WHITE)
    score_text = menu_font.render(f"Final Score: {score}", True, WHITE)
    name_prompt = menu_font.render("Enter 3-letter name: " + name_input, True, WHITE)
    screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, 200))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 250))
    screen.blit(name_prompt, (WIDTH // 2 - name_prompt.get_width() // 2, 300))

def draw_credits():
    global credits_scroll_y, fireworks
    screen.fill(BLACK)
    for star in stars:
        star.update()
        star.draw()

    if random.random() < 0.05:
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        for _ in range(20):
            fireworks.append(FireworkParticle(x, y))
    
    for firework in fireworks[:]:
        firework.update()
        firework.draw()
        if firework.life <= 0:
            fireworks.remove(firework)

    credits_lines = [
        "Credits",
        "",
        "Created by Clint Regenold and Grok 3",
        "",
        "Special Thanks to:",
        "Peanut",
        "Fred",
        "Steph",
        "",
        "Thanks for playing!"
    ]

    rainbow_colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, MAGENTA]
    line_height = 40
    total_height = len(credits_lines) * line_height
    credits_scroll_y -= 1
    if credits_scroll_y < -total_height:
        credits_scroll_y = HEIGHT

    current_time = pygame.time.get_ticks()
    for i, line in enumerate(credits_lines):
        if i == 0:  # "Credits" title
            text = title_font.render(line, True, WHITE)
        elif line == "Peanut":
            color_index = (current_time // 150) % len(rainbow_colors)  # Fast flash (150ms)
            text = menu_font.render(line, True, rainbow_colors[color_index])
        elif line == "Fred":
            color_index = (current_time // 200) % len(rainbow_colors)  # Medium flash (200ms)
            text = menu_font.render(line, True, rainbow_colors[color_index])
        elif line == "Steph":
            color_index = (current_time // 250) % len(rainbow_colors)  # Slower flash (250ms)
            text = menu_font.render(line, True, rainbow_colors[color_index])
        else:
            text = menu_font.render(line, True, WHITE)  # All other lines stay white
        text_rect = text.get_rect(center=(WIDTH // 2, credits_scroll_y + i * line_height))
        screen.blit(text, text_rect)

    back_text = menu_font.render("Press B to go Back", True, WHITE)
    screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 50))

def draw_controls():
    screen.fill(BLACK)
    for star in stars_controls:  # Use separate star list for controls page
        star.update()
        star.draw()

    title = title_font.render("Game Controls", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

    controls_text = [
        "Keyboard Controls:",
        "Move: Arrow Keys",
        "Fire Missiles: Spacebar",
        "Drop Bombs: Left Ctrl",
        "",
        "Mouse Controls:",
        "Move: Mouse Cursor",
        "Fire Missiles: Left Click",
        "Drop Bombs: Right Click"
    ]

    for i, line in enumerate(controls_text):
        text = menu_font.render(line, True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 150 + i * 40))

    back_text = menu_font.render("Press B to go Back", True, WHITE)
    screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 50))

# Game objects initialization
missiles = []
bombs = []
buildings = []
stars = [StarParticle(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(50)]
stars_controls = [StarParticle(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(50)]  # Separate stars for controls page
env_particles = [EnvParticle() for _ in range(50)]
thrusters = []
missile_trails = []
explosions = []
shockwaves = []
turret_projectiles = []
enemy_ships = []
enemy_projectiles = []
power_ups = []
bomb_packages = []
menu_ufos = [MenuUFO() for _ in range(5)]
leaderboard_file = "leaderboard.txt"
leaderboard = []
load_leaderboard()
reset_game()

menu_buttons = [
    MenuButton("Start Game (S)", WIDTH // 2, 250, pygame.K_s, GAME),
    MenuButton("Select Level (V)", WIDTH // 2, 300, pygame.K_v, LEVEL_SELECT),
    MenuButton("Leaderboard (L)", WIDTH // 2, 350, pygame.K_l, LEADERBOARD),
    MenuButton("Controls (T)", WIDTH // 2, 400, pygame.K_t, CONTROLS),
    MenuButton("Credits (C)", WIDTH // 2, 450, pygame.K_c, CREDITS),
    MenuButton("Quit (Q)", WIDTH // 2, 500, pygame.K_q, "quit")
]

# Main game loop
print("Entering main loop...")
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if state == MENU:
                for button in menu_buttons:
                    if event.key == button.key:
                        if button.target_state == "quit":
                            running = False
                        elif button.target_state == GAME:
                            reset_game()
                            state = GAME
                        else:
                            state = button.target_state
            elif state in [LEVEL_SELECT, LEADERBOARD, CONTROLS, CREDITS] and event.key == pygame.K_b:
                state = MENU
            elif state == GAME_OVER:
                if event.key == pygame.K_RETURN and len(name_input) == 3:
                    save_leaderboard(name_input, score)
                    name_input = ""
                    if beat_final_boss:
                        state = CREDITS
                        beat_final_boss = False
                    else:
                        state = LEADERBOARD
                elif event.key == pygame.K_BACKSPACE:
                    name_input = name_input[:-1]
                elif len(name_input) < 3 and event.unicode.isalnum():
                    name_input += event.unicode.upper()
            elif state in [GAME, FINAL_BOSS]:
                if event.key == pygame.K_SPACE and missiles_left > 0 and firing_cooldown <= 0:
                    if power_up_effects["missiles"] > 0:
                        for angle in [-2, -1, 0, 1, 2]:
                            missiles.append(Missile(player_x, player_y + 20, angle))
                    else:
                        missiles.append(Missile(player_x, player_y + 20))
                    missiles_left -= 1
                    firing_cooldown = 10
                elif event.key == pygame.K_LCTRL and bombs_left > 0 and bomb_cooldown <= 0:
                    bombs.append(Bomb(player_x, player_y + 20))
                    bombs_left -= 1
                    bomb_cooldown = 15
            elif state == CREDITS and event.key == pygame.K_b:
                state = MENU
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if state == MENU and title_timer >= 15 * FPS:
                mouse_pos = pygame.mouse.get_pos()
                for button in menu_buttons:
                    if button.check_click(mouse_pos):
                        if button.target_state == "quit":
                            running = False
                        elif button.target_state == GAME:
                            reset_game()
                            state = GAME
                        else:
                            state = button.target_state
            elif state in [GAME, FINAL_BOSS]:
                if event.button == 1 and missiles_left > 0 and firing_cooldown <= 0:
                    if power_up_effects["missiles"] > 0:
                        for angle in [-2, -1, 0, 1, 2]:
                            missiles.append(Missile(player_x, player_y + 20, angle))
                    else:
                        missiles.append(Missile(player_x, player_y + 20))
                    missiles_left -= 1
                    firing_cooldown = 10
                elif event.button == 3 and bombs_left > 0 and bomb_cooldown <= 0:
                    bombs.append(Bomb(player_x, player_y + 20))
                    bombs_left -= 1
                    bomb_cooldown = 15

    if state == MENU:
        draw_menu()
    elif state == LEVEL_SELECT:
        draw_level_select()
        mouse_pos = pygame.mouse.get_pos()
        clicked = pygame.mouse.get_pressed()[0]
        if clicked:
            for i in range(MAX_LEVELS):
                row = i // 5
                col = i % 5
                x = WIDTH // 6 * (col + 1)
                y = 150 + row * 60
                level_rect = menu_font.render(str(i + 1), True, WHITE).get_rect(center=(x, y)).inflate(20, 10)
                if level_rect.collidepoint(mouse_pos):
                    level = i + 1
                    reset_game()
                    state = GAME
                    break
    elif state == GAME:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_x = max(20, min(WIDTH - 20, mouse_x))
        player_y = max(20, min(HEIGHT - 50, mouse_y))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 20:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - 20:
            player_x += player_speed
        if keys[pygame.K_UP] and player_y > 20:
            player_y -= player_speed
        if keys[pygame.K_DOWN] and player_y < HEIGHT - 50:
            player_y += player_speed
        if firing_cooldown > 0:
            firing_cooldown -= 1
        if bomb_cooldown > 0:
            bomb_cooldown -= 1

        missiles_to_remove = []
        bombs_to_remove = []
        buildings_to_remove = []
        ships_to_remove = []
        enemy_projectiles_to_remove = []
        player_rect = pygame.Rect(player_x - 20, player_y, 40, 20)

        for missile in missiles:
            missile.move(missile_trails)
            for building in buildings:
                if missile.rect.colliderect(building.rect):
                    building.hp -= (3 if missile.is_powered else 1)
                    missiles_to_remove.append(missile)
                    if building.hp <= 0:
                        score += 100 if building.type == "tower" else 50
                        for _ in range(20):
                            explosions.append(ExplosionParticle(building.rect.centerx, building.rect.centery))
                        shockwaves.append(Shockwave(building.rect.centerx, building.rect.centery))
                        buildings_to_remove.append(building)
                    break
            else:
                for ship in enemy_ships:
                    if missile.rect.colliderect(ship.rect):
                        ship.hp -= (3 if missile.is_powered else 1)
                        missiles_to_remove.append(missile)
                        if ship.hp <= 0:
                            score += 150
                            missiles_left += 5
                            for _ in range(20):
                                explosions.append(ExplosionParticle(ship.rect.centerx, ship.rect.centery, is_enemy=True))
                            if random.random() < 0.35 and len(enemy_ships) > 1:
                                power_ups.append(PowerUp(ship.rect.centerx, ship.rect.centery))
                            ships_to_remove.append(ship)
                        break
                else:
                    if boss_active and boss and missile.rect.colliderect(boss.rect):
                        boss.hp -= (3 if missile.is_powered else 1)
                        missiles_to_remove.append(missile)
                        if boss.hp <= 0:
                            score += 500
                            boss_active = False
                            boss = None
                            if level == MAX_LEVELS:
                                state = FINAL_BOSS
                                final_boss_form = 1
                                boss = FinalBoss(final_boss_form)
                                print(f"Transition to FINAL_BOSS: boss type={type(boss).__name__}, form={boss.form}, color={boss.color}")
                            else:
                                level += 1
                                reset_game()
                            break

        for bomb in bombs:
            bomb.move(missile_trails)
            for building in buildings:
                if bomb.rect.colliderect(building.rect):
                    building.hp -= bomb.damage
                    bombs_to_remove.append(bomb)
                    for _ in range(30):
                        explosions.append(ExplosionParticle(bomb.rect.centerx, bomb.rect.centery, is_bomb=True))
                    shockwaves.append(Shockwave(bomb.rect.centerx, bomb.rect.centery, is_bomb=True))
                    if building.hp <= 0:
                        score += 100 if building.type == "tower" else 50
                        buildings_to_remove.append(building)
                    break
            else:
                for ship in enemy_ships:
                    if bomb.rect.colliderect(ship.rect):
                        ship.hp -= bomb.damage
                        bombs_to_remove.append(bomb)
                        for _ in range(30):
                            explosions.append(ExplosionParticle(bomb.rect.centerx, bomb.rect.centery, is_bomb=True))
                        shockwaves.append(Shockwave(bomb.rect.centerx, bomb.rect.centery, is_bomb=True))
                        if ship.hp <= 0:
                            score += 150
                            missiles_left += 5
                            for _ in range(20):
                                explosions.append(ExplosionParticle(ship.rect.centerx, ship.rect.centery, is_enemy=True))
                            if random.random() < 0.35 and len(enemy_ships) > 1:
                                power_ups.append(PowerUp(ship.rect.centerx, ship.rect.centery))
                            ships_to_remove.append(ship)
                        break
                else:
                    if boss_active and boss and bomb.rect.colliderect(boss.rect):
                        boss.hp -= bomb.damage
                        bombs_to_remove.append(bomb)
                        for _ in range(30):
                            explosions.append(ExplosionParticle(bomb.rect.centerx, bomb.rect.centery, is_bomb=True))
                        shockwaves.append(Shockwave(bomb.rect.centerx, bomb.rect.centery, is_bomb=True))
                        if boss.hp <= 0:
                            score += 500
                            boss_active = False
                            boss = None
                            if level == MAX_LEVELS:
                                state = FINAL_BOSS
                                final_boss_form = 1
                                boss = FinalBoss(final_boss_form)
                                print(f"Transition to FINAL_BOSS: boss type={type(boss).__name__}, form={boss.form}, color={boss.color}")
                            else:
                                level += 1
                                reset_game()
                            break

        for missile in missiles_to_remove:
            if missile in missiles:
                missiles.remove(missile)
        for bomb in bombs_to_remove:
            if bomb in bombs:
                bombs.remove(bomb)
        for building in buildings_to_remove:
            if building in buildings:
                buildings.remove(building)
        for ship in ships_to_remove:
            if ship in enemy_ships:
                enemy_ships.remove(ship)
        for proj in enemy_projectiles_to_remove:
            if proj in enemy_projectiles:
                enemy_projectiles.remove(proj)

        if not buildings and not boss_active:
            boss_active = True
            boss = Boss()
            enemy_ships.clear()

        if missiles_left <= 0 and bombs_left <= 0 and not missiles and not bombs:
            state = GAME_OVER
        game_over_signal = draw_game()
        if game_over_signal == "game_over":
            state = GAME_OVER

    elif state == FINAL_BOSS:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_x = max(20, min(WIDTH - 20, mouse_x))
        player_y = max(20, min(HEIGHT - 50, mouse_y))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 20:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - 20:
            player_x += player_speed
        if keys[pygame.K_UP] and player_y > 20:
            player_y -= player_speed
        if keys[pygame.K_DOWN] and player_y < HEIGHT - 50:
            player_y += player_speed
        if firing_cooldown > 0:
            firing_cooldown -= 1
        if bomb_cooldown > 0:
            bomb_cooldown -= 1

        missiles_to_remove = []
        bombs_to_remove = []
        player_rect = pygame.Rect(player_x - 20, player_y, 40, 20)
        for missile in missiles:
            missile.move(missile_trails)
            if boss and missile.rect.colliderect(boss.rect):
                boss.hp -= (3 if missile.is_powered else 1)
                missiles_to_remove.append(missile)
                if boss.hp <= 0:
                    final_boss_form += 1
                    if final_boss_form > 3:
                        state = GAME_OVER
                        beat_final_boss = True
                        boss = None
                    else:
                        boss = FinalBoss(final_boss_form)
                        score += 1000
                        print(f"New FinalBoss form: type={type(boss).__name__}, form={boss.form}, color={boss.color}")
        for bomb in bombs:
            bomb.move(missile_trails)
            if boss and bomb.rect.colliderect(boss.rect):
                boss.hp -= bomb.damage
                bombs_to_remove.append(bomb)
                for _ in range(30):
                    explosions.append(ExplosionParticle(bomb.rect.centerx, bomb.rect.centery, is_bomb=True))
                shockwaves.append(Shockwave(bomb.rect.centerx, bomb.rect.centery, is_bomb=True))
                if boss.hp <= 0:
                    final_boss_form += 1
                    if final_boss_form > 3:
                        state = GAME_OVER
                        beat_final_boss = True
                        boss = None
                    else:
                        boss = FinalBoss(final_boss_form)
                        score += 1000
                        print(f"New FinalBoss form: type={type(boss).__name__}, form={boss.form}, color={boss.color}")

        for missile in missiles_to_remove:
            if missile in missiles:
                missiles.remove(missile)
        for bomb in bombs_to_remove:
            if bomb in bombs:
                bombs.remove(bomb)

        if missiles_left <= 0 and bombs_left <= 0 and not missiles and not bombs:
            state = GAME_OVER
        game_over_signal = draw_final_boss()
        if game_over_signal == "game_over":
            state = GAME_OVER

    elif state == LEADERBOARD:
        draw_leaderboard()
    elif state == GAME_OVER:
        draw_game_over()
    elif state == CREDITS:
        draw_credits()
    elif state == CONTROLS:
        draw_controls()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()