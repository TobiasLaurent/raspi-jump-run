# Bavarian Mug Run

Bavarian-themed jump-and-run project targeting Raspberry Pi game simulators.

This repository now contains:
- A fast `pygame` prototype (`/Users/tobiaslaurent/workspace/game/game.py`)
- A real engine version in Godot (`/Users/tobiaslaurent/workspace/game/godot`)

## Recommended Path
For long-term development and better game architecture, use the Godot project:
- `/Users/tobiaslaurent/workspace/game/godot/project.godot`

Read engine setup and Recalbox deployment:
- `/Users/tobiaslaurent/workspace/game/godot/README.md`

## Prototype (Pygame)
Quick local run:
```bash
python3 scripts/generate_assets.py
python3 game.py
```

## Current Theme
- Player: Bavarian festival visitor
- Collectibles: beer + pretzels
- Enemies: waiters + police
- Attack: throwable beer mug
