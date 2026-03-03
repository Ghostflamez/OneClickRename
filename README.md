# OneClickRename

A lightweight Windows 10/11 desktop GUI app for batch renaming files using regex patterns.

## Features

### Rename Rules
- **Prefix/Suffix**: Add or remove text at the start or end of filenames
- **Case Conversion**: UPPER, lower, Title, camelCase, PascalCase
- **Numbering**: Sequential numbering with custom patterns (e.g., `file_{:02d}`)
- **Regex**: Find and replace using regular expressions
- **Folder Name**: Option to add parent folder name as prefix/suffix

### File Management
- **Live Preview**: See changes before applying (300ms debounce)
- **Undo/Redo**: Full history support (up to 50 operations)
- **Clear**: Reset all rule inputs with confirmation dialog
- **Filter**: Dropdown menu with checkboxes for file type filtering
  - Categorized presets: Documents, Images, Media, Archives, Code
  - Custom extension support with validation

### UI Layout
```
┌─────────────────────────────────────────────────┐
│ [Open Folder] [Undo] [Redo] [Clear]             │  <- Toolbar
├─────────────────────────────────────────────────┤
│ Filter: [All Files    ] [Select... ▼]           │  <- Filter Bar
├─────────────────────────────────────────────────┤
│ ✓ │ Original Name        │ New Name             │
│───┼──────────────────────┼──────────────────────│  <- Preview
│   │ file1.txt            │ FILE1.txt (green)    │
│   │ file2.txt            │ FILE2.txt (green)    │
├─────────────────────────────────────────────────┤
│ [Prefix/Suffix] [Case] [Numbering] [Regex]      │  <- Rules Tabs
│ ┌─────────────────────────────────────────────┐ │
│ │ Add Prefix: [________]                      │ │
│ │ Remove Prefix: [________]                   │ │
│ └─────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────┤
│                               [Apply Rename]    │  <- Action Bar
└─────────────────────────────────────────────────┘
```

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
├── main.py          # Entry point + UI (tkinter + ttk)
├── engine.py        # Rename logic (pure functions)
├── history.py       # Undo/redo stack (Command Pattern)
└── requirements.txt # Dependencies
```

## License

MIT
