#!/usr/bin/env python3
"""Bavarian-themed jump-and-run for Raspberry Pi."""

from __future__ import annotations

import argparse
import math
import random
from dataclasses import dataclass
from pathlib import Path

import pygame


WIDTH = 960
HEIGHT = 540
WORLD_WIDTH = 6000
GROUND_Y = 460
GRAVITY = 2300
PLAYER_SPEED = 340
JUMP_SPEED = -960
MUG_SPEED = 680
PLAYER_SHOOT_COOLDOWN = 0.35
GOAL_BEERS = 8

ASSET_DIR = Path(__file__).resolve().parent / "assets" / "generated"


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def draw_player(surface: pygame.Surface) -> None:
    surface.fill((0, 0, 0, 0))
    pygame.draw.rect(surface, (43, 94, 188), (10, 20, 32, 30), border_radius=6)
    pygame.draw.rect(surface, (245, 228, 202), (14, 4, 24, 20), border_radius=9)
    pygame.draw.rect(surface, (210, 130, 70), (16, 10, 20, 8), border_radius=4)
    pygame.draw.rect(surface, (245, 245, 245), (6, 22, 36, 8), border_radius=5)
    pygame.draw.rect(surface, (82, 56, 38), (12, 50, 10, 12), border_radius=4)
    pygame.draw.rect(surface, (82, 56, 38), (30, 50, 10, 12), border_radius=4)


def draw_waiter(surface: pygame.Surface) -> None:
    surface.fill((0, 0, 0, 0))
    pygame.draw.rect(surface, (32, 32, 32), (10, 20, 32, 34), border_radius=6)
    pygame.draw.rect(surface, (245, 232, 205), (14, 4, 24, 20), border_radius=9)
    pygame.draw.rect(surface, (230, 230, 230), (6, 24, 36, 8), border_radius=5)
    pygame.draw.rect(surface, (60, 60, 60), (7, 13, 34, 5), border_radius=3)
    pygame.draw.rect(surface, (72, 72, 72), (12, 54, 10, 10), border_radius=3)
    pygame.draw.rect(surface, (72, 72, 72), (30, 54, 10, 10), border_radius=3)
    pygame.draw.rect(surface, (190, 190, 190), (40, 12, 11, 5), border_radius=3)


def draw_police(surface: pygame.Surface) -> None:
    surface.fill((0, 0, 0, 0))
    pygame.draw.rect(surface, (28, 78, 166), (10, 20, 32, 34), border_radius=6)
    pygame.draw.rect(surface, (245, 232, 205), (14, 4, 24, 20), border_radius=9)
    pygame.draw.rect(surface, (18, 44, 110), (8, 11, 34, 6), border_radius=3)
    pygame.draw.rect(surface, (225, 225, 225), (16, 28, 20, 5), border_radius=3)
    pygame.draw.rect(surface, (26, 60, 130), (12, 54, 10, 10), border_radius=3)
    pygame.draw.rect(surface, (26, 60, 130), (30, 54, 10, 10), border_radius=3)


def draw_beer(surface: pygame.Surface) -> None:
    surface.fill((0, 0, 0, 0))
    pygame.draw.rect(surface, (252, 198, 71), (6, 8, 14, 24), border_radius=5)
    pygame.draw.rect(surface, (255, 244, 207), (5, 2, 16, 10), border_radius=5)
    pygame.draw.rect(surface, (238, 238, 238), (18, 12, 6, 12), border_radius=3)
    pygame.draw.rect(surface, (255, 255, 255), (8, 11, 3, 15), border_radius=2)


def draw_pretzel(surface: pygame.Surface) -> None:
    surface.fill((0, 0, 0, 0))
    pygame.draw.circle(surface, (177, 109, 56), (11, 12), 7, 5)
    pygame.draw.circle(surface, (177, 109, 56), (21, 12), 7, 5)
    pygame.draw.circle(surface, (177, 109, 56), (16, 21), 7, 5)
    pygame.draw.circle(surface, (232, 202, 146), (16, 21), 1)


def draw_mug(surface: pygame.Surface) -> None:
    surface.fill((0, 0, 0, 0))
    pygame.draw.rect(surface, (235, 235, 235), (5, 7, 16, 15), border_radius=4)
    pygame.draw.rect(surface, (249, 200, 86), (7, 9, 12, 11), border_radius=3)
    pygame.draw.rect(surface, (235, 235, 235), (18, 10, 5, 9), border_radius=3)


def draw_stun(surface: pygame.Surface) -> None:
    surface.fill((0, 0, 0, 0))
    points = [(14, 1), (18, 10), (27, 10), (19, 16), (23, 26), (11, 17), (3, 17), (9, 10), (1, 10)]
    pygame.draw.polygon(surface, (247, 212, 87), points)
    pygame.draw.polygon(surface, (171, 129, 21), points, width=2)


def fallback_image(size: tuple[int, int], painter) -> pygame.Surface:
    img = pygame.Surface(size, pygame.SRCALPHA)
    painter(img)
    return img


def load_asset(name: str, size: tuple[int, int], painter) -> pygame.Surface:
    path = ASSET_DIR / f"{name}.png"
    if path.exists():
        loaded = pygame.image.load(path.as_posix()).convert_alpha()
        return pygame.transform.smoothscale(loaded, size)
    return fallback_image(size, painter)


@dataclass
class Collectible:
    kind: str
    rect: pygame.Rect
    value: int
    bob_seed: float
    taken: bool = False


@dataclass
class Projectile:
    rect: pygame.Rect
    velocity: pygame.Vector2
    from_enemy: bool


@dataclass
class Enemy:
    kind: str
    rect: pygame.Rect
    patrol_min: int
    patrol_max: int
    speed: float
    direction: int = 1
    throw_cooldown: float = 0.0
    hurt_timer: float = 0.0


class Player:
    def __init__(self, spawn_x: int, spawn_y: int) -> None:
        self.rect = pygame.Rect(spawn_x, spawn_y, 46, 62)
        self.pos = pygame.Vector2(float(spawn_x), float(spawn_y))
        self.vel = pygame.Vector2(0.0, 0.0)
        self.on_ground = False
        self.facing = 1
        self.shoot_cooldown = 0.0
        self.invuln_timer = 0.0
        self.lives = 3

    def update(self, dt: float, solids: list[pygame.Rect], input_x: float, jump_pressed: bool) -> None:
        self.shoot_cooldown = max(0.0, self.shoot_cooldown - dt)
        self.invuln_timer = max(0.0, self.invuln_timer - dt)

        self.vel.x = input_x * PLAYER_SPEED
        if input_x < -0.1:
            self.facing = -1
        elif input_x > 0.1:
            self.facing = 1

        if jump_pressed and self.on_ground:
            self.vel.y = JUMP_SPEED
            self.on_ground = False

        self.vel.y += GRAVITY * dt
        self.move_and_collide(dt, solids)

    def move_and_collide(self, dt: float, solids: list[pygame.Rect]) -> None:
        self.pos.x += self.vel.x * dt
        self.rect.x = int(self.pos.x)
        for solid in solids:
            if self.rect.colliderect(solid):
                if self.vel.x > 0:
                    self.rect.right = solid.left
                elif self.vel.x < 0:
                    self.rect.left = solid.right
                self.pos.x = float(self.rect.x)

        self.pos.y += self.vel.y * dt
        self.rect.y = int(self.pos.y)
        self.on_ground = False
        for solid in solids:
            if self.rect.colliderect(solid):
                if self.vel.y > 0:
                    self.rect.bottom = solid.top
                    self.on_ground = True
                elif self.vel.y < 0:
                    self.rect.top = solid.bottom
                self.vel.y = 0
                self.pos.y = float(self.rect.y)

        if self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = float(self.rect.x)
        if self.rect.right > WORLD_WIDTH:
            self.rect.right = WORLD_WIDTH
            self.pos.x = float(self.rect.x)

    def can_shoot(self) -> bool:
        return self.shoot_cooldown <= 0.0

    def spawn_mug(self) -> Projectile:
        self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN
        mug_rect = pygame.Rect(0, 0, 22, 22)
        mug_rect.center = (self.rect.centerx + self.facing * 22, self.rect.centery - 8)
        velocity = pygame.Vector2(self.facing * MUG_SPEED, -120)
        return Projectile(mug_rect, velocity, from_enemy=False)

    def take_hit(self, direction: int) -> None:
        if self.invuln_timer > 0:
            return
        self.lives -= 1
        self.invuln_timer = 1.2
        self.vel.x = 260 * direction
        self.vel.y = -480


class BavarianRunGame:
    def __init__(self, fullscreen: bool = False) -> None:
        pygame.init()
        pygame.display.set_caption("Bavarian Mug Run")
        flags = pygame.FULLSCREEN if fullscreen else 0
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("verdana", 30, bold=True)
        self.small_font = pygame.font.SysFont("verdana", 21)
        self.large_font = pygame.font.SysFont("verdana", 54, bold=True)

        self.assets = {
            "player": load_asset("player", (46, 62), draw_player),
            "waiter": load_asset("waiter", (50, 62), draw_waiter),
            "police": load_asset("police", (50, 62), draw_police),
            "beer": load_asset("beer", (26, 34), draw_beer),
            "pretzel": load_asset("pretzel", (30, 30), draw_pretzel),
            "mug": load_asset("mug", (22, 22), draw_mug),
            "stun": load_asset("stun", (30, 30), draw_stun),
        }

        self.joystick = self._init_joystick()
        self.running = True
        self.time_s = 0.0
        self.state = "menu"
        self.fullscreen = fullscreen
        self.jump_queued = False
        self.reset()

    def _init_joystick(self) -> pygame.joystick.Joystick | None:
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            js = pygame.joystick.Joystick(0)
            js.init()
            return js
        return None

    def reset(self) -> None:
        self.solids = self.build_solids()
        self.collectibles = self.build_collectibles()
        self.enemies = self.build_enemies()
        self.player = Player(80, GROUND_Y - 62)
        self.projectiles: list[Projectile] = []
        self.enemy_projectiles: list[Projectile] = []
        self.score = 0
        self.beers = 0
        self.pretzels = 0
        self.camera_x = 0.0
        self.message = "Collect beer and pretzels. Reach the festival gate!"
        self.message_timer = 6.0

    def build_solids(self) -> list[pygame.Rect]:
        solids = [pygame.Rect(0, GROUND_Y, WORLD_WIDTH, HEIGHT - GROUND_Y)]
        platform_specs = [
            (320, 390, 170, 22),
            (760, 350, 220, 22),
            (1220, 402, 160, 22),
            (1580, 338, 190, 22),
            (2020, 372, 200, 22),
            (2480, 326, 180, 22),
            (2880, 402, 220, 22),
            (3380, 348, 190, 22),
            (3800, 382, 200, 22),
            (4280, 328, 210, 22),
            (4740, 368, 210, 22),
            (5230, 330, 180, 22),
        ]
        for x, y, w, h in platform_specs:
            solids.append(pygame.Rect(x, y, w, h))
        return solids

    def build_collectibles(self) -> list[Collectible]:
        items: list[Collectible] = []
        for x in range(240, WORLD_WIDTH - 200, 220):
            kind = "beer" if random.random() < 0.6 else "pretzel"
            value = 30 if kind == "beer" else 20
            y = GROUND_Y - (44 if kind == "beer" else 40)
            items.append(Collectible(kind, pygame.Rect(x, y, 28, 36), value, random.random() * 10))

        for solid in self.solids[1:]:
            if random.random() < 0.75:
                cx = solid.centerx - 12
                kind = "beer" if random.random() < 0.65 else "pretzel"
                value = 30 if kind == "beer" else 20
                y = solid.top - (40 if kind == "beer" else 34)
                items.append(Collectible(kind, pygame.Rect(cx, y, 28, 36), value, random.random() * 10))
        return items

    def build_enemies(self) -> list[Enemy]:
        return [
            Enemy("waiter", pygame.Rect(560, GROUND_Y - 62, 50, 62), 500, 910, 95),
            Enemy("police", pygame.Rect(1360, GROUND_Y - 62, 50, 62), 1260, 1610, 85),
            Enemy("waiter", pygame.Rect(2200, GROUND_Y - 62, 50, 62), 2100, 2480, 100),
            Enemy("police", pygame.Rect(3120, GROUND_Y - 62, 50, 62), 3000, 3360, 92),
            Enemy("waiter", pygame.Rect(4050, GROUND_Y - 62, 50, 62), 3940, 4320, 104),
            Enemy("police", pygame.Rect(4950, GROUND_Y - 62, 50, 62), 4800, 5300, 100),
        ]

    def toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_F11:
                self.toggle_fullscreen()
            elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                if self.state == "running":
                    self.jump_queued = True
                elif self.state in ("menu", "game_over", "win"):
                    self.state = "running"
                    self.reset()
            elif event.key in (pygame.K_j, pygame.K_LCTRL, pygame.K_RETURN):
                if self.state == "running" and self.player.can_shoot():
                    self.projectiles.append(self.player.spawn_mug())
                elif self.state in ("menu", "game_over", "win"):
                    self.state = "running"
                    self.reset()

        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:
                if self.state == "running":
                    self.jump_queued = True
                elif self.state in ("menu", "game_over", "win"):
                    self.state = "running"
                    self.reset()
            if event.button in (1, 2, 5) and self.state == "running" and self.player.can_shoot():
                self.projectiles.append(self.player.spawn_mug())

    def update(self, dt: float) -> None:
        self.time_s += dt
        self.message_timer = max(0.0, self.message_timer - dt)

        if self.state != "running":
            return

        keys = pygame.key.get_pressed()
        move_x = 0.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_x -= 1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x += 1.0

        if self.joystick:
            axis = self.joystick.get_axis(0)
            if abs(axis) > 0.2:
                move_x = clamp(axis, -1.0, 1.0)

        self.player.update(dt, self.solids, move_x, self.jump_queued)
        self.jump_queued = False

        self.update_collectibles()
        self.update_projectiles(dt)
        self.update_enemies(dt)
        self.check_goal_state()
        self.update_camera(dt)

        if self.player.rect.top > HEIGHT + 120:
            self.player.take_hit(-1)
            self.player.rect.topleft = (max(40, self.player.rect.x - 120), GROUND_Y - self.player.rect.height)
            self.player.pos = pygame.Vector2(self.player.rect.x, self.player.rect.y)

        if self.player.lives <= 0:
            self.state = "game_over"

    def update_collectibles(self) -> None:
        for item in self.collectibles:
            if item.taken:
                continue
            if self.player.rect.colliderect(item.rect):
                item.taken = True
                self.score += item.value
                if item.kind == "beer":
                    self.beers += 1
                else:
                    self.pretzels += 1

    def update_projectiles(self, dt: float) -> None:
        for shot in self.projectiles:
            shot.velocity.y += GRAVITY * 0.45 * dt
            shot.rect.x += int(shot.velocity.x * dt)
            shot.rect.y += int(shot.velocity.y * dt)

        for shot in self.enemy_projectiles:
            shot.rect.x += int(shot.velocity.x * dt)
            shot.rect.y += int(shot.velocity.y * dt)

        self.projectiles = [s for s in self.projectiles if 0 < s.rect.right < WORLD_WIDTH and s.rect.bottom < GROUND_Y + 10]
        self.enemy_projectiles = [s for s in self.enemy_projectiles if 0 < s.rect.right < WORLD_WIDTH]

        remaining_enemies: list[Enemy] = []
        for enemy in self.enemies:
            defeated = False
            for shot in self.projectiles:
                if enemy.rect.colliderect(shot.rect):
                    defeated = True
                    shot.rect.x = -500
                    self.score += 60
                    break
            if not defeated:
                remaining_enemies.append(enemy)
        self.enemies = remaining_enemies

        for shot in self.enemy_projectiles:
            if self.player.rect.colliderect(shot.rect):
                direction = -1 if shot.velocity.x > 0 else 1
                self.player.take_hit(direction)
                shot.rect.x = -1000

        self.projectiles = [s for s in self.projectiles if s.rect.x > -50]
        self.enemy_projectiles = [s for s in self.enemy_projectiles if s.rect.x > -900]

    def update_enemies(self, dt: float) -> None:
        for enemy in self.enemies:
            enemy.throw_cooldown = max(0.0, enemy.throw_cooldown - dt)
            enemy.hurt_timer = max(0.0, enemy.hurt_timer - dt)

            speed = enemy.speed
            dist_to_player = self.player.rect.centerx - enemy.rect.centerx
            if enemy.kind == "waiter" and abs(dist_to_player) < 190:
                enemy.direction = 1 if dist_to_player > 0 else -1
                speed *= 1.75

            enemy.rect.x += int(enemy.direction * speed * dt)

            if enemy.rect.left <= enemy.patrol_min:
                enemy.rect.left = enemy.patrol_min
                enemy.direction = 1
            elif enemy.rect.right >= enemy.patrol_max:
                enemy.rect.right = enemy.patrol_max
                enemy.direction = -1

            if enemy.kind == "police" and abs(dist_to_player) < 430 and enemy.throw_cooldown <= 0:
                enemy.throw_cooldown = 1.7
                direction = 1 if dist_to_player > 0 else -1
                bottle = Projectile(
                    rect=pygame.Rect(enemy.rect.centerx - 7, enemy.rect.centery - 16, 14, 14),
                    velocity=pygame.Vector2(direction * 420, 0),
                    from_enemy=True,
                )
                self.enemy_projectiles.append(bottle)

            if enemy.rect.colliderect(self.player.rect.inflate(-10, -6)):
                direction = -1 if self.player.rect.centerx > enemy.rect.centerx else 1
                self.player.take_hit(direction)

    def check_goal_state(self) -> None:
        if self.player.rect.right >= WORLD_WIDTH - 50:
            if self.beers >= GOAL_BEERS:
                self.state = "win"
            else:
                missing = GOAL_BEERS - self.beers
                self.message = f"You need {missing} more beer(s) to enter Oktoberfest!"
                self.message_timer = 2.3
                self.player.rect.right = WORLD_WIDTH - 54
                self.player.pos.x = float(self.player.rect.x)

    def update_camera(self, dt: float) -> None:
        target = self.player.rect.centerx - WIDTH * 0.42
        target = clamp(target, 0, WORLD_WIDTH - WIDTH)
        self.camera_x += (target - self.camera_x) * min(1.0, dt * 8)

    def draw_background(self) -> None:
        self.screen.fill((125, 198, 245))
        pygame.draw.rect(self.screen, (94, 178, 233), (0, 0, WIDTH, 160))

        mountain_offset = int(self.camera_x * 0.18)
        for i in range(-1, 8):
            x = i * 220 - (mountain_offset % 220)
            pygame.draw.polygon(self.screen, (100, 129, 152), [(x, 290), (x + 100, 180), (x + 200, 290)])
            pygame.draw.polygon(self.screen, (131, 164, 188), [(x + 20, 290), (x + 105, 200), (x + 190, 290)])

        tent_offset = int(self.camera_x * 0.42)
        for i in range(-1, 11):
            x = i * 150 - (tent_offset % 150)
            pygame.draw.polygon(self.screen, (248, 237, 214), [(x + 10, GROUND_Y), (x + 70, 338), (x + 130, GROUND_Y)])
            pygame.draw.rect(self.screen, (220, 71, 54), (x + 14, 395, 112, 12))
            pygame.draw.rect(self.screen, (241, 230, 205), (x + 34, 410, 72, 50))

    def draw_solids(self) -> None:
        ground_y = int(GROUND_Y)
        pygame.draw.rect(self.screen, (58, 149, 89), (0, ground_y, WIDTH, HEIGHT - ground_y))
        pygame.draw.rect(self.screen, (46, 112, 67), (0, ground_y, WIDTH, 12))

        for solid in self.solids[1:]:
            x = solid.x - int(self.camera_x)
            rect = pygame.Rect(x, solid.y, solid.w, solid.h)
            if rect.right < -20 or rect.left > WIDTH + 20:
                continue
            pygame.draw.rect(self.screen, (157, 113, 74), rect, border_radius=5)
            pygame.draw.rect(self.screen, (128, 90, 58), (rect.x, rect.y + rect.h - 6, rect.w, 6), border_radius=3)

    def draw_entities(self) -> None:
        for item in self.collectibles:
            if item.taken:
                continue
            bob = int(4 * math.sin(self.time_s * 3.6 + item.bob_seed))
            img = self.assets["beer"] if item.kind == "beer" else self.assets["pretzel"]
            x = item.rect.x - int(self.camera_x)
            y = item.rect.y + bob
            self.screen.blit(img, (x, y))

        for enemy in self.enemies:
            sprite = self.assets["waiter"] if enemy.kind == "waiter" else self.assets["police"]
            if enemy.direction < 0:
                sprite = pygame.transform.flip(sprite, True, False)
            self.screen.blit(sprite, (enemy.rect.x - int(self.camera_x), enemy.rect.y))

        for shot in self.projectiles:
            img = self.assets["mug"]
            if shot.velocity.x < 0:
                img = pygame.transform.flip(img, True, False)
            self.screen.blit(img, (shot.rect.x - int(self.camera_x), shot.rect.y))

        for shot in self.enemy_projectiles:
            x = shot.rect.x - int(self.camera_x)
            pygame.draw.circle(self.screen, (49, 104, 198), (x + 7, shot.rect.y + 7), 7)
            pygame.draw.circle(self.screen, (219, 231, 255), (x + 5, shot.rect.y + 5), 2)

        blink = self.player.invuln_timer > 0 and int(self.time_s * 14) % 2 == 0
        if not blink:
            player_img = self.assets["player"]
            if self.player.facing < 0:
                player_img = pygame.transform.flip(player_img, True, False)
            self.screen.blit(player_img, (self.player.rect.x - int(self.camera_x), self.player.rect.y))

    def draw_goal_gate(self) -> None:
        gate_x_world = WORLD_WIDTH - 62
        gate_x = gate_x_world - int(self.camera_x)
        if gate_x < WIDTH:
            pygame.draw.rect(self.screen, (182, 139, 82), (gate_x, GROUND_Y - 130, 56, 130))
            pygame.draw.rect(self.screen, (104, 62, 39), (gate_x + 6, GROUND_Y - 126, 44, 118))
            text = self.small_font.render("Fest", True, (255, 244, 222))
            self.screen.blit(text, (gate_x + 8, GROUND_Y - 86))

    def draw_hud(self) -> None:
        score_text = self.font.render(f"Score {self.score}", True, (255, 255, 255))
        stats_text = self.small_font.render(
            f"Beer {self.beers}/{GOAL_BEERS}  Pretzels {self.pretzels}  Lives {self.player.lives}",
            True,
            (255, 255, 255),
        )
        self.screen.blit(score_text, (20, 14))
        self.screen.blit(stats_text, (20, 52))

        if self.message_timer > 0:
            msg = self.small_font.render(self.message, True, (22, 22, 22))
            box = pygame.Rect((WIDTH - msg.get_width()) // 2 - 14, 82, msg.get_width() + 28, 36)
            pygame.draw.rect(self.screen, (249, 225, 168), box, border_radius=8)
            pygame.draw.rect(self.screen, (184, 147, 83), box, width=2, border_radius=8)
            self.screen.blit(msg, (box.x + 14, box.y + 8))

    def draw_state_overlay(self) -> None:
        if self.state == "running":
            return

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 10, 130))
        self.screen.blit(overlay, (0, 0))

        if self.state == "menu":
            title = "Bavarian Mug Run"
            subtitle = "Move with A/D or arrows. Jump SPACE. Throw mug J."
            prompt = "Press SPACE or A button to start"
        elif self.state == "game_over":
            title = "Game Over"
            subtitle = "The police ended your Oktoberfest tour."
            prompt = "Press SPACE to retry"
        else:
            title = "Prost! You Made It"
            subtitle = f"Final score {self.score} with {self.beers} beers."
            prompt = "Press SPACE to play again"

        title_s = self.large_font.render(title, True, (255, 246, 220))
        subtitle_s = self.small_font.render(subtitle, True, (255, 255, 255))
        prompt_s = self.small_font.render(prompt, True, (255, 255, 255))
        self.screen.blit(title_s, ((WIDTH - title_s.get_width()) // 2, HEIGHT // 2 - 78))
        self.screen.blit(subtitle_s, ((WIDTH - subtitle_s.get_width()) // 2, HEIGHT // 2 - 18))
        self.screen.blit(prompt_s, ((WIDTH - prompt_s.get_width()) // 2, HEIGHT // 2 + 18))

    def draw_controls_hint(self) -> None:
        hint = "Move A/D or Left/Right | Jump SPACE | Throw Mug J/LCTRL | F11 fullscreen | ESC quit"
        rendered = self.small_font.render(hint, True, (243, 243, 243))
        self.screen.blit(rendered, (12, HEIGHT - 30))

    def draw(self) -> None:
        self.draw_background()
        self.draw_solids()
        self.draw_goal_gate()
        self.draw_entities()
        self.draw_hud()
        self.draw_controls_hint()
        self.draw_state_overlay()
        pygame.display.flip()

    def run(self) -> None:
        self.jump_queued = False
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()
        pygame.quit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bavarian-themed Raspberry Pi platformer")
    parser.add_argument("--fullscreen", action="store_true", help="Start in fullscreen mode")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    BavarianRunGame(fullscreen=args.fullscreen).run()
