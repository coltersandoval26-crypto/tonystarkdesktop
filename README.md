# Tony Stark-Inspired Touch Desktop (PyQt6)

A native Python + PyQt6 fullscreen HUD desktop with draggable futuristic panels, touch gestures, and mixed functional/aesthetic widgets.

## Install

```bash
pip install PyQt6 psutil
```

## Run

```bash
python main.py
```

## Startup Biometric Flow

On launch, the desktop starts in a biometric boot overlay.

- Tap the numbered finger targets on the large hand guide, or place **your hand (4+ touch points)** to scan.
- Keep contact briefly to unlock the full workspace.
- Mouse support: tap the finger targets for guided unlock, or use **Skip Scan (Instant Unlock)**.

## Included Panels

- **System Panel**: live CPU and RAM utilization (updates every 1s)
- **Notes Panel**: editable notes with auto-save
- **Project Panel**: file/folder list from `workspace/projects`
- **Diagnostics Panel**: OS, CPU, and RAM details
- **Clock Panel**: live time and date
- **Arc Reactor Panel**: round 5-finger interactive core (touch 5 points to ignite)
- **Field Visualizer**: animated aesthetic waveform panel
- **Ruler Panel**: sizeable on-screen ruler

## Controls & Gestures

- Launches in fullscreen automatically.
- Press `Esc` to exit fullscreen (app stays open).
- Drag a panel by its top bar.
- Double tap / double click top bar to maximize/restore a panel.
- Two-finger drag on workspace moves every panel.
- Pinch on panel to scale slightly.
- **Arc Reactor** panel responds to **5-finger touch**.

## Runtime Paths

- `workspace/projects/`
- `workspace/runtime/notes.txt`
