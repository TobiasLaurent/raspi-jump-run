# Bavarian Mug Run (Godot)

This is the engine-based version of the game for Raspberry Pi / Recalbox targets.

## Engine
- Godot 4.x (recommended for this project scaffold)

## Open The Project
1. Install Godot 4.x on your development machine.
2. Open `/Users/tobiaslaurent/workspace/game/godot/project.godot`.
3. Run scene: `res://scenes/main.tscn`.

## Controls
- `A` / `D` or arrow keys: move
- `Space` / `W` / `Up`: jump
- `J` / `C` / `Enter`: throw mug
- Controller `A`: jump
- Controller `B/X`: throw mug
- `F11`: fullscreen
- `Esc`: quit

## Recalbox 10 (Raspberry Pi 5) Deployment
1. In Godot, create an export preset for `Linux/X11` `arm64`.
2. Export to a folder, for example `BavarianMugRun/`.
3. Copy that folder to your Recalbox:
   - `/recalbox/share/roms/ports/BavarianMugRun/`
4. Create launcher script:
   - `/recalbox/share/roms/ports/BavarianMugRun.sh`
5. Example launcher content:
```bash
#!/bin/bash
cd /recalbox/share/roms/ports/BavarianMugRun || exit 1
chmod +x ./BavarianMugRun.arm64
./BavarianMugRun.arm64
```
6. Mark launcher as executable:
```bash
chmod +x /recalbox/share/roms/ports/BavarianMugRun.sh
```

## Notes
- Keep the exported binary name in the launcher aligned with your real export output.
- If controller mapping differs on your setup, remap in Recalbox controller settings first.
