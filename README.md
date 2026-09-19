# Pong

A minimal two-mode Pong game built with Python 3.14 and pygame-ce.

## Run

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Press `1` for solo against the AI or `2` for two local players. The left paddle uses `W`/`S`; the right paddle uses the arrow keys. First to 7 wins. `Space` returns to the menu after a match, and `Escape` exits.

## Test

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe main.py --headless --smoke
```

Open this folder directly in VS Code and press F5 to debug the game.

## Windows executable

The ready-to-play executable is `dist/Pong.exe`. Double-click it in File Explorer, or run:

```powershell
.\dist\Pong.exe
```

To rebuild it from source, install the build dependency and run PyInstaller from the project root:

```powershell
.\.venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements-build.txt
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name Pong main.py
```
