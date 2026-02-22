# RasPi Jump Run

A lightweight jump-and-run game built with `pygame`, designed to run on a Raspberry Pi.

## Features
- Single-button jump gameplay
- Endless obstacle runner with increasing speed
- Keyboard and basic gamepad support
- Fullscreen mode for arcade-style setups

## Controls
- `SPACE` / `UP` / `W`: jump, start, restart
- Gamepad button `A` (button `0`): jump, start, restart
- `F11`: toggle fullscreen
- `ESC`: quit

## Run Locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 game.py
```

To launch straight into fullscreen:
```bash
python3 game.py --fullscreen
```

## Raspberry Pi Setup
On Raspberry Pi OS:

```bash
sudo apt update
sudo apt install -y python3-pygame
python3 game.py --fullscreen
```

If you prefer virtual environments on Pi, use the same local setup commands above.

## Next Ideas
- Add sprite assets and tile map levels
- Add lives, power-ups, and sound effects
- Export to RetroPie Ports menu for one-click launch
