#!/usr/bin/env python3
"""Simple jump-and-run game for Raspberry Pi."""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass

import pygame


WIDTH = 960
HEIGHT = 540
GROUND_Y = 430
GRAVITY = 2200
BASE_SPEED = 320


@dataclass
class Obstacle:
    rect: pygame.Rect
    scored: bool = False


class Player:
    def __init__(self) -> None:
        self.width = 48
        self.height = 58
        self.x = 140
        self.y = GROUND_Y - self.height
        self.vel_y = 0.0
        self.on_ground = True

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def jump(self) -> None:
        if self.on_ground:
            self.vel_y = -860
            self.on_ground = False

    def update(self, dt: float) -> None:
        self.vel_y += GRAVITY * dt
        self.y += self.vel_y * dt
        floor = GROUND_Y - self.height
        if self.y >= floor:
            self.y = floor
            self.vel_y = 0
            self.on_ground = True


class Game:
    def __init__(self, fullscreen: bool = False) -> None:
        pygame.init()
        pygame.display.set_caption("RasPi Jump Run")
        flags = pygame.FULLSCREEN if fullscreen else 0
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 30, bold=True)
        self.small_font = pygame.font.SysFont("monospace", 22)
        self.player = Player()
        self.obstacles: list[Obstacle] = []
        self.score = 0
        self.distance = 0.0
        self.game_speed = BASE_SPEED
        self.spawn_in = 0.8
        self.state = "menu"
        self.running = True
        self.joystick = self._init_joystick()

    def _init_joystick(self) -> pygame.joystick.Joystick | None:
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            return joystick
        return None

    def toggle_fullscreen(self) -> None:
        if self.screen.get_flags() & pygame.FULLSCREEN:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

    def reset_round(self) -> None:
        self.player = Player()
        self.obstacles.clear()
        self.score = 0
        self.distance = 0.0
        self.game_speed = BASE_SPEED
        self.spawn_in = 0.8
        self.state = "running"

    def spawn_obstacle(self) -> None:
        width = random.randint(35, 65)
        height = random.randint(40, 95)
        rect = pygame.Rect(WIDTH + 20, GROUND_Y - height, width, height)
        self.obstacles.append(Obstacle(rect))
        self.spawn_in = random.uniform(0.7, 1.35)

    def update(self, dt: float) -> None:
        if self.state != "running":
            return

        self.player.update(dt)
        self.distance += self.game_speed * dt
        self.game_speed = BASE_SPEED + min(self.distance * 0.04, 220)
        self.spawn_in -= dt
        if self.spawn_in <= 0:
            self.spawn_obstacle()

        for obstacle in self.obstacles:
            obstacle.rect.x -= int(self.game_speed * dt)
            if not obstacle.scored and obstacle.rect.right < self.player.rect.left:
                obstacle.scored = True
                self.score += 1

        self.obstacles = [o for o in self.obstacles if o.rect.right > -10]

        player_rect = self.player.rect.inflate(-10, -4)
        for obstacle in self.obstacles:
            if player_rect.colliderect(obstacle.rect):
                self.state = "game_over"
                break

    def draw_background(self) -> None:
        self.screen.fill((12, 30, 56))
        for i in range(6):
            cloud_x = (i * 190 - int(self.distance * 0.18)) % (WIDTH + 240) - 120
            pygame.draw.ellipse(self.screen, (34, 68, 110), (cloud_x, 80 + i % 2 * 40, 150, 55))
        pygame.draw.rect(self.screen, (26, 128, 89), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.rect(self.screen, (17, 87, 62), (0, GROUND_Y, WIDTH, 8))

    def draw(self) -> None:
        self.draw_background()
        pygame.draw.rect(self.screen, (250, 220, 95), self.player.rect, border_radius=8)
        for obstacle in self.obstacles:
            pygame.draw.rect(self.screen, (220, 93, 74), obstacle.rect, border_radius=5)

        score_surface = self.font.render(f"Score: {self.score}", True, (245, 245, 245))
        self.screen.blit(score_surface, (20, 20))

        if self.state == "menu":
            self._draw_center_message("RasPi Jump Run", "Press SPACE / A button to start")
        elif self.state == "game_over":
            self._draw_center_message("Game Over", "Press SPACE / A button to restart")

        help_text = "Jump: SPACE/UP/W or Controller A | F11 Fullscreen | ESC Quit"
        hint = self.small_font.render(help_text, True, (230, 230, 230))
        self.screen.blit(hint, (18, HEIGHT - 34))
        pygame.display.flip()

    def _draw_center_message(self, title: str, subtitle: str) -> None:
        title_surface = self.font.render(title, True, (255, 255, 255))
        subtitle_surface = self.small_font.render(subtitle, True, (235, 235, 235))
        tx = (WIDTH - title_surface.get_width()) // 2
        sx = (WIDTH - subtitle_surface.get_width()) // 2
        self.screen.blit(title_surface, (tx, HEIGHT // 2 - 48))
        self.screen.blit(subtitle_surface, (sx, HEIGHT // 2 - 8))

    def handle_jump_or_start(self) -> None:
        if self.state == "running":
            self.player.jump()
        else:
            self.reset_round()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                self.handle_jump_or_start()
            elif event.key == pygame.K_r and self.state == "game_over":
                self.reset_round()
            elif event.key == pygame.K_F11:
                self.toggle_fullscreen()
        elif event.type == pygame.JOYBUTTONDOWN and event.button in (0, 7):
            self.handle_jump_or_start()

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()
        pygame.quit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simple Raspberry Pi jump-and-run")
    parser.add_argument("--fullscreen", action="store_true", help="Start in fullscreen mode")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    Game(fullscreen=args.fullscreen).run()
