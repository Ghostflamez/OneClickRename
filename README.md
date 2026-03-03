# OneClickRename

A lightweight Windows 10/11 desktop GUI app for batch renaming files using regex patterns.

## Features

- **Prefix/Suffix**: Add or remove text at the start or end of filenames
- **Case Conversion**: UPPER, lower, Title, camelCase, PascalCase
- **Numbering**: Sequential numbering with custom patterns (e.g., `file_{:02d}`)
- **Regex**: Find and replace using regular expressions
- **Live Preview**: See changes before applying with 300ms debounce
- **Undo/Redo**: Full history support (up to 50 operations)
- **File Filtering**: Filter by extension or pattern (e.g., `*.txt`)

## Requirements

- Python 3.10+
- Windows 10/11
- No third-party runtime dependencies (stdlib only)

## Usage

```bash
python main.py
```

## Building Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

The `.exe` will be created in the `dist/` folder.

## Project Structure

```
OneClickRename/
├── main.py          # Entry point + UI
├── engine.py        # Rename logic (pure functions)
├── history.py       # Undo/redo stack
└── requirements.txt # Dependencies
```

## License

MIT
