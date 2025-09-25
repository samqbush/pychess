# PyChess Development Guide for AI Assistants

## Architecture Overview

PyChess follows a **perspective-based architecture** where the UI is organized into distinct modes:
- **Perspectives** (`lib/pychess/perspectives/`): welcome, games, database, fics, learn
- Each perspective auto-loads `*Panel.py` files from its directory as dockable side panels
- Entry point: `pychess` executable → `lib/pychess/Main.py` → `PyChess(Gtk.Application)`

## Key Patterns

### Perspective System
```python
# All perspectives inherit from Perspective base class
class MyPerspective(GObject.GObject, Perspective):
    def __init__(self):
        Perspective.__init__(self, "name", "Label")
        # Panels auto-discovered by filename pattern: *Panel.py
```
- Panels must define `__title__`, `__desc__`, `__icon__` module variables
- Menu items auto-generated from panel metadata

### Player Architecture
- **Player base class**: `lib/pychess/Players/Player.py` with GObject signals
- **Engine protocols**: CECP (`CECPEngine.py`) and UCI (`UCIEngine.py`)
- **Built-in engine**: `PyChess.py` - pure Python implementation
- **Online players**: `ICPlayer.py` for FICS/ICC integration

### Game State Management
- **GameModel** (`Utils/GameModel.py`): Central game state with move history, time control
- **Board representation**: Low-level utilities in `Utils/lutils/` (bitboards, move generation)
- **Move objects**: `Utils/Move.py` with SAN/LAN/AN notation support

## Critical Development Patterns

### GTK Signal Architecture
```python
# Standard pattern for UI components
class MyWidget(GObject.GObject):
    __gsignals__ = {
        'custom_event': (GObject.SignalFlags.RUN_FIRST, None, (object,)),
    }
    
    def emit_event(self, data):
        self.emit('custom_event', data)
```

### File System Layout
- **Entry points**: Root `pychess` (executable) and `lib/__main__.py`
- **Core logic**: Always in `lib/pychess/` subdirectories
- **Assets**: Top-level directories (`boards/`, `pieces/`, `sounds/`)
- **Configuration**: Uses `pychess.System.conf` for settings persistence

### Testing Approach
```bash
# Run tests (sets PYCHESS_UNITTEST=true)
./run_tests.sh
# Or: PYTHONPATH=lib python3 -m unittest discover -s testing -p "*.py" -v
```
- Tests use `unittest.mock.patch` extensively for UI components
- Engine tests mock stdin/stdout communication
- Test files mirror `lib/pychess/` structure

## Essential Integration Points

### External Dependencies
- **Chess engines**: Via `Players/engineNest.py` discovery system
- **Database tools**: `external/scoutfish.py` and `external/chess_db.py`
- **File formats**: `Savers/` directory handles PGN, FEN, EPD parsing
- **Internet chess**: `ic/` manages FICS/ICC protocol implementations

### Data Flow Patterns
1. **Game creation**: `GameModel` → `Player` instances → `GameWidget` (UI)
2. **Move processing**: User input → `Player.getMove()` → `GameModel.addMove()` → board updates
3. **Engine communication**: Async pipes with `subprocess.Popen` and asyncio

## Development Workflow

### Running from Source
```python
# Always use lib/ directory in PYTHONPATH
python pychess  # Uses lib/pychess as module
```

### Adding New Features
- **New perspective**: Create directory in `perspectives/` with `__init__.py` and `*Panel.py` files
- **New engine**: Inherit from `ProtocolEngine` and implement protocol methods
- **New chess variant**: Add to `Variants/` following `normal.py` pattern

### Configuration System
```python
from pychess.System import conf
# Settings auto-persist to user data directory
conf.set("setting_name", value)
value = conf.get("setting_name")
```

## Common Gotchas

- **Module imports**: Always use `lib/` as Python path root
- **GTK threading**: UI updates must happen on main thread - use `GLib.idle_add()`
- **Game state**: Never modify `GameModel` directly - use provided methods for move validation
- **File paths**: Use `pychess.System.prefix` functions for cross-platform compatibility
- **Engine protocols**: CECP and UCI have different command patterns - check existing implementations

## Key Files for Reference
- `lib/pychess/Main.py`: Application lifecycle and window management
- `lib/pychess/Utils/const.py`: Essential constants and enumerations
- `lib/pychess/perspectives/__init__.py`: Perspective loading system
- `testing/engine.py`: Example test patterns with mocking