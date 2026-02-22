#!/usr/bin/env python3
"""Generate simple Bavarian-themed sprite assets for the game."""

from __future__ import annotations

from pathlib import Path

import pygame


ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "assets" / "generated"


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


def create_and_save(name: str, size: tuple[int, int], painter) -> None:
    surf = pygame.Surface(size, pygame.SRCALPHA)
    painter(surf)
    pygame.image.save(surf, (OUT_DIR / f"{name}.png").as_posix())


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pygame.init()
    create_and_save("player", (46, 62), draw_player)
    create_and_save("waiter", (50, 62), draw_waiter)
    create_and_save("police", (50, 62), draw_police)
    create_and_save("beer", (26, 34), draw_beer)
    create_and_save("pretzel", (30, 30), draw_pretzel)
    create_and_save("mug", (22, 22), draw_mug)
    create_and_save("stun", (30, 30), draw_stun)
    pygame.quit()
    print(f"Assets written to {OUT_DIR}")


if __name__ == "__main__":
    main()
