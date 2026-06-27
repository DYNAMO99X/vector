# VECTOR — Vibe-Engineered Chess Tactician for Online Rankings

A desktop chess application built with **Python 3.12** and **Pygame**, featuring a playable chess bot with four engine versions, full chess rules, and self-play mode.

## Features

- Full chess rules (castling, en passant, promotion, check/draw detection, 50-move rule, threefold repetition)
- Click-to-move with legal move dot highlighting
- Board flip (press **F**), move history with scrollbar
- Captured pieces display, chess clock with time control presets
- Promotion dialog (click or Q/R/B/N keys)
- Resign button, game over overlay with PGN copy
- **Play vs Bot** / **vs Player** / **Self-Play** mode
- Configurable bot version, search depth (2–10 ply), and opening book toggle
- 4 bot versions with increasing strength
- UHO opening book (uho-pohl.bin, 5M entries, 2300+ Elo filtered)
- Threaded bot search — UI stays responsive during computation
- Abort active search via Esc / N

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
| N | Return to menu (aborts active search) |
| Esc | Back / Quit (aborts active search) |

## Bot Versions

| Version | Search | Evaluation | Strength |
|---------|--------|------------|----------|
| **Mark 1** | Alpha-beta pruning depth 3 | Material + piece-square tables | Baseline |
| **Mark 2** | Iterative deepening (depth 1→N), MVV-LVA ordering, null-move pruning, PVS, check extensions, quiescence search, transposition table | Same as Mark 1 | ~100–150 Elo over Mark 1 |
| **Mark 3** | Same as Mark 2 | Advanced eval: passed/doubled/isolated pawns, king safety, rook open file, bishop pair, mobility, king tropism, hanging piece penalty, threat detection | ~100–150 Elo over Mark 2 |
| **Mark 4** | Same as Mark 3 + history heuristic, killer moves (2/ply, 64 ply depth), late move reductions, aspiration windows | Same as Mark 3 | ~100–150 Elo over Mark 3 |

Configure in **Settings → Bot Version / Bot Depth**.

## Project Structure

```
vector/
├── main.py              # Entry point, game screens, state machine
├── board.py             # Board rendering & square mapping
├── game.py              # Game state, clock, PGN, captures
├── pieces.py            # Unicode piece rendering
├── constants.py         # Colors, dimensions, piece map
├── settings.py          # Settings UI (time, bot config, theme)
├── uho-pohl.bin         # UHO Polyglot opening book (80 MB)
├── bot/
│   ├── engine.py        # Search engine (versions 0-3)
│   ├── evaluator.py     # Position evaluation (Mark 1-3)
│   ├── ordering.py      # Move ordering (MVV-LVA, TT, history, killers)
│   ├── book.py          # Polyglot opening book reader
│   └── transposition.py # Zobrist-hashed transposition table
└── assets/
    └── pieces/          # SVG piece assets (unused — Unicode used instead)
```

## Roadmap

- **v2.0 — Phase 4**: Mark 5 engine (IID, SEE, razoring, futility pruning), board color schemes, PNG piece styles, smooth animations, dark/light mode, menu animations

## Releases

Pre-built Windows executables are available on the [Releases](https://github.com/DYNAMO99X/vector/releases) page.
