# VECTOR — Vibe-Engineered Chess Tactician for Online Rankings

A desktop chess application built with Python and Pygame featuring a playable chess bot with multiple difficulty levels.

## Features

- Full chess rules (castling, en passant, promotion, check/draw detection)
- Click-to-move with legal move highlighting
- Board flip support (press F)
- Move history with scrollbar
- Captured pieces display
- Chess clock with time control presets
- Game over overlay with PGN export
- **Play vs Bot** or **vs Player** locally
- Bot engine with configurable search depth (2–10 ply)
- Multiple bot versions (Mark 1: alpha-beta, Mark 2: move ordering + iterative deepening)

## Getting Started

### Prerequisites

- Python 3.12+
- A virtual environment (recommended)

### Installation

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Running

```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| Left Click | Select / move piece |
| F | Flip board |
| N | Return to menu (during game) |
| Esc | Back / Quit |

## Bot Versions

| Version | Algorithm | Strength |
|---------|-----------|----------|
| Mark 1 | Alpha-beta pruning + material/PST eval | Depth 3 baseline |
| Mark 2 | + Move ordering, iterative deepening | ~Depth 5-6 in same time |

Configure in **Settings → Bot Version / Bot Depth**.

## Project Structure

```
vector/
├── main.py          # Entry point, game screens, state machine
├── board.py         # Board rendering & square mapping
├── game.py          # Game state, clock, PGN, captures
├── pieces.py        # Unicode piece rendering
├── constants.py     # Colors, dimensions, piece map
├── settings.py      # Settings UI (time, bot config)
├── bot/
│   ├── engine.py    # Search engine (minimax + alpha-beta)
│   └── evaluator.py # Position evaluation (material + PST)
└── assets/pieces/   # SVG piece assets (unused — Unicode used instead)
```

## Roadmap

- Mark 3: Advanced evaluation (pawn structure, king safety, mobility)
- Mark 4: Opening book + time management
- Threading for non-blocking bot search
