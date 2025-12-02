import pygame
import sys
import math
import random
import os
from pygame import Vector2

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 60
TILE_SIZE = 50
PLAYER_SPEED = 5
BULLET_SPEED = 10
BULLET_LIFETIME = 60  # frames
PLAYER_SIZE = 40
BULLET_SIZE = 6
RESPAWN_TIME = 120  # frames

# Bullet settings
BULLET_BOUNCES_MAX = 3
MAX_BULLETS = 200  # cap to prevent perf spikes

# Weapon balance settings
ROCKET_WINDOW_FRAMES = 5 * FPS  # 5 seconds window
ROCKET_MAX_PER_WINDOW = 3  # max RPG shots per 5s window

# Dash settings
DASH_DISTANCE = 140
DASH_COOLDOWN_FRAMES = 90

# Skill settings
SKILL_DURATION_FRAMES = 180  # 3s shield
SKILL_COOLDOWN_FRAMES = 600  # 10s cooldown

# Match settings
TARGET_SCORE = 10


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)

# Game setup
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Holo shoot")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
SPRITE_CACHE = {}
GRID_CACHE = {}

def load_sprite(path, size):
    if not path:
        return None
    try:
        if not os.path.isfile(path):
            return None
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.smoothscale(img, (size, size))
        return img
    except Exception:
        return None

def generate_char_sprite(char_name, size, fallback_color):
    base_size = 24
    surf_small = pygame.Surface((base_size, base_size), pygame.SRCALPHA)
    cx = base_size // 2
    cy = base_size // 2

    skin = (255, 228, 210)
    hair = fallback_color
    outfit = fallback_color
    accent = (255, 255, 255)
    eye = (40, 40, 60)
    name = (char_name or '').lower()
    if name == 'risto':
        hair = (190, 140, 255)
        outfit = (120, 70, 200)
        accent = (80, 255, 220)
        eye = (70, 40, 120)
    elif name == 'nerissa':
        hair = (40, 200, 170)
        outfit = (20, 40, 60)
        accent = (180, 220, 255)
        eye = (120, 200, 190)
    elif name == 'suisei':
        hair = (90, 170, 255)
        outfit = (40, 80, 160)
        accent = (255, 230, 120)
        eye = (70, 130, 220)
    elif name == 'miko':
        hair = (255, 150, 210)
        outfit = (250, 250, 250)
        accent = (220, 60, 80)
        eye = (80, 140, 80)
    elif name == 'botan':
        hair = (230, 230, 230)
        outfit = (90, 90, 90)
        accent = (120, 255, 180)
        eye = (80, 80, 80)
    elif name == 'kronii':
        hair = (80, 110, 200)
        outfit = (20, 30, 80)
        accent = (240, 220, 120)
        eye = (100, 140, 220)
    elif name == 'moona':
        hair = (190, 160, 255)
        outfit = (40, 50, 130)
        accent = (120, 220, 255)
        eye = (110, 80, 160)
    elif name == 'raora':
        hair = (220, 120, 255)
        outfit = (50, 10, 70)
        accent = (255, 120, 120)
        eye = (200, 120, 200)
    elif name == 'marine':
        hair = (220, 80, 120)
        outfit = (40, 20, 60)
        accent = (240, 200, 80)
        eye = (200, 80, 120)
    elif name == 'ayame':
        hair = (255, 255, 255)
        outfit = (230, 230, 230)
        accent = (230, 70, 70)
        eye = (200, 60, 90)

    shadow_rect = pygame.Rect(cx - 7, base_size - 6, 14, 4)
    pygame.draw.ellipse(surf_small, (0, 0, 0, 110), shadow_rect)

    body_rect = pygame.Rect(cx - 4, cy + 1, 8, 7)
    pygame.draw.rect(surf_small, outfit, body_rect)
    inner_body = body_rect.inflate(-4, -3)
    if inner_body.width > 0 and inner_body.height > 0:
        pygame.draw.rect(surf_small, accent, inner_body)

    head_rect = pygame.Rect(cx - 5, cy - 7, 10, 8)
    pygame.draw.rect(surf_small, hair, head_rect)
    face_rect = pygame.Rect(head_rect.left + 1, head_rect.top + 3, head_rect.width - 2, head_rect.height - 3)
    pygame.draw.rect(surf_small, skin, face_rect)

    eye_y = face_rect.top + 2
    pygame.draw.rect(surf_small, eye, (face_rect.left + 1, eye_y, 2, 2))
    pygame.draw.rect(surf_small, eye, (face_rect.right - 3, eye_y, 2, 2))

    if name == 'ayame':
        pygame.draw.rect(surf_small, accent, (head_rect.left - 1, head_rect.top + 1, 2, 3))
        pygame.draw.rect(surf_small, accent, (head_rect.right - 1, head_rect.top + 1, 2, 3))
    elif name == 'suisei':
        pygame.draw.rect(surf_small, accent, (head_rect.right - 2, head_rect.top + 1, 2, 2))
    elif name == 'nerissa':
        pygame.draw.rect(surf_small, outfit, (body_rect.left - 2, body_rect.top, 2, 4))
        pygame.draw.rect(surf_small, outfit, (body_rect.right, body_rect.top, 2, 4))
    elif name == 'miko':
        pygame.draw.rect(surf_small, accent, (body_rect.left, body_rect.top + 2, body_rect.width, 2))
    elif name == 'botan':
        pygame.draw.rect(surf_small, hair, (body_rect.left - 1, body_rect.top - 1, body_rect.width + 2, 2))
    elif name == 'kronii':
        pygame.draw.rect(surf_small, accent, (head_rect.left - 1, head_rect.top, head_rect.width + 2, 1))
    elif name == 'moona':
        pygame.draw.rect(surf_small, accent, (head_rect.left, head_rect.bottom, head_rect.width, 1))

    return pygame.transform.scale(surf_small, (size, size))

def get_char_sprite_cached(char_name, size, fallback_color):
    key = (char_name or '', size, fallback_color)
    sprite = SPRITE_CACHE.get(key)
    if sprite is None:
        sprite = generate_char_sprite(char_name, size, fallback_color)
        SPRITE_CACHE[key] = sprite
    return sprite

# UI helpers
def draw_background_grid(surface, gap=50, color=(30,30,30)):
    key = (gap, color)
    grid = GRID_CACHE.get(key)
    if grid is None:
        grid = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        grid.fill(BLACK)
        for x in range(0, WINDOW_WIDTH, gap):
            pygame.draw.line(grid, color, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, gap):
            pygame.draw.line(grid, color, (0, y), (WINDOW_WIDTH, y))
        GRID_CACHE[key] = grid
    surface.blit(grid, (0, 0))

def draw_panel(surface, rect, color=(0,0,0,140)):
    panel = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    panel.fill(color)
    surface.blit(panel, (rect[0], rect[1]))

# Particles
class Particle:
    def __init__(self, pos, vel, life, color):
        self.pos = Vector2(pos.x, pos.y)
        self.vel = Vector2(vel.x, vel.y)
        self.life = life
        self.color = color
        self.radius = 2
    def update(self):
        self.pos += self.vel
        self.vel *= 0.92
        self.life -= 1
        return self.life <= 0
    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)

# No time stop overlay anymore

class Player:
    def __init__(self, x, y, color, controls, shoot_key, image_path=None, dash_key=None, skill_key=None, char_class='Generic'):
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.color = color
        self.radius = PLAYER_SIZE // 2
        self.speed = PLAYER_SPEED
        self.max_health = 100
        self.health = self.max_health
        self.score = 0
        self.level = 1
        self.exp = 0
        self.exp_to_next = 100
        self.pending_levelups = 0
        self.respawn_timer = 0
        self.controls = controls  # [up, left, down, right]
        self.shoot_key = shoot_key
        self.dash_key = dash_key
        self.skill_key = skill_key
        self.direction = Vector2(1, 0)  # Default facing right
        self.char_class = char_class
        self.last_shot = 0
        self.shot_delay = 15  # frames between shots
        # effects
        self.effect_timers = {}
        self.base_speed = PLAYER_SPEED
        self.base_shot_delay = 15
        self.speed = self.base_speed
        self.shot_delay = self.base_shot_delay
        self.multishot = 1
        self.bullet_speed_mult = 1.0
        # Botan weapon mode
        self.weapon_mode = 'pistol'  # rpg | sniper | dsmg
        # Ayame sword mode (flag: 0 = off, 1 = on)
        self.sword_mode_timer = 0
        # dash
        self.dash_cooldown = 0
        # skill
        self.skill_cooldown = 0
        # botan rocket rate-limit window (timestamps of fired rockets)
        self.rocket_fire_times = []
        # Kronii rewind state
        self.rewind_history = []
        self.rewind_shadow_pos = None
        # Moona meteor shower state
        self.meteor_shower_timer = 0
        self.meteor_shower_big_done = False
        # Marine pirate ship state
        self.marine_ship_primed = False
        self.skill_was_down = False
        # polish
        self.hit_flash_timer = 0
        self.invuln_timer = 0
        # sprite
        self.anim_timer = 0
        self.is_moving = False
        self.sprite_base = load_sprite(image_path, PLAYER_SIZE)
        if self.sprite_base is None:
            self.sprite_base = get_char_sprite_cached(self.char_class, PLAYER_SIZE, self.color)
        self.sprite = self.sprite_base

    # Effects API
    def apply_effect(self, name, duration_frames):
        self.effect_timers[name] = duration_frames
        if name == 'speed':
            self.speed = self.base_speed * 1.6
        elif name == 'rapid':
            self.shot_delay = max(4, int(self.base_shot_delay * 0.5))
        elif name == 'multi':
            self.multishot = 10
        elif name == 'shield':
            self.invuln_timer = max(self.invuln_timer, duration_frames)
        elif name == 'time_slow':
            # drastically slow movement and attack speed
            self.speed = self.base_speed * 0.4
            self.shot_delay = max(6, int(self.base_shot_delay * 2.0))
        elif name == 'heal':
            self.health = min(self.max_health, self.health + 30)

    def update_effects(self):
        expired = []
        for k in list(self.effect_timers.keys()):
            self.effect_timers[k] -= 1
            if self.effect_timers[k] <= 0:
                expired.append(k)
        for k in expired:
            self.effect_timers.pop(k, None)
            if k == 'speed':
                self.speed = self.base_speed
            elif k == 'rapid':
                self.shot_delay = self.base_shot_delay
            elif k == 'multi':
                self.multishot = 1
            elif k == 'time_slow':
                # restore to base when slow ends
                self.speed = self.base_speed
                self.shot_delay = self.base_shot_delay
            # 'shield' ends via invuln_timer countdown in draw/update

    def gain_exp(self, amount):
        if amount <= 0:
            return
        # Increase experience gained by 50%
        amount = int(amount * 1.5)
        self.exp += amount
        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level += 1
            self.pending_levelups += 1
            # Slightly reduce exp needed for next level to make leveling smoother
            self.exp_to_next = int(self.exp_to_next * 1.35)
            # Small heal on level up
            self.health = min(self.max_health, self.health + 15)

    def apply_level_upgrade(self, choice_index):
        if choice_index == 0:
            self.base_speed *= 1.12
            self.speed = self.base_speed
        elif choice_index == 1:
            self.base_shot_delay = max(4, int(self.base_shot_delay * 0.85))
            self.shot_delay = min(self.shot_delay, self.base_shot_delay)
        elif choice_index == 2:
            self.max_health += 40
            self.health = self.max_health

    def get_bullet_speed(self):
        return BULLET_SPEED

    def current_effect_label(self):
        if not self.effect_timers:
            return ''
        # pick longest remaining to display
        name = max(self.effect_timers, key=lambda k: self.effect_timers[k])
        secs = self.effect_timers.get(name, 0) / FPS
        labels = {
            'speed': 'Speed Boost',
            'rapid': 'Rapid Fire',
            'multi': 'Multishot',
            'shield': 'Shield',
        }
        return f"{labels.get(name, name)} {secs:.1f}s"

    def update(self, walls, bullets, lasers, rockets, meteors, particles, domains, enemy, current_frame):
        if self.respawn_timer > 0:
            self.respawn_timer -= 1
            if self.respawn_timer == 0:
                self.respawn(walls)
            return

        keys = pygame.key.get_pressed()

        # Movement
        move = Vector2(0, 0)
        if keys[self.controls[0]]:  # Up
            move.y -= 1
        if keys[self.controls[1]]:  # Left
            move.x -= 1
        if keys[self.controls[2]]:  # Down
            move.y += 1
        if keys[self.controls[3]]:  # Right
            move.x += 1

        moving_vec = move.length() > 0
        if moving_vec:
            move = move.normalize()
            self.direction = move
        self.is_moving = moving_vec

        target_vel = Vector2(0, 0)
        if moving_vec:
            target_vel = move * self.speed
        smooth = 0.35
        self.vel += (target_vel - self.vel) * smooth
        if not moving_vec and self.vel.length() < 0.15:
            self.vel.xy = (0, 0)

        new_pos = self.pos + self.vel
        player_rect = pygame.Rect(
            new_pos.x - self.radius, 
            new_pos.y - self.radius,
            PLAYER_SIZE, PLAYER_SIZE
        )
        can_move = True
        for wall in walls:
            if player_rect.colliderect(wall.rect):
                can_move = False
                break
        if can_move:
            self.pos = new_pos

        # Keep player in bounds
        self.pos.x = max(self.radius, min(WINDOW_WIDTH - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(WINDOW_HEIGHT - self.radius, self.pos.y))

        if self.char_class.lower() == 'kronii':
            self.rewind_history.append((Vector2(self.pos.x, self.pos.y), self.health))
            max_len = FPS * 3
            if len(self.rewind_history) > max_len:
                self.rewind_history.pop(0)
            if self.rewind_history:
                self.rewind_shadow_pos = Vector2(self.rewind_history[0][0].x, self.rewind_history[0][0].y)

        # Dash removed (no dash action)

        # Active skill by character
        if self.skill_cooldown > 0:
            self.skill_cooldown -= 1
        skill_down = bool(self.skill_key is not None and keys[self.skill_key])
        just_pressed = skill_down and not self.skill_was_down
        if just_pressed:
            cc = self.char_class.lower()
            next_cd = None
            if cc == 'nerissa':
                if self.skill_cooldown == 0:
                    lasers.append(Laser(self, self.pos, self.direction))
                    next_cd = max(0, SKILL_COOLDOWN_FRAMES - 120)
            elif cc == 'suisei':
                if self.skill_cooldown == 0:
                    self.apply_effect('shield', SKILL_DURATION_FRAMES + 240)
                    self.health = min(self.max_health, self.health + 35)
                    next_cd = max(0, SKILL_COOLDOWN_FRAMES - 120)
            elif cc == 'risto':
                if self.skill_cooldown == 0:
                    if enemy is not None:
                        for _ in range(16):  # buff: more bullets
                            rx = random.randint(int(enemy.pos.x - 120), int(enemy.pos.x + 120))
                            rx = max(20, min(WINDOW_WIDTH-20, rx))
                            spawn_y = max(10, int(enemy.pos.y - 300))
                            bullets.append(Bullet(rx, spawn_y, Vector2(0,1), self, damage=80))  # buff: more damage
                    next_cd = SKILL_COOLDOWN_FRAMES
            elif cc == 'miko':
                if self.skill_cooldown == 0:
                    domains.append(FireDomain(self, self.pos))
                    next_cd = SKILL_COOLDOWN_FRAMES - 120
            elif cc == 'kronii':
                if self.skill_cooldown == 0:
                    if self.rewind_history:
                        old_pos, old_hp = self.rewind_history[0]
                        self.pos = Vector2(old_pos.x, old_pos.y)
                        self.health = max(0, min(self.max_health, old_hp))
                        self.invuln_timer = max(self.invuln_timer, int(0.5 * FPS))
                        for _ in range(16):
                            particles.append(Particle(self.pos, Vector2(random.uniform(-3,3), random.uniform(-3,3)), 18, (160, 200, 255)))
                    next_cd = SKILL_COOLDOWN_FRAMES
            elif cc == 'moona':
                if self.skill_cooldown == 0:
                    self.meteor_shower_timer = int(2 * FPS)
                    self.meteor_shower_big_done = False
                    next_cd = SKILL_COOLDOWN_FRAMES
            elif cc in ('nakiri','ayame'):
                if self.skill_cooldown == 0:
                    # toggle sword mode: unlimited duration while active
                    self.sword_mode_timer = 4 * FPS
                    next_cd = SKILL_COOLDOWN_FRAMES
            elif cc == 'botan':
                if self.skill_cooldown == 0:
                    seq = ['rpg','sniper','dsmg']
                    if self.weapon_mode not in seq:
                        self.weapon_mode = seq[0]
                    else:
                        self.weapon_mode = seq[(seq.index(self.weapon_mode)+1) % len(seq)]
                    next_cd = int(SKILL_COOLDOWN_FRAMES * 0.5)
            elif cc == 'raora':
                if self.skill_cooldown == 0:
                    # spawn black hole at Raora's position
                    domains.append(BlackHole(self, Vector2(self.pos.x, self.pos.y)))
                    next_cd = SKILL_COOLDOWN_FRAMES
            elif cc == 'marine':
                # two-phase: first press board ship (speed buff), second press throw ship (AoE + cooldown)
                if self.marine_ship_primed:
                    blast_pos = self.pos + self.direction * 80
                    domains.append(PirateShipBlast(self, blast_pos, radius=160, lifetime_frames=int(0.35 * FPS)))
                    self.marine_ship_primed = False
                    next_cd = max(0, SKILL_COOLDOWN_FRAMES - 120)
                elif self.skill_cooldown == 0:
                    self.apply_effect('speed', int(2 * FPS))
                    self.marine_ship_primed = True
            else:
                if self.skill_cooldown == 0:
                    self.apply_effect('shield', SKILL_DURATION_FRAMES)
                    next_cd = SKILL_COOLDOWN_FRAMES
            if next_cd is not None:
                self.skill_cooldown = max(0, next_cd)
        # Raora charge handling: holding skill key charges to grow DOOM; released -> stop charge
        if self.char_class.lower() == 'raora':
            self.is_charging = skill_down

        self.skill_was_down = skill_down

        if getattr(self, 'sword_mode_timer', 0) > 0:
            self.sword_mode_timer -= 1

        # Shooting
        if keys[self.shoot_key] and current_frame - self.last_shot > self.shot_delay:
            # Bullet cap
            if len(bullets) >= MAX_BULLETS:
                pass
            else:
                bullet_pos = self.pos + self.direction * (self.radius + 5)
                # Ayame sword slash: dash strike instead of bullet (while sword mode active)
                if self.char_class.lower() in ('nakiri','ayame') and getattr(self, 'sword_mode_timer', 0) > 0:
                    slash_dist = 60
                    step = self.direction.normalize() * 12 if self.direction.length() > 0 else Vector2(12,0)
                    moved = 0
                    # spawn initial slash particles
                    for _ in range(8):
                        particles.append(Particle(self.pos, Vector2(random.uniform(-2,2), random.uniform(-2,2)), 14, (255, 220, 220)))
                    while moved < slash_dist:
                        candidate = self.pos + step
                        rect = pygame.Rect(candidate.x - self.radius, candidate.y - self.radius, PLAYER_SIZE, PLAYER_SIZE)
                        if any(rect.colliderect(w.rect) for w in walls):
                            break
                        self.pos = candidate
                        moved += step.length()
                        # trailing slash particles
                        particles.append(Particle(self.pos, Vector2(random.uniform(-1.5,1.5), random.uniform(-1.5,1.5)), 10, (255, 180, 180)))
                    if enemy is not None and (enemy.pos - self.pos).length() <= self.radius + 30:
                        if enemy.take_damage(30):
                            self.score += 1
                    self.last_shot = current_frame + 10
                elif self.char_class.lower() == 'botan':
                    if self.weapon_mode == 'Rpg':
                        # rate-limit RPG in 5s window
                        self.rocket_fire_times = [t for t in self.rocket_fire_times if current_frame - t <= ROCKET_WINDOW_FRAMES]
                        if len(self.rocket_fire_times) < ROCKET_MAX_PER_WINDOW:
                            rockets.append(Rocket(self, bullet_pos, self.direction))
                            self.rocket_fire_times.append(current_frame)
                        # reduce attack speed (slower follow-up)
                        self.last_shot = current_frame + 18
                    elif self.weapon_mode == 'Sniper':
                        # longer range: faster bullet so it travels farther than RPG
                        bullets.append(Bullet(bullet_pos.x, bullet_pos.y, self.direction, self, speed=14, damage=35))
                        # reduce attack speed for sniper
                        self.last_shot = current_frame + 12
                    elif self.weapon_mode == 'Dual Smg':
                        spread = 6
                        for side in (-1,1):
                            rad = math.radians(side * spread)
                            dir_rot = Vector2(
                                self.direction.x * math.cos(rad) - self.direction.y * math.sin(rad),
                                self.direction.x * math.sin(rad) + self.direction.y * math.cos(rad)
                            )
                            bullets.append(Bullet(bullet_pos.x, bullet_pos.y, dir_rot, self, damage=5))
                        self.last_shot = current_frame
                        self.shot_delay = max(4, int(self.base_shot_delay * 0.6))
                    else:
                        bullets.append(Bullet(bullet_pos.x, bullet_pos.y, self.direction, self))
                        self.last_shot = current_frame
                else:
                    if self.multishot <= 1:
                        bullets.append(Bullet(bullet_pos.x, bullet_pos.y, self.direction, self))
                    else:
                        spread = 10  # degrees
                        count = self.multishot
                        mid = (count - 1) / 2.0
                        for i in range(count):
                            angle_deg = (i - mid) * spread
                            rad = math.radians(angle_deg)
                            dir_rot = Vector2(
                                self.direction.x * math.cos(rad) - self.direction.y * math.sin(rad),
                                self.direction.x * math.sin(rad) + self.direction.y * math.cos(rad)
                            )
                            bullets.append(Bullet(bullet_pos.x, bullet_pos.y, dir_rot, self))
                    self.last_shot = current_frame

        if self.char_class.lower() == 'moona' and self.meteor_shower_timer > 0:
            self.meteor_shower_timer -= 1
            if self.meteor_shower_timer % 6 == 0:
                for _ in range(2):
                    tx = random.randint(40, WINDOW_WIDTH - 40)
                    ty = random.randint(40, WINDOW_HEIGHT - 40)
                    start_y = -40
                    meteors.append(Meteor(self, Vector2(tx, start_y), Vector2(tx, ty), speed=14, radius=18, damage=20, big=False))
            if self.meteor_shower_timer == 0 and not self.meteor_shower_big_done:
                if enemy is not None:
                    tx = enemy.pos.x
                    ty = enemy.pos.y
                else:
                    tx = WINDOW_WIDTH / 2
                    ty = WINDOW_HEIGHT / 2
                start_y = -80
                meteors.append(Meteor(self, Vector2(tx, start_y), Vector2(tx, ty), speed=18, radius=40, damage=9999, big=True))
                self.meteor_shower_big_done = True

        # Tick effects
        self.update_effects()
        self.anim_timer += 1

    def take_damage(self, damage):
        if self.respawn_timer > 0 or self.invuln_timer > 0:
            return
            
        # interrupt Raora charging when taking damage
        if self.char_class.lower() == 'raora':
            setattr(self, 'is_charging', False)
        
        self.health -= damage
        self.hit_flash_timer = 10
        if self.health <= 0:
            self.health = 0
            self.respawn_timer = RESPAWN_TIME
            return True  # Player died
        return False

    def respawn(self, walls):
        self.health = self.max_health
        self.marine_ship_primed = False
        self.invuln_timer = 60
        if hasattr(self, 'rewind_history'):
            self.rewind_history = []
            self.rewind_shadow_pos = None
        if hasattr(self, 'meteor_shower_timer'):
            self.meteor_shower_timer = 0
            self.meteor_shower_big_done = False
        # Try multiple times to find a non-colliding spot
        for _ in range(100):
            candidate = Vector2(
                random.randint(100, WINDOW_WIDTH - 100),
                random.randint(100, WINDOW_HEIGHT - 100)
            )
            rect = pygame.Rect(candidate.x - self.radius, candidate.y - self.radius, PLAYER_SIZE, PLAYER_SIZE)
            if not any(rect.colliderect(w.rect) for w in walls):
                self.pos = candidate
                return
        # Fallback: keep current pos if none found

    def draw(self, screen, highlight=False):
        if self.respawn_timer > 0:
            # Draw respawn timer
            text = font.render(f"Respawning... {self.respawn_timer//FPS + 1}", True, WHITE)
            screen.blit(text, (self.pos.x - text.get_width()//2, self.pos.y - 50))
            return
            
        # countdown timers
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
        if self.invuln_timer > 0:
            self.invuln_timer -= 1
        # also tick effects here to keep UI responsive
        self.update_effects()

        bob_amp = 2 if not self.is_moving else 3
        bob = math.sin(self.anim_timer * 0.2) * bob_amp
        draw_x = self.pos.x
        draw_y = self.pos.y + bob

        if self.char_class.lower() == 'kronii' and self.rewind_shadow_pos is not None:
            pygame.draw.circle(screen, (120, 200, 255), (int(self.rewind_shadow_pos.x), int(self.rewind_shadow_pos.y)), self.radius + 4, 2)

        # Draw player (sprite if available)
        if self.sprite_base is not None:
            angle = -math.degrees(math.atan2(self.direction.y, self.direction.x))
            self.sprite = pygame.transform.rotate(self.sprite_base, angle)
            rect = self.sprite.get_rect(center=(int(draw_x), int(draw_y)))
            screen.blit(self.sprite, rect.topleft)
        else:
            color = (255,255,255) if self.hit_flash_timer > 0 else self.color
            pygame.draw.circle(screen, color, (int(draw_x), int(draw_y)), self.radius)

        # Sword mode aura (Ayame/Nakiri)
        if self.char_class.lower() in ('nakiri','ayame') and getattr(self, 'sword_mode_timer', 0) > 0:
            pygame.draw.circle(screen, (255, 120, 120), (int(self.pos.x), int(self.pos.y)), self.radius + 6, 2)

        # Invuln blink overlay
        if self.invuln_timer > 0 and (self.invuln_timer // 5) % 2 == 0:
            pygame.draw.circle(screen, (255,255,255), (int(self.pos.x), int(self.pos.y)), self.radius, 2)

        # Owner highlight during time stop
        if highlight:
            pygame.draw.circle(screen, (255, 215, 0), (int(self.pos.x), int(self.pos.y)), self.radius + 4, 3)
        
        # Draw health bar (styled)
        bar_width = 52
        bar_h = 8
        bx = int(draw_x - bar_width//2)
        by = int(draw_y - self.radius - 18)
        pygame.draw.rect(screen, (30,30,30), (bx-2, by-2, bar_width+4, bar_h+4))
        pygame.draw.rect(screen, (90,90,90), (bx, by, bar_width, bar_h))
        max_hp = max(1, self.max_health)
        health_width = int((self.health / max_hp) * bar_width)
        pygame.draw.rect(screen, (40,190,40), (bx, by, max(0, health_width), bar_h))
        pygame.draw.rect(screen, (255,255,255), (bx, by, bar_width, bar_h), 1)
        
        # Draw direction indicator
        center_vec = Vector2(draw_x, draw_y)
        end_pos = center_vec + self.direction * (self.radius + 5)
        pygame.draw.line(screen, (255, 255, 0), center_vec, end_pos, 3)

    # Dash removed

    def move_safely(self, delta: Vector2, walls):
        # move in small steps, stop before hitting walls
        total = delta.length()
        if total == 0:
            return
        steps = max(1, int(total // 3))
        step_vec = delta / steps
        for _ in range(steps):
            candidate = self.pos + step_vec
            rect = pygame.Rect(candidate.x - self.radius, candidate.y - self.radius, PLAYER_SIZE, PLAYER_SIZE)
            if any(rect.colliderect(w.rect) for w in walls):
                break
            self.pos = candidate
        self.pos.x = max(self.radius, min(WINDOW_WIDTH - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(WINDOW_HEIGHT - self.radius, self.pos.y))
 
class Enemy:
    def __init__(self, x, y, is_boss=False):
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.is_boss = is_boss
        self.radius = 18 if not is_boss else 26  # Slightly smaller hitbox
        self.color = (200, 80, 80) if not is_boss else (255, 120, 160)
        self.max_health = 70 if not is_boss else 200  # Reduced health
        self.health = self.max_health
        self.speed = 2.0 if not is_boss else 2.5  # Slower movement
        self.contact_damage = 8 if not is_boss else 15  # Less damage on contact
        self.slow_factor = 0.25  # Weaker slow effect

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

    def update(self, players, walls):
        live_players = [p for p in players if p.respawn_timer == 0]
        if not live_players:
            return
            
        target = min(live_players, key=lambda p: (p.pos - self.pos).length())
        to_target = target.pos - self.pos
        desired = Vector2(0, 0)
        
        if to_target.length() > 0:
            desired = to_target.normalize() * self.speed
            
            # Check for walls in the path
            future_pos = self.pos + desired.normalize() * (self.radius * 1.5)
            future_rect = pygame.Rect(
                future_pos.x - self.radius, 
                future_pos.y - self.radius, 
                self.radius * 2, 
                self.radius * 2
            )
            
            # Find the closest wall in the movement direction
            closest_wall = None
            min_dist = float('inf')
            
            for w in walls:
                if future_rect.colliderect(w.rect):
                    # Calculate distance to wall
                    wall_center = Vector2(w.rect.centerx, w.rect.centery)
                    wall_dist = (wall_center - self.pos).length()
                    if wall_dist < min_dist:
                        min_dist = wall_dist
                        closest_wall = w
            
            # If we're about to hit a wall, adjust movement direction
            if closest_wall is not None:
                # Calculate normal vector from wall to enemy
                wall_center = Vector2(closest_wall.rect.centerx, closest_wall.rect.centery)
                wall_normal = (self.pos - wall_center).normalize()
                
                # Add a force away from the wall
                avoid_force = wall_normal * self.speed * 2.0
                desired = (desired + avoid_force).normalize() * self.speed
        
        # Smooth movement
        self.vel += (desired - self.vel) * 0.3
        if self.vel.length() > self.speed:
            self.vel = self.vel.normalize() * self.speed
        
        # Try to move in the desired direction
        new_pos = self.pos + self.vel
        
        # Check for collisions with walls
        rect = pygame.Rect(
            new_pos.x - self.radius, 
            new_pos.y - self.radius, 
            self.radius * 2, 
            self.radius * 2
        )
        
        # Only update position if not colliding with walls
        can_move = True
        for w in walls:
            if rect.colliderect(w.rect):
                can_move = False
                # Slide along the wall
                if abs(self.vel.x) > abs(self.vel.y):
                    self.vel.y *= 1.5  # Move more vertically
                    self.vel.x = 0
                else:
                    self.vel.x *= 1.5  # Move more horizontally
                    self.vel.y = 0
                break
                
        if can_move:
            self.pos = new_pos
        
        # Keep enemy within screen bounds
        self.pos.x = max(self.radius, min(WINDOW_WIDTH - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(WINDOW_HEIGHT - self.radius, self.pos.y))

        for p in live_players:
            if (p.pos - self.pos).length() <= self.radius + p.radius:
                p.take_damage(self.contact_damage)
                # knockback on contact
                kb_dir = (p.pos - self.pos)
                if kb_dir.length() > 0:
                    kb = kb_dir.normalize() * 12
                    p.move_safely(kb, walls)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
        bar_w = self.radius * 2 + 8
        bar_h = 6
        bx = int(self.pos.x - bar_w / 2)
        by = int(self.pos.y - self.radius - 10)
        pygame.draw.rect(screen, (30, 30, 30), (bx-1, by-1, bar_w+2, bar_h+2))
        pygame.draw.rect(screen, (90, 0, 0), (bx, by, bar_w, bar_h))
        ratio = 0 if self.max_health <= 0 else max(0.0, self.health / self.max_health)
        pygame.draw.rect(screen, (220, 80, 80), (bx, by, int(bar_w * ratio), bar_h))
        pygame.draw.rect(screen, (255, 255, 255), (bx, by, bar_w, bar_h), 1)


class Bullet:
    def __init__(self, x, y, direction, owner, speed=BULLET_SPEED, damage=10):
        self.pos = Vector2(x, y)
        self.direction = direction
        self.speed = speed
        self.lifetime = BULLET_LIFETIME
        self.owner = owner
        self.radius = BULLET_SIZE // 2
        self.bounces_left = BULLET_BOUNCES_MAX
        self.trail = []  # recent positions for trail
        self.damage = damage
        self.trail_surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.trail_surface, (255, 255, 0), (self.radius, self.radius), self.radius)
        
    def draw(self, screen):
        # trail
        alpha_steps = max(1, len(self.trail))
        for idx, p in enumerate(self.trail):
            fade = int(255 * (idx + 1) / (alpha_steps + 1))
            alpha = max(40, min(120, fade))
            self.trail_surface.set_alpha(alpha)
            screen.blit(self.trail_surface, (int(p.x - self.radius), int(p.y - self.radius)))
        # core
        pygame.draw.circle(screen, (255, 255, 0), (int(self.pos.x), int(self.pos.y)), self.radius)


class Wall:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        
    def draw(self, screen):
        outer = GRAY
        inner = (160, 160, 175)
        pygame.draw.rect(screen, outer, self.rect)
        inner_rect = self.rect.inflate(-4, -4)
        if inner_rect.width > 0 and inner_rect.height > 0:
            pygame.draw.rect(screen, inner, inner_rect)
        pygame.draw.rect(screen, (20, 20, 30), self.rect, 2)

class FireDomain:
    def __init__(self, owner, pos, radius=180, lifetime_frames=600, tick_interval=6):
        self.owner = owner
        self.pos = Vector2(pos.x, pos.y)
        self.radius = radius
        self.life = lifetime_frames
        self.tick_interval = tick_interval
        self.tick_counter = 0
        self.surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.surface, (255, 100, 60, 110), (self.radius, self.radius), self.radius)
        pygame.draw.circle(self.surface, (255, 140, 80), (self.radius, self.radius), self.radius, 5)
    def update(self):
        # follow owner so domain stays around the character
        self.pos.x = self.owner.pos.x
        self.pos.y = self.owner.pos.y
        self.life -= 1
        self.tick_counter = (self.tick_counter + 1) % self.tick_interval
        return self.life <= 0
    def ready_to_damage(self):
        return self.tick_counter == 0
    def draw(self, screen):
        screen.blit(self.surface, (int(self.pos.x - self.radius), int(self.pos.y - self.radius)))

class TimeZone:
    def __init__(self, owner, pos, radius=220, lifetime_frames=600, tick_interval=18):
        self.owner = owner
        self.pos = Vector2(pos.x, pos.y)
        self.radius = radius
        self.life = lifetime_frames
        self.tick_interval = tick_interval  # slightly faster ticks for more DPS
        self.tick_counter = 0
        self.surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.surface, (100, 170, 255, 100), (self.radius, self.radius), self.radius)
        pygame.draw.circle(self.surface, (160, 200, 255), (self.radius, self.radius), self.radius, 4)
    def update(self):
        # follow owner
        self.pos.x = self.owner.pos.x
        self.pos.y = self.owner.pos.y
        self.life -= 1
        self.tick_counter = (self.tick_counter + 1) % self.tick_interval
        return self.life <= 0
    def ready_to_damage(self):
        return self.tick_counter == 0
    def draw(self, screen):
        screen.blit(self.surface, (int(self.pos.x - self.radius), int(self.pos.y - self.radius)))

class BlackHole:
    def __init__(self, owner, pos, radius=220, lifetime_frames=540, tick_interval=10, pull_strength=2.8, growth_per_frame=0.22):
        self.owner = owner
        self.pos = Vector2(pos.x, pos.y)
        self.base_radius = radius
        self.radius = radius
        self.life = lifetime_frames
        self.tick_interval = tick_interval
        self.tick_counter = 0
        self.pull_strength = pull_strength
        self.growth_per_frame = growth_per_frame
        self.elapsed = 0
        self.doom_font = pygame.font.Font(None, 96)
        self.doom_text = self.doom_font.render('DOOM', True, (255, 60, 60))
    def update(self):
        self.life -= 1
        self.elapsed += 1
        # grow over time; charge no longer affects growth
        self.radius = int(self.base_radius + self.elapsed * self.growth_per_frame)
        self.tick_counter = (self.tick_counter + 1) % self.tick_interval
        return self.life <= 0
    def ready_to_damage(self):
        return self.tick_counter == 0
    def draw(self, screen):
        s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        # dark vortex that grows
        pygame.draw.circle(s, (30, 30, 30, 160), (self.radius, self.radius), self.radius)
        pygame.draw.circle(s, (0, 0, 0), (self.radius, self.radius), self.radius//2)
        screen.blit(s, (int(self.pos.x - self.radius), int(self.pos.y - self.radius)))
        # DOOM text
        doom = self.doom_text
        screen.blit(doom, (self.pos.x - doom.get_width()//2, self.pos.y - doom.get_height()//2))


class PirateShipBlast:
    def __init__(self, owner, pos, radius=150, lifetime_frames=18, tick_interval=6):
        self.owner = owner
        self.pos = Vector2(pos.x, pos.y)
        self.radius = radius
        self.life = lifetime_frames
        self.tick_interval = tick_interval
        self.tick_counter = 0
    def update(self):
        self.life -= 1
        self.tick_counter = (self.tick_counter + 1) % self.tick_interval
        return self.life <= 0
    def ready_to_damage(self):
        return self.tick_counter == 0
    def draw(self, screen):
        s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 220, 160, 140), (self.radius, self.radius), self.radius)
        pygame.draw.circle(s, (255, 180, 100), (self.radius, self.radius), self.radius, 4)
        screen.blit(s, (int(self.pos.x - self.radius), int(self.pos.y - self.radius)))

class Rocket:
    def __init__(self, owner, pos, direction, speed=7, radius=80, damage=35):
        self.owner = owner
        self.pos = Vector2(pos.x, pos.y)
        self.dir = direction.normalize() if direction.length() > 0 else Vector2(1,0)
        self.speed = speed
        self.radius = radius
        self.damage = damage
        self.life = 120
    def update(self):
        self.pos += self.dir * self.speed
        self.life -= 1
        out = not (0 <= self.pos.x <= WINDOW_WIDTH and 0 <= self.pos.y <= WINDOW_HEIGHT)
        return self.life <= 0 or out
    def explode(self, walls, players, particles):
        for pl in players:
            if pl is not self.owner and pl.respawn_timer == 0:
                if (pl.pos - self.pos).length() <= self.radius:
                    pl.take_damage(self.damage)
        for _ in range(20):
            particles.append(Particle(self.pos, Vector2(random.uniform(-4,4), random.uniform(-4,4)), 25, (255,200,120)))
    def explode_on_enemies(self, enemies, owner, particles):
        for e in enemies[:]:
            if (e.pos - self.pos).length() <= self.radius:
                if e.take_damage(self.damage):
                    if owner is not None:
                        if hasattr(owner, 'gain_exp'):
                            owner.gain_exp(22 if getattr(e, 'is_boss', False) else 8)
                    enemies.remove(e)
        for _ in range(20):
            particles.append(Particle(self.pos, Vector2(random.uniform(-4,4), random.uniform(-4,4)), 25, (255,200,120)))
    def draw(self, screen):
        pygame.draw.circle(screen, (250,150,80), (int(self.pos.x), int(self.pos.y)), 5)

class Meteor:
    def __init__(self, owner, pos, target_pos, speed=12, radius=26, damage=25, big=False):
        self.owner = owner
        self.pos = Vector2(pos.x, pos.y)
        self.target = Vector2(target_pos.x, target_pos.y)
        direction = self.target - self.pos
        self.dir = direction.normalize() if direction.length() > 0 else Vector2(0,1)
        self.speed = speed
        self.radius = radius
        self.damage = damage
        self.big = big
        self.life = 240
    def update(self):
        self.pos += self.dir * self.speed
        self.life -= 1
        reached = (self.dir.y >= 0 and self.pos.y >= self.target.y) or self.life <= 0
        return reached
    def explode(self, players, particles):
        for pl in players:
            if pl is not self.owner and pl.respawn_timer == 0:
                killed = False
                if self.big:
                    killed = pl.take_damage(self.damage)
                else:
                    if (pl.pos - self.pos).length() <= self.radius:
                        killed = pl.take_damage(self.damage)
                if killed:
                    if self.owner is players[0]:
                        players[0].score += 1
                    elif self.owner is players[1]:
                        players[1].score += 1
        color = (180, 160, 255) if not self.big else (255, 240, 200)
        count = 18 if not self.big else 40
        for _ in range(count):
            particles.append(Particle(self.pos, Vector2(random.uniform(-4,4), random.uniform(-4,4)), 25, color))
    def explode_on_enemies(self, enemies, owner, particles):
        for e in enemies[:]:
            killed = False
            if self.big:
                killed = e.take_damage(self.damage)
            else:
                if (e.pos - self.pos).length() <= self.radius:
                    killed = e.take_damage(self.damage)
            if killed:
                if owner is not None and hasattr(owner, 'gain_exp'):
                    owner.gain_exp(26 if getattr(e, 'is_boss', False) else 10)
                enemies.remove(e)
        color = (180, 160, 255) if not self.big else (255, 240, 200)
        count = 18 if not self.big else 40
        for _ in range(count):
            particles.append(Particle(self.pos, Vector2(random.uniform(-4,4), random.uniform(-4,4)), 25, color))
    def draw(self, screen):
        color = (150, 130, 255) if not self.big else (255, 220, 160)
        pygame.draw.circle(screen, color, (int(self.pos.x), int(self.pos.y)), self.radius)

class Laser:
    def __init__(self, owner, pos, direction):
        self.owner = owner
        self.pos = Vector2(pos.x, pos.y)
        self.dir = direction.normalize() if direction.length() > 0 else Vector2(1,0)
        self.life = 26  # buff: longer lasting beam
        self.width = 10   # buff: thicker beam
        self.end = self.compute_end()
        self.damage = 65  # buff: higher damage
    def compute_end(self):
        # raycast until wall or screen edge
        step = 12
        p = Vector2(self.pos.x, self.pos.y)
        while 0 <= p.x <= WINDOW_WIDTH and 0 <= p.y <= WINDOW_HEIGHT:
            p_next = p + self.dir * step
            # simple stop at edges
            if not (0 <= p_next.x <= WINDOW_WIDTH and 0 <= p_next.y <= WINDOW_HEIGHT):
                return p
            # cannot access walls here; end will be refined in collision by clipping
            p = p_next
        return p
    def update(self):
        self.life -= 1
        return self.life <= 0
    def draw(self, screen):
        # Proper laser beam draw
        pygame.draw.line(screen, (120,220,255), (int(self.pos.x), int(self.pos.y)), (int(self.end.x), int(self.end.y)), self.width)

def create_map():
    return create_map_preset('arena')

def create_map_preset(name):
    walls = []
    border = 20
    # Borders
    walls.append(Wall(0, 0, WINDOW_WIDTH, border))
    walls.append(Wall(0, WINDOW_HEIGHT - border, WINDOW_WIDTH, border))
    walls.append(Wall(0, 0, border, WINDOW_HEIGHT))
    walls.append(Wall(WINDOW_WIDTH - border, 0, border, WINDOW_HEIGHT))

    center_x = WINDOW_WIDTH // 2
    center_y = WINDOW_HEIGHT // 2
    cw = 20
    ch = 200

    if name == 'arena':
        walls.append(Wall(center_x - cw // 2, center_y - ch, cw, ch * 2))
        walls.append(Wall(center_x - ch, center_y - cw // 2, ch * 2, cw))
        p = 60; s = 80
        walls.append(Wall(p, p, s, cw))
        walls.append(Wall(WINDOW_WIDTH - p - s, p, s, cw))
        walls.append(Wall(p, WINDOW_HEIGHT - p - cw, s, cw))
        walls.append(Wall(WINDOW_WIDTH - p - s, WINDOW_HEIGHT - p - cw, s, cw))
        gap = 120; side_w = 20; seg = 200
        walls.append(Wall(border + 100, border + 0, side_w, seg))
        walls.append(Wall(border + 100, border + seg + gap, side_w, seg))
        walls.append(Wall(WINDOW_WIDTH - border - 100 - side_w, border + 0, side_w, seg))
        walls.append(Wall(WINDOW_WIDTH - border - 100 - side_w, border + seg + gap, side_w, seg))
        cover_w = 60; cover_h = 40; offset = 150
        walls.append(Wall(center_x - offset - cover_w, center_y - 100, cover_w, cover_h))
        walls.append(Wall(center_x + offset, center_y - 100, cover_w, cover_h))
        walls.append(Wall(center_x - offset - cover_w, center_y + 60, cover_w, cover_h))
        walls.append(Wall(center_x + offset, center_y + 60, cover_w, cover_h))
    elif name == 'crossfire':
        # Four central blocks and long corridors
        block = 120
        walls.append(Wall(center_x - block//2 - 160, center_y - block//2, block, 20))
        walls.append(Wall(center_x + 160 - block//2, center_y - block//2, block, 20))
        walls.append(Wall(center_x - block//2 - 160, center_y + block//2, block, 20))
        walls.append(Wall(center_x + 160 - block//2, center_y + block//2, block, 20))
        walls.append(Wall(border + 120, border + 80, 20, WINDOW_HEIGHT - 2*(border + 80)))
        walls.append(Wall(WINDOW_WIDTH - border - 140, border + 80, 20, WINDOW_HEIGHT - 2*(border + 80)))
    elif name == 'corridor':
        # Multiple horizontal corridors
        gap = 120
        for i in range(3):
            y = border + 150 + i*gap
            walls.append(Wall(border + 80, y, WINDOW_WIDTH - 2*(border + 80), 20))
        # openings
        walls.append(Wall(center_x - 200, border + 150, 100, 20))
        walls.append(Wall(center_x + 100, border + 270, 100, 20))
        walls.append(Wall(center_x - 200, border + 390, 100, 20))
    return walls

# Character selection
CHAR_CLASSES = ['Risto', 'Nerissa', 'Suisei', 'Miko', 'Botan', 'Kronii', 'Moona', 'Raora', 'Ayame', 'Marine']
CHAR_DESC = {
    'Risto': 'Skill: Bullet Rain ',
    'Nerissa': 'Skill: Laser Beam',
    'Suisei': 'Skill: Shield',
    'Miko': 'Skill: Fire Domain ',
    'Botan': 'Skill: Change Weapon' ,
    'Kronii': 'Skill: Rewind Time ',
    'Moona': 'Skill: Meteor Shower',
    'Raora': 'Skill: Black Hole',
    'Ayame': 'Skill: Sword Mode ',
    'Marine': 'Skill: Pirate Ship',
}

def draw_char_card(surface, title, char_name, x, y, selected=False):
    w, h = 280, 200
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill((0,0,0,190) if selected else (0,0,0,130))
    surface.blit(panel, (x, y))
    border_color = (255, 215, 0) if selected else (120, 120, 120)
    pygame.draw.rect(surface, border_color, (x, y, w, h), 2)
    t = font.render(title, True, WHITE)
    surface.blit(t, (x + 12, y + 10))
    cn = font.render(char_name, True, (255, 215, 0) if selected else WHITE)
    surface.blit(cn, (x + 12, y + 46))
    desc = CHAR_DESC.get(char_name, '')
    surface.blit(font.render(desc, True, (200,200,200)), (x + 12, y + 80))

    sprite = get_char_sprite_cached(char_name, 56, WHITE)
    s_rect = sprite.get_rect()
    s_rect.center = (x + w - 70, y + h//2 + 4)
    surface.blit(sprite, s_rect.topleft)


def character_select():
    p1_idx = 0
    p2_idx = 1
    info = font.render('P1: A/D to choose | P2: Left/Right | Enter to start | Esc to quit', True, WHITE)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None, None
                elif event.key == pygame.K_a:
                    p1_idx = (p1_idx - 1) % len(CHAR_CLASSES)
                elif event.key == pygame.K_d:
                    p1_idx = (p1_idx + 1) % len(CHAR_CLASSES)
                elif event.key == pygame.K_LEFT:
                    p2_idx = (p2_idx - 1) % len(CHAR_CLASSES)
                elif event.key == pygame.K_RIGHT:
                    p2_idx = (p2_idx + 1) % len(CHAR_CLASSES)
                elif event.key == pygame.K_RETURN:
                    return CHAR_CLASSES[p1_idx], CHAR_CLASSES[p2_idx]
        # draw
        screen.fill(BLACK)
        draw_background_grid(screen, gap=50, color=(30,30,30))
        title = font.render('Select Characters', True, (255, 215, 0))
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 60))
        screen.blit(info, (WINDOW_WIDTH//2 - info.get_width()//2, 100))
        draw_char_card(screen, 'Player 1', CHAR_CLASSES[p1_idx], WINDOW_WIDTH//2 - 320, 200, selected=True)
        draw_char_card(screen, 'Player 2', CHAR_CLASSES[p2_idx], WINDOW_WIDTH//2 + 60, 200, selected=True)
        pygame.display.flip()
        clock.tick(60)


def draw_ui(screen, player1, player2, paused=False, preset_name='arena'):
    # Panels
    draw_panel(screen, (10, 10, 300, 180))
    draw_panel(screen, (WINDOW_WIDTH - 310, 10, 300, 180))

    pygame.draw.rect(screen, (70, 120, 230), (10, 10, 300, 4))
    pygame.draw.rect(screen, (220, 70, 70), (WINDOW_WIDTH - 310, 10, 300, 4))

    # Player 1 (Blue) stats
    p1_text = font.render(f"P1: {player1.score}/{TARGET_SCORE}", True, BLUE)
    p1_health = font.render(f"HP: {int(player1.health)}/{player1.max_health}", True, BLUE)
    screen.blit(p1_text, (20, 20))
    screen.blit(p1_health, (20, 60))
    # EXP bar P1
    exp_ratio1 = 0.0 if player1.exp_to_next <= 0 else max(0.0, min(1.0, player1.exp / player1.exp_to_next))
    exp_bar_w = 180
    exp_bar_h = 6
    ex1 = 20
    ey1 = 90
    pygame.draw.rect(screen, (30,30,30), (ex1-1, ey1-1, exp_bar_w+2, exp_bar_h+2))
    pygame.draw.rect(screen, (40,40,70), (ex1, ey1, exp_bar_w, exp_bar_h))
    pygame.draw.rect(screen, (80, 180, 255), (ex1, ey1, int(exp_bar_w * exp_ratio1), exp_bar_h))
    lvl_text1 = font.render(f"Lv {player1.level}", True, BLUE)
    screen.blit(lvl_text1, (ex1 + exp_bar_w + 8, ey1 - 6))
    eff1 = player1.current_effect_label()
    if eff1:
        screen.blit(font.render(eff1, True, (255, 215, 0)), (20, 110))
    # Skill cooldown
    sk1 = player1.skill_cooldown / FPS
    skill1_text = f"Skill ({player1.char_class}): READY (G)" if player1.skill_cooldown == 0 else f"Skill ({player1.char_class}): {sk1:.1f}s"
    screen.blit(font.render(skill1_text, True, (180, 220, 255)), (20, 140))
    # Botan weapon display
    if player1.char_class.lower() == 'botan':
        screen.blit(font.render(f"Weapon: {player1.weapon_mode.upper()}", True, (255, 200, 120)), (20, 160))

    # Player 2 (Red) stats
    p2_text = font.render(f"P2: {player2.score}/{TARGET_SCORE}", True, RED)
    p2_health = font.render(f"HP: {int(player2.health)}/{player2.max_health}", True, RED)
    screen.blit(p2_text, (WINDOW_WIDTH - 300, 20))
    screen.blit(p2_health, (WINDOW_WIDTH - 300, 60))
    # EXP bar P2
    exp_ratio2 = 0.0 if player2.exp_to_next <= 0 else max(0.0, min(1.0, player2.exp / player2.exp_to_next))
    exp_bar_w2 = 180
    exp_bar_h2 = 6
    ex2 = WINDOW_WIDTH - 300
    ey2 = 90
    pygame.draw.rect(screen, (30,30,30), (ex2-1, ey2-1, exp_bar_w2+2, exp_bar_h2+2))
    pygame.draw.rect(screen, (40,40,70), (ex2, ey2, exp_bar_w2, exp_bar_h2))
    pygame.draw.rect(screen, (255, 160, 120), (ex2, ey2, int(exp_bar_w2 * exp_ratio2), exp_bar_h2))
    lvl_text2 = font.render(f"Lv {player2.level}", True, RED)
    screen.blit(lvl_text2, (ex2 + exp_bar_w2 + 8, ey2 - 6))
    eff2 = player2.current_effect_label()
    if eff2:
        screen.blit(font.render(eff2, True, (255, 215, 0)), (WINDOW_WIDTH - 300, 110))
    sk2 = player2.skill_cooldown / FPS
    skill2_text = f"Skill ({player2.char_class}): READY (ENTER)" if player2.skill_cooldown == 0 else f"Skill ({player2.char_class}): {sk2:.1f}s"
    screen.blit(font.render(skill2_text, True, (180, 220, 255)), (WINDOW_WIDTH - 300, 140))
    if player2.char_class.lower() == 'botan':
        screen.blit(font.render(f"Weapon: {player2.weapon_mode.upper()}", True, (255, 200, 120)), (WINDOW_WIDTH - 300, 160))

    p1_sprite = get_char_sprite_cached(player1.char_class, 44, BLUE)
    p1_rect = p1_sprite.get_rect()
    p1_rect.center = (10 + 300 - 58, 10 + 110)
    screen.blit(p1_sprite, p1_rect.topleft)

    p2_sprite = get_char_sprite_cached(player2.char_class, 44, RED)
    p2_rect = p2_sprite.get_rect()
    p2_rect.center = (WINDOW_WIDTH - 310 + 58, 10 + 110)
    screen.blit(p2_sprite, p2_rect.topleft)

    # Help/preset
    help_text = font.render(f"[P] Pause  [R] Restart  [F1/F2/F3] Map ({preset_name})", True, WHITE)
    screen.blit(help_text, (WINDOW_WIDTH//2 - help_text.get_width()//2, 10))
    if paused:
        paused_t = font.render("PAUSED", True, (255, 215, 0))
        screen.blit(paused_t, (WINDOW_WIDTH//2 - paused_t.get_width()//2, 40))

def vs_main():
    # Character select UI
    p1_class, p2_class = character_select()
    if p1_class is None or p2_class is None:
        return False

    # Game objects
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    p1_path = os.path.join(assets_dir, 'p1.png')
    p2_path = os.path.join(assets_dir, 'p2.png')
    preset_name = 'arena'
    player1 = Player(200, 300, BLUE, [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d], pygame.K_f, p1_path, dash_key=pygame.K_LSHIFT, skill_key=pygame.K_g, char_class=p1_class)
    player2 = Player(800, 300, RED, [pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT], pygame.K_RSHIFT, p2_path, dash_key=pygame.K_RCTRL, skill_key=pygame.K_RETURN, char_class=p2_class)
    walls = create_map_preset(preset_name)
    bullets = []
    lasers = []
    rockets = []
    meteors = []
    domains = []
    particles = []
    frame_count = 0
    paused = False
    winner = None
    shake_timer = 0
    shake_mag = 6

    # Lucky boxes removed

    # Ensure initial positions are safe
    p1_rect = pygame.Rect(player1.pos.x - player1.radius, player1.pos.y - player1.radius, PLAYER_SIZE, PLAYER_SIZE)
    p2_rect = pygame.Rect(player2.pos.x - player2.radius, player2.pos.y - player2.radius, PLAYER_SIZE, PLAYER_SIZE)
    if any(p1_rect.colliderect(w.rect) for w in walls):
        player1.respawn(walls)
    if any(p2_rect.colliderect(w.rect) for w in walls):
        player2.respawn(walls)
    
    # Game loop
    running = True
    while running:
        frame_count += 1
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_r:
                    # restart
                    bullets.clear()
                    particles.clear()
                    player1.score = player2.score = 0
                    player1.respawn(walls); player2.respawn(walls)
                    winner = None
                elif event.key in (pygame.K_F1, pygame.K_F2, pygame.K_F3):
                    # change map preset
                    if event.key == pygame.K_F1:
                        preset_name = 'arena'
                    elif event.key == pygame.K_F2:
                        preset_name = 'crossfire'
                    else:
                        preset_name = 'corridor'
                    walls = create_map_preset(preset_name)
                    bullets.clear(); particles.clear();
                    player1.respawn(walls); player2.respawn(walls)
        
        # Update
        if winner is None and not paused:
            player1.update(walls, bullets, lasers, rockets, meteors, particles, domains, player2, frame_count)
            player2.update(walls, bullets, lasers, rockets, meteors, particles, domains, player1, frame_count)

        # (Lucky Box removed)
        
        # Update lasers
        if winner is None and not paused:
            lasers[:] = [l for l in lasers if not l.update()]
            # laser collision with players and walls (clip by walls approx)
            for l in lasers:
                for player in [player1, player2]:
                    if player is not l.owner and player.respawn_timer == 0:
                        # distance from point to segment
                        ax, ay = l.pos.x, l.pos.y
                        bx, by = l.end.x, l.end.y
                        px, py = player.pos.x, player.pos.y
                        abx, aby = bx-ax, by-ay
                        apx, apy = px-ax, py-ay
                        ab_len2 = abx*abx + aby*aby
                        t = 0 if ab_len2 == 0 else max(0, min(1, (apx*abx + apy*aby)/ab_len2))
                        cx, cy = ax + abx*t, ay + aby*t
                        dist = math.hypot(px - cx, py - cy)
                        if dist <= player.radius + max(3, l.width/2):
                            if player.take_damage(l.damage):
                                if l.owner == player1:
                                    player1.score += 1
                                else:
                                    player2.score += 1
                            for _ in range(10):
                                particles.append(Particle(player.pos, Vector2(random.uniform(-3,3), random.uniform(-3,3)), 15, (120,220,255)))
        # Update domains (Miko fire, Kronii time zone, Raora black hole, Marine ship)
        if winner is None and not paused:
            domains[:] = [d for d in domains if not d.update()]
            for d in domains:
                for player in [player1, player2]:
                    if player is not d.owner and player.respawn_timer == 0:
                        if (player.pos - d.pos).length() <= d.radius:
                            # Miko's FireDomain damage (buffed)
                            if isinstance(d, FireDomain):
                                if d.ready_to_damage():
                                    if player.take_damage(3):
                                        if d.owner == player1:
                                            player1.score += 1
                                        else:
                                            player2.score += 1
                            # Kronii's TimeZone: apply slow and higher DPS (buffed)
                            elif isinstance(d, TimeZone):
                                player.apply_effect('time_slow', 5)
                                if d.ready_to_damage():
                                    if player.take_damage(2):
                                        if d.owner == player1:
                                            player1.score += 1
                                        else:
                                            player2.score += 1
                            # Marine's PirateShipBlast: short AoE burst + knockback
                            elif isinstance(d, PirateShipBlast):
                                if d.ready_to_damage():
                                    kb_dir = (player.pos - d.pos)
                                    if kb_dir.length() > 0:
                                        kb = kb_dir.normalize() * 18
                                        player.move_safely(kb, walls)
                                    if player.take_damage(18):
                                        if d.owner == player1:
                                            player1.score += 1
                                        else:
                                            player2.score += 1
                                    for _ in range(10):
                                        particles.append(Particle(player.pos, Vector2(random.uniform(-3,3), random.uniform(-3,3)), 16, (255, 220, 160)))
                            # Raora's BlackHole: pull inward + stronger scaling damage over time
                            elif isinstance(d, BlackHole):
                                # pull toward center with gentler strength
                                dirv = (d.pos - player.pos)
                                dist = dirv.length()
                                if dist > 0:
                                    # pull toward center with gentler strength
                                    dirv = (d.pos - player.pos)
                                    dist = dirv.length()
                                    if dist > 0:
                                        norm = dirv.normalize()
                                        # reduced base pull, softer scaling by proximity
                                        proximity = max(0.0, (d.radius - dist) / max(1.0, d.radius))
                                        pull_scale = d.pull_strength * (0.4 + proximity * 0.6)
                                        step = norm * pull_scale
                                        player.move_safely(step, walls)
                                    # damage scales with time AND proximity to center (buffed)
                                    if d.ready_to_damage():
                                        time_bonus = max(0, d.elapsed // 120)
                                        center_bonus = 0
                                        if dist >= 0:
                                            # higher damage the closer you are to the center
                                            center_bonus = int(max(0.0, (d.radius - dist) / max(1.0, d.radius) * 5))
                                        # buff: higher base damage + stronger center scaling
                                        dmg = 3 + time_bonus + center_bonus
                                        if player.take_damage(dmg):
                                            if d.owner == player1:
                                                player1.score += 1
                                            else:
                                                player2.score += 1
                                    norm = dirv.normalize()
                                    # reduced base pull, softer scaling by proximity
                                    proximity = max(0.0, (d.radius - dist) / max(1.0, d.radius))
                                    pull_scale = d.pull_strength * (0.4 + proximity * 0.6)
                                    step = norm * pull_scale
                                    player.move_safely(step, walls)
                                # damage scales with time AND proximity to center (unchanged)
                                if d.ready_to_damage():
                                    time_bonus = max(0, d.elapsed // 120)
                                    center_bonus = 0
                                    if dist >= 0:
                                        # higher damage the closer you are to the center
                                        center_bonus = int(max(0.0, (d.radius - dist) / max(1.0, d.radius) * 3))
                                    # buff: higher base damage + stronger center scaling
                                    dmg = 2 + time_bonus + center_bonus
                                    if player.take_damage(dmg):
                                        if d.owner == player1:
                                            player1.score += 1
                                        else:
                                            player2.score += 1
        
        # Update rockets (RPG explodes on walls and players)
        if winner is None and not paused:
            r_to_remove = []
            for i, r in enumerate(rockets):
                if r.update():
                    # check collision with walls; explode on wall
                    rrect = pygame.Rect(r.pos.x-3, r.pos.y-3, 6, 6)
                    if any(rrect.colliderect(w.rect) for w in walls):
                        r.explode(walls, [player1, player2], particles)
                    r_to_remove.append(i)
                    continue
                # explode on player proximity
                for pl in [player1, player2]:
                    if pl is not r.owner and (pl.pos - r.pos).length() <= pl.radius + 6:
                        r.explode(walls, [player1, player2], particles)
                        r_to_remove.append(i)
                        break
            for i in sorted(r_to_remove, reverse=True):
                if i < len(rockets):
                    rockets.pop(i)

        if winner is None and not paused:
            m_to_remove = []
            for i, m in enumerate(meteors):
                if m.update():
                    m.explode([player1, player2], particles)
                    m_to_remove.append(i)
            for i in sorted(m_to_remove, reverse=True):
                if i < len(meteors):
                    meteors.pop(i)

        # Update bullets dan collision
        bullets_to_remove = []
        if winner is None and not paused:
            for i, bullet in enumerate(bullets):
                # Manual move to support bouncing
                prev_pos = bullet.pos.copy()
                bullet.pos += bullet.direction * bullet.speed
                bullet.lifetime -= 1
                # trail update
                bullet.trail.append(prev_pos)
                if len(bullet.trail) > 6:
                    bullet.trail.pop(0)

                # Lifetime or out-of-bounds cleanup
                if bullet.lifetime <= 0 or not (0 <= bullet.pos.x <= WINDOW_WIDTH and 0 <= bullet.pos.y <= WINDOW_HEIGHT):
                    bullets_to_remove.append(i)
                    continue
                
                # Bullet collision with walls (bounce)
                bullet_rect = pygame.Rect(
                    bullet.pos.x - bullet.radius,
                    bullet.pos.y - bullet.radius,
                    BULLET_SIZE, BULLET_SIZE
                )
                collided = False
                for wall in walls:
                    if bullet_rect.colliderect(wall.rect):
                        collided = True
                        # particles on bounce
                        for _ in range(4):
                            particles.append(Particle(bullet.pos, Vector2(random.uniform(-2,2), random.uniform(-2,2)), 20, (255,230,120)))
                        if bullet.bounces_left > 0:
                            # Minimal penetration axis resolution
                            dx_left = abs((bullet_rect.right) - wall.rect.left)
                            dx_right = abs((wall.rect.right) - bullet_rect.left)
                            dy_top = abs((bullet_rect.bottom) - wall.rect.top)
                            dy_bottom = abs((wall.rect.bottom) - bullet_rect.top)
                            min_pen = min(dx_left, dx_right, dy_top, dy_bottom)

                            if min_pen == dx_left:
                                # hit left side of wall -> reflect x negative
                                bullet.direction.x *= -1
                                bullet.pos.x = wall.rect.left - bullet.radius - 0.01
                            elif min_pen == dx_right:
                                # hit right side -> reflect x positive
                                bullet.direction.x *= -1
                                bullet.pos.x = wall.rect.right + bullet.radius + 0.01
                            elif min_pen == dy_top:
                                # hit top -> reflect y negative
                                bullet.direction.y *= -1
                                bullet.pos.y = wall.rect.top - bullet.radius - 0.01
                            else:
                                # hit bottom -> reflect y positive
                                bullet.direction.y *= -1
                                bullet.pos.y = wall.rect.bottom + bullet.radius + 0.01

                            # Normalize direction to avoid drift
                            if bullet.direction.length() != 0:
                                bullet.direction = bullet.direction.normalize()
                            bullet.bounces_left -= 1
                        else:
                            bullets_to_remove.append(i)
                        break
                if collided:
                    continue
                
                # Bullet collision with players
                for player in [player1, player2]:
                    if player is not bullet.owner and player.respawn_timer == 0:
                        # Ayame sword mode: parry normal bullets instead of taking damage
                        if player.char_class.lower() in ('nakiri','ayame') and getattr(player, 'sword_mode_timer', 0) > 0:
                            # deflect bullet away
                            away = (bullet.pos - player.pos)
                            if away.length() > 0:
                                bullet.direction = away.normalize()
                            # small spark particles
                            for _ in range(6):
                                particles.append(Particle(player.pos, Vector2(random.uniform(-2,2), random.uniform(-2,2)), 12, (255,255,255)))
                            continue
                        distance = (bullet.pos - player.pos).length()
                        if distance < player.radius + bullet.radius:
                            if player.take_damage(bullet.damage):
                                if bullet.owner == player1:
                                    player1.score += 1
                                else:
                                    player2.score += 1
                                shake_timer = max(shake_timer, 10)
                            # hit particles for better feedback
                            for _ in range(10):
                                particles.append(Particle(player.pos, Vector2(random.uniform(-3,3), random.uniform(-3,3)), 18, (255, 230, 200)))
                            # knockback (safe)
                            kb = bullet.direction * 6
                            player.move_safely(kb, walls)
                            if i not in bullets_to_remove:
                                bullets_to_remove.append(i)
                            break
        
        # Remove bullets that hit something or timed out
        for i in sorted(bullets_to_remove, reverse=True):
            if i < len(bullets):
                bullets.pop(i)

        # Update particles
        if not paused:
            particles[:] = [p for p in particles if not p.update()]
            if len(particles) > 400:
                del particles[:len(particles)-400]
        
        # Draw
        screen.fill(BLACK)
        draw_background_grid(screen, gap=50, color=(30,30,30))
        
        # Draw walls
        for wall in walls:
            wall.draw(screen)
        
        # Draw bullets
        for bullet in bullets:
            bullet.draw(screen)
        # Draw lasers
        for l in lasers:
            l.draw(screen)
        # Draw rockets
        for r in rockets:
            r.draw(screen)
        for m in meteors:
            m.draw(screen)
        # Draw fire domains
        for d in domains:
            d.draw(screen)
        # Draw particles (after bullets, before players)
        for p in particles:
            p.draw(screen)
        
        # Draw players
        player1.draw(screen)
        player2.draw(screen)
        
        # Draw UI
        draw_ui(screen, player1, player2, paused=paused, preset_name=preset_name)

        # (no Lucky Box)

        # End match when someone reaches target score: return to mode select
        if player1.score >= TARGET_SCORE or player2.score >= TARGET_SCORE:
            return True

        # Winner banner (unused, winner is never set)
        if winner is not None:
            banner = font.render(f"{winner} WINS! Press R to restart", True, (255, 215, 0))
            screen.blit(banner, (WINDOW_WIDTH//2 - banner.get_width()//2, WINDOW_HEIGHT//2 - 20))
        
        pygame.display.flip()
        clock.tick(FPS)


def is_position_valid(pos, radius, walls):
    # Check if position is within screen bounds
    if (pos.x < radius or pos.x > WINDOW_WIDTH - radius or 
        pos.y < radius or pos.y > WINDOW_HEIGHT - radius):
        return False
    
    # Check collision with walls
    test_rect = pygame.Rect(
        pos.x - radius,
        pos.y - radius,
        radius * 2,
        radius * 2
    )
    
    for wall in walls:
        if test_rect.colliderect(wall.rect):
            return False
    return True

def get_valid_spawn_position(radius, walls, max_attempts=50):
    for _ in range(max_attempts):
        # Try to spawn near walls more often (more interesting gameplay)
        if random.random() < 0.7:  # 70% chance to spawn near edges
            side = random.choice(['top', 'right', 'bottom', 'left'])
            if side == 'top':
                x = random.randint(radius, WINDOW_WIDTH - radius)
                y = radius + 10
            elif side == 'right':
                x = WINDOW_WIDTH - radius - 10
                y = random.randint(radius, WINDOW_HEIGHT - radius)
            elif side == 'bottom':
                x = random.randint(radius, WINDOW_WIDTH - radius)
                y = WINDOW_HEIGHT - radius - 10
            else:  # left
                x = radius + 10
                y = random.randint(radius, WINDOW_HEIGHT - radius)
        else:  # 30% chance to spawn randomly
            x = random.randint(radius, WINDOW_WIDTH - radius)
            y = random.randint(radius, WINDOW_HEIGHT - radius)
            
        pos = Vector2(x, y)
        if is_position_valid(pos, radius, walls):
            return pos
    
    # If no valid position found after max attempts, return a safe default
    return Vector2(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

def spawn_campaign_wave(wave_index, enemies, walls):
    enemies.clear()
    # Fewer enemies per wave
    num_enemies = min(3 + wave_index, 12)  # Reduced max enemies
    boss_wave = (wave_index % 5 == 0)
    
    # Only one boss per boss wave
    boss_count = 1 if boss_wave else 0
    
    for _ in range(num_enemies):
        is_boss = (boss_wave and _ < boss_count)
        
        if is_boss:
            boss_pos = get_valid_spawn_position(26, walls)
            boss = Enemy(boss_pos.x, boss_pos.y, is_boss=True)
            # Slightly scale boss stats with wave index
            if wave_index > 5:
                boss.max_health = int(boss.max_health * (1 + (wave_index - 5) * 0.05))
                boss.health = boss.max_health
            enemies.append(boss)
        else:
            enemy_pos = get_valid_spawn_position(18, walls)
            enemy = Enemy(enemy_pos.x, enemy_pos.y, is_boss=False)
            # Slower scaling for regular enemies
            if wave_index > 5:
                enemy.max_health = int(enemy.max_health * (1 + (wave_index - 5) * 0.04))
                enemy.health = enemy.max_health
                enemy.speed *= 1.05
            enemies.append(enemy)

    # Only add final boss every 3 waves starting from wave 6
    if wave_index >= 6 and wave_index % 3 == 0:
        bx = WINDOW_WIDTH // 2
        by = -80
        final_boss = Enemy(bx, by, is_boss=True)
        # Less aggressive scaling for final boss
        final_boss.max_health = int(final_boss.max_health * (1 + (wave_index // 3) * 0.1))
        final_boss.health = final_boss.max_health
        enemies.append(final_boss)


def campaign_main():
    p1_class, p2_class = character_select()
    if p1_class is None or p2_class is None:
        return False

    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    p1_path = os.path.join(assets_dir, 'p1.png')
    p2_path = os.path.join(assets_dir, 'p2.png')
    preset_name = 'arena'
    player1 = Player(200, 300, BLUE, [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d], pygame.K_f, p1_path, dash_key=pygame.K_LSHIFT, skill_key=pygame.K_g, char_class=p1_class)
    player2 = Player(800, 300, RED, [pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT], pygame.K_RSHIFT, p2_path, dash_key=pygame.K_RCTRL, skill_key=pygame.K_RETURN, char_class=p2_class)
    walls = create_map_preset(preset_name)
    bullets = []
    lasers = []
    rockets = []
    meteors = []
    domains = []
    particles = []
    enemies = []
    frame_count = 0
    paused = False
    wave_index = 1
    max_waves = 5
    spawn_campaign_wave(wave_index, enemies, walls)
    levelup_menu = False
    levelup_player_index = None

    running = True
    while running:
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if levelup_menu:
                    if event.key in (pygame.K_1, pygame.K_KP1):
                        choice = 0
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        choice = 1
                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        choice = 2
                    else:
                        choice = None
                    if choice is not None:
                        pl = player1 if levelup_player_index == 0 else player2
                        pl.apply_level_upgrade(choice)
                        levelup_menu = False
                        levelup_player_index = None
                else:
                    if event.key == pygame.K_ESCAPE:
                        return False
                    elif event.key == pygame.K_p:
                        paused = not paused

        if not paused and not levelup_menu:
            primary_enemy = enemies[0] if enemies else None
            player1.update(walls, bullets, lasers, rockets, meteors, particles, domains, primary_enemy, frame_count)
            player2.update(walls, bullets, lasers, rockets, meteors, particles, domains, primary_enemy, frame_count)

            for e in enemies:
                e.update([player1, player2], walls)

            if not enemies and wave_index < max_waves:
                wave_index += 1
                spawn_campaign_wave(wave_index, enemies, walls)
            elif not enemies and wave_index == max_waves:
                return True

            # Rockets (Botan RPG) vs enemies
            r_to_remove = []
            for i, r in enumerate(rockets):
                if r.update():
                    r.explode_on_enemies(enemies, r.owner, particles)
                    r_to_remove.append(i)
                    continue
                rrect = pygame.Rect(r.pos.x - 3, r.pos.y - 3, 6, 6)
                if any(rrect.colliderect(w.rect) for w in walls):
                    r.explode_on_enemies(enemies, r.owner, particles)
                    r_to_remove.append(i)
                    continue
                hit_enemy = False
                for enemy in enemies:
                    if (enemy.pos - r.pos).length() <= enemy.radius + 6:
                        r.explode_on_enemies(enemies, r.owner, particles)
                        r_to_remove.append(i)
                        hit_enemy = True
                        break
                if hit_enemy:
                    continue
            for i in sorted(r_to_remove, reverse=True):
                if i < len(rockets):
                    rockets.pop(i)

            # Meteors (Moona) vs enemies
            m_to_remove = []
            for i, m in enumerate(meteors):
                if m.update():
                    m.explode_on_enemies(enemies, m.owner, particles)
                    m_to_remove.append(i)
            for i in sorted(m_to_remove, reverse=True):
                if i < len(meteors):
                    meteors.pop(i)

            # Lasers (Nerissa) vs enemies
            lasers[:] = [l for l in lasers if not l.update()]
            for l in lasers:
                for enemy in enemies[:]:
                    ax, ay = l.pos.x, l.pos.y
                    bx, by = l.end.x, l.end.y
                    px, py = enemy.pos.x, enemy.pos.y
                    abx, aby = bx - ax, by - ay
                    apx, apy = px - ax, py - ay
                    ab_len2 = abx * abx + aby * aby
                    t = 0 if ab_len2 == 0 else max(0, min(1, (apx * abx + apy * aby) / ab_len2))
                    cx, cy = ax + abx * t, ay + aby * t
                    dist = math.hypot(px - cx, py - cy)
                    if dist <= enemy.radius + max(3, l.width / 2):
                        if enemy.take_damage(l.damage):
                            owner = l.owner
                            if owner is player1:
                                player1.gain_exp(20 if enemy.is_boss else 8)
                            elif owner is player2:
                                player2.gain_exp(20 if enemy.is_boss else 8)
                            enemies.remove(enemy)
                        for _ in range(8):
                            particles.append(Particle(enemy.pos, Vector2(random.uniform(-3, 3), random.uniform(-3, 3)), 15, (120, 220, 255)))

            # Bullets vs enemies
            bullets_to_remove = []
            enemies_to_remove = []
            for i, bullet in enumerate(bullets):
                prev_pos = bullet.pos.copy()
                bullet.pos += bullet.direction * bullet.speed
                bullet.lifetime -= 1
                bullet.trail.append(prev_pos)
                if len(bullet.trail) > 6:
                    bullet.trail.pop(0)

                if bullet.lifetime <= 0 or not (0 <= bullet.pos.x <= WINDOW_WIDTH and 0 <= bullet.pos.y <= WINDOW_HEIGHT):
                    bullets_to_remove.append(i)
                    continue

                bullet_rect = pygame.Rect(
                    bullet.pos.x - bullet.radius,
                    bullet.pos.y - bullet.radius,
                    BULLET_SIZE, BULLET_SIZE
                )
                collided = False
                for wall in walls:
                    if bullet_rect.colliderect(wall.rect):
                        collided = True
                        for _ in range(3):
                            particles.append(Particle(bullet.pos, Vector2(random.uniform(-2, 2), random.uniform(-2, 2)), 18, (255, 230, 120)))
                        bullets_to_remove.append(i)
                        break
                if collided:
                    continue

                for enemy in enemies:
                    if (bullet.pos - enemy.pos).length() <= bullet.radius + enemy.radius:
                        if enemy.take_damage(bullet.damage):
                            owner = bullet.owner
                            if owner is player1:
                                player1.gain_exp(18 if enemy.is_boss else 6)
                            elif owner is player2:
                                player2.gain_exp(18 if enemy.is_boss else 6)
                            enemies_to_remove.append(enemy)
                        for _ in range(8):
                            particles.append(Particle(enemy.pos, Vector2(random.uniform(-3, 3), random.uniform(-3, 3)), 18, (255, 230, 200)))
                        if i not in bullets_to_remove:
                            bullets_to_remove.append(i)
                        break

            for i in sorted(bullets_to_remove, reverse=True):
                if i < len(bullets):
                    bullets.pop(i)
            if enemies_to_remove:
                enemies = [e for e in enemies if e not in enemies_to_remove]

            # Domains (Miko, Kronii, Raora, Marine ship) vs enemies
            domains[:] = [d for d in domains if not d.update()]
            for d in domains:
                for enemy in enemies[:]:
                    if (enemy.pos - d.pos).length() <= d.radius:
                        if isinstance(d, FireDomain):
                            if d.ready_to_damage():
                                if enemy.take_damage(3):
                                    owner = d.owner
                                    if owner is player1:
                                        player1.gain_exp(12 if enemy.is_boss else 5)
                                    elif owner is player2:
                                        player2.gain_exp(12 if enemy.is_boss else 5)
                                    enemies.remove(enemy)
                        elif isinstance(d, TimeZone):
                            if d.ready_to_damage():
                                if enemy.take_damage(2):
                                    owner = d.owner
                                    if owner is player1:
                                        player1.gain_exp(10 if enemy.is_boss else 4)
                                    elif owner is player2:
                                        player2.gain_exp(10 if enemy.is_boss else 4)
                                    enemies.remove(enemy)
                        elif isinstance(d, PirateShipBlast):
                            if d.ready_to_damage():
                                kb_dir = (enemy.pos - d.pos)
                                if kb_dir.length() > 0:
                                    kb = kb_dir.normalize() * 10
                                    enemy.pos += kb
                                if enemy.take_damage(24):
                                    owner = d.owner
                                    if owner is player1:
                                        player1.gain_exp(22 if enemy.is_boss else 9)
                                    elif owner is player2:
                                        player2.gain_exp(22 if enemy.is_boss else 9)
                                    enemies.remove(enemy)
                        elif isinstance(d, BlackHole):
                            dirv = (d.pos - enemy.pos)
                            dist = dirv.length()
                            if dist > 0:
                                norm = dirv.normalize()
                                proximity = max(0.0, (d.radius - dist) / max(1.0, d.radius))
                                pull_scale = d.pull_strength * (0.4 + proximity * 0.6)
                                enemy.pos += norm * pull_scale
                            if d.ready_to_damage():
                                time_bonus = max(0, d.elapsed // 120)
                                center_bonus = 0
                                if dist >= 0:
                                    center_bonus = int(max(0.0, (d.radius - dist) / max(1.0, d.radius) * 5))
                                dmg = 3 + time_bonus + center_bonus
                                if enemy.take_damage(dmg):
                                    owner = d.owner
                                    if owner is player1:
                                        player1.gain_exp(24 if enemy.is_boss else 10)
                                    elif owner is player2:
                                        player2.gain_exp(24 if enemy.is_boss else 10)
                                    enemies.remove(enemy)

            # Particles + levelup trigger
            particles[:] = [p for p in particles if not p.update()]
            if len(particles) > 400:
                del particles[:len(particles) - 400]

            for pl in (player1, player2):
                if not levelup_menu and pl.pending_levelups > 0:
                    pl.pending_levelups -= 1
                    levelup_menu = True
                    levelup_player_index = 0 if pl is player1 else 1
                    break

        screen.fill(BLACK)
        draw_background_grid(screen, gap=50, color=(30, 30, 30))
        for wall in walls:
            wall.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        for l in lasers:
            l.draw(screen)
        for r in rockets:
            r.draw(screen)
        for m in meteors:
            m.draw(screen)
        for d in domains:
            d.draw(screen)
        for p in particles:
            p.draw(screen)

        player1.draw(screen)
        player2.draw(screen)

        draw_ui(screen, player1, player2, paused=paused, preset_name=f"Wave {wave_index}/{max_waves}")

        if levelup_menu:
            pl = player1 if levelup_player_index == 0 else player2
            panel_w, panel_h = 520, 200
            px = WINDOW_WIDTH // 2 - panel_w // 2
            py = WINDOW_HEIGHT // 2 - panel_h // 2
            draw_panel(screen, (px, py, panel_w, panel_h))
            title = font.render(f"LEVEL UP - P{levelup_player_index + 1} (Lv {pl.level})", True, (255, 215, 0))
            screen.blit(title, (px + 20, py + 20))
            opt1 = font.render("[1] Speed Up", True, WHITE)
            opt2 = font.render("[2] Attack Speed Up", True, WHITE)
            opt3 = font.render("[3] +40 Max HP", True, WHITE)
            screen.blit(opt1, (px + 30, py + 70))
            screen.blit(opt2, (px + 30, py + 110))
            screen.blit(opt3, (px + 30, py + 150))

        pygame.display.flip()
        clock.tick(FPS)


def mode_select():
    options = ["VS MODE", "CAMPAIGN", "QUIT"]
    index = 0
    running = True
    info = font.render("Use Up/Down, Enter to select", True, WHITE)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    index = (index - 1) % len(options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    index = (index + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if index == 0:
                        return 'vs'
                    elif index == 1:
                        return 'campaign'
                    else:
                        return None

        screen.fill(BLACK)
        draw_background_grid(screen, gap=50, color=(30, 30, 30))
        title = font.render("HOLO SHOOT", True, (255, 215, 0))
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 120))
        screen.blit(info, (WINDOW_WIDTH // 2 - info.get_width() // 2, 160))
        for i, txt in enumerate(options):
            color = (255, 215, 0) if i == index else WHITE
            r = font.render(txt, True, color)
            screen.blit(r, (WINDOW_WIDTH // 2 - r.get_width() // 2, 220 + i * 40))

        pygame.display.flip()
        clock.tick(60)


def main():
    running = True
    while running:
        choice = mode_select()
        if choice is None:
            break
        if choice == 'vs':
            cont = vs_main()
        else:
            cont = campaign_main()
        if not cont:
            break
    pygame.quit()
    sys.exit()


# (Lucky Box effects helper removed)

if __name__ == "__main__":
    main()
