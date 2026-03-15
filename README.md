# Tony Stark Desktop & Workspace Recreation

This project gives you a **Tony Stark-style desktop/workspace folder setup** that runs fully on your own computer with **no internet required after download**.

It is designed for people with little or no coding experience.

---

## What you get

- A themed `desktop/` configuration folder (display layout ideas, widgets, shortcuts, HUD theme).
- A `workspace/` folder with JARVIS profile, diagnostics, and mission/project notes.
- A setup script that creates a local `runtime/` folder for active files.
- An optional local offline viewer server script for opening in a browser and using **full screen**.

---

## Folder map (simple explanation)

- `desktop/layout/` → screen and widget placement presets (JSON files).
- `desktop/shortcuts/` → example app shortcut definitions.
- `desktop/themes/` → HUD-inspired CSS theme.
- `desktop/wallpapers/` → place your own wallpaper images here.
- `workspace/JARVIS/` → assistant behavior/persona text.
- `workspace/diagnostics/` → machine/system status sample.
- `workspace/projects/` → project/mission documents.
- `scripts/` → helper scripts to initialize and run locally.

---

## Download and use offline (step-by-step)

## 1) Download this repository

If you received a ZIP:
1. Save ZIP to your computer.
2. Extract it (right-click → Extract / Unzip).
3. Open the extracted folder.

If you use Git:
```bash
git clone <repo-url>
cd tonystarkdesktop
```

> After this step, you can disconnect from internet. Everything here is local files.

## 2) Initialize once

From the project folder run:

```bash
bash scripts/bootstrap_workspace.sh
```

This creates a `runtime/` folder with active config files.

## 3) Open in browser locally (offline)

Start a local file server:

```bash
bash scripts/start_offline_view.sh
```

Then open this address in your browser:

- `http://127.0.0.1:8080`

## 4) Enter full screen

- **Windows/Linux browsers:** press `F11`
- **macOS browsers:** press `Control + Command + F`

Now you have a clean, full-screen local workspace view.

---

## Very simple use flow (non-technical)

1. Open folder.
2. Run bootstrap script once.
3. Run offline viewer script.
4. Open browser link.
5. Press full-screen shortcut.
6. Edit files in `desktop/` and `workspace/` to personalize.

---

## What to customize first

- `desktop/layout/monitors.json` for your display arrangement.
- `desktop/layout/widgets.json` for panel positions.
- `desktop/themes/stark-hud.css` for color/style tweaks.
- `workspace/JARVIS/assistant-profile.yaml` for assistant behavior.

---

## No-code editing tips

- Use a plain text editor (Notepad, TextEdit, VS Code, etc.).
- Change only values inside quotes when possible.
- Save file, refresh browser page to see updated content listing.
- If something breaks, restore from your backup copy.

---

## Troubleshooting

### “Command not found” when running scripts
- Ensure you are inside this project folder before running commands.
- On macOS/Linux, run exactly with `bash scripts/<script-name>.sh`.

### Port 8080 is already in use
Run with a different port:

```bash
PORT=9090 bash scripts/start_offline_view.sh
```

Then open `http://127.0.0.1:9090`.

### Browser did not enter full screen
Use the menu in browser:
- View → Enter Full Screen

---

## Security note

This project is local-first and static. It does not require cloud services to function as a folder workspace + local browser view.
