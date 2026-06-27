# VECTOR — Vibe-Engineered Chess Tactician for Online Rankings

A desktop chess application built with **Python 3.12** and **Pygame**, featuring a playable chess bot with five engine versions, full chess rules, self-play mode, and customizable appearance.

## Features

- Full chess rules (castling, en passant, promotion, check/draw detection, 50-move rule, threefold repetition)
- Click-to-move with legal move dot highlighting
- Board flip (press **F**), move history with scrollbar
- Captured pieces display, chess clock with time control presets
- Promotion dialog (click or Q/R/B/N keys)
- Resign button, game over overlay with PGN copy
- **Play vs Bot** / **vs Player** / **Self-Play** mode
- Configurable bot version, search depth (2–10 ply), and opening book toggle
- 5 bot versions with increasing strength (Mark 1–5)
- 23 opening books available (in-app download), default Komodo book shipped
- Threaded bot search — UI stays responsive during computation
- Abort active search via Esc / N
- **Board color schemes**: 6 presets (Classic, Marble, Ocean, Walnut, Emerald, Midnight)
- **Piece styles**: Merida, Julius, Alpha SVGs + Unicode fallback
- **Smooth piece animations** (250ms slide)
- **Dark/Light mode** (toggle with T key)
- **Menu animations & button hover effects**

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
| T | Toggle Dark/Light theme |
| Esc | Back / Quit (aborts active search) |

## Bot Versions

| Version | Search | Evaluation | Strength |
|---------|--------|------------|----------|
| **Mark 1** | Alpha-beta pruning depth 3 | Material + piece-square tables | Baseline |
| **Mark 2** | Iterative deepening (depth 1→N), MVV-LVA ordering, null-move pruning, PVS, check extensions, quiescence search, transposition table | Same as Mark 1 | ~100–150 Elo over Mark 1 |
| **Mark 3** | Same as Mark 2 | Advanced eval: passed/doubled/isolated pawns, king safety, rook open file, bishop pair, mobility, king tropism, hanging piece penalty, threat detection | ~100–150 Elo over Mark 2 |
| **Mark 4** | Same as Mark 3 + history heuristic, killer moves (2/ply, 64 ply depth), late move reductions, aspiration windows | Same as Mark 3 | ~100–150 Elo over Mark 3 |
| **Mark 5** | Same as Mark 4 + internal iterative deepening, static exchange evaluation (SEE), SEE pruning in quiescence, razoring, futility pruning | Same as Mark 4 | ~50–100 Elo over Mark 4 |

Configure in **Settings → Bot Version / Bot Depth**.

## Project Structure

```
vector/
├── main.py              # Entry point, game screens, state machine
├── board.py             # Board rendering & square mapping
├── game.py              # Game state, clock, PGN, captures
├── pieces.py            # SVG/Unicode piece rendering & caching
├── constants.py         # Colors, dimensions, theme system
├── settings.py          # Settings UI (time, bot config, theme, books)
├── books/               # Opening book storage (komodo.bin shipped)
├── bot/
│   ├── engine.py        # Search engine (versions 0-4)
│   ├── evaluator.py     # Position evaluation (Mark 1-5) + SEE
│   ├── ordering.py      # Move ordering (MVV-LVA, TT, history, killers, SEE)
│   ├── book.py          # Polyglot opening book reader
│   └── transposition.py # Zobrist-hashed transposition table
└── assets/
    └── pieces/
        ├── merida/      # Shaded SVG pieces (Codeberg)
        ├── julius/      # Clean SVG pieces (Codeberg)
        └── alpha/       # Minimalist SVG pieces (piece-packager)
```

## Roadmap

- **v2.0 ✅**: Mark 5 engine (IID, SEE, razoring, futility pruning), board color schemes (6 presets), piece styles (Merida/Julius/Alpha SVGs), smooth piece animations, dark/light mode, menu animations & hover effects
- **v2.1 — TBD**: Sound effects, game save/load, PGN import, undo/takeback

## Releases

Pre-built Windows executables are available on the [Releases](https://github.com/DYNAMO99X/vector/releases) page.
